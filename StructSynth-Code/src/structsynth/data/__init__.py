"""Dataset loading, training metadata, and reproducible sampling.

The public imports from ``structsynth.data`` remain available; implementation
modules separate file loading, validation, metadata, and sampling.
"""
from .loading import load_dataset
from .metadata import infer_training_schema, training_metadata
from .sampling import DataSplit, sample_examples, split_dataset

__all__ = [
    "DataSplit",
    "infer_training_schema",
    "load_dataset",
    "sample_examples",
    "split_dataset",
    "training_metadata",
]
