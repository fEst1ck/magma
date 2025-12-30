#!/usr/bin/env python3
"""
Script to plot coverage growth over time for all fuzzer types in an experiment.
Generates one plot for each coverage metric (block, edge, path, pfp, quad).
Usage: python3 plot_edge_coverage_growth.py <experiment_dir> [-m]
       -m, --median: Use median instead of mean (no std dev shading)
"""

import json
import sys
import os
import re
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# Fuzzer types to plot
FUZZER_TYPES = [
    "dummy_fuzzer_block",
    "dummy_fuzzer_edge",
    "dummy_fuzzer_path",
    "dummy_fuzzer_pfp",
    "dummy_fuzzer_quad"
]

# Coverage metrics to generate plots for
COVERAGE_METRICS = ["block", "edge", "path", "pfp", "quad", "rawpath"]

# Prettier names for legend
FUZZER_NAMES = {
    "dummy_fuzzer_block": "Block",
    "dummy_fuzzer_edge": "Edge",
    "dummy_fuzzer_path": "Path",
    "dummy_fuzzer_pfp": "PFP",
    "dummy_fuzzer_quad": "Quad"
}

# Coverage metric display names
METRIC_NAMES = {
    "block": "Block Coverage",
    "edge": "Edge Coverage",
    "path": "Path Coverage",
    "pfp": "PFP Coverage",
    "quad": "Quad Coverage",
    "rawpath": "Raw Path Coverage"
}

def extract_target_name(exp_dir):
    """
    Extract target name from directory name.
    Example: exp-libpng_read_fuzzer-10-17 -> libpng_read_fuzzer
    """
    match = re.match(r'exp-(.+)-\d{2}-\d{2}', exp_dir)
    if match:
        return match.group(1)
    return exp_dir

def load_coverage_data(exp_path, fuzzer_type, coverage_metric):
    """
    Load coverage data for a specific metric for all trials of a fuzzer type.
    Returns a list of (time, coverage) tuples for each trial.
    """
    trials_data = []

    # Find all trial directories
    fuzzer_base = exp_path / "ar" / fuzzer_type

    if not fuzzer_base.exists():
        return trials_data

    # Navigate through project/fuzzer_name structure
    for project_dir in fuzzer_base.iterdir():
        if not project_dir.is_dir():
            continue
        for fuzzer_name_dir in project_dir.iterdir():
            if not fuzzer_name_dir.is_dir():
                continue
            # Now iterate through trial numbers
            for trial_dir in fuzzer_name_dir.iterdir():
                if not trial_dir.is_dir():
                    continue

                log_file = trial_dir / "findings" / "stats" / "fuzzer_log.json"
                if not log_file.exists():
                    continue

                try:
                    with open(log_file, 'r') as f:
                        log_data = json.load(f)

                    time_data = []
                    coverage_data = []

                    for entry in log_data:
                        runtime = entry.get('runtime_seconds', 0)
                        metric_value = entry.get('coverage_count', {}).get(coverage_metric, 0)
                        time_data.append(runtime)
                        coverage_data.append(metric_value)

                    if time_data and coverage_data:
                        trials_data.append((time_data, coverage_data))
                except Exception as e:
                    print(f"Warning: Error loading {log_file}: {e}", file=sys.stderr)

    return trials_data

def compute_average_coverage(trials_data, use_median=False):
    """
    Compute average or median coverage across trials.
    Args:
        trials_data: List of (time_data, coverage_data) tuples
        use_median: If True, use median instead of mean
    Returns (time_points, avg_coverage, std_coverage).
    """
    if not trials_data:
        return [], [], []

    # Find all unique time points
    all_times = set()
    for time_data, _ in trials_data:
        all_times.update(time_data)

    time_points = sorted(all_times)

    # Interpolate coverage for each trial at common time points
    coverage_matrix = []
    for time_data, coverage_data in trials_data:
        # Interpolate
        interpolated = np.interp(time_points, time_data, coverage_data)
        coverage_matrix.append(interpolated)

    coverage_matrix = np.array(coverage_matrix)

    if use_median:
        avg_coverage = np.median(coverage_matrix, axis=0)
        std_coverage = np.zeros_like(avg_coverage)  # No std dev for median
    else:
        avg_coverage = np.mean(coverage_matrix, axis=0)
        std_coverage = np.std(coverage_matrix, axis=0)

    return time_points, avg_coverage, std_coverage

def plot_coverage_growth(exp_dir, use_median=False):
    """
    Plot coverage growth for all fuzzer types for each coverage metric.
    Generates one plot per coverage metric.
    Args:
        exp_dir: Experiment directory path
        use_median: If True, plot median instead of mean (no std dev)
    """
    exp_path = Path(exp_dir)

    if not exp_path.exists():
        print(f"Error: Experiment directory '{exp_dir}' does not exist", file=sys.stderr)
        return

    # Extract target name for title
    target_name = extract_target_name(exp_path.name)

    # Generate one plot for each coverage metric
    for coverage_metric in COVERAGE_METRICS:
        print(f"Generating plot for {coverage_metric} coverage...")

        # Create figure
        plt.figure(figsize=(12, 7))

        # Plot each fuzzer type
        for fuzzer_type in FUZZER_TYPES:
            trials_data = load_coverage_data(exp_path, fuzzer_type, coverage_metric)

            if not trials_data:
                print(f"Warning: No data found for {fuzzer_type} - {coverage_metric}", file=sys.stderr)
                continue

            time_points, avg_coverage, std_coverage = compute_average_coverage(trials_data, use_median)

            # Convert time from seconds to hours
            time_hours = np.array(time_points) / 3600.0

            # Plot mean/median with optional shaded std
            label = FUZZER_NAMES.get(fuzzer_type, fuzzer_type)
            line = plt.plot(time_hours, avg_coverage, label=label, linewidth=2, marker='o',
                           markersize=4, markevery=max(1, len(time_hours)//20))

            # Add shaded region for standard deviation (only for mean, not median)
            if not use_median and len(trials_data) > 1:  # Only show std if multiple trials and using mean
                color = line[0].get_color()
                plt.fill_between(time_hours,
                               avg_coverage - std_coverage,
                               avg_coverage + std_coverage,
                               alpha=0.2, color=color)

        plt.xlabel('Time (hours)', fontsize=12)
        plt.ylabel(METRIC_NAMES.get(coverage_metric, coverage_metric), fontsize=12)
        plt.title(f'{target_name}', fontsize=14, fontweight='bold')

        # Set x-axis ticks at 4-hour intervals
        ax = plt.gca()
        ax.xaxis.set_major_locator(ticker.MultipleLocator(4))

        plt.legend(loc='lower right', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        # Save figure
        output_file = exp_path / f"{target_name}-{coverage_metric}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Figure saved to: {output_file}")

        plt.close()

def main():
    parser = argparse.ArgumentParser(
        description='Plot coverage growth over time for all fuzzer types in an experiment.'
    )
    parser.add_argument('experiment_dir', help='Path to experiment directory')
    parser.add_argument('-m', '--median', action='store_true',
                        help='Use median instead of mean (no std dev shading)')

    args = parser.parse_args()

    plot_coverage_growth(args.experiment_dir, use_median=args.median)

if __name__ == "__main__":
    main()
