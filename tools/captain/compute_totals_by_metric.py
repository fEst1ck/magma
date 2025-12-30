#!/usr/bin/env python3
"""
Script to compute total bugs reached and triggered for each fuzzer type (metric).
Reads JSON from stdin and outputs JSON to stdout.
"""

import json
import sys

def main():
    # Read JSON from stdin
    data = json.load(sys.stdin)

    # Initialize totals dictionary
    totals = {}

    # Aggregate data by fuzzer type
    for target, fuzzer_data in data.items():
        if fuzzer_data is None:
            continue

        for fuzzer_type, stats in fuzzer_data.items():
            if fuzzer_type not in totals:
                totals[fuzzer_type] = {
                    'reached': 0,
                    'triggered': 0
                }

            totals[fuzzer_type]['reached'] += stats.get('reached', 0)
            totals[fuzzer_type]['triggered'] += stats.get('triggered', 0)

    # Output as JSON
    print(json.dumps(totals, indent=2))

if __name__ == "__main__":
    main()
