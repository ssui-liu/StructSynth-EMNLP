"""Association evidence from training data, as defined in the paper appendix.

These scores measure association strength, not direction or causality. Undefined
scores have the numeric value zero and carry an explicit ``defined=False`` flag.
Missing and non-finite observations are excluded separately for each pair.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

import numpy as np
import pandas as pd
from pandas.api.types import is_bool_dtype, is_numeric_dtype


@dataclass(frozen=True)
class AssociationScore:
    value: float
    method: str
    n_observations: int
    defined: bool = True
    reason: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def categorical_features(
    data: pd.DataFrame, categorical_columns: Iterable[str] | None = None
) -> set[str]:
    """Use declared categorical columns, or infer nonnumeric and boolean columns.

    An explicit declaration is authoritative, including an empty declaration.
    This prevents integer-coded categories from silently using Pearson's r.
    """
    if data.columns.has_duplicates:
        raise ValueError("Attribute names must be unique")
    if not all(isinstance(column, str) and column for column in data.columns):
        raise ValueError("Attribute names must be nonempty strings")
    if categorical_columns is None:
        return {
            column
            for column in data
            if not is_numeric_dtype(data[column]) or is_bool_dtype(data[column])
        }
    categorical = set(categorical_columns)
    unknown = categorical.difference(data.columns)
    if unknown:
        raise ValueError(f"Unknown categorical attributes: {sorted(unknown)}")
    return categorical


def _numeric(series: pd.Series) -> np.ndarray:
    # Explicitly declared continuous columns must actually contain numeric data;
    # coercing unexpected text to NaN would silently throw away evidence.
    try:
        converted = pd.to_numeric(series, errors="raise")
        return converted.to_numpy(dtype=float, na_value=np.nan)
    except (TypeError, ValueError) as error:
        raise ValueError(f"Continuous attribute {series.name!r} contains nonnumeric data") from error


def _scaled(values: np.ndarray) -> np.ndarray:
    """Scale before centering to avoid overflow without changing a coefficient."""
    scale = np.max(np.abs(values))
    return values / scale if scale else values


def association_score(
    left: pd.Series,
    right: pd.Series,
    *,
    left_categorical: bool = False,
    right_categorical: bool = False,
) -> AssociationScore:
    """Compute |Pearson r|, correlation ratio η, or bias-corrected Cramér V.

    Series are paired by position (the input table's rows), never by index label.
    Cramér V uses the uncorrected Pearson chi-square statistic followed by the
    paper's finite-sample bias correction, with no Yates continuity correction.
    """
    if len(left) != len(right):
        raise ValueError("Association inputs must have the same number of rows")
    method = (
        "cramers_v_bias_corrected"
        if left_categorical and right_categorical
        else "correlation_ratio"
        if left_categorical or right_categorical
        else "absolute_pearson"
    )
    x = left.to_numpy() if left_categorical else _numeric(left)
    y = right.to_numpy() if right_categorical else _numeric(right)
    valid = np.asarray(pd.notna(x) & pd.notna(y), dtype=bool)
    if not left_categorical:
        valid &= np.isfinite(x)
    if not right_categorical:
        valid &= np.isfinite(y)
    x, y = x[valid], y[valid]
    n = len(x)

    def undefined(reason: str) -> AssociationScore:
        return AssociationScore(0.0, method, n, False, reason)

    if n < 2:
        return undefined("fewer_than_two_complete_observations")
    if not left_categorical and not right_categorical:
        x, y = _scaled(x), _scaled(y)
        x, y = x - x.mean(), y - y.mean()
        x_norm, y_norm = np.linalg.norm(x), np.linalg.norm(y)
        if x_norm == 0 or y_norm == 0:
            return undefined("constant_attribute")
        value = abs(float(np.dot(x / x_norm, y / y_norm)))
    elif left_categorical and right_categorical:
        x_codes, x_labels = pd.factorize(x, sort=False)
        y_codes, y_labels = pd.factorize(y, sort=False)
        r, k = len(x_labels), len(y_labels)
        if r < 2 or k < 2:
            return undefined("constant_attribute")
        observed = np.bincount(x_codes * k + y_codes, minlength=r * k).reshape(r, k)
        expected = np.outer(observed.sum(axis=1), observed.sum(axis=0)) / n
        chi_squared = float(np.sum((observed - expected) ** 2 / expected))
        phi_squared = max(0.0, chi_squared / n - (k - 1) * (r - 1) / (n - 1))
        corrected_r = r - (r - 1) ** 2 / (n - 1)
        corrected_k = k - (k - 1) ** 2 / (n - 1)
        denominator = min(corrected_r - 1, corrected_k - 1)
        if denominator <= 0:
            return undefined("nonpositive_bias_corrected_dimension")
        value = float(np.sqrt(phi_squared / denominator))
    else:
        categories, continuous = (x, y) if left_categorical else (y, x)
        continuous = _scaled(continuous)
        centered = continuous - continuous.mean()
        denominator = float(np.dot(centered, centered))
        if denominator == 0:
            return undefined("constant_attribute")
        codes, _ = pd.factorize(categories, sort=False)
        counts = np.bincount(codes)
        centered_means = np.bincount(codes, weights=centered) / counts
        numerator = float(np.dot(counts, centered_means**2))
        value = float(np.sqrt(numerator / denominator))
    return AssociationScore(float(np.clip(value, 0.0, 1.0)), method, n)


def association_evidence(
    data: pd.DataFrame, categorical_columns: Iterable[str] | None = None
) -> dict[str, dict[str, AssociationScore]]:
    """Compute each unordered pair once; exclude self-scores from evidence."""
    categorical = categorical_features(data, categorical_columns)
    columns = list(data.columns)
    result: dict[str, dict[str, AssociationScore]] = {column: {} for column in columns}
    for index, left in enumerate(columns):
        for right in columns[index + 1 :]:
            score = association_score(
                data[left],
                data[right],
                left_categorical=left in categorical,
                right_categorical=right in categorical,
            )
            result[left][right] = result[right][left] = score
    return result


def association_matrix(
    data: pd.DataFrame, categorical_columns: Iterable[str] | None = None
) -> pd.DataFrame:
    """Return normalized symmetric strengths in the original column order.

    The diagonal is one by convention and is never used for graph induction.
    Off-diagonal diagnostics are available through ``association_evidence``.
    """
    evidence = association_evidence(data, categorical_columns)
    result = pd.DataFrame(np.eye(len(data.columns)), index=data.columns, columns=data.columns)
    for left, scores in evidence.items():
        for right, score in scores.items():
            result.loc[left, right] = score.value
    return result
