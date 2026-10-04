"""Downstream preprocessing fitted exclusively on model-training rows."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder

from ..data.validation import _check_frame
from ..schema import DatasetSpec
from .common import _categorical, _numeric


class TrainingPreprocessor:
    """Median imputation and one-hot encoding learned only from model-fit rows.

    An all-missing training feature is retained with a fixed zero fill; unseen
    categorical test values receive an all-zero block. No test rows are added,
    removed, relabeled, or included in the fitted category vocabulary.
    """

    def __init__(self, spec: DatasetSpec):
        self.spec = spec
        self.numeric_columns = [column for column in spec.numeric_columns if column != spec.target_column]
        cats = set(spec.categorical_columns) | set(spec.boolean_columns)
        self.categorical_columns = [column for column in spec.columns if column in cats and column != spec.target_column]
        self.encoder = None
        self.medians = None

    def fit(self, train: pd.DataFrame) -> TrainingPreprocessor:
        _check_frame(train, self.spec)
        numeric = _numeric(train, self.numeric_columns, missing=True)
        self.medians = np.array([
            np.median(column[~np.isnan(column)]) if (~np.isnan(column)).any() else 0.0
            for column in numeric.T
        ])
        if self.categorical_columns:
            # sparse_output was introduced after sklearn 1.0; use the current
            # name when present while retaining the repository's older runtime.
            try:
                self.encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False, dtype=float)
            except TypeError:
                self.encoder = OneHotEncoder(handle_unknown="ignore", sparse=False, dtype=float)
            self.encoder.fit(_categorical(train, self.categorical_columns))
        return self

    def transform(self, frame: pd.DataFrame) -> np.ndarray:
        if self.medians is None:
            raise ValueError("TrainingPreprocessor must be fitted before transform")
        _check_frame(frame, self.spec)
        numeric = _numeric(frame, self.numeric_columns, missing=True)
        numeric = np.where(np.isnan(numeric), self.medians, numeric)
        categorical = self.encoder.transform(_categorical(frame, self.categorical_columns)) if self.encoder is not None else np.empty((len(frame), 0))
        result = np.concatenate([numeric, categorical], axis=1)
        if result.shape[1] == 0:
            raise ValueError("Downstream evaluation requires at least one feature")
        return result

    def fit_transform(self, train: pd.DataFrame) -> np.ndarray:
        return self.fit(train).transform(train)
