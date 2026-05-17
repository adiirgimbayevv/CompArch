"""
Address types and constants for the virtual memory simulator.

This is foundation code used by everyone. Don't modify without
coordinating with the team — changing the address layout breaks
every module.

Owner: Person 1
"""
from dataclasses import dataclass


# Page size: 4 KiB (12 bits offset) — same as x86-64.
PAGE_SHIFT: int = 12
PAGE_SIZE: int = 1 << PAGE_SHIFT             # 4096 bytes
PAGE_MASK: int = PAGE_SIZE - 1               # 0xFFF (low 12 bits)

# Multi-level page table layout (x86-64 style: 4 levels of 9 bits each).
LEVELS: int = 4                              # PGD -> PUD -> PMD -> PT
BITS_PER_LEVEL: int = 9
ENTRIES_PER_TABLE: int = 1 << BITS_PER_LEVEL  # 512

# Virtual address: 12 (offset) + 4*9 (indices) = 48 bits used.
VIRTUAL_ADDRESS_BITS: int = PAGE_SHIFT + LEVELS * BITS_PER_LEVEL  # 48


@dataclass(frozen=True)
class VirtualAddress:
    """A 48-bit virtual address.

    Provides helpers to extract:
      - offset (low 12 bits)
      - page_number (everything above the offset)
      - per-level indices for multi-level page table walks
    """
    value: int

    def __post_init__(self) -> None:
        if self.value < 0 or self.value >= (1 << VIRTUAL_ADDRESS_BITS):
            raise ValueError(
                f"VirtualAddress {self.value:#x} out of range "
                f"(must fit in {VIRTUAL_ADDRESS_BITS} bits)"
            )

    @property
    def offset(self) -> int:
        """Byte offset within the page."""
        return self.value & PAGE_MASK

    @property
    def page_number(self) -> int:
        """Virtual page number (VPN)."""
        return self.value >> PAGE_SHIFT

    def multi_level_indices(
        self, levels: int = LEVELS, bits_per_level: int = BITS_PER_LEVEL
    ) -> list[int]:
        """Extract the index into each level of a multi-level page table.

        Returns indices from top level (PGD) down to bottom level (PT).
        Example for x86-64 (4 levels, 9 bits each):
            [pgd_idx, pud_idx, pmd_idx, pt_idx]
        """
        indices = []
        mask = (1 << bits_per_level) - 1
        for level in range(levels - 1, -1, -1):
            shift = PAGE_SHIFT + level * bits_per_level
            indices.append((self.value >> shift) & mask)
        return indices

    def __repr__(self) -> str:
        return f"VA({self.value:#x})"


@dataclass(frozen=True)
class PhysicalAddress:
    """A physical address (frame_number * PAGE_SIZE + offset)."""
    value: int

    @classmethod
    def from_frame(cls, frame_number: int, offset: int) -> "PhysicalAddress":
        if offset < 0 or offset >= PAGE_SIZE:
            raise ValueError(f"offset {offset} out of range")
        return cls((frame_number << PAGE_SHIFT) | offset)

    @property
    def frame_number(self) -> int:
        return self.value >> PAGE_SHIFT

    @property
    def offset(self) -> int:
        return self.value & PAGE_MASK

    def __repr__(self) -> str:
        return f"PA({self.value:#x})"
