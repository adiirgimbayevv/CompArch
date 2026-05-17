"""
Physical memory: a finite array of frames.

Provides frame allocation, freeing, and tracking of resident pages.
Used by paging, the page-fault handler, and swap.

Owner: Person 2 (foundation — extend if needed).
"""
from .address import PAGE_SIZE


class OutOfMemoryError(Exception):
    """No free physical frames available."""


class PhysicalMemory:
    """A simple physical memory abstraction.

    We don't actually store bytes (this is a simulator) — we just
    track which frames are allocated and to which (vpn, process)
    they currently belong, for the benefit of the page-fault handler
    and replacement policies.
    """

    def __init__(self, num_frames: int):
        if num_frames <= 0:
            raise ValueError("num_frames must be positive")
        self.num_frames = num_frames
        # frame_number -> vpn that currently occupies it (None if free)
        self._owner: list[int | None] = [None] * num_frames
        self._free: list[int] = list(range(num_frames))

    @property
    def size_bytes(self) -> int:
        return self.num_frames * PAGE_SIZE

    @property
    def num_free(self) -> int:
        return len(self._free)

    @property
    def num_allocated(self) -> int:
        return self.num_frames - self.num_free

    def allocate_frame(self, vpn: int) -> int:
        """Allocate a free frame for the given virtual page.
        Returns frame number.
        Raises OutOfMemoryError if no frames are free."""
        if not self._free:
            raise OutOfMemoryError("no free frames")
        frame = self._free.pop()
        self._owner[frame] = vpn
        return frame

    def free_frame(self, frame_number: int) -> None:
        """Return a frame to the free pool."""
        if not (0 <= frame_number < self.num_frames):
            raise ValueError(f"invalid frame {frame_number}")
        if self._owner[frame_number] is None:
            return  # already free, idempotent
        self._owner[frame_number] = None
        self._free.append(frame_number)

    def owner_of(self, frame_number: int) -> int | None:
        """Which VPN currently lives in this frame (None if free)."""
        return self._owner[frame_number]

    def allocated_frames(self) -> list[int]:
        """List of currently allocated frame numbers."""
        return [f for f in range(self.num_frames) if self._owner[f] is not None]
