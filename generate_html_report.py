#!/usr/bin/env python3

# ==============================================================================
#
#          FILE:  generate_html_report.py
#
#         USAGE:  python3 generate_html_report.py <path_to_experiment_directory>
#
#   DESCRIPTION:  This script generates a single HTML file to view all plots
#                 (PNG images) within a given experiment directory.
#
#       OPTIONS:  ---
#  REQUIREMENTS:  python3
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Gemini
#       CREATED:  2025-09-02
#      REVISION:  1.0
#
# ==============================================================================

import os
import sys
import glob

def generate_html_report(exp_dir):
    """
    Generates a single HTML file to view all plots in the experiment directory.
    """
    if not os.path.isdir(exp_dir):
        print(f"Error: Directory not found: {exp_dir}")
        return

    output_html_file = os.path.join(exp_dir, "plots_report.html")

    # Find all PNG files in the experiment directory
    plot_files = glob.glob(os.path.join(exp_dir, "*.png"))
    plot_files.sort() # Sort files for consistent order

    with open(output_html_file, 'w') as f:
        f.write("<!DOCTYPE html>\n")
        f.write("<html lang='en'>\n")
        f.write("<head>\n")
        f.write("    <meta charset='UTF-8'>\n")
        f.write("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n")
        f.write(f"    <title>Plots Report for {os.path.basename(exp_dir)}</title>\n")
        f.write("    <style>\n")
        f.write("        body { font-family: sans-serif; margin: 20px; }\n")
        f.write("        .plot-container { margin-bottom: 40px; border: 1px solid #ccc; padding: 15px; border-radius: 8px; }\n")
        f.write("        img { max-width: 100%; height: auto; display: block; margin: 0 auto; }\n")
        f.write("        h2 { text-align: center; color: #333; }\n")
        f.write("    </style>\n")
        f.write("</head>\n")
        f.write("<body>\n")
        f.write(f"    <h1>Plots Report for {os.path.basename(exp_dir)}</h1>\n")

        if not plot_files:
            f.write("    <p>No plots found in this directory.</p>\n")
        else:
            for plot_file in plot_files:
                relative_path = os.path.basename(plot_file)
                plot_title = os.path.splitext(relative_path)[0].replace('_', ' ').title()
                f.write("    <div class='plot-container'>\n")
                f.write(f"        <h2>{plot_title}</h2>\n")
                f.write(f"        <img src='{relative_path}' alt='{plot_title}'>\n")
                f.write("    </div>\n")

        f.write("</body>\n")
        f.write("</html>\n")

    print(f"HTML report generated: {output_html_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 generate_html_report.py <path_to_experiment_directory>")
    else:
        generate_html_report(sys.argv[1])
