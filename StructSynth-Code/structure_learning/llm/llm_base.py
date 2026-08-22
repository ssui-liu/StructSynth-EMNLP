from typing import Dict, List, Any, Optional, Tuple, Type, Union, Callable
import os
import time
from abc import ABC, abstractmethod

from langchain_core.language_models import BaseLLM, BaseChatModel
from langchain_core.output_parsers import BaseOutputParser
from langchain_openai import ChatOpenAI
# from langchain_google_genai import GoogleGenerativeAI
from langchain_deepseek import ChatDeepSeek
from langchain_community.chat_models import Tongyi
from langchain_community.callbacks import get_openai_callback
from pydantic import BaseModel

from .utils import (
    VALID_PROVIDERS,
    InitialCausalResult,
    retry_function
)

class LLMProvider(ABC):
    """Base class for LLM providers"""

    @abstractmethod
    def get_model(self) -> Union[BaseLLM, BaseChatModel]:
        """Get the underlying LLM model"""
        pass

    @abstractmethod
    def get_structured_model(self, output_schema: Type[BaseModel]) -> Any:
        """Get model with structured output"""
        pass

    @abstractmethod
    def get_usage_callback(self):
        """Get usage tracking callback"""
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider"""

    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.0, **kwargs):
        """
        Initialize OpenAI provider

        Args:
            model_name: Name of the OpenAI model to use
            temperature: Temperature setting for the model
            **kwargs: Additional parameters for the model
        """
        self.model_name = model_name
        self.temperature = temperature
        self.kwargs = kwargs
        self._model = None

    def get_model(self) -> BaseChatModel:
        """Get OpenAI model"""
        if self._model is None:
            self._model = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                **self.kwargs
            )
        return self._model

    def get_structured_model(self, output_schema: Type[BaseModel]) -> Any:
        """Get model with structured output"""
        model = self.get_model()
        return model.with_structured_output(output_schema)

    def get_usage_callback(self):
        """Get OpenAI usage callback"""
        return get_openai_callback()

class DeepSeekProvider(LLMProvider):
    """DeepSeek LLM provider"""

    def __init__(self, model_name: str = "deepseek-chat", temperature: float = 0.0, api_key: Optional[str] = None, **kwargs):
        """
        Initialize DeepSeek provider

        Args:
            model_name: Name of the DeepSeek model to use
            temperature: Temperature setting for the model
            api_key: API key for DeepSeek (optional, uses global key if not provided)
            **kwargs: Additional parameters for the model
        """
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key
        self.kwargs = kwargs
        self._model = None

    def get_model(self) -> BaseChatModel:
        """Get DeepSeek model"""
        if self._model is None:
            if not self.api_key:
                # Use the globally defined deepseek_api_key if not provided in config
                self.api_key = os.getenv("DEEPSEEK_API_KEY")
            self._model = ChatDeepSeek(
                model=self.model_name,
                temperature=self.temperature,
                api_key=self.api_key,
                **self.kwargs
            )
        return self._model

    def get_structured_model(self, output_schema: Type[BaseModel]) -> Any:
        """Get model with structured output"""
        model = self.get_model()
        return model.with_structured_output(output_schema)

    def get_usage_callback(self):
        """Get usage callback (placeholder for DeepSeek)"""
        # Using a dummy callback similar to GoogleAIProvider
        class DummyCallback:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            prompt_tokens = 0
            completion_tokens = 0
            total_cost = 0
        return DummyCallback()

class QwenProvider(LLMProvider):
    """Qwen LLM provider from Alibaba"""

    def __init__(self, model_name: str = "qwen-turbo", temperature: float = 0.0, api_key: Optional[str] = None, **kwargs):
        """
        Initialize Qwen provider

        Args:
            model_name: Name of the Qwen model to use
            temperature: Temperature setting for the model
            api_key: API key for Qwen (optional, uses global key if not provided)
            **kwargs: Additional parameters for the model
        """
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key
        self.kwargs = kwargs
        self._model = None

    def get_model(self) -> BaseChatModel:
        """Get Qwen model"""
        if self._model is None:
            if not self.api_key:
                self.api_key = os.getenv("QWEN_API_KEY")
            self._model = Tongyi(
                model=self.model_name,
                temperature=self.temperature,
                dashscope_api_key=self.api_key,  # Tongyi uses dashscope_api_key
                **self.kwargs
            )
        return self._model

    def get_structured_model(self, output_schema: Type[BaseModel]) -> Any:
        """Get model with structured output"""
        model = self.get_model()
        return model.with_structured_output(output_schema)

    def get_usage_callback(self):
        """Get usage callback (placeholder for Qwen)"""
        class DummyCallback:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            prompt_tokens = 0
            completion_tokens = 0
            total_cost = 0
        return DummyCallback()


class OpenRouterProvider(LLMProvider):
    """OpenRouter provider for models like Llama"""

    def __init__(self, model_name: str, temperature: float = 0.0, api_key: Optional[str] = None, **kwargs):
        """
        Initialize OpenRouter provider

        Args:
            model_name: Name of the model on OpenRouter (e.g., 'llama-3-8b-instruct')
            temperature: Temperature setting for the model
            api_key: API key for OpenRouter (optional, uses global key if not provided)
            **kwargs: Additional parameters for the model
        """
        self.model_name = "meta-llama/" + model_name
        self.temperature = temperature
        self.api_key = api_key
        # Default OpenRouter specific params
        self.kwargs = {
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "top_p": 0.95,
            **kwargs
        }
        self._model = None

    def get_model(self) -> BaseChatModel:
        """Get OpenRouter model (using ChatOpenAI client)"""
        if self._model is None:
            if not self.api_key:
                self.api_key = os.getenv("OPENROUTER_API_KEY")
            self._model = ChatOpenAI(
                openai_api_key=self.api_key,
                openai_api_base="https://openrouter.ai/api/v1",
                model_name=self.model_name,
                temperature=self.temperature,
                **self.kwargs
            )
        return self._model

    def get_structured_model(self, output_schema: Type[BaseModel]) -> Any:
        """Get model with structured output"""
        model = self.get_model()
        return model.with_structured_output(output_schema)

    def get_usage_callback(self):
        """Get usage callback (placeholder for OpenRouter)"""
        class DummyCallback:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            prompt_tokens = 0
            completion_tokens = 0
            total_cost = 0
        return DummyCallback()

def create_provider(config: Dict[str, Any]) -> LLMProvider:
    """
    Factory function to create LLM provider

    Args:
        config: Configuration dictionary containing provider settings

    Returns:
        LLMProvider instance based on configuration

    Raises:
        ValueError: If provider type is invalid or unsupported
    """
    provider_type = config.get("provider_type")
    model_name = config.get("model_name")
    temperature = config.get("temperature", 0.0)
    api_key = config.get("api_key")

    # Validate provider_type
    if not provider_type:
        raise ValueError("LLM provider_type must be specified in the configuration.")
    if provider_type not in VALID_PROVIDERS:
        raise ValueError(f"Unsupported provider type: {provider_type}. Valid options are: {list(VALID_PROVIDERS.keys())}")

    # Get provider specific settings
    provider_settings = VALID_PROVIDERS[provider_type]

    # Set default model_name if not provided, or validate if provided
    if not model_name:
        model_name = provider_settings["default_model"]
    elif model_name not in provider_settings["allowed_models"]:
        raise ValueError(
            f"Unsupported model_name '{model_name}' for provider '{provider_type}'. "
            f"Allowed models are: {provider_settings['allowed_models']}"
        )

    if provider_type == "openai":
        return OpenAIProvider(model_name, temperature, api_key=api_key)
    elif provider_type == "deepseek":
        return DeepSeekProvider(model_name, temperature, api_key=api_key)
    elif provider_type == "qwen":
        return QwenProvider(model_name, temperature, api_key=api_key)
    elif provider_type == "llama":
        return OpenRouterProvider(model_name, temperature, api_key=api_key)
    else:
        # This case should not be reached due to earlier validation, but as a safeguard:
        raise ValueError(f"Unsupported provider type: {provider_type}")

class BaseLLMInterface:
    """
    Base interface for interacting with Large Language Models using LangChain components
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the base LLM interface with configuration

        Args:
            config: Configuration dictionary with LLM settings (api_key, model, etc.)
        """
        self.config = config
        self.provider = create_provider(config)
        self.model = self.provider.get_model()
        self.initial_structured_model = self.provider.get_structured_model(InitialCausalResult)

        # Retry configuration
        self.max_retries = config.get("max_retries", 3)
        self.delay = config.get("retry_delay", 2)

    def query(self, prompt: str, structured_output: Optional[Type[BaseModel]] = None) -> Any:
        """
        Send a query to the LLM and get the response

        Args:
            prompt: The prompt to send to the LLM
            structured_output: Optional output schema for structured parsing

        Returns:
            The LLM's response (string or structured output)
        """
        with self.provider.get_usage_callback() as cb:
            if structured_output:
                # Use with structured output
                structured_model = self.provider.get_structured_model(structured_output)
                result = retry_function(structured_model.invoke, self.max_retries, self.delay, prompt)
                return result
            else:
                # Simple string output
                result = retry_function(self.model.invoke, self.max_retries, self.delay, prompt)
                return result 