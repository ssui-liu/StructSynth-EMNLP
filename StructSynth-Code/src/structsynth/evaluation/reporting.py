"""Aggregate compatible experiments without treating repeated seeds as replicas.

Only manifest.json, metrics.json and usage.json are read. No evaluation is run,
and individual runs are never modified. Undefined results remain missing.
"""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, stdev
from typing import Any

import pandas as pd

from ..artifacts import atomic_csv, atomic_json, canonical_json, fingerprint


PERFORMANCE_FIELDS = {
    "downstream": ("auc_roc", "r2", "accuracy", "f1_macro", "mae", "rmse"),
    "privacy": ("privacy_risk", "mean_distance_to_train", "mean_distance_to_test"),
    "fidelity": ("statistical_fidelity",),
}
USAGE_FIELDS = ("requests", "api_requests", "replayed_requests", "successful_requests", "total_tokens",
                "known_total_tokens", "requests_with_unknown_usage")


def _read_json(path: Path):
    try:
        raw = path.read_bytes()
        value = json.loads(raw, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
        if not isinstance(value, dict):
            raise ValueError("JSON root is not an object")
        return value, hashlib.sha256(raw).hexdigest(), None
    except (OSError, UnicodeError, ValueError) as exc:
        return None, None, f"{path.name}: {type(exc).__name__}: {exc}"


def _integer(value, *, positive=False):
    return isinstance(value, int) and not isinstance(value, bool) and value >= (1 if positive else 0)


def _load_run(directory: Path):
    manifest, _, error = _read_json(directory / "manifest.json")
    if error:
        raise ValueError(error)
    identity = manifest.get("identity")
    if not isinstance(identity, dict):
        raise ValueError("manifest.identity is missing or malformed")
    config = identity.get("config")
    if not isinstance(config, dict):
        raise ValueError("manifest.identity.config is missing or malformed")
    for section in ("data", "generation", "evaluation"):
        if not isinstance(config.get(section), dict):
            raise ValueError(f"Identity config.{section} is missing or malformed")
    for field in ("backend", "source_sha256", "data_sha256", "metadata_sha256", "environment", "artifact_schema"):
        if field not in identity:
            raise ValueError(f"Identity field {field} is required to establish compatible experiments")
    for field in ("source_sha256", "data_sha256", "metadata_sha256"):
        if not isinstance(identity[field], str) or not identity[field]:
            raise ValueError(f"Identity {field} must be a nonempty fingerprint")
    if not isinstance(identity["environment"], dict) or not identity["environment"]:
        raise ValueError("Identity environment must declare dependency versions")
    if not isinstance(identity["backend"], (str, dict)) or not identity["backend"]:
        raise ValueError("Identity backend must be a nonempty name or object")
    if not _integer(identity.get("seed")) or not _integer(identity.get("shot"), positive=True):
        raise ValueError("Identity seed/shot must be nonnegative/positive integers")
    if not isinstance(config["data"].get("name"), str) or not config["data"]["name"]:
        raise ValueError("Identity dataset name must be nonempty")
    for field in ("protocol", "model"):
        if not isinstance(config["evaluation"].get(field), str) or not config["evaluation"][field]:
            raise ValueError(f"Identity evaluation.{field} must be a nonempty name")
    sizes = config["generation"].get("n_samples")
    if not isinstance(sizes, list) or not sizes or any(not _integer(n, positive=True) for n in sizes):
        raise ValueError("Identity generation.n_samples must declare positive sample counts")
    metrics, metrics_hash, metrics_error = _read_json(directory / "metrics.json")
    expected = manifest.get("artifacts", {}).get("metrics.json")
    if expected and not metrics_error and metrics_hash != expected:
        metrics_error = "metrics.json does not match the manifest artifact hash"
    usage, _, usage_error = _read_json(directory / "usage.json")
    requested_grid = manifest.get("requested_grid", {})
    planned = requested_grid.get("seeds", config["data"].get("seeds", [])) if isinstance(requested_grid, dict) else []
    expected_seeds = [seed for seed in planned if _integer(seed)] if isinstance(planned, list) else []
    return {"run_dir": str(directory), "manifest": manifest, "identity": identity,
            "metrics": metrics, "metrics_error": metrics_error, "usage": usage, "usage_error": usage_error,
            "expected_seeds": expected_seeds, "metrics_integrity": "verified" if expected else "not_recorded"}


def _group_identity(run: dict, n_samples: int) -> dict:
    identity = deepcopy(run["identity"])
    identity.pop("seed")
    config = identity["config"]
    config.pop("output_dir", None)
    # Lists of requested executions and local file locations do not change an
    # effective run; immutable input hashes still isolate different datasets.
    for field in ("seeds", "shots", "path", "metadata"):
        config["data"].pop(field, None)
    identity["n_samples"] = n_samples
    return identity


def _sample(run, n_samples):
    manifest = run["manifest"]
    evaluation = run["identity"]["config"]["evaluation"]
    if not evaluation.get("enabled", True):
        return None, "evaluation_disabled"
    if manifest.get("status") != "complete" or "evaluate" not in manifest.get("completed_stages", []):
        error = manifest.get("error") or {}
        reason = f"run_not_evaluated: status={manifest.get('status', 'unknown')}"
        if isinstance(error, dict) and error.get("message"):
            reason += f"; {error['message']}"
        return None, reason
    if run["metrics_error"]:
        return None, run["metrics_error"]
    sample = run["metrics"].get(str(n_samples))
    if not isinstance(sample, dict):
        return None, f"metrics_missing_for_n_samples={n_samples}"
    if (not _integer(sample.get("seed")) or not _integer(sample.get("n_samples"), positive=True)
            or sample.get("seed") != run["identity"]["seed"] or sample.get("n_samples") != n_samples):
        return None, "metric_seed_or_sample_count_disagrees_with_manifest"
    downstream = sample.get("downstream", {})
    if not isinstance(downstream, dict):
        return None, "downstream_metrics_are_not_an_object"
    for field in ("protocol", "model"):
        if downstream.get(field) != evaluation.get(field):
            return None, f"downstream_{field}_disagrees_with_manifest"
    if downstream.get("task_type") not in ("classification", "regression"):
        return None, "downstream_task_type_missing_or_invalid"
    declared_task = run["identity"]["config"]["data"].get("task_type")
    if declared_task and downstream.get("task_type") != declared_task:
        return None, "downstream_task_type_disagrees_with_manifest"
    privacy = sample.get("privacy", {})
    if not isinstance(privacy, dict):
        return None, "privacy_metrics_are_not_an_object"
    if privacy.get("numeric_scaling", "none") != evaluation.get("numeric_scaling", "none"):
        return None, "privacy_numeric_scaling_disagrees_with_manifest"
    if sample.get("fidelity_reference") != evaluation.get("fidelity_reference"):
        return None, "fidelity_reference_disagrees_with_manifest"
    return sample, None


def _seed_record(records, n_samples):
    seed = records[0]["identity"]["seed"]
    samples = [(run, *_sample(run, n_samples)) for run in records]
    eligible = [(run, sample) for run, sample, reason in samples if reason is None]
    distinct = {canonical_json(sample) for _, sample in eligible}
    conflict = len(distinct) > 1
    if conflict:
        sample, reason = None, "duplicate_seed_conflict: different valid results for the same seed; all excluded"
    elif eligible:
        sample, reason = eligible[0][1], None
    else:
        sample, reason = None, "; ".join(sorted({reason for _, _, reason in samples}))
    # Costs describe entire executions, not an n-row synthetic prefix. Do not
    # choose one cost when multiple copies of the same seed disagree.
    valid_usage = [(run["usage"], run) for run in records if run["usage_error"] is None]
    if conflict:
        usage, usage_reason = None, "duplicate_seed_conflict"
    elif len({canonical_json(value) for value, _ in valid_usage}) > 1:
        usage, usage_reason = None, "duplicate_seed_usage_conflict"
    elif valid_usage:
        usage, usage_reason = valid_usage[0][0], None
    else:
        usage, usage_reason = None, "; ".join(sorted({run["usage_error"] for run in records}))
    duplicate = None
    if len(records) > 1:
        duplicate = {"seed": seed, "run_dirs": [run["run_dir"] for run in records],
                     "policy": "conflicting_results_excluded" if conflict else "counted_once",
                     "eligible_copies": len(eligible)}
    return {"seed": seed, "run_dirs": [run["run_dir"] for run in records],
            "sample": sample, "reason": reason, "usage": usage, "usage_reason": usage_reason,
            "duplicate": duplicate,
            "runs": [{"run_dir": run["run_dir"], "run_id": run["manifest"].get("run_id"),
                      "status": run["manifest"].get("status"), "metric_issue": problem,
                      "metrics_integrity": run["metrics_integrity"]} for run, _, problem in samples]}


def _value(section, name, fallback_reason):
    if not isinstance(section, dict):
        return None, fallback_reason or "metric_section_missing"
    value = section.get(name)
    # These are aliases of one score, not two independent metrics.
    if value is None and name == "privacy_risk" and "privacy_risk" not in section:
        value = section.get("dcr")
    if value is None and name == "statistical_fidelity" and "statistical_fidelity" not in section:
        value = section.get("pairwise_correlation_diff")
    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
        return float(value), None
    issues = section.get("metric_issues", [])
    explanation = "; ".join(str(issue) for issue in issues) if isinstance(issues, list) else str(issues)
    if value is not None:
        return None, "metric_value_is_not_a_finite_number"
    return None, explanation or fallback_reason or "metric_missing_or_undefined"


def _statistics(observations, *, costs=False):
    values = [value for _, value, reason in observations if reason is None]
    missing = [{"seed": record["seed"], "reason": reason, "run_dirs": record["run_dirs"]}
               for record, _, reason in observations if reason is not None]
    result = {"mean": float(mean(values)) if values else None,
              "sample_std": float(stdev(values)) if len(values) > 1 else None,
              "valid_count": len(values), "missing_count": len(missing), "missing": missing}
    if costs:
        result.update(known_sum=float(sum(values)) if values else None,
                      sum=float(sum(values)) if values and not missing else None)
    return result


def _summarize_group(identity, runs):
    by_seed = defaultdict(list)
    for run in runs:
        by_seed[run["identity"]["seed"]].append(run)
    records = [_seed_record(by_seed[seed], identity["n_samples"]) for seed in sorted(by_seed)]
    tasks = {record["sample"].get("downstream", {}).get("task_type") for record in records if record["sample"]}
    tasks.discard(None)
    declared_task = identity["config"]["data"].get("task_type")
    if declared_task:
        tasks.add(declared_task)
    if len(tasks) > 1:
        # With identical input/schema fingerprints and evaluator code, two task
        # types are inconsistent provenance, not independently mergeable scores.
        for record in records:
            record["reason"] = "conflicting_task_type_metadata"
    fields = {"privacy.privacy_risk", "fidelity.statistical_fidelity"}
    if tasks == {"classification"}:
        fields.update(("downstream.auc_roc", "downstream.accuracy", "downstream.f1_macro"))
    elif tasks == {"regression"}:
        fields.update(("downstream.r2", "downstream.mae", "downstream.rmse"))
    for record in records:
        for section, names in PERFORMANCE_FIELDS.items():
            source = (record["sample"] or {}).get(section, {})
            if isinstance(source, dict):
                fields.update(f"{section}.{name}" for name in names if name in source)
    metrics = {}
    for field in sorted(fields):
        section, name = field.split(".")
        observations = []
        for record in records:
            if record["reason"]:
                value, reason = None, record["reason"]
            else:
                value, reason = _value(record["sample"].get(section), name, None)
            observations.append((record, value, reason))
        metrics[field] = _statistics(observations)
    usage = {}
    for stage in ("discovery", "generation"):
        for name in USAGE_FIELDS:
            observations = []
            for record in records:
                if record["usage_reason"]:
                    value, reason = None, record["usage_reason"]
                else:
                    value, reason = _value(record["usage"].get(stage), name,
                                           "usage_value_missing_or_unknown")
                observations.append((record, value, reason))
            usage[f"{stage}.{name}"] = _statistics(observations, costs=True)
    expected = sorted({seed for run in runs for seed in run["expected_seeds"]})
    seeds = sorted(by_seed)
    evaluation = identity["config"]["evaluation"]
    return {
        "group_id": fingerprint(identity), "identity": identity,
        "dataset": identity["config"]["data"]["name"], "shot": identity["shot"],
        "n_samples": identity["n_samples"], "backend": identity["backend"],
        "protocol": evaluation.get("protocol"), "model": evaluation.get("model"),
        "task_type": next(iter(tasks)) if len(tasks) == 1 else None,
        "provided_seeds": seeds, "provided_seed_count": len(seeds), "expected_seeds": expected,
        "missing_expected_seeds": sorted(set(expected) - set(seeds)),
        "metrics": metrics, "usage": usage,
        "usage_scope": "entire_run_including_maximum_requested_n; repeated_across_n_groups_do_not_sum",
        "usage_requests_definition": "ledger_records; api_requests_counts_provider_calls",
        "duplicate_seeds": [record["duplicate"] for record in records if record["duplicate"]],
        "runs": [{"seed": record["seed"], "metric_issue": record["reason"], "copies": record["runs"]} for record in records],
        "issues": ["conflicting_task_type_metadata"] if len(tasks) > 1 else [],
    }


def summarize_runs(run_dirs: list[Path]) -> dict[str, Any]:
    """Return means and sample SD for compatible, independently seeded runs.

    Incomplete/missing/corrupt evaluation results contribute explicit missing
    observations. Identical duplicate seeds count once; conflicting duplicates
    contribute no score. Expected seeds absent from the input directory list are
    recorded separately and are not falsely counted as completed experiments.
    """
    paths = [Path(path).resolve() for path in run_dirs]
    path_counts = defaultdict(int)
    for path in paths:
        path_counts[path] += 1
    groups, identities, excluded = defaultdict(list), {}, []
    for directory in sorted(path_counts):
        try:
            run = _load_run(directory)
        except (TypeError, ValueError, AttributeError) as exc:
            excluded.append({"run_dir": str(directory), "reason": str(exc)})
            continue
        for n_samples in sorted(set(run["identity"]["config"]["generation"]["n_samples"])):
            identity = _group_identity(run, n_samples)
            key = fingerprint(identity)
            identities[key] = identity
            groups[key].append(run)
    summaries = [_summarize_group(identities[key], runs) for key, runs in groups.items()]
    summaries.sort(key=lambda group: (group["dataset"], group["shot"], group["n_samples"], group["group_id"]))
    return {
        "summary_version": 1, "input_directory_count": len(paths), "unique_directory_count": len(path_counts),
        "duplicate_input_paths": [{"run_dir": str(path), "count": count} for path, count in sorted(path_counts.items()) if count > 1],
        "groups": summaries, "excluded_runs": excluded,
        "standard_deviation": "sample, ddof=1; null when fewer than two valid independent seeds",
        "metric_units": "raw evaluator units; no percentage conversion",
        "missing_seed_policy": "missing_expected_seeds are listed separately from missing provided results",
    }


def write_summary(run_dirs: list[Path], output_dir: str | Path) -> Path:
    """Write summary.json and a tidy summary.csv; return the JSON path.

    CSV kind distinguishes performance from full-run resource usage. Detailed
    provenance, per-seed exclusions and non-scalar backend identities remain in
    JSON; their compact representations are also available in CSV columns.
    """
    output = Path(output_dir)
    summary = summarize_runs(run_dirs)
    rows = []
    for group in summary["groups"]:
        common = {key: group[key] for key in ("group_id", "dataset", "shot", "n_samples", "protocol", "model")}
        common.update(backend=canonical_json(group["backend"]),
                      provided_seeds=canonical_json(group["provided_seeds"]),
                      missing_expected_seeds=canonical_json(group["missing_expected_seeds"]))
        for section, kind in (("metrics", "performance"), ("usage", "usage_entire_run")):
            for metric, statistics in group[section].items():
                rows.append({**common, "kind": kind, "metric": metric,
                             **{key: statistics[key] for key in ("mean", "sample_std", "valid_count", "missing_count")},
                             "known_sum": statistics.get("known_sum"), "sum": statistics.get("sum"),
                             "usage_scope": group["usage_scope"] if section == "usage" else None,
                             "missing_reasons": canonical_json(statistics["missing"])})
    columns = ["group_id", "dataset", "shot", "n_samples", "protocol", "model", "backend", "provided_seeds",
               "missing_expected_seeds", "kind", "metric", "mean", "sample_std", "valid_count", "missing_count",
               "known_sum", "sum", "usage_scope", "missing_reasons"]
    atomic_json(output / "summary.json", summary)
    atomic_csv(output / "summary.csv", pd.DataFrame(rows, columns=columns))
    return output / "summary.json"
