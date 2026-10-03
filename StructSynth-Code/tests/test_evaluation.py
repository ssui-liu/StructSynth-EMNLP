import json

import numpy as np
import pandas as pd
import pytest

from structsynth.evaluation import (
    PAPER_XGBOOST_PARAMS, TrainingPreprocessor, evaluate_downstream, evaluate_fidelity, evaluate_privacy,
)
from structsynth.schema import DatasetSpec


class RecordingClassifier:
    def fit(self, features, labels):
        self.features_ = features.copy()
        self.labels_ = labels.copy()
        self.classes_ = np.unique(labels)
        return self

    def predict(self, features):
        return (features[:, 0] > 0.5).astype(int)

    def predict_proba(self, features):
        positive = np.where(features[:, 0] > 0.5, 0.9, 0.1)
        return np.column_stack([1 - positive, positive])


def classification_data():
    spec = DatasetSpec("demo", ["number", "category", "target"], "target", "classification", ["category", "target"])
    real = pd.DataFrame({"number": [0.0, 1.0, 0.1, 0.9], "category": ["a", "b", "a", "b"], "target": ["no", "yes", "no", "yes"]})
    synth = pd.DataFrame({"number": [0.2, 0.8], "category": ["a", "b"], "target": ["no", "yes"]})
    test = pd.DataFrame({"number": [0.1, 0.9], "category": ["never seen", "b"], "target": ["no", "yes"]})
    return spec, real, synth, test


def test_preprocessor_fit_is_independent_of_test_values_and_preserves_rows():
    spec, real, _, test = classification_data()
    real.loc[0, "number"] = np.nan
    original = real.copy(deep=True)
    prep = TrainingPreprocessor(spec)
    train_before = prep.fit_transform(real)
    categories_before = [entry.copy() for entry in prep.encoder.categories_]
    transformed = prep.transform(test)
    changed = test.assign(number=[10000.0, -10000.0], category=["another unseen", "yet another unseen"])
    prep.transform(changed)
    np.testing.assert_array_equal(train_before, prep.transform(real))
    for before, after in zip(categories_before, prep.encoder.categories_):
        np.testing.assert_array_equal(before, after)
    assert transformed.shape == (2, 3)
    np.testing.assert_array_equal(transformed[0, 1:], [0, 0])
    assert train_before[0, 0] == pytest.approx(0.9)
    pd.testing.assert_frame_equal(real, original)


@pytest.mark.parametrize("protocol,rows,real_rows,synth_rows", [
    ("augmentation", 6, 4, 2), ("synthetic_only", 2, 0, 2), ("real_only", 4, 4, 0),
])
def test_downstream_protocol_uses_the_declared_training_data(protocol, rows, real_rows, synth_rows):
    spec, real, synth, test = classification_data()
    estimator = RecordingClassifier()
    result = evaluate_downstream(real, synth, test, spec, estimator=estimator, protocol=protocol)
    assert len(estimator.features_) == rows
    assert result["real_train_rows_used"] == real_rows
    assert result["synthetic_rows_used"] == synth_rows
    assert result["auc_roc"] == 1
    assert result["protocol"] == protocol
    assert result["metric_issues"] == []
    json.dumps(result, allow_nan=False)


def test_unknown_test_target_does_not_expand_train_label_vocabulary():
    spec, real, synth, test = classification_data()
    test = test.copy()
    test.loc[0, "target"] = "unseen target"
    estimator = RecordingClassifier()
    result = evaluate_downstream(real, synth, test, spec, estimator=estimator)
    assert len(estimator.classes_) == 2
    assert result["auc_roc"] is None
    assert "absent" in result["metric_issues"][0]


def test_multiclass_auc_and_probability_column_order_follow_training_classes():
    from sklearn.linear_model import LogisticRegression
    spec = DatasetSpec("multiclass", ["x", "target"], "target", "classification", ["target"])
    train = pd.DataFrame({"x": [-3, -2, 0, 1, 3, 4], "target": ["a", "a", "b", "b", "c", "c"]})
    result = evaluate_downstream(train, train, train, spec, estimator=LogisticRegression(), protocol="real_only")
    assert result["auc_average"] == "macro_ovr"
    assert result["auc_roc"] == 1


def test_regression_is_explicit_and_constant_target_does_not_get_fake_r2():
    spec = DatasetSpec("not_a_known_dataset", ["x", "target"], "target", "regression", [])
    train = pd.DataFrame({"x": [0.0, 1.0, 2.0, 3.0], "target": [0.0, 2.0, 4.0, 6.0]})
    result = evaluate_downstream(train, train, train, spec, model="ridge")
    assert result["r2"] > 0.9
    constant = train.assign(target=2.0)
    result = evaluate_downstream(train, train, constant, spec, model="ridge")
    assert result["r2"] is None
    assert result["metric_issues"]


def test_paper_xgboost_backend_can_train_classification_and_regression():
    pytest.importorskip("xgboost")
    spec, real, synth, test = classification_data()
    result = evaluate_downstream(real, synth, test, spec)
    assert result["model"] == "xgboost"
    assert result["protocol"] == "augmentation"
    assert result["auc_roc"] is not None
    spec = DatasetSpec("regression", ["number", "target"], "target", "regression", [])
    frame = pd.DataFrame({"number": np.arange(20), "target": np.arange(20) * 2.0})
    assert evaluate_downstream(frame, frame, frame, spec)["r2"] > 0.95
    assert PAPER_XGBOOST_PARAMS["n_estimators"] == 100


@pytest.mark.parametrize("task", ["classification", "regression"])
def test_auxiliary_mlp_runs_with_declared_model_and_seed(task):
    spec, real, synth, test = classification_data()
    if task == "regression":
        spec = DatasetSpec("regression", list(real), "target", "regression", ["category"])
        real = real.assign(target=real["number"] * 2)
        synth = synth.assign(target=synth["number"] * 2)
        test = test.assign(target=test["number"] * 2)
    result = evaluate_downstream(real, synth, test, spec, model="mlp", seed=73,
                                model_params={"solver": "lbfgs", "hidden_layer_sizes": (5,), "max_iter": 1000})
    assert result["model"] == "mlp"
    assert result["seed"] == 73
    assert result[result["primary_metric"]] is not None


def test_privacy_balances_references_and_uses_uniform_all_record_ties():
    spec = DatasetSpec("privacy", ["x", "target"], "target", "regression", [])
    train = pd.DataFrame({"x": [0.0, 0.0], "target": [0.0, 0.0]})
    test = pd.DataFrame({"x": [0.0, 2.0], "target": [0.0, 0.0]})
    synthetic = train.iloc[:1]
    result = evaluate_privacy(synthetic, train, test, spec)
    assert result["privacy_risk"] == pytest.approx(2 / 3)
    assert result["tied_synthetic_rows"] == 1
    reversed_result = evaluate_privacy(synthetic, train.iloc[::-1], test.iloc[::-1], spec)
    assert reversed_result["privacy_risk"] == result["privacy_risk"]
    assert evaluate_privacy(train, train, train, spec)["privacy_risk"] == 0.5
    large_test = pd.concat([test] * 7, ignore_index=True)
    equalized = evaluate_privacy(synthetic, train, large_test, spec, seed=8)
    assert equalized["reference_size_per_split"] == 2
    assert equalized == evaluate_privacy(synthetic, train, large_test, spec, seed=8)
    json.dumps(equalized, allow_nan=False)


def test_privacy_raw_distance_and_optional_train_scaling_are_explicit():
    spec = DatasetSpec("privacy", ["x", "target"], "target", "regression", [])
    train = pd.DataFrame({"x": [0.0, 100.0], "target": [0.0, 1.0]})
    test = pd.DataFrame({"x": [10.0, 30.0], "target": [1.0, 0.0]})
    synthetic = pd.DataFrame({"x": [9.0], "target": [0.0]})
    raw = evaluate_privacy(synthetic, train, test, spec)
    scaled = evaluate_privacy(synthetic, train, test, spec, numeric_scaling="train_range")
    assert raw["numeric_scaling"] == "none"
    assert raw["mean_distance_to_train"] == 9
    assert raw["mean_distance_to_test"] == 2
    assert raw["privacy_risk"] == 0
    assert scaled["numeric_scale"] == {"x": 100.0, "target": 1.0}
    assert scaled["privacy_risk"] == 1
    transformed = [frame.assign(x=frame["x"] * 1000) for frame in (synthetic, train, test)]
    assert evaluate_privacy(*transformed, spec, numeric_scaling="train_range")["privacy_risk"] == scaled["privacy_risk"]


def test_privacy_categories_and_chunking_preserve_hamming_definition():
    spec = DatasetSpec("privacy", ["color", "target"], "target", "classification", ["color", "target"])
    train = pd.DataFrame({"color": ["red", "blue"], "target": ["yes", "no"]})
    test = pd.DataFrame({"color": ["green", "green"], "target": ["yes", "no"]})
    result = evaluate_privacy(train, train, test, spec, chunk_size=1)
    assert result["privacy_risk"] == 1
    assert result["mean_distance_to_test"] == 1
    assert result == evaluate_privacy(train, train, test, spec, chunk_size=100)


def test_fidelity_uses_signed_not_absolute_pearson_and_all_pairs():
    spec = DatasetSpec("fidelity", ["x", "target"], "target", "regression", [])
    real = pd.DataFrame({"x": [0, 1, 2, 3], "target": [0, 1, 2, 3]})
    synth = pd.DataFrame({"x": [0, 1, 2, 3], "target": [3, 2, 1, 0]})
    result = evaluate_fidelity(real, synth, spec)
    assert result["pair_count"] == 1
    assert result["statistical_fidelity"] == pytest.approx(2)
    assert evaluate_fidelity(real, real, spec)["statistical_fidelity"] == 0


def test_fidelity_joint_tvd_keeps_mass_from_unseen_categories():
    spec = DatasetSpec("fidelity", ["category", "target"], "target", "classification", ["category", "target"])
    real = pd.DataFrame({"category": ["a", "a", "b", "b"], "target": ["0", "0", "1", "1"]})
    synth = pd.DataFrame({"category": ["a", "a", "c", "c"], "target": ["0", "0", "1", "1"]})
    assert evaluate_fidelity(real, synth, spec)["statistical_fidelity"] == 0.5


def test_large_integer_categories_do_not_collapse_through_float_encoding():
    spec = DatasetSpec("fidelity", ["category", "target"], "target", "classification", ["category", "target"])
    real = pd.DataFrame({"category": [2**53, 2**53], "target": ["a", "a"]})
    synth = pd.DataFrame({"category": [2**53 + 1, 2**53 + 1], "target": ["a", "a"]})
    assert evaluate_fidelity(real, synth, spec)["statistical_fidelity"] == 1


def test_mixed_fidelity_shares_reference_bins_and_constant_columns_are_defined():
    spec = DatasetSpec("fidelity", ["x", "target"], "target", "classification", ["target"])
    real = pd.DataFrame({"x": np.arange(100), "target": ["a"] * 100})
    shifted = pd.DataFrame({"x": np.arange(100) + 100, "target": ["a"] * 100})
    result = evaluate_fidelity(real, shifted, spec)
    assert result["statistical_fidelity"] == pytest.approx(0.9)
    assert result["real_bin_edges"]["x"][0] == 0
    assert result["real_bin_edges"]["x"][-1] == 99
    assert evaluate_fidelity(real, real, spec)["statistical_fidelity"] == 0
    assert evaluate_fidelity(real.assign(x=1), shifted.assign(x=2), spec)["statistical_fidelity"] == 1
    json.dumps(result, allow_nan=False)


def test_metrics_reject_missing_numeric_and_duplicate_columns_instead_of_silent_scores():
    spec, real, synth, test = classification_data()
    synth = synth.copy()
    synth.loc[0, "number"] = np.nan
    with pytest.raises(ValueError, match="finite"):
        evaluate_privacy(synth, real, test, spec)
    with pytest.raises(ValueError, match="finite"):
        evaluate_fidelity(real, synth, spec)
    duplicate = pd.concat([real, real[["number"]]], axis=1)
    with pytest.raises(ValueError, match="unique"):
        evaluate_downstream(duplicate, real, test, spec, estimator=RecordingClassifier())
