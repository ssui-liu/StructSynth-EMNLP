"""Evidence-grounded BFS graph induction following the EMNLP method/algorithm."""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
import json
from typing import Any, Callable

import networkx as nx
import pandas as pd

from ..artifacts import canonical_json, frame_records
from .associations import association_evidence
from .graph import DependencyGraph
from .prompts import SOURCE_SYSTEM, SUCCESSORS_SYSTEM, CYCLE_SYSTEM
from ..llm import BudgetExceeded, LLMConfigurationError, LLMRequest, LLMResponseError, LLMTransportError
from ..schema import DatasetSpec


@dataclass
class DiscoveryResult:
    graph: DependencyGraph
    events: list[dict[str, Any]]


class DiscoveryError(RuntimeError):
    """A bounded discovery failure with an inspectable audit and last valid DAG."""

    def __init__(
        self, message: str, *, events: list[dict[str, Any]], partial_graph: DependencyGraph
    ) -> None:
        super().__init__(message)
        self.events = list(events)
        self.partial_graph = partial_graph.to_dict()


class _InvalidResponse(ValueError):
    pass




def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    # Avoid DataFrame.to_json's default decimal rounding: the prompt should
    # contain the actual training values. Strict JSON rejects unsupported types.
    records = frame_records(frame)
    canonical_json(records)
    return records


def _object(content: Any) -> dict[str, Any]:
    if not isinstance(content, dict):
        raise _InvalidResponse("Response must be a JSON object")
    return content


def _audit_content(content: Any) -> Any:
    try:
        json.dumps(content, allow_nan=False)
        return content
    except (TypeError, ValueError):
        return repr(content)


def _prepare_examples(train: pd.DataFrame, examples: pd.DataFrame | None) -> pd.DataFrame:
    if examples is None:
        return train.head(min(10, len(train))).copy()
    if not isinstance(examples, pd.DataFrame) or list(examples.columns) != list(train.columns):
        raise ValueError("Few-shot examples must be a DataFrame with the training columns in order")
    if examples.empty:
        raise ValueError("Few-shot examples cannot be empty")
    # Enforce D_few_shot ⊆ D_train, including multiplicities and JSON types,
    # without index assumptions or Python's equality between True and 1.
    available = Counter(canonical_json(row) for row in _records(train))
    selected = Counter(canonical_json(row) for row in _records(examples))
    if any(count > available[row] for row, count in selected.items()):
        raise ValueError("Few-shot examples must be a row subset of the training data")
    return examples.copy()


def discover_structure(
    train: pd.DataFrame,
    spec: DatasetSpec,
    client: Any,
    *,
    examples: pd.DataFrame | None = None,
    max_response_attempts: int = 3,
    max_cycles: int = 1000,
) -> DiscoveryResult:
    """Induce selected V and a validated DAG; keep A\\V for final completion.

    Every selected node is expanded exactly once. Each expansion evaluates all
    elementary cycles in the complete candidate edge set, as in Algorithm 1;
    the union of one validated removal per cycle is pruned before continuation.
    Provider retries and token accounting belong to the shared LLM client.
    """
    for name, limit in (("max_response_attempts", max_response_attempts), ("max_cycles", max_cycles)):
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError(f"{name} must be a positive integer")
    if not isinstance(train, pd.DataFrame) or train.empty:
        raise ValueError("Graph induction requires nonempty training data")
    if list(train.columns) != spec.columns:
        raise ValueError("Training columns must exactly match the dataset schema and order")
    few_shot = _prepare_examples(train, examples)
    categorical = set(spec.categorical_columns) | set(spec.boolean_columns)
    if spec.task_type == "classification":
        categorical.add(spec.target_column)
    evidence = association_evidence(train, categorical)
    order = {column: index for index, column in enumerate(spec.columns)}
    features = [
        {
            "name": column,
            "type": "categorical" if column in categorical else "continuous",
            "description": spec.descriptions.get(column, ""),
        }
        for column in spec.columns
    ]
    common = {"features": features, "examples": _records(few_shot), "task": spec.task}
    graph = DependencyGraph(spec.columns, [], [])
    events: list[dict[str, Any]] = []
    request_counter = 0

    def fail(message: str) -> None:
        events.append({"event": "discovery_failed", "reason": message})
        raise DiscoveryError(message, events=events, partial_graph=graph)

    def ask(
        purpose: str,
        system: str,
        payload: dict[str, Any],
        schema: dict[str, Any],
        validate: Callable[[Any], Any],
        context: dict[str, Any],
    ) -> Any:
        nonlocal request_counter
        request_counter += 1
        last_error = ""
        for attempt in range(1, max_response_attempts + 1):
            request_id = f"discovery-{request_counter:04d}-attempt-{attempt}"
            record = {
                "purpose": purpose,
                "request_id": request_id,
                "attempt": attempt,
                **context,
            }
            response_content = None
            # A failed content attempt gets explicit feedback. Previously accepted
            # state is retained; no edges/nodes are mutated until validation.
            request_payload = dict(payload)
            if last_error:
                request_payload["validation_error"] = last_error
            try:
                response = client.complete(
                    LLMRequest(
                        purpose=purpose,
                        system=system,
                        payload=request_payload,
                        response_schema=schema,
                        request_id=request_id,
                    )
                )
                response_content = response.content
                result = validate(response_content)
            except (BudgetExceeded, LLMConfigurationError, LLMTransportError) as error:
                events.append(
                    {"event": "discovery_aborted", **record, "error_type": type(error).__name__, "reason": str(error)}
                )
                # Preserve the original typed failure so budgets/configuration
                # cannot become content retries, while retaining review evidence.
                error.events = list(events)
                error.partial_graph = graph.to_dict()
                raise
            except (LLMResponseError, _InvalidResponse) as error:
                last_error = str(error)
                events.append(
                    {
                        "event": "invalid_response",
                        **record,
                        "reason": last_error,
                        "response": _audit_content(response_content),
                    }
                )
                continue
            events.append(
                {"event": "response_validated", **record, "response": _audit_content(response_content)}
            )
            return result
        fail(f"{purpose} failed after {max_response_attempts} response attempts: {last_error}")

    def validate_sources(content: Any) -> list[str]:
        content = _object(content)
        if set(content) != {"source_nodes"}:
            raise _InvalidResponse("Response must contain exactly source_nodes")
        values = content["source_nodes"]
        if not isinstance(values, list):
            raise _InvalidResponse("source_nodes must be a list of exact feature names")
        if any(not isinstance(value, str) or value not in order for value in values):
            raise _InvalidResponse("source_nodes contains an unknown or malformed feature name")
        if len(set(values)) != len(values):
            raise _InvalidResponse("source_nodes contains duplicate names")
        return sorted(values, key=order.__getitem__)

    source_schema = {
        "type": "object",
        "properties": {"source_nodes": {"type": "array", "items": {"type": "string", "enum": spec.columns}}},
        "required": ["source_nodes"],
        "additionalProperties": False,
    }
    sources = ask("source_nodes", SOURCE_SYSTEM, common, source_schema, validate_sources, {})
    graph = DependencyGraph(spec.columns, sources, [])
    queue = deque(sources)
    enqueued = set(sources)
    events.append({"event": "source_nodes_selected", "nodes": list(sources), "few_shot_rows": len(few_shot)})

    while queue:
        source = queue.popleft()

        def validate_successors(content: Any) -> list[dict[str, Any]]:
            content = _object(content)
            if set(content) != {"successors"}:
                raise _InvalidResponse("Response must contain exactly successors")
            successors = content["successors"]
            if not isinstance(successors, list):
                raise _InvalidResponse("successors must be a list")
            targets: set[str] = set()
            edges = []
            for successor in successors:
                if not isinstance(successor, dict):
                    raise _InvalidResponse("Every successor must be a JSON object")
                if not {"target", "reasoning"}.issubset(successor) or set(successor) - {"target", "reasoning", "confidence"}:
                    raise _InvalidResponse("A successor requires target and reasoning, with only optional confidence")
                target = successor.get("target")
                if not isinstance(target, str) or target not in order:
                    raise _InvalidResponse("A successor target is not an exact feature name")
                if target == source:
                    raise _InvalidResponse("Self dependencies are not valid successor proposals")
                if target in targets:
                    raise _InvalidResponse("Duplicate successor targets are not allowed")
                reasoning = successor.get("reasoning")
                if not isinstance(reasoning, str) or not reasoning.strip():
                    raise _InvalidResponse("Each successor requires nonempty evidence-based reasoning")
                confidence = successor.get("confidence", "Unspecified")
                if confidence is not None and (not isinstance(confidence, str) or not confidence.strip()):
                    raise _InvalidResponse("confidence must be a nonempty string or null")
                targets.add(target)
                edges.append(
                    {
                        "from": source,
                        "to": target,
                        "reasoning": reasoning.strip(),
                        "confidence": confidence,
                        "association_value": evidence[source][target].value,
                    }
                )
            return sorted(edges, key=lambda edge: order[edge["to"]])

        successor_schema = {
            "type": "object",
            "properties": {
                "successors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "target": {"type": "string", "enum": spec.columns},
                            "reasoning": {"type": "string"},
                            "confidence": {"type": ["string", "null"]},
                        },
                        "required": ["target", "reasoning"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["successors"],
            "additionalProperties": False,
        }
        proposed = ask(
            "direct_successors",
            SUCCESSORS_SYSTEM,
            {
                **common,
                "source": source,
                "graph": {"nodes": list(graph.nodes), "edges": [dict(edge) for edge in graph.edges]},
                "associations": {
                    column: evidence[source][column].to_dict()
                    for column in spec.columns
                    if column != source
                },
            },
            successor_schema,
            validate_successors,
            {"source": source},
        )
        new_nodes = [edge["to"] for edge in proposed if edge["to"] not in enqueued]
        candidate_nodes = sorted(set(graph.nodes).union(new_nodes), key=order.__getitem__)
        candidate_edges = graph.edges + proposed
        candidate = nx.DiGraph()
        candidate.add_nodes_from(candidate_nodes)
        candidate.add_edges_from((edge["from"], edge["to"]) for edge in candidate_edges)
        edge_lookup = {(edge["from"], edge["to"]): edge for edge in candidate_edges}
        cycles = []
        for cycle in nx.simple_cycles(candidate):
            if len(cycles) >= max_cycles:
                fail(f"Candidate expansion of {source!r} exceeds max_cycles={max_cycles}; no partial cycle pruning accepted")
            start = min(range(len(cycle)), key=lambda index: order[cycle[index]])
            cycles.append(cycle[start:] + cycle[:start])
        cycles.sort(key=lambda cycle: tuple(order[node] for node in cycle))
        removed: set[tuple[str, str]] = set()
        remaining = candidate.copy()
        for cycle_index, cycle in enumerate(cycles):
            pairs = [(cycle[index], cycle[(index + 1) % len(cycle)]) for index in range(len(cycle))]
            cycle_edges = [dict(edge_lookup[pair]) for pair in pairs]

            def validate_removal(content: Any) -> tuple[str, str]:
                content = _object(content)
                if not {"source", "target"}.issubset(content) or set(content) - {"source", "target", "reasoning"}:
                    raise _InvalidResponse("Cycle removal requires source and target, with only optional reasoning")
                if "reasoning" in content and not isinstance(content["reasoning"], str):
                    raise _InvalidResponse("Cycle removal reasoning must be a string")
                source_name, target_name = content.get("source"), content.get("target")
                if not isinstance(source_name, str) or not isinstance(target_name, str):
                    raise _InvalidResponse("Cycle removal requires source and target names")
                pair = (source_name, target_name)
                if pair not in pairs:
                    raise _InvalidResponse("The edge to remove must belong to the supplied cycle in its original direction")
                return pair

            removal_schema = {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "target": {"type": "string"},
                    "reasoning": {"type": "string"},
                },
                "required": ["source", "target"],
                "additionalProperties": False,
            }
            removal = ask(
                "resolve_cycle",
                CYCLE_SYSTEM,
                {
                    "cycle": list(cycle),
                    "edges": cycle_edges,
                    "graph": {"nodes": candidate_nodes, "edges": candidate_edges},
                },
                removal_schema,
                validate_removal,
                {"expanded_source": source, "cycle_index": cycle_index, "cycle": list(cycle)},
            )
            removed.add(removal)
            remaining.remove_edges_from([removal])
            # A removal can break one cycle while leaving another intact. Audit
            # the entire candidate graph after each choice, never just one path.
            events.append(
                {
                    "event": "cycle_edge_pruned",
                    "expanded_source": source,
                    "cycle": list(cycle),
                    "edge": {"from": removal[0], "to": removal[1]},
                    "dag_after_removal": nx.is_directed_acyclic_graph(remaining),
                }
            )
        if not nx.is_directed_acyclic_graph(remaining):
            fail(f"Cycle resolution left a cyclic candidate after expansion of {source!r}")
        graph = DependencyGraph(
            spec.columns,
            candidate_nodes,
            [edge for edge in candidate_edges if (edge["from"], edge["to"]) not in removed],
        )
        for node in sorted(new_nodes, key=order.__getitem__):
            queue.append(node)
            enqueued.add(node)
        events.append(
            {
                "event": "bfs_expanded",
                "source": source,
                "new_nodes": sorted(new_nodes, key=order.__getitem__),
                "proposed_edges": proposed,
                "candidate_cycles": len(cycles),
                "removed_edges": [
                    {"from": u, "to": v}
                    for u, v in sorted(removed, key=lambda pair: (order[pair[0]], order[pair[1]]))
                ],
            }
        )
    events.append(
        {
            "event": "discovery_complete",
            "nodes": list(graph.nodes),
            "edge_count": len(graph.edges),
            "layers": graph.layers(),
            "isolated_columns": graph.isolated_columns,
        }
    )
    return DiscoveryResult(graph, events)
