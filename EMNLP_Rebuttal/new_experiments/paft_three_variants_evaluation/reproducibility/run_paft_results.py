#!/usr/bin/env python3
"""Evaluate PAFT result folders with the shared 3-part evaluation suite.

This aligns the PAFT repository layout with the evaluation code in this folder.

Default PAFT layout:
  ../../Permutation-aided-Fine-tuning/
    data/structsynth/{dataset}/{shot}_shot/seed_{seed}/{train,test}.csv
    results/{variant}/{dataset}/{shot}_shot/paft/seed_{seed}/n{n}/synthetic_data.csv

Metrics:
  - downstream: XGBoost task performance from D_fewshot + D_synth to real test data
  - fidelity: pairwise correlation/distribution difference
  - privacy: DCR, probability that a synthetic row's nearest real neighbor is from train
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

try:
    import xgboost as xgb
except ImportError:  # pragma: no cover - exercised only in incomplete environments
    xgb = None

from src.evaluation.dcr_evaluation_pipeline import evaluate_dcr
from src.evaluation.downstream_performance_evaluation import calculate_metrics, is_regression_task
from src.evaluation.metrics import METRIC_CHOICES
from src.evaluation.pairwise_correlation_evaluation import evaluate_pairwise_correlation


DEFAULT_VARIANTS = ("paft_full", "paft_anon_headers", "paft_graph_orders")
METRIC_ALIASES = {
    "all": "all",
    "downstream": "downstream",
    "utility": "downstream",
    "fidelity": "fidelity",
    "pairwise": "fidelity",
    "pairwise_correlation": "fidelity",
    "privacy": "privacy",
    "dcr": "privacy",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def eval_root() -> Path:
    return Path(__file__).resolve().parent


def resolve_path(path_value: str | Path, base: Path | None = None) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return (base or eval_root()) / path


def split_csv_arg(value: str | None) -> list[str] | None:
    if value is None:
        return None
    items = [item.strip() for item in value.split(",") if item.strip()]
    return items or None


def parse_int_csv_arg(value: str | None) -> set[int] | None:
    items = split_csv_arg(value)
    if not items:
        return None
    return {int(item) for item in items}


def normalize_metrics(value: str | None) -> set[str]:
    items = split_csv_arg(value) or ["all"]
    normalized: set[str] = set()
    for item in items:
        key = item.lower()
        mapped = METRIC_ALIASES.get(key)
        if mapped is None:
            valid = ", ".join(sorted(METRIC_ALIASES))
            raise ValueError(f"Unknown metric '{item}'. Valid values: {valid}")
        if mapped == "all":
            return set(METRIC_CHOICES)
        normalized.add(mapped)
    return normalized


def parse_seed(seed_dir: Path) -> int | None:
    if not seed_dir.name.startswith("seed_"):
        return None
    try:
        return int(seed_dir.name.split("seed_", 1)[1])
    except ValueError:
        return None


def load_dataset_info(data_root: Path, dataset: str) -> dict[str, Any]:
    info_path = data_root / dataset / "dataset_info.json"
    if not info_path.exists():
        raise FileNotFoundError(f"Missing dataset_info.json: {info_path}")
    with open(info_path, "r") as f:
        return json.load(f)


def target_column_from_info(dataset_info: dict[str, Any]) -> str:
    target = dataset_info.get("target_column") or dataset_info.get("label_column")
    if not target:
        raise ValueError("dataset_info.json must define target_column or label_column")
    return str(target)


def normalize_missing(series: pd.Series) -> pd.Series:
    values = series.astype(str).str.strip()
    return values.replace(
        {
            "": np.nan,
            "nan": np.nan,
            "NaN": np.nan,
            "None": np.nan,
            "none": np.nan,
            "null": np.nan,
            "NULL": np.nan,
            "NA": np.nan,
            "N/A": np.nan,
            "?": np.nan,
        }
    )


def default_value_for_column(series: pd.Series) -> Any:
    if pd.api.types.is_numeric_dtype(series):
        numeric = pd.to_numeric(series, errors="coerce").dropna()
        return float(numeric.median()) if not numeric.empty else 0.0

    cleaned = normalize_missing(series).dropna()
    if cleaned.empty:
        return "__MISSING__"
    return str(cleaned.mode().iloc[0])


def is_confident_numeric(series: pd.Series, threshold: float = 0.99) -> bool:
    if pd.api.types.is_numeric_dtype(series):
        return True
    cleaned = normalize_missing(series)
    non_missing = int(cleaned.notna().sum())
    if non_missing == 0:
        return False
    numeric = pd.to_numeric(cleaned, errors="coerce")
    return float(numeric.notna().sum()) / float(non_missing) >= threshold


def align_synthetic_to_real_schema(
    synth_df: pd.DataFrame,
    real_train_df: pd.DataFrame,
) -> pd.DataFrame:
    aligned = pd.DataFrame(index=synth_df.index)
    for col in real_train_df.columns:
        if col in synth_df.columns:
            aligned[col] = synth_df[col]
        else:
            aligned[col] = default_value_for_column(real_train_df[col])
    return aligned[real_train_df.columns]


def align_frames_and_types(
    synth_df: pd.DataFrame,
    real_train_df: pd.DataFrame,
    real_test_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str], list[str]]:
    """Align schema and coerce dtypes using the real training split as reference."""
    synth_df = align_synthetic_to_real_schema(synth_df, real_train_df)
    real_test_df = real_test_df.reindex(columns=real_train_df.columns)

    categorical_cols: list[str] = []
    numerical_cols: list[str] = []
    for col in real_train_df.columns:
        if is_confident_numeric(real_train_df[col]):
            numerical_cols.append(col)
        else:
            categorical_cols.append(col)

    for col in numerical_cols:
        for df in (synth_df, real_train_df, real_test_df):
            df[col] = pd.to_numeric(normalize_missing(df[col]), errors="coerce")
        fill_value = real_train_df[col].median()
        if pd.isna(fill_value):
            fill_value = 0.0
        for df in (synth_df, real_train_df, real_test_df):
            df[col] = df[col].fillna(fill_value)

    for col in categorical_cols:
        for df in (synth_df, real_train_df, real_test_df):
            df[col] = normalize_missing(df[col]).fillna("__MISSING__").astype(str)

    return synth_df, real_train_df, real_test_df, categorical_cols, numerical_cols


def prepare_xgboost_data(
    synth_df: pd.DataFrame,
    real_train_df: pd.DataFrame,
    real_test_df: pd.DataFrame,
    target_col: str,
    regression_task: bool,
) -> tuple[pd.DataFrame, np.ndarray, pd.DataFrame, np.ndarray]:
    """Match the StructSynth paper's preprocessing before XGBoost evaluation.

    The paper evaluator trains on D_fewshot + D_synth, normalizes categorical
    strings, maps generated categories absent from the real test split to an
    ``others`` bucket, jointly one-hot encodes train/test, and globally encodes
    classification labels.  Keeping this behavior here makes PAFT utility
    directly comparable to the StructSynth/FD-prior utility results.
    """
    train_df = pd.concat([real_train_df, synth_df], ignore_index=True)
    eval_df = real_test_df.copy()
    train_df = train_df.copy()
    feature_cols = [col for col in eval_df.columns if col != target_col]
    categorical_features = [
        col
        for col in eval_df.select_dtypes(include=["object", "category"]).columns
        if col != target_col
    ]

    dummy_row_indices: list[int] = []
    for col in categorical_features:
        eval_df[col] = eval_df[col].astype(str).str.strip().str.lower()
        train_df[col] = train_df[col].astype(str).str.strip().str.lower()
        valid_values = set(eval_df[col].unique())
        train_df[col] = train_df[col].map(lambda value: value if value in valid_values else "others")
        if "others" in train_df[col].values and "others" not in valid_values:
            dummy_row = eval_df.iloc[0].copy()
            dummy_row[col] = "others"
            eval_df = pd.concat([eval_df, pd.DataFrame([dummy_row])], ignore_index=True)
            dummy_row_indices.append(len(eval_df) - 1)

    if regression_task:
        eval_df[target_col] = pd.to_numeric(eval_df[target_col], errors="coerce")
        train_df[target_col] = pd.to_numeric(train_df[target_col], errors="coerce")
        train_df = train_df.dropna(subset=[target_col])
    else:
        eval_df[target_col] = eval_df[target_col].astype(str).str.strip().str.lower()
        train_df[target_col] = train_df[target_col].astype(str).str.strip().str.lower()

    combined_df = pd.concat([eval_df, train_df], ignore_index=True)
    if categorical_features:
        categorical_data = pd.get_dummies(
            combined_df[categorical_features],
            drop_first=True,
        )
    else:
        categorical_data = pd.DataFrame(index=combined_df.index)

    numerical_features = [col for col in feature_cols if col not in categorical_features]
    numerical_data = combined_df[numerical_features].select_dtypes(
        include=["int64", "float64", "int32", "float32", "bool"]
    )
    processed_features = pd.concat([numerical_data, categorical_data], axis=1)

    if regression_task:
        processed_labels = combined_df[target_col].to_numpy(dtype=float)
    else:
        processed_labels = LabelEncoder().fit_transform(combined_df[target_col])

    eval_mask = np.ones(len(eval_df), dtype=bool)
    eval_mask[dummy_row_indices] = False
    X_test = processed_features.iloc[: len(eval_df)].loc[eval_mask]
    y_test = processed_labels[: len(eval_df)][eval_mask]
    X_train = processed_features.iloc[len(eval_df) :]
    y_train = processed_labels[len(eval_df) :]
    return X_train, y_train, X_test, y_test


def calculate_xgboost_downstream_performance(
    synth_df: pd.DataFrame,
    real_train_df: pd.DataFrame,
    real_test_df: pd.DataFrame,
    dataset: str,
    dataset_info: dict[str, Any],
) -> dict[str, float]:
    """Evaluate PAFT with the XGBoost configuration used by StructSynth."""
    if xgb is None:
        raise ImportError(
            "xgboost is required for PAFT utility evaluation. "
            "Run this script with 00_active/StructSynthFull/venv/bin/python."
        )

    target_col = target_column_from_info(dataset_info)
    regression_task = is_regression_task(dataset, dataset_info)
    X_train, y_train, X_test, y_test = prepare_xgboost_data(
        synth_df=synth_df,
        real_train_df=real_train_df,
        real_test_df=real_test_df,
        target_col=target_col,
        regression_task=regression_task,
    )

    common_params = {
        "max_depth": 6,
        "learning_rate": 0.1,
        "n_estimators": 100,
        "seed": 42,
    }
    if regression_task:
        model = xgb.XGBRegressor(
            objective="reg:squarederror",
            eval_metric="rmse",
            **common_params,
        )
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        return calculate_metrics(
            pd.Series(y_test),
            y_pred,
            None,
            is_regression=True,
        )

    unique_train = np.unique(y_train)
    if unique_train.size < 2:
        y_pred = np.full(len(X_test), unique_train[0])
        return calculate_metrics(
            pd.Series(y_test),
            y_pred,
            None,
            is_regression=False,
            classes=unique_train,
        )

    train_encoder = LabelEncoder()
    y_train_encoded = train_encoder.fit_transform(y_train)
    n_classes = len(train_encoder.classes_)
    classification_params = dict(common_params)
    if n_classes == 2:
        classification_params.update(objective="binary:logistic", eval_metric="logloss")
    else:
        classification_params.update(
            objective="multi:softprob",
            eval_metric="mlogloss",
            num_class=n_classes,
        )

    model = xgb.XGBClassifier(**classification_params)
    model.fit(X_train, y_train_encoded)
    y_pred_encoded = model.predict(X_test).astype(int)
    y_pred = train_encoder.inverse_transform(y_pred_encoded)
    y_pred_proba = model.predict_proba(X_test)
    return calculate_metrics(
        pd.Series(y_test),
        y_pred,
        y_pred_proba,
        is_regression=False,
        classes=train_encoder.classes_,
    )


def discover_datasets(results_root: Path, variants: Iterable[str], shot: int) -> list[str]:
    datasets: set[str] = set()
    for variant in variants:
        variant_root = results_root / variant
        if not variant_root.exists():
            continue
        for dataset_dir in variant_root.iterdir():
            if (dataset_dir / f"{shot}_shot" / "paft").exists():
                datasets.add(dataset_dir.name)
    return sorted(datasets)


def discover_synthetic_files(
    results_root: Path,
    variant: str,
    dataset: str,
    shot: int,
    n_samples: int,
    seed_filter: set[int] | None,
) -> list[tuple[int, Path]]:
    method_root = results_root / variant / dataset / f"{shot}_shot" / "paft"
    files: list[tuple[int, Path]] = []
    for seed_dir in sorted(method_root.glob("seed_*")):
        seed = parse_seed(seed_dir)
        if seed is None or (seed_filter is not None and seed not in seed_filter):
            continue
        synth_path = seed_dir / f"n{n_samples}" / "synthetic_data.csv"
        if synth_path.exists():
            files.append((seed, synth_path))
    return files


def finite_values(values: Iterable[Any]) -> np.ndarray:
    numeric = pd.to_numeric(pd.Series(list(values)), errors="coerce").to_numpy(dtype=float)
    return numeric[np.isfinite(numeric)]


def mean_std(values: Iterable[Any]) -> tuple[float, float, int]:
    arr = finite_values(values)
    if arr.size == 0:
        return float("nan"), float("nan"), 0
    return float(arr.mean()), float(arr.std(ddof=0)), int(arr.size)


def write_summary(
    output_dir: Path,
    dataset: str,
    variant: str,
    shot: int,
    n_samples: int,
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "detailed_results.json", "w") as f:
        json.dump(rows, f, indent=2)

    df = pd.DataFrame(rows).sort_values("seed")
    df.to_csv(output_dir / "detailed_results.csv", index=False)

    metric_cols = [col for col in df.columns if col not in {"dataset", "variant", "seed"}]
    summary: dict[str, Any] = {
        "dataset": dataset,
        "variant": variant,
        "shot": shot,
        "n_samples": n_samples,
        "num_seeds": int(df.shape[0]),
        "metrics": {},
    }
    for col in metric_cols:
        mean_value, std_value, n_valid = mean_std(df[col])
        if n_valid > 0:
            summary["metrics"][col] = {
                "mean": mean_value,
                "std": std_value,
                "n": n_valid,
                "display": f"{mean_value:.4f} +- {std_value:.4f}",
            }

    with open(output_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    lines = [
        f"# PAFT Evaluation Summary: {variant}",
        "",
        f"Dataset: {dataset}",
        f"Shot: {shot}",
        f"n_samples: {n_samples}",
        f"Number of seeds: {df.shape[0]}",
        "",
        "## Averaged Metrics",
        "",
    ]
    for col, stats in sorted(summary["metrics"].items()):
        lines.append(f"- **{col}**: {stats['display']}")
    lines.append("")
    (output_dir / "summary.md").write_text("\n".join(lines))

    return summary


def evaluate_one_dataset_variant(
    data_root: Path,
    results_root: Path,
    output_root: Path,
    dataset: str,
    variant: str,
    shot: int,
    n_samples: int,
    seed_filter: set[int] | None,
    metrics: set[str],
) -> dict[str, Any] | None:
    dataset_info = load_dataset_info(data_root, dataset)
    target_col = target_column_from_info(dataset_info)
    synthetic_files = discover_synthetic_files(
        results_root=results_root,
        variant=variant,
        dataset=dataset,
        shot=shot,
        n_samples=n_samples,
        seed_filter=seed_filter,
    )
    if not synthetic_files:
        print(f"Skip {variant}/{dataset}: no synthetic files found.")
        return None

    rows: list[dict[str, Any]] = []
    for seed, synth_path in synthetic_files:
        train_path = data_root / dataset / f"{shot}_shot" / f"seed_{seed}" / "train.csv"
        test_path = data_root / dataset / f"{shot}_shot" / f"seed_{seed}" / "test.csv"
        if not train_path.exists() or not test_path.exists():
            print(f"Skip {variant}/{dataset}/seed_{seed}: missing real split.")
            continue

        synth_df = pd.read_csv(synth_path)
        real_train_df = pd.read_csv(train_path)
        real_test_df = pd.read_csv(test_path)
        if target_col not in real_train_df.columns:
            raise KeyError(f"Target column '{target_col}' is missing from {train_path}")

        # Preserve the raw dtypes for the exact StructSynth XGBoost
        # preprocessing.  Fidelity and DCR continue to use normalized frames.
        xgb_synth_df = align_synthetic_to_real_schema(synth_df, real_train_df)
        xgb_real_train_df = real_train_df.copy()
        xgb_real_test_df = real_test_df.reindex(columns=real_train_df.columns).copy()

        synth_df, real_train_df, real_test_df, categorical_cols, numerical_cols = align_frames_and_types(
            synth_df=synth_df,
            real_train_df=real_train_df,
            real_test_df=real_test_df,
        )

        row: dict[str, Any] = {
            "dataset": dataset,
            "variant": variant,
            "seed": seed,
        }
        if "privacy" in metrics:
            row.update(
                evaluate_dcr(
                    synth_df,
                    real_train_df,
                    real_test_df,
                    categorical_cols,
                    numerical_cols,
                    seed,
                )
            )
        if "fidelity" in metrics:
            row.update(
                evaluate_pairwise_correlation(
                    real_test_df,
                    synth_df,
                    numerical_cols,
                    categorical_cols,
                )
            )
        if "downstream" in metrics:
            row.update(
                calculate_xgboost_downstream_performance(
                    xgb_synth_df,
                    xgb_real_train_df,
                    xgb_real_test_df,
                    dataset,
                    dataset_info,
                )
            )

        rows.append(row)
        headline_bits = []
        for key in ("auc_roc", "accuracy", "r2", "pairwise_correlation_diff", "dcr"):
            value = row.get(key)
            if isinstance(value, (int, float)) and math.isfinite(float(value)):
                headline_bits.append(f"{key}={float(value):.4f}")
        print(f"Processed {variant}/{dataset}/seed_{seed}: " + ", ".join(headline_bits))

    if not rows:
        print(f"Skip {variant}/{dataset}: no rows evaluated.")
        return None

    output_dir = output_root / dataset / f"{shot}_shot" / variant
    return write_summary(output_dir, dataset, variant, shot, n_samples, rows)


def summary_key(summary: dict[str, Any]) -> tuple[Any, ...]:
    return (
        summary.get("dataset"),
        summary.get("variant"),
        summary.get("shot"),
        summary.get("n_samples"),
    )


def collect_existing_summaries(output_root: Path, current_summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries_by_key = {summary_key(summary): summary for summary in current_summaries}
    for summary_path in output_root.glob("*/100_shot/*/summary.json"):
        try:
            with open(summary_path, "r") as f:
                summary = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        summaries_by_key.setdefault(summary_key(summary), summary)
    return list(summaries_by_key.values())


def write_overview(output_root: Path, summaries: list[dict[str, Any]]) -> None:
    overview_rows: list[dict[str, Any]] = []
    for summary in summaries:
        row = {
            "dataset": summary["dataset"],
            "variant": summary["variant"],
            "shot": summary["shot"],
            "n_samples": summary["n_samples"],
            "num_seeds": summary["num_seeds"],
        }
        for metric, stats in summary["metrics"].items():
            row[f"{metric}_mean"] = stats["mean"]
            row[f"{metric}_std"] = stats["std"]
        overview_rows.append(row)

    output_root.mkdir(parents=True, exist_ok=True)
    overview_df = pd.DataFrame(overview_rows).sort_values(["dataset", "variant"])
    overview_df.to_csv(output_root / "paft_overview.csv", index=False)

    md_lines = ["# PAFT Evaluation Overview", ""]
    if overview_df.empty:
        md_lines.append("No results.")
    else:
        columns = list(overview_df.columns)
        md_lines.append("| " + " | ".join(columns) + " |")
        md_lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
        for _, row in overview_df.iterrows():
            values = []
            for col in columns:
                value = row[col]
                if isinstance(value, float):
                    values.append("" if pd.isna(value) else f"{value:.6f}")
                else:
                    values.append(str(value))
            md_lines.append("| " + " | ".join(values) + " |")
    md_lines.append("")
    (output_root / "paft_overview.md").write_text("\n".join(md_lines))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate PAFT generated data with downstream, fidelity, and privacy metrics."
    )
    parser.add_argument(
        "--paft-root",
        default=str(repo_root() / "Permutation-aided-Fine-tuning"),
        help="Path to the PAFT repository checkout.",
    )
    parser.add_argument(
        "--data-root",
        default=None,
        help="Real data root. Defaults to <paft-root>/data/structsynth.",
    )
    parser.add_argument(
        "--results-root",
        default=None,
        help="PAFT generated results root. Defaults to <paft-root>/results.",
    )
    parser.add_argument(
        "--output-root",
        default="results/paft_aligned",
        help="Where to write aligned evaluation outputs.",
    )
    parser.add_argument(
        "--variants",
        default=",".join(DEFAULT_VARIANTS),
        help="Comma-separated PAFT result variants.",
    )
    parser.add_argument(
        "--datasets",
        default=None,
        help="Comma-separated datasets. Defaults to datasets discovered under the selected variants.",
    )
    parser.add_argument("--shot", type=int, default=100)
    parser.add_argument("--n-samples", type=int, default=1000)
    parser.add_argument("--seeds", default=None, help="Comma-separated seed filter, e.g. 42,43,44.")
    parser.add_argument(
        "--metrics",
        default="all",
        help="Comma-separated metrics: downstream,fidelity,privacy or all.",
    )

    args = parser.parse_args()

    paft_root = resolve_path(args.paft_root, repo_root())
    data_root = resolve_path(args.data_root, eval_root()) if args.data_root else paft_root / "data" / "structsynth"
    results_root = (
        resolve_path(args.results_root, eval_root()) if args.results_root else paft_root / "results"
    )
    output_root = resolve_path(args.output_root, eval_root())
    variants = split_csv_arg(args.variants) or list(DEFAULT_VARIANTS)
    datasets = split_csv_arg(args.datasets)
    if datasets is None:
        datasets = discover_datasets(results_root, variants, args.shot)
    seed_filter = parse_int_csv_arg(args.seeds)
    metrics = normalize_metrics(args.metrics)

    print(f"PAFT root: {paft_root}")
    print(f"Data root: {data_root}")
    print(f"Results root: {results_root}")
    print(f"Output root: {output_root}")
    print(f"Datasets: {', '.join(datasets)}")
    print(f"Variants: {', '.join(variants)}")
    print(f"Metrics: {', '.join(sorted(metrics))}")

    summaries: list[dict[str, Any]] = []
    for variant in variants:
        for dataset in datasets:
            summary = evaluate_one_dataset_variant(
                data_root=data_root,
                results_root=results_root,
                output_root=output_root,
                dataset=dataset,
                variant=variant,
                shot=args.shot,
                n_samples=args.n_samples,
                seed_filter=seed_filter,
                metrics=metrics,
            )
            if summary is not None:
                summaries.append(summary)

    write_overview(output_root, collect_existing_summaries(output_root, summaries))
    print(f"\nWrote PAFT aligned evaluation outputs to: {output_root}")


if __name__ == "__main__":
    main()
