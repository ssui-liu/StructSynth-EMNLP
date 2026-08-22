import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Add evaluation metrics import for regression detection
from data_generation.evaluation.metrics import EvaluationMetrics

class DataPreprocessor:
    """
    Preprocessor for both classification and regression data.
    Handles categorical encoding, duplicate detection, and target processing.
    """
    
    def __init__(self, target_col=None, categorical_cols=None, dataset_name=None):
        """
        Initialize DataPreprocessor.
        
        Args:
            target_col (str): Name of target column
            categorical_cols (list): List of categorical column names
            dataset_name (str): Name of dataset for regression task detection
        """
        self.target_col = target_col
        self.categorical_cols = categorical_cols or []
        self.dataset_name = dataset_name
        self.label_encoders = {}
        self.scaler = None
        
    def _is_regression_task(self):
        """
        Determine if this is a regression task based on dataset name.
        
        Returns:
            bool: True if regression task, False if classification
        """
        if self.dataset_name is None:
            return False
        return EvaluationMetrics.is_regression_task(self.dataset_name)
    
    def prepare_data(self, data):
        """
        Prepare data for structure discovery algorithms.
        Handles both numerical and categorical variables.
        """
        data_prepared = data.copy()
        
        # Handle categorical columns
        if self.categorical_cols:
            for col in self.categorical_cols:
                if col in data_prepared.columns:
                    if col not in self.label_encoders:
                        self.label_encoders[col] = LabelEncoder()
                    data_prepared[col] = self.label_encoders[col].fit_transform(data_prepared[col].astype(str))
        
        return data_prepared
    
    def remove_duplicates(self, df1, df2):
        """
        Remove duplicate columns between two dataframes.
        """
        # Find duplicate columns
        duplicate_cols = list(set(df1.columns) & set(df2.columns))
        if duplicate_cols:
            print(f"Found duplicate columns: {duplicate_cols}")
            # Remove duplicates from df2
            df2_cleaned = df2.drop(columns=duplicate_cols)
        else:
            df2_cleaned = df2
        
        return df1, df2_cleaned
    
    def transform(self, eval_data: pd.DataFrame, synth_data: pd.DataFrame) -> tuple:
        """
        Preprocess the evaluation and synthetic data.
        
        Args:
            eval_data: Evaluation data (test set)
            synth_data: Combined training and synthetic data
            
        Returns:
            Tuple of (eval_features, eval_labels, synth_features, synth_labels)
        """
        # Get all columns except target as features
        feature_columns = [col for col in eval_data.columns if col != self.target_col]
        
        # Make copies to avoid modifying original data
        eval_data = eval_data.copy()
        synth_data = synth_data.copy()
        
        # Determine if this is a regression task
        is_regression = self._is_regression_task()
        
        # Check for duplicate columns in synth_data
        duplicate_cols = synth_data.columns[synth_data.columns.duplicated(keep=False)]
        if len(duplicate_cols) > 0:
            print(f"Warning: Found duplicate columns in synthetic data: {list(duplicate_cols)}")
            
            # For each set of duplicate columns, keep only one
            for col in duplicate_cols:
                # Get all indices of this column
                col_indices = [i for i, c in enumerate(synth_data.columns) if c == col]
                
                # For columns that match target, check which has more non-NaN values
                if col == self.target_col:
                    nan_counts = [synth_data.iloc[:, idx].isna().sum() for idx in col_indices]
                    valid_col_idx = col_indices[nan_counts.index(min(nan_counts))]
                else:
                    # For feature columns, just keep the first occurrence
                    valid_col_idx = col_indices[0]
                
                # Create new column names, preserving the valid one
                new_cols = list(synth_data.columns)
                for i, idx in enumerate(col_indices):
                    if idx != valid_col_idx:
                        new_cols[idx] = f"{col}_duplicate_{i}"
                
                synth_data.columns = new_cols
                
            # Drop all duplicate columns
            duplicate_pattern_cols = [col for col in synth_data.columns if "_duplicate_" in col]
            if duplicate_pattern_cols:
                print(f"Dropping duplicate columns: {duplicate_pattern_cols}")
                synth_data = synth_data.drop(columns=duplicate_pattern_cols)
        
        # Get categorical columns if not specified
        if not self.categorical_cols:  # Check if list is empty instead of None
            categorical_columns = eval_data.select_dtypes(include=['object', 'category']).columns
            self.categorical_cols = [col for col in categorical_columns if col != self.target_col]
            
        # Track indices of dummy rows added to eval_data
        dummy_row_indices = []
        
        # Unify text values in categorical feature columns (excluding target for now)
        for col in self.categorical_cols:
            # Make sure columns exist in both dataframes
            if col not in eval_data.columns:
                print(f"Warning: Column '{col}' not found in evaluation data")
                continue
                
            if col not in synth_data.columns:
                print(f"Warning: Column '{col}' not found in synthetic data")
                continue
                
            # Now safely apply string operations to the Series
            eval_data[col] = eval_data[col].astype(str).str.strip().str.lower()
            synth_data[col] = synth_data[col].astype(str).str.strip().str.lower()
            
            # Handle unseen values in features
            valid_values = set(eval_data[col].unique())
            synth_data[col] = synth_data[col].apply(
                lambda x: x if x in valid_values else "others"
            )
            if "others" in synth_data[col].values and "others" not in valid_values:
                dummy_row = eval_data.iloc[0].copy()
                dummy_row[col] = "others"
                eval_data = pd.concat([eval_data, pd.DataFrame([dummy_row])], ignore_index=True)
                dummy_row_indices.append(len(eval_data) - 1)
        
        # Process target column based on task type
        if is_regression:
            # For regression: convert target to numeric, handle string representations of numbers
            eval_data[self.target_col] = pd.to_numeric(eval_data[self.target_col], errors='coerce')
            synth_data[self.target_col] = pd.to_numeric(synth_data[self.target_col], errors='coerce')
            
            # Handle any NaN values that might have been created
            if eval_data[self.target_col].isna().any():
                print(f"Warning: Found non-numeric values in regression target '{self.target_col}' for eval_data")
            if synth_data[self.target_col].isna().any():
                print(f"Warning: Found non-numeric values in regression target '{self.target_col}' for synth_data")
                # For synthetic data, we can drop rows with invalid targets
                synth_data = synth_data.dropna(subset=[self.target_col])
        else:
            # For classification: apply categorical preprocessing to target
            if self.target_col in eval_data.columns and self.target_col in synth_data.columns:
                eval_data[self.target_col] = eval_data[self.target_col].astype(str).str.strip().str.lower()
                synth_data[self.target_col] = synth_data[self.target_col].astype(str).str.strip().str.lower()
                    
        # Combine datasets for consistent processing
        combined_data = pd.concat([eval_data, synth_data], axis=0, ignore_index=True)
        
        # Process features
        if self.categorical_cols:
            # Get dummy variables for categorical features
            categorical_data = pd.get_dummies(combined_data[self.categorical_cols], drop_first=True)
            
            # Get numerical features (excluding categorical ones)
            numerical_feature_cols = [col for col in feature_columns if col not in self.categorical_cols]
            numerical_data = combined_data[numerical_feature_cols].select_dtypes(include=['int64', 'float64', 'int32', 'float32', 'bool'])
            
            # Combine numerical and dummy-encoded categorical features
            processed_features = pd.concat([numerical_data, categorical_data], axis=1)
        else:
            # If no categorical columns, just select numerical features
            processed_features = combined_data[feature_columns].select_dtypes(include=['int64', 'float64', 'int32', 'float32', 'bool'])
            
        # Process labels based on task type
        if is_regression:
            # For regression: keep numeric target values as-is
            processed_labels = combined_data[self.target_col].values.astype(float)
        else:
            # For classification: apply label encoding if categorical, otherwise keep as-is
            if combined_data[self.target_col].dtype in ['object', 'category']:
                if not hasattr(self, 'label_encoder'):
                    self.label_encoder = LabelEncoder()
                processed_labels = self.label_encoder.fit_transform(combined_data[self.target_col])
            else:
                processed_labels = combined_data[self.target_col].values
        
        # Create boolean mask for non-dummy rows in eval_data
        eval_mask = np.ones(len(eval_data), dtype=bool)
        eval_mask[dummy_row_indices] = False
        
        # Split back into evaluation and synthetic sets
        eval_features = processed_features[:len(eval_data)][eval_mask]
        eval_labels = processed_labels[:len(eval_data)][eval_mask]
        synth_features = processed_features[len(eval_data):]
        synth_labels = processed_labels[len(eval_data):]
        
        return eval_features, eval_labels, synth_features, synth_labels