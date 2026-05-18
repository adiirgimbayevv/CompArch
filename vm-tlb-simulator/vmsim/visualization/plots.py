"""
matplotlib plots for the experiments section.

Person 6 produces the graphs that are explicitly in the deliverable
("plots of TLB hit rate vs parameters"). Suggested plots:

  1. TLB hit rate vs TLB capacity (for one workload, e.g. locality 80/20).
  2. TLB hit rate vs replacement policy (FIFO/LRU/Clock), bar chart.
  3. TLB hit rate vs workload type (sequential / random / locality / stride).
  4. Page-fault count vs physical memory size (for one workload).
  5. Multi-level vs single-level memory overhead (from MultiLevelPageTable
     .memory_overhead_bytes vs single-level dict size).

Owner: Person 6.
"""
import random
from vmsim.core import PAGE_SIZE

def sequential(num_accesses: int, start_page: int = 0) -> list[int]:
    """VPN 0, 1, 2... Превращаем их в виртуальные адреса."""
    return [(start_page + i) * PAGE_SIZE for i in range(num_accesses)]

def random_uniform(num_accesses: int, num_pages: int, seed: int = 0) -> list[int]:
    """Случайные страницы по всему объему."""
    rng = random.Random(seed)
    return [rng.randint(0, num_pages - 1) * PAGE_SIZE for _ in range(num_accesses)]

def locality_80_20(num_accesses: int, hot_pages: int = 8, cold_pages: int = 1024, 
                    hot_fraction: float = 0.8, seed: int = 0) -> list[int]:
    """80% запросов в малую область (hot), 20% в большую (cold)."""
    rng = random.Random(seed)
    addresses = []
    for _ in range(num_accesses):
        if rng.random() < hot_fraction:
            vpn = rng.randint(0, hot_pages - 1)
        else:
            vpn = rng.randint(hot_pages, hot_pages + cold_pages - 1)
        addresses.append(vpn * PAGE_SIZE)
    return addresses

def stride(num_accesses: int, stride_pages: int) -> list[int]:
    """Каждая N-я страница для проверки ассоциативности TLB."""
    return [(i * stride_pages) * PAGE_SIZE for i in range(num_accesses)]