"""
Segmentation: turning a logical address into a linear (virtual) address.

This is the FIRST stage of address translation. After segmentation, the
linear address goes into the paging module (single- or multi-level).

x86-64 essentially flattens segmentation (base=0, limit=max for CS/DS/SS),
but legacy modes and our simulator still support it explicitly:

  Logical address layout (64-bit):
    [ 16-bit selector ][ 48-bit offset ]

  selector picks a segment (by index in the segment table).
  offset is checked against the segment's limit, then added to its base.
  Result = linear address (input to paging).

This module is fully implemented as the team's reference example.

Owner: Person 1.
"""
from dataclasses import dataclass

from vmsim.core import Translator, TraceStep, Trace


# Logical address layout
SELECTOR_BITS = 16
SELECTOR_SHIFT = 48
SELECTOR_MASK = (1 << SELECTOR_BITS) - 1            # 0xFFFF
OFFSET_MASK = (1 << SELECTOR_SHIFT) - 1             # low 48 bits


class SegmentationFault(Exception):
    """Raised when a logical address violates segment bounds or
    references an unknown segment selector."""


@dataclass
class Segment:
    """One segment descriptor.

    base   — start of the segment in the linear address space
    limit  — number of bytes inside the segment (offset must be < limit)
    name   — human-readable label ("code", "stack", "heap", ...)
    """
    name: str
    base: int
    limit: int
    readable: bool = True
    writable: bool = True
    executable: bool = False

    def __post_init__(self) -> None:
        if self.base < 0:
            raise ValueError(f"segment '{self.name}' has negative base")
        if self.limit <= 0:
            raise ValueError(f"segment '{self.name}' has non-positive limit")

    def __repr__(self) -> str:
        perms = ("r" if self.readable else "-") \
              + ("w" if self.writable else "-") \
              + ("x" if self.executable else "-")
        return f"Segment(name={self.name!r}, base={self.base:#x}, " \
               f"limit={self.limit:#x}, {perms})"


class SegmentTable(Translator):
    """Maps selectors to segments and translates logical addresses."""

    def __init__(self) -> None:
        self._segments: dict[int, Segment] = {}

    def add_segment(self, selector: int, segment: Segment) -> None:
        """Install a segment under the given selector.

        Selectors must fit in 16 bits.
        """
        if not (0 <= selector <= SELECTOR_MASK):
            raise ValueError(
                f"selector {selector:#x} out of range "
                f"(must fit in {SELECTOR_BITS} bits)"
            )
        if selector in self._segments:
            raise ValueError(
                f"selector {selector:#x} already maps to {self._segments[selector]}"
            )
        self._segments[selector] = segment

    def get_segment(self, selector: int) -> Segment | None:
        return self._segments.get(selector)

    @staticmethod
    def pack_logical(selector: int, offset: int) -> int:
        """Build a logical address from selector + offset.
        Convenience for callers / tests."""
        if not (0 <= selector <= SELECTOR_MASK):
            raise ValueError(f"selector {selector:#x} out of range")
        if not (0 <= offset <= OFFSET_MASK):
            raise ValueError(f"offset {offset:#x} out of range")
        return (selector << SELECTOR_SHIFT) | offset

    def translate(self, address: int, trace: Trace) -> int:
        """Logical address -> linear (virtual) address.

        Implements the Translator interface. Appends one TraceStep
        for the segmentation lookup.

        Raises SegmentationFault on bad selector or offset.
        """
        selector = (address >> SELECTOR_SHIFT) & SELECTOR_MASK
        offset = address & OFFSET_MASK

        segment = self._segments.get(selector)
        if segment is None:
            trace.append(TraceStep(
                stage="segmentation",
                description=f"unknown segment selector {selector:#x}",
                input_value=address,
                output_value=None,
                hit=False,
                metadata={"selector": selector, "offset": offset},
            ))
            raise SegmentationFault(
                f"no segment for selector {selector:#x}"
            )

        if offset >= segment.limit:
            trace.append(TraceStep(
                stage="segmentation",
                description=(
                    f"offset {offset:#x} out of bounds for segment "
                    f"'{segment.name}' (limit={segment.limit:#x})"
                ),
                input_value=address,
                output_value=None,
                hit=False,
                metadata={
                    "selector": selector,
                    "offset": offset,
                    "segment": segment.name,
                    "limit": segment.limit,
                },
            ))
            raise SegmentationFault(
                f"offset {offset:#x} >= limit {segment.limit:#x} "
                f"of segment '{segment.name}'"
            )

        linear = segment.base + offset
        trace.append(TraceStep(
            stage="segmentation",
            description=(
                f"segment '{segment.name}': base={segment.base:#x} "
                f"+ offset={offset:#x} = linear={linear:#x}"
            ),
            input_value=address,
            output_value=linear,
            hit=True,
            metadata={
                "selector": selector,
                "offset": offset,
                "segment": segment.name,
                "base": segment.base,
            },
        ))
        return linear

    def __repr__(self) -> str:
        lines = [f"SegmentTable ({len(self._segments)} segments):"]
        for sel, seg in sorted(self._segments.items()):
            lines.append(f"  [{sel:#06x}] -> {seg}")
        return "\n".join(lines)


def make_default_segment_table() -> SegmentTable:
    """A reasonable default for demos: code / data / stack / heap."""
    table = SegmentTable()
    table.add_segment(0x0001, Segment(
        name="code", base=0x0000_0000_0000_0000, limit=0x0000_0000_0010_0000,
        readable=True, writable=False, executable=True,
    ))
    table.add_segment(0x0002, Segment(
        name="data", base=0x0000_0000_0010_0000, limit=0x0000_0000_0010_0000,
        readable=True, writable=True, executable=False,
    ))
    table.add_segment(0x0003, Segment(
        name="heap", base=0x0000_0000_0020_0000, limit=0x0000_0000_0040_0000,
        readable=True, writable=True, executable=False,
    ))
    table.add_segment(0x0004, Segment(
        name="stack", base=0x0000_0000_0060_0000, limit=0x0000_0000_0010_0000,
        readable=True, writable=True, executable=False,
    ))
    return table
