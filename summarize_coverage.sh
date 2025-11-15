#!/bin/bash

# ==============================================================================
#
#          FILE:  summarize_coverage.sh
#
#         USAGE:  ./summarize_coverage.sh <path_to_experiment_directory>
#
#   DESCRIPTION:  This script summarizes the final coverage values from all
#                 'average_report.html' files within a given experiment
#                 directory and saves the summary to a CSV file.
#
#       OPTIONS:  ---
#  REQUIREMENTS:  grep with Perl-compatible regular expressions (PCRE)
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Gemini
#       CREATED:  2025-09-02
#      REVISION:  2.0
#
# ==============================================================================

# --- Check for script arguments ---
if [ -z "$1" ]; then
  echo "Usage: $0 <path_to_experiment_directory>"
  exit 1
fi

if [ ! -d "$1" ]; then
  echo "Error: Directory not found: $1"
  exit 1
fi

# --- Main script ---
exp_dir=$1
output_csv="$exp_dir/coverage_summary.csv"

# Write CSV header
echo "Fuzzer,Block Coverage,Edge Coverage,Quad Coverage,Path Coverage,PFP Coverage,Raw Path Coverage" > "$output_csv"

# Find all average_report.html files
find "$exp_dir/ar" -type f -name average_report.html | while read report_file; do
  # Extract fuzzer name from the path
  fuzzer_name=$(echo "$report_file" | sed -n 's|.*/ar/\(dummy_fuzzer_[^/]*\)/.*|\1|p')

  # Extract coverage values using grep -oP
  block_coverage=$(grep -oP '<strong>Block Coverage:<\/strong> \K[0-9.]+' "$report_file")
  edge_coverage=$(grep -oP '<strong>Edge Coverage:<\/strong> \K[0-9.]+' "$report_file")
  quad_coverage=$(grep -oP '<strong>Quad Coverage:<\/strong> \K[0-9.]+' "$report_file")
  path_coverage=$(grep -oP '<strong>Path Coverage:<\/strong> \K[0-9.]+' "$report_file")
  pfp_coverage=$(grep -oP '<strong>PFP Coverage:<\/strong> \K[0-9.]+' "$report_file")
  raw_path_coverage=$(grep -oP '<strong>Raw Path Coverage:<\/strong> \K[0-9.]+' "$report_file")

  # Write data to CSV
  echo "$fuzzer_name,$block_coverage,$edge_coverage,$quad_coverage,$path_coverage,$pfp_coverage,$raw_path_coverage" >> "$output_csv"
done

echo "Coverage summary saved to $output_csv"