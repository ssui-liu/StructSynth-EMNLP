"""Local baseline validation and per-size evaluation artifacts."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..artifacts import atomic_csv, atomic_json
from ..evaluation import evaluate_downstream, evaluate_fidelity, evaluate_privacy


def evaluate_baseline(train, test, spec, config, seed):
    """Fit the real-only baseline before any paid model stage."""
    for name, data in (("train", train), ("test", test)):
        if not np.isfinite(data[spec.numeric_columns].to_numpy(dtype=float)).all():
            raise ValueError(f"Paper privacy/fidelity metrics require finite numeric {name} values")
    return evaluate_downstream(train, train.iloc[:0], test, spec, protocol="real_only",
                               seed=seed, model=config.evaluation.model,
                               model_params=config.evaluation.model_params)


def evaluate_run(directory, train, test, synthetic, spec, config, seed):
    results = {}
    if config.evaluation.fidelity_reference == "train_test":
        reference = pd.concat([train, test], ignore_index=True)
    elif config.evaluation.fidelity_reference == "test":
        reference = test
    else:
        reference = train
    for n_samples in sorted(config.generation.n_samples):
        subset = synthetic.iloc[:n_samples].copy()
        if len(subset) != n_samples:
            raise ValueError(f"Expected {n_samples} synthetic records, found {len(subset)}")
        target = directory / f"n{n_samples}"
        atomic_csv(target / "synthetic.csv", subset)
        metrics = {
            "n_samples": n_samples, "seed": seed,
            "downstream": evaluate_downstream(train, subset, test, spec, protocol=config.evaluation.protocol,
                                               seed=seed, model=config.evaluation.model,
                                               model_params=config.evaluation.model_params),
            "privacy": evaluate_privacy(subset, train, test, spec, seed=seed,
                                         numeric_scaling=config.evaluation.numeric_scaling),
            "fidelity": evaluate_fidelity(reference, subset, spec),
            "fidelity_reference": config.evaluation.fidelity_reference,
        }
        atomic_json(target / "metrics.json", metrics)
        results[str(n_samples)] = metrics
    atomic_json(directory / "metrics.json", results)
    return results
