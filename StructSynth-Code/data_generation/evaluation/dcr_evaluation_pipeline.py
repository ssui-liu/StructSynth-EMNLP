# dcr_evaluation_pipeline.py

import pandas as pd
import numpy as np
from tqdm import tqdm


def calculate_prob_nn_in_train(synth_df, train_df, test_df, categorical_cols, numerical_cols):
    """
    Calculates the probability that a synthetic example's nearest neighbor is from the training set.

    Args:
        synth_df (pd.DataFrame): The synthetic data.
        train_df (pd.DataFrame): The training data.
        test_df (pd.DataFrame): The holdout/test data.
        categorical_cols (list): List of categorical column names.
        numerical_cols (list): List of numerical column names.

    Returns:
        float: The probability value.
    """
    # Combine train and test data, adding a label to identify origin
    train_df_labelled = train_df.copy()
    train_df_labelled['origin'] = 'train'
    test_df_labelled = test_df.copy()
    test_df_labelled['origin'] = 'test'
    
    real_df = pd.concat([train_df_labelled, test_df_labelled], ignore_index=True)
    
    # Separate features and origin label
    real_df_features = real_df.drop('origin', axis=1)
    real_df_origins = real_df['origin'].to_numpy()

    # Extract numerical and categorical data as numpy arrays for efficiency
    synth_numerical = synth_df[numerical_cols].to_numpy()
    real_numerical = real_df_features[numerical_cols].to_numpy()
    synth_categorical = synth_df[categorical_cols].to_numpy()
    real_categorical = real_df_features[categorical_cols].to_numpy()

    from_train_count = 0
    
    # Iterate through each record in the synthetic dataframe
    for i in tqdm(range(len(synth_df)), desc="Calculating Prob(NN in Train)"):
        synth_num_record = synth_numerical[i]
        synth_cat_record = synth_categorical[i]

        # Calculate L1 distance for numerical features
        numerical_distances = np.sum(np.abs(real_numerical - synth_num_record), axis=1)

        # Calculate distance for categorical features
        categorical_distances = np.sum(real_categorical != synth_cat_record, axis=1)
        
        # Total distance is the sum of numerical and categorical distances
        total_distances = numerical_distances + categorical_distances
        
        # Find the index of the nearest neighbor
        nn_index = np.argmin(total_distances)
        
        # Check if the nearest neighbor is from the train set
        if real_df_origins[nn_index] == 'train':
            from_train_count += 1
            
    return from_train_count / len(synth_df)


def evaluate_dcr(
    synth_data: pd.DataFrame,
    real_train_data: pd.DataFrame,
    real_test_data: pd.DataFrame,
    categorical_cols: list,
    numerical_cols: list,
    seed: int
) -> dict:
    """
    Evaluates the DCR (Distance to Closest Record).

    Args:
        synth_data (pd.DataFrame): The synthetic data.
        real_train_data (pd.DataFrame): The real training data.
        real_test_data (pd.DataFrame): The real test data.
        categorical_cols (list): List of categorical column names.
        numerical_cols (list): List of numerical column names.
        seed (int): The random seed for sampling.

    Returns:
        dict: A dictionary containing the DCR metric.
    """
    # --- Enforce Equal Sizes for Train and Holdout Sets ---
    n_train = len(real_train_data)
    n_test = len(real_test_data)
    
    if n_train > n_test:
        real_train_data = real_train_data.sample(n=n_test, random_state=seed)
    elif n_test > n_train:
        real_test_data = real_test_data.sample(n=n_train, random_state=seed)

    # --- Privacy Evaluation ---
    prob_value = calculate_prob_nn_in_train(
        synth_data, real_train_data, real_test_data, categorical_cols, numerical_cols
    )
    
    return {"dcr": prob_value} 