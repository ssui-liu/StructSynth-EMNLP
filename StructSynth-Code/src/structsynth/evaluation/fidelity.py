"""Pairwise statistical fidelity using Pearson differences and joint TVD."""
from __future__ import annotations

from itertools import combinations
from typing import Any

import numpy as np
import pandas as pd

from ..data.validation import _check_frame
from ..schema import DatasetSpec
from .common import _numeric, _token


def _joint_tvd(real_a, real_b, synth_a, synth_b) -> float:
    real = pd.Series(list(zip(real_a, real_b)), dtype=object).value_counts(normalize=True)
    synth = pd.Series(list(zip(synth_a, synth_b)), dtype=object).value_counts(normalize=True)
    real, synth = real.align(synth, join="outer", fill_value=0)
    return float(0.5 * np.abs(real.to_numpy() - synth.to_numpy()).sum())


def _correlation(first: np.ndarray, second: np.ndarray) -> tuple[float, bool]:
    if len(first) < 2 or np.ptp(first) == 0 or np.ptp(second) == 0:
        return 0.0, True
    return float(np.corrcoef(first, second)[0, 1]), False


def evaluate_fidelity(
    real_reference: pd.DataFrame, synthetic: pd.DataFrame, spec: DatasetSpec, *, quantiles: int = 10,
) -> dict[str, Any]:
    """Mean signed-Pearson difference / joint TVD across all unordered pairs.

    Mixed pairs share quantile boundaries fitted on the stated real reference.
    Numeric constants have correlation zero by explicit convention; a constant
    mixed-pair reference uses exact-value categories rather than invalid qcut bins.
    The caller must label whether real_reference is train+test, test, or train.
    """
    _check_frame(real_reference, spec)
    _check_frame(synthetic, spec)
    if isinstance(quantiles, bool) or not isinstance(quantiles, (int, np.integer)) or quantiles < 2:
        raise ValueError("quantiles must be an integer >= 2")
    numeric = set(spec.numeric_columns)
    real_num = {column: _numeric(real_reference, [column])[:, 0] for column in numeric}
    synth_num = {column: _numeric(synthetic, [column])[:, 0] for column in numeric}
    real_cat = {column: real_reference[column].map(_token).to_numpy() for column in spec.columns if column not in numeric}
    synth_cat = {column: synthetic[column].map(_token).to_numpy() for column in spec.columns if column not in numeric}
    bin_edges, real_binned, synth_binned = {}, {}, {}
    for column in spec.numeric_columns:
        edges = np.unique(np.quantile(real_num[column], np.linspace(0, 1, quantiles + 1)))
        bin_edges[column] = edges.tolist()
        if len(edges) == 1:
            real_binned[column] = [_token(value) for value in real_num[column]]
            synth_binned[column] = [_token(value) for value in synth_num[column]]
        else:
            # The outer bins extend to infinity so synthetic outliers retain mass.
            real_binned[column] = np.searchsorted(edges[1:-1], real_num[column], side="left")
            synth_binned[column] = np.searchsorted(edges[1:-1], synth_num[column], side="left")
    pairs, constant_pairs = [], []
    for first, second in combinations(spec.columns, 2):
        if first in numeric and second in numeric:
            real_r, real_constant = _correlation(real_num[first], real_num[second])
            synth_r, synth_constant = _correlation(synth_num[first], synth_num[second])
            difference = abs(real_r - synth_r)
            kind = "absolute_signed_pearson_difference"
            if real_constant or synth_constant:
                constant_pairs.append([first, second])
        elif first not in numeric and second not in numeric:
            difference = _joint_tvd(real_cat[first], real_cat[second], synth_cat[first], synth_cat[second])
            kind = "joint_tvd"
        else:
            number, category = (first, second) if first in numeric else (second, first)
            difference = _joint_tvd(real_binned[number], real_cat[category], synth_binned[number], synth_cat[category])
            kind = "shared_quantile_joint_tvd"
        pairs.append({"columns": [first, second], "metric": kind, "difference": float(difference)})
    score = float(np.mean([pair["difference"] for pair in pairs])) if pairs else None
    return {
        "statistical_fidelity": score, "pairwise_correlation_diff": score,
        "pair_count": len(pairs), "pairs": pairs, "real_reference_rows": len(real_reference),
        "synthetic_rows": len(synthetic), "quantiles": int(quantiles), "binning": "shared_real_reference_quantiles",
        "real_bin_edges": bin_edges, "constant_correlation_policy": "zero",
        "constant_correlation_pairs": constant_pairs, "constant_mixed_policy": "exact_value_categories",
        "metric_issues": [] if pairs else ["Fidelity requires at least two columns"],
    }
