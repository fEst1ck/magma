#!/usr/bin/env python3
"""
Script to collect edge and path growth curves from experiments and generate LaTeX document.
"""

import os
import re
import shutil
from pathlib import Path

# Experiment directories to process
EXPERIMENT_DIRS = [
    "exp-libpng_read_fuzzer-10-17",
    "exp-exif-10-20",
    "exp-tiffcp-10-24",
    "exp-tiff_read_rgba_fuzzer-10-30",
    "exp-x509-11-02",
    "exp-server-11-05",
    "exp-libxml2_xml_read_memory_fuzzer-11-18",
    "exp-lua-11-19",
]

# Coverage metrics to collect
METRICS = ["edge", "path"]

# Output directory for growth curves
OUTPUT_DIR = "growth-curves"


def extract_target_name(exp_dir):
    """
    Extract target name from directory name.
    Example: exp-libpng_read_fuzzer-10-17 -> libpng_read_fuzzer
    """
    match = re.match(r'exp-(.+)-\d{2}-\d{2}', exp_dir)
    if match:
        return match.group(1)
    return exp_dir


def format_target_name_latex(target):
    """Format target name for LaTeX (escape underscores)."""
    return target.replace('_', '\\_')


def collect_growth_curves():
    """Collect edge and path growth curves from all experiments."""

    # Create output directory
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)
    print(f"Created output directory: {OUTPUT_DIR}")

    # Track collected files
    collected = []

    for exp_dir in EXPERIMENT_DIRS:
        exp_path = Path(exp_dir)

        if not exp_path.exists():
            print(f"Warning: Experiment directory not found: {exp_dir}")
            continue

        target_name = extract_target_name(exp_dir)
        print(f"\nProcessing {exp_dir} (target: {target_name})...")

        for metric in METRICS:
            # Look for the growth curve file
            source_file = exp_path / f"{target_name}-{metric}.png"

            if not source_file.exists():
                print(f"  Warning: File not found: {source_file}")
                continue

            # Copy to output directory
            dest_file = output_path / f"{target_name}-{metric}.png"
            shutil.copy2(source_file, dest_file)
            print(f"  Copied: {source_file} -> {dest_file}")

            collected.append((target_name, metric, dest_file.name))

    return collected


def generate_latex_document(collected_files):
    """Generate LaTeX document with all growth curves."""

    latex_lines = []

    # Document header
    latex_lines.append("\\documentclass{article}")
    latex_lines.append("\\usepackage{graphicx}")
    latex_lines.append("\\usepackage{subcaption}")
    latex_lines.append("\\usepackage{float}")
    latex_lines.append("")
    latex_lines.append("\\begin{document}")
    latex_lines.append("")

    # Group by target
    targets = {}
    for target, metric, filename in collected_files:
        if target not in targets:
            targets[target] = {}
        targets[target][metric] = filename

    # Generate figures
    for target in sorted(targets.keys()):
        metrics_dict = targets[target]

        # Check if we have both edge and path
        if "edge" in metrics_dict and "path" in metrics_dict:
            # Create a figure with two subfigures side by side
            latex_lines.append("\\begin{figure}[H]")
            latex_lines.append("\\centering")

            # Edge coverage
            latex_lines.append("\\begin{subfigure}{0.49\\textwidth}")
            latex_lines.append("\\centering")
            latex_lines.append(f"\\includegraphics[width=\\textwidth]{{growth-curves/{metrics_dict['edge']}}}")
            latex_lines.append("\\caption{Edge Coverage}")
            latex_lines.append("\\end{subfigure}")
            latex_lines.append("\\hfill")

            # Path coverage
            latex_lines.append("\\begin{subfigure}{0.49\\textwidth}")
            latex_lines.append("\\centering")
            latex_lines.append(f"\\includegraphics[width=\\textwidth]{{growth-curves/{metrics_dict['path']}}}")
            latex_lines.append("\\caption{Path Coverage}")
            latex_lines.append("\\end{subfigure}")

            latex_lines.append(f"\\caption{{Coverage growth over time for \\texttt{{{format_target_name_latex(target)}}}}}")
            latex_lines.append(f"\\label{{fig:growth-{target}}}")
            latex_lines.append("\\end{figure}")
            latex_lines.append("")
        else:
            # Create separate figures for available metrics
            for metric in ["edge", "path"]:
                if metric not in metrics_dict:
                    continue

                latex_lines.append("\\begin{figure}[H]")
                latex_lines.append("\\centering")
                latex_lines.append(f"\\includegraphics[width=0.8\\textwidth]{{growth-curves/{metrics_dict[metric]}}}")
                latex_lines.append(f"\\caption{{{metric.capitalize()} coverage growth over time for \\texttt{{{format_target_name_latex(target)}}}}}")
                latex_lines.append(f"\\label{{fig:growth-{target}-{metric}}}")
                latex_lines.append("\\end{figure}")
                latex_lines.append("")

    # Document footer
    latex_lines.append("\\end{document}")

    # Write to file
    output_file = Path("growth_curves.tex")
    with open(output_file, 'w') as f:
        f.write('\n'.join(latex_lines))

    print(f"\nLaTeX document generated: {output_file}")
    return output_file


def main():
    print("=" * 80)
    print("Collecting Growth Curves")
    print("=" * 80)

    # Collect growth curve files
    collected = collect_growth_curves()

    if not collected:
        print("\nNo growth curve files collected!")
        return

    print(f"\n{'=' * 80}")
    print(f"Collected {len(collected)} growth curve files")
    print("=" * 80)

    # Generate LaTeX document
    latex_file = generate_latex_document(collected)

    print("\n" + "=" * 80)
    print("Done!")
    print("=" * 80)
    print(f"\nGrowth curves directory: {OUTPUT_DIR}/")
    print(f"LaTeX document: {latex_file}")
    print(f"\nTo compile: pdflatex {latex_file}")


if __name__ == "__main__":
    main()
