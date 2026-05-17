"""
Abstract base classes — the contracts between modules.

If your module is a Translator (segmentation, single-level paging,
multi-level paging), inherit from Translator and implement translate().

If your module is a replacement policy (FIFO, LRU, Clock — used by
both TLB and page replacement), inherit from ReplacementPolicy.

Don't break these signatures without telling the whole team.

Owner: Person 1 (foundation).
"""
from abc import ABC, abstractmethod
from typing import Any

from .trace import Trace


class Translator(ABC):
    """Anything that turns one address into another address.

    Segmentation turns logical -> linear.
    Paging turns linear (= virtual) -> physical.

    Implementations MUST append diagnostic TraceSteps to `trace`
    so the visualizer can show what happened.
    """

    @abstractmethod
    def translate(self, address: int, trace: Trace) -> int:
        """Translate `address`, appending steps to `trace`.

        Returns the translated address.
        Raises on faults (SegmentationFault, PageFault, etc.).
        """
        ...


class ReplacementPolicy(ABC):
    """Generic eviction policy. Used by both the TLB
    (which key = VPN) and the page-fault handler
    (which key = frame number).

    Lifecycle:
      insert(key)       — a new key has been brought in
      access(key)       — an already-present key was used
      evict() -> key    — choose a victim (caller will remove it)
      remove(key)       — explicitly drop a key (e.g. TLB flush)
      contains(key)     — is this key tracked?
    """

    @abstractmethod
    def insert(self, key: Any) -> None: ...

    @abstractmethod
    def access(self, key: Any) -> None: ...

    @abstractmethod
    def evict(self) -> Any: ...

    @abstractmethod
    def remove(self, key: Any) -> None: ...

    @abstractmethod
    def contains(self, key: Any) -> bool: ...

    @abstractmethod
    def __len__(self) -> int: ...
