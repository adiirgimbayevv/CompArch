"""
Workload Generator Interface.
Provides high-level access to different memory access patterns.
Owner: Person 6.
"""

from vmsim.visualization.plots import sequential, random_uniform, locality_80_20, stride

class WorkloadGenerator:
    """
    A utility class to generate various memory access workloads 
    for the Virtual Memory Simulator.
    """
    
    def __init__(self, num_accesses: int, num_pages: int):
        self.num_accesses = num_accesses
        self.num_pages = num_pages

    def get_sequential(self):
        """Returns a list of sequential memory addresses."""
        return sequential(self.num_accesses)

    def get_random(self, seed: int = 42):
        """Returns a list of random memory addresses."""
        return random_uniform(self.num_accesses, self.num_pages, seed=seed)

    def get_locality(self, hot_pages: int = 10, seed: int = 42):
        """Returns a list of addresses following the 80/20 rule."""
        return locality_80_20(
            self.num_accesses, 
            hot_pages=hot_pages, 
            cold_pages=self.num_pages - hot_pages, 
            seed=seed
        )

    def get_stride(self, stride_size: int = 4):
        """Returns a list of addresses with a fixed stride."""
        return stride(self.num_accesses, stride_pages=stride_size)