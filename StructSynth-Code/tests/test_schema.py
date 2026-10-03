import pytest

from structsynth.schema import DatasetSpec


def spec(**changes):
    values = {"name": "toy", "columns": ["x", "label"], "target_column": "label",
              "task_type": "classification", "categorical_columns": [], **changes}
    return DatasetSpec(**values)


def test_classification_target_is_categorical_even_when_integer_coded():
    dataset = spec()
    assert dataset.categorical_columns == ["label"]
    assert dataset.numeric_columns == ["x"]
    assert dataset.to_dict()["target_column"] == "label"


def test_boolean_target_retains_boolean_schema_without_duplicate_declaration():
    dataset = spec(boolean_columns=["label"], categories={"label": [True, False]})
    assert dataset.categorical_columns == []
    assert dataset.numeric_columns == ["x"]


@pytest.mark.parametrize("field,value", [
    ("columns", "x,label"), ("columns", ["x", []]), ("columns", ["x", "x"]),
    ("columns", []), ("categorical_columns", "x"), ("categorical_columns", [["x"]]),
    ("integer_columns", "x"), ("boolean_columns", None), ("nullable_columns", {"x": True}),
    ("target_column", ["label"]), ("task_type", ["classification"]),
    ("name", 12), ("task", {"predict": "label"}),
])
def test_schema_rejects_malformed_containers_before_treating_strings_as_columns(field, value):
    with pytest.raises(ValueError):
        spec(**{field: value})


@pytest.mark.parametrize("changes", [
    {"categorical_columns": ["absent"]}, {"integer_columns": ["x", "x"]},
    {"integer_columns": ["x"], "boolean_columns": ["x"]},
    {"task_type": "regression", "categorical_columns": ["label"]},
    {"task_type": "regression", "boolean_columns": ["label"]},
    {"categories": {"x": ["a", "b"]}},
])
def test_contradictory_field_and_task_declarations_fail_early(changes):
    with pytest.raises(ValueError):
        spec(**changes)


def test_regression_target_may_be_integer_without_becoming_categorical():
    dataset = spec(task_type="regression", integer_columns=["label"])
    assert dataset.numeric_columns == ["x", "label"]
    assert dataset.categorical_columns == []


@pytest.mark.parametrize("domain", [
    [], [None], ["a", 1], [False, 0], [{"bad": "object"}],
    [float("nan")], [float("inf")], [2 ** 63], [-2 ** 63 - 1],
])
def test_unusable_category_domains_fail_before_discovery(domain):
    with pytest.raises(ValueError):
        spec(categories={"label": domain})


def test_numeric_domains_allow_integer_float_equivalence_and_missing_marker():
    dataset = spec(categories={"label": [0, 1.0, None]}, nullable_columns=["label"])
    assert dataset.categories["label"] == [0, 1.0, None]


def test_boolean_domains_cannot_declare_string_or_integer_values():
    with pytest.raises(ValueError, match="Boolean category"):
        spec(boolean_columns=["x"], categories={"x": ["true", "false"]})
    with pytest.raises(ValueError, match="Boolean category"):
        spec(boolean_columns=["x"], categories={"x": [0, 1]})


@pytest.mark.parametrize("categories", [["label"], {1: ["a"]}])
def test_category_container_must_be_a_column_mapping(categories):
    with pytest.raises(ValueError):
        spec(categories=categories)


def test_legacy_text_descriptions_for_additional_fields_remain_readable():
    dataset = spec(descriptions={"x": "feature", "old_column": "legacy metadata"})
    assert dataset.descriptions["old_column"] == "legacy metadata"
