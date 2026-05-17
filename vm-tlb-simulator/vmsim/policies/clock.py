"""
Clock (Second-chance) replacement policy.

A pragmatic approximation of LRU using a circular buffer and one
reference bit per slot.

  - On access(key): set reference bit of that slot to 1.
  - On evict():
        loop:
            if slot[hand].ref == 0: evict it, advance hand, return its key
            else: slot[hand].ref = 0, advance hand
  - On insert(key): place in next free slot with ref=1.

Owner: Person 4.
"""
from typing import Any

from vmsim.core import ReplacementPolicy


class ClockPolicy(ReplacementPolicy):
    """Second-chance / Clock algorithm."""

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        # Parallel arrays:
        self._slots: list[Any | None] = [None] * capacity
        self._ref: list[int] = [0] * capacity
        self._hand: int = 0
        self._index: dict[Any, int] = {}  # key -> slot index, for O(1) access

    def insert(self, key: Any) -> None:
        """Place key in a free slot (caller has already evicted if needed)
        with ref bit set to 1."""
        if key in self._index:
            self.access(key)
            return
        if len(self._index) >= self.capacity:
            raise RuntimeError("Clock policy is full; evict before inserting")

        for offset in range(self.capacity):
            index = (self._hand + offset) % self.capacity
            if self._slots[index] is None:
                self._slots[index] = key
                self._ref[index] = 1
                self._index[key] = index
                self._hand = (index + 1) % self.capacity
                return

        raise RuntimeError("Clock policy has no free slot")

    def access(self, key: Any) -> None:
        """Set the reference bit on key's slot to 1."""
        self._ref[self._index[key]] = 1

    def evict(self) -> Any:
        """Run the clock hand until it finds a slot with ref=0,
        clearing ref bits along the way. Return the evicted key."""
        if not self._index:
            raise KeyError("cannot evict from an empty Clock policy")

        while True:
            key = self._slots[self._hand]
            if key is None:
                self._hand = (self._hand + 1) % self.capacity
                continue

            if self._ref[self._hand] == 0:
                victim = key
                del self._index[victim]
                self._slots[self._hand] = None
                self._hand = (self._hand + 1) % self.capacity
                return victim

            self._ref[self._hand] = 0
            self._hand = (self._hand + 1) % self.capacity

    def remove(self, key: Any) -> None:
        index = self._index.pop(key, None)
        if index is None:
            return
        self._slots[index] = None
        self._ref[index] = 0

    def contains(self, key: Any) -> bool:
        return key in self._index

    def __len__(self) -> int:
        return len(self._index)
