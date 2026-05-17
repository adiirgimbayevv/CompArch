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
        # Convert VPN to a full address with offset = 0, so we can use
        # the existing multi_level_indices() helper from VirtualAddress.
        indices = VirtualAddress(vpn << PAGE_SHIFT).multi_level_indices(self.levels)

        # Start at the top of the tree (PGD level).
        node = self._root

        # Walk down all levels EXCEPT the last one.
        # At each step: if the sub-dict for this index doesn't exist yet,
        # create one and count it. Then descend into it.
        for idx in indices[:-1]:
            if idx not in node:
                node[idx] = {}
                self._intermediate_tables_allocated += 1
            node = node[idx]

        # Now `node` is the bottom-level dict (the PT — the "leaf table").
        # The last index tells us where to put the PTE inside it.
        leaf_index = indices[-1]
        node[leaf_index] = pte

    def lookup(self, vpn: int) -> PTE | None:
        """Return PTE for this VPN, or None if any intermediate level is missing."""
        indices = VirtualAddress(vpn << PAGE_SHIFT).multi_level_indices(self.levels)

        # Start at the top of the tree.
        node = self._root

        # Walk down all levels except the last.
        # If any sub-dict is missing, the page isn't mapped — return None.
        for idx in indices[:-1]:
            if idx not in node:
                return None
            node = node[idx]

        # At the leaf level. .get() returns None if the key doesn't exist,
        # or the PTE if it does. That's exactly the behavior we want.
        return node.get(indices[-1])

    def translate(self, address: int, trace: Trace) -> int:
        """Linear address -> physical address.

        Append one TraceStep per level walked (use stage="page_table_l<N>")
        so the visualizer can show the recursive walk. Final step is the
        physical address access (stage="physical_access" or similar).

        Raise PageFault if any level is missing or final PTE is invalid.
        """
        # Split address into VPN (used for tree walk) and offset
        # (used at the end to build the physical address).
        vpn = address >> PAGE_SHIFT
        offset = address & PAGE_MASK
        indices = VirtualAddress(vpn << PAGE_SHIFT).multi_level_indices(self.levels)

        # Walk the tree top-down. Each iteration handles one level.
        node = self._root
        for level, idx in enumerate(indices):
            stage = f"page_table_l{level}"

            # If this level doesn't contain the index we need → page fault.
            if idx not in node:
                trace.append(TraceStep(
                    stage=stage,
                    description=f"level {level}: index {idx:#x} not present — page fault",
                    input_value=address,
                    hit=False,
                    metadata={"vpn": vpn, "level": level, "index": idx},
                ))
                raise PageFault(vpn)

            # Index found — descend (or land on the PTE at the last level).
            node = node[idx]
            trace.append(TraceStep(
                stage=stage,
                description=f"level {level}: index {idx:#x} found",
                input_value=address,
                hit=True,
                metadata={"vpn": vpn, "level": level, "index": idx},
            ))

        # After the loop, `node` is the PTE stored at the leaf.
        pte: PTE = node

        # The PTE might be present but marked invalid (e.g. swapped out).
        if not pte.valid:
            trace.append(TraceStep(
                stage="page_fault",
                description=f"PTE for VPN {vpn:#x} is invalid",
                input_value=address,
                hit=False,
                metadata={"vpn": vpn},
            ))
            raise PageFault(vpn)

        # Build the physical address from the PTE's frame_number and the offset.
        physical = (pte.frame_number << PAGE_SHIFT) | offset

        # Mark the page as accessed (used later by the replacement policy).
        pte.accessed = True

        # Final success step — the visualizer shows this as the result.
        trace.append(TraceStep(
            stage="physical_access",
            description=f"frame {pte.frame_number:#x} + offset {offset:#x} = {physical:#x}",
            input_value=address,
            output_value=physical,
            hit=True,
            metadata={"vpn": vpn, "frame": pte.frame_number},
        ))

        return physical

    def memory_overhead_bytes(self) -> int:
        """How many bytes of memory the page tables themselves take.

        Useful for the experiment: compare against single-level
        (which would be 2^36 * 8 = 512 GiB if dense).
        Each table is ENTRIES_PER_TABLE * 8 bytes.
        """
        return self._intermediate_tables_allocated * ENTRIES_PER_TABLE * 8
