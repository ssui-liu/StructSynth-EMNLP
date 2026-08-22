from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from typing import Dict, Optional  # Update import to include Optional
import pandas as pd

def langchain_templates(
    example_df: pd.DataFrame, 
    dataset: str, 
    task_str: Optional[str] = None,
    col_description: Optional[Dict[str, str]] = None,
    target_col: str = "target"  # Add target_col parameter with default value
):
    """
    Create LangChain templates for synthetic data generation.
    
    Args:
        example_df: Example DataFrame containing both features and target
        dataset: Name of dataset for template selection
        task_str: Description of the task
        col_description: Dictionary mapping column names to descriptions
        target_col: Name of the target column (used for response schema naming)
    """
    response_schemas = []
    
    # Create response schemas for each column
    for col in example_df.columns:
        # Determine if this column is a target/label column
        is_target_column = False
        
        # Check if this is a known label column from predefined list
        if col in ["is_dead", "mortCancer", "death", "death_all", "y", "salary", "Diagnosis", "Anxiety Level"]:
            is_target_column = True
            
            # Use the description based on column type
            if col in ["is_dead", "mortCancer", "death", "death_all"]:
                description = f"label if patient dead or not, {col}"
            elif col == "y":
                description = f"binary label, {col}"
            elif col == "salary":
                description = f"label if salary above 50K or not, {col}, valid values: '<=50K' and '>50K'"
            elif col == "Diagnosis":
                description = f"label if patient has Alzheimer's Disease or not, {col}"
            elif col == "Anxiety Level":
                description = f"label indicating anxiety level (Low, Medium, High), {col}"
            else:
                description = f"target column, {col}"
        else:
            # Use custom description if provided, otherwise use generic description
            description = col_description.get(col, f"feature column, {col}") if col_description else f"feature column, {col}"
        
        # Create schema with the right name based on whether it's a target column
        resp = ResponseSchema(
            # Use the target_col parameter for target columns, otherwise use the original column name
            name=target_col if is_target_column and col != target_col else col,
            description=description,
        )
        response_schemas.append(resp)

    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    # Base template structure
    base_template = """You are a synthetic data generator specialized in {domain}.

Task Description:
----------------
{task_str}

Your goal is to generate synthetic data that:
1. Maintains the statistical properties and relationships between features
2. Preserves the causal structure of the data
3. Creates diverse but realistic samples
4. Follows the format specified in the examples

Example Data:
------------
{data}

{causal_info}

Format Instructions:
------------------
{format_instructions}


Generate 1000 new samples following this structure but DO NOT copy the examples directly. DO NOT generate code to conduct generation.
Each sample should be a valid JSON object matching the example structure.
"""

    # Dataset-specific configurations
    dataset_configs = {
        "covid": {
            "domain": "COVID-19 medical data",
            "task_prefix": "Generate synthetic COVID-19 patient data that reflects realistic medical conditions and outcomes in Brazil."
        },
        "cutract": {
            "domain": "prostate cancer data in the UK",
            "task_prefix": "Generate synthetic prostate cancer patient data that reflects realistic medical conditions and outcomes in the UK."
        },
        "compas": {
            "domain": "criminal recidivism prediction",
            "task_prefix": "Generate synthetic criminal justice data that reflects realistic patterns in recidivism while maintaining demographic distributions."
        },
        "seer": {
            "domain": "prostate cancer data in the USA",
            "task_prefix": "Generate synthetic prostate cancer patient data that reflects realistic medical conditions and outcomes in the USA."
        },
        "support": {
            "domain": "hospitalized patient data",
            "task_prefix": "Generate synthetic hospitalized patient data that reflects realistic medical conditions and outcomes."
        },
        "maggic": {
            "domain": "heart failure patient data",
            "task_prefix": "Generate synthetic heart failure patient data that reflects realistic medical conditions and outcomes."
        },
        "adult": {
            "domain": "income prediction",
            "task_prefix": "Generate synthetic demographic and employment data that reflects realistic patterns in salary prediction."
        },
        "higgs": {
            "domain": "particle physics",
            "task_prefix": "Generate synthetic particle physics data that reflects realistic patterns in Higgs boson detection."
        },
        "bio": {
            "domain": "biological response prediction",
            "task_prefix": "Generate synthetic molecular data that reflects realistic patterns in biological response prediction."
        },
        "drug": {
            "domain": "drug consumption prediction",
            "task_prefix": "Generate synthetic demographic and behavioral data that reflects realistic patterns in drug usage."
        },
        "alzheimers": {
            "domain": "Alzheimer's disease prediction",
            "task_prefix": "Generate synthetic Alzheimer's disease patient data that reflects realistic patterns in Alzheimer's disease prediction."
        },
        "anxiety": {
            "domain": "anxiety level prediction",
            "task_prefix": "Generate synthetic patient data reflecting demographic, lifestyle, physiological, and behavioral factors related to anxiety levels."
        },
        "default": {
            "domain": "tabular data generation",
            "task_prefix": "Generate synthetic tabular data that reflects realistic patterns in the given domain."
        }
    }

    # Get dataset config, defaulting to "default" if dataset not found
    config = dataset_configs.get(dataset, dataset_configs["default"])
    
    # Use provided task_str or default to dataset-specific task prefix
    task_description = task_str if task_str else config["task_prefix"]

    # Create the generator template
    generator_template = base_template.format(
        domain=config["domain"],
        task_str=task_description,
        data="{data}",
        format_instructions="{format_instructions}",
        causal_info="{causal_info}"
    )

    prompt = ChatPromptTemplate.from_template(template=generator_template)

    return prompt, generator_template, format_instructions, example_df
