import json

import pandas as pd
import pytest

from structsynth.discovery import DiscoveryError, discover_structure
from structsynth.llm import BudgetExceeded, LLMConfigurationError, LLMResponse, LLMResponseError, LLMTransportError
from structsynth.schema import DatasetSpec


class ScriptedClient:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []

    def complete(self, request):
        self.requests.append(request)
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return LLMResponse(response)


def fixture(columns=("A", "B", "C", "D", "outside")):
    train = pd.DataFrame({column: [1, 2, 3, 4] for column in columns})
    spec = DatasetSpec("test", list(columns), columns[-1], "regression", [])
    return train, spec


def successors(*names):
    return {"successors": [{"target": name, "reasoning": f"Evidence for {name}"} for name in names]}


def diamond_responses():
    return [
        {"source_nodes": ["A"]},
        successors("C", "B"),  # Deliberately reverse schema order.
        successors("D"),
        successors("D"),
        successors("A"),
    ]


def test_bfs_requests_include_examples_current_graph_and_all_associations():
    train, spec = fixture()
    examples = train.iloc[[1, 3]]
    client = ScriptedClient([{"source_nodes": ["A"]}, successors("B"), successors()])
    result = discover_structure(train, spec, client, examples=examples)
    assert result.graph.nodes == ["A", "B"]
    assert result.graph.isolated_columns == ["C", "D", "outside"]
    assert result.graph.layers() == [["A"], ["B"]]
    assert [r.purpose for r in client.requests] == ["source_nodes", "direct_successors", "direct_successors"]
    source, expansion_a, expansion_b = client.requests
    assert source.payload["examples"] == examples.to_dict("records")
    assert expansion_a.payload["examples"] == examples.to_dict("records")
    assert expansion_a.payload["graph"] == {"nodes": ["A"], "edges": []}
    assert set(expansion_a.payload["associations"]) == set(spec.columns) - {"A"}
    assert expansion_a.payload["associations"]["B"]["n_observations"] == len(train)
    assert expansion_b.payload["graph"]["edges"][0]["from"] == "A"
    assert expansion_b.payload["graph"]["edges"][0]["to"] == "B"
    json.dumps(result.events, allow_nan=False)


def test_all_overlapping_cycles_are_resolved_with_each_new_edge_in_prompt():
    train, spec = fixture()
    client = ScriptedClient(diamond_responses() + [
        {"source": "A", "target": "B"},
        {"source": "C", "target": "D"},
    ])
    result = discover_structure(train, spec, client)
    expansions = [r.payload["source"] for r in client.requests if r.purpose == "direct_successors"]
    assert expansions == ["A", "B", "C", "D"]
    resolutions = [r for r in client.requests if r.purpose == "resolve_cycle"]
    assert [r.payload["cycle"] for r in resolutions] == [["A", "B", "D"], ["A", "C", "D"]]
    assert all(any(e["from"] == "D" and e["to"] == "A" and e["reasoning"] for e in r.payload["edges"]) for r in resolutions)
    pruned = [e for e in result.events if e["event"] == "cycle_edge_pruned"]
    assert [e["dag_after_removal"] for e in pruned] == [False, True]
    assert result.graph.layers() == [["B"], ["D"], ["A"], ["C"]]
    # Initial source choices may acquire parents after reasoned expansion.
    assert result.graph.parents("A") == ["D"]
    assert result.graph.isolated_columns == ["outside"]


def test_paper_union_of_removals_may_choose_same_shared_edge_for_both_cycles():
    train, spec = fixture()
    client = ScriptedClient(diamond_responses() + [
        {"source": "D", "target": "A"},
        {"source": "D", "target": "A"},
    ])
    result = discover_structure(train, spec, client)
    assert result.graph.layers() == [["A"], ["B", "C"], ["D"]]
    assert len(result.graph.edges) == 4
    assert len([r for r in client.requests if r.purpose == "resolve_cycle"]) == 2


def test_cycle_removal_must_be_on_exact_cycle_even_if_edge_is_elsewhere_in_graph():
    train, spec = fixture()
    client = ScriptedClient(diamond_responses() + [
        {"source": "C", "target": "D"},  # Existing, but not in first cycle A-B-D.
        {"source": "A", "target": "B"},
        {"source": "C", "target": "D"},
    ])
    result = discover_structure(train, spec, client, max_response_attempts=2)
    invalid = [e for e in result.events if e["event"] == "invalid_response"]
    assert len(invalid) == 1
    assert invalid[0]["purpose"] == "resolve_cycle"
    assert "supplied cycle" in invalid[0]["reason"]
    retries = [r for r in client.requests if "validation_error" in r.payload]
    assert len(retries) == 1
    assert result.graph.layers() == [["B"], ["D"], ["A"], ["C"]]


def test_cycle_count_limit_fails_before_partial_cycle_resolution():
    train, spec = fixture()
    client = ScriptedClient(diamond_responses())
    with pytest.raises(DiscoveryError, match="max_cycles=1") as caught:
        discover_structure(train, spec, client, max_cycles=1)
    assert not any(r.purpose == "resolve_cycle" for r in client.requests)
    assert caught.value.partial_graph["layers"] == [["A"], ["B", "C"], ["D"]]
    assert caught.value.events[-1]["event"] == "discovery_failed"


def test_empty_roots_is_explicit_all_completion_plan_not_fabricated_graph():
    train, spec = fixture()
    client = ScriptedClient([{"source_nodes": []}])
    result = discover_structure(train, spec, client)
    assert result.graph.nodes == []
    assert result.graph.isolated_columns == spec.columns
    assert len(client.requests) == 1


def test_selected_root_without_edges_stays_selected():
    train, spec = fixture()
    client = ScriptedClient([{"source_nodes": ["A"]}, successors()])
    result = discover_structure(train, spec, client)
    assert result.graph.layers() == [["A"]]
    assert result.graph.isolated_columns == ["B", "C", "D", "outside"]


def test_invalid_initial_response_retries_with_feedback_and_audit():
    train, spec = fixture()
    client = ScriptedClient([{"source_nodes": ["hallucinated"]}, {"source_nodes": ["A"]}, successors()])
    result = discover_structure(train, spec, client)
    assert "validation_error" in client.requests[1].payload
    assert result.events[0]["event"] == "invalid_response"
    assert result.events[0]["response"] == {"source_nodes": ["hallucinated"]}


def test_invalid_successor_batch_does_not_commit_its_other_valid_edges():
    train, spec = fixture()
    client = ScriptedClient([{"source_nodes": ["A"]}, successors("B", "unknown"), successors()])
    result = discover_structure(train, spec, client)
    assert result.graph.nodes == ["A"]
    assert result.graph.edges == []


@pytest.mark.parametrize("response", [
    successors("A"),
    successors("B", "B"),
    {"successors": [{"target": "B", "reasoning": "  "}]},
    {"successors": "B"},
    {"successors": [{"target": ["B"], "reasoning": "invalid name type"}]},
    {"successors": [], "unexpected": True},
    {"successors": [{"target": "B", "reasoning": "dependency", "source": "C"}]},
])
def test_persistent_malformed_effects_fail_at_bound_with_last_valid_graph(response):
    train, spec = fixture()
    client = ScriptedClient([{"source_nodes": ["A"]}, response, response])
    with pytest.raises(DiscoveryError, match="2 response attempts") as caught:
        discover_structure(train, spec, client, max_response_attempts=2)
    assert len(client.requests) == 3
    assert caught.value.partial_graph["nodes"] == ["A"]
    assert caught.value.partial_graph["edges"] == []
    assert sum(e["event"] == "invalid_response" for e in caught.value.events) == 2


def test_model_json_errors_are_bounded_and_retried():
    train, spec = fixture()
    client = ScriptedClient([LLMResponseError("bad JSON"), {"source_nodes": []}])
    result = discover_structure(train, spec, client)
    assert result.graph.nodes == []
    assert result.events[0]["reason"] == "bad JSON"


@pytest.mark.parametrize("error", [BudgetExceeded("limit"), LLMConfigurationError("missing model"), LLMTransportError("HTTP attempts exhausted")])
def test_provider_abort_is_not_content_retried_and_retains_audit(error):
    train, spec = fixture()
    client = ScriptedClient([error])
    with pytest.raises(type(error)) as caught:
        discover_structure(train, spec, client)
    assert len(client.requests) == 1
    assert caught.value.events[-1]["event"] == "discovery_aborted"
    assert caught.value.partial_graph["nodes"] == []


def test_examples_from_test_or_external_data_are_rejected_before_model_call():
    train, spec = fixture()
    client = ScriptedClient([])
    with pytest.raises(ValueError, match="row subset"):
        discover_structure(train, spec, client, examples=train + 100)
    assert not client.requests


def test_few_shot_row_multiplicity_cannot_exceed_training_subset():
    train, spec = fixture()
    client = ScriptedClient([])
    with pytest.raises(ValueError, match="row subset"):
        discover_structure(train, spec, client, examples=pd.concat([train.iloc[[0]], train.iloc[[0]]]))
    assert not client.requests


def test_examples_preserve_training_float_precision():
    train, spec = fixture()
    train = train.astype(float)
    train.loc[0, "A"] = 1.1234567890123457
    client = ScriptedClient([{"source_nodes": []}])
    discover_structure(train, spec, client, examples=train.iloc[[0]])
    assert client.requests[0].payload["examples"][0]["A"] == train.loc[0, "A"]


def test_boolean_true_cannot_impersonate_numeric_training_value_one():
    train, spec = fixture()
    examples = train.iloc[[0]].copy()
    examples["A"] = True
    with pytest.raises(ValueError, match="row subset"):
        discover_structure(train, spec, ScriptedClient([]), examples=examples)


def test_explicit_categorical_and_boolean_metadata_choose_association_measures():
    train = pd.DataFrame({"code": [0, 0, 1, 1], "flag": [True, False, True, False], "value": [1, 2, 3, 4]})
    spec = DatasetSpec("test", list(train.columns), "value", "regression", ["code"], boolean_columns=["flag"])
    client = ScriptedClient([{"source_nodes": ["code"]}, successors()])
    discover_structure(train, spec, client)
    evidence = client.requests[-1].payload["associations"]
    assert evidence["value"]["method"] == "correlation_ratio"
    assert evidence["flag"]["method"] == "cramers_v_bias_corrected"


def test_numeric_classification_target_is_categorical_in_public_api():
    train = pd.DataFrame({"feature": [1, 2, 3, 4], "label": [0, 0, 1, 1]})
    spec = DatasetSpec("test", list(train.columns), "label", "classification", [])
    client = ScriptedClient([{"source_nodes": ["feature"]}, successors()])
    discover_structure(train, spec, client)
    assert client.requests[-1].payload["associations"]["label"]["method"] == "correlation_ratio"


def test_source_extra_keys_are_rejected_consistently_with_response_schema():
    train, spec = fixture()
    client = ScriptedClient([{"source_nodes": [], "extra": 1}])
    with pytest.raises(DiscoveryError, match="exactly source_nodes"):
        discover_structure(train, spec, client, max_response_attempts=1)


@pytest.mark.parametrize("invalid", [
    {"source": "A", "target": "B", "reasoning": 123},
    {"source": "A", "target": "B", "extra": True},
])
def test_invalid_cycle_response_shape_preserves_last_acyclic_state(invalid):
    train, spec = fixture()
    client = ScriptedClient(diamond_responses() + [invalid])
    with pytest.raises(DiscoveryError) as caught:
        discover_structure(train, spec, client, max_response_attempts=1)
    assert caught.value.partial_graph["layers"] == [["A"], ["B", "C"], ["D"]]
