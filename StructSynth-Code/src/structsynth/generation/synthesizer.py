"""Fit and orchestrate bounded, resumable graph-planned generation."""

from __future__ import annotations

import json
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import List, Optional

import pandas as pd

from ..llm import LLMResponseError, LLMTransportError
from .checkpoints import checkpoint_lock, load_batch_state, new_state, prepare_manifest, save_state
from .errors import GenerationError
from .planning import build_stages
from .prompts import build_request, last_feedback
from .serialization import canonical_json, digest, records
from .validation import assemble, infer_schema, validate_response, value_error


class GraphSynthesizer:
    """Generate exact-size tables in DAG order using a shared metered client.

    ``fit`` reads only training data. ``examples`` must be training records;
    omitting it uses the supplied training frame. Parallel requests require a
    thread-safe client. The shared client owns all token and HTTP accounting.
    """

    def __init__(self, graph, spec, client, *, batch_size=10, max_attempts=5,
                 seed=42, checkpoint_dir=None, max_workers=1):
        for name, value in (("batch_size", batch_size), ("max_attempts", max_attempts),
                            ("max_workers", max_workers)):
            if type(value) is not int or value < 1:
                raise ValueError("%s must be a positive integer" % name)
        if type(seed) is not int:
            raise ValueError("seed must be an integer")
        self.graph = graph
        self.spec = spec
        self.client = client
        self.batch_size = batch_size
        self.max_attempts = max_attempts
        self.seed = seed
        self.checkpoint_dir = Path(checkpoint_dir) if checkpoint_dir is not None else None
        self.max_workers = max_workers
        self.events: List[dict] = []
        self._event_lock = threading.Lock()
        self._run_lock = threading.Lock()
        self._fitted = False

    def fit(self, train: pd.DataFrame, examples: Optional[pd.DataFrame] = None):
        """Validate training-only types/categories and select prompt examples."""
        if not self._run_lock.acquire(blocking=False):
            raise GenerationError("Cannot fit while this generator is running")
        try:
            self._fitted = False
            columns = list(self.spec.columns)
            if not columns or len(columns) != len(set(columns)):
                raise ValueError("Dataset columns must be nonempty and unique")
            if any(not isinstance(column, str) or not column for column in columns):
                raise ValueError("Dataset column names must be nonempty strings")
            if list(train.columns) != columns or train.empty:
                raise ValueError("Training data must be nonempty and match DatasetSpec column order")
            examples = train if examples is None else examples
            if list(examples.columns) != columns or examples.empty:
                raise ValueError("Examples must be nonempty and match the training columns")
            train_records = records(train)
            self._example_records = records(examples)
            train_rows = Counter(canonical_json(row) for row in train_records)
            example_rows = Counter(canonical_json(row) for row in self._example_records)
            if any(count > train_rows[row] for row, count in example_rows.items()):
                raise ValueError("Few-shot examples must be a subset of the supplied training records")
            self._columns = columns
            self._field_schema = infer_schema(train, train_records, spec=self.spec, columns=self._columns)
            for row in train_records:
                for column, value in row.items():
                    error = value_error(self._field_schema, column, value)
                    if error:
                        raise ValueError("Invalid training value: %s" % error)
            self._train_fingerprint = digest(train_records)
            self._spec_snapshot = json.loads(canonical_json(asdict(self.spec) if is_dataclass(self.spec) else vars(self.spec)))
            self._graph_snapshot = json.loads(canonical_json(self.graph.to_dict()))
            self._stages = build_stages(self.graph, self._columns)
            self._fitted = True
            return self
        finally:
            self._run_lock.release()

    def generate(self, n_samples: int) -> pd.DataFrame:
        """Return exactly ``n_samples`` complete rows, or raise with checkpoints."""
        if not self._fitted:
            raise GenerationError("Call fit() with training data before generate()")
        current_spec = asdict(self.spec) if is_dataclass(self.spec) else vars(self.spec)
        if current_spec != self._spec_snapshot or self.graph.to_dict() != self._graph_snapshot:
            raise GenerationError("Graph or DatasetSpec changed after fit(); fit again before generation")
        if type(n_samples) is not int or n_samples < 0:
            raise ValueError("n_samples must be a nonnegative integer")
        if not self._run_lock.acquire(blocking=False):
            raise GenerationError("This generator is already running")
        try:
            self.events = []
            with checkpoint_lock(self.checkpoint_dir):
                fingerprint = prepare_manifest(
                    self.checkpoint_dir, n_samples=n_samples, batch_size=self.batch_size,
                    max_attempts=self.max_attempts, seed=self.seed, field_schema=self._field_schema,
                    spec_snapshot=self._spec_snapshot, graph_snapshot=self._graph_snapshot,
                    client=self.client, train_fingerprint=self._train_fingerprint,
                    example_records=self._example_records)
                rows = {row_id: {} for row_id in range(n_samples)}
                for stage_index, stage in enumerate(self._stages):
                    batches = [list(range(start, min(start + self.batch_size, n_samples)))
                               for start in range(0, n_samples, self.batch_size)]
                    if self.max_workers == 1:
                        for batch_index, ids in enumerate(batches):
                            generated = self._generate_batch(stage_index, stage, batch_index, ids,
                                                             rows, fingerprint)
                            for row_id, values in generated.items():
                                rows[row_id].update(values)
                    else:
                        self._parallel_stage(stage_index, stage, batches, rows, fingerprint)
                return assemble(rows, self._columns, self._field_schema)
        finally:
            self._run_lock.release()

    def _parallel_stage(self, stage_index, stage, batches, rows, fingerprint):
        # Workers receive immutable stage context; only the caller merges values.
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            pending = {}
            iterator = iter(enumerate(batches))
            for _ in range(min(self.max_workers, len(batches))):
                batch_index, ids = next(iterator)
                future = executor.submit(self._generate_batch, stage_index, stage, batch_index,
                                         ids, rows, fingerprint)
                pending[future] = batch_index
            try:
                while pending:
                    future = next(as_completed(pending))
                    pending.pop(future)
                    generated = future.result()
                    for row_id, values in generated.items():
                        rows[row_id].update(values)
                    try:
                        batch_index, ids = next(iterator)
                    except StopIteration:
                        continue
                    future = executor.submit(self._generate_batch, stage_index, stage, batch_index,
                                             ids, rows, fingerprint)
                    pending[future] = batch_index
            except BaseException:
                # Already-running independent batches can finish and checkpoint.
                # Do not submit the remaining batches after a failure.
                for future in pending:
                    future.cancel()
                raise

    def _generate_batch(self, stage_index, stage, batch_index, ids, rows, fingerprint):
        context = [{"row_id": row_id, "values": dict(rows[row_id])} for row_id in ids]
        state = new_state(stage_index, batch_index, ids, context, fingerprint)
        path = (self.checkpoint_dir / ("stage_%03d_batch_%06d.json" % (stage_index, batch_index))
                if self.checkpoint_dir is not None else None)
        state, accepted, resumed = load_batch_state(
            path, state, max_attempts=self.max_attempts, ids=ids,
            variables=stage["variables"], field_schema=self._field_schema)
        if resumed:
            with self._event_lock:
                self.events.extend(state["events"])
            self._event(state, "checkpoint_resumed", accepted_row_ids=sorted(accepted))
        if state["completed"]:
            return accepted
        context_by_id = {row["row_id"]: row for row in context}
        feedback = last_feedback(state)
        while len(accepted) < len(ids) and state["attempts"] < self.max_attempts:
            pending_ids = [row_id for row_id in ids if row_id not in accepted]
            state["attempts"] += 1
            request = build_request(
                stage_index, stage, batch_index, pending_ids, context_by_id,
                state["attempts"], feedback, fingerprint, example_records=self._example_records,
                field_schema=self._field_schema, descriptions=self.spec.descriptions,
                columns=self._columns, task=self.spec.task, seed=self.seed)
            self._event(state, "request_started", requested_row_ids=pending_ids,
                        request_id=request.request_id)
            save_state(path, state, accepted)
            try:
                response = self.client.complete(request)
            except (LLMResponseError, LLMTransportError) as error:
                feedback = ["%s: %s" % (type(error).__name__, error)]
                self._event(state, "request_failed", validation_errors=feedback)
                save_state(path, state, accepted)
                continue
            valid, feedback = validate_response(response.content, pending_ids, stage["variables"],
                                                field_schema=self._field_schema)
            accepted.update(valid)
            missing = [row_id for row_id in pending_ids if row_id not in valid]
            if missing:
                feedback.append("Missing or invalid requested row_ids: %s" % missing)
            self._event(state, "response_validated", accepted_row_ids=sorted(valid),
                        validation_errors=feedback)
            state["completed"] = len(accepted) == len(ids)
            save_state(path, state, accepted)
        if not state["completed"]:
            missing = [row_id for row_id in ids if row_id not in accepted]
            raise GenerationError("Generation exhausted %s attempts at stage %s, batch %s; pending row_ids=%s. %s" %
                                  (self.max_attempts, stage_index, batch_index, missing, "; ".join(feedback)),
                                  stage_index=stage_index, batch_index=batch_index, row_ids=missing)
        return accepted

    def _event(self, state, kind, **fields):
        event = {"kind": kind, "stage_index": state["stage_index"],
                 "batch_index": state["batch_index"], "attempt": state["attempts"], **fields}
        state["events"].append(event)
        with self._event_lock:
            self.events.append(event)
