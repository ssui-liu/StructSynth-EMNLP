import numpy as np
import pandas as pd
import pytest

from structsynth.associations import (
    association_evidence,
    association_matrix,
    association_score,
    categorical_features,
)


def test_negative_pearson_is_strength_not_signed_correlation():
    score = association_score(pd.Series([1, 2, 3, 4]), pd.Series([8, 6, 4, 2]))
    assert score.value == pytest.approx(1)
    assert score.method == "absolute_pearson"
    assert score.defined


def test_cramers_v_matches_appendix_bias_correction_without_yates():
    # Contingency table [[10, 0], [0, 10]] has chi²=20 and corrected V=1.
    left = pd.Series(["a"] * 10 + ["b"] * 10)
    right = pd.Series(["x"] * 10 + ["y"] * 10)
    score = association_score(left, right, left_categorical=True, right_categorical=True)
    assert score.value == pytest.approx(1)
    # Table [[8, 2], [2, 8]] has chi²=7.2; direct appendix expression.
    right = pd.Series(["x"] * 8 + ["y"] * 2 + ["x"] * 2 + ["y"] * 8)
    score = association_score(left, right, left_categorical=True, right_categorical=True)
    expected = np.sqrt((7.2 / 20 - 1 / 19) / (1 - 1 / 19))
    assert score.value == pytest.approx(expected)


def test_mixed_ratio_uses_category_means_and_is_order_independent():
    category, value = pd.Series(["a", "a", "b", "b"]), pd.Series([0, 2, 4, 6])
    expected = np.sqrt(16 / 20)
    forward = association_score(category, value, left_categorical=True)
    reverse = association_score(value, category, right_categorical=True)
    assert forward.value == pytest.approx(expected)
    assert reverse == forward


def test_single_category_eta_is_defined_zero_when_continuous_variance_exists():
    score = association_score(pd.Series(["a", "a", "a"]), pd.Series([0, 1, 2]), left_categorical=True)
    assert score.value == 0
    assert score.defined


def test_pairwise_missing_and_nonfinite_values_are_excluded_without_imputation():
    left = pd.Series([1, 2, np.nan, np.inf, 5], index=[10, 11, 12, 13, 14])
    right = pd.Series([5, 4, 3, 2, np.nan])
    score = association_score(left, right)
    assert score.n_observations == 2
    assert score.value == pytest.approx(1)


@pytest.mark.parametrize(
    "left,right,categorical,reason",
    [
        ([None, 1], [2, None], False, "fewer_than_two_complete_observations"),
        ([1, 1], [2, 3], False, "constant_attribute"),
        (["a", "b"], ["x", "y"], True, "nonpositive_bias_corrected_dimension"),
    ],
)
def test_undefined_evidence_is_finite_and_explicit(left, right, categorical, reason):
    score = association_score(
        pd.Series(left), pd.Series(right),
        left_categorical=categorical, right_categorical=categorical,
    )
    assert score.value == 0
    assert not score.defined
    assert score.reason == reason


def test_integer_categorical_metadata_overrides_dtype_and_pair_is_cached():
    data = pd.DataFrame({"code": [0, 0, 1, 1], "value": [1, 3, 5, 7], "flag": [True, False] * 2})
    assert categorical_features(data) == {"flag"}
    evidence = association_evidence(data, ["code", "flag"])
    assert evidence["code"]["value"].method == "correlation_ratio"
    assert evidence["code"]["value"] is evidence["value"]["code"]
    matrix = association_matrix(data, ["code", "flag"])
    assert list(matrix.columns) == list(data.columns)
    assert np.allclose(matrix, matrix.T)
    assert ((matrix.to_numpy() >= 0) & (matrix.to_numpy() <= 1)).all()


def test_invalid_declared_continuous_text_and_unknown_categories_fail():
    with pytest.raises(ValueError, match="nonnumeric"):
        association_matrix(pd.DataFrame({"a": ["one", "two"], "b": [1, 2]}), [])
    with pytest.raises(ValueError, match="Unknown categorical"):
        association_matrix(pd.DataFrame({"a": [1, 2]}), ["unknown"])


def test_nullable_numeric_columns_and_extreme_finite_values():
    left = pd.Series([1, 2, None], dtype="Int64")
    score = association_score(left, pd.Series([3, 2, 1]))
    assert score.n_observations == 2
    assert score.value == pytest.approx(1)
    score = association_score(pd.Series([-1e300, 0, 1e300]), pd.Series([1e300, 0, -1e300]))
    assert score.value == pytest.approx(1)
