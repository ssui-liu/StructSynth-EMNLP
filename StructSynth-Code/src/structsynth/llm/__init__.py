"""A small JSON LLM boundary with budgets, request logs and offline replay.

No credentials are loaded and no provider dependencies are imported at import time.
The package exports preserve the public API of the former ``llm.py`` module.
"""

from .client import OpenAICompatibleClient
from .contracts import (
    BudgetExceeded,
    LLMClient,
    LLMConfigurationError,
    LLMError,
    LLMRequest,
    LLMResponse,
    LLMResponseError,
    LLMTransportError,
    TokenUsage,
)
from .ledger import UsageLedger
from .parsing import parse_json_content
from .replay import ReplayClient

__all__ = [
    "BudgetExceeded",
    "LLMClient",
    "LLMConfigurationError",
    "LLMError",
    "LLMRequest",
    "LLMResponse",
    "LLMResponseError",
    "LLMTransportError",
    "OpenAICompatibleClient",
    "ReplayClient",
    "TokenUsage",
    "UsageLedger",
    "parse_json_content",
]
