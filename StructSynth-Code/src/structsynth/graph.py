"""Validated dependency DAG and the paper's deterministic generation plan."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Iterable

import networkx as nx


@dataclass
class DependencyGraph:
    """A DAG over selected attributes V, with the full attribute set A separate.

    A selected node without edges is still in V. Only ``columns - nodes`` belong
    to the final completion phase. Public methods revalidate mutable inputs so
    a changed graph cannot silently produce an invalid generation plan.
    """

    columns: list[str]
    nodes: list[str]
    edges: list[dict[str, Any]]

    def __post_init__(self) -> None:
        self.columns = list(self.columns)
        self.nodes = list(self.nodes)
        self.edges = [dict(edge) for edge in self.edges]
        self._networkx()
        order = {column: index for index, column in enumerate(self.columns)}
        self.nodes.sort(key=order.__getitem__)
        self.edges.sort(key=lambda edge: (order[edge["from"]], order[edge["to"]]))

    def _networkx(self) -> nx.DiGraph:
        for label, names in (("columns", self.columns), ("nodes", self.nodes)):
            if not all(isinstance(name, str) and name for name in names):
                raise ValueError(f"Graph {label} must contain nonempty attribute names")
            if len(names) != len(set(names)):
                raise ValueError(f"Graph {label} contains duplicate attributes")
        unknown = set(self.nodes).difference(self.columns)
        if unknown:
            raise ValueError(f"Graph contains unknown attributes: {sorted(unknown)}")
        selected = set(self.nodes)
        graph = nx.DiGraph()
        graph.add_nodes_from(column for column in self.columns if column in selected)
        seen = set()
        for edge in self.edges:
            if "from" not in edge or "to" not in edge:
                raise ValueError("Every dependency edge requires 'from' and 'to'")
            source, target = edge["from"], edge["to"]
            if not isinstance(source, str) or not isinstance(target, str):
                raise ValueError("Dependency endpoints must be attribute names")
            if source not in selected or target not in selected:
                raise ValueError(f"Dependency {source!r} -> {target!r} has an endpoint outside selected V")
            if source == target:
                raise ValueError(f"Self dependency is not allowed: {source!r}")
            if (source, target) in seen:
                raise ValueError(f"Duplicate dependency: {source!r} -> {target!r}")
            seen.add((source, target))
            association = edge.get("association_value")
            if association is not None and (
                isinstance(association, bool)
                or not isinstance(association, (int, float))
                or not math.isfinite(association)
                or not 0 <= association <= 1
            ):
                raise ValueError("Edge association_value must be finite in [0, 1] or null")
            if "reasoning" in edge and not isinstance(edge["reasoning"], str):
                raise ValueError("Edge reasoning must be a string")
            graph.add_edge(source, target, **{k: v for k, v in edge.items() if k not in {"from", "to"}})
        if not nx.is_directed_acyclic_graph(graph):
            raise ValueError("Dependency graph must be acyclic; resolve cycles before synthesis")
        return graph

    @property
    def isolated_columns(self) -> list[str]:
        """Paper A_iso = A \\ V, not the set of zero-degree selected nodes."""
        self._networkx()
        selected = set(self.nodes)
        return [column for column in self.columns if column not in selected]

    def parents(self, name: str) -> list[str]:
        graph = self._networkx()
        if name not in graph:
            raise ValueError(f"Attribute {name!r} is not a selected graph node")
        parents = set(graph.predecessors(name))
        return [column for column in self.columns if column in parents]

    def layers(self) -> list[list[str]]:
        """Topological generations ordered by A; depth is the longest parent path.

        Unlike discovery BFS distance, this places every parent strictly before
        its child even when a shortcut and a longer dependency path coexist.
        """
        graph = self._networkx()
        order = {column: index for index, column in enumerate(self.columns)}
        return [
            sorted(generation, key=order.__getitem__)
            for generation in nx.topological_generations(graph)
        ]

    def local_subgraph(self, variables: Iterable[str]) -> dict[str, Any]:
        """Return the full induced graph G[L ∪ parents(L)], including parent edges."""
        graph = self._networkx()
        variables = list(variables)
        if len(variables) != len(set(variables)):
            raise ValueError("Local subgraph variables must be unique")
        unknown = set(variables).difference(graph.nodes)
        if unknown:
            raise ValueError(f"Local subgraph contains unselected attributes: {sorted(unknown)}")
        selected = set(variables)
        for variable in variables:
            selected.update(graph.predecessors(variable))
        nodes = [column for column in self.columns if column in selected]
        return {
            "nodes": nodes,
            "edges": [
                dict(edge)
                for edge in self.edges
                if edge["from"] in selected and edge["to"] in selected
            ],
        }

    def to_dict(self) -> dict[str, Any]:
        self._networkx()
        return {
            "schema_version": 1,
            "columns": list(self.columns),
            "nodes": list(self.nodes),
            "edges": [dict(edge) for edge in self.edges],
            "layers": self.layers(),
            "isolated_columns": self.isolated_columns,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any], columns: list[str] | None = None) -> DependencyGraph:
        """Load explicit V and recompute every derived generation property.

        For legacy artifacts pass the dataset columns when ``columns`` is not
        stored. Explicit legacy nodes are preserved: membership cannot safely be
        inferred from degree, because the old discovery pre-added every column.
        """
        if not isinstance(data, dict):
            raise ValueError("Graph artifact must be a JSON object")
        version = data.get("schema_version")
        if version is not None and (type(version) is not int or version != 1):
            raise ValueError(f"Unsupported graph schema version: {version!r}")
        declared_columns = data.get("columns")
        if columns is not None and declared_columns is not None and list(columns) != declared_columns:
            raise ValueError("Graph columns differ from dataset columns or their order")
        actual_columns = columns if columns is not None else declared_columns
        if actual_columns is None:
            raise ValueError("Graph artifact has no attribute schema; provide columns explicitly")
        if not isinstance(actual_columns, list):
            raise ValueError("Graph columns must be an explicit list")
        if not isinstance(data.get("nodes"), list) or not isinstance(data.get("edges"), list):
            raise ValueError("Graph artifact requires explicit nodes and edges lists")
        # Ignore obsolete hierarchical_structure and any persisted layers:
        # only the validated edges determine the topological plan.
        return cls(list(actual_columns), list(data["nodes"]), list(data["edges"]))
