"""LLM request/response contracts, usage values, and typed failures."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Optional, Protocol

from ..artifacts import fingerprint


class LLMError(RuntimeError):
    pass


class LLMConfigurationError(LLMError):
    pass


class BudgetExceeded(LLMError):
    pass


class LLMResponseError(LLMError):
    pass


class LLMTransportError(LLMError):
    pass


@dataclass(frozen=True)
class TokenUsage:
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None

    @property
    def total_tokens(self):
        if self.prompt_tokens is None or self.completion_tokens is None:
            return None
        return self.prompt_tokens + self.completion_tokens

    def to_dict(self):
        return {**asdict(self), "total_tokens": self.total_tokens}


@dataclass(frozen=True)
class LLMRequest:
    purpose: str
    system: str
    payload: dict[str, Any]
    response_schema: Optional[dict[str, Any]] = None
    request_id: str = ""

    @property
    def key(self):
        return fingerprint(asdict(self))


@dataclass(frozen=True)
class LLMResponse:
    content: Any
    usage: TokenUsage = TokenUsage()
    model: str = ""


class LLMClient(Protocol):
    identity: dict[str, Any]

    def complete(self, request: LLMRequest) -> LLMResponse:
        ...
