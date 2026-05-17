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
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless backend — works in CI / WSL / SSH.
import matplotlib.pyplot as plt


def plot_hit_rate_vs_capacity(
    capacities: list[int],
    hit_rates: list[float],
    title: str,
    output_path: Path,
) -> None:
    """Line plot."""
    # TODO Person 6: plt.figure, plt.plot(capacities, hit_rates, marker='o'),
    # set xlabel/ylabel/title/grid, savefig(output_path), plt.close.
    raise NotImplementedError("Person 6: implement plot_hit_rate_vs_capacity()")


def plot_hit_rate_by_policy(
    policy_names: list[str],
    hit_rates: list[float],
    title: str,
    output_path: Path,
) -> None:
    """Bar chart of hit rate per replacement policy."""
    # TODO Person 6: plt.bar(policy_names, hit_rates), label/title/save/close.
    raise NotImplementedError("Person 6: implement plot_hit_rate_by_policy()")


def plot_hit_rate_by_workload(
    workload_names: list[str],
    hit_rates: list[float],
    title: str,
    output_path: Path,
) -> None:
    """Bar chart of hit rate per workload type."""
    # TODO Person 6
    raise NotImplementedError("Person 6: implement plot_hit_rate_by_workload()")


def plot_faults_vs_memory(
    memory_sizes: list[int],
    fault_counts: list[int],
    title: str,
    output_path: Path,
) -> None:
    """How many page faults occur as physical memory grows."""
    # TODO Person 6
    raise NotImplementedError("Person 6: implement plot_faults_vs_memory()")
