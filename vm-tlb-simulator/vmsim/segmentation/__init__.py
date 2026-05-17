"""Segmentation module — logical -> linear address translation."""
from .segments import (
    Segment,
    SegmentTable,
    SegmentationFault,
    make_default_segment_table,
    SELECTOR_BITS,
    SELECTOR_SHIFT,
    SELECTOR_MASK,
    OFFSET_MASK,
)

__all__ = [
    "Segment",
    "SegmentTable",
    "SegmentationFault",
    "make_default_segment_table",
    "SELECTOR_BITS",
    "SELECTOR_SHIFT",
    "SELECTOR_MASK",
    "OFFSET_MASK",
]
