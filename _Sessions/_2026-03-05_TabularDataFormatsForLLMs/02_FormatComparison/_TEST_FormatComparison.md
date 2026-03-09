<DevSystem MarkdownTablesAllowed=true />

# TEST: Format Comparison

**Doc ID**: TBLF-TP02
**Goal**: Test 5 hypotheses across 8 formats and 5 models to determine format impact on scale limits
**Timeline**: Created 2026-03-09
**Target file**: `_Scripts/03_find_scale_limit.py`, `_Scripts/05_analyze_results.py`

**Depends on:**
- `_INFO_FormatComparison.md [TBLF-IN02]` for hypotheses and prior evidence
- `_SPEC_FormatComparison.md [TBLF-SP02]` for test framework specification
- `_INFO_CSVScaleLimits.md [TBLF-IN01]` for CSV baseline scale limits

## Executive Summary

**Status**: 0/35 tests complete. Ready for execution.

### CSV Baselines (from Test 01)

| Model | Effort | CSV Scale Limit | Time/req | Cost/req |
|-------|--------|-----------------|----------|----------|
| gpt-5-mini | medium | 500 | ~3.5 min | $0.034 |
| gpt-5 | low | 356 | ~2.4 min | $0.05 |
| gpt-5.2 | medium | 215 | ~1 min | $0.031 |
| claude-opus | medium | 177 | ~1.6 min | $0.00* |
| claude-sonnet | medium | 168 | ~1.4 min | $0.040 |

*Cost tracking error

### Hypothesis Status

| ID | Hypothesis | Status | Evidence |
|----|------------|--------|----------|
| H2 | JSON not optimal despite structure | Pending | - |
| H3 | Format preferences differ by model family | Pending | - |
| H4 | Optimal format depends on complexity | Pending | - |
| H5 | Token-efficient formats enable higher scale | Pending | - |
| H6 | Key-value outperforms structured formats | Pending | - |

### Results Table (All Tests)

| Model | Format | Scale Limit | vs CSV | Time/req | Cost/req | Status |
|-------|--------|-------------|--------|----------|----------|--------|
| gpt-5-mini | csv_quoted | 500 | baseline | ~3.5 min | $0.034 | Baseline |
| gpt-5-mini | csv_raw | - | - | - | - | Pending |
| gpt-5-mini | kv_colon_space | - | - | - | - | Pending |
| gpt-5-mini | markdown_table | - | - | - | - | Pending |
| gpt-5-mini | json | - | - | - | - | Pending |
| gpt-5-mini | xml | - | - | - | - | Pending |
| gpt-5-mini | yaml | - | - | - | - | Pending |
| gpt-5-mini | toml | - | - | - | - | Pending |
| gpt-5 | csv_quoted | 356 | baseline | ~2.4 min | $0.05 | Baseline |
| gpt-5 | csv_raw | - | - | - | - | Pending |
| gpt-5 | kv_colon_space | - | - | - | - | Pending |
| gpt-5 | markdown_table | - | - | - | - | Pending |
| gpt-5 | json | - | - | - | - | Pending |
| gpt-5 | xml | - | - | - | - | Pending |
| gpt-5 | yaml | - | - | - | - | Pending |
| gpt-5 | toml | - | - | - | - | Pending |
| gpt-5.2 | csv_quoted | 215 | baseline | ~1 min | $0.031 | Baseline |
| gpt-5.2 | csv_raw | - | - | - | - | Pending |
| gpt-5.2 | kv_colon_space | - | - | - | - | Pending |
| gpt-5.2 | markdown_table | - | - | - | - | Pending |
| gpt-5.2 | json | - | - | - | - | Pending |
| gpt-5.2 | xml | - | - | - | - | Pending |
| gpt-5.2 | yaml | - | - | - | - | Pending |
| gpt-5.2 | toml | - | - | - | - | Pending |
| claude-opus | csv_quoted | 177 | baseline | ~1.6 min | $0.00* | Baseline |
| claude-opus | csv_raw | - | - | - | - | Pending |
| claude-opus | kv_colon_space | - | - | - | - | Pending |
| claude-opus | markdown_table | - | - | - | - | Pending |
| claude-opus | json | - | - | - | - | Pending |
| claude-opus | xml | - | - | - | - | Pending |
| claude-opus | yaml | - | - | - | - | Pending |
| claude-opus | toml | - | - | - | - | Pending |
| claude-sonnet | csv_quoted | 168 | baseline | ~1.4 min | $0.040 | Baseline |
| claude-sonnet | csv_raw | - | - | - | - | Pending |
| claude-sonnet | kv_colon_space | - | - | - | - | Pending |
| claude-sonnet | markdown_table | - | - | - | - | Pending |
| claude-sonnet | json | - | - | - | - | Pending |
| claude-sonnet | xml | - | - | - | - | Pending |
| claude-sonnet | yaml | - | - | - | - | Pending |
| claude-sonnet | toml | - | - | - | - | Pending |

**Total: 35 new tests** (5 models × 7 new formats, csv_quoted baseline from Test 01)

## MUST-NOT-FORGET

- Use CSV baseline as starting point for binary search (faster convergence)
- Same seed (42), columns, filters as Test 01 - only format changes
- Do NOT re-run CSV tests - use Test 01 baselines
- Capture per-request metrics: time/req, cost/req (NOT totals)
- Run cheapest model (gpt-5.2) first to validate format functions

## Table of Contents

1. [Overview](#1-overview)
2. [Test Matrix](#2-test-matrix)
3. [Hypothesis Testing Strategy](#3-hypothesis-testing-strategy)
4. [Test Execution Order](#4-test-execution-order)
5. [Test Configurations](#5-test-configurations)
6. [Metrics Collection](#6-metrics-collection)
7. [Verification Checklist](#7-verification-checklist)
8. [Document History](#8-document-history)

## 1. Overview

### 1.1 Research Questions

1. Does token efficiency correlate with scale limits? (csv_raw 1.0x vs xml 2.1x)
2. Do structured formats (JSON, XML) aid or hinder comprehension?
3. Do format preferences differ between model families (GPT vs Claude)?

### 1.2 Format Token Efficiency

| Format | Size (300 rows) | Relative | Hypothesis |
|--------|-----------------|----------|------------|
| csv_raw | 148 KB | 1.00x | Best scale (most compact) |
| csv_quoted | 156 KB | 1.06x | Baseline |
| markdown_table | 197 KB | 1.33x | - |
| kv_colon_space | 217 KB | 1.47x | May match CSV (TK-001) |
| toml | 235 KB | 1.59x | - |
| yaml | 249 KB | 1.68x | Structured, may help |
| json | 269 KB | 1.82x | Structured, may help |
| xml | 314 KB | 2.12x | Worst scale (most verbose) |

### 1.3 Expected Outcomes

**If H5 confirmed (token efficiency):**
- csv_raw > xml by ~2x in scale limit
- Scale limit inversely proportional to token size

**If H6 confirmed (key-value outperforms):**
- kv_colon_space >= JSON, XML, YAML
- Format type matters more than token count

**If H3 confirmed (model family differs):**
- GPT-5 and Claude have different optimal formats
- No universal "best format"

## 2. Test Matrix

### 2.1 Models (5)

| Model | Effort | CSV Baseline | Start Row |
|-------|--------|--------------|-----------|
| gpt-5-mini | medium | 500 | 500 |
| gpt-5 | low | 356 | 356 |
| gpt-5.2 | medium | 215 | 215 |
| claude-opus | medium | 177 | 177 |
| claude-sonnet | medium | 168 | 168 |

### 2.2 Formats (7 new + 1 baseline)

| Format | File Ext | Notes |
|--------|----------|-------|
| csv_quoted | .csv | Baseline (Test 01) |
| csv_raw | .csv | Unquoted CSV |
| kv_colon_space | .txt | Key: value pairs |
| markdown_table | .md | Markdown table |
| json | .json | JSON array |
| xml | .xml | XML records |
| yaml | .yaml | YAML list |
| toml | .toml | TOML array |

### 2.3 Test ID Mapping

| Test ID | Model | Format | Hypotheses |
|---------|-------|--------|------------|
| F01 | gpt-5-mini | csv_raw | H5 |
| F02 | gpt-5-mini | kv_colon_space | H6 |
| F03 | gpt-5-mini | markdown_table | H5 |
| F04 | gpt-5-mini | json | H2, H5 |
| F05 | gpt-5-mini | xml | H5 |
| F06 | gpt-5-mini | yaml | H2 |
| F07 | gpt-5-mini | toml | H5 |
| F08 | gpt-5 | csv_raw | H3, H5 |
| F09 | gpt-5 | kv_colon_space | H3, H6 |
| F10 | gpt-5 | markdown_table | H3 |
| F11 | gpt-5 | json | H2, H3 |
| F12 | gpt-5 | xml | H3, H5 |
| F13 | gpt-5 | yaml | H2, H3 |
| F14 | gpt-5 | toml | H3 |
| F15 | gpt-5.2 | csv_raw | H5 |
| F16 | gpt-5.2 | kv_colon_space | H6 |
| F17 | gpt-5.2 | markdown_table | H5 |
| F18 | gpt-5.2 | json | H2 |
| F19 | gpt-5.2 | xml | H5 |
| F20 | gpt-5.2 | yaml | H2 |
| F21 | gpt-5.2 | toml | H5 |
| F22 | claude-opus | csv_raw | H3, H5 |
| F23 | claude-opus | kv_colon_space | H3, H6 |
| F24 | claude-opus | markdown_table | H3 |
| F25 | claude-opus | json | H2, H3 |
| F26 | claude-opus | xml | H3, H5 |
| F27 | claude-opus | yaml | H2, H3 |
| F28 | claude-opus | toml | H3 |
| F29 | claude-sonnet | csv_raw | H3, H5 |
| F30 | claude-sonnet | kv_colon_space | H3, H6 |
| F31 | claude-sonnet | markdown_table | H3 |
| F32 | claude-sonnet | json | H2, H3 |
| F33 | claude-sonnet | xml | H3, H5 |
| F34 | claude-sonnet | yaml | H2, H3 |
| F35 | claude-sonnet | toml | H3 |

**Total: 35 tests**

## 3. Hypothesis Testing Strategy

### 3.1 H2: JSON Not Optimal

**Test**: Compare JSON scale limit vs CSV and Markdown for each model.

**Expected**: CSV >= JSON (GPT-4 preferred Markdown over JSON in Microsoft/MIT 2024)

**Data needed**: F04, F06, F11, F13, F18, F20, F25, F27, F32, F34

### 3.2 H3: Model Family Differences

**Test**: Compare format rankings between GPT-5 models and Claude models.

**Expected**: Different optimal formats for GPT vs Claude

**Data needed**: All GPT tests (F01-F21) vs all Claude tests (F22-F35)

### 3.3 H5: Token Efficiency

**Test**: Compare csv_raw (1.0x) vs xml (2.12x) scale limits.

**Expected**: csv_raw > xml by ~2x

**Data needed**: F01, F05, F08, F12, F15, F19, F22, F26, F29, F33

### 3.4 H6: Key-Value Outperforms

**Test**: Compare kv_colon_space vs JSON, XML, YAML.

**Expected**: kv_colon_space >= structured formats

**Data needed**: F02, F04, F05, F06, F09, F11, F12, F13, F16, F18, F19, F20, F23, F25, F26, F27, F30, F32, F33, F34

## 4. Test Execution Order

### 4.1 Phase 1: Setup Validation (1 test)

**Goal**: Verify format functions work before running all tests

```bash
cd E:\Dev\LLM-Research\_Sessions\_2026-03-05_TabularDataFormatsForLLMs\02_FormatComparison\_Scripts

# Test with cheapest model, smallest baseline
python 03_find_scale_limit.py \
  --test-path .. \
  --model gpt-5.2 \
  --format json \
  --initial-rows 215 \
  --tolerance 10
```

**Pass criteria**:
- Script completes without error
- JSON data file generated correctly
- At least one PASS and one FAIL observed

### 4.2 Phase 2: gpt-5.2 All Formats (7 tests)

**Goal**: Cheapest model, fastest validation of all formats

```bash
# Run all 7 formats for gpt-5.2 (F15-F21)
for format in csv_raw kv_colon_space markdown_table json xml yaml toml; do
  python 03_find_scale_limit.py --test-path .. --model gpt-5.2 --format $format --initial-rows 215 --tolerance 10
done
```

### 4.3 Phase 3: gpt-5-mini All Formats (7 tests)

**Goal**: Primary model with most TK-001 prior data

```bash
# Run all 7 formats for gpt-5-mini (F01-F07)
for format in csv_raw kv_colon_space markdown_table json xml yaml toml; do
  python 03_find_scale_limit.py --test-path .. --model gpt-5-mini --format $format --initial-rows 500 --tolerance 10
done
```

### 4.4 Phase 4: gpt-5 All Formats (7 tests)

```bash
# Run all 7 formats for gpt-5 (F08-F14)
for format in csv_raw kv_colon_space markdown_table json xml yaml toml; do
  python 03_find_scale_limit.py --test-path .. --model gpt-5 --format $format --initial-rows 356 --tolerance 10
done
```

### 4.5 Phase 5: Claude Models (14 tests)

```bash
# claude-opus (F22-F28)
for format in csv_raw kv_colon_space markdown_table json xml yaml toml; do
  python 03_find_scale_limit.py --test-path .. --model claude-opus --format $format --initial-rows 177 --tolerance 10
done

# claude-sonnet (F29-F35)
for format in csv_raw kv_colon_space markdown_table json xml yaml toml; do
  python 03_find_scale_limit.py --test-path .. --model claude-sonnet --format $format --initial-rows 168 --tolerance 10
done
```

### 4.6 Parallel Execution Strategy

**Cascade Limitation:** Windsurf can only run 3-4 background commands simultaneously.
Use PowerShell script `run_all_tests.ps1` for full parallelization outside Cascade.

**Time estimates per test (from Test 01 data):**

| Model | Time/req | Requests (~10 iter × 3 runs) | Total/test |
|-------|----------|------------------------------|------------|
| gpt-5-mini | ~3.5 min | ~30 | **~105 min** |
| gpt-5 | ~2.4 min | ~30 | **~72 min** |
| gpt-5.2 | ~1 min | ~30 | **~30 min** |
| claude-opus | ~1.6 min | ~30 | **~48 min** |
| claude-sonnet | ~1.4 min | ~30 | **~42 min** |

**API rate limits (tested in Test 01):**
- OpenAI: 120+ concurrent workers
- Anthropic: 60+ concurrent workers

**Parallel execution: Run all 35 tests simultaneously**

Each test uses ~3 internal workers, so total concurrent:
- OpenAI (3 models × 7 formats × 3 workers): 63 workers ✓
- Anthropic (2 models × 7 formats × 3 workers): 42 workers ✓

**Total time = slowest test = gpt-5-mini = ~2 hours**

### 4.7 35 Terminal Commands (Full Parallel)

```bash
cd E:\Dev\LLM-Research\_Sessions\_2026-03-05_TabularDataFormatsForLLMs\02_FormatComparison\_Scripts

# gpt-5-mini (7 terminals) - baseline 500, ~105 min each
python 03_find_scale_limit.py --test-path .. --model gpt-5-mini --format csv_raw --initial-rows 500 --reasoning-effort medium
python 03_find_scale_limit.py --test-path .. --model gpt-5-mini --format kv_colon_space --initial-rows 500 --reasoning-effort medium
python 03_find_scale_limit.py --test-path .. --model gpt-5-mini --format markdown_table --initial-rows 500 --reasoning-effort medium
python 03_find_scale_limit.py --test-path .. --model gpt-5-mini --format json --initial-rows 500 --reasoning-effort medium
python 03_find_scale_limit.py --test-path .. --model gpt-5-mini --format xml --initial-rows 500 --reasoning-effort medium
python 03_find_scale_limit.py --test-path .. --model gpt-5-mini --format yaml --initial-rows 500 --reasoning-effort medium
python 03_find_scale_limit.py --test-path .. --model gpt-5-mini --format toml --initial-rows 500 --reasoning-effort medium

# gpt-5 (7 terminals) - baseline 356, ~72 min each
python 03_find_scale_limit.py --test-path .. --model gpt-5 --format csv_raw --initial-rows 356 --reasoning-effort low
python 03_find_scale_limit.py --test-path .. --model gpt-5 --format kv_colon_space --initial-rows 356 --reasoning-effort low
python 03_find_scale_limit.py --test-path .. --model gpt-5 --format markdown_table --initial-rows 356 --reasoning-effort low
python 03_find_scale_limit.py --test-path .. --model gpt-5 --format json --initial-rows 356 --reasoning-effort low
python 03_find_scale_limit.py --test-path .. --model gpt-5 --format xml --initial-rows 356 --reasoning-effort low
python 03_find_scale_limit.py --test-path .. --model gpt-5 --format yaml --initial-rows 356 --reasoning-effort low
python 03_find_scale_limit.py --test-path .. --model gpt-5 --format toml --initial-rows 356 --reasoning-effort low

# gpt-5.2 (7 terminals) - baseline 215, ~30 min each
python 03_find_scale_limit.py --test-path .. --model gpt-5.2 --format csv_raw --initial-rows 215 --reasoning-effort medium
python 03_find_scale_limit.py --test-path .. --model gpt-5.2 --format kv_colon_space --initial-rows 215 --reasoning-effort medium
python 03_find_scale_limit.py --test-path .. --model gpt-5.2 --format markdown_table --initial-rows 215 --reasoning-effort medium
python 03_find_scale_limit.py --test-path .. --model gpt-5.2 --format json --initial-rows 215 --reasoning-effort medium
python 03_find_scale_limit.py --test-path .. --model gpt-5.2 --format xml --initial-rows 215 --reasoning-effort medium
python 03_find_scale_limit.py --test-path .. --model gpt-5.2 --format yaml --initial-rows 215 --reasoning-effort medium
python 03_find_scale_limit.py --test-path .. --model gpt-5.2 --format toml --initial-rows 215 --reasoning-effort medium

# claude-opus (7 terminals) - baseline 177, ~48 min each
python 03_find_scale_limit.py --test-path .. --model claude-opus-4-5-20251101 --format csv_raw --initial-rows 177
python 03_find_scale_limit.py --test-path .. --model claude-opus-4-5-20251101 --format kv_colon_space --initial-rows 177
python 03_find_scale_limit.py --test-path .. --model claude-opus-4-5-20251101 --format markdown_table --initial-rows 177
python 03_find_scale_limit.py --test-path .. --model claude-opus-4-5-20251101 --format json --initial-rows 177
python 03_find_scale_limit.py --test-path .. --model claude-opus-4-5-20251101 --format xml --initial-rows 177
python 03_find_scale_limit.py --test-path .. --model claude-opus-4-5-20251101 --format yaml --initial-rows 177
python 03_find_scale_limit.py --test-path .. --model claude-opus-4-5-20251101 --format toml --initial-rows 177

# claude-sonnet (7 terminals) - baseline 168, ~42 min each
python 03_find_scale_limit.py --test-path .. --model claude-sonnet-4-5-20250929 --format csv_raw --initial-rows 168
python 03_find_scale_limit.py --test-path .. --model claude-sonnet-4-5-20250929 --format kv_colon_space --initial-rows 168
python 03_find_scale_limit.py --test-path .. --model claude-sonnet-4-5-20250929 --format markdown_table --initial-rows 168
python 03_find_scale_limit.py --test-path .. --model claude-sonnet-4-5-20250929 --format json --initial-rows 168
python 03_find_scale_limit.py --test-path .. --model claude-sonnet-4-5-20250929 --format xml --initial-rows 168
python 03_find_scale_limit.py --test-path .. --model claude-sonnet-4-5-20250929 --format yaml --initial-rows 168
python 03_find_scale_limit.py --test-path .. --model claude-sonnet-4-5-20250929 --format toml --initial-rows 168
```

### 4.8 Time Comparison

| Strategy | Terminals | Total Time |
|----------|-----------|------------|
| Sequential | 1 | ~12 hours |
| Per model (5 groups) | 5 | ~2.5 hours |
| **All parallel** | **35** | **~2 hours** |

### 4.9 Phase 6: Analysis

```bash
python 05_analyze_results.py --test-path .. --output format_comparison_report.md
```

## 5. Test Configurations

### 5.1 Format-Specific Config Template

Each format has a config template: `test-config-template-{format}.json`

```json
{
  "data_generation": {
    "output_format": "json",
    "seed": 42,
    "number_of_columns": 7
  },
  "execution": {
    "model": "gpt-5-mini",
    "reasoning_effort": "medium"
  }
}
```

### 5.2 Command Line Override

```bash
python 03_find_scale_limit.py \
  --test-path .. \
  --model gpt-5-mini \
  --format json \
  --initial-rows 500 \
  --tolerance 10 \
  --verify-runs 3
```

## 6. Metrics Collection

### 6.1 Per-Request Metrics (Required)

| Metric | Source | Unit |
|--------|--------|------|
| time_per_request | response_time / runs | seconds |
| cost_per_request | total_cost / runs | USD |
| input_tokens | API response | tokens |
| output_tokens | API response | tokens |

### 6.2 Scale Limit Metrics

| Metric | Source |
|--------|--------|
| max_reliable_rows | Binary search result |
| vs_csv_baseline | (format_limit / csv_limit) × 100% |
| failure_mode | comprehension or truncation |
| context_utilization_pct | tokens_used / max_context |

### 6.3 Result File Format

```json
{
  "model": "gpt-5-mini",
  "format": "json",
  "scale_limit": 450,
  "csv_baseline": 500,
  "vs_baseline_pct": 90,
  "avg_time_per_request_sec": 45.2,
  "avg_cost_per_request_usd": 0.038,
  "failure_mode": "comprehension",
  "context_utilization_pct": 5.2
}
```

## 7. Verification Checklist

- [ ] All 8 format functions generate correct output
- [ ] Same seed produces identical records across formats
- [ ] Binary search starts at CSV baseline (not default 300)
- [ ] Per-request metrics captured (time, cost)
- [ ] Results comparable to Test 01 CSV baselines
- [ ] At least one test per format completed
- [ ] At least one test per model completed
- [ ] Hypothesis verdicts updated after analysis

## 8. Document History

**[2026-03-09 20:49]**
- Added: Cascade limitation note (3-4 background commands max)
- Added: `run_all_tests.ps1` PowerShell script for full parallelization
- Fixed: Folder naming now includes format to prevent conflicts
- Started: gpt-5.2 tests (3 running)

**[2026-03-09 20:36]**
- Added: Section 4.6 Parallel Execution Strategy with realistic time estimates from Test 01
- Added: Section 4.7 with all 35 terminal commands for full parallel execution
- Added: Section 4.8 Time Comparison (sequential vs parallel)
- Time estimate: ~2 hours with full parallelization (slowest = gpt-5-mini ~105 min)

**[2026-03-09 20:19]**
- Initial test plan created
- 35 tests defined (5 models × 7 formats)
- Hypothesis mapping to test IDs
- Per-request metrics focus (not totals)
