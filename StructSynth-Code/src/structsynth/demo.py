"""Deterministic offline pipeline exercise, explicitly not a quality baseline."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import threading

import pandas as pd

from .artifacts import atomic_csv, atomic_json, frame_records
from .config import DataConfig, EvaluationConfig, ExperimentConfig, GenerationConfig, LLMConfig
from .llm import LLMResponse, TokenUsage
from .pipeline import run_experiments


class DemoClient:
    """Return training rows to exercise plumbing, deliberately allowing memorization."""

    def __init__(self, train, spec, config, ledger):
        self.rows = frame_records(train)
        self.spec, self.config, self.ledger = spec, config, ledger
        self.identity = {"kind": "offline-demo-bootstrap", "version": 1}
        self._lock = threading.Lock()

    def complete(self, request):
        ticket = self.ledger.reserve(self.config, {"request_key": request.key, "request": asdict(request),
                                                    "client_identity": self.identity, "model": "offline-demo",
                                                    "execution_mode": "offline-demo"})
        record = {"request_key": request.key, "request": asdict(request), "client_identity": self.identity,
                  "model": "offline-demo", "usage": TokenUsage(0, 0).to_dict(), "status": "error",
                  "execution_mode": "offline-demo"}
        try:
            root = self.spec.columns[0]
            if request.purpose == "source_nodes":
                content = {"source_nodes": [root]}
            elif request.purpose == "direct_successors":
                content = {"successors": []}
                if request.payload["source"] == root and self.spec.target_column != root:
                    content["successors"] = [{"target": self.spec.target_column, "reasoning": "Offline test edge; not model inference", "confidence": "High"}]
            elif request.purpose.startswith("generation."):
                columns = request.payload["features_to_generate"]
                content = {"rows": [{"row_id": row_id,
                                     "values": {c: self.rows[row_id % len(self.rows)][c] for c in columns}}
                                    for row_id in request.payload["requested_row_ids"]]}
            else:
                raise ValueError(f"Offline demo does not implement {request.purpose}")
            record.update(status="ok", content=content)
            return LLMResponse(content, TokenUsage(0, 0), "offline-demo")
        finally:
            self.ledger.record(record, ticket)


def demo_factory(name, config, ledger, train, spec):
    return DemoClient(train, spec, config, ledger)


def run_demo(output_dir: str | Path, *, resume=False, max_workers=1, model="logistic"):
    output = Path(output_dir).resolve()
    inputs = output / "demo_inputs"
    frame = pd.DataFrame({
        "age": [18 + i % 53 for i in range(120)],
        "group": ["ABC"[i % 3] for i in range(120)],
        "outcome": ["yes" if (i * 7) % 13 > 5 else "no" for i in range(120)],
    })
    atomic_csv(inputs / "toy.csv", frame)
    atomic_json(inputs / "metadata.json", {"name": "offline_demo", "target_column": "outcome",
                                          "task_type": "classification", "task": "Offline software verification only",
                                          "descriptions": {c: c for c in frame}})
    config = ExperimentConfig(
        data=DataConfig("offline_demo", str(inputs / "toy.csv"), str(inputs / "metadata.json"),
                        shots=[20], seeds=[42], example_rows=10),
        discovery_llm=LLMConfig(request_limit=50), generation_llm=LLMConfig(request_limit=100),
        generation=GenerationConfig(n_samples=[10, 30], batch_size=7, max_workers=max_workers),
        evaluation=EvaluationConfig(model=model), output_dir=str(output),
    )
    atomic_json(output / "demo_config.json", config.to_dict())
    return run_experiments(config, client_factory=demo_factory, backend="offline-demo", resume=resume)
