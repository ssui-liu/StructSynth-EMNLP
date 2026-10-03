"""Paper-aligned downstream utility, nearest-record privacy, and fidelity.

All evaluators state their protocol in their result. Undefined primary metrics
are returned as ``None`` with a reason, never converted into a successful score.
"""
from __future__ import annotations

import json
from itertools import combinations
from numbers import Integral, Real
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, mean_squared_error, r2_score, roc_auc_score
from sklearn.preprocessing import OneHotEncoder

from .data import _check_frame
from .schema import DatasetSpec


PAPER_XGBOOST_PARAMS = {
    "booster": "gbtree", "n_estimators": 100, "learning_rate": 0.1, "max_depth": 6,
    "min_child_weight": 1, "gamma": 0, "subsample": 1, "colsample_bytree": 1,
    "reg_alpha": 0, "reg_lambda": 1,
}


def _token(value: Any) -> str:
    """Collision-free categorical representation, including an explicit NA atom."""
    if pd.isna(value):
        atom = ["missing"]
    elif isinstance(value, (bool, np.bool_)):
        atom = ["boolean", bool(value)]
    elif isinstance(value, Integral):
        # Converting a categorical identifier through float would collapse
        # distinct integers above 2**53 into the same class.
        atom = ["number", int(value)]
    elif isinstance(value, Real):
        # Pandas concatenation can promote integer category values to floats.
        number = float(value)
        atom = ["number", int(number) if np.isfinite(number) and number.is_integer() else str(number)]
    else:
        atom = ["string", str(value)]
    return json.dumps(atom, ensure_ascii=False, separators=(",", ":"))


def _categorical(frame: pd.DataFrame, columns: list[str]) -> np.ndarray:
    if not columns:
        return np.empty((len(frame), 0), dtype=object)
    return np.column_stack([frame[column].map(_token).to_numpy() for column in columns])


def _numeric(frame: pd.DataFrame, columns: list[str], *, missing: bool = False) -> np.ndarray:
    if not columns:
        return np.empty((len(frame), 0), dtype=float)
    values = np.column_stack([pd.to_numeric(frame[column], errors="raise").to_numpy(dtype=float) for column in columns])
    if np.isinf(values).any() or (not missing and np.isnan(values).any()):
        raise ValueError("Numerical evaluation values must be finite; missing numeric values are not defined by this metric")
    return values


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


def _make_estimator(task_type: str, model: str, seed: int, n_classes: int, params: dict | None):
    params = dict(params or {})
    if model == "xgboost":
        try:
            from xgboost import XGBClassifier, XGBRegressor
        except ImportError as exc:
            raise ImportError("XGBoost is required for the paper evaluator; install the project's evaluation extra or explicitly choose another model") from exc
        settings = {**PAPER_XGBOOST_PARAMS, "random_state": seed, "n_jobs": 1, **params}
        if task_type == "regression":
            settings.setdefault("objective", "reg:squarederror")
            return XGBRegressor(**settings)
        settings.setdefault("objective", "binary:logistic" if n_classes == 2 else "multi:softprob")
        settings.setdefault("eval_metric", "logloss" if n_classes == 2 else "mlogloss")
        return XGBClassifier(**settings)
    if model == "random_forest":
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        cls = RandomForestRegressor if task_type == "regression" else RandomForestClassifier
        return cls(**{"n_estimators": 200, "n_jobs": 1, "random_state": seed, **params})
    if model == "logistic" and task_type == "classification":
        from sklearn.linear_model import LogisticRegression
        return LogisticRegression(**{"max_iter": 1000, "solver": "lbfgs", "random_state": seed, **params})
    if model == "ridge" and task_type == "regression":
        from sklearn.linear_model import Ridge
        # Dense SVD implements the same objective without depending on the
        # removed scipy.linalg.solve(sym_pos=...) used by older sklearn versions.
        return Ridge(**{"alpha": 1.0, "solver": "svd", **params})
    if model == "mlp":
        from sklearn.neural_network import MLPClassifier, MLPRegressor
        cls = MLPRegressor if task_type == "regression" else MLPClassifier
        return cls(**{"hidden_layer_sizes": (100,), "max_iter": 500, "random_state": seed, **params})
    raise ValueError(f"Unsupported {model!r} model for {task_type}")


def evaluate_downstream(
    real_train: pd.DataFrame,
    synthetic: pd.DataFrame,
    test: pd.DataFrame,
    spec: DatasetSpec,
    *,
    protocol: str = "augmentation",
    seed: int = 42,
    estimator: Any = None,
    model: str = "xgboost",
    model_params: dict | None = None,
) -> dict[str, Any]:
    """Fit augmentation by default; report AUC (macro OVR) or R² on real test.

    ``synthetic_only`` and ``real_only`` are explicit comparison protocols. A
    caller-supplied estimator is fitted in place and identified in the result.
    """
    if protocol not in {"augmentation", "synthetic_only", "real_only"}:
        raise ValueError(f"Unknown downstream protocol: {protocol}")
    _check_frame(real_train, spec)
    _check_frame(test, spec)
    if protocol != "real_only":
        _check_frame(synthetic, spec)
    if protocol == "augmentation":
        train = pd.concat([real_train[spec.columns], synthetic[spec.columns]], ignore_index=True)
    elif protocol == "synthetic_only":
        train = synthetic[spec.columns].copy()
    else:
        train = real_train[spec.columns].copy()
    prep = TrainingPreprocessor(spec)
    x_train = prep.fit_transform(train)
    x_test = prep.transform(test)
    issues = []
    classes = []
    if spec.task_type == "regression":
        y_train = pd.to_numeric(train[spec.target_column], errors="raise").to_numpy(dtype=float)
        y_test = pd.to_numeric(test[spec.target_column], errors="raise").to_numpy(dtype=float)
    else:
        train_labels = train[spec.target_column].map(_token)
        classes = sorted(train_labels.unique())
        if len(classes) < 2:
            raise ValueError("Classification fitting requires at least two training classes")
        mapping = {label: i for i, label in enumerate(classes)}
        y_train = train_labels.map(mapping).to_numpy(dtype=int)
        y_test = test[spec.target_column].map(_token).map(mapping).fillna(-1).to_numpy(dtype=int)
        if (y_test == -1).any():
            issues.append("Test labels include classes absent from model-fit data; AUC is undefined")
    supplied = estimator is not None
    if estimator is None:
        estimator = _make_estimator(spec.task_type, model, seed, len(classes), model_params)
    estimator.fit(x_train, y_train)
    predicted = estimator.predict(x_test)
    result = {
        "protocol": protocol, "model": estimator.__class__.__name__ if supplied else model,
        "seed": int(seed), "task_type": spec.task_type, "train_rows": len(train), "test_rows": len(test),
        "real_train_rows_used": len(real_train) if protocol != "synthetic_only" else 0,
        "synthetic_rows_used": len(synthetic) if protocol != "real_only" else 0,
        "preprocessing_fit": "model_training_rows_only", "encoded_feature_count": int(x_train.shape[1]),
    }
    if spec.task_type == "regression":
        score = float(r2_score(y_test, predicted)) if len(test) > 1 and np.var(y_test) > 0 else None
        if score is None:
            issues.append("R² is undefined for fewer than two test rows or a constant test target")
        result.update({"primary_metric": "r2", "r2": score, "mae": float(mean_absolute_error(y_test, predicted)),
                       "rmse": float(np.sqrt(mean_squared_error(y_test, predicted)))})
    else:
        auc = None
        if not issues and len(np.unique(y_test)) == len(classes) and hasattr(estimator, "predict_proba"):
            probabilities = np.asarray(estimator.predict_proba(x_test))
            model_classes = np.asarray(estimator.classes_, dtype=int)
            if set(model_classes.tolist()) != set(range(len(classes))):
                raise ValueError("Estimator probability classes do not match fitted target vocabulary")
            probabilities = probabilities[:, [int(np.flatnonzero(model_classes == i)[0]) for i in range(len(classes))]]
            if len(classes) == 2:
                auc = float(roc_auc_score(y_test, probabilities[:, 1]))
            else:
                auc = float(roc_auc_score(y_test, probabilities, multi_class="ovr", average="macro", labels=np.arange(len(classes))))
        elif not issues:
            issues.append("AUC requires probabilities and every fitted class to appear in the test set")
        result.update({"primary_metric": "auc_roc", "auc_roc": auc, "auc_average": "binary" if len(classes) == 2 else "macro_ovr",
                       "accuracy": float(accuracy_score(y_test, predicted)),
                       "f1_macro": float(f1_score(y_test, predicted, average="macro", zero_division=0)),
                       "class_tokens": classes})
    result["metric_issues"] = issues
    return result


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
