"""Shared categorical tokens and numeric array conversion for evaluation."""
from __future__ import annotations

import json
from numbers import Integral, Real
from typing import Any

import numpy as np
import pandas as pd


def _token(value: Any) -> str:
    """Collision-free categorical representation, including an explicit NA atom."""
    if pd.isna(value):
        atom = ["missing"]
    elif isinstance(value, (bool, np.bool_)):
        atom = ["boolean", bool(value)]
    elif isinstance(value, Integral):
        # Converting a categorical identifier through float would collapse
        # distinct integers above 2**53 into the same class.
        atom = ["number", int(value)]
    elif isinstance(value, Real):
        # Pandas concatenation can promote integer category values to floats.
        number = float(value)
        atom = ["number", int(number) if np.isfinite(number) and number.is_integer() else str(number)]
    else:
        atom = ["string", str(value)]
    return json.dumps(atom, ensure_ascii=False, separators=(",", ":"))


def _categorical(frame: pd.DataFrame, columns: list[str]) -> np.ndarray:
    if not columns:
        return np.empty((len(frame), 0), dtype=object)
    return np.column_stack([frame[column].map(_token).to_numpy() for column in columns])


def _numeric(frame: pd.DataFrame, columns: list[str], *, missing: bool = False) -> np.ndarray:
    if not columns:
        return np.empty((len(frame), 0), dtype=float)
    values = np.column_stack([pd.to_numeric(frame[column], errors="raise").to_numpy(dtype=float) for column in columns])
    if np.isinf(values).any() or (not missing and np.isnan(values).any()):
        raise ValueError("Numerical evaluation values must be finite; missing numeric values are not defined by this metric")
    return values
