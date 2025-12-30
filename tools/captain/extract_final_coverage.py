#!/usr/bin/env python3
"""
Script to extract final coverage values for each fuzzer, coverage type, and trial.
Usage: python3 extract_final_coverage.py <experiment_dir>
"""

import json
import sys
from pathlib import Path

# Fuzzer types to process
FUZZER_TYPES = [
    "dummy_fuzzer_block",
    "dummy_fuzzer_edge",
    "dummy_fuzzer_path",
    "dummy_fuzzer_pfp",
    "dummy_fuzzer_quad",
    "dummy_fuzzer_fun",
]

# Coverage metrics to extract
COVERAGE_METRICS = ["block", "edge", "path", "pfp", "quad", "rawpath"]

def extract_final_coverage(exp_dir):
    """
    Extract final coverage values for each fuzzer type, coverage metric, and trial.
    """
    exp_path = Path(exp_dir)

    if not exp_path.exists():
        print(f"Error: Experiment directory '{exp_dir}' does not exist", file=sys.stderr)
        return None

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

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 extract_final_coverage.py <experiment_dir>")
        print("Example: python3 extract_final_coverage.py exp-libpng_read_fuzzer-10-17")
        sys.exit(1)

    exp_dir = sys.argv[1]
    results = extract_final_coverage(exp_dir)

    if results:
        # Output as JSON to stdout
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
