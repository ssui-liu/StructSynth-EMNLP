from typing import Dict, List, Any, Tuple
from langchain_core.prompts import PromptTemplate
from pydantic import Field
from .llm_base import BaseLLMInterface
from .utils import retry_function, format_single_variable_details_for_prompt, ConfidenceLevel, Effect, DirectEffectsResult


class LLMGenerate(BaseLLMInterface):
    """
    LLM interface specialized for generating direct causal effects.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the LLM interface for generating direct effects.
        """
        super().__init__(config)
        self._load_direct_effects_prompt_template()

    def _load_direct_effects_prompt_template(self):
        """Load and prepare prompt templates for identifying direct effects."""
        self.direct_effects_prompt_template = PromptTemplate.from_template(
            """You are an expert data analyst building a dependency graph. Based on the following information:

Task Description:

For the given '{source_variable}', your task is to propose its direct successors (effects) from the list of available features. For each proposed dependency, you must provide a brief, evidence-based rationale.

Current Graph State:
{current_graph}

All Candidate Features:
{variable_descriptions}

Statistical Evidence (Association Scores):
{correlation_info}

Your Task is to Propose and Justify New Links:
- Your focus is on the feature: '{source_variable}'.
- Review the Statistical Evidence, which shows the strength of association between '{source_variable}' and other candidate features.
- Based on the statistical scores and the existing graph, identify which other features are most likely to be direct effects of '{source_variable}'.
- For each dependency you propose, you must provide the variable name, your confidence level (Very High, High, Medium, Low, or Very Low), and a concise rationale. This rationale should explain why the dependency makes sense (e.g., "Higher Education is strongly correlated with and typically precedes higher Income").
- Do not propose links that would create an obvious logical contradiction with the existing graph structure. Do not list variables that are already known to be parents of '{source_variable}' or have an indirect relationship.
"""
        )
        self.direct_effects_structured_model = self.provider.get_structured_model(DirectEffectsResult)

    def identify_direct_effects(self, source_variable: str, all_vars_details: Dict[str, Dict[str, Any]],
                                current_graph_str: str, correlation_info: str) -> Tuple[List[Effect], Dict[str, Any]]:
        """
        Identifies variables that are direct causal effects of a source variable.
        """
        variable_descriptions = "\\n".join(
            [format_single_variable_details_for_prompt(name, details) for name, details in all_vars_details.items()]
        )
        prompt = self.direct_effects_prompt_template.format(
            source_variable=source_variable,
            current_graph=current_graph_str,
            variable_descriptions=variable_descriptions,
            correlation_info=correlation_info
        )

        with self.provider.get_usage_callback() as cb:
            try:
                result = retry_function(
                    self.direct_effects_structured_model.invoke,
                    self.max_retries,
                    self.delay,
                    prompt
                )
                usage = {
                    "prompt_tokens": getattr(cb, "prompt_tokens", 0),
                    "completion_tokens": getattr(cb, "completion_tokens", 0),
                    "total_cost": getattr(cb, "total_cost", 0)
                }
                return result.direct_effects, usage
            except Exception as e:
                print(f"Error identifying direct effects for '{source_variable}': {e}")
                return [], {"prompt_tokens": 0, "completion_tokens": 0, "total_cost": 0} 