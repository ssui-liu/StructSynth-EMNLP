from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, f1_score,
    precision_score, recall_score, roc_auc_score,
    mean_absolute_error, mean_squared_error, r2_score
)
import pandas as pd
import numpy as np


def is_regression_task(dataset_name: str, dataset_info: dict) -> bool:
    """Determine if the dataset is a regression task based on dataset info."""
    return dataset_info.get(dataset_name, {}).get('task_type') == 'regression'


def calculate_metrics(y_true, y_pred, y_pred_proba_or_none, is_regression: bool) -> dict:
    """
    Calculate metrics for both classification and regression tasks.

    Args:
        y_true: True labels.
        y_pred: Predicted labels.
        y_pred_proba_or_none: Predicted probabilities (for classification).
        is_regression (bool): Flag indicating if it's a regression task.

    Returns:
        dict: A dictionary of calculated metrics.
    """
    if is_regression:
        # Calculate regression metrics
        metrics = {
            'mae': mean_absolute_error(y_true, y_pred),
            'mse': mean_squared_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'r2': r2_score(y_true, y_pred),
        }
    else:
        # Calculate classification metrics
        n_classes = len(np.unique(y_true))
        average = 'binary' if n_classes == 2 else 'micro'

        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'f1': f1_score(y_true, y_pred, average=average),
            'precision': precision_score(y_true, y_pred, average=average, zero_division=0),
            'recall': recall_score(y_true, y_pred, average=average, zero_division=0),
        }

        # Handle ROC AUC calculation
        if y_pred_proba_or_none is not None:
            if n_classes == 2:
                if y_pred_proba_or_none.shape[1] == 2:
                    metrics['auc_roc'] = roc_auc_score(y_true, y_pred_proba_or_none[:, 1])
            else:
                metrics['auc_roc'] = roc_auc_score(y_true, y_pred_proba_or_none, multi_class='ovr')

    return metrics


def calculate_downstream_performance(
    synth_df: pd.DataFrame,
    test_df: pd.DataFrame,
    dataset_name: str,
    dataset_info: dict,
    numerical_cols: list,
    categorical_cols: list
) -> dict:
    """
    Trains a model on synthetic data and evaluates its performance on real test data.

    Args:
        synth_df (pd.DataFrame): The synthetic data for training.
        test_df (pd.DataFrame): The real test data for evaluation.
        dataset_name (str): The name of the dataset.
        dataset_info (dict): Information about the dataset, including task type and target column.
        numerical_cols (list): List of numerical column names.
        categorical_cols (list): List of categorical column names.

    Returns:
        dict: A dictionary of performance metrics.
    """
    target_col = dataset_info.get(dataset_name, {}).get('target_column')
    if not target_col:
        raise ValueError(f"Target column for dataset '{dataset_name}' not specified in dataset_info.")

    if target_col not in synth_df.columns or target_col not in test_df.columns:
        raise ValueError(f"Target column '{target_col}' not found in the dataframes.")

    X_train = synth_df.drop(columns=[target_col])
    y_train = synth_df[target_col]
    X_test = test_df.drop(columns=[target_col])
    y_test = test_df[target_col]

    regression_task = is_regression_task(dataset_name, dataset_info)

    # Define model based on task type
    if regression_task:
        model = LinearRegression()
    else:
        model = LogisticRegression(random_state=42, max_iter=1000)

    # Create a preprocessor for numerical and categorical features
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', 'passthrough', [col for col in numerical_cols if col != target_col]),
            ('cat', OneHotEncoder(handle_unknown='ignore'), [col for col in categorical_cols if col != target_col])
        ],
        remainder='passthrough'
    )

    # Create the full pipeline
    pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                               ('classifier', model)])

    # Train the model
    pipeline.fit(X_train, y_train)

    # Make predictions
    y_pred = pipeline.predict(X_test)
    y_pred_proba = None
    if not regression_task:
        try:
            y_pred_proba = pipeline.predict_proba(X_test)
        except AttributeError:
            pass  # Some classifiers might not have predict_proba

    # Calculate and return metrics
    return calculate_metrics(y_test, y_pred, y_pred_proba, regression_task) 