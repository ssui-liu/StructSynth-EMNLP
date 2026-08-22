import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
import json
import os # Added for os.path.join
from dython.nominal import associations # Added import for associations

class DataLoader:
    """
    Class for loading and processing datasets for causal discovery
    """
    def __init__(self, data_config: Dict[str, Any]): # Changed config to data_config for clarity
        """
        Initialize the data loader with data-specific configuration
        
        Args:
            data_config: Configuration dictionary with data paths and settings
        """
        # Determine the project root assuming this file (data_loader.py) is at <project_root>/src/data/data_loader.py
        # This ensures that paths to data files are resolved correctly from the project's base directory.
        current_file_path = os.path.abspath(__file__)
        # Navigate up three levels from data_loader.py's directory (src/data/) to reach the project root
        src_data_dir = os.path.dirname(current_file_path)  # Gets the directory of data_loader.py (e.g., .../project_root/src/data)
        src_dir = os.path.dirname(src_data_dir)            # Gets the parent directory (e.g., .../project_root/src)
        self.project_root = os.path.dirname(src_dir)       # Gets the parent directory (e.g., .../project_root)

        self.config = data_config # Store data_config
        self.dataset = None
        self.variables = None
        self.metadata = None
        # Construct absolute paths for dataset and metadata immediately using the determined project root
        self._dataset_path = self._construct_dataset_path()
        self._metadata_path = self._construct_metadata_path()
        self.variable_descriptions: Optional[Dict[str, Dict[str, Any]]] = None # Added attribute

    def _construct_dataset_path(self) -> str:
        """
        Constructs the full, absolute dataset path from config.
        It assumes self.config["data_base_dir"] is a path relative to the project root (e.g., "datasets").
        """
        # Create an absolute path for the base data directory by joining project_root with the configured relative path
        absolute_data_base_dir = os.path.join(self.project_root, self.config["data_base_dir"])
        
        # Join with other path components to form the full dataset path
        return os.path.join(
            absolute_data_base_dir,
            self.config["dataset_name"],
            f"{self.config['num_shots']}_shot",
            f"seed_{self.config['seed']}",
            self.config["train_file_name"]
        )

    def _construct_metadata_path(self) -> str:
        """
        Constructs the full, absolute metadata path from config.
        It assumes self.config["data_base_dir"] is a path relative to the project root.
        """
        # Create an absolute path for the base data directory by joining project_root with the configured relative path
        absolute_data_base_dir = os.path.join(self.project_root, self.config["data_base_dir"])
        
        # Join with other path components to form the full metadata path
        return os.path.join(
            absolute_data_base_dir,
            self.config["dataset_name"],
            self.config["metadata_file_name"]
        )

    @property
    def dataset_path(self) -> str:
        """Public property to get the dataset path."""
        return self._dataset_path

    @property
    def metadata_path(self) -> str:
        """Public property to get the metadata path."""
        return self._metadata_path
        
    def load_dataset(self) -> pd.DataFrame: # Removed path argument
        """
        Load the dataset from the path constructed from config.
            
        Returns:
            Loaded dataset as pandas DataFrame
        """
        # Load dataset from CSV file using the constructed path
        self.dataset = pd.read_csv(self._dataset_path)
        return self.dataset
    
    def load_metadata(self) -> Dict[str, Dict[str, Any]]: # Removed path argument
        """
        Load variable metadata from the path constructed from config.
            
        Returns:
            Dictionary mapping variable names to their metadata
        """
        # Load metadata from JSON file using the constructed path
        with open(self._metadata_path, 'r') as f:
            self.metadata = json.load(f)
        return self.metadata
    
    def get_variables(self) -> List[str]:
        """
        Get the list of variables in the dataset
        
        Returns:
            List of variable names
        """
        if self.dataset is not None:
            self.variables = list(self.dataset.columns)
        return self.variables

    def _build_variable_descriptions(self) -> Dict[str, Dict[str, Any]]:
        """
        Builds detailed descriptions for each variable in the dataset.
        The 'statistics' and 'frequent_values' fields are returned as formatted strings.
        This is an internal method.
            
        Returns:
            Dict[str, Dict[str, Any]]: A dictionary where keys are column names and 
                                       values are dictionaries containing descriptions and stats (as strings).
                                       Returns an error dictionary if data/metadata is not loaded or 
                                       'description' key is missing in metadata.
        """
        if self.dataset is None:
            return {"error": "Dataset not loaded. Please call load_dataset() first."}
        if self.metadata is None:
            return {"error": "Metadata not loaded. Please call load_metadata() first."}
        if "description" not in self.metadata:
            return {"error": "Input 'metadata' dictionary must contain a 'description' key."}

        df = self.dataset
        meta_data_descriptions = self.metadata["description"]
        
        numeric_stats_df = df.describe()
        variable_info_dict: Dict[str, Dict[str, Any]] = {}

        for col in df.columns:
            current_col_info: Dict[str, Any] = {}
            
            current_col_info["type"] = "categorical" if df[col].dtype in ['object', 'category'] else "numerical"
            current_col_info["description"] = meta_data_descriptions.get(col, "No description available.")
            
            if col in numeric_stats_df: # Check if column has numeric stats
                stats = numeric_stats_df[col]
                # Ensure all expected stats are present, especially for non-numeric or all-NaN columns
                mean_val = stats.get('mean', float('nan'))
                std_val = stats.get('std', float('nan'))
                min_val = stats.get('min', float('nan'))
                max_val = stats.get('max', float('nan'))
                count_val = stats.get('count', 0)

                stats_str = (
                    f"mean={mean_val:.2f}, std={std_val:.2f}, "
                    f"min={min_val:.2f}, max={max_val:.2f}, count={int(count_val)}"
                )
                current_col_info["statistics_str"] = stats_str
            
            if df[col].dtype in ['object', 'category']:
                # Drop NA values before calculating value_counts for categorical columns
                value_counts = df[col].dropna().value_counts().head(10)
                if not value_counts.empty:
                    frequent_values_lines = []
                    # Use len(df[col].dropna()) for percentage calculation if you want to exclude NaNs
                    # or len(df) if you want percentage of total including NaNs
                    total_non_na = len(df[col].dropna()) if len(df[col].dropna()) > 0 else 1 # Avoid division by zero
                    for val, count in value_counts.items():
                        percentage = (count / total_non_na) * 100 
                        frequent_values_lines.append(
                            f"  - '{str(val)}': {int(count)} occurrences ({percentage:.1f}% of non-NA)"
                        )
                    current_col_info["frequent_values_str"] = "Top most frequent values:\n" + "\n".join(frequent_values_lines)
                else:
                    current_col_info["frequent_values_str"] = "No frequent values found or column is effectively empty (all NA)."
            
            variable_info_dict[col] = current_col_info
        return variable_info_dict

    def get_variable_descriptions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed descriptions for each variable in the dataset.
        Loads dataset and metadata if not already loaded.
        Descriptions are generated once and cached.

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of variable descriptions.
        """
        if self.variable_descriptions is not None:
            return self.variable_descriptions

        if self.dataset is None:
            self.load_dataset()
        
        if self.metadata is None:
            self.load_metadata()

        self.variable_descriptions = self._build_variable_descriptions()
        return self.variable_descriptions 

    def get_correlation_matrix(self) -> Optional[pd.DataFrame]:
        """
        Calculates and returns the correlation matrix for the dataset.
        Uses Cramer's V for nominal-nominal, correlation ratio for nominal-numerical.
        The dataset is loaded if it hasn't been already.

        Returns:
            pd.DataFrame: The correlation matrix, or None if the dataset is not loaded.
        """
        if self.dataset is None:
            self.load_dataset() # Load dataset if not already loaded
        
        if self.dataset is None: # Check again if loading failed or dataset is empty
            print("Error: Dataset could not be loaded.")
            return None

        # Calculate associations
        # nominal_columns='auto' will automatically identify categorical columns
        # nom_nom_assoc='cramer' uses Cramér's V for nominal-nominal association
        # nom_num_assoc='correlation_ratio' uses correlation ratio for nominal-numerical association
        # plot=False ensures no plot is generated
        assoc_results = associations(
            self.dataset,
            nominal_columns='auto',
            nom_nom_assoc='cramer',
            nom_num_assoc='correlation_ratio',
            plot=False 
        )
        
        # The 'corr' key in the returned dictionary contains the correlation matrix
        return assoc_results['corr'] 