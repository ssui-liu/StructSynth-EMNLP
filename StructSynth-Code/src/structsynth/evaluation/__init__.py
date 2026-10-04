"""Paper-aligned downstream utility, privacy, and statistical fidelity.

These exports preserve the public ``structsynth.evaluation`` API. Individual
metric implementations and preprocessing live in the corresponding submodules.
"""
from .downstream import PAPER_XGBOOST_PARAMS, evaluate_downstream
from .fidelity import evaluate_fidelity
from .preprocessing import TrainingPreprocessor
from .privacy import evaluate_privacy

__all__ = [
    "PAPER_XGBOOST_PARAMS",
    "TrainingPreprocessor",
    "evaluate_downstream",
    "evaluate_fidelity",
    "evaluate_privacy",
]
