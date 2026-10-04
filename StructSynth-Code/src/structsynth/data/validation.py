"""Shared validation for tabular data and target types."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..schema import DatasetSpec


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
