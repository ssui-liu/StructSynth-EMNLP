"""Compatibility imports; implementation lives in :mod:`structsynth.structure.discovery`."""

from .structure.discovery import (
    DiscoveryError,
    DiscoveryResult,
    discover_structure,
    SOURCE_SYSTEM,
    SUCCESSORS_SYSTEM,
    CYCLE_SYSTEM,
)

__all__ = ['DiscoveryError', 'DiscoveryResult', 'discover_structure', 'SOURCE_SYSTEM', 'SUCCESSORS_SYSTEM', 'CYCLE_SYSTEM']
