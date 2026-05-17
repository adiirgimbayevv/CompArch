"""
FIFO replacement policy.

Evicts whichever key was inserted longest ago, regardless of
how recently it was used.

Used by:
  - TLB (Person 4) — key = VPN
  - Page replacement (Person 5) — key = frame number

Owner: Person 4.
"""
from collections import deque
from typing import Any

from vmsim.core import ReplacementPolicy


class FIFOPolicy(ReplacementPolicy):
    """First-in, first-out."""

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._queue: deque = deque()
        self._set: set = set()

    def insert(self, key: Any) -> None:
        """Add a new key. Caller guarantees key is not already present
        and that there is room (i.e. caller calls evict() first if full)."""
        if key in self._set:
            return
        if len(self._set) >= self.capacity:
            raise RuntimeError("FIFO policy is full; evict before inserting")
        self._queue.append(key)
        self._set.add(key)

    def access(self, key: Any) -> None:
        """In FIFO, access doesn't change order. Just check it exists."""
        if key not in self._set:
            raise KeyError(key)

    def evict(self) -> Any:
        """Remove and return the oldest key."""
        if not self._queue:
            raise KeyError("cannot evict from an empty FIFO policy")
        key = self._queue.popleft()
        self._set.remove(key)
        return key

    def remove(self, key: Any) -> None:
        """Drop a key explicitly (e.g. TLB flush of one entry)."""
        if key not in self._set:
            return
        self._set.remove(key)
        self._queue.remove(key)

    def contains(self, key: Any) -> bool:
        return key in self._set

    def __len__(self) -> int:
        return len(self._set)
