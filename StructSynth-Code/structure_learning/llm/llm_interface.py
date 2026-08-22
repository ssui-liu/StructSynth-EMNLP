"""
Unified LLM Interface for Causal Discovery

This module provides a unified interface that combines:
- Initial pairwise causal assessment (llm_init.py)
- Graph refinement and contradiction resolution (llm_refine.py)
- Base LLM functionality and providers (llm_base.py)
- Utility functions and data models (utils.py)
"""

from typing import Dict, List, Any, Optional, Tuple, Type, Union, Callable

# Import all components from the modularized structure
from .utils import (
    CausalRelationship,
    ConfidenceLevel,
    InitialCausalResult,
    RefinementResult,
    format_single_variable_details_for_prompt,
    retry_function,
    get_association_type,
    VALID_PROVIDERS,
    openai_api_key,
    deepseek_api_key,
    Effect
)

from .llm_base import (
    LLMProvider,
    OpenAIProvider,
    GoogleAIProvider,
    DeepSeekProvider,
    create_provider,
    BaseLLMInterface
)

from .llm_init import LLMInitialAssessment
from .llm_resolve import LLMCycleResolver
from .llm_generate import LLMGenerate


class LLMInterface:
    """
    Unified interface for LLM-based causal discovery that combines
    initial assessment and refinement capabilities
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the unified LLM interface
        
        Args:
            config: Configuration dictionary with LLM settings (api_key, model, etc.)
        """
        self.config = config
        
        # Initialize specialized components
        self.initial_assessment = LLMInitialAssessment(config)
        self.cycle_resolver = LLMCycleResolver(config)
        self.generate = LLMGenerate(config)
        
        # Expose commonly used attributes from the base components
        self.provider = self.initial_assessment.provider
        self.model = self.initial_assessment.model
        self.max_retries = config.get("max_retries", 3)
        self.delay = config.get("retry_delay", 2)
    
    def identify_root_causes(self, all_vars_details: Dict[str, Dict[str, Any]]) -> Tuple[List[str], Dict[str, Any]]:
        """
        Identifies root cause variables by calling the specialized method in LLMInitialAssessment.
        """
        return self.initial_assessment.identify_root_causes(all_vars_details)

    def identify_direct_effects(self, source_variable: str, all_vars_details: Dict[str, Dict[str, Any]], current_graph_str: str, correlation_info: str) -> Tuple[List[Effect], Dict[str, Any]]:
        """
        Identifies direct effects of a variable by calling the specialized method in LLMInitialAssessment.
        """
        return self.generate.identify_direct_effects(source_variable, all_vars_details, current_graph_str, correlation_info)

    def resolve_cycle_conflict(self, cycle_edges: List[Dict[str, Any]], new_edge: Dict[str, Any]) -> Tuple[str, str]:
        """
        Resolves a cycle conflict by asking the LLM which edge to remove.
        """
        return self.cycle_resolver.resolve_cycle_conflict(cycle_edges, new_edge)
    
    # ==================== Unified Workflow Methods ====================
    
    def query(self, prompt: str, structured_output: Optional[Type] = None) -> Any:
        """
        Send a query to the LLM and get the response
        
        Args:
            prompt: The prompt to send to the LLM
            structured_output: Optional output schema for structured parsing
            
        Returns:
            The LLM's response (string or structured output)
        """
        return self.initial_assessment.query(prompt, structured_output)

# ==================== Backward Compatibility ====================
# Keep the original class name and methods for backward compatibility
# This allows existing code to continue working without changes

# Export the unified interface as the main LLMInterface
__all__ = [
    'LLMInterface',
    'LLMInitialAssessment', 
    'BaseLLMInterface',
    'LLMProvider',
    'OpenAIProvider',
    'GoogleAIProvider', 
    'DeepSeekProvider',
    'create_provider',
    'CausalRelationship',
    'ConfidenceLevel',
    'InitialCausalResult',
    'RefinementResult',
    'format_single_variable_details_for_prompt',
    'retry_function',
    'get_association_type',
    'VALID_PROVIDERS',
    'openai_api_key',
    'deepseek_api_key',
    'LLMCycleResolver',
    'LLMGenerate'
] 