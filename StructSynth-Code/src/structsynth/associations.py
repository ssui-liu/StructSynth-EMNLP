"""Compatibility imports; implementation lives in :mod:`structsynth.structure.associations`."""

from .structure.associations import (
    AssociationScore,
    categorical_features,
    association_score,
    association_evidence,
    association_matrix,
)

__all__ = ['AssociationScore', 'categorical_features', 'association_score', 'association_evidence', 'association_matrix']
