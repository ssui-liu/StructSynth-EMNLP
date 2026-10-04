"""Explicit CSV/metadata loading and opt-in benchmark cleaning."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd

from ..schema import DatasetSpec
from .validation import _check_frame


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
