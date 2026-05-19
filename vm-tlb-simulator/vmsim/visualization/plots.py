from pathlib import Path
import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt

def plot_hit_rate_vs_capacity(capacities: list[int], hit_rates: list[float], title: str, output_path: Path):
    plt.figure(figsize=(10, 6))
    plt.plot(capacities, hit_rates, marker='o', linestyle='-', color='b')
    plt.title(title)
    plt.xlabel("TLB Capacity")
    plt.ylabel("Hit Rate")
    plt.grid(True)
    plt.savefig(output_path)
    plt.close()

def plot_hit_rate_by_policy(policy_names: list[str], hit_rates: list[float], title: str, output_path: Path):
    plt.figure(figsize=(10, 6))
    plt.bar(policy_names, hit_rates, color=['skyblue', 'royalblue', 'navy'])
    plt.title(title)
    plt.ylabel("Hit Rate")
    plt.savefig(output_path)
    plt.close()