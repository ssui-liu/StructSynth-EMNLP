"""Training-only schema inference and descriptive metadata."""
from __future__ import annotations

from dataclasses import replace
from typing import Any

import numpy as np
import pandas as pd

from ..schema import DatasetSpec
from .validation import _check_frame


def _scalar(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    return value


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
