#!/usr/bin/env python3
"""
Script to compute normalized coverage for each target and fuzzer.
Normalizes each fuzzer by the edge fuzzer for that specific target.
Reads from final_coverage_summary.json and outputs normalized results.

Usage: python3 normalize_coverage_by_target.py
"""

import json
import csv
import sys
from pathlib import Path

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

    edge_fuzzer = "dummy_fuzzer_edge"
    normalized_data = {}

    # Normalize each target's fuzzers by that target's edge fuzzer
    for target, fuzzer_data in data.items():
        if edge_fuzzer not in fuzzer_data:
            print(f"Warning: {edge_fuzzer} not found in {target}, skipping", file=sys.stderr)
            continue

        edge_metrics = fuzzer_data[edge_fuzzer]
        normalized_data[target] = {}

        # Normalize each fuzzer by edge fuzzer for this target
        for fuzzer_type in FUZZER_TYPES:
            if fuzzer_type not in fuzzer_data:
                continue

            normalized_data[target][fuzzer_type] = {}
            fuzzer_metrics = fuzzer_data[fuzzer_type]

            for metric in COVERAGE_METRICS:
                edge_value = edge_metrics.get(metric, 0)
                fuzzer_value = fuzzer_metrics.get(metric, 0)

                if edge_value > 0:
                    normalized_value = fuzzer_value / edge_value
                    normalized_data[target][fuzzer_type][metric] = round(normalized_value, 4)
                else:
                    normalized_data[target][fuzzer_type][metric] = 0

    # Output JSON
    json_output = json.dumps(normalized_data, indent=2)
    print("\n=== JSON Output (Normalized by Edge Fuzzer per Target) ===")
    print(json_output)

    # Save JSON to file
    json_file = base_dir / "coverage_normalized_by_target.json"
    with open(json_file, 'w') as f:
        f.write(json_output)
    print(f"\nJSON saved to: {json_file}", file=sys.stderr)

    # Generate CSV
    csv_file = base_dir / "coverage_normalized_by_target.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)

        # Header
        header = ["target", "fuzzer"] + COVERAGE_METRICS
        writer.writerow(header)

        # Data rows
        for target in sorted(normalized_data.keys()):
            for fuzzer_type in FUZZER_TYPES:
                if fuzzer_type not in normalized_data[target]:
                    continue
                row = [target, fuzzer_type]
                for metric in COVERAGE_METRICS:
                    row.append(normalized_data[target][fuzzer_type].get(metric, 0))
                writer.writerow(row)

    print(f"CSV saved to: {csv_file}", file=sys.stderr)

    # Print CSV preview
    print("\n=== CSV Output (Normalized by Edge Fuzzer per Target) ===")
    with open(csv_file, 'r') as f:
        print(f.read())

if __name__ == "__main__":
    main()
