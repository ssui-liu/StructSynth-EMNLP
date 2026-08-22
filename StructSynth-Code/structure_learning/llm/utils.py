from typing import Dict, List, Any, Optional, Tuple, Type, Union, Callable
import os
import time
from enum import Enum
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define API keys from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
qwen_api_key = os.getenv("QWEN_API_KEY")
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

# Define valid providers and their models/defaults
VALID_PROVIDERS = {
    "openai": {
        "default_model": "gpt-4o",
        "allowed_models": ["gpt-4o", "gpt-4o-mini"] # Add other valid OpenAI models
    },
    "deepseek": {
        "default_model": "deepseek-chat",
        "allowed_models": ["deepseek-chat", "deepseek-reasoner"] # Add other valid DeepSeek models
    },
    "qwen": {
        "default_model": "qwen2.5-72b-instruct",
        "allowed_models": ["qwen2.5-72b-instruct", "qwen2.5-32b-instruct"]
    },
    "llama": {
        "default_model": "llama-4-scout",
        "allowed_models": ["llama-4-scout", "llama-4-maverick"]
    }
}

class CausalRelationship(str, Enum):
    """Enum for possible causal relationships"""
    VAR1_CAUSES_VAR2 = "1->2"
    VAR2_CAUSES_VAR1 = "2->1"
    NO_RELATION = "none"

class ConfidenceLevel(str, Enum):
    """Enum for confidence levels"""
    VERY_HIGH = "Very High"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    VERY_LOW = "Very Low"

class InitialCausalResult(BaseModel):
    """Structured output for initial causal assessment"""
    relationship: CausalRelationship = Field(
        description="The causal relationship between the variables"
    )
    confidence: ConfidenceLevel = Field(
        description="The confidence level in the assessment"
    )
    reasoning: str = Field(
        description="Concise reasoning behind the assessment (max 200 characters)",
        max_length=200,
        min_length=10
    )

class RootCauseResult(BaseModel):
    """Structured output for identifying root cause variables."""
    root_causes: List[str] = Field(
        description="List of variable names that are identified as root causes (unaffected by other variables)."
    )

class Effect(BaseModel):
    """Represents a single causal effect with its metadata."""
    variable: str = Field(
        description="The name of the variable that is a direct effect."
    )
    confidence: ConfidenceLevel = Field(
        description="The confidence level for this causal link (e.g., High, Medium, Low)."
    )
    reasoning: str = Field(
        description="Concise reasoning for why this causal relationship exists.",
        max_length=200,
    )

class DirectEffectsResult(BaseModel):
    """Structured output for identifying direct effects of a variable."""
    direct_effects: List[Effect] = Field(
        description="List of objects, where each object represents a direct causal effect with its variable name, confidence, and reasoning."
    )

class EdgeToRemove(BaseModel):
    """
    Pydantic model for the output of the cycle resolution LLM call.
    """
    source: str = Field(..., description="The source node of the edge to be removed.")
    target: str = Field(..., description="The target node of the edge to be removed.")


def format_single_variable_details_for_prompt(var_name: str, var_details: Dict[str, Any]) -> str:
    """
    Helper function to format a single variable's details for prompt inclusion.
    
    Args:
        var_name: Name of the variable
        var_details: Dictionary containing variable details
        
    Returns:
        Formatted string representation of variable details
    """
    if not var_details:
        return f"{var_name}: Details not available.\n"
    
    details_str = f"Variable: {var_name}\n"
    details_str += f"  Description: {var_details.get('description', 'N/A')}\n"
    details_str += f"  Type: {var_details.get('type', 'N/A')}\n"
    
    if "statistics_str" in var_details:
        details_str += f"  Statistics: {var_details['statistics_str']}\n"
    elif "frequent_values_str" in var_details:
        fv_str = var_details["frequent_values_str"]
        # Indent multi-line frequent_values_str for better readability in the prompt
        if '\n' in fv_str: # Check if it's already multi-line (e.g. from DataLoader)
            indented_fv = "\n".join([f"    {line.strip()}" for line in fv_str.split('\n')])
            details_str += f"  Frequent Values:\n{indented_fv}\n"
        else: # Single line or unformatted
             details_str += f"  Frequent Values: {fv_str}\n"
    else:
        details_str += "  Additional Details: Not available\n"
    return details_str

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

def get_association_type(var1_type: str, var2_type: str) -> str:
    """
    Determine the appropriate association type based on variable types.
    
    Args:
        var1_type: Type of the first variable
        var2_type: Type of the second variable
        
    Returns:
        String indicating the association type
    """
    if var1_type == "categorical" and var2_type == "categorical":
        return "cramer"
    elif (var1_type == "categorical" and var2_type == "numerical") or \
         (var1_type == "numerical" and var2_type == "categorical"):
        return "correlation_ratio"
    else:
        return "pearson" 