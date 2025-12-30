#!/usr/bin/env python3
"""
Script to summarize num-bugs.json files from all fuzzing experiments.
Outputs the summary as JSON to stdout.
"""

import json
import os
import sys
import re
from pathlib import Path

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
    "exp-sqlite3_fuzz-11-23",
]

def extract_target_name(exp_dir):
    """
    Extract target name from directory name.
    Example: exp-libpng_read_fuzzer-10-17 -> libpng_read_fuzzer
    """
    match = re.match(r'exp-(.+)-\d{2}-\d{2}', exp_dir)
    if match:
        return match.group(1)
    return exp_dir

def main():
    base_dir = Path(__file__).parent
    summary = {}

    for exp_dir in EXPERIMENT_DIRS:
        exp_path = base_dir / exp_dir
        num_bugs_file = exp_path / "num-bugs.json"

        # Extract target name from directory name
        target_name = extract_target_name(exp_dir)

        if num_bugs_file.exists():
            with open(num_bugs_file, 'r') as f:
                data = json.load(f)
                summary[target_name] = data
        else:
            summary[target_name] = None

    # Write summary to stdout as JSON
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
