"""Cross-module recovery checks with real process exits and offline transports."""

import json
import os
from pathlib import Path
import selectors
import subprocess
import sys
from urllib.error import URLError

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from structsynth.artifacts import atomic_json, file_lock
from structsynth.config import DataConfig, EvaluationConfig, ExperimentConfig, GenerationConfig, LLMConfig
from structsynth.generation import GenerationError, GraphSynthesizer
from structsynth.graph import DependencyGraph
from structsynth.llm import (BudgetExceeded, LLMRequest, OpenAICompatibleClient,
                             ReplayClient, UsageLedger)
from structsynth.pipeline import experiment_dir, experiment_identity, run_experiment
from structsynth.schema import DatasetSpec


def child_environment():
    environment = os.environ.copy()
    source = str(Path(__file__).resolve().parents[1] / "src")
    environment["PYTHONPATH"] = source + os.pathsep + environment.get("PYTHONPATH", "")
    return environment


def basic_request():
    return LLMRequest("recovery-test", "Return JSON.", {"value": 1}, request_id="recovery-1")


@pytest.mark.parametrize("budget", ["request", "token"])
def test_process_exit_during_http_preserves_pending_request_budget(tmp_path, budget):
    path = tmp_path / "requests.jsonl"
    script = """
import os, sys
from structsynth.config import LLMConfig
from structsynth.llm import LLMRequest, OpenAICompatibleClient, UsageLedger
config = LLMConfig(request_limit=1 if sys.argv[2] == 'request' else 10,
                   token_limit=100 if sys.argv[2] == 'token' else None)
def crash_after_reservation(body):
    os._exit(17)
client = OpenAICompatibleClient(config, ledger=UsageLedger(sys.argv[1]),
                                transport=crash_after_reservation)
client.complete(LLMRequest('recovery-test', 'Return JSON.', {'value': 1}, request_id='recovery-1'))
"""
    child = subprocess.run([sys.executable, "-c", script, str(path), budget],
                           env=child_environment(), capture_output=True, text=True, timeout=15)
    assert child.returncode == 17, child.stderr
    records = [json.loads(line) for line in path.read_text().splitlines()]
    assert len(records) == 1
    assert records[0]["status"] == "pending"
    restored = UsageLedger(path)
    assert restored.summary()["requests"] == 1
    assert restored.summary()["requests_with_unknown_usage"] == 1
    assert restored.summary()["total_tokens"] is None
    config = LLMConfig(request_limit=1 if budget == "request" else 10,
                       token_limit=100 if budget == "token" else None)
    client = OpenAICompatibleClient(config, ledger=restored,
                                    transport=lambda body: pytest.fail("A crashed attempt must remain charged"))
    with pytest.raises(BudgetExceeded, match="Request limit" if budget == "request" else "unknown usage"):
        client.complete(basic_request())


@pytest.mark.parametrize("torn_utf8", [False, True])
def test_incomplete_final_ledger_write_keeps_the_durable_pending_attempt(tmp_path, torn_utf8):
    path = tmp_path / "requests.jsonl"
    config = LLMConfig(request_limit=1)
    ledger = UsageLedger(path)
    ticket = ledger.reserve(config, {"request_key": basic_request().key})
    # A process can exit while appending the terminal event after its request
    # reservation was fsynced. Only the incomplete tail may be discarded.
    tail = ('{"attempt_id":' + json.dumps(ticket) + ',"status":"ok","usage":').encode()
    with path.open("ab") as handle:
        handle.write(tail + (b'"\xe4\xb8' if torn_utf8 else b''))
    restored = UsageLedger(path)
    assert restored.summary()["requests"] == 1
    assert restored.records[0]["status"] == "pending"
    with pytest.raises(BudgetExceeded, match="Request limit"):
        restored.reserve(config)


def test_complete_last_ledger_event_without_newline_is_kept_before_next_append(tmp_path):
    path = tmp_path / "requests.jsonl"
    initial = {"attempt_id": "complete", "status": "ok", "usage": {"total_tokens": 12}}
    path.write_text(json.dumps(initial))
    restored = UsageLedger(path)
    assert restored.summary()["successful_requests"] == 1
    restored.reserve(LLMConfig(request_limit=2))
    reloaded = UsageLedger(path)
    assert reloaded.summary()["requests"] == 2
    assert reloaded.summary()["known_total_tokens"] == 12


def test_corrupt_interior_ledger_record_is_not_silently_dropped(tmp_path):
    path = tmp_path / "requests.jsonl"
    path.write_text('{"broken":\n{"attempt_id":"later","status":"pending"}\n')
    with pytest.raises(ValueError):
        UsageLedger(path)


@pytest.mark.skipif(os.name == "nt", reason="Pipe readiness check uses POSIX selector support")
def test_os_lock_excludes_another_process_and_releases_after_abrupt_exit(tmp_path):
    path = tmp_path / ".run.lock"
    script = """
import os, sys
from structsynth.artifacts import file_lock
with file_lock(sys.argv[1]):
    print('locked', flush=True)
    sys.stdin.read(1)
    os._exit(23)
"""
    child = subprocess.Popen([sys.executable, "-c", script, str(path)], env=child_environment(),
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        with selectors.DefaultSelector() as selector:
            selector.register(child.stdout, selectors.EVENT_READ)
            assert selector.select(timeout=10), "Child did not acquire the lock"
        assert child.stdout.readline().strip() == "locked"
        with pytest.raises(OSError):
            with file_lock(path):
                pytest.fail("A second process acquired the live owner's lock")
        child.stdin.write("x")
        child.stdin.flush()
        assert child.wait(timeout=10) == 23
        assert path.exists()
        with file_lock(path):
            pass
    finally:
        if child.poll() is None:
            child.kill()
        child.communicate(timeout=10)


def test_process_exit_before_atomic_replace_preserves_previous_artifact(tmp_path):
    path = tmp_path / "manifest.json"
    atomic_json(path, {"status": "last-durable-state"})
    script = """
import os, sys
import structsynth.artifacts as artifacts
def crash_before_replace(source, destination):
    os._exit(19)
artifacts.os.replace = crash_before_replace
artifacts.atomic_json(sys.argv[1], {'status': 'not-yet-committed'})
"""
    child = subprocess.run([sys.executable, "-c", script, str(path)], env=child_environment(),
                           capture_output=True, text=True, timeout=15)
    assert child.returncode == 19, child.stderr
    assert json.loads(path.read_text()) == {"status": "last-durable-state"}
    atomic_json(path, {"status": "resumed-and-committed"})
    assert json.loads(path.read_text()) == {"status": "resumed-and-committed"}


def generation_setup():
    frame = pd.DataFrame({"A": [1, 2], "B": [2, 3]})
    spec = DatasetSpec("recovery", list(frame), "B", "regression", [])
    graph = DependencyGraph(list(frame), list(frame), [{"from": "A", "to": "B", "reasoning": "dependency"}])
    return frame, spec, graph


def generated_provider_response(body):
    payload = json.loads(body["messages"][-1]["content"])
    rows = []
    for item in reversed(payload["conditioning_data"]):
        values = {column: item["row_id"] + 20 if column == "A" else item["values"]["A"] + 1
                  for column in payload["features_to_generate"]}
        rows.append({"row_id": item["row_id"], "values": values})
    return {"choices": [{"message": {"content": json.dumps({"rows": rows})}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 8, "completion_tokens": 4}}


@pytest.mark.parametrize("initial_failures", [1, 2])
def test_replay_preserves_transport_retry_boundaries_and_generator_identity(tmp_path, initial_failures):
    frame, spec, graph = generation_setup()
    path = tmp_path / "requests.jsonl"
    attempts = []

    def transport(body):
        attempts.append(body)
        if len(attempts) <= initial_failures:
            raise URLError("offline simulated disconnect")
        return generated_provider_response(body)

    client = OpenAICompatibleClient(LLMConfig(max_attempts=2, retry_delay=0),
                                    ledger=UsageLedger(path), transport=transport)
    expected = GraphSynthesizer(graph, spec, client, max_attempts=2).fit(frame).generate(2)
    replay = ReplayClient(path)
    assert replay.identity == client.identity
    actual = GraphSynthesizer(graph, spec, replay, max_attempts=2).fit(frame).generate(2)
    assert_frame_equal(expected, actual)
    assert replay.replayed == len(attempts) == initial_failures + 2
    records = UsageLedger(path).records
    assert records[0]["retry_scheduled"] is True
    if initial_failures == 2:
        assert records[1]["retry_scheduled"] is False
        assert records[0]["request_key"] == records[1]["request_key"]
        assert records[1]["request_key"] != records[2]["request_key"]


def test_replay_identity_allows_completed_generation_checkpoint_resume(tmp_path):
    frame, spec, graph = generation_setup()
    path = tmp_path / "requests.jsonl"
    checkpoint = tmp_path / "checkpoints"
    live = OpenAICompatibleClient(LLMConfig(max_attempts=1), ledger=UsageLedger(path),
                                  transport=generated_provider_response)
    expected = GraphSynthesizer(graph, spec, live, checkpoint_dir=checkpoint).fit(frame).generate(2)
    replay = ReplayClient(path)
    actual = GraphSynthesizer(graph, spec, replay, checkpoint_dir=checkpoint).fit(frame).generate(2)
    assert_frame_equal(expected, actual)
    assert replay.replayed == 0


def test_replay_preserves_budget_abort_between_transport_attempts(tmp_path):
    path = tmp_path / "requests.jsonl"

    def transport(body):
        raise URLError("first HTTP request fails, retry cannot reserve more budget")

    live = OpenAICompatibleClient(LLMConfig(max_attempts=2, request_limit=1, retry_delay=0),
                                  ledger=UsageLedger(path), transport=transport)
    request = basic_request()
    with pytest.raises(BudgetExceeded):
        live.complete(request)
    assert UsageLedger(path).summary()["requests"] == 1
    with pytest.raises(BudgetExceeded):
        ReplayClient(path).complete(request)


def pipeline_config(tmp_path):
    data = tmp_path / "data.csv"
    metadata = tmp_path / "metadata.json"
    pd.DataFrame({"x": list(range(20)), "label": ["yes", "no"] * 10}).to_csv(data, index=False)
    metadata.write_text(json.dumps({"name": "recovery", "target_column": "label",
                                    "task_type": "classification", "categorical_columns": ["label"]}))
    return ExperimentConfig(DataConfig("recovery", str(data), str(metadata), shots=[4], seeds=[42],
                                        example_rows=4),
                            generation=GenerationConfig(n_samples=[2]),
                            evaluation=EvaluationConfig(enabled=False),
                            output_dir=str(tmp_path / "runs"))


def test_pipeline_existing_lock_path_does_not_prevent_resume_after_owner_exits(tmp_path):
    config = pipeline_config(tmp_path)
    directory = experiment_dir(config, experiment_identity(config, 4, 42))
    directory.mkdir(parents=True)
    # A crashed process leaves the lock filename behind. Ownership belongs to
    # the OS lock, so the filename must never itself mean "still running".
    (directory / ".run.lock").write_text("stale owner")
    actual = run_experiment(config, 4, 42, stage="split")
    assert actual == directory
    assert json.loads((directory / "manifest.json").read_text())["completed_stages"] == ["split"]
    assert run_experiment(config, 4, 42, stage="split", resume=True) == directory


def test_pipeline_holds_run_lock_before_reading_or_mutating_artifacts(tmp_path):
    config = pipeline_config(tmp_path)
    directory = experiment_dir(config, experiment_identity(config, 4, 42))
    with file_lock(directory / ".run.lock"):
        with pytest.raises(OSError):
            run_experiment(config, 4, 42, stage="split")
        assert not (directory / "manifest.json").exists()


def test_pipeline_resume_rejects_modified_completed_split_artifact(tmp_path):
    config = pipeline_config(tmp_path)
    directory = run_experiment(config, 4, 42, stage="split")
    with (directory / "train.csv").open("a") as handle:
        handle.write("123,yes\n")
    with pytest.raises(ValueError, match="missing or modified"):
        run_experiment(config, 4, 42, stage="split", resume=True)


def offline_pipeline_factory(calls, *, invalid_generation=False):
    def factory(stage_name, config, ledger, train, spec):
        def transport(body):
            payload = json.loads(body["messages"][-1]["content"])
            calls.append((stage_name, payload))
            if stage_name == "discovery":
                if "source" not in payload:
                    content = {"source_nodes": ["x"]}
                elif payload["source"] == "x":
                    content = {"successors": [{"target": "label", "reasoning": "A useful generation plan"}]}
                else:
                    content = {"successors": []}
            elif invalid_generation:
                content = {"rows": []}
            else:
                content = {"rows": []}
                for item in payload["conditioning_data"]:
                    values = {column: payload["column_schema"][column]["enum"][0] if column == "label"
                              else item["row_id"] + 100 for column in payload["features_to_generate"]}
                    content["rows"].append({"row_id": item["row_id"], "values": values})
            return {"choices": [{"message": {"content": json.dumps(content)}, "finish_reason": "stop"}],
                    "usage": {"prompt_tokens": 8, "completion_tokens": 4}}

        return OpenAICompatibleClient(config, ledger=ledger, transport=transport)
    return factory


def test_complete_offline_pipeline_resume_reuses_artifacts_without_clients(tmp_path):
    config = pipeline_config(tmp_path)
    calls = []
    directory = run_experiment(config, 4, 42, client_factory=offline_pipeline_factory(calls),
                                backend="offline-recovery")
    manifest = json.loads((directory / "manifest.json").read_text())
    assert manifest["status"] == "complete"
    assert manifest["completed_stages"] == ["split", "discover", "generate"]
    assert sum(stage == "discovery" for stage, _ in calls) == 3
    assert sum(stage == "generation" for stage, _ in calls) == 2
    assert [row["x"] for row in json.loads((directory / "synthetic.json").read_text())] == [100, 101]
    assert run_experiment(config, 4, 42, resume=True, backend="offline-recovery",
                          client_factory=lambda *args: pytest.fail("A complete run must not construct model clients")) == directory
    usage = json.loads((directory / "usage.json").read_text())
    assert usage["discovery"]["requests"] == 3
    assert usage["generation"]["requests"] == 2


def test_pipeline_exhausted_generation_resume_preserves_budget_and_failure_events(tmp_path):
    config = pipeline_config(tmp_path)
    config.generation.max_attempts = 1
    calls = []
    factory = offline_pipeline_factory(calls, invalid_generation=True)
    with pytest.raises(GenerationError, match="exhausted"):
        run_experiment(config, 4, 42, client_factory=factory, backend="offline-recovery")
    directory = experiment_dir(config, experiment_identity(config, 4, 42, backend="offline-recovery"))
    first_calls = len(calls)
    with pytest.raises(GenerationError, match="exhausted"):
        run_experiment(config, 4, 42, resume=True, client_factory=factory, backend="offline-recovery")
    assert len(calls) == first_calls
    manifest = json.loads((directory / "manifest.json").read_text())
    assert manifest["status"] == "failed"
    assert manifest["completed_stages"] == ["split", "discover"]
    assert not (directory / "synthetic.json").exists()
    assert UsageLedger(directory / "generation_requests.jsonl").summary()["requests"] == 1
    details = json.loads((directory / "failure_details.json").read_text())
    assert details["events"]
    assert any(event["kind"] == "response_validated" for event in details["events"])
