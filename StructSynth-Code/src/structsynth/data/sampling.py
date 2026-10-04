"""Held-out splits and reproducible training/prompt sampling."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from ..schema import DatasetSpec
from .metadata import training_metadata
from .validation import _check_frame


@dataclass
class DataSplit:
    train: pd.DataFrame
    test: pd.DataFrame
    unused: pd.DataFrame
    metadata: dict[str, Any]


def _classification_sample(
    frame: pd.DataFrame, target: str, n: int, rng: np.random.Generator, *, balanced: bool,
) -> np.ndarray:
    groups = [np.flatnonzero((frame[target] == label).to_numpy()) for label in pd.unique(frame[target])]
    classes = len(groups)
    if n < classes:
        raise ValueError(f"Requested {n} examples, but classification requires at least {classes} to cover every class")
    capacities = np.array([len(group) for group in groups])
    counts = np.ones(classes, dtype=int)
    priorities = rng.permutation(classes)
    rank = np.empty(classes, dtype=int)
    rank[priorities] = np.arange(classes)
    if balanced:
        # Water filling redistributes unused minority-class quota without replacement.
        while counts.sum() < n:
            candidates = np.flatnonzero(counts < capacities)
            chosen = min(candidates, key=lambda i: (counts[i], rank[i]))
            counts[chosen] += 1
    else:
        ideal = n * capacities / capacities.sum()
        while counts.sum() < n:
            candidates = np.flatnonzero(counts < capacities)
            chosen = min(candidates, key=lambda i: (counts[i] - ideal[i], rank[i]))
            counts[chosen] += 1
    selected = np.concatenate([rng.choice(group, size=int(count), replace=False) for group, count in zip(groups, counts)])
    rng.shuffle(selected)
    return selected


def sample_examples(
    train: pd.DataFrame, spec: DatasetSpec, *, n: int = 20, seed: int = 42, balanced: bool = True,
) -> pd.DataFrame:
    """Sample prompt examples without replacement or global RNG side effects.

    Classification prompts use equal class quotas where capacity permits;
    regression prompts use uniform sampling. ``n`` is capped at available rows.
    """
    _check_frame(train, spec)
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or n <= 0:
        raise ValueError("n must be a positive integer")
    n = min(n, len(train))
    rng = np.random.default_rng(seed)
    if spec.task_type == "classification":
        positions = _classification_sample(train, spec.target_column, n, rng, balanced=balanced)
    else:
        positions = rng.choice(len(train), size=n, replace=False)
    return train.iloc[positions].copy().reset_index(drop=True)


def split_dataset(
    frame: pd.DataFrame, spec: DatasetSpec, *, shot: int, seed: int, test_size: float = 0.2,
) -> DataSplit:
    """Hold out test first, then subsample the limited real training set.

    Classification holdout is stratified; its training subsample is proportional
    with at least one instance per class. Remaining rows are ``unused`` and must
    never enter graph discovery, synthesis, training metadata, or evaluation fit.
    """
    _check_frame(frame, spec)
    if isinstance(shot, bool) or not isinstance(shot, (int, np.integer)) or shot <= 0:
        raise ValueError("shot must be a positive integer")
    if not isinstance(test_size, (float, int)) or isinstance(test_size, bool) or not 0 < test_size < 1:
        raise ValueError("test_size must be a fraction strictly between 0 and 1")
    frame = frame.reset_index(drop=True)
    positions = np.arange(len(frame))
    stratify = frame[spec.target_column] if spec.task_type == "classification" else None
    try:
        full_train, test_positions = train_test_split(positions, test_size=test_size, random_state=seed, stratify=stratify)
    except ValueError as exc:
        raise ValueError(f"Cannot create requested holdout split: {exc}") from exc
    if shot > len(full_train):
        raise ValueError(f"shot={shot} exceeds available training rows ({len(full_train)}) after holdout")
    rng = np.random.default_rng(seed)
    if spec.task_type == "classification":
        local = _classification_sample(frame.iloc[full_train], spec.target_column, shot, rng, balanced=False)
        train_positions = full_train[local]
    else:
        train_positions = rng.choice(full_train, size=shot, replace=False)
    unused_positions = full_train[~np.isin(full_train, train_positions)]
    train = frame.iloc[train_positions].copy().reset_index(drop=True)
    fingerprint = hashlib.sha256(frame.to_csv(index=False).encode("utf-8")).hexdigest()
    metadata = {
        "split_version": "holdout_then_limited_v1", "seed": int(seed), "test_size": float(test_size),
        "shot": int(shot), "total_rows": len(frame), "train_full_rows": len(full_train),
        "train_rows": len(train), "test_rows": len(test_positions), "unused_rows": len(unused_positions),
        "stratified": spec.task_type == "classification", "data_sha256": fingerprint,
        "source_row_positions": {"train": train_positions.tolist(), "test": test_positions.tolist(), "unused": unused_positions.tolist()},
        "training_schema": training_metadata(train, spec),
    }
    return DataSplit(train, frame.iloc[test_positions].copy().reset_index(drop=True),
                     frame.iloc[unused_positions].copy().reset_index(drop=True), metadata)
