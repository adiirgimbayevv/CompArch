"""
Workload generators.

Different access patterns for experiments:
  - sequential: VPNs 0, 1, 2, 3, ... (best locality)
  - random: uniform random VPNs (worst locality)
  - locality: 80/20 working-set (realistic — most accesses fall in
              a hot region, sometimes jumps out)
  - stride: every Nth page (TLB-stress)

These produce VIRTUAL ADDRESSES (already past segmentation) for
feeding into the paging / TLB layers. Each function returns a list
of ints.

Owner: Person 6.
"""
import random

from vmsim.core import PAGE_SIZE


def sequential(num_accesses: int, start_page: int = 0) -> list[int]:
    """Sequential pages: VPN start_page, start_page+1, ..."""
    # TODO Person 6: produce a list of `num_accesses` virtual addresses,
    # each pointing at the start of a successive page.
    raise NotImplementedError("Person 6: implement sequential()")


def random_uniform(
    num_accesses: int, num_pages: int, seed: int = 0
) -> list[int]:
    """Uniformly random VPNs in [0, num_pages)."""
    # TODO Person 6: use random.Random(seed) for reproducibility.
    raise NotImplementedError("Person 6: implement random_uniform()")


def locality_80_20(
    num_accesses: int,
    hot_pages: int = 8,
    cold_pages: int = 1024,
    hot_fraction: float = 0.8,
    seed: int = 0,
) -> list[int]:
    """80% of accesses go to the hot working set, 20% go cold."""
    # TODO Person 6: a random.Random(seed) picks hot vs cold per access.
    raise NotImplementedError("Person 6: implement locality_80_20()")


def stride(num_accesses: int, stride_pages: int) -> list[int]:
    """Every Nth page — stresses TLB associativity."""
    # TODO Person 6: VPN i = i * stride_pages
    raise NotImplementedError("Person 6: implement stride()")
