"""Shared dataset contract, independent of models and evaluation."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
import math


def _names(values, name, *, nonempty=False):
    if not isinstance(values, list) or (nonempty and not values):
        raise ValueError(f"{name} must be {'a nonempty' if nonempty else 'a'} list of column names")
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError(f"{name} must contain nonempty string column names")
    if len(set(values)) != len(values):
        raise ValueError(f"{name} must contain unique column names")


@dataclass
class DatasetSpec:
    name: str
    columns: list[str]
    target_column: str
    task_type: str
    categorical_columns: list[str]
    descriptions: dict[str, str] = field(default_factory=dict)
    task: str = ""
    integer_columns: list[str] = field(default_factory=list)
    boolean_columns: list[str] = field(default_factory=list)
    nullable_columns: list[str] = field(default_factory=list)
    categories: dict[str, list[Any]] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Dataset name must be a nonempty string")
        _names(self.columns, "Dataset columns", nonempty=True)
        if not isinstance(self.target_column, str) or self.target_column not in self.columns:
            raise ValueError("target_column must be a dataset column")
        if not isinstance(self.task_type, str) or self.task_type not in {"classification", "regression"}:
            raise ValueError("task_type must be classification or regression")
        if not isinstance(self.task, str):
            raise ValueError("Dataset task description must be text")
        for name in ("categorical_columns", "integer_columns", "boolean_columns", "nullable_columns"):
            values = getattr(self, name)
            _names(values, name)
            if set(values) - set(self.columns):
                raise ValueError(f"Invalid {name}: {values}")
        if self.task_type == "classification" and self.target_column not in self.categorical_columns + self.boolean_columns:
            self.categorical_columns = [*self.categorical_columns, self.target_column]
        if set(self.integer_columns) & (set(self.categorical_columns) | set(self.boolean_columns)):
            raise ValueError("Integer and categorical/boolean columns must be disjoint")
        if not isinstance(self.categories, dict):
            raise ValueError("categories must map column names to explicit value lists")
        if any(not isinstance(column, str) for column in self.categories):
            raise ValueError("Category domain keys must be column names")
        if set(self.categories) - set(self.categorical_columns) - set(self.boolean_columns):
            raise ValueError("Category domains must refer to categorical or boolean columns")
        if self.task_type == "regression" and self.target_column not in self.numeric_columns:
            raise ValueError("Regression target must be numerical")
        if not isinstance(self.descriptions, dict) or any(not isinstance(k, str) or not isinstance(v, str)
                                                        for k, v in self.descriptions.items()):
            raise ValueError("descriptions must map column names to text")
        for column, domain in self.categories.items():
            if not isinstance(domain, list) or not domain:
                raise ValueError(f"Category domain for {column} must be a nonempty list")
            for value in domain:
                if value is not None and (type(value) not in (str, bool, int, float)
                                          or (type(value) is float and not math.isfinite(value))):
                    raise ValueError(f"Invalid JSON category in {column}")
                if type(value) is int and not -(2 ** 63) <= value < 2 ** 63:
                    raise ValueError(f"Integer category in {column} must fit a signed 64-bit integer")
            kinds = {
                "number" if type(value) in (int, float) else "boolean" if type(value) is bool else "string"
                for value in domain
                if value is not None
            }
            # The generator emits one scalar type per attribute. A mixed or
            # all-null domain cannot define that contract and must fail before
            # graph-induction requests, rather than at the later generator fit.
            if len(kinds) != 1:
                raise ValueError(f"Category domain for {column} needs one consistent non-null JSON type")
            if column in self.boolean_columns and kinds != {"boolean"}:
                raise ValueError(f"Boolean category domain for {column} must contain boolean values")

    @property
    def numeric_columns(self) -> list[str]:
        excluded = set(self.categorical_columns) | set(self.boolean_columns)
        return [c for c in self.columns if c not in excluded]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
