from copy import deepcopy
import json
from pathlib import Path
import shutil

import pandas as pd
import pytest

from structsynth.artifacts import atomic_json, file_hash, fingerprint
from structsynth.reporting import summarize_runs, write_summary


def make_run(tmp_path, seed=42, score=0.8, *, name=None, identity_changes=None,
             expected_seeds=(42, 43, 44), sample_changes=None, status="complete"):
    directory = tmp_path / (name or f"seed_{seed}")
    identity = {
        "config": {
            "data": {"name": "toy", "path": "/local/data.csv", "metadata": "/local/meta.json", "task_type": "classification"},
            "generation": {"n_samples": [100], "batch_size": 10},
            "evaluation": {"enabled": True, "protocol": "augmentation", "model": "xgboost",
                           "numeric_scaling": "none", "fidelity_reference": "train_test", "model_params": {}},
        },
        "seed": seed, "shot": 20, "backend": "live", "data_sha256": "data-v1",
        "metadata_sha256": "schema-v1", "source_sha256": "code-v1", "artifact_schema": 1,
        "environment": {"python": "3.11", "numpy": "2.0", "xgboost": "3.2"},
    }
    if identity_changes:
        identity.update(deepcopy(identity_changes))
    sample = {
        "seed": seed, "n_samples": 100,
        "downstream": {"protocol": "augmentation", "model": "xgboost", "task_type": "classification",
                       "auc_roc": score, "accuracy": 0.75, "f1_macro": 0.7, "train_rows": 120,
                       "test_rows": 400, "primary_metric": "auc_roc", "metric_issues": []},
        "privacy": {"privacy_risk": 0.6, "dcr": 0.6, "mean_distance_to_train": 2.0,
                    "mean_distance_to_test": 3.0, "reference_size_per_split": 20, "numeric_scaling": "none"},
        "fidelity": {"statistical_fidelity": 0.2, "pairwise_correlation_diff": 0.2,
                     "pair_count": 3, "pairs": [{"difference": 0.2}], "metric_issues": []},
        "fidelity_reference": "train_test",
    }
    if sample_changes:
        for section, changes in sample_changes.items():
            if isinstance(changes, dict):
                sample[section].update(changes)
            else:
                sample[section] = changes
    atomic_json(directory / "metrics.json", {"100": sample})
    usage = {stage: {"requests": 4, "api_requests": 4, "replayed_requests": 0, "successful_requests": 4,
                     "total_tokens": 100, "known_total_tokens": 100, "requests_with_unknown_usage": 0}
             for stage in ("discovery", "generation")}
    atomic_json(directory / "usage.json", usage)
    manifest = {"identity": identity, "run_id": fingerprint(identity), "status": status,
                "requested_grid": {"shots": [20], "seeds": list(expected_seeds)},
                "completed_stages": ["split", "discover", "generate", "evaluate"] if status == "complete" else ["split"],
                "artifacts": {"metrics.json": file_hash(directory / "metrics.json")}}
    atomic_json(directory / "manifest.json", manifest)
    return directory


def update_manifest(directory, change):
    path = directory / "manifest.json"
    manifest = json.loads(path.read_text())
    change(manifest)
    manifest["run_id"] = fingerprint(manifest["identity"])
    atomic_json(path, manifest)


def test_compatible_seeds_use_sample_std_and_do_not_average_counts_or_aliases(tmp_path):
    first, second = make_run(tmp_path, 42, 0.6), make_run(tmp_path, 43, 0.8)
    summary = summarize_runs([first, second])
    assert summary["excluded_runs"] == []
    group = summary["groups"][0]
    assert len(summary["groups"]) == 1
    statistics = group["metrics"]["downstream.auc_roc"]
    assert statistics["mean"] == pytest.approx(0.7)
    assert statistics["sample_std"] == pytest.approx(0.2 / 2**0.5)
    assert statistics["valid_count"] == 2
    assert statistics["missing_count"] == 0
    assert group["provided_seeds"] == [42, 43]
    assert group["missing_expected_seeds"] == [44]
    assert "downstream.train_rows" not in group["metrics"]
    assert "fidelity.pair_count" not in group["metrics"]
    assert "privacy.dcr" not in group["metrics"]
    assert group["usage"]["generation.api_requests"]["sum"] == 8
    json.dumps(summary, allow_nan=False)


def test_single_seed_has_undefined_std_and_explicit_undefined_auc_reason(tmp_path):
    directory = make_run(tmp_path, sample_changes={"downstream": {"auc_roc": None, "metric_issues": ["test has one class"]}})
    group = summarize_runs([directory])["groups"][0]
    auc = group["metrics"]["downstream.auc_roc"]
    assert auc["mean"] is None and auc["sample_std"] is None
    assert auc["valid_count"] == 0 and auc["missing_count"] == 1
    assert auc["missing"][0]["reason"] == "test has one class"
    assert group["metrics"]["privacy.privacy_risk"]["sample_std"] is None


def test_repeated_paths_and_identical_seed_copies_count_once(tmp_path):
    first = make_run(tmp_path)
    copy = tmp_path / "copied_run"
    shutil.copytree(first, copy)
    summary = summarize_runs([first, first, copy])
    assert summary["input_directory_count"] == 3
    assert summary["unique_directory_count"] == 2
    assert summary["duplicate_input_paths"][0]["count"] == 2
    group = summary["groups"][0]
    assert group["metrics"]["downstream.auc_roc"]["valid_count"] == 1
    assert group["duplicate_seeds"][0]["policy"] == "counted_once"
    assert group["usage"]["generation.api_requests"]["sum"] == 4


def test_conflicting_seed_copies_are_excluded_instead_of_cherry_picked_or_averaged(tmp_path):
    first = make_run(tmp_path, 42, 0.6)
    conflict = make_run(tmp_path, 42, 0.9, name="conflict")
    second = make_run(tmp_path, 43, 0.7)
    group = summarize_runs([first, second, conflict])["groups"][0]
    auc = group["metrics"]["downstream.auc_roc"]
    assert auc["mean"] == 0.7
    assert auc["valid_count"] == 1 and auc["missing_count"] == 1
    assert auc["sample_std"] is None
    assert "duplicate_seed_conflict" in auc["missing"][0]["reason"]
    assert group["duplicate_seeds"][0]["policy"] == "conflicting_results_excluded"


@pytest.mark.parametrize("field,value", [
    ("backend", "offline-demo"), ("data_sha256", "another-data"), ("metadata_sha256", "another-schema"),
    ("source_sha256", "another-code"), ("environment", {"python": "3.12"}), ("shot", 100),
    ("backend", {"kind": "replay", "source_ledgers": {"discovery": "hash-a", "generation": "hash-b"}}),
])
def test_incompatible_inputs_code_environment_backend_and_shots_never_mix(tmp_path, field, value):
    first = make_run(tmp_path, 42)
    second = make_run(tmp_path, 43, identity_changes={field: value})
    assert len(summarize_runs([first, second])["groups"]) == 2


def test_protocol_model_config_and_sample_count_are_group_dimensions(tmp_path):
    first = make_run(tmp_path, 42)
    protocol = make_run(tmp_path, 43, name="protocol", sample_changes={"downstream": {"protocol": "real_only"}})
    update_manifest(protocol, lambda manifest: manifest["identity"]["config"]["evaluation"].update(protocol="real_only"))
    model = make_run(tmp_path, 43, name="model", sample_changes={"downstream": {"model": "logistic"}})
    update_manifest(model, lambda manifest: manifest["identity"]["config"]["evaluation"].update(model="logistic"))
    config = make_run(tmp_path, 43, name="config")
    update_manifest(config, lambda manifest: manifest["identity"]["config"]["generation"].update(batch_size=20))
    assert len(summarize_runs([first, protocol, model, config])["groups"]) == 4
    update_manifest(first, lambda manifest: manifest["identity"]["config"]["generation"].update(n_samples=[100, 200]))
    summary = summarize_runs([first])
    assert [group["n_samples"] for group in summary["groups"]] == [100, 200]
    assert summary["groups"][1]["metrics"]["privacy.privacy_risk"]["missing_count"] == 1


def test_seed_grids_and_input_locations_do_not_prevent_compatible_grouping(tmp_path):
    first, second = make_run(tmp_path, 42), make_run(tmp_path, 43)
    update_manifest(first, lambda m: m["identity"]["config"]["data"].update(seeds=[42], shots=[20]))
    update_manifest(second, lambda m: m["identity"]["config"]["data"].update(
        path="/another/data.csv", metadata="/another/meta.json", seeds=[43], shots=[20, 100]))
    update_manifest(second, lambda m: m["identity"]["config"].update(output_dir="/another/output"))
    group = summarize_runs([first, second])["groups"]
    assert len(group) == 1
    assert group[0]["metrics"]["downstream.auc_roc"]["valid_count"] == 2


def test_unfinished_missing_and_corrupt_results_remain_missing(tmp_path):
    first = make_run(tmp_path, 42)
    failed = make_run(tmp_path, 43, status="failed")
    missing = make_run(tmp_path, 44)
    (missing / "metrics.json").unlink()
    corrupt = make_run(tmp_path, 45)
    (corrupt / "metrics.json").write_text('{"100":{}}')
    invalid = tmp_path / "not_a_run"
    group = summarize_runs([first, failed, missing, corrupt, invalid])
    assert len(group["excluded_runs"]) == 1
    auc = group["groups"][0]["metrics"]["downstream.auc_roc"]
    assert auc["valid_count"] == 1 and auc["missing_count"] == 3
    reasons = [missing["reason"] for missing in auc["missing"]]
    assert any("run_not_evaluated" in reason for reason in reasons)
    assert any("FileNotFoundError" in reason for reason in reasons)
    assert any("artifact hash" in reason for reason in reasons)


def test_unknown_usage_is_not_zero_and_ledger_requests_are_not_api_calls(tmp_path):
    first, second = make_run(tmp_path, 42), make_run(tmp_path, 43)
    usage = json.loads((second / "usage.json").read_text())
    usage["generation"].update(total_tokens=None, known_total_tokens=70, requests_with_unknown_usage=1,
                               api_requests=0, replayed_requests=4)
    atomic_json(second / "usage.json", usage)
    group = summarize_runs([first, second])["groups"][0]
    total = group["usage"]["generation.total_tokens"]
    assert total["valid_count"] == 1 and total["missing_count"] == 1
    assert total["sum"] is None
    assert total["known_sum"] == 100
    assert group["usage"]["generation.known_total_tokens"]["sum"] == 170
    assert group["usage"]["generation.requests"]["sum"] == 8
    assert group["usage"]["generation.api_requests"]["sum"] == 4


def test_report_protocol_disagreement_is_missing_and_replay_hashes_isolate_inputs(tmp_path):
    first = make_run(tmp_path, 42, sample_changes={"downstream": {"protocol": "synthetic_only"}})
    group = summarize_runs([first])["groups"][0]
    assert group["metrics"]["downstream.auc_roc"]["valid_count"] == 0
    assert "protocol_disagrees" in group["metrics"]["downstream.auc_roc"]["missing"][0]["reason"]
    replay_a = {"kind": "replay", "source_ledgers": {"discovery": "a", "generation": "b"}}
    replay_b = {"kind": "replay", "source_ledgers": {"discovery": "a", "generation": "c"}}
    a = make_run(tmp_path, 42, name="replay-a", identity_changes={"backend": replay_a})
    b = make_run(tmp_path, 43, name="replay-b", identity_changes={"backend": replay_b})
    assert len(summarize_runs([a, b])["groups"]) == 2


def test_json_and_csv_exports_are_tidy_and_leave_source_runs_unchanged(tmp_path):
    directory = make_run(tmp_path)
    before = {path.name: path.read_bytes() for path in directory.iterdir()}
    result = write_summary([directory], tmp_path / "report")
    assert isinstance(result, Path)
    assert result.name == "summary.json"
    report = json.loads(result.read_text())
    table = pd.read_csv(result.with_suffix(".csv"))
    assert len(report["groups"]) == 1
    performance = table[table["kind"] == "performance"]
    assert performance.loc[performance["metric"] == "downstream.auc_roc", "mean"].iloc[0] == 0.8
    assert set(table["kind"]) == {"performance", "usage_entire_run"}
    assert {path.name: path.read_bytes() for path in directory.iterdir()} == before
    empty = write_summary([], tmp_path / "empty_report")
    assert json.loads(empty.read_text())["groups"] == []
    assert pd.read_csv(empty.with_suffix(".csv")).empty
