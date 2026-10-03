"""Explicit dataset schemas, held-out splits, and reproducible prompt examples.

Only ``infer_training_schema`` learns the classification target domain. Call it
after splitting so the generator never receives value domains from test.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from .schema import DatasetSpec


@dataclass
class DataSplit:
    train: pd.DataFrame
    test: pd.DataFrame
    unused: pd.DataFrame
    metadata: dict[str, Any]


def _scalar(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    return value


def _check_frame(frame: pd.DataFrame, spec: DatasetSpec, *, allow_empty: bool = False) -> None:
    if not frame.columns.is_unique:
        raise ValueError("Dataset columns must be unique")
    missing = set(spec.columns) - set(frame.columns)
    extra = set(frame.columns) - set(spec.columns)
    if missing or extra:
        raise ValueError(f"Dataset/schema mismatch: missing={sorted(missing)}, extra={sorted(extra)}")
    if frame.empty and not allow_empty:
        raise ValueError("Dataset is empty")
    if spec.target_column not in frame:
        raise ValueError(f"Target column {spec.target_column!r} is missing")
    if frame[spec.target_column].isna().any():
        raise ValueError("Target values cannot be missing")
    if spec.task_type not in {"classification", "regression"}:
        raise ValueError("task_type must be 'classification' or 'regression'")
    if spec.task_type == "regression":
        target = pd.to_numeric(frame[spec.target_column], errors="raise")
        if not np.isfinite(target.to_numpy(dtype=float)).all():
            raise ValueError("Regression targets must be finite numbers")


def _clean(frame: pd.DataFrame, cleaning: str) -> pd.DataFrame:
    """Historical benchmark transforms, enabled only by an explicit argument."""
    frame = frame.copy()
    if cleaning == "none":
        return frame
    if cleaning == "adult":
        required = {"country", "capital-gain", "capital-loss", "marital-status", "salary"}
        if not required.issubset(frame):
            raise ValueError(f"adult cleaning requires columns {sorted(required)}")
        frame = frame.replace(r"^\s*\?\s*$", np.nan, regex=True).dropna().copy()
        for column in frame.select_dtypes(include=["object", "category"]).columns:
            frame[column] = frame[column].astype(str).str.strip()
        frame["country"] = np.where(frame["country"] == "United-States", "US", "Non-US")
        frame["capital-gain"] = np.where(pd.to_numeric(frame["capital-gain"]) > 0, "Had gains", "No gains")
        frame["capital-loss"] = np.where(pd.to_numeric(frame["capital-loss"]) > 0, "Had losses", "No losses")
        frame["marital-status"] = frame["marital-status"].replace({
            "Divorced": "Single", "Married-spouse-absent": "Single", "Never-married": "Single",
            "Separated": "Single", "Widowed": "Single", "Married-AF-spouse": "Couple",
            "Married-civ-spouse": "Couple",
        })
        return frame.reset_index(drop=True)
    if cleaning == "anxiety":
        frame = frame.rename(columns={"Anxiety Level (1-10)": "Anxiety Level"})
        if "Anxiety Level" not in frame:
            raise ValueError("anxiety cleaning requires the Anxiety Level column")
        levels = pd.to_numeric(frame["Anxiety Level"], errors="raise")
        if levels.isna().any():
            raise ValueError("Anxiety target values cannot be missing")
        frame["Anxiety Level"] = np.select([levels <= 3, levels <= 6], ["Low", "Medium"], default="High")
        return frame
    raise ValueError(f"Unknown cleaning mode: {cleaning!r}")


def load_dataset(
    csv_path: str | Path,
    metadata_path: str | Path,
    *,
    task_type: str | None = None,
    target_column: str | None = None,
    cleaning: str = "none",
) -> tuple[pd.DataFrame, DatasetSpec]:
    """Read an explicit CSV and metadata, accepting legacy label/description keys.

    Task type must be declared in metadata or supplied explicitly; dataset names
    and target names never determine whether a task is classification/regression.
    Dtype inference describes storage only, and no category values are collected.
    """
    csv_path, metadata_path = Path(csv_path), Path(metadata_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if not isinstance(metadata, dict):
        raise ValueError("Dataset metadata must be a JSON object")
    # Earlier evaluation code also accepted {dataset_name: {...}} metadata.
    if csv_path.parent.name in metadata and isinstance(metadata[csv_path.parent.name], dict):
        metadata = metadata[csv_path.parent.name]
    # Pandas silently renames duplicate headers (e.g. target -> target.1), which
    # can turn a second copy of the label into a misleading downstream feature.
    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        header = next(csv.reader(stream), [])
    if not header or any(not name for name in header) or len(set(header)) != len(header):
        raise ValueError("CSV column names must be nonempty and unique")
    declared_categorical = metadata.get("categorical_columns", metadata.get("categorical_cols", []))
    domains = metadata.get("categories", {})
    boolean_columns = metadata.get("boolean_columns", [])
    string_columns = [
        column for column in declared_categorical
        if column not in boolean_columns and (
            not domains.get(column) or all(isinstance(value, str) for value in domains[column])
        )
    ]
    # Explicit textual domains preserve values such as "001". Numeric/bool
    # domains retain numeric/bool parsing; undeclared columns use ordinary dtype
    # inference. No value domains are learned from the full CSV.
    frame = _clean(pd.read_csv(csv_path, dtype={column: str for column in string_columns}), cleaning)
    target = target_column or metadata.get("target_column") or metadata.get("label_column")
    task_type = task_type or metadata.get("task_type")
    if target is None:
        raise ValueError("Declare target_column (legacy label_column is also accepted)")
    if task_type not in {"classification", "regression"}:
        raise ValueError("Declare task_type explicitly as 'classification' or 'regression'")
    if cleaning == "anxiety" and target == "Anxiety Level (1-10)":
        target = "Anxiety Level"
    if target not in frame:
        raise ValueError(f"Target column {target!r} is missing")
    if task_type == "regression":
        frame[target] = pd.to_numeric(frame[target], errors="raise")
    declared_columns = metadata.get("columns")
    if declared_columns is not None and list(declared_columns) != frame.columns.tolist():
        raise ValueError("Metadata columns must match CSV columns in order")
    booleans = list(metadata.get("boolean_columns", [c for c in frame if pd.api.types.is_bool_dtype(frame[c])]))
    inferred_categorical = [
        c for c in frame if not pd.api.types.is_numeric_dtype(frame[c]) and c not in booleans
    ]
    categorical = list(metadata.get("categorical_columns", metadata.get("categorical_cols", inferred_categorical)))
    if task_type == "classification" and target not in categorical and target not in booleans:
        categorical.append(target)
    spec = DatasetSpec(
        name=metadata.get("name", csv_path.parent.name), columns=frame.columns.tolist(),
        target_column=target, task_type=task_type, categorical_columns=categorical,
        descriptions=metadata.get("descriptions", metadata.get("description", {})),
        task=metadata.get("task", ""), integer_columns=list(metadata.get("integer_columns", [])),
        boolean_columns=booleans, nullable_columns=list(metadata.get("nullable_columns", [])),
        categories=dict(metadata.get("categories", {})),
    )
    _check_frame(frame, spec)
    for column in spec.numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    return frame, spec


def infer_training_schema(train: pd.DataFrame, spec: DatasetSpec) -> DatasetSpec:
    """Attach target domains inferred exclusively from limited real training.

    Feature domains are closed only when explicitly declared by metadata; a
    limited training set cannot establish that every feature category was seen.
    Likewise, numerical extrema are never inferred as generation constraints.
    """
    _check_frame(train, spec)
    categories = {column: list(values) for column, values in spec.categories.items()}
    if spec.task_type == "classification" and spec.target_column not in categories:
        categories[spec.target_column] = [_scalar(value) for value in pd.unique(train[spec.target_column].dropna())]
    integer_columns = list(spec.integer_columns)
    for column in spec.numeric_columns:
        values = pd.to_numeric(train[column].dropna(), errors="raise").to_numpy(dtype=float)
        # Float-valued measurements such as age may happen to be integral in a
        # small sample, so only storage dtype or explicit metadata imply integers.
        if pd.api.types.is_integer_dtype(train[column]) and column not in integer_columns:
            integer_columns.append(column)
        if not np.isfinite(values).all():
            raise ValueError(f"Numerical column {column!r} contains infinity")
    nullable = list(spec.nullable_columns)
    nullable.extend(c for c in spec.columns if train[c].isna().any() and c not in nullable)
    return replace(spec, categories=categories, integer_columns=integer_columns, nullable_columns=nullable)


def training_metadata(train: pd.DataFrame, spec: DatasetSpec) -> dict[str, Any]:
    """Descriptive provenance suitable for JSON; every statistic uses train only."""
    resolved = infer_training_schema(train, spec)
    numeric = {}
    for column in resolved.numeric_columns:
        values = pd.to_numeric(train[column], errors="raise").dropna()
        numeric[column] = {
            "count": int(len(values)),
            "min": float(values.min()) if len(values) else None,
            "max": float(values.max()) if len(values) else None,
            "mean": float(values.mean()) if len(values) else None,
        }
    return {
        "source": "limited_real_training_set", "rows": len(train), "columns": list(resolved.columns),
        "target_column": resolved.target_column, "task_type": resolved.task_type,
        "categorical_columns": list(resolved.categorical_columns),
        "numeric_columns": list(resolved.numeric_columns), "categories": resolved.categories,
        "observed_categories": {
            column: [_scalar(value) for value in pd.unique(train[column].dropna())]
            for column in resolved.columns
            if column in set(resolved.categorical_columns) | set(resolved.boolean_columns)
        },
        "integer_columns": resolved.integer_columns, "boolean_columns": resolved.boolean_columns,
        "nullable_columns": resolved.nullable_columns, "numeric_summary": numeric,
    }


def _classification_sample(
    frame: pd.DataFrame, target: str, n: int, rng: np.random.Generator, *, balanced: bool,
) -> np.ndarray:
    groups = [np.flatnonzero((frame[target] == label).to_numpy()) for label in pd.unique(frame[target])]
    classes = len(groups)
    if n < classes:
        raise ValueError(f"Requested {n} examples, but classification requires at least {classes} to cover every class")
    capacities = np.array([len(group) for group in groups])
    counts = np.ones(classes, dtype=int)
    priorities = rng.permutation(classes)
    rank = np.empty(classes, dtype=int)
    rank[priorities] = np.arange(classes)
    if balanced:
        # Water filling redistributes unused minority-class quota without replacement.
        while counts.sum() < n:
            candidates = np.flatnonzero(counts < capacities)
            chosen = min(candidates, key=lambda i: (counts[i], rank[i]))
            counts[chosen] += 1
    else:
        ideal = n * capacities / capacities.sum()
        while counts.sum() < n:
            candidates = np.flatnonzero(counts < capacities)
            chosen = min(candidates, key=lambda i: (counts[i] - ideal[i], rank[i]))
            counts[chosen] += 1
    selected = np.concatenate([rng.choice(group, size=int(count), replace=False) for group, count in zip(groups, counts)])
    rng.shuffle(selected)
    return selected


def sample_examples(
    train: pd.DataFrame, spec: DatasetSpec, *, n: int = 20, seed: int = 42, balanced: bool = True,
) -> pd.DataFrame:
    """Sample prompt examples without replacement or global RNG side effects.

    Classification prompts use equal class quotas where capacity permits;
    regression prompts use uniform sampling. ``n`` is capped at available rows.
    """
    _check_frame(train, spec)
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or n <= 0:
        raise ValueError("n must be a positive integer")
    n = min(n, len(train))
    rng = np.random.default_rng(seed)
    if spec.task_type == "classification":
        positions = _classification_sample(train, spec.target_column, n, rng, balanced=balanced)
    else:
        positions = rng.choice(len(train), size=n, replace=False)
    return train.iloc[positions].copy().reset_index(drop=True)


def split_dataset(
    frame: pd.DataFrame, spec: DatasetSpec, *, shot: int, seed: int, test_size: float = 0.2,
) -> DataSplit:
    """Hold out test first, then subsample the limited real training set.

    Classification holdout is stratified; its training subsample is proportional
    with at least one instance per class. Remaining rows are ``unused`` and must
    never enter graph discovery, synthesis, training metadata, or evaluation fit.
    """
    _check_frame(frame, spec)
    if isinstance(shot, bool) or not isinstance(shot, (int, np.integer)) or shot <= 0:
        raise ValueError("shot must be a positive integer")
    if not isinstance(test_size, (float, int)) or isinstance(test_size, bool) or not 0 < test_size < 1:
        raise ValueError("test_size must be a fraction strictly between 0 and 1")
    frame = frame.reset_index(drop=True)
    positions = np.arange(len(frame))
    stratify = frame[spec.target_column] if spec.task_type == "classification" else None
    try:
        full_train, test_positions = train_test_split(positions, test_size=test_size, random_state=seed, stratify=stratify)
    except ValueError as exc:
        raise ValueError(f"Cannot create requested holdout split: {exc}") from exc
    if shot > len(full_train):
        raise ValueError(f"shot={shot} exceeds available training rows ({len(full_train)}) after holdout")
    rng = np.random.default_rng(seed)
    if spec.task_type == "classification":
        local = _classification_sample(frame.iloc[full_train], spec.target_column, shot, rng, balanced=False)
        train_positions = full_train[local]
    else:
        train_positions = rng.choice(full_train, size=shot, replace=False)
    unused_positions = full_train[~np.isin(full_train, train_positions)]
    train = frame.iloc[train_positions].copy().reset_index(drop=True)
    fingerprint = hashlib.sha256(frame.to_csv(index=False).encode("utf-8")).hexdigest()
    metadata = {
        "split_version": "holdout_then_limited_v1", "seed": int(seed), "test_size": float(test_size),
        "shot": int(shot), "total_rows": len(frame), "train_full_rows": len(full_train),
        "train_rows": len(train), "test_rows": len(test_positions), "unused_rows": len(unused_positions),
        "stratified": spec.task_type == "classification", "data_sha256": fingerprint,
        "source_row_positions": {"train": train_positions.tolist(), "test": test_positions.tolist(), "unused": unused_positions.tolist()},
        "training_schema": training_metadata(train, spec),
    }
    return DataSplit(train, frame.iloc[test_positions].copy().reset_index(drop=True),
                     frame.iloc[unused_positions].copy().reset_index(drop=True), metadata)
