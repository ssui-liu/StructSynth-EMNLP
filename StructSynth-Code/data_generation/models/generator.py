import pandas as pd
from typing import Dict, Tuple, Optional, Union
import numpy as np
from data_generation.models.structure_llm.structure_llm import HierarchicalStructureLLM
import os
from pathlib import Path


def get_dataset_info(
    df: pd.DataFrame,
    meta_data: Dict,
    n_row_samples_per_class: int
) -> Tuple[pd.DataFrame, str, Dict[str, str]]:
    """
    Prepare dataset information with examples split by class from existing DataFrame.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        meta_data (Dict): Metadata dictionary containing task and column descriptions
        n_row_samples_per_class (int): Target number of examples to show per class
        
    Returns:
        Tuple[pd.DataFrame, str, Dict[str, str]]: Returns (example_df, task_str, enhanced_col_descriptions_dict)
    """
    # Get basic statistics for numerical columns
    numeric_stats = df.describe()
    
    # Determine label column based on dataset
    label_column = meta_data["label_column"]
    
    # Generate example DataFrame with samples from each class
    example_dfs = []
    for class_label in df[label_column].unique():
        class_df = df[df[label_column] == class_label]
        # Handle case where we have fewer samples than requested
        actual_samples = min(n_row_samples_per_class, len(class_df))
        if actual_samples < n_row_samples_per_class:
            # Use all available samples if we have fewer than requested
            class_sample = class_df
        else:
            # Randomly sample n rows from this class
            class_sample = class_df.sample(n=actual_samples)
        example_dfs.append(class_sample)
    
    example_df = pd.concat(example_dfs, axis=0).reset_index(drop=True)
    
    task_str = meta_data["task"]
    
    # Get original column descriptions from meta_data
    original_descriptions = meta_data["description"]
    enhanced_descriptions_dict = {}

    for col, base_desc_text in original_descriptions.items():
        # Start with the base description for the column
        # Use a list to gather all parts of the description for this column
        description_parts = [base_desc_text]

        # Add numerical statistics if available
        if col in numeric_stats:
            stats = numeric_stats[col]
            # Append statistics to the parts list
            description_parts.append(f"  - Statistics (from available data): mean={stats['mean']:.2f}, std={stats['std']:.2f}")
        
        # Add categorical value frequencies if the column is categorical or object type
        if df[col].dtype in ['object', 'category']:
            value_counts = df[col].value_counts().head(10)
            if not value_counts.empty:
                # Prepare lines for categorical information
                categorical_info_lines = ["  - Top most frequent values (from available data):"]
                for val, count in value_counts.items():
                    percentage = (count / len(df)) * 100
                    categorical_info_lines.append(f"    - {val}: {count} ({percentage:.1f}%)")
                # Add the joined categorical info as a single part
                description_parts.append("\n".join(categorical_info_lines))
        
        # Join all parts with newline characters to form the complete description for this column
        enhanced_descriptions_dict[col] = "\n".join(description_parts)
    
    return example_df, task_str, enhanced_descriptions_dict

class HierarchicalSyntheticDataGenerator:
    """
    A class for generating synthetic data using HierarchicalStructureLLM.
    This class provides an interface for training and generating synthetic data
    while maintaining hierarchical structure relationships defined in the structure graph file.
    """
    
    def __init__(
        self,
        few_shot_df: pd.DataFrame,
        meta_data: Dict,
        graph_file: str,
        n_row_samples_per_class: int = 10,
        model: str = "gpt-4o-mini",
        temperature: float = 0.9,
        max_tokens: int = 2000,
        api_key: Optional[str] = None,
        dataset: str = "default",
    ):
        """
        Initialize the HierarchicalStructureLLM-based synthetic data generator.
        
        Args:
            few_shot_df: DataFrame with examples for few-shot learning
            meta_data: Metadata dictionary containing task and column descriptions
            graph_file: Path to the structure graph JSON file for hierarchical structure
            n_row_samples_per_class: Number of example rows per class to use
            model: OpenAI model name (default: 'gpt-4o-mini')
            temperature: Sampling temperature (default: 0.9)
            max_tokens: Maximum tokens for generation (default: 2000)
            api_key: OpenAI API key (default: None, will use predefined key)
            dataset: Name of dataset for template selection (default: "default")
        """
        # Store parameters
        self.graph_file = graph_file
        self.n_row_samples_per_class = n_row_samples_per_class
        self.col_description = meta_data["description"]
        self.target_col = meta_data["label_column"]
        
        # Store model parameters
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key
        self.dataset = dataset

        self.example_df, self.task_str, self.col_description = get_dataset_info(
            few_shot_df,
            meta_data,
            self.n_row_samples_per_class
        )
        
    def fit(self):
        """
        Fit the HierarchicalStructureLLM model on the training data.
        The structure is automatically loaded from the graph file.
        """
        
        # Initialize HierarchicalStructureLLM model
        print("Initializing full HierarchicalStructureLLM...")
        self.generation_model = HierarchicalStructureLLM(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            api_key=self.api_key,
            dataset=self.dataset,
            target_col=self.target_col,
            graph_file=self.graph_file
        )
        
        # Fit the model - structure comes from the graph file
        self.generation_model.fit(self.example_df, self.task_str, self.col_description)

    def generate(self, n_samples: int, return_token_usage: bool = False):
        """
        Generate synthetic samples using the fitted HierarchicalStructureLLM model.
        
        Args:
            n_samples: Number of synthetic samples to generate
            return_token_usage: Whether to return OpenAI API token usage
            
        Returns:
            If return_token_usage is False:
                Tuple of (synthetic_features, synthetic_labels)
            If return_token_usage is True:
                Tuple of (synthetic_features, synthetic_labels, token_usage)
        """
        if not hasattr(self, 'cllm_model'):
            raise RuntimeError("Must call fit() before generating data")
            
        # HierarchicalStructureLLM uses 'generate_hierarchical'
        if return_token_usage:
            X_syn, y_syn, usage = self.generation_model.generate_hierarchical(
                n_samples, 
                self.task_str, 
                self.col_description, 
                return_token_usage=True
            )
            return X_syn, y_syn, usage
        else:
            X_syn, y_syn = self.generation_model.generate_hierarchical(
                n_samples, 
                self.task_str, 
                self.col_description, 
                return_token_usage=False
            )
            return X_syn, y_syn
    
    def get_generation_order(self):
        """
        Get the hierarchical generation order from the structure graph.
        
        Returns:
            List of variables in generation order
        """
        if not hasattr(self, 'cllm_model'):
            raise RuntimeError("Must call fit() before accessing generation order")
        return self.generation_model.get_generation_order()
    
    def get_structure_relationships(self):
        """
        Get parent-child relationships from the structure graph.
        
        Returns:
            Dictionary mapping each variable to its list of parent variables
        """
        if not hasattr(self, 'cllm_model'):
            raise RuntimeError("Must call fit() before accessing structure relationships")
        return self.generation_model.get_parent_child_relationships()
    
    def get_simple_relationships_text(self):
        """
        Get a simple text representation of structure relationships.
        
        Returns:
            String containing the simple relationships format
        """
        if not hasattr(self, 'cllm_model'):
            raise RuntimeError("Must call fit() before accessing relationships text")
        return self.generation_model.generate_simple_relationships_text()