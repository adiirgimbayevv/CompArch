"""
LRU (Least Recently Used) replacement policy.

Evicts the key that was used longest ago. Hint: collections.OrderedDict
gives you LRU very cleanly — move_to_end on access, popitem(last=False)
for eviction.

Owner: Person 4.
"""
from collections import OrderedDict
from typing import Any

from vmsim.core import ReplacementPolicy


class LRUPolicy(ReplacementPolicy):
    """Least Recently Used."""

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._order: OrderedDict = OrderedDict()  # key -> dummy value (None)

    def insert(self, key: Any) -> None:
        """Add a fresh key as most-recently-used."""
        if key in self._order:
            self.access(key)
            return
        if len(self._order) >= self.capacity:
            raise RuntimeError("LRU policy is full; evict before inserting")
        self._order[key] = None

    def access(self, key: Any) -> None:
        """Bump key to most-recently-used."""
        if key not in self._order:
            raise KeyError(key)
        self._order.move_to_end(key)

    def evict(self) -> Any:
        """Remove and return the least-recently-used key."""
        if not self._order:
            raise KeyError("cannot evict from an empty LRU policy")
        key, _ = self._order.popitem(last=False)
        return key

    def remove(self, key: Any) -> None:
        self._order.pop(key, None)

    def contains(self, key: Any) -> bool:
        return key in self._order

    def __len__(self) -> int:
        return len(self._order)
