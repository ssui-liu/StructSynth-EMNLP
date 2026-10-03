from concurrent.futures import ThreadPoolExecutor
from urllib.error import URLError

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
    assert replay.identity == client.identity
    assert replay.complete(REQUEST) == output
    with pytest.raises(LLMResponseError, match="No replay"):
        replay.complete(REQUEST)


def test_provider_snapshot_survives_replay_without_new_api_consumption(tmp_path):
    source = tmp_path / "source.jsonl"
    original = UsageLedger(source)
    raw = {**response(), "model": "provider-snapshot-2026-01", "system_fingerprint": "backend-version"}
    client = OpenAICompatibleClient(LLMConfig(model="provider-alias"), ledger=original, transport=lambda _: raw)
    expected = client.complete(REQUEST)
    record = original.records[0]
    assert record["requested_model"] == "provider-alias"
    assert record["resolved_model"] == expected.model == "provider-snapshot-2026-01"
    assert record["system_fingerprint"] == "backend-version"
    assert original.summary()["api_requests"] == 1
    replay_ledger = UsageLedger(tmp_path / "replay.jsonl")
    assert ReplayClient(source, ledger=replay_ledger).complete(REQUEST) == expected
    assert replay_ledger.summary()["api_requests"] == 0
    assert replay_ledger.summary()["replayed_requests"] == 1
    assert replay_ledger.summary()["total_tokens"] == 0
    assert replay_ledger.records[0]["source_usage"]["total_tokens"] == 10


@pytest.mark.parametrize("tail", [b"", b'\n{"partial":"\xe4'])
def test_replay_reads_without_repairing_the_original_journal(tmp_path, tail):
    path = tmp_path / "source.jsonl"
    client = OpenAICompatibleClient(LLMConfig(), ledger=UsageLedger(path), transport=lambda _: response())
    client.complete(REQUEST)
    source = path.read_bytes().rstrip(b"\n") + tail
    path.write_bytes(source)
    assert ReplayClient(path).complete(REQUEST).content == {"ok": True}
    assert path.read_bytes() == source


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


def test_replay_preserves_logical_response_after_transport_retry(tmp_path):
    ledger = UsageLedger(tmp_path / "requests.jsonl")
    calls = []
    def transport(_):
        calls.append(1)
        if len(calls) == 1:
            raise URLError("temporary")
        return response()
    client = OpenAICompatibleClient(LLMConfig(retry_delay=0), ledger=ledger, transport=transport)
    expected = client.complete(REQUEST)
    replay = ReplayClient(tmp_path / "requests.jsonl")
    assert replay.complete(REQUEST) == expected
    assert replay.replayed == 2
