"""Offline integration tests of paper stages, artifacts, and resumption.

The demo client deliberately copies training records and is never a quality
baseline. These tests verify control flow using real local downstream models.
"""
from dataclasses import replace
import json

import numpy as np
import pandas as pd
import pytest

from structsynth.artifacts import atomic_csv, atomic_json
from structsynth.config import DataConfig, EvaluationConfig, ExperimentConfig, GenerationConfig, LLMConfig
from structsynth.demo import demo_factory, run_demo
from structsynth.pipeline import experiment_dir, experiment_identity, run_experiment


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def toy_config(tmp_path):
    inputs = tmp_path / "inputs"
    frame = pd.DataFrame({"row": np.arange(80), "group": ["001", "002"] * 40,
                          "outcome": ["no", "yes"] * 40})
    atomic_csv(inputs / "toy.csv", frame)
    atomic_json(inputs / "metadata.json", {
        "name": "toy", "columns": list(frame), "target_column": "outcome", "task_type": "classification",
        "categorical_columns": ["group", "outcome"],
    })
    return ExperimentConfig(
        data=DataConfig("toy", str(inputs / "toy.csv"), str(inputs / "metadata.json"),
                        shots=[20], seeds=[42], example_rows=10),
        discovery_llm=LLMConfig(request_limit=40), generation_llm=LLMConfig(request_limit=80),
        generation=GenerationConfig(n_samples=[5, 12], batch_size=5),
        evaluation=EvaluationConfig(model="logistic"), output_dir=str(tmp_path / "runs"),
    )


def forbidden_client(*args, **kwargs):
    raise AssertionError("A finished/resumed stage must not create a model client")


def test_run_demo_completes_xgboost_and_resume_never_reissues_requests(tmp_path):
    pytest.importorskip("xgboost")
    directory = run_demo(tmp_path, model="xgboost", max_workers=2)[0]
    manifest = read_json(directory / "manifest.json")
    assert manifest["status"] == "complete"
    assert manifest["completed_stages"] == ["split", "discover", "generate", "evaluate"]
    assert manifest["identity"]["backend"] == "offline-demo"
    metrics = read_json(directory / "metrics.json")
    assert set(metrics) == {"10", "30"}
    for n in (10, 30):
        report = metrics[str(n)]
        assert report["downstream"]["model"] == "xgboost"
        assert report["downstream"]["train_rows"] == 20 + n
        assert report["privacy"]["reference_size_per_split"] == 20
        assert report["fidelity"]["pair_count"] == 3
        assert len(pd.read_csv(directory / f"n{n}" / "synthetic.csv")) == n
    before = {name: (directory / name).read_bytes() for name in
              ("discovery_requests.jsonl", "generation_requests.jsonl", "synthetic.json", "metrics.json")}
    assert run_demo(tmp_path, model="xgboost", max_workers=2, resume=True) == [directory]
    for name, content in before.items():
        assert (directory / name).read_bytes() == content
    assert read_json(directory / "usage.json")["generation"]["total_tokens"] == 0


def test_stage_progression_resumes_and_keeps_string_category_identity(toy_config):
    config = toy_config
    directory = run_experiment(config, 20, 42, stage="split", backend="offline-test", client_factory=forbidden_client)
    assert read_json(directory / "manifest.json")["completed_stages"] == ["split"]
    split = read_json(directory / "split.json")
    assert len(split["source_row_positions"]["train"]) == 20
    assert not set(split["source_row_positions"]["train"]) & set(split["source_row_positions"]["test"])
    assert "group" not in read_json(directory / "schema.json")["categories"]
    assert split["training_schema"]["observed_categories"]["group"] in (["001", "002"], ["002", "001"])
    calls = []

    def observed_factory(name, config, ledger, train, spec):
        calls.append(name)
        assert len(train) == 20
        assert set(train["row"]).isdisjoint(set(split["source_row_positions"]["test"]))
        return demo_factory(name, config, ledger, train, spec)

    assert run_experiment(config, 20, 42, stage="discover", resume=True,
                          backend="offline-test", client_factory=observed_factory) == directory
    assert calls == ["discovery"]
    assert read_json(directory / "manifest.json")["completed_stages"] == ["split", "discover"]
    discovery_requests = (directory / "discovery_requests.jsonl").read_bytes()
    assert run_experiment(config, 20, 42, stage="generate", resume=True,
                          backend="offline-test", client_factory=observed_factory) == directory
    assert calls == ["discovery", "generation"]
    assert (directory / "discovery_requests.jsonl").read_bytes() == discovery_requests
    saved = read_json(directory / "synthetic.json")
    assert {row["group"] for row in saved}.issubset({"001", "002"})
    generation_requests = (directory / "generation_requests.jsonl").read_bytes()
    assert run_experiment(config, 20, 42, stage="evaluate", resume=True,
                          backend="offline-test", client_factory=forbidden_client) == directory
    assert read_json(directory / "manifest.json")["status"] == "complete"
    assert (directory / "generation_requests.jsonl").read_bytes() == generation_requests
    assert read_json(directory / "metrics.json")["12"]["downstream"]["train_rows"] == 32


def test_resume_rejects_modified_artifacts_before_using_the_model(toy_config):
    directory = run_experiment(toy_config, 20, 42, stage="split", backend="offline-test", client_factory=forbidden_client)
    with (directory / "train.csv").open("a") as stream:
        stream.write("999,modified,yes\n")
    with pytest.raises(ValueError, match="modified"):
        run_experiment(toy_config, 20, 42, resume=True, backend="offline-test", client_factory=forbidden_client)


def test_existing_run_requires_resume_and_later_stage_requires_prior_graph(toy_config):
    run_experiment(toy_config, 20, 42, stage="split", backend="offline-test", client_factory=forbidden_client)
    with pytest.raises(FileExistsError, match="resume"):
        run_experiment(toy_config, 20, 42, stage="split", backend="offline-test", client_factory=forbidden_client)
    with pytest.raises(FileNotFoundError, match="Discover"):
        run_experiment(toy_config, 20, 42, stage="generate", resume=True,
                       backend="offline-test", client_factory=forbidden_client)


def test_run_identity_separates_shots_seeds_models_backends_and_input_content(toy_config):
    first = experiment_identity(toy_config, 20, 42, backend="offline-test")
    changed_model = replace(toy_config, generation_llm=replace(toy_config.generation_llm, model="another-model"))
    identities = [first, experiment_identity(toy_config, 30, 42, backend="offline-test"),
                  experiment_identity(toy_config, 20, 43, backend="offline-test"),
                  experiment_identity(changed_model, 20, 42, backend="offline-test"),
                  experiment_identity(toy_config, 20, 42, backend="live")]
    assert len({experiment_dir(toy_config, identity) for identity in identities}) == len(identities)
    raw_path = toy_config.data.path
    frame = pd.read_csv(raw_path)
    frame.loc[0, "row"] = 1000
    atomic_csv(raw_path, frame)
    changed_data = experiment_identity(toy_config, 20, 42, backend="offline-test")
    assert changed_data["data_sha256"] != first["data_sha256"]
    assert experiment_dir(toy_config, changed_data) != experiment_dir(toy_config, first)


def test_offline_regression_runs_same_graph_and_synthesis_stages(toy_config):
    frame = pd.DataFrame({"row": np.arange(80), "group": ["a", "b"] * 40,
                          "outcome": 2.0 * np.arange(80) + 0.5})
    atomic_csv(toy_config.data.path, frame)
    atomic_json(toy_config.data.metadata, {
        "name": "toy_regression", "target_column": "outcome", "task_type": "regression",
        "categorical_columns": ["group"],
    })
    config = replace(toy_config, evaluation=EvaluationConfig(model="ridge"))
    directory = run_experiment(config, 20, 42, backend="offline-test", client_factory=demo_factory)
    report = read_json(directory / "metrics.json")["12"]
    assert report["downstream"]["task_type"] == "regression"
    assert report["downstream"]["r2"] > 0.99
    assert report["downstream"]["train_rows"] == 32
    assert read_json(directory / "manifest.json")["status"] == "complete"
