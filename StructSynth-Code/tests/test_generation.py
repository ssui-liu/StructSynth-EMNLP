import json
import threading
from dataclasses import replace

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from structsynth.config import LLMConfig
from structsynth.generation import CheckpointError, GenerationError, GraphSynthesizer
from structsynth.graph import DependencyGraph
from structsynth.llm import (BudgetExceeded, LLMConfigurationError, LLMResponse,
                             LLMResponseError, LLMTransportError,
                             OpenAICompatibleClient, TokenUsage, UsageLedger)
from structsynth.schema import DatasetSpec


class MockClient:
    identity = {"kind": "generation-test", "model": "deterministic"}

    def __init__(self, handler):
        self.handler = handler
        self.requests = []
        self.lock = threading.Lock()

    def complete(self, request):
        with self.lock:
            self.requests.append(request)
        content = self.handler(request)
        return LLMResponse(content, TokenUsage(10, 5), "mock")


def edge(source, target):
    return {"from": source, "to": target, "reasoning": "dependency"}


def row(row_id, **values):
    return {"row_id": row_id, "values": values}


def linear_setup():
    frame = pd.DataFrame({"A": [1, 2, 3], "B": [2, 3, 4]})
    spec = DatasetSpec("linear", list(frame), "B", "regression", [])
    graph = DependencyGraph(list(frame), list(frame), [edge("A", "B")])
    return frame, spec, graph


def linear_response(request):
    columns = request.payload["features_to_generate"]
    return {"rows": [row(item["row_id"], **{
        column: item["row_id"] * 10 if column == "A" else item["values"]["A"] + 2
        for column in columns}) for item in reversed(request.payload["conditioning_data"])]}


def test_paper_layers_condition_on_all_previous_values_and_complete_outside_graph():
    frame = pd.DataFrame({"A": [1, 2], "B": [2, 3], "C": [3, 4],
                          "W": [5, 6], "label": ["yes", "no"]})
    spec = DatasetSpec("paper", list(frame), "label", "classification", ["label"])
    graph = DependencyGraph(list(frame), ["A", "B", "C", "W"],
                            [edge("A", "B"), edge("A", "C"), edge("B", "C")])

    def respond(request):
        payload = request.payload
        result = []
        for item in reversed(payload["conditioning_data"]):
            values = {}
            for column in payload["features_to_generate"]:
                if column == "A":
                    values[column] = 100 + item["row_id"]
                elif column == "W":
                    values[column] = 999
                elif column == "B":
                    values[column] = item["values"]["A"] + 1
                elif column == "C":
                    values[column] = item["values"]["B"] + 1
                else:
                    values[column] = "yes"
            result.append(row(item["row_id"], **values))
        return {"rows": result}

    client = MockClient(respond)
    result = GraphSynthesizer(graph, spec, client).fit(frame).generate(2)
    assert result.to_dict("records") == [
        {"A": 100, "B": 101, "C": 102, "W": 999, "label": "yes"},
        {"A": 101, "B": 102, "C": 103, "W": 999, "label": "yes"}]
    requests = client.requests
    assert [request.payload["features_to_generate"] for request in requests] == [
        ["A", "W"], ["B"], ["C"], ["label"]]
    assert requests[-1].purpose == "generation.isolated"
    assert requests[0].payload["conditioning_data"] == [row(0), row(1)]
    assert set(requests[1].payload["conditioning_data"][0]["values"]) == {"A", "W"}
    assert set(requests[2].payload["conditioning_data"][0]["values"]) == {"A", "W", "B"}
    assert requests[2].payload["local_subgraph"]["nodes"] == ["A", "B", "C"]
    assert requests[2].payload["local_subgraph"]["edges"] == graph.edges
    assert set(requests[2].payload["examples"][0]) == {"A", "B", "C"}
    assert set(requests[-1].payload["examples"][0]) == set(frame)
    assert set(requests[-1].payload["conditioning_data"][0]["values"]) == {"A", "B", "C", "W"}


def test_out_of_order_partial_responses_keep_identity_across_retry():
    frame, spec, graph = linear_setup()

    def respond(request):
        if request.payload["stage_index"] == 1 and request.payload["attempt"] == 1:
            return {"rows": [row(2, B=22), row(0, B="wrong type")]}
        return linear_response(request)

    client = MockClient(respond)
    generator = GraphSynthesizer(graph, spec, client, max_attempts=2).fit(frame)
    result = generator.generate(3)
    assert result.to_dict("records") == [{"A": 0, "B": 2}, {"A": 10, "B": 12}, {"A": 20, "B": 22}]
    retry = client.requests[-1].payload
    assert retry["requested_row_ids"] == [0, 1]
    assert retry["conditioning_data"] == [row(0, A=0), row(1, A=10)]
    assert any("JSON type integer" in error for error in retry["validation_feedback"])
    assert generator.events[-1]["accepted_row_ids"] == [0, 1]


@pytest.mark.parametrize("bad", [
    {"rows": [row(0, A=0), row(0, A=1)]},
    {"rows": [row(0, A=0), row(4, A=1)]},
    {"rows": [row(True, A=0)]},
    {"rows": [row("0", A=0)]},
    {"rows": [{"row_id": 0, "values": {"A": 0}, "metadata": "extra"}]},
    {"rows": [row(0, A=0)], "metadata": "extra"},
    [row(0, A=0)],
])
def test_ambiguous_envelopes_reject_entire_response(bad):
    frame, spec, graph = linear_setup()

    def respond(request):
        return bad if request.payload["stage_index"] == 0 and request.payload["attempt"] == 1 else linear_response(request)

    client = MockClient(respond)
    result = GraphSynthesizer(graph, spec, client, max_attempts=2).fit(frame).generate(2)
    assert len(result) == 2
    assert client.requests[1].payload["requested_row_ids"] == [0, 1]


@pytest.mark.parametrize("values", [
    {}, {"B": 1, "A": 0}, {"B": None}, {"B": True}, {"B": "12"},
    {"B": 12.0}, {"B": float("nan")}, {"B": float("inf")}, {"B": 2 ** 64},
])
def test_invalid_values_never_bypass_validation_on_last_attempt(values):
    frame, spec, graph = linear_setup()

    def respond(request):
        if request.payload["stage_index"] == 0:
            return linear_response(request)
        return {"rows": [{"row_id": 0, "values": values}]}

    client = MockClient(respond)
    with pytest.raises(GenerationError, match="exhausted 2 attempts") as error:
        GraphSynthesizer(graph, spec, client, max_attempts=2).fit(frame).generate(1)
    assert error.value.row_ids == [0]
    assert error.value.stage_index == 1
    assert len(client.requests) == 3


def test_empty_responses_terminate_without_returning_partial_table():
    frame, spec, graph = linear_setup()
    client = MockClient(lambda request: {"rows": []})
    with pytest.raises(GenerationError, match="exhausted 3 attempts"):
        GraphSynthesizer(graph, spec, client, max_attempts=3).fit(frame).generate(2)
    assert len(client.requests) == 3


@pytest.mark.parametrize("error_class", [LLMResponseError, LLMTransportError])
def test_retryable_client_failures_consume_finite_attempts(error_class):
    frame, spec, graph = linear_setup()

    def respond(request):
        raise error_class("scripted failure")

    client = MockClient(respond)
    with pytest.raises(GenerationError, match="exhausted 2 attempts"):
        GraphSynthesizer(graph, spec, client, max_attempts=2).fit(frame).generate(1)
    assert len(client.requests) == 2


@pytest.mark.parametrize("error_class", [BudgetExceeded, LLMConfigurationError])
def test_budget_and_configuration_errors_propagate_without_retry(error_class):
    frame, spec, graph = linear_setup()

    def respond(request):
        raise error_class("stop now")

    client = MockClient(respond)
    with pytest.raises(error_class, match="stop now"):
        GraphSynthesizer(graph, spec, client, max_attempts=5).fit(frame).generate(1)
    assert len(client.requests) == 1


def test_completed_checkpoints_resume_without_model_calls(tmp_path):
    frame, spec, graph = linear_setup()
    client = MockClient(linear_response)
    first = GraphSynthesizer(graph, spec, client, batch_size=2, checkpoint_dir=tmp_path).fit(frame).generate(3)
    assert len(client.requests) == 4
    resumed_client = MockClient(lambda request: pytest.fail("Completed batches must not be regenerated"))
    resumed = GraphSynthesizer(graph, spec, resumed_client, batch_size=2, checkpoint_dir=tmp_path, max_workers=2).fit(frame)
    assert_frame_equal(first, resumed.generate(3))
    assert sum(event["kind"] == "checkpoint_resumed" for event in resumed.events) == 4


def test_interruption_preserves_valid_rows_context_and_attempt_budget(tmp_path):
    frame, spec, graph = linear_setup()

    def interrupted(request):
        if request.payload["stage_index"] == 0:
            return linear_response(request)
        if request.payload["attempt"] == 1:
            return {"rows": [row(2, B=22)]}
        raise KeyboardInterrupt("simulated process interruption")

    with pytest.raises(KeyboardInterrupt):
        GraphSynthesizer(graph, spec, MockClient(interrupted), max_attempts=3,
                         checkpoint_dir=tmp_path).fit(frame).generate(3)
    resumed_client = MockClient(linear_response)
    resumed = GraphSynthesizer(graph, spec, resumed_client, max_attempts=3, checkpoint_dir=tmp_path).fit(frame)
    result = resumed.generate(3)
    assert result["B"].tolist() == [2, 12, 22]
    assert len(resumed_client.requests) == 1
    request = resumed_client.requests[0]
    assert request.payload["attempt"] == 3
    assert request.payload["requested_row_ids"] == [0, 1]
    assert request.payload["conditioning_data"] == [row(0, A=0), row(1, A=10)]
    assert request.request_id.endswith(":a003")


def test_resume_does_not_reset_exhausted_retry_budget(tmp_path):
    frame, spec, graph = linear_setup()
    first = GraphSynthesizer(graph, spec, MockClient(lambda request: {"rows": []}),
                             max_attempts=2, checkpoint_dir=tmp_path).fit(frame)
    with pytest.raises(GenerationError):
        first.generate(1)
    client = MockClient(lambda request: pytest.fail("An exhausted checkpoint must not call the model"))
    with pytest.raises(GenerationError, match="exhausted 2 attempts"):
        GraphSynthesizer(graph, spec, client, max_attempts=2, checkpoint_dir=tmp_path).fit(frame).generate(1)


@pytest.mark.parametrize("changed", ["train", "examples", "model", "graph", "spec", "seed", "count", "batch_size", "max_attempts"])
def test_checkpoints_reject_input_or_config_changes(tmp_path, changed):
    frame, spec, graph = linear_setup()
    GraphSynthesizer(graph, spec, MockClient(linear_response), checkpoint_dir=tmp_path).fit(frame).generate(2)
    kwargs = {"checkpoint_dir": tmp_path}
    examples = None
    count = 2
    client = MockClient(lambda request: pytest.fail("Mismatched checkpoints must fail before requests"))
    if changed == "train":
        frame.loc[0, "A"] = 99
    elif changed == "examples":
        examples = frame.iloc[:1]
    elif changed == "model":
        client.identity = {"kind": "generation-test", "model": "other"}
    elif changed == "graph":
        graph = DependencyGraph(list(frame), list(frame), [])
    elif changed == "spec":
        spec = replace(spec, task="new task")
    elif changed == "seed":
        kwargs["seed"] = 17
    elif changed == "count":
        count = 1
    elif changed == "batch_size":
        kwargs["batch_size"] = 1
    elif changed == "max_attempts":
        kwargs["max_attempts"] = 7
    with pytest.raises(CheckpointError, match="mismatch"):
        GraphSynthesizer(graph, spec, client, **kwargs).fit(frame, examples).generate(count)


@pytest.mark.parametrize("changed", ["type", "row_id", "context", "attempts", "completed"])
def test_corrupt_checkpoints_are_revalidated(tmp_path, changed):
    frame, spec, graph = linear_setup()
    GraphSynthesizer(graph, spec, MockClient(linear_response), checkpoint_dir=tmp_path).fit(frame).generate(1)
    path = tmp_path / "stage_001_batch_000000.json"
    saved = json.loads(path.read_text())
    if changed == "type":
        saved["rows"][0]["values"]["B"] = "invalid"
    elif changed == "row_id":
        saved["rows"][0]["row_id"] = 99
    elif changed == "context":
        saved["context_sha256"] = "not-the-parent-values"
    elif changed == "attempts":
        saved["attempts"] = True
    else:
        saved["completed"] = False
    path.write_text(json.dumps(saved))
    client = MockClient(lambda request: pytest.fail("Corrupt checkpoints must not issue requests"))
    with pytest.raises(CheckpointError):
        GraphSynthesizer(graph, spec, client, checkpoint_dir=tmp_path).fit(frame).generate(1)


def test_nullable_numeric_boolean_and_training_category_validation():
    frame = pd.DataFrame({"amount": [1.25, None], "flag": [True, False], "label": [0, 1]})
    spec = DatasetSpec("types", list(frame), "label", "classification", [],
                       boolean_columns=["flag"], nullable_columns=["amount"])
    graph = DependencyGraph(list(frame), [], [])

    def respond(request):
        if request.payload["attempt"] == 1:
            return {"rows": [row(0, amount=None, flag=True, label=9)]}
        return {"rows": [row(0, amount=None, flag=True, label=1)]}

    client = MockClient(respond)
    result = GraphSynthesizer(graph, spec, client, max_attempts=2).fit(frame).generate(1)
    assert pd.isna(result.loc[0, "amount"])
    assert bool(result.loc[0, "flag"])
    assert result.loc[0, "label"] == 1
    assert "outside the allowed categories" in client.requests[-1].payload["validation_feedback"][0]
    assert client.requests[0].payload["column_schema"]["label"]["enum"] == [0, 1]


def test_unseen_feature_category_is_allowed_but_unknown_target_is_retried():
    frame = pd.DataFrame({"animal": ["cat", "dog"], "label": ["yes", "no"]})
    spec = DatasetSpec("open-feature-domain", list(frame), "label", "classification", list(frame))
    graph = DependencyGraph(list(frame), [], [])

    def respond(request):
        label = "unknown" if request.payload["attempt"] == 1 else "yes"
        return {"rows": [row(0, animal="fox", label=label)]}

    client = MockClient(respond)
    result = GraphSynthesizer(graph, spec, client, max_attempts=2).fit(frame).generate(1)
    assert result.to_dict("records") == [{"animal": "fox", "label": "yes"}]
    assert len(client.requests) == 2
    schema = client.requests[0].payload["column_schema"]
    assert schema["animal"]["observed_values"] == ["cat", "dog"]
    assert "enum" not in schema["animal"]
    assert schema["label"]["enum"] == ["yes", "no"]
    properties = client.requests[0].response_schema["properties"]["rows"]["items"]["properties"]["values"]["properties"]
    assert "enum" not in properties["animal"]
    assert any("label is outside" in error for error in client.requests[1].payload["validation_feedback"])


def test_explicit_feature_category_domain_remains_a_hard_constraint():
    frame = pd.DataFrame({"animal": ["cat", "dog"], "label": ["yes", "no"]})
    spec = DatasetSpec("explicit-feature-domain", list(frame), "label", "classification", list(frame),
                       categories={"animal": ["cat", "dog"]})
    graph = DependencyGraph(list(frame), [], [])
    client = MockClient(lambda request: {"rows": [row(0, animal="fox", label="yes")]})
    with pytest.raises(GenerationError, match="animal is outside the allowed categories"):
        GraphSynthesizer(graph, spec, client, max_attempts=1).fit(frame).generate(1)


def test_data_column_named_row_id_is_supported_inside_values():
    frame = pd.DataFrame({"row_id": [10, 20], "target": [3.0, 4.0]})
    spec = DatasetSpec("id-column", list(frame), "target", "regression", [])
    graph = DependencyGraph(list(frame), [], [])
    client = MockClient(lambda request: {"rows": [{"row_id": 0, "values": {"row_id": 300, "target": 99.5}}]})
    result = GraphSynthesizer(graph, spec, client).fit(frame).generate(1)
    assert result.to_dict("records") == [{"row_id": 300, "target": 99.5}]


def test_explicit_category_domain_supports_an_all_null_training_column():
    frame = pd.DataFrame({"A": [1, 2], "label": [None, None]})
    spec = DatasetSpec("missing-category", list(frame), "label", "classification", ["label"],
                       nullable_columns=["label"], categories={"label": ["known", "other"]})
    graph = DependencyGraph(list(frame), [], [])
    client = MockClient(lambda request: {"rows": [row(0, A=999, label="known")]})
    result = GraphSynthesizer(graph, spec, client).fit(frame).generate(1)
    assert result.to_dict("records") == [{"A": 999, "label": "known"}]


def test_json_number_category_accepts_equivalent_integer_output():
    frame = pd.DataFrame({"A": [1, 2], "label": [0.0, 1.0]})
    spec = DatasetSpec("float-label", list(frame), "label", "classification", ["label"])
    graph = DependencyGraph(list(frame), [], [])
    client = MockClient(lambda request: {"rows": [row(0, A=3, label=1)]})
    assert GraphSynthesizer(graph, spec, client).fit(frame).generate(1).loc[0, "label"] == 1.0


def test_integer_labels_accept_equivalent_numeric_enum_but_require_integer_output():
    frame = pd.DataFrame({"A": [1, 2], "label": [0, 1]})
    spec = DatasetSpec("integer-enum", list(frame), "label", "classification", ["label"],
                       categories={"label": [0.0, 1.0]})
    graph = DependencyGraph(list(frame), [], [])

    def respond(request):
        label = {1: True, 2: 1.0, 3: 1}[request.payload["attempt"]]
        return {"rows": [row(0, A=3, label=label)]}

    client = MockClient(respond)
    result = GraphSynthesizer(graph, spec, client, max_attempts=3).fit(frame).generate(1)
    assert result.loc[0, "label"] == 1
    assert str(result["label"].dtype) == "int64"
    assert len(client.requests) == 3
    assert all(any("JSON type integer" in error for error in request.payload["validation_feedback"])
               for request in client.requests[1:])


def test_unrepresentable_numeric_output_is_retried_before_assembly():
    frame = pd.DataFrame({"amount": [1.5, 2.5]})
    spec = DatasetSpec("float", list(frame), "amount", "regression", [])
    graph = DependencyGraph(list(frame), [], [])

    def respond(request):
        return {"rows": [row(0, amount=10 ** 400 if request.payload["attempt"] == 1 else 100.25)]}

    client = MockClient(respond)
    assert GraphSynthesizer(graph, spec, client, max_attempts=2).fit(frame).generate(1).loc[0, "amount"] == 100.25
    assert len(client.requests) == 2


def test_empty_graph_completes_all_columns_and_zero_samples_needs_no_requests():
    frame, spec, _ = linear_setup()
    graph = DependencyGraph(list(frame), [], [])
    client = MockClient(lambda request: {"rows": [row(0, A=7, B=8)]})
    generator = GraphSynthesizer(graph, spec, client).fit(frame)
    empty = generator.generate(0)
    assert empty.empty and list(empty) == list(frame)
    assert client.requests == []
    assert generator.generate(1).to_dict("records") == [{"A": 7, "B": 8}]
    assert client.requests[0].purpose == "generation.isolated"


def test_fit_rejects_nontraining_examples_and_unpermitted_nulls():
    frame, spec, graph = linear_setup()
    generator = GraphSynthesizer(graph, spec, MockClient(linear_response))
    with pytest.raises(ValueError, match="subset"):
        generator.fit(frame, pd.DataFrame({"A": [999], "B": [3]}))
    frame.loc[0, "A"] = None
    with pytest.raises(ValueError, match="does not allow null"):
        generator.fit(frame)


def test_mutating_fitted_graph_requires_refitting():
    frame, spec, graph = linear_setup()
    generator = GraphSynthesizer(graph, spec, MockClient(linear_response)).fit(frame)
    graph.edges.clear()
    with pytest.raises(GenerationError, match="changed after fit"):
        generator.generate(1)


def test_graph_schema_column_order_must_match_training():
    frame, spec, _ = linear_setup()
    graph = DependencyGraph(["B", "A"], ["A", "B"], [edge("A", "B")])
    with pytest.raises(ValueError, match="columns and order"):
        GraphSynthesizer(graph, spec, MockClient(linear_response)).fit(frame)


def test_checkpoint_directory_cannot_be_used_by_concurrent_generators(tmp_path):
    frame, spec, graph = linear_setup()
    started = threading.Event()
    release = threading.Event()
    failures = []

    def slow_response(request):
        started.set()
        assert release.wait(timeout=5)
        return linear_response(request)

    first = GraphSynthesizer(graph, spec, MockClient(slow_response), checkpoint_dir=tmp_path).fit(frame)

    def run_first():
        try:
            first.generate(1)
        except BaseException as error:
            failures.append(error)

    thread = threading.Thread(target=run_first)
    thread.start()
    try:
        assert started.wait(timeout=5)
        second = GraphSynthesizer(graph, spec, MockClient(linear_response), checkpoint_dir=tmp_path).fit(frame)
        with pytest.raises(CheckpointError, match="in use"):
            second.generate(1)
    finally:
        release.set()
        thread.join(timeout=5)
    assert not thread.is_alive()
    assert failures == []


def test_independent_batches_run_concurrently_with_a_barrier_between_layers():
    frame, spec, graph = linear_setup()
    barrier = threading.Barrier(2)
    lock = threading.Lock()
    active = 0
    peak = 0
    completed_roots = set()

    def respond(request):
        nonlocal active, peak
        stage = request.payload["stage_index"]
        with lock:
            active += 1
            peak = max(peak, active)
            if stage == 1:
                assert completed_roots == {0, 1, 2, 3}
        barrier.wait(timeout=5)
        response = linear_response(request)
        with lock:
            if stage == 0:
                completed_roots.update(request.payload["requested_row_ids"])
            active -= 1
        return response

    result = GraphSynthesizer(graph, spec, MockClient(respond), batch_size=1,
                              max_workers=2).fit(frame).generate(4)
    assert peak == 2
    assert result["B"].tolist() == [2, 12, 22, 32]


def test_shared_client_ledger_counts_invalid_response_and_successful_retries():
    frame, spec, graph = linear_setup()
    calls = []

    def transport(body):
        payload = json.loads(body["messages"][-1]["content"])
        calls.append(payload)
        if len(calls) == 1:
            content = {"rows": []}
        else:
            values = {column: 4 if column == "A" else 6 for column in payload["features_to_generate"]}
            content = {"rows": [row(row_id, **values) for row_id in payload["requested_row_ids"]]}
        return {"choices": [{"message": {"content": json.dumps(content)}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 11, "completion_tokens": 7}}

    ledger = UsageLedger()
    client = OpenAICompatibleClient(LLMConfig(max_attempts=1), ledger=ledger, transport=transport)
    result = GraphSynthesizer(graph, spec, client, max_attempts=2).fit(frame).generate(1)
    assert result.to_dict("records") == [{"A": 4, "B": 6}]
    assert ledger.summary()["requests"] == 3
    assert ledger.summary()["total_tokens"] == 54
    assert len({record["request"]["request_id"] for record in ledger.records}) == 3
