from typing import Dict, List, Any, Tuple
from langchain_core.prompts import PromptTemplate
from .llm_base import BaseLLMInterface
from .utils import EdgeToRemove, retry_function


class LLMCycleResolver(BaseLLMInterface):
    """
    LLM interface specialized for resolving cycles in causal graphs.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the LLM interface for cycle resolution.
        """
        super().__init__(config)
        self._load_cycle_resolution_prompt_template()

    def _load_cycle_resolution_prompt_template(self):
        """Load and prepare prompt templates for cycle resolution."""
        self.cycle_resolution_prompt_template = PromptTemplate.from_template("""You are a logical reasoning expert tasked with resolving a contradiction in a dependency graph. Based on the following information:

Task Description:
Analyze the provided dependencies and their rationales within the cycle. Identify the single dependency with the weakest or least plausible rationale and recommend it for removal to break the cycle.

Conflicting Cycle with Rationales:
{cycle_edges_str}

Your Task is to Identify the Weakest Link:
- A logical contradiction (a cycle) has been detected in the graph, detailed in 'Conflicting Cycle with Rationales'.
- Your task is to carefully evaluate the `rationale` provided for each edge in this cycle.
- Based on your analysis of the rationales, identify the single weakest link.
- The weakest link is the dependency whose rationale is the least plausible, least supported, or most likely to be spurious.
- Provide your final answer as the single dependency edge that should be removed to resolve the contradiction. Respond with the source and target of the edge to remove.
""")

    def format_cycle_resolution_prompt(self, cycle_edges: List[Dict[str, Any]]) -> str:
        """
        Format the prompt for LLM-based cycle resolution.
        """
        cycle_edges_str = ""
        for edge in cycle_edges:
            cycle_edges_str += f"- {edge['from']} -> {edge['to']} (Confidence: {edge.get('confidence', 'N/A')}, Reasoning: {edge.get('reasoning', 'N/A')})\n"

        return self.cycle_resolution_prompt_template.format(
            cycle_edges_str=cycle_edges_str
        )

    def resolve_cycle_conflict(self, cycle_edges: List[Dict[str, Any]], new_edge: Dict[str, Any]) -> Tuple[str, str]:
        """
        Use the LLM to decide which edge to remove from a cycle.
        """
        prompt = self.format_cycle_resolution_prompt(cycle_edges)
        
        with self.provider.get_usage_callback() as cb:
            try:
                structured_model = self.provider.with_structured_output(EdgeToRemove)
                result = retry_function(
                    structured_model.invoke,
                    self.max_retries,
                    self.delay,
                    prompt
                )
                
                usage = {
                    "prompt_tokens": getattr(cb, "prompt_tokens", 0),
                    "completion_tokens": getattr(cb, "completion_tokens", 0),
                    "total_cost": getattr(cb, "total_cost", 0)
                }
                
                print(f"LLM usage for cycle resolution: {usage}")
                return result.source, result.target

            except Exception as e:
                print(f"Error in LLM cycle resolution: {e}. Defaulting to removing the new edge.")
                return new_edge['from'], new_edge['to'] 