"""Page faults and swap."""
from .handler import PageFaultHandler
from .swap import SwapArea

__all__ = ["PageFaultHandler", "SwapArea"]
