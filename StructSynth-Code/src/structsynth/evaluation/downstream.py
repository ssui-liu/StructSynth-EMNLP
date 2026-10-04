"""Downstream estimators, training protocols, and utility metrics."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, mean_squared_error, r2_score, roc_auc_score

from ..data.validation import _check_frame
from ..schema import DatasetSpec
from .common import _token
from .preprocessing import TrainingPreprocessor


PAPER_XGBOOST_PARAMS = {
    "booster": "gbtree", "n_estimators": 100, "learning_rate": 0.1, "max_depth": 6,
    "min_child_weight": 1, "gamma": 0, "subsample": 1, "colsample_bytree": 1,
    "reg_alpha": 0, "reg_lambda": 1,
}


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
