from concurrent.futures import ThreadPoolExecutor
import json

import pytest

from structsynth.config import LLMConfig
from structsynth.llm import (BudgetExceeded, LLMConfigurationError, LLMRequest, LLMResponseError,
                             OpenAICompatibleClient, ReplayClient, UsageLedger)


def response(content='{"ok":true}', usage=None, reason="stop"):
    return {"choices": [{"message": {"content": content}, "finish_reason": reason}],
            "usage": usage if usage is not None else {"prompt_tokens": 7, "completion_tokens": 3}}


REQUEST = LLMRequest("test", "Return an object", {"x": 1}, {"type": "object"})


def test_parameters_usage_and_replay(tmp_path):
    calls = []
    ledger = UsageLedger(tmp_path / "llm.jsonl")
    def transport(body):
        calls.append(body)
        return response()
    client = OpenAICompatibleClient(LLMConfig(max_tokens=1234, temperature=0.4), ledger=ledger, transport=transport)
    output = client.complete(REQUEST)
    assert output.content == {"ok": True}
    assert calls[0]["max_tokens"] == 1234
    assert calls[0]["temperature"] == 0.4
    assert calls[0]["top_p"] == 0.95
    assert ledger.summary()["total_tokens"] == 10
    assert "Authorization" not in (tmp_path / "llm.jsonl").read_text()
    replay = ReplayClient(tmp_path / "llm.jsonl")
    assert replay.complete(REQUEST) == output
    with pytest.raises(LLMResponseError, match="No replay"):
        replay.complete(REQUEST)


def test_invalid_json_still_records_consumption(tmp_path):
    ledger = UsageLedger(tmp_path / "usage.jsonl")
    client = OpenAICompatibleClient(LLMConfig(), ledger=ledger, transport=lambda _: response("invalid"))
    with pytest.raises(LLMResponseError):
        client.complete(REQUEST)
    assert ledger.summary()["total_tokens"] == 10
    assert ledger.summary()["successful_requests"] == 0


def test_request_limit_survives_restart(tmp_path):
    path = tmp_path / "usage.jsonl"
    config = LLMConfig(request_limit=1)
    OpenAICompatibleClient(config, ledger=UsageLedger(path), transport=lambda _: response()).complete(REQUEST)
    resumed = OpenAICompatibleClient(config, ledger=UsageLedger(path), transport=lambda _: pytest.fail("network called"))
    with pytest.raises(BudgetExceeded):
        resumed.complete(REQUEST)


def test_parallel_calls_cannot_exceed_request_limit():
    calls = []
    def transport(_):
        calls.append(1)
        return response()
    client = OpenAICompatibleClient(LLMConfig(request_limit=3), transport=transport)
    def complete(_):
        try:
            return client.complete(REQUEST)
        except BudgetExceeded:
            return None
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(complete, range(20)))
    assert len(calls) == 3


def test_unknown_usage_is_not_reported_as_zero():
    client = OpenAICompatibleClient(LLMConfig(token_limit=100), transport=lambda _: response(usage={}))
    assert client.complete(REQUEST).usage.total_tokens is None
    assert client.ledger.summary()["total_tokens"] is None
    with pytest.raises(BudgetExceeded, match="unknown usage"):
        client.complete(REQUEST)


def test_missing_key_fails_before_budget_consumption(monkeypatch):
    monkeypatch.delenv("STRUCTSYNTH_TEST_KEY", raising=False)
    client = OpenAICompatibleClient(LLMConfig(api_key_env="STRUCTSYNTH_TEST_KEY"))
    with pytest.raises(LLMConfigurationError):
        client.complete(REQUEST)
    assert client.ledger.summary()["requests"] == 0


@pytest.mark.parametrize("content", ['{"x":NaN}', '{"x":Infinity}'])
def test_nonfinite_json_rejected(content):
    client = OpenAICompatibleClient(LLMConfig(), transport=lambda _: response(content))
    with pytest.raises(LLMResponseError):
        client.complete(REQUEST)


def test_truncated_response_rejected_even_if_json_is_valid():
    client = OpenAICompatibleClient(LLMConfig(), transport=lambda _: response(reason="length"))
    with pytest.raises(LLMResponseError, match="Incomplete"):
        client.complete(REQUEST)
