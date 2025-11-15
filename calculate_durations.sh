#!/bin/bash

# ==============================================================================
#
#          FILE:  calculate_durations.sh
#
#         USAGE:  ./calculate_durations.sh [--from-fuzzer-log] <path_to_experiment_directory>
#
#   DESCRIPTION:  This script calculates the run time of each trial in a given
#                 experiment directory. It supports two methods for calculating
#                 the runtime:
#                 1. Default method: Calculates the duration from the 'monitor'
#                    directory by subtracting the first timestamp from the last.
#                 2. --from-fuzzer-log: Gets the duration from the
#                    'fuzzer_log.json' file.
#
#       OPTIONS:  --from-fuzzer-log   Use the fuzzer_log.json file to determine
#                                     the runtime.
#  REQUIREMENTS:  jq (JSON processor) if using --from-fuzzer-log
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Gemini
#       CREATED:  2025-09-02
#      REVISION:  4.0
#
# ==============================================================================

# --- Default values ---
from_fuzzer_log=false
exp_dir=""

# --- Parse command-line arguments ---
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --from-fuzzer-log)
      from_fuzzer_log=true
      shift # past argument
      ;;
    *)
      exp_dir="$1"
      shift # past value
      ;;
  esac
done


# --- Check for script arguments ---
if [ -z "$exp_dir" ]; then
  echo "Usage: $0 [--from-fuzzer-log] <path_to_experiment_directory>"
  exit 1
fi

if [ ! -d "$exp_dir" ]; then
  echo "Error: Directory not found: $exp_dir"
  exit 1
fi

# --- Main script ---
if [ "$from_fuzzer_log" = true ]; then
  # --- New logic: from fuzzer_log.json ---
  echo "Using fuzzer_log.json to determine runtime."
  find "$exp_dir/ar" -type f -name fuzzer_log.json | while read log_file; do
    duration=$(jq -r 'if .[-1] | has("runtime_seconds") then .[-1].runtime_seconds else empty end' "$log_file")
    if [ -n "$duration" ]; then
      trial_dir=$(dirname "$(dirname "$log_file")")
      echo "Trial: $trial_dir, Duration: $duration seconds"
    fi
  done
else
  # --- Original logic: from monitor directory ---
  echo "Using monitor directory to determine runtime."
  find "$exp_dir/ar" -type d -name monitor | while read monitor_dir; do
    first=$(ls -v "$monitor_dir" | head -n 1)
    last=$(ls -v "$monitor_dir" | tail -n 1)
    if [ -n "$first" ] && [ -n "$last" ]; then
      duration=$((last - first))
      echo "Trial: $monitor_dir, Duration: $duration seconds"
    fi
  done
fi