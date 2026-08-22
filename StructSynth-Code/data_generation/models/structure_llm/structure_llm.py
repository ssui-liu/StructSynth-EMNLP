import pandas as pd
import numpy as np
import json
import re
import time
from typing import Tuple, Optional, Dict, Any, List, Set, Union, Callable
from copy import deepcopy
from tqdm import tqdm

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks import get_openai_callback

# Import base CLLM and templates from parent directory
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from basic_llm import BasicLLM
from basic_llm.dataset_llm_templates import langchain_templates

# Import the new modular components
from .structure_graph_processor import StructureGraphProcessor
from .structure_prompt_templates import HierarchicalPromptTemplateManager


def retry_function(func: Callable, max_retries: int = 3, delay: float = 2.0, *args, **kwargs) -> Any:
    """
    Helper function to retry operations on failure.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Result of the function call
        
    Raises:
        Exception: If all retry attempts fail
    """
    last_exception = None
    for attempt in range(1, max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            print(f"Attempt {attempt} failed: {str(e)}")
            if attempt < max_retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise last_exception


class HierarchicalStructureLLM(BasicLLM):
    """
    Hierarchical Structure Language Model Learning (Hierarchical CLLM) for synthetic data generation.
    Generates tabular data following a hierarchical structure:
    1. First generates root variables (level 0)
    2. Then generates each subsequent level based on parent values
    3. Finally generates non-structure variables
    """
    
    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        api_key: Optional[str] = None,
        dataset: str = "default",
        target_col: str = "target",
        graph_file: str = "graph.json",
        cycle_size: int = 10,  # Standard number of root samples per cycle
        max_retries: int = 5,  # Maximum retry attempts for LLM calls
        retry_delay: float = 2.0,  # Delay between retries in seconds
        generation_retries: int = 10  # Retries for generation loops when no children produced
    ):
        """
        Initialize Hierarchical CLLM generator.
        
        Args:
            model: Name of the LLM model to use
            temperature: Temperature parameter for generation
            max_tokens: Maximum tokens for generation
            api_key: Optional API key for the LLM
            dataset: Name of dataset for template selection
            target_col: Name of the target column to use for label validation
            graph_file: Path to the structure graph JSON file
            cycle_size: Standard number of root samples per cycle
            max_retries: Maximum retry attempts for LLM calls
            retry_delay: Delay between retries in seconds
            generation_retries: Retries for generation loops when no children produced
        """
        super().__init__(model, temperature, max_tokens, api_key, dataset, target_col)
        
        # Initialize the structure graph processor
        self.graph_processor = StructureGraphProcessor(graph_file)
        
        # Initialize the prompt template manager
        self.prompt_manager = HierarchicalPromptTemplateManager(target_col)
        
        # Storage for intermediate generated data
        self.partial_data = None
        
        self.cycle_size = cycle_size  # Standard number of root samples per cycle
        
        # Retry configuration
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.generation_retries = generation_retries
        
        print(f"Hierarchical CLLM initialized with graph: {graph_file}")
        print(f"Cycle size: {cycle_size}")
        print(f"Retry config: max_retries={max_retries}, retry_delay={retry_delay}s, generation_retries={generation_retries}")
        print(f"Max generation attempts before skipping consistency: {generation_retries}")  # Updated logging
    
    def _parse_level_response(self, response: str, expected_variables: List[str]) -> pd.DataFrame:
        """Parse LLM response into DataFrame with label validation."""
        try:
            # Extract and parse JSON objects
            dict_strings = re.findall(r"\{[^{}]*\}", response)
            dicts = [json.loads(ds) for ds in dict_strings]
            df = pd.DataFrame(dicts)
            
            # Filter out metadata rows
            df = df[~df.apply(
                lambda row: any(
                    isinstance(cell, str) and cell in ["integer", "float", "numeric", "categorical"]
                    for cell in row
                ), axis=1
            )]

            # Validate target labels if available
            if self.valid_labels and self.target_col and self.target_col in df.columns:
                invalid_mask = ~df[self.target_col].isin(self.valid_labels)
                if invalid_mask.any():
                    invalid_count = invalid_mask.sum()
                    print(f"Warning: Filtered {invalid_count}/{len(df)} rows with invalid labels")
                    df = df[~invalid_mask]

            return df

        except Exception as e:
            print(f"Error parsing response: {str(e)}")
            return pd.DataFrame()
    
    def generate_hierarchical(
        self,
        n_samples: int,
        task_str: str,
        col_description: Dict[str, str],
        return_token_usage: bool = False
    ) -> Union[Tuple[pd.DataFrame, pd.Series], Tuple[pd.DataFrame, pd.Series, Dict[str, int]]]:
        """
        Generate synthetic samples following the hierarchical structure.
        Uses an iterative approach:
        1. Generate root variables (typically gets L < n samples)
        2. For each level, generate based on existing partial data
        3. If level generates fewer samples, fill remaining slots iteratively
        4. Repeat entire process until n_samples are generated
        
        Args:
            n_samples: Number of samples to generate
            task_str: Task description
            col_description: Column descriptions
            return_token_usage: Whether to return token usage statistics
            
        Returns:
            Tuple of (synthetic_features, synthetic_labels) or with token_usage if requested
        """
        if self.example_df is None:
            raise RuntimeError("Must call fit() before generating data")
        
        print(f"Starting iterative hierarchical generation of {n_samples} samples")
        print(f"Generation order: {self.graph_processor.generation_order}")
        
        # Initialize storage for all generated data
        all_generated_data = []
        total_usage = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
        total_generated = 0
        
        # Generate in cycles until we have enough samples
        while total_generated < n_samples:
            remaining = n_samples - total_generated
            print(f"\nGeneration cycle: need {remaining} more samples ({total_generated}/{n_samples})")
            
            cycle_data = self._generate_cycle(remaining, task_str, col_description)
            
            if not cycle_data.empty:
                all_generated_data.append(cycle_data)
                total_generated += len(cycle_data)
                print(f"Cycle completed: generated {len(cycle_data)} samples")
            else:
                print("Warning: No data generated in this cycle")
                continue
        
        # Combine all generated data
        if all_generated_data:
            final_data = pd.concat(all_generated_data, ignore_index=True)
            # Trim to exact number of samples requested
            final_data = final_data.head(n_samples)
        else:
            raise RuntimeError("No data was generated")
        
        # Ensure we have the target column
        if self.target_col not in final_data.columns:
            raise ValueError(f"Target column '{self.target_col}' not found in generated data")
        
        # Extract features and labels
        y = final_data[self.target_col].copy()
        X = final_data.drop(columns=[self.target_col])
        
        print(f"Final result: Generated {len(X)} samples with {len(X.columns)} features")
        
        if return_token_usage:
            return X, y, total_usage
        return X, y

    def _generate_cycle(self, target_samples: int, task_str: str, col_description: Dict[str, str]) -> pd.DataFrame:
        """Generate one complete cycle with adaptive root generation based on target samples needed."""
        current_data = pd.DataFrame()
        
        # Use adaptive cycle size - don't generate more roots than needed
        adaptive_cycle_size = min(self.cycle_size, target_samples)
        
        # Generate root variables with adaptive cycle size
        root_vars = self._get_available_variables(self.graph_processor.get_level_variables(0))
        if root_vars:
            print(f"Generating root variables: {root_vars} (adaptive size: {adaptive_cycle_size})")
            current_data = self._generate_variables(
                variables=root_vars,
                parent_data=pd.DataFrame(),
                max_samples=adaptive_cycle_size,  # Use adaptive size instead of fixed cycle_size
                task_str=task_str,
                col_description=col_description
            )
            
            if current_data.empty:
                print("Warning: Root generation failed")
                return pd.DataFrame()
            
            print(f"Generated {len(current_data)} root samples")
        
        # Generate subsequent levels with while loop tracking
        max_level = self.graph_processor.get_max_level()
        for level in range(1, max_level + 1):
            if current_data.empty:
                break
                
            level_vars = self._get_available_variables(self.graph_processor.get_level_variables(level))
            if level_vars:
                # New logic: determine direct parents for current level's variables
                all_parents = self.graph_processor.get_parent_child_relationships()
                level_parents = set()
                for var in level_vars:
                    if var in all_parents:
                        level_parents.update(all_parents[var])
                
                # Filter current_data to only include direct parent columns
                parent_cols = [p for p in level_parents if p in current_data.columns]
                parent_data_for_level = current_data[parent_cols]

                print(f"Generating level {level}: {level_vars} for {len(current_data)} samples, using parents: {parent_cols}")
                
                generated_level_data = self._generate_with_parent_matching(
                    variables=level_vars,
                    parent_data=parent_data_for_level,
                    task_str=task_str,
                    col_description=col_description,
                    level_name=f"level {level}"
                )
                
                if generated_level_data.empty:
                    print(f"Warning: No children generated at level {level}, stopping generation for this cycle.")
                    break
                
                # Merge the newly generated data with the existing data
                new_vars_data = generated_level_data[level_vars]
                
                # Align indices for a safe merge, and select columns that are not newly generated
                parent_and_ancestor_cols = [col for col in current_data.columns if col not in level_vars]
                current_data_subset = current_data.loc[generated_level_data.index, parent_and_ancestor_cols]
                
                # Concatenate along columns
                current_data = pd.concat([current_data_subset, new_vars_data], axis=1)

                if current_data.empty:
                    print(f"Warning: No children generated at level {level}")
                    break
                
                print(f"Level {level} completed: {len(current_data)} total samples")
        
        # Generate non-structure variables with same matching process
        if current_data.empty:
            return current_data
            
        non_structure_vars = self._get_available_variables(self.graph_processor.non_structure_variables or [])
        if non_structure_vars:
            print(f"Generating non-structure variables: {non_structure_vars} for {len(current_data)} samples")
            current_data = self._generate_with_parent_matching(
                variables=non_structure_vars,
                parent_data=current_data,
                task_str=task_str,
                col_description=col_description,
                level_name="non-structure"
            )

        return current_data

    def _generate_with_parent_matching(
        self,
        variables: List[str],
        parent_data: pd.DataFrame,
        task_str: str,
        col_description: Dict[str, str],
        level_name: str
    ) -> pd.DataFrame:
        """
        Generate variables with parent matching using while loop until all parents have valid children.
        
        Args:
            variables: List of variable names to generate
            parent_data: DataFrame containing parent variable values
            task_str: Task description string
            col_description: Dictionary mapping column names to descriptions
            level_name: Name of the current level for logging
            
        Returns:
            DataFrame with generated variables matching parent structure
        """
        if not variables or parent_data.empty:
            return parent_data
        
        # Use while loop to generate children until all parents have valid children
        remaining_parents = parent_data.copy()
        generated_children = []
        iteration_count = 0  # Track while loop iterations (for logging)
        consecutive_failed_attempts = 0  # Track consecutive failed generation attempts
        
        while not remaining_parents.empty:
            iteration_count += 1
            print(f"  Processing iteration {iteration_count}: Attempting to generate {level_name} for {len(remaining_parents)} remaining parents")
            
            # Generate children for remaining parents (single attempt, no inner retry loop)
            new_children = None
            try:
                new_children = self._generate_variables(
                    variables=variables,
                    parent_data=remaining_parents,
                    max_samples=len(remaining_parents),
                    task_str=task_str,
                    col_description=col_description,
                    generation_attempt=consecutive_failed_attempts + 1  # Pass failed attempts + 1
                )
                
            except Exception as e:
                print(f"    Generation iteration {iteration_count} failed: {str(e)}")
                consecutive_failed_attempts += 1
                
                # Check if we should give up after consecutive failures
                if consecutive_failed_attempts >= self.generation_retries:
                    print(f"  Too many consecutive failed attempts ({consecutive_failed_attempts}), stopping generation for {level_name}")
                    break
                continue  # Try next iteration
            
            if new_children is None or new_children.empty:
                print(f"  No valid children generated in iteration {iteration_count}")
                consecutive_failed_attempts += 1
                
                # Check if we should give up after consecutive failures
                if consecutive_failed_attempts >= self.generation_retries:
                    print(f"  Too many consecutive failed attempts ({consecutive_failed_attempts}), stopping generation for {level_name}")
                    break
                continue  # Try again in next iteration
            
            # Check if consistency was skipped in _generate_batch (this happens when generation_attempt >= self.generation_retries)
            # The generation_attempt we passed was consecutive_failed_attempts + 1
            generation_attempt_used = consecutive_failed_attempts + 1
            consistency_was_skipped = generation_attempt_used >= self.generation_retries
            
            # Reset consecutive failures since we got some children
            consecutive_failed_attempts = 0
            
            if consistency_was_skipped:
                print(f"  Consistency checks were skipped in generation - using generated children directly")
                generated_children.append(new_children)
                
                # Remove the first N samples from remaining_parents where N = number of generated children
                num_generated = len(new_children)
                if num_generated > 0 and len(remaining_parents) >= num_generated:
                    remaining_parents = remaining_parents.iloc[num_generated:].reset_index(drop=True)
                    print(f"  Removed first {num_generated} parents from remaining_parents, {len(remaining_parents)} parents still remaining")
                else:
                    # If we generated more children than remaining parents or equal, clear remaining_parents
                    remaining_parents = pd.DataFrame(columns=remaining_parents.columns)
                    print(f"  Generated {num_generated} children for {len(remaining_parents)} parents - cleared remaining_parents")
                
                # Continue the loop to try generating for any remaining parents
                continue
            
            # Normal case: Check consistency and get matched children
            if not new_children.empty:
                # The new_children df contains only newly generated columns.
                # We need to combine it with the parents it was generated from.
                # The indices of new_children correspond to the indices in remaining_parents.
                parents_for_new_children = remaining_parents.loc[new_children.index]
                matched_children = pd.concat([parents_for_new_children, new_children], axis=1)

                # Update remaining_parents by dropping the ones that now have children
                remaining_parents = remaining_parents.drop(new_children.index)
            else:
                matched_children = pd.DataFrame()

            # Only append the children that matched to parents
            if not matched_children.empty:
                generated_children.append(matched_children)
                print(f"  Generated {len(matched_children)} valid children, {len(remaining_parents)} parents remaining (iteration {iteration_count})")
            else:
                print(f"  No children matched parents in iteration {iteration_count}, {len(remaining_parents)} parents remaining")
        
        # Final logging
        if not remaining_parents.empty:
            print(f"  Warning: Finished processing with {len(remaining_parents)} parents still remaining after {iteration_count} iterations")
        
        # Combine all generated children
        if generated_children:
            result = pd.concat(generated_children, ignore_index=True)
            print(f"  {level_name} completed: {len(result)} total samples")
            return result
        else:
            print(f"  No children generated for {level_name}")
            return pd.DataFrame(columns=list(parent_data.columns) + variables)

    def _match_children_to_parents(
        self,
        children_output: pd.DataFrame,
        remaining_parents: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Match children to parents on a row-level basis (child[i] matches parent[i]).
            
        Returns:
            Tuple of (matched_children_df, updated_remaining_parents_df)
        """
        if remaining_parents.empty or children_output.empty:
            return children_output, remaining_parents
        
        parent_cols = list(remaining_parents.columns)
        matched_children_indices = []
        matched_parent_indices = []
        
        # Determine how many rows we can compare (minimum of both DataFrames)
        num_to_compare = min(len(children_output), len(remaining_parents))
        
        # print(f"    DEBUG: Row-level matching {num_to_compare} children to {num_to_compare} parents")
        
        # Simple row-level matching: child[i] matches parent[i]
        for i in range(num_to_compare):
            child_row = children_output.iloc[i]
            parent_row = remaining_parents.iloc[i]
            
            if self._rows_match(child_row, parent_row, parent_cols):
                matched_children_indices.append(children_output.index[i])
                matched_parent_indices.append(remaining_parents.index[i])
            else:
                print(f"    DEBUG: Child {i} does not match parent {i}")
        
        # print(f"    DEBUG: {len(matched_children_indices)} children matched their corresponding parents")
        
        # Get matched children
        if matched_children_indices:
            matched_children = children_output.loc[matched_children_indices]
        else:
            matched_children = pd.DataFrame(columns=children_output.columns)
        
        # Remove matched parents from remaining_parents
        if matched_parent_indices:
            updated_remaining_parents = remaining_parents.drop(matched_parent_indices).reset_index(drop=True)
        else:
            updated_remaining_parents = remaining_parents
        
        print(f"    DEBUG: After matching - {len(matched_children)} matched children, {len(updated_remaining_parents)} remaining parents")
        
        return matched_children, updated_remaining_parents

    def _rows_match(self, child_row, parent_row, parent_cols: List[str]) -> bool:
        """Check if child row matches parent row for given columns."""
        try:
            for col in parent_cols:
                if child_row[col] != parent_row[col]:
                    return False
            return True
        except Exception as e:
            print(f"      Warning: Could not compare column values: {e}")
            return False

    def _get_available_variables(self, variables: List[str]) -> List[str]:
        """Filter variables to only those available in the example dataset."""
        if not variables:
            return []
        return self.graph_processor.filter_available_variables(variables, self.example_df.columns.tolist())

    def _generate_variables(
        self,
        variables: List[str],
        parent_data: pd.DataFrame,
        max_samples: int,
        task_str: str,
        col_description: Dict[str, str],
        generation_attempt: int = 1  # Add parameter to track current generation attempt
    ) -> pd.DataFrame:
        """
        Generate variables with parent context and consistency checking.
        
        Args:
            variables: List of variable names to generate
            parent_data: Parent data DataFrame
            max_samples: Maximum number of samples to generate
            task_str: Task description
            col_description: Column descriptions
            generation_attempt: Current generation attempt number
            
        Returns:
            DataFrame with generated variables
        """
        if not variables:
            return parent_data
            
        parent_cols = list(parent_data.columns) if not parent_data.empty else []
        
        print(f"Generating {variables}, based on parents {parent_cols} (attempt {generation_attempt})")
        
        # Determine if we should skip consistency check based on generation attempts
        skip_consistency = generation_attempt >= self.generation_retries
        if skip_consistency:
            print(f"  Max generation attempts ({self.generation_retries}) reached - will skip consistency checks")
        
        # Detect if we're generating non-structure variables and use appropriate prompt template
        is_non_structure = (self.graph_processor.non_structure_variables and 
                       any(var in self.graph_processor.non_structure_variables for var in variables))
        
        if is_non_structure:
            # Use non-structure specific prompt for non-structure variables
            print(f"  Using non-structure prompt for variables: {variables}")
            prompt_template, format_instructions = self.prompt_manager.create_non_structure_prompt(
                variables, task_str, col_description
            )
        else:
            # Use standard hierarchical prompt for structure variables
            prompt_template, format_instructions = self.prompt_manager.create_level_specific_prompt(
                variables, parent_data, task_str, col_description
            )
        
        chain = prompt_template | self.llm | StrOutputParser()
        
        # Generate in batches
        batch_size = min(100, max_samples)
        all_results = []
        
        for i in tqdm(range(0, max_samples, batch_size), desc=f"Generating {variables}"):
            current_batch_size = min(batch_size, max_samples - i)
            
            # Prepare batch context
            batch_parent_data = parent_data.iloc[i:i+current_batch_size] if not parent_data.empty else pd.DataFrame()
            
            try:
                # Generate batch with skip_consistency_check parameter
                batch_result = self._generate_batch(
                    chain=chain,
                    batch_parent_data=batch_parent_data,
                    current_batch_size=current_batch_size,
                    task_str=task_str,
                    variables=variables,
                    format_instructions=format_instructions,
                    skip_consistency_check=skip_consistency,  # Pass the skip parameter
                    is_non_structure=is_non_structure  # Pass non-structure detection result
                )
                
                if not batch_result.empty:
                    all_results.append(batch_result)
                    
            except Exception as e:
                print(f"Error in batch generation: {str(e)}")
                continue
        
        return pd.concat(all_results, ignore_index=False) if all_results else pd.DataFrame(columns=variables)

    def _generate_batch(
        self,
        chain,
        batch_parent_data: pd.DataFrame,
        current_batch_size: int,
        task_str: str,
        variables: List[str],
        format_instructions: str,
        skip_consistency_check: bool = False,  # Add parameter to skip consistency check
        is_non_structure: bool = False  # Add parameter to pass non-structure detection result
    ) -> pd.DataFrame:
        """
        Generate a single batch and perform consistency checking.
        
        Args:
            chain: LangChain chain for generation
            batch_parent_data: Parent data for this batch
            current_batch_size: Number of samples to generate
            task_str: Task description
            variables: Variables being generated in this batch
            format_instructions: Format instructions for the LLM
            skip_consistency_check: If True, skip consistency check and return raw LLM output
            is_non_structure: If True, indicates that the generation is for non-structure variables
            
        Returns:
            DataFrame with generated batch data
        """
        # Prepare example data
        example_data = self._get_example_data(variables)
        
        # Prepare parent data for prompt
        parent_data_str = None
        if not batch_parent_data.empty:
            parent_data_str = batch_parent_data.to_dict(orient="records")
        
        # Get structure context
        structure_context = self.graph_processor.get_structure_context_for_level(variables)
        
        # Format prompt
        formatted_prompt = self.prompt_manager.format_prompt_inputs(
            variables=variables,
            task_str=task_str,
            parent_data_str=parent_data_str,
            structure_context=structure_context,
            format_instructions=format_instructions,
            n_samples=current_batch_size,
            example_data_str=str(example_data)
        )
        
        # Generate response
        response_text = self._invoke_llm(chain, formatted_prompt)
        
        # Parse response
        llm_output = self._parse_level_response(response_text, variables)
        if llm_output.empty:
            return pd.DataFrame(columns=variables)
        
        # Ensure all expected columns are present
        for col in variables:
            if col not in llm_output.columns:
                llm_output[col] = np.nan
        llm_output = llm_output[variables]
        
        # Consistency check is removed
        if len(llm_output) > current_batch_size:
            llm_output = llm_output.head(current_batch_size)
        return llm_output

    def _get_example_data(self, cols: List[str]) -> str:
        """Get example data for few-shot prompting."""
        available_cols = [col for col in cols if col in self.example_df.columns]
        if not available_cols or self.example_df.empty:
            return "No example data available."
        
        # num_examples = min(batch_size, len(self.example_df), 5)
        # indices = np.random.choice(len(self.example_df), num_examples,
        #                          replace=len(self.example_df) < num_examples)
        examples = self.example_df[available_cols]
        return examples.to_dict(orient="records")

    def _invoke_llm(self, chain, formatted_prompt: str) -> str:
        """Invoke LLM with retry logic and optional token tracking."""
        def _llm_call():
            if isinstance(self.llm, ChatOpenAI):
                with get_openai_callback() as cb:
                    return chain.invoke(formatted_prompt)
            return chain.invoke(formatted_prompt)
        
        # Use retry function for LLM calls
        try:
            return retry_function(
                _llm_call,
                max_retries=self.max_retries,
                delay=self.retry_delay
            )
        except Exception as e:
            print(f"LLM call failed after {self.max_retries} retries: {str(e)}")
            raise

    def fit(
        self,
        example_df: pd.DataFrame,
        task_str: str,
        col_description: Dict[str, str],
        structure_info: Optional[str] = None
    ):
        """
        Prepare the hierarchical model for generation.
        
        Args:
            example_df: Example DataFrame with features and target
            task_str: Description of the task
            col_description: Description of columns
            structure_info: Optional structure relationship information (will use graph structure)
        """
        # Call parent fit method
        super().fit(example_df, task_str, col_description, structure_info)
        
        # Initialize partial data storage
        self.partial_data = None
        
        print("Hierarchical CLLM fitted and ready for generation")

    def generate_simple_relationships_text(self) -> str:
        """
        Generate a simple text format containing all structure relationships in the graph.
        
        Returns:
            String containing the simple relationships format
        """
        return self.graph_processor.generate_simple_relationships_text()
    
    def get_parent_child_relationships(self) -> Dict[str, List[str]]:
        """
        Get parent-child relationships from the structure graph.
        
        Returns:
            Dictionary mapping each variable to its list of parent variables
        """
        return self.graph_processor.get_parent_child_relationships()
    
    def get_generation_order(self) -> List[str]:
        """
        Get the generation order for structure variables.
        
        Returns:
            List of variables in generation order
        """
        return self.graph_processor.generation_order
    
    def get_structure_edges(self) -> List[Dict[str, Any]]:
        """
        Get all structure edges from the graph.
        
        Returns:
            List of structure edge dictionaries
        """
        return self.graph_processor.structure_edges

