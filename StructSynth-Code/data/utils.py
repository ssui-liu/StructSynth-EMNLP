# Imports
import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
import yaml
from dataclasses import dataclass
from typing import List, Optional


# Function to convert string to number using an encoder
def str2num(s, encoder):
    return encoder[s]


# Helper function to load a dataset from a standard path structure
def _load_raw_dataset_from_standard_path(dataset_name: str) -> pd.DataFrame:
    """
    Load a dataset from a standard CSV path structure.
    Checks for 'data/{dataset_name}/raw_data.csv' and '../data/{dataset_name}/raw_data.csv'.

    Args:
        dataset_name (str): The name of the dataset subdirectory.

    Returns:
        pd.DataFrame: The loaded dataframe.

    Raises:
        FileNotFoundError: If the CSV file cannot be found in the standard paths.
    """
    # Define possible paths for the raw data file
    path1 = Path(f"data/{dataset_name}/raw_data.csv")
    path2 = Path(f"../data/{dataset_name}/raw_data.csv")

    # Check for file existence and load the data
    if path1.exists():
        return pd.read_csv(path1)
    elif path2.exists():
        return pd.read_csv(path2)
    else:
        # Raise an error if the file is not found
        raise FileNotFoundError(f"Raw data for dataset '{dataset_name}' not found at {path1} or {path2}")


# Function to load Adult dataset
def load_adult_dataset(prop=1, seed=42):
    """
    Load the Adult dataset and apply specific preprocessing.

    This function loads the raw data, performs cleaning operations such as handling
    missing values, and transforms categorical features into more meaningful text-based
    representations.

    Args:
        prop (float): Proportion of the dataset to sample (default: 1.0).
        seed (int): Random seed for reproducibility (default: 42).

    Returns:
        pd.DataFrame: The processed and sampled dataframe.
    """

    def process_dataset(df: pd.DataFrame) -> pd.DataFrame:
        """
        Process the dataframe by cleaning and transforming features.
        """
        # Replace placeholder for missing values with actual NaN
        df.replace(" ?", np.nan, inplace=True)
        # Drop rows with any missing values
        df.dropna(how="any", inplace=True)

        # Simplify 'country' into 'US' and 'Non-US'
        df["country"] = df["country"].apply(lambda x: "US" if x.strip() == "United-States" else "Non-US")

        # Convert capital gain/loss into binary textual features
        df["capital-gain"] = df["capital-gain"].astype(str).map(lambda x: "Had gains" if float(x) > 0 else "No gains")
        df["capital-loss"] = df["capital-loss"].astype(str).map(lambda x: "Had losses" if float(x) > 0 else "No losses")

        # Simplify 'marital-status' into 'Single' and 'Couple'
        df["marital-status"] = df["marital-status"].str.strip().replace({
            "Divorced": "Single", "Married-spouse-absent": "Single",
            "Never-married": "Single", "Separated": "Single", "Widowed": "Single",
            "Married-AF-spouse": "Couple", "Married-civ-spouse": "Couple"
        })

        # Strip whitespace from 'salary' column
        df["salary"] = df["salary"].apply(lambda x: x.strip())

        return df

    # Load and process the dataset
    df = _load_raw_dataset_from_standard_path("adult")
    df = process_dataset(df)

    # Sample the dataset if a proportion less than 1 is specified
    if prop < 1:
        df = df.sample(frac=prop, random_state=seed)

    return df


# Function to load Anxiety dataset
def load_anxiety_dataset(prop=1, seed=42):
    """
    Load the Anxiety dataset and preprocess it.

    This function renames the target column and categorizes the 'Anxiety Level'
    into three classes: 'Low', 'Medium', and 'High'.

    Args:
        prop (float): Proportion of the dataset to sample (default: 1.0).
        seed (int): Random seed for reproducibility (default: 42).

    Returns:
        pd.DataFrame: The processed and sampled dataframe.
    """
    # Load the raw dataset
    df = _load_raw_dataset_from_standard_path("anxiety")

    # Standardize the target column name
    if "Anxiety Level (1-10)" in df.columns:
        df = df.rename(columns={"Anxiety Level (1-10)": "Anxiety Level"})

    # Categorize 'Anxiety Level' into 'Low', 'Medium', 'High'
    df['Anxiety Level'] = df['Anxiety Level'].apply(lambda x: 'Low' if x <= 3 else 'Medium' if x <= 6 else 'High')

    # Sample the dataset if needed
    if prop < 1:
        df = df.sample(frac=prop, random_state=seed)

    return df


# Function to get data based on dataset name
def load_dataset(dataset: str, seed: int = 42, prop: float = 1.0) -> pd.DataFrame:
    """
    Retrieve and process data for a specified dataset.

    This function acts as a dispatcher, calling the appropriate loading function
    for specialized datasets or performing a generic load for simpler ones.

    Args:
        dataset (str): Name of the dataset to load.
        seed (int): Random seed for reproducibility.
        prop (float): Proportion of the dataset to sample.

    Returns:
        pd.DataFrame: The loaded and processed dataframe.
    """
    # List of supported datasets
    SUPPORTED_DATASETS = ["adult", "salary", "anxiety", "obesity_reg", "churn", "compas"]
    
    # Ensure the requested dataset is on the supported list
    if dataset not in SUPPORTED_DATASETS:
        raise ValueError(f"The dataset '{dataset}' is not supported. Supported datasets are: {SUPPORTED_DATASETS}")

    # For datasets with special processing, call their dedicated function
    if dataset == "adult":
        return load_adult_dataset(prop=prop, seed=seed)
    if dataset == "anxiety":
        return load_anxiety_dataset(prop=prop, seed=seed)

    # For other datasets, perform a generic load and sample
    df = _load_raw_dataset_from_standard_path(dataset)
    if prop < 1.0:
        df = df.sample(frac=prop, random_state=seed)
        
    return df


def split_dataset(df, test_size=0.2, few_shot_size=100, seed=42, save_path: [str | Path] = None, label_column=None):
    """
    Split the dataset into train, test, and further split train into few-shot and oracle sets.
    The few-shot split maintains class balance using stratified sampling.

    Args:
        df (pd.DataFrame): Input dataframe to split
        test_size (float): Proportion of data to use for test set (default: 0.2)
        few_shot_size (int): Number of samples to use for few-shot learning (default: 100)
        seed (int): Random seed for reproducibility (default: 42)
        save_path (str or Path): Path to save the split datasets (default: None)
        label_column (str): Name of the target column for stratification. If None, uses the last column.

    Returns:
        tuple: (df_few_shot, df_oracle, df_test) - The split dataframes
    """
    # Set random seed for reproducibility
    np.random.seed(seed)

    # Identify target column for stratification
    if label_column is None:
        label_column = df.columns[-1]

    regression_labels = ["Target_Severity_Score", 'salary (k)', 'Weight']
    # First split: train/test with stratification
    df_train, df_test = train_test_split(
        df,
        test_size=test_size,
        random_state=seed,
        shuffle=True,
        stratify=df[label_column] if label_column not in regression_labels else None,
    )

    # Second split: few-shot/oracle from training data with stratification
    df_oracle, df_few_shot = train_test_split(
        df_train,
        test_size=few_shot_size,
        random_state=seed,
        shuffle=True,
        stratify=df_train[label_column] if label_column not in regression_labels else None,
    )

    num_classes = df_train[label_column].nunique()
    num_classes_oracle = df_oracle[label_column].nunique()
    num_classes_few_shot = df_few_shot[label_column].nunique()
    num_classes_test = df_test[label_column].nunique()

    # Save splits if path is provided
    if save_path:
        # Create directory if it doesn't exist
        os.makedirs(save_path, exist_ok=True)

        # Save each split to CSV
        df_few_shot.to_csv(os.path.join(save_path, 'few_shot.csv'), index=False)
        df_oracle.to_csv(os.path.join(save_path, 'oracle.csv'), index=False)
        df_test.to_csv(os.path.join(save_path, 'test.csv'), index=False)

        # Save split info
        split_info = {
            'total_samples': len(df),
            'test_size': test_size,
            'few_shot_size': few_shot_size,
            'few_shot_samples': len(df_few_shot),
            'oracle_samples': len(df_oracle),
            'test_samples': len(df_test),
            'seed': seed,
            'target_column': label_column,
            'class_distribution': {
                'few_shot': df_few_shot[label_column].value_counts(normalize=True).to_dict(),
                'oracle': df_oracle[label_column].value_counts(normalize=True).to_dict(),
                'test': df_test[label_column].value_counts(normalize=True).to_dict()
            }
        }

        # Save split info as JSON
        import json
        with open(os.path.join(save_path, 'split_info.json'), 'w') as f:
            json.dump(split_info, f, indent=4)

    return df_few_shot, df_oracle, df_test


def load_splits(split_path):
    """
    Load previously saved dataset splits.

    Args:
        split_path (str): Path where the split datasets are saved

    Returns:
        tuple: (df_few_shot, df_oracle, df_test) - The loaded split dataframes
    """
    df_few_shot = pd.read_csv(os.path.join(split_path, 'few_shot.csv'))
    df_oracle = pd.read_csv(os.path.join(split_path, 'oracle.csv'))
    df_test = pd.read_csv(os.path.join(split_path, 'test.csv'))

    return df_few_shot, df_oracle, df_test


def get_split_info(split_path):
    """
    Get information about the dataset splits.

    Args:
        split_path (str): Path where the split datasets are saved

    Returns:
        dict: Dictionary containing split information
    """
    with open(os.path.join(split_path, 'split_info.json'), 'r') as f:
        split_info = json.load(f)
    return split_info


@dataclass
class ClassifierConfig:
    max_depth: int
    learning_rate: float
    n_estimators: int
    seed: int

@dataclass
class DataConfig:
    base_dir: str
    dataset_name: str
    shots: List[int]
    seeds: List[int]
    target_column: str
    categorical_columns: Optional[List[str]]

@dataclass
class Config:
    data: DataConfig
    models: List[str]
    synthetic: dict
    classifier: ClassifierConfig

class DataLoader:
    @staticmethod
    def load_config(config_path: str) -> Config:
        """
        Load and parse the YAML configuration file.
        
        Args:
            config_path (str): Path to the YAML configuration file
            
        Returns:
            Config: Parsed configuration object with type hints
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid YAML
        """
        try:
            with open(config_path, 'r') as f:
                config_dict = yaml.safe_load(f)
            
            # Convert dictionary to dataclass objects
            classifier_config = ClassifierConfig(**config_dict['classifier'])
            data_config = DataConfig(**config_dict['data'])
            
            return Config(
                data=data_config,
                models=config_dict['models'],
                synthetic=config_dict['synthetic'],
                classifier=classifier_config
            )
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found at: {config_path}")
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file: {e}")