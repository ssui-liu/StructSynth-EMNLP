import pandas as pd
from typing import Dict, List, Tuple
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser


class HierarchicalPromptTemplateManager:
    """
    Manages prompt template creation for hierarchical structure data generation.
    Handles level-specific prompts and response format instructions.
    """
    
    def __init__(self, target_col: str):
        """
        Initialize the prompt template manager.
        
        Args:
            target_col: Name of the target column for label identification
        """
        self.target_col = target_col
    
    def _get_variable_description(self, var: str, col_description: Dict[str, str]) -> str:
        """
        Get appropriate description for a variable based on its type and role.
        
        Args:
            var: Variable name
            col_description: Dictionary of column descriptions
            
        Returns:
            Formatted description for the variable
        """
        # Get base description from col_description
        description = col_description.get(var, f"feature column, {var}")
        
        # Check if this is a target variable and enhance description accordingly
        if var == self.target_col or var in ["salary", "is_dead", "mortCancer", "death", "death_all", "y", "Diagnosis", "Anxiety Level"]:
            if var == "salary":
                description = f"label if salary above 50K or not, {var}, valid values: '<=50K' and '>50K'"
            elif var in ["is_dead", "mortCancer", "death", "death_all"]:
                description = f"label if patient dead or not, {var}"
            elif var == "y":
                description = f"binary label, {var}"
            elif var == "Diagnosis":
                description = f"label if patient has Alzheimer's Disease or not, {var}"
            elif var == "Anxiety Level":
                description = f"label indicating anxiety level (Low, Medium, High), {var}"
            else:
                description = f"target column, {var}"
        
        return description
    
    def create_level_specific_prompt(
        self, 
        variables: List[str], 
        partial_data: pd.DataFrame,
        task_str: str,
        col_description: Dict[str, str]
    ) -> Tuple[ChatPromptTemplate, str]:
        """
        Create a prompt template for generating specific variables at a level.
        
        Args:
            variables: List of variables to generate at this level
            partial_data: DataFrame with already generated variables (parents)
            task_str: Task description
            col_description: Column descriptions
            
        Returns:
            Tuple of (ChatPromptTemplate, format_instructions)
        """
        # Create response schemas only for the variables we're generating
        response_schemas = []
        for var in variables:
            description = self._get_variable_description(var, col_description)
            resp = ResponseSchema(name=var, description=description)
            response_schemas.append(resp)
        
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        format_instructions = output_parser.get_format_instructions()
        
        # Build template for level-specific generation
        template = self._get_level_generation_template()
        
        return ChatPromptTemplate.from_template(template), format_instructions
    
    def _get_level_generation_template(self) -> str:
        """
        Get the template string for level-specific data generation.
        
        Returns:
            Template string with placeholders for dynamic content
        """
        template = """You are a helpful AI assistant that generates realistic tabular data based on structural dependencies.

Task Description:
{task_str}
Your goal is to generate a realistic synthetic table containing exactly the columns listed in {all_variables_to_output}. This generation must be conditioned on the provided values of their parent features.

Conditioning Data (Current Results):
{parent_data_section}

Relevant Dependency Structure:
{structure_context}

Example Data:
{example_data}

Format Instructions:
------------------
{format_instructions}

Your Task is to Generate the Synthetic Data:
- Your primary task is to generate realistic data for the features listed in {all_variables_to_output}.
- This generation must be **conditioned** on the data provided in 'Conditioning Data (Current Results)'. These are the values of the parent nodes that influence the features you are generating.
- The 'Relevant Dependency Structure' shows you exactly how the conditioning features relate to the features you need to generate.
- Use the 'Example Data' to understand the format, range, and statistical properties of the real data.
- Generate {n_samples} new samples. Each sample must be a valid JSON object.
- Ensure the generated values are plausible and respect the learned dependencies.
{generation_instructions}

IMPORTANT: The output JSON MUST contain all variables listed in '{all_variables_to_output}'.
"""
        return template
    
    def format_prompt_inputs(
        self,
        variables: List[str],
        task_str: str,
        parent_data_str: str,
        structure_context: str,
        format_instructions: str,
        n_samples: int,
        example_data_str: str = ""
    ) -> Dict[str, str]:
        """
        Format the inputs for the prompt template.
        
        Args:
            variables: List of variables being generated
            task_str: Task description
            parent_data_str: String representation of parent data, or None if no parents
            structure_context: Structure context information
            format_instructions: Format instructions for output
            n_samples: Number of samples to generate
            example_data_str: String representation of example data for context
            
        Returns:
            Dictionary of formatted prompt inputs
        """
        # Determine if this is first level generation (no parent variables)
        is_first_level = parent_data_str is None
        
        if is_first_level:
            # First level generation - no parent variables, all variables in the list are new.
            parent_data_section = """Generation Level: ROOT LEVEL (Level 0)
------------------------------------
This is the first level of hierarchical generation. These variables are root variables that do not depend on any parent variables.
Focus on generating realistic baseline values that will serve as foundations for subsequent structural relationships."""
            
            generation_instructions = """- Maintain appropriate statistical distributions similar to the example data.
- Focus on realistic baseline values that can serve as root causes in the structure hierarchy.
- Follow the exact format specified in the format instructions, outputting all requested variables.
"""
            
        else:
            # Subsequent levels - have parent variables.
            # The `variables` list includes these parents AND the new variables to be generated.
            parent_data_section = parent_data_str
            
            generation_instructions = """- For variables listed in 'Conditioning Data (Current Results)', YOU MUST REPRODUCE THEIR VALUES EXACTLY as provided above in your output JSON.
- For any other variables (the new ones for this step), generate new values that are structurally consistent with the parent variable values.
- Maintain appropriate statistical distributions for these new variables, similar to the example data.
- Follow the exact format specified in the format instructions, outputting ALL requested variables (parents and new).
"""
        
        return {
            "task_str": task_str,
            "all_variables_to_output": ", ".join(variables),
            "parent_data_section": parent_data_section,
            "example_data": example_data_str,
            "structure_context": structure_context,
            "format_instructions": format_instructions,
            "n_samples": n_samples,
            "generation_instructions": generation_instructions,
        }
    
    def create_non_structure_prompt(
        self,
        variables: List[str],
        task_str: str,
        col_description: Dict[str, str]
    ) -> Tuple[ChatPromptTemplate, str]:
        """
        Create a prompt template for generating non-structure variables.
        
        Args:
            variables: List of non-structure variables to generate
            task_str: Task description
            col_description: Column descriptions
            
        Returns:
            Tuple of (ChatPromptTemplate, format_instructions)
        """
        # Create response schemas for non-structure variables
        response_schemas = []
        for var in variables:
            description = self._get_variable_description(var, col_description)
            resp = ResponseSchema(name=var, description=description)
            response_schemas.append(resp)
        
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        format_instructions = output_parser.get_format_instructions()
        
        # Use the same template but with different context
        template = self._get_non_structure_generation_template()
        
        return ChatPromptTemplate.from_template(template), format_instructions
    
    def _get_non_structure_generation_template(self) -> str:
        """
        Get the template string for non-structure variable generation.
        
        Returns:
            Template string for non-structure variables
        """
        template = """You are a helpful AI assistant that completes tabular data records by generating values for remaining features.

Task Description:
{task_str}
The core, structurally-dependent features of a dataset have already been generated. Your task is to generate plausible values for the remaining isolated features, ensuring they are statistically consistent with the core features.

Conditioning Data (Generated Graph-Based Features):
{parent_data_section}

Features to Generate (Isolated Features):
{all_variables_to_output}

Example Data:
{example_data}

Format Instructions:
------------------
{format_instructions}

Your Task is to Generate the Independent Values:
- Your primary task is to generate realistic data for the features listed in '{all_variables_to_output}'.
- This generation must be **conditioned** on the complete set of core features provided in 'Conditioning Data'.
- The features you are generating do not have direct parent-child dependencies in the learned graph, but their values should still be plausible and consistent in the context of the entire data record.
- Use the 'Example Data' to understand the typical format and statistical properties of these isolated features.
- Generate {n_samples} new samples. Each sample should be a valid JSON object.

IMPORTANT: The output JSON MUST contain all variables listed in '{all_variables_to_output}', with structural variables exactly matching the provided input.
"""
        return template 