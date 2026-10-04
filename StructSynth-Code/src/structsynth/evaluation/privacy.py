"""Nearest-record privacy evaluation with explicit scaling and tie policies."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from ..data.validation import _check_frame
from ..schema import DatasetSpec
from .common import _categorical, _numeric


def evaluate_privacy(
    synthetic: pd.DataFrame,
    train: pd.DataFrame,
    test: pd.DataFrame,
    spec: DatasetSpec,
    *,
    seed: int = 42,
    numeric_scaling: str = "none",
    chunk_size: int = 128,
) -> dict[str, Any]:
    """Nearest-record training probability with equal-size reference sets.

    The paper's raw L1 + categorical Hamming distance is the default. Optional
    ``train_range`` divides by ranges fitted on the limited real train only.
    Ties are the expected training fraction when sampling uniformly among *all*
    closest records, so duplicate multiplicity is preserved without order bias.
    """
    for frame in (synthetic, train, test):
        _check_frame(frame, spec)
    if numeric_scaling not in {"none", "train_range"}:
        raise ValueError("numeric_scaling must be 'none' or 'train_range'")
    if isinstance(chunk_size, bool) or not isinstance(chunk_size, (int, np.integer)) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")
    numeric_columns = list(spec.numeric_columns)
    categorical_columns = [column for column in spec.columns if column not in numeric_columns]
    # Scale before reference downsampling: this optional fit uses real train only.
    train_numeric = _numeric(train, numeric_columns)
    scale = np.ptp(train_numeric, axis=0) if numeric_scaling == "train_range" else np.ones(len(numeric_columns))
    scale = np.where(scale > 0, scale, 1.0)
    n_reference = min(len(train), len(test))
    train_ref = train.sample(n=n_reference, random_state=seed) if len(train) > n_reference else train
    test_ref = test.sample(n=n_reference, random_state=seed) if len(test) > n_reference else test
    references = pd.concat([train_ref[spec.columns], test_ref[spec.columns]], ignore_index=True)
    real_numeric = _numeric(references, numeric_columns) / scale
    synthetic_numeric = _numeric(synthetic, numeric_columns) / scale
    real_categorical = _categorical(references, categorical_columns)
    synthetic_categorical = _categorical(synthetic, categorical_columns)
    risk_total, train_distance_total, test_distance_total = 0.0, 0.0, 0.0
    tied_records = 0
    for start in range(0, len(synthetic), chunk_size):
        end = min(start + chunk_size, len(synthetic))
        distances = np.zeros((end - start, len(references)), dtype=float)
        # Accumulate columns separately, avoiding O(chunk * refs * features) RAM.
        for column in range(len(numeric_columns)):
            distances += np.abs(synthetic_numeric[start:end, column, None] - real_numeric[None, :, column])
        for column in range(len(categorical_columns)):
            distances += synthetic_categorical[start:end, column, None] != real_categorical[None, :, column]
        closest = distances.min(axis=1)
        ties = np.isclose(distances, closest[:, None], rtol=1e-12, atol=1e-12)
        train_ties = ties[:, :n_reference].sum(axis=1)
        total_ties = ties.sum(axis=1)
        risk_total += (train_ties / total_ties).sum()
        tied_records += int((total_ties > 1).sum())
        train_distance_total += distances[:, :n_reference].min(axis=1).sum()
        test_distance_total += distances[:, n_reference:].min(axis=1).sum()
    risk = float(risk_total / len(synthetic))
    return {
        "privacy_risk": risk, "dcr": risk, "metric": "probability_nearest_record_in_train",
        "reference_size_per_split": n_reference, "synthetic_rows": len(synthetic), "seed": int(seed),
        "distance": "numerical_l1_plus_categorical_hamming", "numeric_scaling": numeric_scaling,
        "numeric_scale": dict(zip(numeric_columns, scale.tolist())),
        "tie_policy": "uniform_over_all_nearest_records", "tie_rtol": 1e-12, "tie_atol": 1e-12,
        "tied_synthetic_rows": tied_records,
        "mean_distance_to_train": float(train_distance_total / len(synthetic)),
        "mean_distance_to_test": float(test_distance_total / len(synthetic)),
    }
