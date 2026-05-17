"""Paging module — single-level and multi-level page tables."""
from .single_level import SingleLevelPageTable, PageFault
from .multi_level import MultiLevelPageTable

__all__ = ["SingleLevelPageTable", "MultiLevelPageTable", "PageFault"]
