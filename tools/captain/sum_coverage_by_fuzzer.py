#!/usr/bin/env python3
"""
Script to compute sum of coverage for each fuzzer across all targets.
Reads from final_coverage_summary.json and outputs aggregated results.
Uses geometric mean for normalized coverage values.

Usage: python3 sum_coverage_by_fuzzer.py
"""

import json
import csv
import sys
from pathlib import Path
from scipy import stats

# Coverage metrics
COVERAGE_METRICS = ["block", "edge", "path", "pfp", "quad", "rawpath"]

# Fuzzer types
FUZZER_TYPES = [
    "dummy_fuzzer_block",
    "dummy_fuzzer_edge",
    "dummy_fuzzer_path",
    "dummy_fuzzer_pfp",
    "dummy_fuzzer_quad"
]

def main():
    base_dir = Path(__file__).parent
    input_file = base_dir / "final_coverage_summary.json"

    if not input_file.exists():
        print(f"Error: {input_file} does not exist", file=sys.stderr)
        print("Please run summarize_final_coverage.py first", file=sys.stderr)
        sys.exit(1)

    # Read the final coverage summary
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Initialize sums for each fuzzer (absolute values)
    fuzzer_sums = {}
    for fuzzer_type in FUZZER_TYPES:
        fuzzer_sums[fuzzer_type] = {metric: 0 for metric in COVERAGE_METRICS}

    # Initialize lists for normalized values (to compute geometric mean)
    normalized_values = {}
    for fuzzer_type in FUZZER_TYPES:
        normalized_values[fuzzer_type] = {metric: [] for metric in COVERAGE_METRICS}

    edge_fuzzer = "dummy_fuzzer_edge"

    # For each target: normalize and collect values
    for target, fuzzer_data in data.items():
        # First, get edge fuzzer values for this target as benchmark
        if edge_fuzzer not in fuzzer_data:
            print(f"Warning: {edge_fuzzer} not found in {target}, skipping normalization", file=sys.stderr)
            continue

        edge_metrics = fuzzer_data[edge_fuzzer]

        # Normalize each fuzzer by edge fuzzer for this target
        for fuzzer_type in FUZZER_TYPES:
            if fuzzer_type not in fuzzer_data:
                continue

            metrics = fuzzer_data[fuzzer_type]

            # Add to absolute sums
            for metric in COVERAGE_METRICS:
                value = metrics.get(metric, 0)
                fuzzer_sums[fuzzer_type][metric] += value

            # Normalize and collect values for geometric mean
            for metric in COVERAGE_METRICS:
                edge_value = edge_metrics.get(metric, 0)
                fuzzer_value = metrics.get(metric, 0)

                if edge_value > 0:
                    normalized_value = fuzzer_value / edge_value
                    normalized_values[fuzzer_type][metric].append(normalized_value)
                # If edge_value is 0, we skip this target for this metric

    # Compute geometric mean of normalized values
    normalized_means = {}
    for fuzzer_type in FUZZER_TYPES:
        normalized_means[fuzzer_type] = {}
        for metric in COVERAGE_METRICS:
            values = normalized_values[fuzzer_type][metric]
            if values:
                # Compute geometric mean
                geom_mean = stats.gmean(values)
                normalized_means[fuzzer_type][metric] = round(geom_mean, 4)
            else:
                normalized_means[fuzzer_type][metric] = 0

    # Output JSON (absolute values)
    json_output = json.dumps(fuzzer_sums, indent=2)
    print("\n=== JSON Output (Absolute Values) ===")
    print(json_output)

    # Save JSON to file
    json_file = base_dir / "coverage_sum_by_fuzzer.json"
    with open(json_file, 'w') as f:
        f.write(json_output)
    print(f"\nJSON saved to: {json_file}", file=sys.stderr)

    # Generate CSV
    csv_file = base_dir / "coverage_sum_by_fuzzer.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)

        # Header
        header = ["fuzzer"] + COVERAGE_METRICS
        writer.writerow(header)

        # Data rows
        for fuzzer_type in FUZZER_TYPES:
            row = [fuzzer_type]
            for metric in COVERAGE_METRICS:
                row.append(fuzzer_sums[fuzzer_type][metric])
            writer.writerow(row)

    print(f"CSV saved to: {csv_file}", file=sys.stderr)

    # Print CSV preview
    print("\n=== CSV Output (Absolute Values) ===")
    with open(csv_file, 'r') as f:
        print(f.read())

    # Output normalized JSON (geometric mean)
    normalized_json_output = json.dumps(normalized_means, indent=2)
    print("\n=== JSON Output (Geometric Mean of Normalized Coverage) ===")
    print(normalized_json_output)

    # Save normalized JSON to file
    normalized_json_file = base_dir / "coverage_geomean_by_fuzzer.json"
    with open(normalized_json_file, 'w') as f:
        f.write(normalized_json_output)
    print(f"\nNormalized (geomean) JSON saved to: {normalized_json_file}", file=sys.stderr)

    # Generate normalized CSV
    normalized_csv_file = base_dir / "coverage_geomean_by_fuzzer.csv"
    with open(normalized_csv_file, 'w', newline='') as f:
        writer = csv.writer(f)

        # Header
        header = ["fuzzer"] + COVERAGE_METRICS
        writer.writerow(header)

        # Data rows
        for fuzzer_type in FUZZER_TYPES:
            row = [fuzzer_type]
            for metric in COVERAGE_METRICS:
                row.append(normalized_means[fuzzer_type][metric])
            writer.writerow(row)

    print(f"Normalized (geomean) CSV saved to: {normalized_csv_file}", file=sys.stderr)

    # Print normalized CSV preview
    print("\n=== CSV Output (Geometric Mean of Normalized Coverage) ===")
    with open(normalized_csv_file, 'r') as f:
        print(f.read())

if __name__ == "__main__":
    main()
