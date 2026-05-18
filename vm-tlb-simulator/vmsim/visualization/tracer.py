"""
Tracer and Plotting Logic for Virtual Memory Simulation.
This module generates visualizations for TLB and Page Table experiments.
Owner: Person 6.
"""

from pathlib import Path
import matplotlib

matplotlib.use("Agg") 
import matplotlib.pyplot as plt

def plot_hit_rate_vs_capacity(
    capacities: list[int],
    hit_rates: list[float],
    title: str,
    output_path: Path,
) -> None:
    """
    Generates a line plot showing how TLB capacity affects hit rate.
    Higher capacity usually leads to a higher hit rate until it plateaus.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(capacities, hit_rates, marker='o', linestyle='-', color='b', linewidth=2)
    plt.title(title, fontsize=14)
    plt.xlabel("TLB Capacity (Number of Entries)", fontsize=12)
    plt.ylabel("Hit Rate (Percentage)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(output_path)
    plt.close()

def plot_hit_rate_by_policy(
    policy_names: list[str],
    hit_rates: list[float],
    title: str,
    output_path: Path,
) -> None:
    """
    Generates a bar chart comparing different replacement policies (FIFO, LRU, Clock).
    Usually, LRU performs better than FIFO in most workloads.
    """
    plt.figure(figsize=(10, 6))
    bars = plt.bar(policy_names, hit_rates, color=['skyblue', 'royalblue', 'navy'])
    plt.title(title, fontsize=14)
    plt.ylabel("Hit Rate", fontsize=12)
    plt.ylim(0, 1.1)  # Hit rate is always between 0 and 1
    
    # Adding data labels on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.01, round(yval, 3), ha='center', va='bottom')
        
    plt.savefig(output_path)
    plt.close()

def plot_hit_rate_by_workload(
    workload_names: list[str],
    hit_rates: list[float],
    title: str,
    output_path: Path,
) -> None:
    """
    Compares how different access patterns (Sequential, Random, 80/20) affect performance.
    Sequential access should have the highest hit rate due to spatial locality.
    """
    plt.figure(figsize=(10, 6))
    plt.bar(workload_names, hit_rates, color='forestgreen')
    plt.title(title, fontsize=14)
    plt.ylabel("Hit Rate", fontsize=12)
    plt.xticks(rotation=15)
    plt.savefig(output_path)
    plt.close()

def plot_faults_vs_memory(
    memory_sizes: list[int],
    fault_counts: list[int],
    title: str,
    output_path: Path,
) -> None:
    """
    Plots the number of Page Faults against physical memory size.
    Demonstrates that increasing physical memory reduces the need for disk swapping.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(memory_sizes, fault_counts, marker='s', color='crimson', markersize=8)
    plt.title(title, fontsize=14)
    plt.xlabel("Physical Memory Size (Number of Pages)", fontsize=12)
    plt.ylabel("Page Fault Count", fontsize=12)
    plt.grid(True)
    plt.savefig(output_path)
    plt.close()