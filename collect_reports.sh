#!/bin/bash

# ==============================================================================
#
#          FILE:  collect_reports.sh
#
#         USAGE:  ./collect_reports.sh
#
#   DESCRIPTION:  This script collects generated HTML reports and their
#                 associated plot images from each experiment directory and
#                 copies them into a centralized './exp-reports' directory.
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

# --- Main script ---

# Create the top-level collection directory if it doesn't exist
mkdir -p ./exp-reports

# Find all experiment directories
for exp_dir in /home/zw/magma/tools/captain/exp-*; do
  if [ -d "$exp_dir" ]; then
    exp_name=$(basename "$exp_dir")
    dest_dir="./exp-reports/$exp_name"

    echo "Collecting reports for $exp_name into $dest_dir..."
    mkdir -p "$dest_dir"

    # Copy the HTML report
    html_report="$exp_dir/plots_report.html"
    if [ -f "$html_report" ]; then
      cp "$html_report" "$dest_dir/"
    else
      echo "Warning: HTML report not found for $exp_name: $html_report"
    fi

    # Copy all PNG plot files
    png_files=$(find "$exp_dir" -maxdepth 1 -type f -name "*.png")
    if [ -n "$png_files" ]; then
      cp $png_files "$dest_dir/"
    else
      echo "Warning: No PNG plots found for $exp_name."
    fi
  fi
done

echo "Report collection complete."
