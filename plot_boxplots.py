#!/usr/bin/env python3

# ==============================================================================
#
#          FILE:  plot_boxplots.py
#
#         USAGE:  python3 plot_boxplots.py <path_to_experiment_directory>
#
#   DESCRIPTION:  This script generates box plots for each coverage metric to
#                 compare the performance of different fuzzers in a given
#                 experiment.
#
#       OPTIONS:  ---
#  REQUIREMENTS:  python3, matplotlib
#          BUGS:  ---
#         NOTES:  ----
#        AUTHOR:  Gemini
#       CREATED:  2025-09-02
#      REVISION:  2.0
#
# ==============================================================================

import json
import matplotlib.pyplot as plt
import sys
import os
import glob

def plot_coverage_boxplots(exp_dir):
    """
    Generates box plots for each coverage metric for each fuzzer in an experiment.
    """
    if not os.path.isdir(exp_dir):
        print(f"Error: Directory not found: {exp_dir}")
        return

    output_dir = exp_dir
    ar_dir = os.path.join(exp_dir, "ar")

    if not os.path.isdir(ar_dir):
        print(f"Error: 'ar' directory not found in {exp_dir}")
        return

    fuzzers = [d for d in os.listdir(ar_dir) if os.path.isdir(os.path.join(ar_dir, d)) and d.startswith("dummy_fuzzer_")]

    coverage_metrics = ["Block Coverage", "Edge Coverage", "Quad Coverage", "Path Coverage", "PFP Coverage", "Raw Path Coverage"]
    coverage_keys = ["block", "edge", "quad", "path", "pfp", "rawpath"]

    for metric, key in zip(coverage_metrics, coverage_keys):
        plt.figure(figsize=(12, 7))
        all_fuzzer_data = []
        fuzzer_names = []

        for fuzzer in fuzzers:
            fuzzer_data = []
            # Find all fuzzer_log.json files for this fuzzer
            log_files = glob.glob(os.path.join(ar_dir, fuzzer, "*", "*", "*", "findings", "stats", "fuzzer_log.json"))

            for log_file in log_files:
                with open(log_file, 'r') as f:
                    try:
                        log_data = json.load(f)
                        if log_data:
                            last_entry = log_data[-1]
                            if 'coverage_count' in last_entry and key in last_entry['coverage_count']:
                                fuzzer_data.append(last_entry['coverage_count'][key])
                    except json.JSONDecodeError:
                        print(f"Warning: Could not decode JSON from {log_file}")
                    except IndexError:
                        print(f"Warning: Empty or invalid log file: {log_file}")

            if fuzzer_data:
                all_fuzzer_data.append(fuzzer_data)
                fuzzer_names.append(fuzzer.replace("dummy_fuzzer_", ""))

        if all_fuzzer_data:
            plt.boxplot(all_fuzzer_data, tick_labels=fuzzer_names) # Changed labels to tick_labels
            plt.xlabel("Fuzzer")
            plt.ylabel(metric)
            plt.title(f"Distribution of {metric} Across Fuzzers")
            plt.xticks(rotation=45, ha='right')
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            output_image = os.path.join(output_dir, f"{metric.replace(' ', '_')}_boxplot.png")
            
            try:
                plt.savefig(output_image)
                print(f"Generated box plot: {output_image}")
            except Exception as e:
                print(f"Error saving chart for {metric}: {e}")
            finally:
                plt.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 plot_boxplots.py <path_to_experiment_directory>")
    else:
        plot_coverage_boxplots(sys.argv[1])