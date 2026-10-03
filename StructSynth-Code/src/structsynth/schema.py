"""Shared dataset contract, independent of models and evaluation."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


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
        if not self.columns or len(set(self.columns)) != len(self.columns):
            raise ValueError("Dataset columns must be nonempty and unique")
        if any(not isinstance(c, str) or not c for c in self.columns):
            raise ValueError("Column names must be nonempty strings")
        if self.target_column not in self.columns:
            raise ValueError("target_column must be a dataset column")
        if self.task_type not in {"classification", "regression"}:
            raise ValueError("task_type must be classification or regression")
        for name in ("categorical_columns", "integer_columns", "boolean_columns", "nullable_columns"):
            values = getattr(self, name)
            if len(set(values)) != len(values) or set(values) - set(self.columns):
                raise ValueError(f"Invalid {name}: {values}")
        if set(self.integer_columns) & (set(self.categorical_columns) | set(self.boolean_columns)):
            raise ValueError("Integer and categorical/boolean columns must be disjoint")
        if set(self.categories) - set(self.categorical_columns) - set(self.boolean_columns):
            raise ValueError("Category domains must refer to categorical or boolean columns")

    @property
    def numeric_columns(self) -> list[str]:
        excluded = set(self.categorical_columns) | set(self.boolean_columns)
        return [c for c in self.columns if c not in excluded]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

