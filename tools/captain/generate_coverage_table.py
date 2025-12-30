#!/usr/bin/env python3
"""
Script to generate a coverage comparison table in JSON format.
- Edge fuzzer (baseline): Shows absolute path and edge values
- Other fuzzers: Shows percentage changes for both path and edge
Uses dummy_fuzzer_edge as baseline.

Usage: python3 generate_coverage_table.py
"""

import json
import sys
from pathlib import Path

# Fuzzer types in display order
FUZZER_TYPES = [
    "dummy_fuzzer_edge",
    "dummy_fuzzer_block",
    "dummy_fuzzer_path",
    "dummy_fuzzer_pfp",
    "dummy_fuzzer_quad"
]

# Prettier names for display
FUZZER_DISPLAY_NAMES = {
    "dummy_fuzzer_edge": "Edge",
    "dummy_fuzzer_block": "Block",
    "dummy_fuzzer_path": "Path",
    "dummy_fuzzer_pfp": "PFP",
    "dummy_fuzzer_quad": "Quad"
}

def load_coverage_data():
    """Load final coverage summary data."""
    base_dir = Path(__file__).parent
    input_file = base_dir / "final_coverage_summary.json"

    if not input_file.exists():
        print(f"Error: {input_file} does not exist", file=sys.stderr)
        print("Please run summarize_final_coverage.py first", file=sys.stderr)
        sys.exit(1)

    with open(input_file, 'r') as f:
        return json.load(f)

def format_percentage(value, baseline):
    """Format a value as percentage change from baseline."""
    if baseline == 0:
        return None
    pct_change = ((value - baseline) / baseline) * 100
    return round(pct_change, 1)

def generate_table_json(data):
    """Generate coverage comparison table as JSON."""
    baseline_fuzzer = "dummy_fuzzer_edge"

    # Collect all targets
    targets = sorted(data.keys())

    table_data = {}

    # Accumulate values for average calculation
    fuzzer_totals = {fuzzer: {'path': 0, 'edge': 0} for fuzzer in FUZZER_TYPES}
    target_count = len(targets)

    # Process each target
    for target in targets:
        target_data = data[target]
        target_row = {}

        # Get baseline values for this target
        baseline_path = target_data.get(baseline_fuzzer, {}).get('path', 0)
        baseline_edge = target_data.get(baseline_fuzzer, {}).get('edge', 0)

        for fuzzer in FUZZER_TYPES:
            if fuzzer not in target_data:
                continue

            path_val = target_data[fuzzer].get('path', 0)
            edge_val = target_data[fuzzer].get('edge', 0)

            # Accumulate for averages
            fuzzer_totals[fuzzer]['path'] += path_val
            fuzzer_totals[fuzzer]['edge'] += edge_val

            fuzzer_name = FUZZER_DISPLAY_NAMES.get(fuzzer, fuzzer)

            if fuzzer == baseline_fuzzer:
                # Show absolute values for baseline
                target_row[fuzzer_name] = {
                    "path": int(path_val),
                    "edge": int(edge_val)
                }
            else:
                # Show percentage change for both path and edge
                path_pct = format_percentage(path_val, baseline_path)
                edge_pct = format_percentage(edge_val, baseline_edge)
                target_row[fuzzer_name] = {
                    "path_pct": path_pct,
                    "edge_pct": edge_pct
                }

        table_data[target] = target_row

    # Calculate averages
    baseline_avg_path = fuzzer_totals[baseline_fuzzer]['path'] / target_count
    baseline_avg_edge = fuzzer_totals[baseline_fuzzer]['edge'] / target_count

    avg_row = {}
    for fuzzer in FUZZER_TYPES:
        avg_path = fuzzer_totals[fuzzer]['path'] / target_count
        avg_edge = fuzzer_totals[fuzzer]['edge'] / target_count

        fuzzer_name = FUZZER_DISPLAY_NAMES.get(fuzzer, fuzzer)

        if fuzzer == baseline_fuzzer:
            avg_row[fuzzer_name] = {
                "path": round(avg_path, 1),
                "edge": round(avg_edge, 1)
            }
        else:
            path_pct = format_percentage(avg_path, baseline_avg_path)
            edge_pct = format_percentage(avg_edge, baseline_avg_edge)
            avg_row[fuzzer_name] = {
                "path_pct": path_pct,
                "edge_pct": edge_pct
            }

    table_data["Average"] = avg_row

    return table_data

def main():
    data = load_coverage_data()
    table_json = generate_table_json(data)

    # Output JSON to stdout
    print(json.dumps(table_json, indent=2))

if __name__ == "__main__":
    main()
