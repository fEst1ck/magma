#!/usr/bin/env python3

# ==============================================================================
#
#          FILE:  plot_coverage_comparison.py
#
#         USAGE:  python3 plot_coverage_comparison.py <path_to_coverage_summary.csv>
#
#   DESCRIPTION:  This script plots the data from a coverage summary CSV file,
#                 creating a bar chart for each coverage metric to compare
#                 the relative performance of different fuzzers.
#
#       OPTIONS:  ---
#  REQUIREMENTS:  python3, matplotlib
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Gemini
#       CREATED:  2025-09-02
#      REVISION:  2.0
#
# ==============================================================================

import csv
import matplotlib.pyplot as plt
import sys
import os

def plot_coverage_comparison(csv_file):
    """
    Reads a coverage summary CSV file and generates bar charts for each coverage metric.
    """
    if not os.path.exists(csv_file):
        print(f"Error: File not found: {csv_file}")
        return

    output_dir = os.path.dirname(csv_file)

    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        data = list(reader)

    fuzzers = [row[0] for row in data]

    for i in range(1, len(header)):
        column_name = header[i]
        try:
            values = [float(row[i]) for row in data]
        except (ValueError, IndexError) as e:
            print(f"Skipping column '{column_name}' due to a data error: {e}")
            continue

        # --- Normalization ---
        max_value = max(values)
        if max_value == 0:
            normalized_values = [0] * len(values)
        else:
            normalized_values = [(v / max_value) * 100 for v in values]

        output_image = os.path.join(output_dir, f"relative_{column_name.replace(' ', '_')}_comparison.png")

        plt.figure(figsize=(10, 6))
        bars = plt.bar(fuzzers, normalized_values, color='skyblue')
        plt.xlabel("Fuzzer", fontsize=12)
        plt.ylabel("Relative Performance (%)", fontsize=12)
        plt.title(f"Relative Comparison of {column_name}", fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.ylim(0, 110) # Set y-axis limit to 0-110%
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Add percentage labels on top of bars
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2.0, yval + 1, f'{yval:.1f}%', ha='center', va='bottom')

        plt.tight_layout()
        
        try:
            plt.savefig(output_image)
            print(f"Generated chart: {output_image}")
        except Exception as e:
            print(f"Error saving chart for {column_name}: {e}")
        finally:
            plt.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 plot_coverage_comparison.py <path_to_coverage_summary.csv>")
    else:
        plot_coverage_comparison(sys.argv[1])