#!/bin/bash

# ==============================================================================
#
#          FILE:  generate_full_report.sh
#
#         USAGE:  ./generate_full_report.sh [-o] <path_to_experiment_directory>
#
#   DESCRIPTION:  This script generates all plots for an experiment and then
#                 creates a single HTML report to view all the generated plots.
#                 Optionally, it can open the generated report automatically.
#
#       OPTIONS:  -o   Open the generated HTML report automatically.
#  REQUIREMENTS:  python3, matplotlib, plot_boxplots.py, generate_html_report.py
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Gemini
#       CREATED:  2025-09-02
#      REVISION:  2.0
#
# ==============================================================================

# --- Default values ---
open_report=false
exp_dir=""

# --- Parse command-line arguments ---
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -o)
      open_report=true
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
  echo "Usage: $0 [-o] <path_to_experiment_directory>"
  exit 1
fi

if [ ! -d "$exp_dir" ]; then
  echo "Error: Directory not found: $exp_dir"
  exit 1
fi

# --- Main script ---
echo "Generating plots for $exp_dir..."
python3 /home/zw/magma/plot_boxplots.py "$exp_dir"

echo "Generating HTML report for $exp_dir..."
python3 /home/zw/magma/generate_html_report.py "$exp_dir"

echo "Full report generation complete."

if [ "$open_report" = true ]; then
  report_path="$exp_dir/plots_report.html"
  if [ -f "$report_path" ]; then
    echo "Opening generated report: $report_path"
    xdg-open "$report_path"
  else
    echo "Error: Report file not found: $report_path"
  fi
fi