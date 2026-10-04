"""Strict JSON values and fingerprints shared by generation components."""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any, List

import pandas as pd


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                      separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def scalar(value: Any) -> Any:
    """Convert pandas/numpy scalars to strict JSON without inventing values."""
    if value is None or value is pd.NA:
        return None
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, float) and math.isnan(value):
        return None
    if type(value) not in (str, int, float, bool):
        raise ValueError("Tabular values must be JSON scalars; got %s" % type(value).__name__)
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Infinite numeric values are not supported")
    return value


def records(frame: pd.DataFrame) -> List[dict]:
    return [{column: scalar(value) for column, value in row.items()}
            for row in frame.to_dict(orient="records")]


def same_scalar(left: Any, right: Any) -> bool:
    # Python's True == 1 must not make boolean outputs valid integer labels.
    return type(left) is type(right) and left == right
