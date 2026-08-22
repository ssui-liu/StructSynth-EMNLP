from typing import Dict, List, Any, Optional, Tuple, Type, Union, Callable
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel

from .llm_base import BaseLLMInterface
from .utils import (
    InitialCausalResult,
    format_single_variable_details_for_prompt,
    get_association_type,
    retry_function,
    RootCauseResult
)

class LLMInitialAssessment(BaseLLMInterface):
    """
    LLM interface specialized for initial pairwise causal discovery
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the LLM interface for initial causal assessment
        
        Args:
            config: Configuration dictionary with LLM settings
        """
        super().__init__(config)
        self._load_root_cause_prompt_templates()
    
    def _load_root_cause_prompt_templates(self):
        """Load and prepare prompt templates for initial assessment"""
        # Template for identifying root causes
        self.root_cause_prompt_template = PromptTemplate.from_template(
            """You are an expert data analyst. Based on the following information:

Task Description:

Identify the initial "source nodes" for a dependency graph. A source node is a foundational variable that is not caused by any other variable in this dataset.


All Feature Descriptions:
{variable_descriptions}


Your Task is to Identify the Source Nodes:
- Your only task is to analyze the provided column descriptions.
- Identify the features that are most likely to be source nodes (i.e., fundamental attributes that are not effects of other features).
- Provide your answer as a simple list of the identified source node names."""
        )

        # Create structured models for the new result types
        self.root_cause_structured_model = self.provider.get_structured_model(RootCauseResult)

    def identify_root_causes(self, all_vars_details: Dict[str, Dict[str, Any]]) -> Tuple[List[str], Dict[str, Any]]:
        """
        Identifies root cause variables from a list of all variables.

        Args:
            all_vars_details: A dictionary where keys are variable names and values are their details.

        Returns:
            A tuple containing a list of root cause variable names and a dictionary with token usage stats.
        """
        variable_descriptions = "\\n".join(
            [format_single_variable_details_for_prompt(name, details) for name, details in all_vars_details.items()]
        )
        prompt = self.root_cause_prompt_template.format(variable_descriptions=variable_descriptions)

        with self.provider.get_usage_callback() as cb:
            try:
                result = retry_function(
                    self.root_cause_structured_model.invoke,
                    self.max_retries,
                    self.delay,
                    prompt
                )
                usage = {
                    "prompt_tokens": getattr(cb, "prompt_tokens", 0),
                    "completion_tokens": getattr(cb, "completion_tokens", 0),
                    "total_cost": getattr(cb, "total_cost", 0)
                }
                return result.root_causes, usage
            except Exception as e:
                print(f"Error identifying root causes: {e}")
                return [], {"prompt_tokens": 0, "completion_tokens": 0, "total_cost": 0} 