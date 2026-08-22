import pandas as pd
import numpy as np
from pathlib import Path
import json
import xgboost as xgb
from typing import Tuple, Dict, Any, Optional

from data_generation.utils.utils import DataPreprocessor
from data_generation.evaluation.metrics import EvaluationMetrics


def train_classifier(X_train: pd.DataFrame, y_train: pd.Series,
                     X_test: pd.DataFrame, y_test: pd.Series,
                     params: Optional[Dict[str, Any]] = None,
                     dataset_name: str = None) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """
    Train XGBoost model (classifier or regressor) and return predictions.

    Args:
        X_train: Training features
        y_train: Training labels
        X_test: Test features
        y_test: Test labels
        params: XGBoost parameters
        dataset_name: Name of dataset to determine if regression task

    Returns:
        Tuple of predictions and prediction probabilities (None for regression)
    """
    # Determine if this is a regression task
    is_regression = EvaluationMetrics.is_regression_task(dataset_name) if dataset_name else False

    if params is None:
        if is_regression:
            # Default regression parameters
            params = {
                'objective': 'reg:squarederror',
                'eval_metric': 'rmse',
                'max_depth': 6,
                'learning_rate': 0.1,
                'n_estimators': 100,
                'seed': 42
            }
        else:
            # Default classification parameters
            params = {
                'objective': 'binary:logistic',
                'eval_metric': 'logloss',
                'max_depth': 6,
                'learning_rate': 0.1,
                'n_estimators': 100,
                'seed': 42
            }

    if is_regression:
        # Use XGBRegressor for regression tasks
        model = xgb.XGBRegressor(**params)
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        return predictions, None  # No probabilities for regression
    else:
        # Use XGBClassifier for classification tasks
        model = xgb.XGBClassifier(**params)
        model.fit(X_train, y_train)
        return model.predict(X_test), model.predict_proba(X_test)


def get_data_paths(base_dir: str, dataset_name: str, shot: int, seed: int) -> Tuple[Path, Path]:
    """
    Get paths for few-shot and test data.

    Args:
        base_dir: Base directory for data
        dataset_name: Name of the dataset
        shot: Number of shots
        seed: Random seed

    Returns:
        Tuple of paths (few_shot_path, test_path)
    """
    base_dir = Path(base_dir)
    few_shot_path = base_dir / dataset_name / f"{shot}_shot" / f"seed_{seed}" / "train.csv"
    test_path = base_dir / dataset_name / f"{shot}_shot" / f"seed_{seed}" / "test.csv"

    if not few_shot_path.exists():
        raise FileNotFoundError(f"Few-shot data not found at {few_shot_path}")
    if not test_path.exists():
        raise FileNotFoundError(f"Test data not found at {test_path}")

    return few_shot_path, test_path


def process_synthetic_data(X_syn: Any, y_syn: Any, few_shot_df: pd.DataFrame,
                           test_df: pd.DataFrame, target_column: str,
                           categorical_cols: list, save_path: Optional[Path] = None,
                           dataset_name: str = None) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Process synthetic data and combine with original data for evaluation.

    Args:
        X_syn: Generated synthetic features
        y_syn: Generated synthetic labels
        few_shot_df: Original few-shot DataFrame
        test_df: Test DataFrame
        target_column: Name of target column
        categorical_cols: List of categorical column names
        save_path: Optional path to save synthetic data (now points to n{n_samples} directory)
        dataset_name: Name of dataset for regression task detection

    Returns:
        Tuple of (X_test, X_train, y_test, y_train) after preprocessing
    """
    # Process features and labels from few-shot data
    features = few_shot_df.drop(columns=[target_column])
    labels = few_shot_df[target_column]

    # Process synthetic features
    if isinstance(X_syn, pd.DataFrame):
        X_syn_df = X_syn.reset_index(drop=True)
    else:
        X_syn_df = pd.DataFrame(X_syn, columns=features.columns)

    # Process synthetic labels
    if isinstance(y_syn, pd.Series):
        y_syn_series = y_syn.rename(target_column).reset_index(drop=True)
    else:
        y_syn_series = pd.Series(y_syn, name=target_column)

    # Save synthetic data if path provided
    if save_path:
        # Save in n{n_samples} directory
        syn_df = pd.concat([X_syn_df, y_syn_series], axis=1)
        syn_df.to_csv(save_path / "synthetic_data.csv", index=False)

    # Check for duplicate columns in X_syn_df
    duplicate_cols_features = X_syn_df.columns[X_syn_df.columns.duplicated(keep=False)]
    if len(duplicate_cols_features) > 0:
        print(f"Warning: Found duplicate columns in synthetic features: {list(duplicate_cols_features)}")

        # For each set of duplicate columns, keep only the first occurrence and rename others
        for col in duplicate_cols_features:
            col_indices = [i for i, c in enumerate(X_syn_df.columns) if c == col]
            valid_col_idx = col_indices[0]  # Keep first occurrence

            new_cols = list(X_syn_df.columns)
            for i, idx in enumerate(col_indices):
                if idx != valid_col_idx:
                    new_cols[idx] = f"{col}_duplicate_{i}"

            X_syn_df.columns = new_cols

        # Drop duplicate columns
        duplicate_pattern_cols = [col for col in X_syn_df.columns if "_duplicate_" in col]
        if duplicate_pattern_cols:
            print(f"Dropping duplicate feature columns: {duplicate_pattern_cols}")
            X_syn_df = X_syn_df.drop(columns=duplicate_pattern_cols)

    # Ensure column order matches the original feature set
    X_syn_df = X_syn_df.reindex(columns=features.columns)

    # Verify that column sets match before concatenation
    missing_cols = set(features.columns) - set(X_syn_df.columns)
    extra_cols = set(X_syn_df.columns) - set(features.columns)

    if missing_cols:
        print(f"Warning: Synthetic data missing columns: {missing_cols}")
        # Add missing columns with default values
        for col in missing_cols:
            if col in categorical_cols:
                # Use most common value from original data
                most_common = features[col].value_counts().index[0]
                X_syn_df[col] = most_common
            else:
                # For numeric columns, use mean
                X_syn_df[col] = features[col].mean()

    if extra_cols:
        print(f"Warning: Dropping extra columns from synthetic data: {extra_cols}")
        X_syn_df = X_syn_df.drop(columns=extra_cols)

    # Combine original and synthetic data
    combined_features = pd.concat([features, X_syn_df], axis=0, ignore_index=True)
    combined_labels = pd.concat([labels, y_syn_series], axis=0, ignore_index=True)
    combined_df = pd.concat([combined_features, combined_labels], axis=1)

    # Check for unexpected duplicate columns in combined data
    if any(combined_df.columns.duplicated()):
        print("Warning: Duplicate columns found in combined data. Renaming duplicates.")
        combined_df.columns = pd.io.parsers.ParserBase({'names': combined_df.columns})._maybe_dedup_names(
            combined_df.columns)

    # Initialize and apply preprocessor
    preprocessor = DataPreprocessor(
        target_col=target_column,
        categorical_cols=categorical_cols,
        dataset_name=dataset_name  # Pass dataset_name for regression detection
    )

    # Preprocess combined data and test data together
    X_test, y_test, X_train, y_train = preprocessor.transform(test_df, combined_df)

    return X_test, X_train, y_test, y_train


def update_token_usage(usage: Dict[str, int],
                       seed_usage: Dict[str, int],
                       shot_usage: Dict[str, int],
                       total_usage: Dict[str, int]) -> None:
    """
    Update token usage statistics at all levels.

    Args:
        usage: Current generation token usage
        seed_usage: Token usage for current seed
        shot_usage: Token usage for current shot
        total_usage: Total token usage across all experiments
    """
    if usage:
        for key in usage:
            seed_usage[key] += usage[key]
            shot_usage[key] += usage[key]
            total_usage[key] += usage[key]


def save_token_usage_stats(results_dir: Path, total_usage: Dict[str, int],
                           dataset_name: str = None, shot: int = None,
                           structure_path: str = None, n_samples: int = None, seed: int = None) -> None:
    """
    Save token usage statistics and cost estimates.

    Args:
        results_dir: Base results directory
        total_usage: Total token usage statistics
        dataset_name: Optional dataset name for more structured saving
        shot: Optional shot count for more structured saving
        structure_path: Optional structure path name for more structured saving
        n_samples: Optional sample count for more structured saving
        seed: Optional seed value for more structured saving
    """
    # Determine the appropriate directory level to save token usage
    if dataset_name and shot and structure_path and seed:
        # Save at seed level
        token_usage_dir = results_dir / dataset_name / f"{shot}_shot" / structure_path / f"seed_{seed}"
    elif dataset_name and shot and structure_path:
        # Save at structure method level
        token_usage_dir = results_dir / dataset_name / f"{shot}_shot" / structure_path
    else:
        # Default: Save at base results level
        token_usage_dir = results_dir

    # Create token_usage file directly in the specified directory
    token_usage_file = token_usage_dir / "token_usage.json"
    with open(token_usage_file, 'w') as f:
        json.dump({
            'total_usage': total_usage,
            'cost_estimate_usd': {
                'prompt_cost': total_usage['prompt_tokens'] * 0.0015 / 1000,  # $0.0015 per 1K tokens
                'completion_cost': total_usage['completion_tokens'] * 0.002 / 1000,  # $0.002 per 1K tokens
                'total_cost': (total_usage['prompt_tokens'] * 0.0015 +
                               total_usage['completion_tokens'] * 0.002) / 1000
            }
        }, f, indent=2)


def print_token_usage(usage: Dict[str, int], level: str = "") -> None:
    """
    Print token usage statistics.

    Args:
        usage: Token usage statistics
        level: Description of the usage level (e.g., "seed", "shot")
    """
    prefix = f"\nToken usage for {level}:" if level else "\nToken usage:"
    print(prefix)
    print(f"- Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
    print(f"- Completion tokens: {usage.get('completion_tokens', 'N/A')}")
    print(f"- Total tokens: {usage.get('total_tokens', 'N/A')}")


def evaluate_and_save_results(X_syn: Any, y_syn: Any,
                              few_shot_df: pd.DataFrame, test_df: pd.DataFrame,
                              config: Any, dataset_name: str, model_name: str,
                              shot: int, seed: int, n_samples: int,
                              save_dir: Path, custom_path: str = None) -> None:
    """
    Process data, evaluate model performance, and save results.

    Args:
        X_syn: Generated synthetic features
        y_syn: Generated synthetic labels
        few_shot_df: Original few-shot DataFrame
        test_df: Test DataFrame
        config: Configuration object
        dataset_name: Name of the dataset
        model_name: Name of the model
        shot: Number of shots
        seed: Random seed
        n_samples: Number of samples
        save_dir: Directory to save results
        custom_path: Optional custom path for results directory (e.g., structure path)
    """
    # Process all data
    X_test, X_train, y_test, y_train = process_synthetic_data(
        X_syn=X_syn,
        y_syn=y_syn,
        few_shot_df=few_shot_df,
        test_df=test_df,
        target_column=config.data.target_column,
        categorical_cols=config.data.categorical_columns,
        save_path=save_dir,
        dataset_name=dataset_name  # Pass dataset_name for regression detection
    )

    # Train model and get predictions
    y_pred, y_pred_proba = train_classifier(
        X_train, y_train,
        X_test, y_test,
        dataset_name=dataset_name
    )

    # Calculate metrics (pass dataset_name for task type detection)
    metrics = EvaluationMetrics.calculate_metrics(
        y_test, y_pred, y_pred_proba,
        train_size=len(X_train),
        dataset_name=dataset_name
    )

    # Generate report
    EvaluationMetrics.generate_report(
        metrics,
        dataset_name=dataset_name,
        model_name=model_name,
        shot=shot,
        seed=seed,
        n_samples=n_samples,
        custom_path=custom_path,
        save_dir=save_dir
    )