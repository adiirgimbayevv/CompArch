import random
from vmsim.core import PAGE_SIZE

def sequential(num_accesses: int, start_page: int = 0) -> list[int]:
    """Generates sequential virtual addresses: VPN 0, 1, 2..."""
    return [(start_page + i) * PAGE_SIZE for i in range(num_accesses)]

def random_uniform(num_accesses: int, num_pages: int, seed: int = 0) -> list[int]:
    """Generates random page accesses across the entire range."""
    rng = random.Random(seed)
    return [rng.randint(0, num_pages - 1) * PAGE_SIZE for _ in range(num_accesses)]

def locality_80_20(num_accesses: int, hot_pages: int = 8, cold_pages: int = 1024, 
                    hot_fraction: float = 0.8, seed: int = 0) -> list[int]:
    """80% of accesses to 'hot' pages, 20% to 'cold' pages."""
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
    """Accesses every N-th page to test TLB associativity."""
    return [(i * stride_pages) * PAGE_SIZE for i in range(num_accesses)]