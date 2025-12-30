#!/usr/bin/env python3
"""
Script to summarize final coverage across all experiments.
Computes average coverage across trials for each fuzzer and experiment.
Outputs both JSON and CSV formats.

Usage: python3 summarize_final_coverage.py
"""

import json
import csv
import sys
import re
from pathlib import Path
import numpy as np

# Dated experiment directories to process
EXPERIMENT_DIRS = [
    "exp-libpng_read_fuzzer-10-17",
    "exp-exif-10-20",
    "exp-tiffcp-10-24",
    "exp-tiff_read_rgba_fuzzer-10-30",
    "exp-x509-11-02",
    "exp-server-11-05",
    "exp-libxml2_xml_read_memory_fuzzer-11-18",
    "exp-lua-11-19",
]

# Fuzzer types to process
FUZZER_TYPES = [
    "dummy_fuzzer_block",
    "dummy_fuzzer_edge",
    "dummy_fuzzer_path",
    "dummy_fuzzer_pfp",
    "dummy_fuzzer_quad"
]

# Coverage metrics to extract
COVERAGE_METRICS = ["block", "edge", "path", "pfp", "quad", "rawpath"]

def extract_target_name(exp_dir):
    """
    Extract target name from directory name.
    Example: exp-libpng_read_fuzzer-10-17 -> libpng_read_fuzzer
    """
    match = re.match(r'exp-(.+)-\d{2}-\d{2}', exp_dir)
    if match:
        return match.group(1)
    return exp_dir

def extract_final_coverage_for_experiment(exp_path):
    """
    Extract final coverage values for all fuzzers in an experiment.
    Returns dict: {fuzzer_type: {metric: {trial: value}}}
    """
    results = {}

    for fuzzer_type in FUZZER_TYPES:
        fuzzer_base = exp_path / "ar" / fuzzer_type

        if not fuzzer_base.exists():
            continue

        results[fuzzer_type] = {}

        # Initialize coverage metrics
        for metric in COVERAGE_METRICS:
            results[fuzzer_type][metric] = {}

        # Navigate through project/fuzzer_name structure
        for project_dir in fuzzer_base.iterdir():
            if not project_dir.is_dir():
                continue
            for fuzzer_name_dir in project_dir.iterdir():
                if not fuzzer_name_dir.is_dir():
                    continue
                # Iterate through trial numbers
                for trial_dir in fuzzer_name_dir.iterdir():
                    if not trial_dir.is_dir():
                        continue

                    trial_num = trial_dir.name
                    log_file = trial_dir / "findings" / "stats" / "fuzzer_log.json"

                    if not log_file.exists():
                        continue

                    try:
                        with open(log_file, 'r') as f:
                            log_data = json.load(f)

                        # Get the last entry (final coverage values)
                        if log_data:
                            final_entry = log_data[-1]
                            coverage_count = final_entry.get('coverage_count', {})

                            # Extract each coverage metric
                            for metric in COVERAGE_METRICS:
                                value = coverage_count.get(metric, 0)
                                results[fuzzer_type][metric][trial_num] = value

                    except Exception as e:
                        print(f"Warning: Error loading {log_file}: {e}", file=sys.stderr)

    return results

def compute_median_coverage(trial_data):
    """
    Compute median coverage across trials.
    trial_data: dict of {trial_num: value}
    Returns: median value
    """
    if not trial_data:
        return 0
    values = list(trial_data.values())
    return np.median(values)

def main():
    base_dir = Path(__file__).parent
    summary = {}

    # Process each experiment
    for exp_dir in EXPERIMENT_DIRS:
        exp_path = base_dir / exp_dir

        if not exp_path.exists():
            print(f"Warning: {exp_dir} does not exist", file=sys.stderr)
            continue

        target_name = extract_target_name(exp_dir)
        print(f"Processing {target_name}...", file=sys.stderr)

        # Extract final coverage for this experiment
        exp_coverage = extract_final_coverage_for_experiment(exp_path)

        # Compute medians across trials
        summary[target_name] = {}
        for fuzzer_type, metrics_data in exp_coverage.items():
            summary[target_name][fuzzer_type] = {}
            for metric, trial_data in metrics_data.items():
                median = compute_median_coverage(trial_data)
                summary[target_name][fuzzer_type][metric] = round(median, 2)

    # Output JSON
    json_output = json.dumps(summary, indent=2)
    print("\n=== JSON Output ===")
    print(json_output)

    # Save JSON to file
    json_file = base_dir / "final_coverage_summary.json"
    with open(json_file, 'w') as f:
        f.write(json_output)
    print(f"\nJSON saved to: {json_file}", file=sys.stderr)

    # Generate CSV
    csv_file = base_dir / "final_coverage_summary.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)

        # Header
        header = ["target", "fuzzer"] + COVERAGE_METRICS
        writer.writerow(header)

        # Data rows
        for target, fuzzer_data in sorted(summary.items()):
            for fuzzer_type, metrics in sorted(fuzzer_data.items()):
                row = [target, fuzzer_type]
                for metric in COVERAGE_METRICS:
                    row.append(metrics.get(metric, 0))
                writer.writerow(row)

    print(f"CSV saved to: {csv_file}", file=sys.stderr)

    # Print CSV preview
    print("\n=== CSV Output (preview) ===")
    with open(csv_file, 'r') as f:
        print(f.read())

if __name__ == "__main__":
    main()
