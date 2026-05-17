"""
Single-level page table.

Maps virtual page number (VPN) -> PTE in one flat lookup.
After segmentation gives us a linear address, this turns it into
a physical address (or raises PageFault).

Layout:
  linear address = [ VPN ][ offset (12 bits) ]
  PT is a dict (or array) indexed by VPN, holding PTEs.

Owner: Person 2.
TODO: implement methods marked `raise NotImplementedError`.

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
        # TODO Person 2: extra fields you want? (e.g. stats counters)

    def map(self, vpn: int, pte: PTE) -> None:
        """Install a PTE for the given VPN."""
        # TODO Person 2: store pte under vpn in self._entries
        raise NotImplementedError("Person 2: implement map()")

    def unmap(self, vpn: int) -> None:
        """Remove the PTE for this VPN (if any)."""
        # TODO Person 2: remove from self._entries
        raise NotImplementedError("Person 2: implement unmap()")

    def lookup(self, vpn: int) -> PTE | None:
        """Return the PTE for this VPN, or None if not mapped."""
        # TODO Person 2: dict lookup; return None if missing
        raise NotImplementedError("Person 2: implement lookup()")

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
        # TODO Person 2: implement following the pattern in segments.py
        raise NotImplementedError("Person 2: implement translate()")

    def __len__(self) -> int:
        return len(self._entries)
