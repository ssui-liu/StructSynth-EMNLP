"""Execute split → graph induction → synthesis → evaluation with verified recovery."""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Callable

import pandas as pd

from ..artifacts import atomic_csv, atomic_json, file_hash, fingerprint, file_lock, frame_records
from ..config import ExperimentConfig
from ..data import infer_training_schema, load_dataset, sample_examples, split_dataset
from ..generation import GraphSynthesizer
from ..llm import OpenAICompatibleClient, UsageLedger
from ..structure import DependencyGraph, discover_structure
from .evaluation import evaluate_baseline, evaluate_run
from .identity import experiment_dir, experiment_identity


def _now():
    return datetime.now(timezone.utc).isoformat()


def _artifact_hashes(directory, filenames):
    return {name: file_hash(directory / name) for name in filenames}


def _verify_artifacts(directory, artifacts):
    for name, digest in artifacts.items():
        path = directory / name
        if not path.is_file() or file_hash(path) != digest:
            raise ValueError(f"Run artifact missing or modified: {path}")


def run_experiment(config: ExperimentConfig, shot: int, seed: int, *, stage="all", resume=False,
                   client_factory: Callable | None = None, backend="live"):
    """Run one configuration. Resume verifies inputs, code and completed artifacts.

    A client factory receives (stage_name, llm_config, ledger, train, spec).
    The test holdout is deliberately not exposed to either model client.
    """
    if stage not in {"all", "split", "discover", "generate", "evaluate"}:
        raise ValueError(f"Unknown stage: {stage}")
    if stage == "evaluate" and not config.evaluation.enabled:
        raise ValueError("Explicit evaluation requires evaluation.enabled=true")
    identity = experiment_identity(config, shot, seed, backend=backend)
    directory = experiment_dir(config, identity)
    directory.mkdir(parents=True, exist_ok=True)
    lock = file_lock(directory / ".run.lock")
    lock.__enter__()
    manifest_path = directory / "manifest.json"
    try:
        if manifest_path.exists():
            if not resume:
                raise FileExistsError(f"Run exists: {directory}. Use --resume to verify and continue it.")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest["identity"] != identity:
                raise ValueError("Run identity differs from configuration, data, code or backend")
            _verify_artifacts(directory, manifest.get("artifacts", {}))
            for name in manifest.get("started_request_stages", []):
                if not (directory / f"{name}_requests.jsonl").is_file():
                    raise ValueError(f"Request ledger missing for started stage: {name}; cannot recover its budget")
            for name, watermark in manifest.get("ledger_watermarks", {}).items():
                path = directory / f"{name}_requests.jsonl"
                if (path.stat().st_size < watermark["size"] or
                        file_hash(path, length=watermark["size"]) != watermark["sha256"]):
                    raise ValueError(f"Request ledger truncated or modified: {name}; cannot recover its budget")
        else:
            manifest = {"identity": identity, "run_id": fingerprint(identity), "created": _now(),
                        "requested_grid": {"shots": config.data.shots, "seeds": config.data.seeds},
                        "status": "running", "completed_stages": [], "started_request_stages": [], "artifacts": {}}
        atomic_json(manifest_path, manifest)
        try:
            frame, base_spec = load_dataset(config.data.path, config.data.metadata,
                                           task_type=config.data.task_type, target_column=config.data.target_column,
                                           cleaning=config.data.cleaning)
            base_spec = replace(base_spec, name=config.data.name)
            split = split_dataset(frame, base_spec, shot=shot, seed=seed, test_size=config.data.test_size)
            train, test = split.train, split.test
            spec = infer_training_schema(train, base_spec)
            examples = sample_examples(train, spec, n=config.data.example_rows, seed=seed)
            def done(name, filenames):
                if name not in manifest["completed_stages"]:
                    manifest["completed_stages"].append(name)
                manifest["artifacts"].update(_artifact_hashes(directory, filenames))
                manifest.update(status="running", updated=_now())
                manifest.pop("error", None)
                atomic_json(manifest_path, manifest)

            if "split" not in manifest["completed_stages"]:
                atomic_csv(directory / "train.csv", train)
                atomic_csv(directory / "test.csv", test)
                atomic_csv(directory / "examples.csv", examples)
                atomic_json(directory / "split.json", split.metadata)
                atomic_json(directory / "schema.json", spec.to_dict())
                done("split", ["train.csv", "test.csv", "examples.csv", "split.json", "schema.json"])
            else:
                # Verify deterministic reconstruction against the frozen split,
                # before giving training rows to any model or evaluating them.
                if split.metadata != json.loads((directory / "split.json").read_text()):
                    raise ValueError("Reconstructed split differs from its frozen manifest")
                if spec.to_dict() != json.loads((directory / "schema.json").read_text()):
                    raise ValueError("Reconstructed training schema differs from its frozen manifest")
                if examples.to_csv(index=False).encode("utf-8") != (directory / "examples.csv").read_bytes():
                    raise ValueError("Prompt examples differ from the frozen run")
            if stage == "split":
                return directory

            if config.evaluation.enabled and "real_baseline.json" not in manifest["artifacts"]:
                # An actual local fit validates model parameters and data before
                # paid requests; constructors alone defer many checks to fit().
                baseline = evaluate_baseline(train, test, spec, config, seed)
                atomic_json(directory / "real_baseline.json", baseline)
                manifest["artifacts"].update(_artifact_hashes(directory, ["real_baseline.json"]))
                atomic_json(manifest_path, manifest)

            def client(name, llm_config):
                path = directory / f"{name}_requests.jsonl"
                if name not in manifest["started_request_stages"]:
                    path.touch(exist_ok=True)
                    manifest["started_request_stages"].append(name)
                    atomic_json(manifest_path, manifest)
                ledger = UsageLedger(path)
                if client_factory:
                    return client_factory(name, llm_config, ledger, train.copy(), spec)
                return OpenAICompatibleClient(llm_config, ledger=ledger)

            if "discover" not in manifest["completed_stages"]:
                if stage in {"generate", "evaluate"}:
                    raise FileNotFoundError("Discover a graph first (structsynth discover, or structsynth run)")
                model = client("discovery", config.discovery_llm)
                result = discover_structure(train, spec, model, examples=examples,
                                            max_response_attempts=config.discovery_attempts,
                                            max_cycles=config.max_cycles)
                atomic_json(directory / "graph.json", result.graph.to_dict())
                atomic_json(directory / "discovery_events.json", result.events)
                done("discover", ["graph.json", "discovery_events.json", "discovery_requests.jsonl"])
            if stage == "discover":
                return directory
            graph = DependencyGraph.from_dict(json.loads((directory / "graph.json").read_text()), columns=spec.columns)
            if "generate" not in manifest["completed_stages"]:
                if stage == "evaluate":
                    raise FileNotFoundError("Generate synthetic records before evaluation")
                generator = GraphSynthesizer(graph, spec, client("generation", config.generation_llm),
                                            batch_size=config.generation.batch_size,
                                            max_attempts=config.generation.max_attempts,
                                            max_workers=config.generation.max_workers, seed=seed,
                                            checkpoint_dir=directory / "checkpoints")
                generator.fit(train, examples=examples)
                try:
                    synthetic = generator.generate(max(config.generation.n_samples))
                except Exception as exc:
                    exc.events = list(generator.events)
                    raise
                atomic_csv(directory / "synthetic.csv", synthetic)
                # JSON preserves string categories such as "001" on resume.
                atomic_json(directory / "synthetic.json", frame_records(synthetic))
                atomic_json(directory / "generation_events.json", generator.events)
                done("generate", ["synthetic.csv", "synthetic.json", "generation_events.json", "generation_requests.jsonl"])
            else:
                synthetic = pd.DataFrame(json.loads((directory / "synthetic.json").read_text()), columns=spec.columns)
            if stage == "generate":
                return directory
            if config.evaluation.enabled and "evaluate" not in manifest["completed_stages"]:
                evaluate_run(directory, train, test, synthetic, spec, config, seed)
                filenames = ["metrics.json"] + [f"n{n}/{name}" for n in config.generation.n_samples
                                                for name in ("metrics.json", "synthetic.csv")]
                done("evaluate", filenames)
            manifest.update(status="complete", updated=_now())
            atomic_json(manifest_path, manifest)
            return directory
        except Exception as exc:
            if hasattr(exc, "events"):
                diagnostic = {"events": exc.events, "error": str(exc)}
                partial = getattr(exc, "partial_graph", None)
                if partial is not None:
                    diagnostic["partial_graph"] = partial.to_dict() if hasattr(partial, "to_dict") else partial
                atomic_json(directory / "failure_details.json", diagnostic)
            manifest.update(status="failed", updated=_now(), error={"type": type(exc).__name__, "message": str(exc)})
            atomic_json(manifest_path, manifest)
            raise
        finally:
            usage = {name: UsageLedger(directory / f"{name}_requests.jsonl").summary()
                     for name in ("discovery", "generation")}
            atomic_json(directory / "usage.json", usage)
            # A journal may append after a crash, but cannot lose the durable
            # prefix known at the last orderly return/failure.
            manifest["ledger_watermarks"] = {
                name: {"size": (directory / f"{name}_requests.jsonl").stat().st_size,
                       "sha256": file_hash(directory / f"{name}_requests.jsonl")}
                for name in manifest["started_request_stages"]}
            atomic_json(manifest_path, manifest)
    finally:
        lock.__exit__(None, None, None)


def run_experiments(config, **kwargs):
    backend = kwargs.get("backend", "live")
    planned = [experiment_dir(config, experiment_identity(config, shot, seed, backend=backend))
               for shot in config.data.shots for seed in config.data.seeds]

    def report():
        if kwargs.get("stage", "all") not in {"all", "evaluate"} or not config.evaluation.enabled:
            return
        from ..evaluation.reporting import write_summary
        existing = [path for path in planned if (path / "manifest.json").is_file()]
        if existing:
            target = Path(config.output_dir) / "summaries" / fingerprint(sorted(path.name for path in planned))[:16]
            write_summary(existing, target)

    results = []
    try:
        for shot in config.data.shots:
            for seed in config.data.seeds:
                results.append(run_experiment(config, shot, seed, **kwargs))
    except Exception:
        try:
            report()
        except Exception:
            logging.getLogger(__name__).exception("Could not summarize the interrupted experiment grid")
        raise
    report()
    return results
