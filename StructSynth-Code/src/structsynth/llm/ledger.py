"""Durable request journal, consumption accounting, and budget reservations."""
from __future__ import annotations

import json
import os
from pathlib import Path
import threading
import uuid

from ..artifacts import canonical_json
from .contracts import BudgetExceeded, TokenUsage


class UsageLedger:
    """Append-only request history; resumes budgets from existing requests."""

    def __init__(self, path: str | Path | None = None, *, repair_tail=True):
        self.path = Path(path) if path else None
        self._lock = threading.RLock()
        self.records = []
        self._active = set()
        positions = {}
        self.recovered_truncated_tail = False
        if self.path and self.path.exists():
            lines = self.path.read_bytes().splitlines(keepends=True)
            offset = 0
            for index, line in enumerate(lines):
                if line.strip():
                    try:
                        record = json.loads(line)
                    except (ValueError, UnicodeDecodeError):
                        # A killed append may leave a partial final line. Keep
                        # its durable reservation as unknown; never erase a
                        # complete corrupt record or an error in the middle.
                        if index != len(lines) - 1 or line.endswith(b"\n"):
                            raise
                        if repair_tail:
                            with self.path.open("r+b") as stream:
                                stream.truncate(offset)
                                stream.flush()
                                os.fsync(stream.fileno())
                        self.recovered_truncated_tail = True
                        break
                    ticket = record.get("attempt_id")
                    if ticket and ticket in positions:
                        self.records[positions[ticket]] = record
                    else:
                        if ticket:
                            positions[ticket] = len(self.records)
                        self.records.append(record)
                offset += len(line)
            else:
                if repair_tail and lines and not lines[-1].endswith(b"\n"):
                    with self.path.open("ab") as stream:
                        stream.write(b"\n")
                        stream.flush()
                        os.fsync(stream.fileno())

    def _append(self, value):
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as stream:
                stream.write(canonical_json(value) + "\n")
                stream.flush()
                os.fsync(stream.fileno())

    def reserve(self, config, record=None):
        with self._lock:
            if len(self.records) >= config.request_limit:
                raise BudgetExceeded(f"Request limit reached: {config.request_limit}")
            if config.token_limit is not None:
                totals = [r.get("usage", {}).get("total_tokens") for r in self.records
                          if r.get("attempt_id") not in self._active]
                if any(value is None for value in totals):
                    raise BudgetExceeded("Cannot enforce token limit after a request with unknown usage")
                if sum(totals) >= config.token_limit:
                    raise BudgetExceeded(f"Accounted token limit reached: {config.token_limit}")
            ticket = uuid.uuid4().hex
            pending = {**(record or {}), "attempt_id": ticket, "status": "pending",
                       "usage": TokenUsage().to_dict()}
            self._append(pending)  # Durable before any HTTP call can begin.
            self.records.append(pending)
            self._active.add(ticket)
            return ticket

    def record(self, value, ticket=None):
        with self._lock:
            value = {**value, "attempt_id": ticket or uuid.uuid4().hex}
            self._append(value)
            if ticket is not None:
                index = next(i for i, existing in enumerate(self.records) if existing.get("attempt_id") == ticket)
                self.records[index] = value
                self._active.discard(ticket)
            else:
                self.records.append(value)

    def summary(self):
        with self._lock:
            known = [r.get("usage", {}).get("total_tokens") for r in self.records]
            return {
                "requests": len(self.records),
                "api_requests": sum(r.get("execution_mode", "live") == "live" for r in self.records),
                "replayed_requests": sum(r.get("execution_mode") == "replay" for r in self.records),
                "successful_requests": sum(r.get("status") == "ok" for r in self.records),
                "known_total_tokens": sum(v for v in known if v is not None),
                "requests_with_unknown_usage": sum(v is None for v in known),
                "total_tokens": sum(known) if all(v is not None for v in known) else None,
            }
