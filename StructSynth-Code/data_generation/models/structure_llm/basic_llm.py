import pandas as pd
from typing import Tuple, Optional, Dict, Any, Set, Union
import json
import re
from tqdm import tqdm
from langchain_community.llms import Tongyi

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek  # Add import for ChatDeepSeek
from langchain_core.output_parsers import StrOutputParser
# Add the import for OpenAI callback
from langchain_community.callbacks import get_openai_callback

# Local imports
from data_generation.models.structure_llm.basic_prompt_templates import langchain_templates
from data_generation.models.structure_llm.llm_provider import create_provider

class BasicLLM:
    """
    Causal Language Model Learning (CLLM) for synthetic data generation using LangChain with OpenAI models
    """
    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        api_key: Optional[str] = None,
        dataset: str = "default",
        target_col: str = "target"  # Add target column parameter with default value
    ):
        """
        Initialize CLLM generator.
        
        Args:
            model: Name of the LLM model to use
            temperature: Temperature parameter for generation
            max_tokens: Maximum tokens for generation
            api_key: Optional API key for the LLM
            dataset: Name of dataset for template selection and regression task detection
            target_col: Name of the target column to use for label validation
        """
        # Determine provider type from model name
        if "deepseek" in model:
            provider_type = "deepseek"
        elif "qwen" in model:
            provider_type = "qwen"
        elif "llama" in model:
            provider_type = "llama"
        else:
            provider_type = "openai"

        # Prepare configuration for the provider
        config = {
            "provider_type": provider_type,
            "model_name": model,
            "temperature": temperature,
            "api_key": api_key,
            "max_tokens": max_tokens
        }

        # Create provider and get model
        self.provider = create_provider(config)
        self.llm = self.provider.get_model()
        
        self.dataset = dataset
        self.example_df = None
        self.chain = None
        self.formatted_prompt = None
        self.format_instructions = None
        self.valid_labels = None  # Will store valid label values
        self.target_col = target_col  # Set target column name directly
        self.is_regression = False  # Flag to track if this is a regression task

    def _is_regression_task(self) -> bool:
        """
        Determine if this is a regression task.
        
        Returns:
            True if regression task, False if classification
        """
        if self.dataset:
            # Import here to avoid circular imports
            from src.evaluation.metrics import EvaluationMetrics
            return EvaluationMetrics.is_regression_task(self.dataset)
        return False

    def _extract_valid_labels(self) -> Set[Any]:
        """
        Extract valid label values from example data.
        For regression tasks, returns empty set (no discrete validation needed).
        
        Returns:
            Set of valid label values (empty for regression)
        """
        if self.example_df is None or self.target_col is None:
            return set()
        
        # Skip label extraction for regression tasks
        if self._is_regression_task():
            return set()
        
        # Check if target column exists in the example dataframe
        if self.target_col not in self.example_df.columns:
            raise ValueError(f"Target column '{self.target_col}' not found in example data. Available columns: {list(self.example_df.columns)}")
        
        # Get unique values from the target column
        valid_values = set(self.example_df[self.target_col].unique())
        return valid_values

    def fit(
        self,
        example_df: pd.DataFrame,
        task_str: str,
        col_description: Dict[str, str],
        causal_info: Optional[str] = None
    ):
        """
        Prepare the model for generation by formatting prompt templates.
        
        Args:
            example_df: Example DataFrame with features and target
            task_str: Description of the task
            col_description_str: Description of columns
            causal_info: Optional causal relationship information
        """
        self.example_df = example_df

        # Verify the target column exists in the data
        if self.target_col not in example_df.columns:
            raise ValueError(f"Target column '{self.target_col}' not found in example data. Available columns: {list(example_df.columns)}")
        
        # Extract valid labels from the example data
        self.is_regression = self._is_regression_task()
        self.valid_labels = self._extract_valid_labels()
        
        if not self.is_regression:
            print(f"Extracted {len(self.valid_labels)} valid labels from example data: {self.valid_labels}")
        else:
            print("Regression task detected - skipping discrete label validation")

        # Get templates using the example data - pass target_col to ensure consistency
        self.prompt, _, self.format_instructions, _ = langchain_templates(
            example_df=self.example_df,
            dataset=self.dataset,
            task_str=task_str,
            col_description=col_description,
            target_col=self.target_col  # Pass the target column name to ensure consistency
        )

        # Create the chain
        self.chain = self.prompt | self.llm | StrOutputParser()

        # Format the prompt dictionary with all available information
        self.formatted_prompt = {
            "data": str(self.example_df.to_dict(orient="records")),
            "format_instructions": self.format_instructions,
            "task_str": task_str,
        }
        
        # Add causal info if provided
        if causal_info:
            causal_prompt = f"\n\nCAUSAL RELATIONSHIPS ANALYSIS:\n{causal_info}\n\nUse the above causal relationships to guide your generation of synthetic data that preserves these causal structures.\n\n"
            self.formatted_prompt["causal_info"] = causal_prompt
            

    def _generate_samples(self) -> Tuple[pd.DataFrame, Dict[str, int]]:
        """Generate synthetic samples using LangChain"""
        if self.chain is None or self.formatted_prompt is None:
            raise RuntimeError("Must call fit() before generating samples")

        try:
            # Use the provider's usage callback
            with self.provider.get_usage_callback() as cb:
                # Generate samples using LangChain chain
                response = self.chain.invoke(self.formatted_prompt)
                
                # Process the response
                df = self._process_response(response)
                
                # Get token usage from the callback
                usage = {
                    'prompt_tokens': cb.prompt_tokens,
                    'completion_tokens': cb.completion_tokens,
                    'total_tokens': cb.total_tokens
                }
                
            return df, usage
            
        except Exception as e:
            print(f"LangChain error: {str(e)}")
            return pd.DataFrame(), {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}

    def _process_response(self, response: str) -> pd.DataFrame:
        """Process LangChain response into a DataFrame with label validation"""
        df_list = []
        
        try:
            # Extract dict-like strings
            dict_strings = re.findall(r"\{[^{}]*\}", response)
            dicts = [json.loads(ds) for ds in dict_strings]
            
            df_tmp = pd.DataFrame(dicts)
            # Filter out metadata rows
            df_tmp = df_tmp[
                ~df_tmp.apply(
                    lambda row: any(
                        isinstance(cell, str) and cell in 
                        ["integer", "float", "numeric", "categorical"]
                        for cell in row
                    ),
                    axis=1
                )
            ]
            
            # Skip label validation for regression tasks
            if not self.is_regression and self.valid_labels and self.target_col and self.target_col in df_tmp.columns:
                # Check for invalid labels (only for classification)
                invalid_mask = ~df_tmp[self.target_col].isin(self.valid_labels)
                invalid_labels = df_tmp.loc[invalid_mask, self.target_col].unique()
                
                if any(invalid_mask):
                    # Count invalid entries
                    invalid_count = invalid_mask.sum()
                    total_count = len(df_tmp)
                    print(f"Warning: Found {invalid_count}/{total_count} rows with invalid labels: {invalid_labels}")
                    
                    # Remove invalid entries (strict validation)
                    df_tmp = df_tmp[~invalid_mask]
                    print(f"Filtered out {invalid_count} rows with invalid labels")
                    
                    # If all entries were filtered out, return empty dataframe
                    if df_tmp.empty:
                        print("All generated entries contained invalid labels!")
                        return pd.DataFrame()
            
            df_list.append(df_tmp)
                
        except Exception as e:
            print(f"Error processing response: {str(e)}")
            
        if df_list:
            return pd.concat(df_list, ignore_index=True)
        return pd.DataFrame()

    def generate(
        self, 
        n_samples: int, 
        return_token_usage: bool = False,
        strict_label_validation: bool = True
    ) -> Union[Tuple[pd.DataFrame, pd.Series], Tuple[pd.DataFrame, pd.Series, Dict[str, int]]]:
        """
        Generate synthetic samples using CLLM.
        
        Args:
            n_samples: Number of samples to generate
            return_token_usage: Whether to return token usage statistics
            strict_label_validation: Whether to strictly enforce valid labels
            
        Returns:
            If return_token_usage=False:
                Tuple of (synthetic_features, synthetic_labels)
            If return_token_usage=True:
                Tuple of (synthetic_features, synthetic_labels, token_usage_dict)
        """
        if self.chain is None:
            raise RuntimeError("Must call fit() before generating data")
            
        df_list = []
        samples_generated = 0
        max_iterations = 500  # Safety limit
        
        # Track total token usage
        total_usage = {
            'prompt_tokens': 0,
            'completion_tokens': 0,
            'total_tokens': 0
        }
        
        # Initialize progress bar
        pbar = tqdm(total=n_samples, desc="Generating samples")
        prev_samples = 0
        
        for i in range(max_iterations):
            try:
                df_synthetic, usage = self._generate_samples()
                if not df_synthetic.empty:
                    df_list.append(df_synthetic)

                # Update token usage
                for key in usage:
                    total_usage[key] += usage[key]

                samples_generated = sum(len(df) for df in df_list)
                
                # Update progress bar with new samples
                new_samples = samples_generated - prev_samples
                pbar.update(min(new_samples, n_samples - prev_samples))
                prev_samples = samples_generated
                
                if samples_generated >= n_samples:
                    break
                    
            except Exception as e:
                print(f"Generation error: {str(e)}")
                continue
        
        pbar.close()
                
        if not df_list:
            raise RuntimeError("Failed to generate any valid synthetic samples")
            
        # Combine all generated samples
        df_combined = pd.concat(df_list, ignore_index=True)
        
        # Ensure correct dtypes
        try:
            df_combined = df_combined.astype(self.example_df.dtypes)
        except:
            # Handle type conversion errors
            for col in df_combined.columns:
                try:
                    df_combined[col] = df_combined[col].astype(self.example_df[col].dtype)
                except:
                    continue
        
        # Verify target column exists in generated data
        if self.target_col not in df_combined.columns:
            raise ValueError(f"Target column '{self.target_col}' not found in generated data. Available columns: {list(df_combined.columns)}")
        
        # Check for duplicate columns, particularly focusing on the target column
        duplicate_cols = df_combined.columns[df_combined.columns.duplicated(keep=False)]
        if self.target_col in duplicate_cols:
            print(f"Warning: Duplicate target column '{self.target_col}' detected.")
            
            # For each duplicate column, identify which one has meaningful data
            # Keep the one that doesn't have NaN values or has fewer NaN values
            col_indices = [i for i, col in enumerate(df_combined.columns) if col == self.target_col]
            if len(col_indices) > 1:
                # Check NaN counts for each column with the same name
                nan_counts = [df_combined.iloc[:, idx].isna().sum() for idx in col_indices]
                
                # Find the index with the minimum number of NaNs
                valid_col_idx = col_indices[nan_counts.index(min(nan_counts))]
                
                # Rename columns to ensure we keep the right one
                new_columns = list(df_combined.columns)
                for i, idx in enumerate(col_indices):
                    if idx == valid_col_idx:
                        new_columns[idx] = self.target_col
                    else:
                        new_columns[idx] = f"{self.target_col}_duplicate_{i}"
                
                df_combined.columns = new_columns
                
                # Log the action taken
                print(f"Renamed duplicate '{self.target_col}' columns to preserve meaningful data.")
        
        # Extract target column before dropping
        y = df_combined[self.target_col].copy()
        
        # Final label validation - ensure all labels are valid (skip for regression)
        if strict_label_validation and not self.is_regression and self.valid_labels:
            invalid_mask = ~y.isin(self.valid_labels)
            invalid_count = invalid_mask.sum()
            
            if invalid_count > 0:
                # print(f"Warning: Final dataset contains {invalid_count} invalid labels")
                
                # # Remove invalid labels from final dataset
                valid_indices = ~invalid_mask
                y = y[valid_indices]
                df_combined = df_combined[valid_indices]
                
                print(f"Filtered out {invalid_count} rows with invalid labels from final dataset")
                # raise ValueError(f"Final dataset contains {invalid_count} invalid labels")
        
        # Drop target column and any duplicates of it
        target_cols_to_drop = [col for col in df_combined.columns if col == self.target_col]
        X = df_combined.drop(columns=target_cols_to_drop)
        
        # Also drop any columns containing "duplicate" in their name as they're likely processed duplicates
        duplicate_pattern_cols = [col for col in X.columns if "_duplicate_" in col]
        if duplicate_pattern_cols:
            X = X.drop(columns=duplicate_pattern_cols)
            
        # Trim to requested number of samples
        X = X.head(n_samples)
        y = y.head(n_samples)
        
        # Sanity check - ensure our feature matrix doesn't contain the target
        target_related_cols = [col for col in X.columns if self.target_col in col]
        if target_related_cols:
            print(f"Warning: Feature matrix still contains columns related to '{self.target_col}': {target_related_cols}")
            X = X.drop(columns=target_related_cols)
        
        if return_token_usage:
            return X, y, total_usage
        return X, y 