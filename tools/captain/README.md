# Fuzzing Experiment Analysis Scripts

This directory contains scripts for analyzing fuzzing experiment results. These scripts process coverage data, bug statistics, and generate visualizations across multiple experiments.

## Directory Structure

Each experiment directory follows the pattern `exp-<target>-<date>` (e.g., `exp-libpng_read_fuzzer-10-17`):
- **bugs.json**: Detailed bug data (reached/triggered per fuzzer/trial)
- **num-bugs.json**: Summary of bugs (reached/triggered per fuzzer)
- **ar/**: Archive containing fuzzer results organized by fuzzer type, target, and trial
- **log/**: Build and container execution logs
- **Coverage plots**: PNG files showing coverage growth over time

## Dependencies

- Python 3
- numpy (for coverage growth plotting)
- matplotlib (for coverage growth plotting)
- scipy (for geometric mean calculation)

Install dependencies:
```bash
pip install numpy matplotlib scipy
# or with conda:
conda install numpy matplotlib scipy
```

## Scripts Overview

### 1. Bug Analysis Scripts

#### `summarize_bugs.py`
**Purpose**: Aggregates num-bugs.json files from all dated experiments into a single JSON summary.

**Usage**:
```bash
python3 summarize_bugs.py > bugs_summary.json
```

**Output**: JSON to stdout with structure:
```json
{
  "target_name": {
    "fuzzer_type": {
      "reached": count,
      "triggered": count
    }
  }
}
```

#### `json_to_csv.py`
**Purpose**: Converts JSON bug summary to CSV format.

**Usage**:
```bash
python3 summarize_bugs.py | python3 json_to_csv.py > bugs_summary.csv
```

**Output**: CSV with columns: target, fuzzer_type, reached, triggered

#### `compute_totals_by_metric.py`
**Purpose**: Computes total bugs reached/triggered for each fuzzer type across all targets.

**Usage**:
```bash
python3 summarize_bugs.py | python3 compute_totals_by_metric.py
```

**Output**: JSON showing aggregated bug counts per fuzzer type

---

### 2. Coverage Analysis Scripts

#### `extract_final_coverage.py`
**Purpose**: Extracts final coverage values for each fuzzer, coverage metric, and trial from a single experiment.

**Usage**:
```bash
python3 extract_final_coverage.py <experiment_dir>
# Example:
python3 extract_final_coverage.py exp-libpng_read_fuzzer-10-17
```

**Output**: JSON to stdout with structure:
```json
{
  "fuzzer_type": {
    "coverage_metric": {
      "trial_number": final_value
    }
  }
}
```

**Coverage metrics**: block, edge, path, pfp, quad, rawpath

#### `summarize_final_coverage.py`
**Purpose**: Summarizes final coverage across ALL experiments, computing median across trials.

**Usage**:
```bash
python3 summarize_final_coverage.py
```

**Output Files**:
- `final_coverage_summary.json`
- `final_coverage_summary.csv`

**Structure**: Median coverage per fuzzer per target (robust to outlier trials)

#### `normalize_coverage_by_target.py`
**Purpose**: Normalizes each target's fuzzer coverage by that target's edge fuzzer values.

**Usage**:
```bash
python3 normalize_coverage_by_target.py
```

**Input**: Requires `final_coverage_summary.json`

**Output Files**:
- `coverage_normalized_by_target.json`
- `coverage_normalized_by_target.csv`

**Note**: Edge fuzzer (dummy_fuzzer_edge) = 1.0 for all metrics per target

#### `sum_coverage_by_fuzzer.py`
**Purpose**: Aggregates coverage across all targets for each fuzzer type, with normalization using geometric mean.

**Usage**:
```bash
python3 sum_coverage_by_fuzzer.py
```

**Input**: Requires `final_coverage_summary.json`

**Output Files**:
- `coverage_sum_by_fuzzer.json` (absolute values)
- `coverage_sum_by_fuzzer.csv` (absolute values)
- `coverage_geomean_by_fuzzer.json` (geometric mean of normalized values)
- `coverage_geomean_by_fuzzer.csv` (geometric mean of normalized values)

**Normalization method**:
1. For each target: normalize each fuzzer by edge fuzzer
2. Compute geometric mean of normalized values across targets
3. Edge fuzzer = 1.0 (geometric mean of all 1.0s)

**Why geometric mean?**: Better for ratios and normalized values; less sensitive to outliers

---

### 3. Visualization Scripts

#### `plot_edge_coverage_growth.py`
**Purpose**: Generates coverage growth plots over time for all fuzzer types. Creates one plot per coverage metric.

**Usage**:
```bash
python3 plot_edge_coverage_growth.py <experiment_dir> [-m]
# Example (mean with std dev):
python3 plot_edge_coverage_growth.py exp-libpng_read_fuzzer-10-17
# Example (median without std dev):
python3 plot_edge_coverage_growth.py exp-libpng_read_fuzzer-10-17 -m
```

**Options**:
- `-m, --median`: Use median instead of mean (no std dev shading)

**Output Files** (in experiment directory):
- `<target>-block.png`
- `<target>-edge.png`
- `<target>-path.png`
- `<target>-pfp.png`
- `<target>-quad.png`
- `<target>-rawpath.png`

**Features**:
- Shows all 5 fuzzer types on each plot
- Default: Mean across trials with standard deviation shading
- With `-m`: Median across trials (no shading)
- X-axis: time in hours (4-hour intervals)
- Y-axis: coverage count for that metric

---

## Common Workflows

### Workflow 1: Analyze Bug Statistics
```bash
# Generate bug summary
python3 summarize_bugs.py > bugs_summary.json

# Convert to CSV
python3 summarize_bugs.py | python3 json_to_csv.py > bugs_summary.csv

# Get totals by fuzzer type
python3 summarize_bugs.py | python3 compute_totals_by_metric.py > bugs_by_fuzzer.json
```

### Workflow 2: Analyze Final Coverage
```bash
# Step 1: Generate summary across all experiments
python3 summarize_final_coverage.py

# Step 2: Normalize by target
python3 normalize_coverage_by_target.py

# Step 3: Sum by fuzzer with normalization
python3 sum_coverage_by_fuzzer.py
```

This produces:
- `final_coverage_summary.json/csv` - Median coverage per target (across trials)
- `coverage_normalized_by_target.json/csv` - Normalized per target
- `coverage_sum_by_fuzzer.json/csv` - Absolute sums
- `coverage_geomean_by_fuzzer.json/csv` - Geometric mean of normalized coverage

### Workflow 3: Generate Coverage Plots for All Experiments
```bash
# Generate plots for each experiment
for exp in exp-libpng_read_fuzzer-10-17 exp-tiff_read_rgba_fuzzer-10-30 exp-tiffcp-10-24 exp-x509-11-02; do
    python3 plot_edge_coverage_growth.py "$exp"
done
```

This generates 6 plots per experiment (one per coverage metric).

### Workflow 4: Extract Raw Coverage Data
```bash
# Extract from a single experiment
python3 extract_final_coverage.py exp-libpng_read_fuzzer-10-17 > libpng_coverage.json

# Extract from all experiments
for exp in exp-*-??-??; do
    name=$(echo "$exp" | sed 's/exp-\(.*\)-[0-9][0-9]-[0-9][0-9]/\1/')
    python3 extract_final_coverage.py "$exp" > "${name}_coverage.json"
done
```

---

## Fuzzer Types

All scripts analyze these fuzzer types:
- `dummy_fuzzer_block` - Block coverage guided fuzzer
- `dummy_fuzzer_edge` - Edge coverage guided fuzzer (baseline)
- `dummy_fuzzer_path` - Path coverage guided fuzzer
- `dummy_fuzzer_pfp` - PFP coverage guided fuzzer
- `dummy_fuzzer_quad` - Quad coverage guided fuzzer

## Coverage Metrics

All coverage analysis includes:
- **block**: Basic block coverage
- **edge**: Control flow edge coverage
- **path**: Path coverage
- **pfp**: Prime path coverage (PFP)
- **quad**: Quadruple coverage
- **rawpath**: Raw path coverage

---

## Experiment Directories

Active experiments (dated directories):
- `exp-libpng_read_fuzzer-10-17`
- `exp-tiff_read_rgba_fuzzer-10-30`
- `exp-tiffcp-10-24`
- `exp-x509-11-02`

Older experiments (undated, not processed by scripts):
- `exp-libpng`, `exp-libsndfile`, `exp-libtiff-12h`, etc.

---

## Output Files Summary

| File | Generated By | Description |
|------|-------------|-------------|
| `bugs_summary.json` | `summarize_bugs.py` | Bug statistics per target |
| `bugs_summary.csv` | `json_to_csv.py` | Bug statistics in CSV |
| `bugs_by_fuzzer.json` | `compute_totals_by_metric.py` | Bug totals by fuzzer |
| `final_coverage_summary.json` | `summarize_final_coverage.py` | Median coverage per target |
| `final_coverage_summary.csv` | `summarize_final_coverage.py` | Median coverage CSV |
| `coverage_normalized_by_target.json` | `normalize_coverage_by_target.py` | Per-target normalized coverage |
| `coverage_normalized_by_target.csv` | `normalize_coverage_by_target.py` | Per-target normalized CSV |
| `coverage_sum_by_fuzzer.json` | `sum_coverage_by_fuzzer.py` | Absolute coverage sums |
| `coverage_sum_by_fuzzer.csv` | `sum_coverage_by_fuzzer.py` | Absolute coverage sums CSV |
| `coverage_geomean_by_fuzzer.json` | `sum_coverage_by_fuzzer.py` | Geometric mean of normalized coverage |
| `coverage_geomean_by_fuzzer.csv` | `sum_coverage_by_fuzzer.py` | Geometric mean of normalized coverage CSV |
| `<target>-<metric>.png` | `plot_edge_coverage_growth.py` | Coverage growth plots |

---

## Notes

- **Normalization**: Always uses `dummy_fuzzer_edge` as the baseline (value = 1.0)
- **Trial aggregation**: Scripts use median across 4 trials (0, 1, 2, 3) per fuzzer (robust to outliers)
- **Time units**: Coverage plots use hours on x-axis (converted from seconds)
- **Data source**: All scripts read from the `ar/*/findings/stats/fuzzer_log.json` files

---

## Quick Reference

**Want to...**
- See bug statistics? → Run `summarize_bugs.py`
- Compare fuzzer performance? → Run `sum_coverage_by_fuzzer.py`
- Visualize coverage over time? → Run `plot_edge_coverage_growth.py`
- Get normalized per-target comparison? → Run `normalize_coverage_by_target.py`
- Extract raw trial data? → Run `extract_final_coverage.py`

**Typical analysis order**:
1. `summarize_final_coverage.py` (generates base data)
2. `normalize_coverage_by_target.py` (per-target normalization)
3. `sum_coverage_by_fuzzer.py` (aggregate comparison)
4. `plot_edge_coverage_growth.py` (visualizations)
