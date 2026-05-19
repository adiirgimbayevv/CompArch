"""
Single-level page table.

Maps virtual page number (VPN) -> PTE in one flat lookup.
After segmentation gives us a linear address, this turns it into
a physical address (or raises PageFault).

Layout:
  linear address = [ VPN ][ offset (12 bits) ]
  PT is a dict (or array) indexed by VPN, holding PTEs.

Owner: Person 2.

Reference: see vmsim/segmentation/segments.py for the style this
project uses (TraceStep on every step, docstrings, type hints).
"""
from vmsim.core import (
    PTE,
    PhysicalAddress,
    PhysicalMemory,
    TraceStep,
    Trace,
    Translator,
    PAGE_SHIFT,
    PAGE_MASK,
)


class PageFault(Exception):
    """Raised when a translation hits an invalid PTE."""

    def __init__(self, vpn: int, message: str = ""):
        self.vpn = vpn
        super().__init__(message or f"page fault on VPN {vpn:#x}")


class SingleLevelPageTable(Translator):
    """One flat dict[VPN -> PTE].

    Sparse storage so we don't have to allocate the whole table
    (which for 48-bit VAs would be 2^36 entries — way too big).
    """

    def __init__(self, physical_memory: PhysicalMemory) -> None:
        self.memory = physical_memory
        self._entries: dict[int, PTE] = {}

    def map(self, vpn: int, pte: PTE) -> None:
        """Install a PTE for the given VPN."""
        self._entries[vpn] = pte

    def unmap(self, vpn: int) -> None:
        """Remove the PTE for this VPN (if any)."""
        self._entries.pop(vpn, None)

    def lookup(self, vpn: int) -> PTE | None:
        """Return the PTE for this VPN, or None if not mapped."""
        return self._entries.get(vpn)

    def translate(self, address: int, trace: Trace) -> int:
        """Linear address -> physical address.

        Steps:
          1. Split address into VPN and offset.
          2. Look up PTE by VPN.
          3. If PTE missing or invalid -> append TraceStep(hit=False)
             and raise PageFault.
          4. Otherwise, set accessed=True, build physical address
             from PTE.frame_number and offset, append a hit step,
             and return it.

        See segmentation/segments.py for the trace step pattern.
        """
        vpn = address >> PAGE_SHIFT
        offset = address & PAGE_MASK
        pte = self._entries.get(vpn)
        
        if pte is None or not pte.valid:
            trace.append(TraceStep(
                stage="page_table",
                description=f"VPN {vpn:#x} not mapped or invalid",
                input_value=address,
                hit=False,
            ))
            raise PageFault(vpn)
            
        pte.accessed = True
        physical_address = (pte.frame_number << PAGE_SHIFT) | offset
        
        trace.append(TraceStep(
            stage="page_table",
            description=f"Translated VPN {vpn:#x} -> Frame {pte.frame_number:#x}",
            input_value=address,
            output_value=physical_address,
            hit=True,
        ))
        return physical_address

    def __len__(self) -> int:
        return len(self._entries)
