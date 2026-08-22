# pairwise_correlation_evaluation.py

import pandas as pd
import numpy as np
from itertools import combinations
from typing import List, Dict


def calculate_pairwise_correlation(
    real_data: pd.DataFrame,
    synthetic_data: pd.DataFrame,
    numerical_cols: List[str],
    categorical_cols: List[str]
) -> Dict[str, float]:
    """
    Calculates the pairwise column correlation difference between real and synthetic data
    based on the description in Appendix E.3.2 of TabSyn (arXiv:2310.09656v3).

    The function handles three cases for column pairs:
    1. Numerical-Numerical: Computes the absolute difference of Pearson correlation coefficients.
    2. Categorical-Categorical: Computes the contingency similarity score.
    3. Numerical-Categorical: Bins the numerical column and then computes the contingency similarity score.

    Args:
        real_data (pd.DataFrame): DataFrame containing the real data.
        synthetic_data (pd.DataFrame): DataFrame containing the synthetic data.
        numerical_cols (List[str]): List of column names for numerical columns.
        categorical_cols (List[str]): List of column names for categorical columns.

    Returns:
        Dict[str, float]: A dictionary where keys are column pair names and values are the calculated correlation difference scores.
    """
    correlation_diffs = {}
    all_cols = numerical_cols + categorical_cols

    # Ensure all columns exist in both DataFrames
    for col in all_cols:
        if col not in real_data.columns or col not in synthetic_data.columns:
            raise ValueError(f"Column '{col}' must exist in both real and synthetic datasets.")

    # Iterate over all unique column pairs
    for col1, col2 in combinations(all_cols, 2):
        pair_key = f"{col1}-{col2}"

        # Case 1: Both columns are numerical
        if col1 in numerical_cols and col2 in numerical_cols:
            # Calculate Pearson correlation
            pearson_real = real_data[[col1, col2]].corr().iloc[0, 1]
            pearson_synth = synthetic_data[[col1, col2]].corr().iloc[0, 1]

            # Performance metric: absolute difference of correlation coefficients
            correlation_diffs[pair_key] = np.abs(pearson_real - pearson_synth)

        # Case 2: Both columns are categorical
        elif col1 in categorical_cols and col2 in categorical_cols:
            # Calculate joint frequencies for real and synthetic data
            real_contingency = pd.crosstab(real_data[col1], real_data[col2], normalize=True)
            synth_contingency = pd.crosstab(synthetic_data[col1], synthetic_data[col2], normalize=True)

            # Align index and columns to handle categories present in one dataset but not the other
            all_rows = real_contingency.index.union(synth_contingency.index)
            all_cols_contingency = real_contingency.columns.union(synth_contingency.columns)

            real_contingency = real_contingency.reindex(index=all_rows, columns=all_cols_contingency, fill_value=0)
            synth_contingency = synth_contingency.reindex(index=all_rows, columns=all_cols_contingency, fill_value=0)

            # Calculate contingency similarity score (Total Variation Distance of joint frequencies)
            score = 0.5 * np.abs(real_contingency - synth_contingency).to_numpy().sum()
            correlation_diffs[pair_key] = score

        # Case 3: One numerical and one categorical column
        else:
            # Identify which column is numerical and which is categorical
            if col1 in numerical_cols:
                num_col, cat_col = col1, col2
            else:
                num_col, cat_col = col2, col1

            # Bin the numerical column to convert it to categorical
            # We use qcut (quantile-based discretization) as a reasonable default.
            # Operate on copies to avoid side effects.
            real_temp = real_data.copy()
            synth_temp = synthetic_data.copy()

            # Use 10 quantiles for binning
            try:
                real_temp[num_col] = pd.qcut(real_temp[num_col], q=10, duplicates='drop').astype(str)
                synth_temp[num_col] = pd.qcut(synth_temp[num_col], q=10, duplicates='drop').astype(str)
            except ValueError:  # If too few unique values to bin, convert to string directly
                real_temp[num_col] = real_temp[num_col].astype(str)
                synth_temp[num_col] = synth_temp[num_col].astype(str)

            # Now both are categorical, apply the same logic as in Case 2
            real_contingency = pd.crosstab(real_temp[num_col], real_temp[cat_col], normalize=True)
            synth_contingency = pd.crosstab(synth_temp[num_col], synth_temp[cat_col], normalize=True)

            all_rows = real_contingency.index.union(synth_contingency.index)
            all_cols_contingency = real_contingency.columns.union(synth_contingency.columns)

            real_contingency = real_contingency.reindex(index=all_rows, columns=all_cols_contingency, fill_value=0)
            synth_contingency = synth_contingency.reindex(index=all_rows, columns=all_cols_contingency, fill_value=0)

            score = 0.5 * np.abs(real_contingency - synth_contingency).to_numpy().sum()
            correlation_diffs[pair_key] = score

    return correlation_diffs


def evaluate_pairwise_correlation(
    real_test_data: pd.DataFrame,
    synth_data: pd.DataFrame,
    numerical_cols: list,
    categorical_cols: list
) -> dict:
    """
    Evaluates the pairwise correlation difference between real and synthetic data.

    Args:
        real_test_data (pd.DataFrame): The real test data.
        synth_data (pd.DataFrame): The synthetic data.
        numerical_cols (list): List of numerical column names.
        categorical_cols (list): List of categorical column names.

    Returns:
        dict: A dictionary containing the pairwise correlation difference metric.
    """
    # Ensure synth_data has the same columns as real_test_data
    synth_data = synth_data[real_test_data.columns]

    correlation_results = calculate_pairwise_correlation(
        real_test_data, synth_data, numerical_cols, categorical_cols
    )
    
    # We take the mean of all pairwise differences for a summary statistic.
    pairwise_correlation_diff = np.mean(list(correlation_results.values())) if correlation_results else 0.0

    return {"pairwise_correlation_diff": pairwise_correlation_diff} 