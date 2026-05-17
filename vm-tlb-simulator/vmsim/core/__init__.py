"""Convenience re-exports — use `from vmsim.core import ...`."""
from .address import (
    PAGE_SHIFT,
    PAGE_SIZE,
    PAGE_MASK,
    LEVELS,
    BITS_PER_LEVEL,
    ENTRIES_PER_TABLE,
    VIRTUAL_ADDRESS_BITS,
    VirtualAddress,
    PhysicalAddress,
)
from .pte import PTE
from .frame import PhysicalMemory, OutOfMemoryError
from .trace import TraceStep, Trace
from .interfaces import Translator, ReplacementPolicy

__all__ = [
    "PAGE_SHIFT", "PAGE_SIZE", "PAGE_MASK",
    "LEVELS", "BITS_PER_LEVEL", "ENTRIES_PER_TABLE", "VIRTUAL_ADDRESS_BITS",
    "VirtualAddress", "PhysicalAddress",
    "PTE",
    "PhysicalMemory", "OutOfMemoryError",
    "TraceStep", "Trace",
    "Translator", "ReplacementPolicy",
]
