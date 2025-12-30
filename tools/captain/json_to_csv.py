#!/usr/bin/env python3
"""
Script to convert JSON bug summary to CSV format.
Reads JSON from stdin and outputs CSV to stdout.
"""

import json
import csv
import sys

def main():
    # Read JSON from stdin
    data = json.load(sys.stdin)

    # Create CSV writer for stdout
    writer = csv.writer(sys.stdout)

    # Write header
    writer.writerow(['target', 'fuzzer_type', 'reached', 'triggered'])

    # Write data rows
    for target, fuzzer_data in data.items():
        if fuzzer_data is None:
            continue

        for fuzzer_type, stats in fuzzer_data.items():
            writer.writerow([
                target,
                fuzzer_type,
                stats.get('reached', 0),
                stats.get('triggered', 0)
            ])

if __name__ == "__main__":
    main()
