"""Offline replay preserving logical responses and source-request provenance."""
from __future__ import annotations

from pathlib import Path
import threading

from ..artifacts import file_hash
from .contracts import (BudgetExceeded, LLMConfigurationError, LLMResponse,
                        LLMResponseError, LLMTransportError, TokenUsage)
from .ledger import UsageLedger


class ReplayClient:
    """Replay recorded requests by content hash; never performs network I/O."""

    def __init__(self, path: str | Path, *, ledger: UsageLedger | None = None):
        path = Path(path)
        self.source_sha256 = file_hash(path)
        self.identity = {"kind": "replay", "sha256": self.source_sha256}
        self.ledger = ledger if ledger is not None else UsageLedger()
        self._lock = threading.Lock()
        self._responses = {}
        self.replayed = 0
        identities = []
        for record in UsageLedger(path, repair_tail=False).records:
            if "client_identity" in record:
                identities.append(record["client_identity"])
            self._responses.setdefault(record["request_key"], []).append(record)
        if identities:
            if any(value != identities[0] for value in identities):
                raise LLMConfigurationError("Replay log contains multiple client identities")
            self.identity = identities[0]

    def complete(self, request):
        with self._lock:
            responses = self._responses.get(request.key, [])
            if not responses:
                raise LLMResponseError(f"No replay response for {request.purpose} ({request.key[:12]})")
            while True:
                record = responses.pop(0)
                self.replayed += 1
                # A live complete() retried these attempts internally; preserve
                # the same logical response for the algorithm during replay.
                if not record.get("retry_scheduled"):
                    break
                if not responses:
                    raise LLMResponseError("Replay log ends during transport retry")
            self.ledger.record({**record, "source_attempt_id": record.get("attempt_id"),
                                "source_usage": record.get("usage"), "usage": TokenUsage(0, 0).to_dict(),
                                "execution_mode": "replay", "source_sha256": self.source_sha256})
        if record.get("status") != "ok":
            error_type = {"LLMTransportError": LLMTransportError,
                          "LLMConfigurationError": LLMConfigurationError,
                          "BudgetExceeded": BudgetExceeded}.get(record.get("error_type"), LLMResponseError)
            raise error_type(record.get("error", "Recorded request failed"))
        usage = record.get("usage", {})
        return LLMResponse(record["content"], TokenUsage(usage.get("prompt_tokens"), usage.get("completion_tokens")),
                           record.get("resolved_model", record.get("model", "replay")))
