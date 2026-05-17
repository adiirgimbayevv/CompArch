"""
Multi-level page table (x86-64 style).

4 levels, 9 bits each (LEVELS, BITS_PER_LEVEL in vmsim.core).
Each level is a sparse dict[index -> next_level_or_PTE].
Walk the tree top-down using VirtualAddress.multi_level_indices().

Why bother with multi-level when single-level works?
  -> Memory: single-level for 48-bit VA needs 2^36 entries.
     Multi-level only allocates tables for ranges that are actually used.
  -> This is what real x86-64 does.

Owner: Person 3.
TODO: implement methods marked `raise NotImplementedError`.

Reference: see segmentation/segments.py for project style.
"""
from vmsim.core import (
    PTE,
    PhysicalMemory,
    TraceStep,
    Trace,
    Translator,
    VirtualAddress,
    LEVELS,
    ENTRIES_PER_TABLE,
    PAGE_SHIFT,
    PAGE_MASK,
)
from vmsim.paging.single_level import PageFault


# A tree node: dict mapping index (0..ENTRIES_PER_TABLE-1) to
# either another dict (internal level) or a PTE (leaf level).
PageTableNode = dict


class MultiLevelPageTable(Translator):
    """4-level page table walked top-down (PGD -> PUD -> PMD -> PT).

    Use ENTRIES_PER_TABLE and LEVELS from vmsim.core — don't hardcode.
    """

    def __init__(
        self,
        physical_memory: PhysicalMemory,
        levels: int = LEVELS,
    ) -> None:
        self.memory = physical_memory
        self.levels = levels
        self._root: PageTableNode = {}
        self._intermediate_tables_allocated = 1  # for memory-overhead stats

    def map(self, vpn: int, pte: PTE) -> None:
        """Install a PTE for this VPN.

        Walks/allocates intermediate tables along the way.
        Use VirtualAddress(vpn << PAGE_SHIFT).multi_level_indices()
        to get the per-level indices.
        """
        # TODO Person 3: walk from self._root, creating empty dicts at
        # each missing intermediate level, store pte at the leaf.
        # Increment self._intermediate_tables_allocated when you create
        # a new intermediate dict (good for the overhead experiment).
        raise NotImplementedError("Person 3: implement map()")

    def lookup(self, vpn: int) -> PTE | None:
        """Return PTE for this VPN, or None if any intermediate level is missing."""
        # TODO Person 3: walk and return None on first missing intermediate.
        raise NotImplementedError("Person 3: implement lookup()")

    def translate(self, address: int, trace: Trace) -> int:
        """Linear address -> physical address.

        Append one TraceStep per level walked (use stage="page_table_l<N>")
        so the visualizer can show the recursive walk. Final step is the
        physical address access (stage="physical_access" or similar).

        Raise PageFault if any level is missing or final PTE is invalid.
        """
        # TODO Person 3: implement the recursive (or iterative) walk.
        # Pattern:
        #   indices = VirtualAddress(address & ~PAGE_MASK).multi_level_indices(self.levels)
        #   node = self._root
        #   for level, idx in enumerate(indices):
        #       trace.append(TraceStep(stage=f"page_table_l{level}", ...))
        #       node = node.get(idx)
        #       if node is None: raise PageFault(...)
        #   # node is now a PTE
        #   if not node.valid: raise PageFault(...)
        #   physical = (node.frame_number << PAGE_SHIFT) | (address & PAGE_MASK)
        #   return physical
        raise NotImplementedError("Person 3: implement translate()")

    def memory_overhead_bytes(self) -> int:
        """How many bytes of memory the page tables themselves take.

        Useful for the experiment: compare against single-level
        (which would be 2^36 * 8 = 512 GiB if dense).
        Each table is ENTRIES_PER_TABLE * 8 bytes.
        """
        return self._intermediate_tables_allocated * ENTRIES_PER_TABLE * 8
