"""
Page Table Entry (PTE).

Used by single-level and multi-level page tables, and by the
page-fault handler / replacement policies.

Owner: Person 2 (already defined here so the rest of the team
isn't blocked). Person 2 can extend if needed but the field
names should stay stable.
"""
from dataclasses import dataclass


@dataclass
class PTE:
    """Page Table Entry — what one slot in a page table looks like.

    Fields follow x86-64 hardware bits closely:
      valid       — page is mapped (the 'P' present bit)
      frame_number — physical frame this VPN maps to
      writable    — page is writable (W bit)
      user        — accessible from user mode (U/S bit)
      accessed    — was accessed since last clear (A bit, set by 'hardware')
      dirty       — was written since last clear (D bit)
    """
    valid: bool = False
    frame_number: int = 0
    writable: bool = True
    user: bool = True
    accessed: bool = False
    dirty: bool = False

    def __repr__(self) -> str:
        if not self.valid:
            return "PTE(invalid)"
        flags = []
        if self.writable:
            flags.append("W")
        if self.user:
            flags.append("U")
        if self.accessed:
            flags.append("A")
        if self.dirty:
            flags.append("D")
        return f"PTE(frame={self.frame_number}, {''.join(flags)})"
