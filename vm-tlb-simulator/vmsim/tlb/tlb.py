"""
Translation Lookaside Buffer.

A small cache of recent VPN -> frame_number translations sitting in
front of the page tables. On a hit we skip the (expensive) page-table
walk entirely.

Internally:
  - dict[VPN -> frame_number] for the actual mapping
  - ReplacementPolicy (FIFO/LRU/Clock) tracks usage and chooses victims

Owner: Person 4.
"""
from vmsim.core import (
    ReplacementPolicy,
    TraceStep,
    Trace,
)
from vmsim.policies import make_policy


class TLB:
    """A capacity-bounded VPN -> frame_number cache."""

    def __init__(self, capacity: int, policy_name: str = "lru") -> None:
        if capacity <= 0:
            raise ValueError("TLB capacity must be positive")
        self.capacity = capacity
        self.policy_name = policy_name
        self.policy: ReplacementPolicy = make_policy(policy_name, capacity)
        self._entries: dict[int, int] = {}  # vpn -> frame_number
        self.hits = 0
        self.misses = 0

    def lookup(self, vpn: int, trace: Trace) -> int | None:
        """Return frame_number on hit (and bump the policy),
        or None on miss. Always appends a TraceStep."""
        frame = self._entries.get(vpn)
        if frame is not None:
            self.hits += 1
            self.policy.access(vpn)
            trace.append(TraceStep(
                stage="tlb",
                description=f"TLB hit on VPN {vpn}: frame {frame}",
                input_value=vpn,
                output_value=frame,
                hit=True,
                metadata={"policy": self.policy_name},
            ))
            return frame

        self.misses += 1
        trace.append(TraceStep(
            stage="tlb",
            description=f"TLB miss on VPN {vpn}",
            input_value=vpn,
            hit=False,
            metadata={"policy": self.policy_name},
        ))
        return None

    def insert(self, vpn: int, frame_number: int) -> None:
        """Insert a fresh mapping. If TLB is full, evict via the policy first."""
        if vpn in self._entries:
            self._entries[vpn] = frame_number
            self.policy.access(vpn)
            return

        if len(self._entries) >= self.capacity:
            victim = self.policy.evict()
            del self._entries[victim]

        self._entries[vpn] = frame_number
        self.policy.insert(vpn)

    def flush(self) -> None:
        """Drop everything (simulates a context switch)."""
        self._entries.clear()
        self.policy = make_policy(self.policy_name, self.capacity)

    def flush_one(self, vpn: int) -> None:
        """Drop a single entry (e.g. when a PTE is invalidated)."""
        if vpn in self._entries:
            del self._entries[vpn]
            self.policy.remove(vpn)

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total else 0.0

    def reset_stats(self) -> None:
        self.hits = 0
        self.misses = 0
