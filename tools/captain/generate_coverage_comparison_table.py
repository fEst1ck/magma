#!/usr/bin/env python3
"""
Generate LaTeX table comparing coverage metrics across different fuzzing strategies.
Reads from final_coverage_summary.json and outputs a LaTeX table.
"""

import json
import sys
from typing import Dict, List, Tuple
import math


def calculate_percentage_change(baseline: float, value: float) -> float:
    """Calculate percentage change from baseline to value."""
    if baseline == 0:
        return 0.0
    return ((value - baseline) / baseline) * 100


def format_percentage(pct: float) -> str:
    """Format percentage with sign and 2 decimal places."""
    sign = "+" if pct > 0 else ""
    return f"${sign}{pct:.2f}\\%$"


def geometric_mean(values: List[float]) -> float:
    """Calculate geometric mean of a list of values."""
    if not values or any(v <= 0 for v in values):
        # For values that include zeros or negatives, use a different approach
        # Convert to ratios for percentage changes
        return 0.0
    product = 1.0
    for v in values:
        product *= v
    return product ** (1.0 / len(values))


def geometric_mean_percentage_change(percentages: List[float]) -> float:
    """Calculate geometric mean of percentage changes.

    Converts percentages to ratios, calculates geometric mean, then converts back.
    """
    if not percentages:
        return 0.0

    # Convert percentages to ratios (e.g., +10% -> 1.10, -10% -> 0.90)
    ratios = [1.0 + (pct / 100.0) for pct in percentages]

    # Calculate geometric mean of ratios
    product = 1.0
    for ratio in ratios:
        product *= ratio
    gm_ratio = product ** (1.0 / len(ratios))

    # Convert back to percentage
    return (gm_ratio - 1.0) * 100.0


def format_target_name(target: str) -> str:
    """Format target name with line breaks for long names.

    The newline (\\) is placed BETWEEN texttt blocks, not inside them.
    Underscores connecting parts are preserved outside texttt blocks.
    """
    # Add line breaks for long target names
    if len(target) > 15:
        parts = target.split('_')
        if len(parts) >= 4:
            # e.g., libxml2_xml_read_memory_fuzzer ->
            # \texttt{libxml2\_xml}\_\\\texttt{read\_memory}\\\texttt{\_fuzzer}
            line1 = '_'.join(parts[:2])
            line2 = '_'.join(parts[2:3])
            line3 = '_'.join(parts[3:])
            return (f"\\texttt{{{line1.replace('_', '\\_')}}}\\_\\\\"
                   f"\\texttt{{{line2.replace('_', '\\_')}}}\\\\"
                   f"\\texttt{{\\_{line3.replace('_', '\\_')}}}")
        elif len(parts) >= 2:
            # e.g., libpng_read_fuzzer -> \texttt{libpng}\_\\\texttt{read}\\\texttt{\_fuzzer}
            if len(parts) == 3:
                line1 = parts[0]
                line2 = parts[1]
                line3 = parts[2]
                return (f"\\texttt{{{line1}}}\\_\\\\"
                       f"\\texttt{{{line2}}}\\\\"
                       f"\\texttt{{\\_{line3}}}")
            else:
                # Only 2 parts
                line1 = parts[0]
                line2 = parts[1]
                return f"\\texttt{{{line1}}}\\_\\\\\\texttt{{\\_{line2}}}"

    # Short names - no line break
    return f"\\texttt{{{target.replace('_', '\\_')}}}"


def generate_table(json_file: str, output_file: str = None):
    """Generate LaTeX table from coverage summary JSON."""

    # Read the JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Define the fuzzer order and their display names
    fuzzers = [
        ('dummy_fuzzer_edge', 'Edge'),
        ('dummy_fuzzer_block', 'Block'),
        ('dummy_fuzzer_path', 'Path'),
        ('dummy_fuzzer_pfp', 'PFP'),
        ('dummy_fuzzer_quad', 'Hyper-Edge')
    ]

    # Metrics to compare
    metrics = ['path', 'edge']

    # Storage for table rows and averages
    rows = []

    # Calculate sums for averaging
    sums = {
        'edge_paths': 0,
        'edge_edges': 0,
        'block_path_pct': [],
        'block_edge_pct': [],
        'path_path_pct': [],
        'path_edge_pct': [],
        'pfp_path_pct': [],
        'pfp_edge_pct': [],
        'hyper-edge_path_pct': [],
        'hyper-edge_edge_pct': [],
    }

    # Process each target
    for target, target_data in sorted(data.items()):
        # Get baseline (edge fuzzer) values
        if 'dummy_fuzzer_edge' not in target_data:
            print(f"Warning: No edge fuzzer data for {target}, skipping", file=sys.stderr)
            continue

        baseline = target_data['dummy_fuzzer_edge']
        baseline_paths = baseline['path']
        baseline_edges = baseline['edge']

        # Store for average calculation
        sums['edge_paths'] += baseline_paths
        sums['edge_edges'] += baseline_edges

        # Build row data
        row_data = {
            'target': target,
            'edge_paths': int(baseline_paths),
            'edge_edges': int(baseline_edges),
        }

        # Calculate percentage changes for other fuzzers
        for fuzzer_key, fuzzer_name in fuzzers[1:]:  # Skip edge (baseline)
            if fuzzer_key not in target_data:
                print(f"Warning: No {fuzzer_name} fuzzer data for {target}", file=sys.stderr)
                row_data[f'{fuzzer_name.lower()}_path_pct'] = 0.0
                row_data[f'{fuzzer_name.lower()}_edge_pct'] = 0.0
                continue

            fuzzer_data = target_data[fuzzer_key]
            path_pct = calculate_percentage_change(baseline_paths, fuzzer_data['path'])
            edge_pct = calculate_percentage_change(baseline_edges, fuzzer_data['edge'])

            row_data[f'{fuzzer_name.lower()}_path_pct'] = path_pct
            row_data[f'{fuzzer_name.lower()}_edge_pct'] = edge_pct

            # Store for averaging
            sums[f'{fuzzer_name.lower()}_path_pct'].append(path_pct)
            sums[f'{fuzzer_name.lower()}_edge_pct'].append(edge_pct)

        rows.append(row_data)

    # Calculate averages using geometric mean
    n_targets = len(rows)

    # Geometric mean for absolute values
    edge_paths_values = [row['edge_paths'] for row in rows]
    edge_edges_values = [row['edge_edges'] for row in rows]
    avg_edge_paths = geometric_mean(edge_paths_values)
    avg_edge_edges = geometric_mean(edge_edges_values)

    # Generate LaTeX table
    latex_lines = []
    latex_lines.append("\\begin{table*}[t]")
    latex_lines.append("\\small")
    latex_lines.append("\\centering")
    latex_lines.append("\\caption{MAGMA: Edge coverage and percent change of Block, Path, PFP, and Hyper-Edge Coverage relative to Edge.}")
    latex_lines.append("\\label{tab:coverage-comparison}")
    latex_lines.append("\\setlength{\\tabcolsep}{4pt}")
    latex_lines.append("\\begin{tabular}{@{}p{2cm}cccccccccc@{}}")
    latex_lines.append("\\toprule")

    # Header
    latex_lines.append("\\textbf{Target} &")
    latex_lines.append("\\multicolumn{2}{c}{\\textbf{Edge Fuzzer}} &")
    latex_lines.append("\\multicolumn{2}{c}{\\textbf{Block Fuzzer}} &")
    latex_lines.append("\\multicolumn{2}{c}{\\textbf{PFP Fuzzer}} &")
    latex_lines.append("\\multicolumn{2}{c}{\\textbf{Hyper-Edge Fuzzer}} &")
    latex_lines.append("\\multicolumn{2}{c}{\\textbf{Path Fuzzer}} \\\\")

    latex_lines.append("\\cmidrule(lr){2-3} \\cmidrule(lr){4-5} \\cmidrule(lr){6-7} \\cmidrule(lr){8-9} \\cmidrule(lr){10-11}")

    # Sub-header
    latex_lines.append("& \\textbf{Paths} & \\textbf{Edges}")
    latex_lines.append("& \\textbf{Paths} & \\textbf{Edges}")
    latex_lines.append("& \\textbf{Paths} & \\textbf{Edges}")
    latex_lines.append("& \\textbf{Paths} & \\textbf{Edges}")
    latex_lines.append("& \\textbf{Paths} & \\textbf{Edges} \\\\")

    latex_lines.append("\\midrule")

    # Data rows (order: edge, block, pfp, hyper-edge, path)
    for row in rows:
        target_name = format_target_name(row['target'])
        line = f"{target_name} & {row['edge_paths']} & {row['edge_edges']}"

        for fuzzer_name in ['block', 'pfp', 'hyper-edge', 'path']:
            path_key = f'{fuzzer_name}_path_pct'
            edge_key = f'{fuzzer_name}_edge_pct'
            line += f" & {format_percentage(row[path_key])} & {format_percentage(row[edge_key])}"

        line += " \\\\"
        latex_lines.append(line)

    # Average row (using geometric mean)
    latex_lines.append("\\midrule")
    avg_line = f"\\textbf{{Geometric Mean}} & {avg_edge_paths:.1f} & {avg_edge_edges:.1f}"

    for fuzzer_name in ['block', 'pfp', 'hyper-edge', 'path']:
        path_key = f'{fuzzer_name}_path_pct'
        edge_key = f'{fuzzer_name}_edge_pct'

        # Use geometric mean for percentage changes
        avg_path_pct = geometric_mean_percentage_change(sums[path_key]) if sums[path_key] else 0
        avg_edge_pct = geometric_mean_percentage_change(sums[edge_key]) if sums[edge_key] else 0

        avg_line += f" & $\\mathbf{{{format_percentage(avg_path_pct)[1:-1]}}}$ & $\\mathbf{{{format_percentage(avg_edge_pct)[1:-1]}}}$"

    avg_line += " \\\\"
    latex_lines.append(avg_line)

    latex_lines.append("\\bottomrule")
    latex_lines.append("\\end{tabular}")
    latex_lines.append("\\end{table*}")

    # Output
    latex_output = "\n".join(latex_lines)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(latex_output)
        print(f"LaTeX table written to {output_file}")
    else:
        print(latex_output)

    return latex_output


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_coverage_comparison_table.py <json_file> [output_file]")
        sys.exit(1)

    json_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    generate_table(json_file, output_file)


if __name__ == "__main__":
    main()
