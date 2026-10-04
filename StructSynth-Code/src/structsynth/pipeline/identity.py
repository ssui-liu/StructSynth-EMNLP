"""Content identities and output locations for individual experiments."""
from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import platform
import re

from ..artifacts import file_hash, fingerprint
from ..config import ExperimentConfig


def source_fingerprint():
    """Hash all package source files using paths relative to the package root.

    Recursive paths cover child packages and distinguish repeated names such as
    ``__init__.py``; installation location and bytecode caches do not participate.
    """
    package = Path(__file__).resolve().parents[1]
    return fingerprint({p.relative_to(package).as_posix(): file_hash(p)
                        for p in sorted(package.rglob("*.py"))})


def experiment_identity(config, shot, seed, *, backend="live"):
    values = config.to_dict()
    values.pop("output_dir")
    # The invocation's grid is not an input to an individual experiment.
    # Selecting one seed for recovery must resolve to the original run.
    values["data"].pop("shots")
    values["data"].pop("seeds")
    environment = {"python": platform.python_version(),
                   **{name: version(name) for name in ("numpy", "pandas", "scipy", "networkx", "scikit-learn", "PyYAML")}}
    if config.evaluation.model == "xgboost":
        try:
            environment["xgboost"] = version("xgboost")
        except PackageNotFoundError:
            environment["xgboost"] = None
    return {
        "config": values, "shot": int(shot), "seed": int(seed), "backend": backend,
        "data_sha256": file_hash(config.data.path),
        "metadata_sha256": file_hash(config.data.metadata),
        "source_sha256": source_fingerprint(), "artifact_schema": 1,
        "environment": environment,
    }


def experiment_dir(config, identity):
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", config.data.name).strip(".") or "dataset"
    return (Path(config.output_dir) / name / f"{identity['shot']}_shot" /
            f"seed_{identity['seed']}" / fingerprint(identity)[:16])


def plan_experiments(config: ExperimentConfig, *, backend="live"):
    return [{"shot": shot, "seed": seed,
             "run_dir": str(experiment_dir(config, experiment_identity(config, shot, seed, backend=backend))),
             "maximum_synthetic_rows": max(config.generation.n_samples),
             "request_limit": config.discovery_llm.request_limit + config.generation_llm.request_limit}
            for shot in config.data.shots for seed in config.data.seeds]
