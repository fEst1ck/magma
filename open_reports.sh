#!/bin/bash

# ==============================================================================
#
#          FILE:  open_reports.sh
#
#         USAGE:  ./open_reports.sh <path_to_experiment_directory>
#
#   DESCRIPTION:  This script opens all 'average_report.html' files within a
#                 given experiment directory.
#
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Gemini
#       CREATED:  2025-09-02
#      REVISION:  1.0
#
# ==============================================================================

# --- Check for script arguments ---
# Check if an argument (the experiment directory) is provided.
if [ -z "$1" ]; then
  echo "Usage: $0 <path_to_experiment_directory>"
  exit 1
fi

# Check if the provided path is a directory.
if [ ! -d "$1" ]; then
  echo "Error: Directory not found: $1"
  exit 1
fi

# --- Main script ---
# The experiment directory path provided as the first argument.
exp_dir=$1

# Find all 'average_report.html' files within the experiment's 'ar' directory
# and open them with the default application.
for f in "$exp_dir"/ar/dummy_fuzzer_*/*/*/average_report/average_report.html; do
  # Check if the file exists before trying to open it.
  if [ -f "$f" ]; then
    echo "Opening $f"
    xdg-open "$f"
  fi
done
