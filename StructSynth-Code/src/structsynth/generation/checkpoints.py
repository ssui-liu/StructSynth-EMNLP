"""Atomic checkpoint storage, run fingerprints and restored batch validation."""

from __future__ import annotations

import json
import os
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Optional

from .errors import CheckpointError
from .prompts import PROMPT_VERSION
from .serialization import canonical_json, digest
from .validation import validate_response


CHECKPOINT_VERSION = 1


def atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_name(path.name + ".%s.%s.tmp" % (os.getpid(), threading.get_ident()))
    try:
        with temporary.open("w", encoding="utf-8") as handle:
            handle.write(canonical_json(value))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(str(temporary), str(path))
    finally:
        if temporary.exists():
            temporary.unlink()


@contextmanager
def checkpoint_lock(directory: Optional[Path]):
    """An OS lock is released after a crash, unlike an exclusive sentinel file."""
    if directory is None:
        yield
        return
    directory.mkdir(parents=True, exist_ok=True)
    handle = (directory / ".generation.lock").open("a+")
    locked = False
    try:
        if os.name == "nt":
            import msvcrt
            handle.seek(0)
            handle.write("0")
            handle.flush()
            handle.seek(0)
            try:
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as error:
                raise CheckpointError("Checkpoint directory is in use by another generator") from error
        else:
            import fcntl
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as error:
                raise CheckpointError("Checkpoint directory is in use by another generator") from error
        locked = True
        yield
    finally:
        if locked:
            if os.name == "nt":
                import msvcrt
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def prepare_manifest(checkpoint_dir, *, n_samples, batch_size, max_attempts, seed, field_schema,
                     spec_snapshot, graph_snapshot, client, train_fingerprint, example_records):
    identity = getattr(client, "identity", None)
    if identity is None:
        identity = {"unknown_client_class": "%s.%s" %
                    (type(client).__module__, type(client).__qualname__)}
    manifest = {"version": CHECKPOINT_VERSION, "prompt_version": PROMPT_VERSION,
                "n_samples": n_samples, "batch_size": batch_size,
                "max_attempts": max_attempts, "seed": seed,
                "schema": field_schema, "dataset_spec": spec_snapshot,
                "graph": graph_snapshot, "client": identity,
                "train_sha256": train_fingerprint,
                "examples_sha256": digest(example_records)}
    fingerprint = digest(manifest)
    if checkpoint_dir is not None:
        path = checkpoint_dir / "manifest.json"
        if path.exists():
            saved = read_checkpoint(path)
            if saved != {"fingerprint": fingerprint, "run": manifest}:
                raise CheckpointError("Checkpoint input/configuration mismatch; use a new checkpoint directory")
        else:
            if any(checkpoint_dir.glob("stage_*.json")):
                raise CheckpointError("Batch checkpoints exist without a run manifest")
            atomic_json(path, {"fingerprint": fingerprint, "run": manifest})
    return fingerprint


def read_checkpoint(path):
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (ValueError, OSError) as error:
        raise CheckpointError("Cannot read checkpoint %s: %s" % (path, error)) from error


def new_state(stage_index, batch_index, ids, context, fingerprint):
    return {"version": CHECKPOINT_VERSION, "fingerprint": fingerprint,
            "stage_index": stage_index, "batch_index": batch_index, "row_ids": ids,
            "context_sha256": digest(context), "attempts": 0, "rows": [],
            "events": [], "completed": False}


def load_batch_state(path, state, *, max_attempts, ids, variables, field_schema):
    """Return validated state, accepted rows and whether a checkpoint existed."""
    if path is None or not path.exists():
        return state, {}, False
    saved = read_checkpoint(path)
    fixed = ("version", "fingerprint", "stage_index", "batch_index", "row_ids", "context_sha256")
    if not isinstance(saved, dict) or any(saved.get(key) != state[key] for key in fixed):
        raise CheckpointError("Batch checkpoint identity/context mismatch: %s" % path)
    attempts = saved.get("attempts")
    if type(attempts) is not int or not 0 <= attempts <= max_attempts:
        raise CheckpointError("Invalid attempt count in %s" % path)
    accepted, errors = validate_response({"rows": saved.get("rows")}, ids, variables, field_schema=field_schema)
    if errors or type(saved.get("completed")) is not bool or saved["completed"] != (len(accepted) == len(ids)):
        raise CheckpointError("Invalid saved generated rows/status in %s" % path)
    if not isinstance(saved.get("events"), list) or any(not isinstance(e, dict) for e in saved["events"]):
        raise CheckpointError("Invalid event history in %s" % path)
    return saved, accepted, True


def save_state(path, state, accepted):
    state["rows"] = [{"row_id": row_id, "values": accepted[row_id]} for row_id in sorted(accepted)]
    if path is not None:
        atomic_json(path, state)
