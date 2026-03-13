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

**Status**: 48/48 tests complete.

### Test Setup

**IMPORTANT**: This test uses a **simplified dataset** (7 columns from 7 available) that differs from Test 01 (7 columns selected from 20 available). Results are **not directly comparable** to Test 01 baselines. See `TBLF-FL-005` in FAILS.md.

**Configuration:**
- 7 columns: id, name, department, salary, hire_date, is_active, email
- Filter: department = "Engineering" AND salary > 75000
- Seed: 42 (deterministic)
- Binary search with 3 runs per scale point

### Hypothesis Status

| ID | Hypothesis                                 | Source                 | Status          | Evidence                                       |
|----|--------------------------------------------|------------------------|-----------------|------------------------------------------------|
| H2 | JSON not optimal despite structure         | Microsoft/MIT 2024     | MIXED           | gpt-5.4/Claude: JSON BEST. Older GPT: mid-tier |
| H3 | Format preferences differ by model family  | Microsoft/MIT 2024     | **CONFIRMED**   | GPT prefers yaml/xml. Claude prefers json      |
| H4 | Optimal format depends on complexity       | Microsoft CFPO 2025    | INCONCLUSIVE    | Requires multi-complexity tests                |
| H5 | Token-efficient formats enable higher scale| Token efficiency theory| **CONTRADICTED**| xml (2.12x) beats csv (1.00x) on GPT           |
| H6 | Key-value outperforms structured formats   | TK-001 benchmark       | **CONTRADICTED**| Only true for gpt-5-mini                       |

### Results Table (All Tests)

Percentages relative to best format per model (100% = max scale limit).

**Columns:**
- **Scale** - Maximum reliable rows at 100% accuracy (3/3 runs passed)
- **vs Best** - Percentage relative to best format for this model (100% = top performer)
- **In (K)** - Input tokens in thousands at scale limit
- **Out (K)** - Output tokens in thousands at scale limit
- **Time** - Average time per request at scale limit
- **TPKC** - Time Per Kilo Cells (seconds) = time / (rows x 7 columns) x 1000
- **Cost** - Cost per request at scale limit
- **CPKC** - Cost Per Kilo Cells = cost / (rows x 7 columns) x 1000

**Why per-kilo-cell metrics?** Raw time and cost are measured at different scale limits (row counts). TPKC and CPKC normalize these to a common unit (1000 cells), making formats directly comparable regardless of their scale limit.

| Model      | Effort | Format         | Scale   | vs Best | In (K) | Out (K) | Time     | TPKC | Cost  | CPKC   |
|------------|--------|----------------|---------|---------|--------|---------|----------|------|-------|--------|
| gpt-5.4    | medium | json           | **702** | 100%    | -      | -       | ~2.9 min | 35s  | $0.93 | $0.189 |
| gpt-5.4    | medium | markdown_table | **554** | 79%     | -      | -       | ~3.0 min | 46s  | $0.54 | $0.139 |
| gpt-5.4    | medium | xml            | **546** | 78%     | -      | -       | ~3.0 min | 47s  | $0.63 | $0.165 |
| gpt-5.4    | medium | csv            | **523** | 75%     | -      | -       | ~2.5 min | 41s  | $0.53 | $0.145 |
| gpt-5.4    | medium | csv_quoted     | **523** | 75%     | -      | -       | ~2.5 min | 41s  | $0.53 | $0.145 |
| gpt-5.4    | medium | toml           | **523** | 75%     | -      | -       | ~2.9 min | 47s  | $0.53 | $0.145 |
| gpt-5.4    | medium | yaml           | **523** | 75%     | -      | -       | ~2.5 min | 41s  | $0.53 | $0.145 |
| gpt-5.4    | medium | kv_colon_space | **359** | 51%     | -      | -       | ~2.2 min | 52s  | $0.33 | $0.131 |
|            |        |                |         |         |        |         |          |      |       |        |
| gpt-5-mini | medium | kv_colon_space | **500** | 100%    | 98     | 42      | ~9.3 min | 159s | $0.13 | $0.037 |
| gpt-5-mini | medium | yaml           | **500** | 100%    | 110    | 44      | ~4.4 min | 76s  | $0.12 | $0.034 |
| gpt-5-mini | medium | csv_quoted     | **437** | 87%     | 62     | 39      | ~4.7 min | 92s  | $0.10 | $0.033 |
| gpt-5-mini | medium | json           | **335** | 67%     | 86     | 35      | ~5.1 min | 131s | $0.10 | $0.043 |
| gpt-5-mini | medium | xml            | **296** | 59%     | 87     | 42      | ~4.0 min | 116s | $0.10 | $0.048 |
| gpt-5-mini | medium | toml           | **296** | 59%     | 63     | 29      | ~3.7 min | 107s | $0.09 | $0.043 |
| gpt-5-mini | medium | csv            | **194** | 39%     | 28     | 27      | ~3.6 min | 159s | $0.07 | $0.052 |
| gpt-5-mini | medium | markdown_table | **163** | 33%     | 24     | 22      | ~2.2 min | 116s | $0.07 | $0.061 |
|            |        |                |         |         |        |         |          |      |       |        |
| gpt-5      | low    | yaml           | **333** | 100%    | 73     | 38      | ~2.6 min | 67s  | $0.42 | $0.180 |
| gpt-5      | low    | xml            | **327** | 98%     | 96     | 32      | ~3.2 min | 84s  | $0.42 | $0.183 |
| gpt-5      | low    | json           | **249** | 75%     | 64     | 32      | ~3.0 min | 103s | $0.37 | $0.212 |
| gpt-5      | low    | kv_colon_space | **238** | 71%     | 47     | 29      | ~3.9 min | 141s | $0.36 | $0.216 |
| gpt-5      | low    | csv_quoted     | **227** | 68%     | 33     | 23      | ~2.7 min | 102s | $0.32 | $0.201 |
| gpt-5      | low    | toml           | **216** | 65%     | 46     | 23      | ~2.4 min | 95s  | $0.34 | $0.225 |
| gpt-5      | low    | csv            | **166** | 50%     | 24     | 21      | ~2.3 min | 119s | $0.25 | $0.215 |
| gpt-5      | low    | markdown_table | **83**  | 25%     | 13     | 13      | ~2.4 min | 248s | $0.20 | $0.344 |
|            |        |                |         |         |        |         |          |      |       |        |
| gpt-5.2    | medium | csv_quoted     | **268** | 100%    | 39     | 20      | ~1.4 min | 45s  | $0.37 | $0.197 |
| gpt-5.2    | medium | xml            | **261** | 97%     | 77     | 24      | ~1.5 min | 49s  | $0.46 | $0.252 |
| gpt-5.2    | medium | json           | **241** | 90%     | 62     | 20      | ~1.2 min | 43s  | $0.40 | $0.237 |
| gpt-5.2    | medium | csv            | **215** | 80%     | 30     | 19      | ~1.3 min | 52s  | $0.34 | $0.226 |
| gpt-5.2    | medium | markdown_table | **154** | 57%     | 22     | 18      | ~1.1 min | 61s  | $0.29 | $0.269 |
| gpt-5.2    | medium | yaml           | **134** | 50%     | 30     | 10      | ~0.6 min | 38s  | $0.22 | $0.235 |
| gpt-5.2    | medium | kv_colon_space | **100** | 37%     | 20     | 6       | ~0.5 min | 43s  | $0.15 | $0.214 |
| gpt-5.2    | medium | toml           | **46**  | 17%     | 11     | 3       | ~0.4 min | 75s  | $0.12 | $0.373 |
|            |        |                |         |         |        |         |          |      |       |        |
| opus-4.5   | medium | json           | **265** | 100%    | 81     | 30      | ~1.8 min | 58s  | $1.23 | $0.663 |
| opus-4.5   | medium | yaml           | **259** | 98%     | 69     | 29      | ~1.7 min | 56s  | $1.03 | $0.568 |
| opus-4.5   | medium | csv            | **232** | 88%     | 38     | 29      | ~1.6 min | 59s  | $0.92 | $0.566 |
| opus-4.5   | medium | kv_colon_space | **226** | 85%     | 51     | 30      | ~1.7 min | 65s  | $0.98 | $0.619 |
| opus-4.5   | medium | markdown_table | **221** | 83%     | 38     | 28      | ~1.8 min | 70s  | $0.93 | $0.601 |
| opus-4.5   | medium | xml            | **182** | 69%     | 63     | 29      | ~1.8 min | 85s  | $0.82 | $0.644 |
| opus-4.5   | medium | toml           | **182** | 69%     | 47     | 27      | ~1.7 min | 80s  | $0.97 | $0.761 |
| opus-4.5   | medium | csv_quoted     | **171** | 65%     | 29     | 27      | ~1.3 min | 65s  | $0.82 | $0.685 |
|            |        |                |         |         |        |         |          |      |       |        |
| sonnet-4.5 | medium | json           | **189** | 100%    | 58     | 22      | ~1.6 min | 73s  | $0.54 | $0.408 |
| sonnet-4.5 | medium | csv            | **126** | 67%     | 21     | 16      | ~1.1 min | 75s  | $0.30 | $0.340 |
| sonnet-4.5 | medium | kv_colon_space | **126** | 67%     | 29     | 19      | ~1.2 min | 82s  | $0.37 | $0.419 |
| sonnet-4.5 | medium | markdown_table | **126** | 67%     | 22     | 16      | ~1.2 min | 82s  | $0.32 | $0.363 |
| sonnet-4.5 | medium | csv_quoted     | **120** | 63%     | 21     | 14      | ~1.0 min | 71s  | $0.29 | $0.345 |
| sonnet-4.5 | medium | yaml           | **120** | 63%     | 33     | 15      | ~1.1 min | 79s  | $0.32 | $0.381 |
| sonnet-4.5 | medium | toml           | **115** | 61%     | 30     | 14      | ~1.0 min | 75s  | $0.31 | $0.385 |
| sonnet-4.5 | medium | xml            | **99**  | 52%     | 35     | 12      | ~1.0 min | 87s  | $0.33 | $0.476 |

**Total: 48 tests** (6 models × 8 formats)

## MUST-NOT-FORGET

- **TBLF-FL-005**: Test uses 7/7 columns, NOT Test 01's 7/20 - results not comparable
- Seed: 42, Filter: department="Engineering" AND salary>75000
- Capture per-request metrics: time/req, cost/req (NOT totals)
- Best format varies by model family (see results)

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

1. Does token efficiency correlate with scale limits? (csv 1.0x vs xml 2.1x)
2. Do structured formats (JSON, XML) aid or hinder comprehension?
3. Do format preferences differ between model families (GPT vs Claude)?

### 1.2 Format Token Efficiency

| Format         | Size (300 rows) | Relative | Hypothesis                 |
|----------------|-----------------|----------|----------------------------|
| csv            | 148 KB          | 1.00x    | Best scale (most compact)  |
| csv_quoted     | 156 KB          | 1.06x    | Baseline                   |
| markdown_table | 197 KB          | 1.33x    | -                          |
| kv_colon_space | 217 KB          | 1.47x    | May match CSV (TK-001)     |
| toml           | 235 KB          | 1.59x    | -                          |
| yaml           | 249 KB          | 1.68x    | Structured, may help       |
| json           | 269 KB          | 1.82x    | Structured, may help       |
| xml            | 314 KB          | 2.12x    | Worst scale (most verbose) |

### 1.3 Expected Outcomes

**If H5 confirmed (token efficiency):**
- csv > xml by ~2x in scale limit
- Scale limit inversely proportional to token size

**If H6 confirmed (key-value outperforms):**
- kv_colon_space >= JSON, XML, YAML
- Format type matters more than token count

**If H3 confirmed (model family differs):**
- GPT-5 and Claude have different optimal formats
- No universal "best format"

## 2. Test Matrix

### 2.1 Models (5)

| Model         | Effort | CSV Baseline | Start Row |
|---------------|--------|--------------|-----------|
| gpt-5-mini    | medium | 500          | 500       |
| gpt-5         | low    | 356          | 356       |
| gpt-5.2       | medium | 215          | 215       |
| claude-opus   | medium | 177          | 177       |
| claude-sonnet | medium | 168          | 168       |

### 2.2 Formats (7 new + 1 baseline)

| Format         | File Ext | Notes              |
|----------------|----------|--------------------|
| csv_quoted     | .csv     | Baseline (Test 01) |
| csv            | .csv     | Unquoted CSV       |
| kv_colon_space | .txt     | Key: value pairs   |
| markdown_table | .md      | Markdown table     |
| json           | .json    | JSON array         |
| xml            | .xml     | XML records        |
| yaml           | .yaml    | YAML list          |
| toml           | .toml    | TOML array         |

### 2.3 Test ID Mapping

| Test ID | Model         | Format         | Hypotheses |
|---------|---------------|----------------|------------|
| F01     | gpt-5-mini    | csv            | H5         |
| F02     | gpt-5-mini    | kv_colon_space | H6         |
| F03     | gpt-5-mini    | markdown_table | H5         |
| F04     | gpt-5-mini    | json           | H2, H5     |
| F05     | gpt-5-mini    | xml            | H5         |
| F06     | gpt-5-mini    | yaml           | H2         |
| F07     | gpt-5-mini    | toml           | H5         |
| F08     | gpt-5         | csv            | H3, H5     |
| F09     | gpt-5         | kv_colon_space | H3, H6     |
| F10     | gpt-5         | markdown_table | H3         |
| F11     | gpt-5         | json           | H2, H3     |
| F12     | gpt-5         | xml            | H3, H5     |
| F13     | gpt-5         | yaml           | H2, H3     |
| F14     | gpt-5         | toml           | H3         |
| F15     | gpt-5.2       | csv            | H5         |
| F16     | gpt-5.2       | kv_colon_space | H6         |
| F17     | gpt-5.2       | markdown_table | H5         |
| F18     | gpt-5.2       | json           | H2         |
| F19     | gpt-5.2       | xml            | H5         |
| F20     | gpt-5.2       | yaml           | H2         |
| F21     | gpt-5.2       | toml           | H5         |
| F22     | claude-opus   | csv            | H3, H5     |
| F23     | claude-opus   | kv_colon_space | H3, H6     |
| F24     | claude-opus   | markdown_table | H3         |
| F25     | claude-opus   | json           | H2, H3     |
| F26     | claude-opus   | xml            | H3, H5     |
| F27     | claude-opus   | yaml           | H2, H3     |
| F28     | claude-opus   | toml           | H3         |
| F29     | claude-sonnet | csv            | H3, H5     |
| F30     | claude-sonnet | kv_colon_space | H3, H6     |
| F31     | claude-sonnet | markdown_table | H3         |
| F32     | claude-sonnet | json           | H2, H3     |
| F33     | claude-sonnet | xml            | H3, H5     |
| F34     | claude-sonnet | yaml           | H2, H3     |
| F35     | claude-sonnet | toml           | H3         |

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

**Test**: Compare csv (1.0x) vs xml (2.12x) scale limits.

**Expected**: csv > xml by ~2x

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
for format in csv kv_colon_space markdown_table json xml yaml toml; do
  python 03_find_scale_limit.py --test-path .. --model gpt-5.2 --format $format --initial-rows 215 --tolerance 10
done
```

### 4.3 Phase 3: gpt-5-mini All Formats (7 tests)

**Goal**: Primary model with most TK-001 prior data

```bash
# Run all 7 formats for gpt-5-mini (F01-F07)
for format in csv kv_colon_space markdown_table json xml yaml toml; do
  python 03_find_scale_limit.py --test-path .. --model gpt-5-mini --format $format --initial-rows 500 --tolerance 10
done
```

### 4.4 Phase 4: gpt-5 All Formats (7 tests)

```bash
# Run all 7 formats for gpt-5 (F08-F14)
for format in csv kv_colon_space markdown_table json xml yaml toml; do
  python 03_find_scale_limit.py --test-path .. --model gpt-5 --format $format --initial-rows 356 --tolerance 10
done
```

### 4.5 Phase 5: Claude Models (14 tests)

```bash
# claude-opus (F22-F28)
for format in csv kv_colon_space markdown_table json xml yaml toml; do
  python 03_find_scale_limit.py --test-path .. --model claude-opus --format $format --initial-rows 177 --tolerance 10
done

# claude-sonnet (F29-F35)
for format in csv kv_colon_space markdown_table json xml yaml toml; do
  python 03_find_scale_limit.py --test-path .. --model claude-sonnet --format $format --initial-rows 168 --tolerance 10
done
```

### 4.6 Parallel Execution Strategy

**Cascade Limitation:** Windsurf can only run 3-4 background commands simultaneously.
Run tests in **batches of 4**: 2 slow + 2 fast models to maximize throughput while keeping logs visible.

**Batch composition (2 slow + 2 fast):**
- Slow: gpt-5-mini (~105 min), gpt-5 (~72 min)
- Fast: gpt-5.2 (~30 min), claude-sonnet (~42 min), claude-opus (~48 min)

**Time estimates per test (from Test 01 data):**

| Model         | Time/req | Requests (~10 iter × 3 runs) | Total/test   |
|---------------|----------|------------------------------|--------------|  
| gpt-5-mini    | ~3.5 min | ~30                          | **~105 min** |
| gpt-5         | ~2.4 min | ~30                          | **~72 min**  |
| gpt-5.2       | ~1 min   | ~30                          | **~30 min**  |
| claude-opus   | ~1.6 min | ~30                          | **~48 min**  |
| claude-sonnet | ~1.4 min | ~30                          | **~42 min**  |

**API rate limits (tested in Test 01):**
- OpenAI: 120+ concurrent workers
- Anthropic: 60+ concurrent workers

**Parallel execution: Run all 35 tests simultaneously**

Each test uses ~3 internal workers, so total concurrent:
- OpenAI (3 models × 7 formats × 3 workers): 63 workers ✓
- Anthropic (2 models × 7 formats × 3 workers): 42 workers ✓

**Total time = slowest test = gpt-5-mini = ~2 hours**

### 4.7 Batch Execution Plan (4 parallel, logs visible)

**Strategy:** Run 4 tests at a time (2 slow + 2 fast) to balance throughput and log visibility.

**Batch 1** (gpt-5.2 all formats - RUNNING):
```bash
# Already running - 3 done, 4 in progress
python 03_find_scale_limit.py --test-path .. --model gpt-5.2 --format csv --initial-rows 215 --reasoning-effort medium      # DONE: 215
python 03_find_scale_limit.py --test-path .. --model gpt-5.2 --format kv_colon_space --initial-rows 215 --reasoning-effort medium  # DONE: 100
python 03_find_scale_limit.py --test-path .. --model gpt-5.2 --format markdown_table --initial-rows 215 --reasoning-effort medium  # DONE: 154
python 03_find_scale_limit.py --test-path .. --model gpt-5.2 --format json --initial-rows 215 --reasoning-effort medium       # RUNNING
python 03_find_scale_limit.py --test-path .. --model gpt-5.2 --format xml --initial-rows 215 --reasoning-effort medium        # RUNNING
python 03_find_scale_limit.py --test-path .. --model gpt-5.2 --format yaml --initial-rows 215 --reasoning-effort medium       # RUNNING
python 03_find_scale_limit.py --test-path .. --model gpt-5.2 --format toml --initial-rows 215 --reasoning-effort medium       # RUNNING
```

**Batch 2** (csv_quoted baseline verification - 2 slow + 2 fast):
```bash
# Slow - verify consistency with Test 01
python 03_find_scale_limit.py --test-path .. --model gpt-5-mini --format csv_quoted --initial-rows 500 --reasoning-effort medium
python 03_find_scale_limit.py --test-path .. --model gpt-5 --format csv_quoted --initial-rows 356 --reasoning-effort low
# Fast
python 03_find_scale_limit.py --test-path .. --model claude-sonnet-4-5-20250929 --format csv_quoted --initial-rows 168
python 03_find_scale_limit.py --test-path .. --model claude-opus-4-5-20251101 --format csv_quoted --initial-rows 177
```

**Batch 3** (csv - 2 slow + 2 fast):
```bash
python 03_find_scale_limit.py --test-path .. --model gpt-5-mini --format csv --initial-rows 500 --reasoning-effort medium
python 03_find_scale_limit.py --test-path .. --model gpt-5 --format csv --initial-rows 356 --reasoning-effort low
python 03_find_scale_limit.py --test-path .. --model claude-sonnet-4-5-20250929 --format csv --initial-rows 168
python 03_find_scale_limit.py --test-path .. --model claude-opus-4-5-20251101 --format csv --initial-rows 177
```

**Batch 4-9:** Continue pattern for remaining formats (kv_colon_space, markdown_table, json, xml, yaml, toml)

### 4.8 Time Estimate

| Strategy            | Batches | Total Time                           |
|---------------------|---------|--------------------------------------|
| Sequential (1 test) | 40      | ~14 hours                            |
| Batches of 4        | 10      | **~3.5 hours**                       |
| Full parallel (40)  | 1       | ~2 hours (requires external terminals)|

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

| Metric           | Source               | Unit    |
|------------------|----------------------|---------|
| time_per_request | response_time / runs | seconds |
| cost_per_request | total_cost / runs    | USD     |
| input_tokens     | API response         | tokens  |
| output_tokens    | API response         | tokens  |

### 6.2 Scale Limit Metrics

| Metric                  | Source                             |
|-------------------------|------------------------------------|
| max_reliable_rows       | Binary search result               |
| vs_csv_baseline         | (format_limit / csv_limit) × 100%  |
| failure_mode            | comprehension or truncation        |
| context_utilization_pct | tokens_used / max_context          |

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

**[2026-03-09 21:03]**
- Changed: Format naming - csv_quoted (baseline, QUOTE_ALL) and csv (regular, QUOTE_MINIMAL)
- Previously csv_raw renamed to csv for clarity
- Both formats must be run

**[2026-03-09 20:59]**
- Changed: 35 -> 40 tests (include csv_quoted baseline verification)
- Reason: Verify consistency with Test 01 before comparing formats
- Results: gpt-5.2 json=241 (112%), yaml=134 (62%), toml=46 (21%)

**[2026-03-09 20:54]**
- Changed: Batch execution strategy (4 tests: 2 slow + 2 fast) instead of PowerShell
- Reason: Keep logs visible, avoid hidden execution
- Results: gpt-5.2 csv=215 (100%), kv_colon_space=100 (47%), markdown_table=154 (72%)

**[2026-03-09 20:49]**
- Added: Cascade limitation note (3-4 background commands max)
- Fixed: Folder naming now includes format to prevent conflicts
- Started: gpt-5.2 tests (3 done, 4 running)

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
