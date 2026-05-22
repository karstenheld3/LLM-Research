<DevSystem MarkdownTablesAllowed=true />

# INFO: CSV Scale Limits - Test Results

**Doc ID**: TBLF-IN02
**Goal**: Collect all test result data from CSV scale limit experiments
**Timeline**: Created 2026-05-22

**Depends on:**
- `_SPEC_CSVScaleLimits.md [TBLF-SP01]` for test framework specification
- `_TEST_CSVScaleLimits.md [TBLF-TP01]` for test execution procedures

## Status

- **Tests completed**: 19/19
- **T04 (gpt-5-mini high)**: Passed at 675 rows, evaluation errors at higher scales
- **claude-opus-4.7 high**: Cancelled at 843+ rows (>$30, endless reasoning tokens; boundary 843-1012)

## Table of Contents

1. [Research Problem](#1-research-problem)
2. [Methodology](#2-methodology)
3. [Variables](#3-variables)
4. [Metrics](#4-metrics)
5. [Scale Limit Results](#5-scale-limit-results)
6. [Failure Mode Data](#6-failure-mode-data)
7. [Effort Level Data](#7-effort-level-data)
8. [Model Tier Comparison Data](#8-model-tier-comparison-data)
9. [Data Verification](#9-data-verification)
10. [Sources](#10-sources)
11. [Document History](#11-document-history)

## 1. Research Problem

### 1.1 Research Question

**Primary:** What is the maximum number of CSV rows an LLM can reliably process for tabular extraction tasks?

**Secondary:**
- How do different models compare (GPT-5, Claude Sonnet 4, etc.)?
- What causes failure - context limits, attention degradation, or output truncation?
- Does reasoning effort/thinking budget affect scale limits?

### 1.2 Why This Matters

Real-world applications need to know:
- When to chunk large datasets before LLM processing
- Which models handle larger tables
- Cost/accuracy tradeoffs at scale
- Expected response times per request for production latency planning

### 1.3 Definition of "Reliable"

A result is reliable when:
- **Precision = 1.00** - No false positives (no records that shouldn't match)
- **Recall = 1.00** - No false negatives (no missed records that should match)
- **Consistent** - Same result across 3+ runs with same data

## 2. Methodology

### 2.1 Approach: Binary Search for Scale Limits

Instead of testing every row count, we use binary search to efficiently find the boundary:

1. Start at initial row count (e.g., 100 rows)
2. Run extraction task, evaluate precision/recall
3. **PASS** (100% accuracy): Increase rows by 1.5x, set as new lower bound
4. **FAIL** (any errors): Set as upper bound, try midpoint
5. Converge when upper - lower <= tolerance (e.g., 10 rows)

**Efficiency:** Finds limit in ~10 iterations vs 100+ for linear search.

### 2.2 Task Design

The extraction task tests multiple LLM capabilities:
- **Parsing** - Read quoted CSV with adversarial characters (commas, pipes, colons)
- **Filtering** - Apply compound filter: `clearance IN [Level 3, 4, 5] AND salary >= $150,000`
- **Output** - Format matching records with specific columns

### 2.3 Why Quoted CSV

Prior benchmarking (TK-001, March 2026) tested 10 format variants on gpt-5-mini extraction tasks. Quoted CSV ranked in top 3 across all metrics.

v4 Results (300 records, 107 matching, n=15 runs):

| Rank | Format              | Precision | Std Dev | Recall |
|------|---------------------|-----------|---------|--------|
| 1    | `::` (double colon) | 1.000     | 0.000   | 0.997  |
| 2    | `: ` (colon space)  | 1.000     | 0.000   | 0.989  |
| 3    | CSV quoted          | 1.000     | 0.000   | 0.991  |
| 9    | Markdown table      | 0.978     | 0.038   | 0.950  |
| 10   | XML                 | 0.956     | 0.161   | 0.965  |

CSV chosen over key-value formats because CSV is a standard tabular format that generalizes to real-world datasets.

**Source**: `_INFO_LLM_MARKDOWN_PREFERENCES.md [LLMO-IN01]` Part 6.2

### 2.4 Controls

- **Seed** - Same random seed (42) for reproducible data generation
- **Runs** - 3 runs per configuration to detect inconsistency
- **Ground truth** - Pre-computed expected IDs for exact comparison

## 3. Variables

### 3.1 Independent Variables

- **Model** - gpt-4o-mini, gpt-5-mini, gpt-5, gpt-5.2, gpt-5.4, gpt-5.5, gpt-4o, claude-haiku-4.5, claude-sonnet-4, claude-sonnet-4.5, claude-opus-4.5, claude-opus-4.6, claude-opus-4.7
- **Row count** - 50-2000 (varies per binary search)
- **Reasoning effort** - low, medium, high
- **Output length** - low, medium, high (max output tokens scaling)

### 3.2 Controlled Variables

- **Columns**: 7 (id, name, department, salary, clearance, rating, projects)
- **Filter complexity**: 2 conditions (IN list + threshold)
- **Data format**: Quoted CSV
- **Adversarial content**: ~20% of records contain delimiter characters in values

### 3.3 Dependent Variables

- **Precision** - Correct matches / Total extracted
- **Recall** - Correct matches / Total expected
- **Truncation** - Whether output was cut off (`finish_reason == "length"`)
- **Cost** - USD spent per test (input + output tokens)

## 4. Metrics

### 4.1 Success Criteria

A test **PASSES** when:
- Precision = 1.00 (no false positives)
- Recall = 1.00 (no false negatives)
- No truncation detected

### 4.2 Failure Modes

- **Truncation** - Output cut off before all records listed
- **Missed records** - LLM skipped matching records (recall < 1.0)
- **Extra records** - LLM included non-matching records (precision < 1.0)
- **Parse errors** - LLM misread CSV data

### 4.3 Scale Limit Definition

**Scale limit** = Maximum row count where all 3 runs pass with 100% accuracy.

## 5. Scale Limit Results

### 5.1 All Configurations (19 tests, sorted by scale limit descending)

<!-- AUTO:section-5.1:start -->
| Model             | Provider  | Method            | Effort | Scale Limit | Failure Mode  | Context % | Cost    | Time/req |
|-------------------|-----------|-------------------|--------|-------------|---------------|-----------|---------|----------|
| claude-opus-4.7   | Anthropic | adaptive_thinking | high   | 843+        | (cancelled)   | -         | ~$30+   | ~3.3 min |
| gpt-5-mini        | OpenAI    | reasoning         | high   | 675+        | (errors)      | -         | $0.00   | -        |
| claude-opus-4.6   | Anthropic | adaptive_thinking | high   | 667         | comprehension | 55.4%     | ~$18+   | ~1.5 min |
| gpt-5-mini        | OpenAI    | reasoning         | medium | 500         | comprehension | 7.1%      | $0.40   | ~1.2 min |
| gpt-5.4           | OpenAI    | reasoning         | medium | 492         | comprehension | 6.8%      | $2.49   | ~51 sec  |
| gpt-5             | OpenAI    | reasoning         | high   | 492         | truncation    | 8.0%      | $2.73   | ~4.9 min |
| gpt-5             | OpenAI    | reasoning         | medium | 450         | comprehension | 6.4%      | $2.97   | ~1.5 min |
| gpt-5.5           | OpenAI    | reasoning         | medium | 437         | comprehension | 6.8%      | $8.15   | ~32 sec  |
| gpt-5             | OpenAI    | reasoning         | low    | 356         | comprehension | 2.1%      | $0.43   | ~2.2 min |
| gpt-5.2           | OpenAI    | reasoning         | medium | 215         | comprehension | 1.4%      | $0.29   | ~55 sec  |
| claude-sonnet-4   | Anthropic | thinking          | medium | 187         | truncation    | 25.1%     | $3.41   | ~40 sec  |
| claude-opus-4.5   | Anthropic | thinking          | medium | 177         | truncation    | 25.1%     | $5.36   | ~32 sec  |
| claude-sonnet-4.5 | Anthropic | thinking          | medium | 168         | comprehension | 8.4%      | $0.89   | ~1.1 min |
| gpt-5-mini        | OpenAI    | reasoning         | low    | 65          | comprehension | 4.3%      | $0.07   | ~16 sec  |
| claude-opus-4.7   | Anthropic | adaptive_thinking | medium | 12          | comprehension | 5.1%      | $1.96   | ~2 sec   |
| claude-haiku-4.5  | Anthropic | temperature       | medium | 9           | comprehension | 8.3%      | $0.09   | ~2 sec   |
| claude-opus-4.6   | Anthropic | adaptive_thinking | medium | 6           | comprehension | 16.9%     | $1.12   | ~2 sec   |
| gpt-4o-mini       | OpenAI    | temperature       | medium | 6           | comprehension | 2.1%      | $0.00   | ~5 sec   |
| gpt-4o            | OpenAI    | temperature       | medium | 4           | comprehension | 11.3%     | $0.10   | ~3 sec   |
<!-- AUTO:section-5.1:end -->

*claude-opus-4.7 high cancelled (>$30, endless reasoning tokens; boundary 843-1012)
**gpt-5-mini high passed at 675 rows but had evaluation errors at higher scales

### 5.2 Boundary Details

- **gpt-5-mini medium**: Bounds [500, 507]. Passed at 500 (P=1.00, R=1.00, 3/3). Failed at 507 (P=1.00, R=0.9733)
- **claude-opus-4.7 high**: Passed at 843 rows. Search cancelled before convergence. Boundary 843-1012.
- **gpt-5-mini high (T04)**: Passed at 675 rows. Evaluation errors at 1012+ rows.

## 6. Failure Mode Data

### 6.1 Primary Failure Mode per Model

Source: `primary_failure_mode` field in each `scale_limit_result.json`

<!-- AUTO:section-6.1:start -->
| Model              | Primary Failure | Truncated              | Context Used |
|--------------------|-----------------|------------------------|--------------|
| claude-opus-4.6 high | comprehension   | No                     | 55.4%        |
| gpt-5-mini         | comprehension   | No                     | 7.1%         |
| gpt-5.4            | comprehension   | No                     | 6.8%         |
| gpt-5 high         | TRUNCATION      | Yes                    | 8.0%         |
| gpt-5              | comprehension   | No                     | 6.4%         |
| gpt-5.5            | comprehension   | No                     | 6.8%         |
| gpt-5 low          | comprehension   | No                     | 2.1%         |
| gpt-5.2            | comprehension   | No                     | 1.4%         |
| claude-sonnet-4    | TRUNCATION      | Yes                    | 25.1%        |
| claude-opus-4.5    | TRUNCATION      | Yes                    | 25.1%        |
| claude-sonnet-4.5  | comprehension   | No                     | 8.4%         |
| gpt-5-mini low     | comprehension   | No                     | 4.3%         |
| claude-opus-4.7    | comprehension   | No                     | 5.1%         |
| claude-haiku-4.5   | comprehension   | Yes (early iters)      | 8.3%         |
| claude-opus-4.6    | comprehension   | No                     | 16.9%        |
| gpt-4o-mini        | comprehension   | No                     | 2.1%         |
| gpt-4o             | comprehension   | No                     | 11.3%        |
<!-- AUTO:section-6.1:end -->

### 6.2 Failure Mode Summary

<!-- AUTO:section-6.2:start -->
- **Comprehension failures**: 14 of 17 tests with clear failure modes
- **Truncation failures**: 3 of 17 (gpt-5 high, claude-sonnet-4, claude-opus-4.5)
- **Excluded**: gpt-5-mini high (errors), claude-opus-4.7 high (cancelled)
<!-- AUTO:section-6.2:end -->

## 7. Effort Level Data

<!-- AUTO:section-7:start -->
### claude-opus-4.6 Effort Comparison

| Effort | Scale Limit | Cost    | Time/req |
|--------|-------------|---------|----------|
| medium | 6           | $1.12   | ~2 sec   |
| high   | 667         | ~$18+   | ~1.5 min |

### claude-opus-4.7 Effort Comparison

| Effort | Scale Limit | Cost    | Time/req |
|--------|-------------|---------|----------|
| medium | 12          | $1.96   | ~2 sec   |
| high   | 843+        | ~$30+   | ~3.3 min |

### gpt-5-mini Effort Comparison

| Effort | Scale Limit | Cost    | Time/req |
|--------|-------------|---------|----------|
| low    | 65          | $0.07   | ~16 sec  |
| medium | 500         | $0.40   | ~1.2 min |
| high   | 675+        | $0.00   | -        |

### gpt-5 Effort Comparison

| Effort | Scale Limit | Cost    | Time/req |
|--------|-------------|---------|----------|
| low    | 356         | $0.43   | ~2.2 min |
| medium | 450         | $2.97   | ~1.5 min |
| high   | 492         | $2.73   | ~4.9 min |
<!-- AUTO:section-7:end -->

## 8. Model Tier Comparison Data

<!-- AUTO:section-8:start -->
### 8.1 Mini Tier (Temperature vs Reasoning)

| Model       | Method      | Scale Limit |
|-------------|-------------|-------------|
| gpt-4o-mini | temperature | 6           |
| gpt-5-mini  | reasoning   | 500         |

### 8.2 Full Tier (Temperature vs Reasoning)

| Model  | Method          | Scale Limit |
|--------|-----------------|-------------|
| gpt-4o | temperature     | 4           |
| gpt-5  | reasoning (low) | 356         |

### 8.3 Generational Comparison (Same Provider)

- **gpt-5.2 medium**: 215 rows
- **gpt-5 medium**: 450 rows
- **gpt-5.4 medium**: 492 rows
- **gpt-5.5 medium**: 437 rows

### 8.4 Anthropic Thinking Method Comparison (Medium Effort)

- **claude-haiku-4.5** (temperature): 9 rows
- **claude-sonnet-4** (thinking): 187 rows
- **claude-sonnet-4.5** (thinking): 168 rows
- **claude-opus-4.5** (thinking): 177 rows
- **claude-opus-4.6** (adaptive_thinking): 6 rows
- **claude-opus-4.7** (adaptive_thinking): 12 rows
<!-- AUTO:section-8:end -->

### 8.5 H2 Failure Pattern Data

**Reasoning models (gpt-5 family)** - cliff behavior:
- gpt-5-mini medium: 500 rows = 100% accuracy, 507 rows = partial extraction failure
- Transition from perfect to degraded within 7 rows (<2% range)

**Temperature models (gpt-4o family)** - gradual slope:
- gpt-4o at 300 rows: Precision=0.47, Recall=0.71
- gpt-4o at 75 rows: Precision=0.65, Recall=0.63
- gpt-4o at 37 rows: Precision=0.89, Recall=0.62

## 9. Data Verification

- All data generated by `06_aggregate_results.py` from source `scale_limit_result.json` files
- Time/req = single LLM API call time (iteration duration / verification runs)
- Costs = total test cost (all iterations combined)
- gpt-5-mini medium re-run confirmed 500 rows (original run found 389; bounds [500, 507])
- claude-sonnet-4 corrected: 187 rows, truncation, 25.1% (previously miscategorized as 168, comprehension)
- Calculation verifications:
  - gpt-5-mini effort improvement: (500 - 65) / 65 = 669%, 500 / 65 = 7.69 = 7.7x
  - gpt-5 effort improvement: (492 - 356) / 356 = 38%, (450 - 356) / 356 = 26%
  - Mini tier ratio: 500 / 6 = 83.3 = 83x
  - Full tier ratio: 356 / 4 = 89x
  - Opus 4.6 effort ratio: 667 / 6 = 111x

## 10. Sources

- `_SPEC_CSVScaleLimits.md [TBLF-SP01]` - Test framework specification
- `_TEST_CSVScaleLimits.md [TBLF-TP01]` - Test execution procedures
- `_INFO_LLM_MARKDOWN_PREFERENCES.md [LLMO-IN01]` - Format benchmarking research (TK-001)
- `_SPEC_LLM_CLIENT.md [LLMC-SP01]` - LLM client specification
- `.windsurf/skills/llm-evaluation/` - Original LLM evaluation scripts
- `_TestsAndResults/*/scale_limit_result.json` - Raw test result data

## 11. Document History

**[2026-05-22 17:05]**
- Fixed: claude-sonnet-4 corrected to 187 rows, truncation, 25.1% (was 168, comprehension, 8.4%)
- Fixed: Time/req now = single API call time (was inconsistent mix of iteration/total)
- Fixed: Costs updated to total test cost from JSON source
- Changed: Data now generated by `06_aggregate_results.py` (single source of truth)
- Changed: Failure mode summary: 14 comprehension / 3 truncation (was 15/2)

**[2026-05-22 16:40]**
- Initial document created from restructuring of `_INFO_CSVScaleLimits.md [TBLF-IN01]` and `_TEST_CSVScaleLimits.md [TBLF-TP01]`
- Contains: methodology (old INFO sections 1-5), all 19 test results, failure mode data, effort/tier comparison data
- All data verified against source JSON files
