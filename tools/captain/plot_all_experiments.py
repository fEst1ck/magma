#!/usr/bin/env python3
"""
Script to generate coverage growth plots for all experiments.
Usage: python3 plot_all_experiments.py [--median]
"""

import sys
import argparse
from pathlib import Path
import subprocess

def find_experiment_directories(base_path="."):
    """Find all experiment directories (exp-*)."""
    base = Path(base_path)
    exp_dirs = sorted([d for d in base.iterdir() if d.is_dir() and d.name.startswith("exp-")])
    return exp_dirs

def generate_plots_for_all(use_median=False):
    """Generate coverage growth plots for all experiments."""
    exp_dirs = find_experiment_directories()

    if not exp_dirs:
        print("No experiment directories found (exp-*)")
        return

    print(f"Found {len(exp_dirs)} experiment directories")
    print("=" * 80)

    successful = 0
    failed = 0

    for i, exp_dir in enumerate(exp_dirs, 1):
        print(f"\n[{i}/{len(exp_dirs)}] Processing: {exp_dir.name}")
        print("-" * 80)

        # Build command
        cmd = ["python3", "plot_edge_coverage_growth.py", str(exp_dir)]
        if use_median:
            cmd.append("--median")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(result.stdout, end='')
                successful += 1
            else:
                print(f"ERROR: Failed to generate plots for {exp_dir.name}")
                print(result.stderr)
                failed += 1

        except Exception as e:
            print(f"ERROR: Exception while processing {exp_dir.name}: {e}")
            failed += 1

    print("\n" + "=" * 80)
    print(f"Summary: {successful} successful, {failed} failed out of {len(exp_dirs)} experiments")
    print("=" * 80)

def main():
    parser = argparse.ArgumentParser(
        description='Generate coverage growth plots for all experiments.'
    )
    parser.add_argument('--median', action='store_true',
                        help='Use median instead of mean (no std dev shading)')

    args = parser.parse_args()

    generate_plots_for_all(use_median=args.median)

if __name__ == "__main__":
    main()
