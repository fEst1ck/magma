#!/usr/bin/env python3
"""
Count how many bugs were reached and triggered by each fuzzer across trials.

Definitions:
------------
- For each fuzzer and each trial:
    - Each bug ID in trial["reached"] counts as 1 reach event.
    - Each bug ID in trial["triggered"] counts as 1 trigger event.
- The total for a fuzzer is the sum of all such events across all trials.

Example:
- BUG1 reached in trials 0,1,2 -> contributes 3 to "reached".
- BUG2 reached in trials 1,3 -> contributes 2.
Total reached = 5.

Input structure:
----------------
{
  "results": {
    "<fuzzer_name>": {
      "<benchmark>": {
        "<target>": {
          "<trial_id>": {
            "reached": { "BUG1": int, ... },
            "triggered": { "BUG1": int, ... }
          }
        }
      }
    }
  }
}

Output:
-------
{
  "<fuzzer_name>": {
    "reached": <int>,
    "triggered": <int>
  }
}

Usage:
------
    python count_reach_trigger.py results.json
"""

import json
import sys
from typing import Any, Dict


def count_reached_triggered(data: Dict[str, Any]) -> Dict[str, Dict[str, int]]:
    results = data.get("results", {})
    summary: Dict[str, Dict[str, int]] = {}

    for fuzzer_name, benchmarks in results.items():
        reached_total = 0
        triggered_total = 0

        for _bench, targets in benchmarks.items():
            for _target, trials in targets.items():
                for _trial_id, tdata in trials.items():

                    reached = tdata.get("reached", {}) or {}
                    triggered = tdata.get("triggered", {}) or {}

                    # Counting rule: each bug ID counts once per trial
                    reached_total += len(reached)
                    triggered_total += len(triggered)

        summary[fuzzer_name] = {
            "reached": reached_total,
            "triggered": triggered_total,
        }

    return summary


def main():
    # Read JSON (from file or stdin)
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    summary = count_reached_triggered(data)

    # Output JSON
    json.dump(summary, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
