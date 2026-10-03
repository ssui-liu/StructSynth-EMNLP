import json

import numpy as np
import pandas as pd
import pytest

from structsynth.data import infer_training_schema, load_dataset, sample_examples, split_dataset, training_metadata
from structsynth.schema import DatasetSpec


def classification_data():
    frame = pd.DataFrame({"row": np.arange(100), "color": ["blue", "red"] * 50, "label": ["major"] * 80 + ["minor"] * 20})
    spec = DatasetSpec("test", list(frame), "label", "classification", ["color", "label"])
    return frame, spec


def test_holdout_then_limited_training_is_disjoint_reproducible_and_shot_independent():
    frame, spec = classification_data()
    first = split_dataset(frame, spec, shot=20, seed=42)
    second = split_dataset(frame, spec, shot=20, seed=42)
    larger = split_dataset(frame, spec, shot=30, seed=42)
    assert (len(first.train), len(first.test), len(first.unused)) == (20, 20, 60)
    pd.testing.assert_frame_equal(first.train, second.train)
    pd.testing.assert_frame_equal(first.test, larger.test)
    partitions = [set(part["row"]) for part in (first.train, first.test, first.unused)]
    assert len(set.union(*partitions)) == len(frame)
    assert not partitions[0] & partitions[1]
    assert not partitions[0] & partitions[2]
    assert not partitions[1] & partitions[2]
    assert first.train["label"].value_counts().to_dict() == {"major": 16, "minor": 4}
    assert first.test["label"].value_counts().to_dict() == {"major": 16, "minor": 4}
    assert first.metadata == second.metadata
    json.dumps(first.metadata, allow_nan=False)


def test_all_available_training_rows_and_regression_targets_are_supported():
    frame = pd.DataFrame({"x": np.arange(20), "arbitrary_target_name": np.linspace(0, 1, 20)})
    spec = DatasetSpec("unknown_dataset", list(frame), "arbitrary_target_name", "regression", [])
    result = split_dataset(frame, spec, shot=16, seed=7)
    assert len(result.train) == 16
    assert result.unused.empty
    assert not result.metadata["stratified"]
    assert len(sample_examples(result.train, spec, n=5, seed=3)) == 5


def test_invalid_shot_and_impossible_class_coverage_fail_explicitly():
    frame, spec = classification_data()
    with pytest.raises(ValueError, match="exceeds available"):
        split_dataset(frame, spec, shot=81, seed=42)
    with pytest.raises(ValueError, match="cover every class"):
        split_dataset(frame, spec, shot=1, seed=42)
    with pytest.raises(ValueError, match="positive integer"):
        split_dataset(frame, spec, shot=0, seed=42)
    singleton = frame.copy()
    singleton.loc[0, "label"] = "singleton"
    with pytest.raises(ValueError, match="holdout"):
        split_dataset(singleton, spec, shot=20, seed=42)


def test_prompt_examples_balance_capacity_and_do_not_modify_global_rng():
    frame, spec = classification_data()
    np.random.seed(83)
    state = np.random.get_state()
    first = sample_examples(frame, spec, n=20, seed=42)
    second = sample_examples(frame, spec, n=20, seed=42)
    assert first["label"].value_counts().to_dict() == {"major": 10, "minor": 10}
    pd.testing.assert_frame_equal(first, second)
    assert first["row"].is_unique
    assert np.array_equal(state[1], np.random.get_state()[1])
    capped = sample_examples(frame, spec, n=60, seed=42)
    assert capped["label"].value_counts().to_dict() == {"major": 40, "minor": 20}
    assert len(sample_examples(frame, spec, n=1000, seed=42)) == len(frame)


def test_schema_domains_are_train_only_and_do_not_bound_continuous_values():
    frame, spec = classification_data()
    train = frame.iloc[:20].copy()
    learned = infer_training_schema(train, spec)
    assert learned.categories["label"] == ["major"]
    assert "color" not in learned.categories
    assert training_metadata(train, spec)["observed_categories"]["color"] == ["blue", "red"]
    assert spec.categories == {}
    assert learned.integer_columns == ["row"]
    assert "min" not in learned.to_dict()
    explicit = DatasetSpec("test", list(frame), "label", "classification", ["color", "label"], categories={"label": ["major", "minor"]})
    assert infer_training_schema(train, explicit).categories["label"] == ["major", "minor"]


def test_metadata_compatibility_requires_explicit_task_and_never_learns_csv_categories(tmp_path):
    frame, _ = classification_data()
    csv_path = tmp_path / "raw.csv"
    metadata = tmp_path / "meta.json"
    frame.to_csv(csv_path, index=False)
    metadata.write_text(json.dumps({"label_column": "label", "description": {"row": "row id"}}))
    with pytest.raises(ValueError, match="Declare task_type"):
        load_dataset(csv_path, metadata)
    loaded, spec = load_dataset(csv_path, metadata, task_type="classification")
    pd.testing.assert_frame_equal(frame, loaded)
    assert spec.descriptions == {"row": "row id"}
    assert spec.categories == {}
    assert "label" in spec.categorical_columns


def test_cleaning_is_opt_in_and_original_inputs_remain_untouched(tmp_path):
    frame = pd.DataFrame({"country": [" United-States", " Canada"], "capital-gain": [0, 20],
                          "capital-loss": [0, 0], "marital-status": [" Never-married", " Married-civ-spouse"],
                          "salary": [" <=50K", " >50K"]})
    csv_path, metadata = tmp_path / "raw.csv", tmp_path / "meta.json"
    frame.to_csv(csv_path, index=False)
    metadata.write_text(json.dumps({"target_column": "salary", "task_type": "classification"}))
    raw, _ = load_dataset(csv_path, metadata)
    cleaned, _ = load_dataset(csv_path, metadata, cleaning="adult")
    assert raw["country"].tolist() == [" United-States", " Canada"]
    assert cleaned["country"].tolist() == ["US", "Non-US"]
    assert cleaned["capital-gain"].tolist() == ["No gains", "Had gains"]
    assert cleaned["salary"].tolist() == ["<=50K", ">50K"]
    pd.testing.assert_frame_equal(pd.read_csv(csv_path), frame)


def test_source_positions_do_not_depend_on_nonunique_dataframe_index():
    frame, spec = classification_data()
    frame.index = [0] * len(frame)
    result = split_dataset(frame, spec, shot=20, seed=9)
    indices = result.metadata["source_row_positions"]
    assert len(set(indices["train"] + indices["test"] + indices["unused"])) == len(frame)


def test_regression_rejects_non_numeric_target(tmp_path):
    csv_path, metadata = tmp_path / "raw.csv", tmp_path / "meta.json"
    pd.DataFrame({"x": [1, 2], "target": ["a", "b"]}).to_csv(csv_path, index=False)
    metadata.write_text(json.dumps({"target_column": "target", "task_type": "regression"}))
    with pytest.raises(ValueError):
        load_dataset(csv_path, metadata)


def test_explicit_string_category_domains_preserve_leading_zeroes(tmp_path):
    csv_path, metadata = tmp_path / "raw.csv", tmp_path / "meta.json"
    csv_path.write_text("postal_code,label\n001,0\n002,1\n")
    metadata.write_text(json.dumps({"target_column": "label", "task_type": "classification",
                                    "categorical_columns": ["postal_code", "label"],
                                    "categories": {"label": [0, 1]}}))
    frame, spec = load_dataset(csv_path, metadata)
    assert frame["postal_code"].tolist() == ["001", "002"]
    assert frame["label"].tolist() == [0, 1]
    assert "postal_code" not in infer_training_schema(frame, spec).categories
    assert training_metadata(frame, spec)["observed_categories"]["postal_code"] == ["001", "002"]


def test_duplicate_csv_headers_fail_before_pandas_can_rename_a_copied_target(tmp_path):
    csv_path, metadata = tmp_path / "raw.csv", tmp_path / "meta.json"
    csv_path.write_text("x,label,label\n1,0,0\n2,1,1\n")
    metadata.write_text(json.dumps({"target_column": "label", "task_type": "classification"}))
    with pytest.raises(ValueError, match="unique"):
        load_dataset(csv_path, metadata)
