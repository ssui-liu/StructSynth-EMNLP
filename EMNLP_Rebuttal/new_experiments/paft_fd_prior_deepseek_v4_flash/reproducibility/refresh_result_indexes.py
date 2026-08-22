#!/usr/bin/env python3
"""Rebuild flat result indexes from the per-seed metrics artifacts."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path


# Keep an explicit lexical path option for workspaces where this experiment is
# reached through a symlink (and therefore resolves outside the write sandbox).
EXPERIMENT_ROOT = Path(os.environ.get("EXPERIMENT_ROOT", Path(__file__).parents[1]))
RESULTS_ROOT = EXPERIMENT_ROOT / "results"
METHOD = "paft_fd_prior_deepseek-v4-flash"
METRIC_COLUMNS = [
    "accuracy", "f1", "precision", "recall", "auc_roc", "mae", "mse", "rmse", "r2",
]


def main() -> None:
    rows: list[dict[str, object]] = []
    for path in sorted(RESULTS_ROOT.glob(f"*/100_shot/{METHOD}/seed_*/n*/metrics.json")):
        metrics = json.loads(path.read_text(encoding="utf-8"))
        n_dir, seed_dir, _method_dir, _shot_dir, dataset_dir = path.parents[:5]
        seed = int(seed_dir.name.removeprefix("seed_"))
        n_samples = int(n_dir.name.removeprefix("n"))
        synthetic_path = n_dir / "synthetic_data.csv"
        row: dict[str, object] = {
            "dataset": dataset_dir.name,
            "seed": seed,
            "n_samples": n_samples,
            "synthetic_data_path": str(synthetic_path.relative_to(EXPERIMENT_ROOT)),
            "metrics_path": str(path.relative_to(EXPERIMENT_ROOT)),
            "line_count": sum(1 for _ in synthetic_path.open(encoding="utf-8")),
            "train_size": metrics.get("train_size"),
            "task_type": metrics.get("task_type"),
        }
        row.update({key: metrics.get(key) for key in METRIC_COLUMNS})
        rows.append(row)

    fieldnames = [
        "dataset", "seed", "n_samples", "synthetic_data_path", "metrics_path", "line_count",
        "train_size", "task_type", *METRIC_COLUMNS,
    ]
    with (RESULTS_ROOT / "metrics_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    with (EXPERIMENT_ROOT / "synthetic_data_paths.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["dataset", "seed", "n_samples", "synthetic_data_path", "metrics_path"],
            delimiter="\t",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    expected = 6 * 5 * 4
    if len(rows) != expected:
        raise SystemExit(f"Expected {expected} metric rows, found {len(rows)}")
    print(f"Wrote {len(rows)} rows to both result indexes.")


if __name__ == "__main__":
    main()
