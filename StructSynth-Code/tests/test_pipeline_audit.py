"""Run identity, request-journal provenance and pre-payment evaluator checks."""

from dataclasses import replace
import json

import pandas as pd
import pytest
import yaml

from structsynth.cli import main
from structsynth.config import DataConfig, EvaluationConfig, ExperimentConfig, GenerationConfig, LLMConfig
from structsynth.llm import BudgetExceeded, OpenAICompatibleClient
from structsynth.pipeline import experiment_dir, experiment_identity, run_experiment


@pytest.fixture
def config(tmp_path):
    csv = tmp_path / "data.csv"
    metadata = tmp_path / "metadata.json"
    pd.DataFrame({"x": range(30), "label": ["yes", "no"] * 15}).to_csv(csv, index=False)
    metadata.write_text(json.dumps({"target_column": "label", "task_type": "classification"}))
    return ExperimentConfig(
        DataConfig("audit", str(csv), str(metadata), shots=[4], seeds=[42], example_rows=4),
        discovery_llm=LLMConfig(max_attempts=1), generation_llm=LLMConfig(max_attempts=1),
        generation=GenerationConfig(n_samples=[2], max_attempts=1), discovery_attempts=1,
        evaluation=EvaluationConfig(enabled=False, model="logistic"), output_dir=str(tmp_path / "runs"),
    )


def factory_for(calls, *, fail_stage=None):
    def factory(stage, llm_config, ledger, train, spec):
        def transport(body):
            payload = json.loads(body["messages"][-1]["content"])
            calls.append((stage, payload))
            if stage == fail_stage:
                content = {"rows": []} if stage == "generation" else {"source_nodes": ["unknown"]}
            elif stage == "discovery":
                if "source" not in payload:
                    content = {"source_nodes": ["x"]}
                elif payload["source"] == "x":
                    content = {"successors": [{"target": "label", "reasoning": "Offline test dependency"}]}
                else:
                    content = {"successors": []}
            else:
                content = {"rows": []}
                for item in payload["conditioning_data"]:
                    values = {column: payload["column_schema"][column]["enum"][0] if column == "label"
                              else item["row_id"] + 100 for column in payload["features_to_generate"]}
                    content["rows"].append({"row_id": item["row_id"], "values": values})
            return {"choices": [{"message": {"content": json.dumps(content)}, "finish_reason": "stop"}],
                    "usage": {"prompt_tokens": 8, "completion_tokens": 4}}
        return OpenAICompatibleClient(llm_config, ledger=ledger, transport=transport)
    return factory


def test_selecting_one_shot_and_seed_resumes_its_original_grid_run(config):
    config.data.shots = [4, 6]
    config.data.seeds = [42, 43]
    first = run_experiment(config, 4, 42, stage="split")
    initial = json.loads((first / "manifest.json").read_text())
    assert initial["requested_grid"] == {"shots": [4, 6], "seeds": [42, 43]}
    narrowed = replace(config, data=replace(config.data, shots=[4], seeds=[42]))
    resumed = run_experiment(narrowed, 4, 42, stage="split", resume=True)
    assert resumed == first
    assert len(list(first.parents[3].rglob("manifest.json"))) == 1


@pytest.mark.parametrize("stage", ["discovery", "generation"])
@pytest.mark.parametrize("mutation", ["delete", "alter"])
def test_completed_request_journals_are_verified_before_resume(config, stage, mutation):
    calls = []
    directory = run_experiment(config, 4, 42, client_factory=factory_for(calls), backend="offline-audit")
    usage_before = (directory / "usage.json").read_bytes()
    journal = directory / f"{stage}_requests.jsonl"
    if mutation == "delete":
        journal.unlink()
    else:
        with journal.open("a") as handle:
            handle.write('{"status":"forged"}\n')
    with pytest.raises(ValueError, match="(?i)(journal|ledger|artifact)"):
        run_experiment(config, 4, 42, resume=True, backend="offline-audit",
                       client_factory=lambda *args: pytest.fail("Modified journals must fail before model construction"))
    assert (directory / "usage.json").read_bytes() == usage_before


@pytest.mark.parametrize("stage", ["discovery", "generation"])
def test_missing_failed_stage_journal_cannot_reset_request_budget(config, stage):
    calls = []
    with pytest.raises(RuntimeError):
        run_experiment(config, 4, 42, client_factory=factory_for(calls, fail_stage=stage), backend="offline-audit")
    directory = experiment_dir(config, experiment_identity(config, 4, 42, backend="offline-audit"))
    journal = directory / f"{stage}_requests.jsonl"
    assert journal.exists() and journal.stat().st_size > 0
    journal.unlink()
    with pytest.raises(ValueError, match="(?i)(journal|ledger)"):
        run_experiment(config, 4, 42, resume=True, backend="offline-audit",
                       client_factory=lambda *args: pytest.fail("Lost budget history must fail before model construction"))


def test_cleared_failed_journal_cannot_reset_request_budget(config):
    config.generation.max_attempts = 5
    config.generation_llm = replace(config.generation_llm, request_limit=1)
    calls = []
    with pytest.raises(BudgetExceeded):
        run_experiment(config, 4, 42, client_factory=factory_for(calls, fail_stage="generation"),
                       backend="offline-audit")
    directory = experiment_dir(config, experiment_identity(config, 4, 42, backend="offline-audit"))
    journal = directory / "generation_requests.jsonl"
    usage_before = (directory / "usage.json").read_bytes()
    assert sum(stage == "generation" for stage, _ in calls) == 1
    journal.write_text("")
    with pytest.raises(ValueError):
        run_experiment(config, 4, 42, resume=True, backend="offline-audit",
                       client_factory=lambda *args: pytest.fail("A truncated journal reset the known budget"))
    assert (directory / "usage.json").read_bytes() == usage_before


@pytest.mark.parametrize("stage", ["discovery", "generation"])
def test_cli_replay_rejects_model_configuration_different_from_source(config, tmp_path, capsys, stage):
    directory = run_experiment(config, 4, 42, client_factory=factory_for([]), backend="offline-audit")
    source_bytes = {name: (directory / f"{name}_requests.jsonl").read_bytes()
                    for name in ("discovery", "generation")}
    field = f"{stage}_llm"
    setattr(config, field, replace(getattr(config, field), model="different-model-from-recording"))
    path = tmp_path / "mismatched-replay.yaml"
    path.write_text(yaml.safe_dump(config.to_dict()))
    assert main(["run", "--config", str(path), "--replay-dir", str(directory)]) == 1
    message = capsys.readouterr().err.lower()
    assert "replay" in message
    assert "config" in message or "model" in message
    for name, content in source_bytes.items():
        assert (directory / f"{name}_requests.jsonl").read_bytes() == content


def test_invalid_evaluator_parameters_fail_before_any_model_client(config):
    config.evaluation = EvaluationConfig(model="logistic", model_params={"C": -1})
    with pytest.raises(ValueError, match="C"):
        run_experiment(config, 4, 42, backend="offline-audit",
                       client_factory=lambda *args: pytest.fail("Invalid evaluator settings reached a paid stage"))


def test_real_baseline_is_saved_verified_and_reused_before_discovery(config, monkeypatch):
    config.evaluation = EvaluationConfig(model="logistic")
    calls = []
    directory = run_experiment(config, 4, 42, stage="discover", client_factory=factory_for(calls),
                                backend="offline-audit")
    baseline = directory / "real_baseline.json"
    assert baseline.is_file()
    assert json.loads(baseline.read_text())
    manifest = json.loads((directory / "manifest.json").read_text())
    assert "real_baseline.json" in manifest["artifacts"]
    assert manifest["completed_stages"] == ["split", "discover"]
    monkeypatch.setattr("structsynth.pipeline.evaluation.evaluate_downstream",
                        lambda *args, **kwargs: pytest.fail("A verified baseline should be reused"))
    assert run_experiment(config, 4, 42, stage="discover", resume=True, backend="offline-audit",
                          client_factory=lambda *args: pytest.fail("Completed discovery should be reused")) == directory
