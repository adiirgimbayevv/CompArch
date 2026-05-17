"""Shared replacement policies — used by TLB and page-fault handler.

To get a policy by name:
    from vmsim.policies import make_policy
    policy = make_policy("lru", capacity=64)
"""
from .fifo import FIFOPolicy
from .lru import LRUPolicy
from .clock import ClockPolicy
from vmsim.core import ReplacementPolicy


_REGISTRY = {
    "fifo": FIFOPolicy,
    "lru": LRUPolicy,
    "clock": ClockPolicy,
}


def make_policy(name: str, capacity: int) -> ReplacementPolicy:
    """Construct a policy by name (case-insensitive)."""
    cls = _REGISTRY.get(name.lower())
    if cls is None:
        valid = ", ".join(sorted(_REGISTRY))
        raise ValueError(f"unknown policy {name!r} (valid: {valid})")
    return cls(capacity)


__all__ = ["FIFOPolicy", "LRUPolicy", "ClockPolicy", "make_policy"]
