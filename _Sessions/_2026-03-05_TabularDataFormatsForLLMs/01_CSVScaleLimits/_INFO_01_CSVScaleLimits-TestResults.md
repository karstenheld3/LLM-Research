<DevSystem MarkdownTablesAllowed=true />

# INFO: CSV Scale Limits - Test Results

**Doc ID**: TBLF-IN02
**Goal**: Collect all test result data from CSV scale limit experiments
**Timeline**: Created 2026-05-22

**Depends on:**
- `_SPEC_CSVScaleLimits.md [TBLF-SP01]` for test framework specification
- `_TEST_CSVScaleLimits.md [TBLF-TP01]` for test execution procedures

## Status

- **Tests completed**: 20/20
- **T04 (gpt-5-mini high)**: Passed at 675 rows, evaluation errors at higher scales
- **claude-opus-4.7 high**: Cancelled at 843+ rows (>$30, endless reasoning tokens; boundary 843-1012)
- **claude-opus-4.8 high**: Confirmed at 492 rows (comprehension failure; boundary 492-500; $19.96 total)

## Table of Contents

1. [Research Problem](#1-research-problem)
2. [Methodology](#2-methodology)
3. [Variables](#3-variables)
4. [Metrics](#4-metrics)
5. [Scale Limit Results](#5-scale-limit-results)
6. [Failure Mode Data](#6-failure-mode-data)
7. [Effort Level Data](#7-effort-level-data)
8. [Model Tier Comparison Data](#8-model-tier-comparison-data)
9. [Deep Analysis](#9-deep-analysis-per-iteration-data)
10. [Data Verification](#10-data-verification)
11. [Sources](#11-sources)
12. [Document History](#12-document-history)

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

TK-001 benchmark results (gpt-5-mini, 300 records, 107 matching, n=15 runs):

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

- **Model** - gpt-4o-mini, gpt-5-mini, gpt-5, gpt-5.2, gpt-5.4, gpt-5.5, gpt-4o, claude-haiku-4.5, claude-sonnet-4, claude-sonnet-4.5, claude-opus-4.5, claude-opus-4.6, claude-opus-4.7, claude-opus-4.8
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

### 5.1 All Configurations (20 tests, sorted by scale limit descending)

<!-- AUTO:section-5.1:start -->
| Model             | Provider  | Method            | Effort | Scale Limit | Failure Mode  | Context % | Cost    | Time/req |
|-------------------|-----------|-------------------|--------|-------------|---------------|-----------|---------|----------|
| claude-opus-4.7   | Anthropic | adaptive_thinking | high   | 843+        | (cancelled)   | -         | ~$30+   | ~3.3 min |
| gpt-5-mini        | OpenAI    | reasoning         | high   | 675+        | (errors)      | -         | $0.00   | -        |
| claude-opus-4.6   | Anthropic | adaptive_thinking | high   | 667         | comprehension | 55.4%     | ~$18+   | ~1.5 min |
| gpt-5-mini        | OpenAI    | reasoning         | medium | 500         | comprehension | 7.1%      | $0.40   | ~1.2 min |
| claude-opus-4.8   | Anthropic | adaptive_thinking | high   | 492         | comprehension | 12.4%     | ~$20+   | ~59 sec  |
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
- **claude-opus-4.8 high**: Bounds [492, 500]. Passed at 492 (P=1.00, R=1.00, 3/3). Failed at 500 (P=1.00, R=0.998)

## 6. Failure Mode Data

### 6.1 Primary Failure Mode per Model

Source: `primary_failure_mode` field in each `scale_limit_result.json`

<!-- AUTO:section-6.1:start -->
| Model              | Primary Failure | Truncated              | Context Used |
|--------------------|-----------------|------------------------|--------------|
| claude-opus-4.6 high | comprehension   | No                     | 55.4%        |
| gpt-5-mini         | comprehension   | No                     | 7.1%         |
| claude-opus-4.8 high | comprehension   | No                     | 12.4%        |
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
- **Comprehension failures**: 15 of 18 tests with clear failure modes
- **Truncation failures**: 3 of 18 (gpt-5 high, claude-sonnet-4, claude-opus-4.5)
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

## 9. Deep Analysis (Per-Iteration Data)

### 9.1 Accuracy vs Scale (Precision/Recall at Each Tested Row Count)

<!-- AUTO:section-9.1:start -->
**claude-opus-4.6 high**

| Rows | Precision | Recall  | F1      | Pass | Failure Mode  |
|------|-----------|---------|---------|------|---------------|
| 200  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 300  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 450  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 562  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 618  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 646  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 660  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 667  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 675  | 0.998     | 1.000   | 0.999   | NO   | comprehension |

**gpt-5-mini medium**

| Rows | Precision | Recall  | F1      | Pass | Failure Mode  |
|------|-----------|---------|---------|------|---------------|
| 37   | 1.000     | 1.000   | 1.000   | YES  | -             |
| 56   | 1.000     | 1.000   | 1.000   | YES  | -             |
| 65   | 1.000     | 1.000   | 1.000   | YES  | -             |
| 75   | 1.000     | 0.986   | 0.993   | NO   | comprehension |
| 150  | 1.000     | 0.993   | 0.997   | NO   | comprehension |
| 300  | 1.000     | 0.871   | 0.929   | NO   | comprehension |
| 500  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 507  | 1.000     | 0.991   | 0.995   | NO   | comprehension |
| 515  | 1.000     | 0.991   | 0.996   | NO   | comprehension |
| 531  | 1.000     | 0.998   | 0.999   | NO   | comprehension |
| 562  | 1.000     | 0.998   | 0.999   | NO   | comprehension |
| 625  | 1.000     | 0.984   | 0.992   | NO   | comprehension |
| 750  | 0.996     | 0.648   | 0.728   | NO   | comprehension |

**claude-opus-4.8 high**

| Rows | Precision | Recall  | F1      | Pass | Failure Mode  |
|------|-----------|---------|---------|------|---------------|
| 250  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 375  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 437  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 468  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 484  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 492  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 500  | 1.000     | 0.998   | 0.999   | NO   | comprehension |

**gpt-5.4 medium**

| Rows | Precision | Recall  | F1      | Pass | Failure Mode  |
|------|-----------|---------|---------|------|---------------|
| 250  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 375  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 437  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 468  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 484  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 492  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 500  | 1.000     | 0.996   | 0.998   | NO   | comprehension |

**gpt-5 high**

| Rows | Precision | Recall  | F1      | Pass | Failure Mode  |
|------|-----------|---------|---------|------|---------------|
| None | -         | -       | -       | NO   | -             |
| 300  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 450  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 478  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 492  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 499  | 0.667     | 0.667   | 0.667   | NO   | truncation    |
| 506  | 1.000     | 0.996   | 0.998   | NO   | comprehension |
| 562  | 0.667     | 0.667   | 0.667   | NO   | truncation    |

**gpt-5 medium**

| Rows | Precision | Recall  | F1      | Pass | Failure Mode  |
|------|-----------|---------|---------|------|---------------|
| 300  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 300  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 337  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 356  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 365  | 1.000     | 0.991   | 0.996   | NO   | comprehension |
| 375  | 1.000     | 0.991   | 0.996   | NO   | comprehension |
| 450  | 0.993     | 1.000   | 0.996   | NO   | comprehension |
| 450  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 457  | 1.000     | 0.988   | 0.994   | NO   | comprehension |
| 464  | 1.000     | 0.995   | 0.998   | NO   | comprehension |
| 478  | 0.995     | 0.990   | 0.993   | NO   | comprehension |
| 506  | 1.000     | 0.998   | 0.999   | NO   | comprehension |
| 562  | 1.000     | 0.984   | 0.992   | NO   | comprehension |
| 675  | 1.000     | 0.993   | 0.996   | NO   | comprehension |

**gpt-5.5 medium**

| Rows | Precision | Recall  | F1      | Pass | Failure Mode  |
|------|-----------|---------|---------|------|---------------|
| 250  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 375  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 437  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 444  | 1.000     | 0.998   | 0.999   | NO   | comprehension |
| 452  | 1.000     | 0.998   | 0.999   | NO   | comprehension |
| 468  | 1.000     | 0.998   | 0.999   | NO   | comprehension |
| 500  | 1.000     | 0.987   | 0.993   | NO   | comprehension |

**gpt-5.2 medium**

| Rows | Precision | Recall  | F1      | Pass | Failure Mode  |
|------|-----------|---------|---------|------|---------------|
| 150  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 187  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 206  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 215  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 225  | 1.000     | 0.987   | 0.994   | NO   | comprehension |
| 300  | 1.000     | 0.871   | 0.931   | NO   | comprehension |

**claude-sonnet-4 medium**

| Rows | Precision | Recall  | F1      | Pass | Failure Mode  |
|------|-----------|---------|---------|------|---------------|
| 150  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 187  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 196  | 0.995     | 1.000   | 0.998   | NO   | comprehension |
| 206  | 1.000     | 0.277   | 0.403   | NO   | truncation    |
| 225  | 0.992     | 0.849   | 0.898   | NO   | truncation    |
| 300  | 0.667     | 0.308   | 0.381   | NO   | truncation    |

**claude-opus-4.5 medium**

| Rows | Precision | Recall  | F1      | Pass | Failure Mode  |
|------|-----------|---------|---------|------|---------------|
| 150  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 168  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 177  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 187  | 1.000     | 0.963   | 0.980   | NO   | truncation    |
| 225  | 0.983     | 1.000   | 0.991   | NO   | comprehension |
| 300  | 0.667     | 0.509   | 0.576   | NO   | truncation    |

**claude-sonnet-4.5 medium**

| Rows | Precision | Recall  | F1      | Pass | Failure Mode  |
|------|-----------|---------|---------|------|---------------|
| 150  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 168  | 1.000     | 1.000   | 1.000   | YES  | -             |
| 177  | 1.000     | 0.983   | 0.992   | NO   | comprehension |
| 187  | 0.969     | 1.000   | 0.984   | NO   | comprehension |
| 225  | 0.806     | 0.974   | 0.882   | NO   | comprehension |
| 300  | 0.979     | 1.000   | 0.989   | NO   | comprehension |

**claude-opus-4.7 medium**

| Rows | Precision | Recall  | F1      | Pass | Failure Mode  |
|------|-----------|---------|---------|------|---------------|
| 12   | 1.000     | 1.000   | 1.000   | YES  | -             |
| 18   | 0.944     | 1.000   | 0.970   | NO   | comprehension |
| 25   | 0.963     | 1.000   | 0.980   | NO   | comprehension |
| 50   | 0.851     | 1.000   | 0.919   | NO   | comprehension |
| 100  | 0.792     | 0.655   | 0.669   | NO   | comprehension |
| 200  | 0.713     | 0.402   | 0.397   | NO   | comprehension |

**claude-haiku-4.5 medium**

| Rows | Precision | Recall  | F1      | Pass | Failure Mode  |
|------|-----------|---------|---------|------|---------------|
| 9    | 1.000     | 1.000   | 1.000   | YES  | -             |
| 18   | 0.625     | 1.000   | 0.769   | NO   | comprehension |
| 37   | 0.722     | 1.000   | 0.839   | NO   | comprehension |
| 75   | 0.649     | 1.000   | 0.787   | NO   | comprehension |
| 150  | 0.520     | 0.796   | 0.629   | NO   | truncation    |
| 300  | 0.527     | 0.419   | 0.467   | NO   | truncation    |

**claude-opus-4.6 medium**

| Rows | Precision | Recall  | F1      | Pass | Failure Mode  |
|------|-----------|---------|---------|------|---------------|
| 6    | 1.000     | 1.000   | 1.000   | YES  | -             |
| 12   | 1.000     | 0.500   | 0.667   | NO   | comprehension |
| 25   | 1.000     | 0.875   | 0.933   | NO   | comprehension |
| 50   | 1.000     | 0.941   | 0.970   | NO   | comprehension |
| 100  | 1.000     | 0.931   | 0.964   | NO   | comprehension |
| 200  | 1.000     | 0.980   | 0.990   | NO   | comprehension |

**gpt-4o-mini medium**

| Rows | Precision | Recall  | F1      | Pass | Failure Mode  |
|------|-----------|---------|---------|------|---------------|
| 6    | 1.000     | 1.000   | 1.000   | YES  | -             |
| 12   | 0.500     | 1.000   | 0.667   | NO   | comprehension |
| 25   | 0.700     | 0.875   | 0.778   | NO   | comprehension |
| 50   | 0.722     | 0.765   | 0.743   | NO   | comprehension |

**gpt-4o medium**

| Rows | Precision | Recall  | F1      | Pass | Failure Mode  |
|------|-----------|---------|---------|------|---------------|
| 4    | 1.000     | 1.000   | 1.000   | YES  | -             |
| 9    | 1.000     | 0.500   | 0.667   | NO   | comprehension |
| 18   | 0.750     | 0.600   | 0.667   | NO   | comprehension |
| 37   | 0.889     | 0.615   | 0.727   | NO   | comprehension |
| 75   | 0.652     | 0.625   | 0.638   | NO   | comprehension |
| 150  | 0.508     | 0.653   | 0.571   | NO   | comprehension |
| 300  | 0.468     | 0.710   | 0.564   | NO   | comprehension |
<!-- AUTO:section-9.1:end -->

### 9.2 Cost Scaling (Cost per Request at Each Row Count)

<!-- AUTO:section-9.2:start -->
| Config              | Rows | Cost/req  | In Tokens | Out Tokens | Total Cost |
|---------------------|------|-----------|-----------|------------|------------|
| claude-haiku-4.5 medium | 9    | $0.0014   | 899       | 109        | $0.0014    |
| claude-haiku-4.5 medium | 18   | $0.0036   | 1383      | 438        | $0.0036    |
| claude-haiku-4.5 medium | 37   | $0.0073   | 2395      | 986        | $0.0073    |
| claude-haiku-4.5 medium | 75   | $0.015    | 4460      | 2038       | $0.015     |
| claude-haiku-4.5 medium | 150  | $0.029    | 8521      | 4096       | $0.029     |
| claude-haiku-4.5 medium | 300  | $0.037    | 16687     | 4096       | $0.037     |
| claude-opus-4.5 medium | 150  | $0.248    | 25650     | 24648      | $0.744     |
| claude-opus-4.5 medium | 168  | $0.294    | 28575     | 29539      | $0.881     |
| claude-opus-4.5 medium | 177  | $0.293    | 29970     | 29124      | $0.878     |
| claude-opus-4.5 medium | 187  | $0.302    | 31698     | 29932      | $0.907     |
| claude-opus-4.5 medium | 225  | $0.290    | 37818     | 27294      | $0.871     |
| claude-opus-4.5 medium | 300  | $0.359    | 50148     | 33072      | $1.078     |
| claude-opus-4.6 high | 200  | $0.248    | 33732     | 22996      | $0.744     |
| claude-opus-4.6 high | 300  | $0.433    | 50061     | 41929      | $1.299     |
| claude-opus-4.6 high | 450  | $0.558    | 74409     | 52137      | $1.675     |
| claude-opus-4.6 high | 562  | $0.679    | 92511     | 63021      | $2.038     |
| claude-opus-4.6 high | 618  | $0.748    | 101589    | 69384      | $2.243     |
| claude-opus-4.6 high | 646  | $0.754    | 106104    | 69212      | $2.261     |
| claude-opus-4.6 high | 660  | $0.814    | 108357    | 75988      | $2.441     |
| claude-opus-4.6 high | 667  | $0.811    | 109464    | 75418      | $2.433     |
| claude-opus-4.6 high | 675  | $0.817    | 110757    | 75945      | $2.452     |
| claude-opus-4.6 medium | 6    | $0.0064   | 2214      | 327        | $0.019     |
| claude-opus-4.6 medium | 12   | $0.0068   | 3183      | 174        | $0.020     |
| claude-opus-4.6 medium | 25   | $0.024    | 5271      | 1777       | $0.071     |
| claude-opus-4.6 medium | 50   | $0.049    | 9264      | 4040       | $0.147     |
| claude-opus-4.6 medium | 100  | $0.089    | 17436     | 7134       | $0.266     |
| claude-opus-4.6 medium | 200  | $0.199    | 33732     | 17093      | $0.596     |
| claude-opus-4.7 medium | 12   | $0.012    | 4776      | 507        | $0.037     |
| claude-opus-4.7 medium | 18   | $0.023    | 6246      | 1502       | $0.069     |
| claude-opus-4.7 medium | 25   | $0.036    | 7968      | 2765       | $0.109     |
| claude-opus-4.7 medium | 50   | $0.108    | 14016     | 10133      | $0.323     |
| claude-opus-4.7 medium | 100  | $0.180    | 26301     | 16362      | $0.541     |
| claude-opus-4.7 medium | 200  | $0.295    | 50847     | 25237      | $0.885     |
| claude-opus-4.8 high | 250  | $0.388    | 62979     | 33988      | $1.165     |
| claude-opus-4.8 high | 375  | $0.543    | 93552     | 46401      | $1.628     |
| claude-opus-4.8 high | 437  | $0.635    | 108702    | 54516      | $1.906     |
| claude-opus-4.8 high | 468  | $0.702    | 116400    | 60956      | $2.106     |
| claude-opus-4.8 high | 484  | $0.727    | 120336    | 63136      | $2.180     |
| claude-opus-4.8 high | 492  | $0.721    | 122289    | 62069      | $2.163     |
| claude-opus-4.8 high | 500  | $0.748    | 124308    | 64921      | $2.245     |
| claude-sonnet-4 medium | 150  | $0.168    | 25650     | 28489      | $0.504     |
| claude-sonnet-4 medium | 187  | $0.184    | 31698     | 30527      | $0.553     |
| claude-sonnet-4 medium | 196  | $0.180    | 33162     | 29408      | $0.541     |
| claude-sonnet-4 medium | 206  | $0.200    | 34770     | 33072      | $0.600     |
| claude-sonnet-4 medium | 225  | $0.189    | 37818     | 30211      | $0.567     |
| claude-sonnet-4 medium | 300  | $0.216    | 50148     | 33072      | $0.647     |
| claude-sonnet-4.5 medium | 150  | $0.109    | 8550      | 5551       | $0.109     |
| claude-sonnet-4.5 medium | 168  | $0.121    | 9525      | 6180       | $0.121     |
| claude-sonnet-4.5 medium | 177  | $0.133    | 9990      | 6872       | $0.133     |
| claude-sonnet-4.5 medium | 187  | $0.137    | 10566     | 7037       | $0.137     |
| claude-sonnet-4.5 medium | 225  | $0.178    | 12606     | 9345       | $0.178     |
| claude-sonnet-4.5 medium | 300  | $0.211    | 16716     | 10725      | $0.211     |
| gpt-4o medium       | 4    | $0.0011   | 548       | 90         | $0.0011    |
| gpt-4o medium       | 9    | $0.0012   | 785       | 45         | $0.0012    |
| gpt-4o medium       | 18   | $0.0024   | 1203      | 187        | $0.0024    |
| gpt-4o medium       | 37   | $0.0048   | 2079      | 432        | $0.0048    |
| gpt-4o medium       | 75   | $0.010    | 3858      | 1086       | $0.010     |
| gpt-4o medium       | 150  | $0.024    | 7370      | 2997       | $0.024     |
| gpt-4o medium       | 300  | $0.052    | 14425     | 6717       | $0.052     |
| gpt-4o-mini medium  | 6    | $0.0001   | 648       | 90         | $0.0001    |
| gpt-4o-mini medium  | 12   | $0.0001   | 927       | 188        | $0.0001    |
| gpt-4o-mini medium  | 25   | $0.0003   | 1528      | 470        | $0.0003    |
| gpt-4o-mini medium  | 50   | $0.0005   | 2679      | 853        | $0.0005    |
| gpt-5 high          | None | $0.0000   | -         | -          | -          |
| gpt-5 high          | 300  | $0.123    | 43272     | 68158      | $0.368     |
| gpt-5 high          | 450  | $0.140    | 64263     | 76228      | $0.421     |
| gpt-5 high          | 478  | $0.138    | 68145     | 74169      | $0.413     |
| gpt-5 high          | 492  | $0.132    | 23380     | 23480      | $0.132     |
| gpt-5 high          | 499  | $0.166    | 71127     | 90609      | $0.497     |
| gpt-5 high          | 506  | $0.137    | 72111     | 73476      | $0.412     |
| gpt-5 high          | 562  | $0.163    | 79944     | 87894      | $0.489     |
| gpt-5 medium        | 300  | $0.050    | 14424     | 8234       | $0.050     |
| gpt-5 medium        | 300  | $0.080    | 43272     | 42750      | $0.241     |
| gpt-5 medium        | 337  | $0.078    | 16147     | 13506      | $0.078     |
| gpt-5 medium        | 356  | $0.076    | 17048     | 12990      | $0.076     |
| gpt-5 medium        | 365  | $0.061    | 17468     | 9935       | $0.061     |
| gpt-5 medium        | 375  | $0.092    | 17924     | 16171      | $0.092     |
| gpt-5 medium        | 450  | $0.077    | 21421     | 12743      | $0.077     |
| gpt-5 medium        | 450  | $0.132    | 64263     | 70981      | $0.395     |
| gpt-5 medium        | 457  | $0.130    | 65232     | 69852      | $0.390     |
| gpt-5 medium        | 464  | $0.119    | 66198     | 62946      | $0.356     |
| gpt-5 medium        | 478  | $0.152    | 68145     | 82705      | $0.456     |
| gpt-5 medium        | 506  | $0.125    | 72111     | 66037      | $0.375     |
| gpt-5 medium        | 562  | $0.139    | 79944     | 73432      | $0.417     |
| gpt-5 medium        | 675  | $0.171    | 63778     | 60560      | $0.343     |
| gpt-5-mini medium   | 37   | $0.0015   | 6234      | 3661       | $0.0044    |
| gpt-5-mini medium   | 56   | $0.0022   | 8892      | 5477       | $0.0066    |
| gpt-5-mini medium   | 65   | $0.0026   | 10173     | 6433       | $0.0077    |
| gpt-5-mini medium   | 75   | $0.0028   | 11571     | 6977       | $0.0084    |
| gpt-5-mini medium   | 150  | $0.0050   | 22107     | 12245      | $0.015     |
| gpt-5-mini medium   | 300  | $0.0077   | 43272     | 17660      | $0.023     |
| gpt-5-mini medium   | 500  | $0.017    | 71268     | 42471      | $0.051     |
| gpt-5-mini medium   | 507  | $0.018    | 72243     | 46442      | $0.055     |
| gpt-5-mini medium   | 515  | $0.025    | 73353     | 65524      | $0.075     |
| gpt-5-mini medium   | 531  | $0.020    | 75576     | 51112      | $0.061     |
| gpt-5-mini medium   | 562  | $0.019    | 79944     | 45935      | $0.056     |
| gpt-5-mini medium   | 625  | $0.021    | 88764     | 50535      | $0.062     |
| gpt-5-mini medium   | 750  | $0.019    | 70848     | 29043      | $0.038     |
| gpt-5.2 medium      | 150  | $0.032    | 7369      | 3709       | $0.032     |
| gpt-5.2 medium      | 187  | $0.041    | 9114      | 4674       | $0.041     |
| gpt-5.2 medium      | 206  | $0.049    | 10005     | 5701       | $0.049     |
| gpt-5.2 medium      | 215  | $0.046    | 10425     | 5300       | $0.046     |
| gpt-5.2 medium      | 225  | $0.064    | 10881     | 7735       | $0.064     |
| gpt-5.2 medium      | 300  | $0.055    | 14424     | 6074       | $0.055     |
| gpt-5.4 medium      | 250  | $0.070    | 36156     | 21799      | $0.209     |
| gpt-5.4 medium      | 375  | $0.119    | 53772     | 38580      | $0.357     |
| gpt-5.4 medium      | 437  | $0.129    | 62415     | 41057      | $0.386     |
| gpt-5.4 medium      | 468  | $0.115    | 66780     | 34933      | $0.345     |
| gpt-5.4 medium      | 484  | $0.134    | 69009     | 42248      | $0.403     |
| gpt-5.4 medium      | 492  | $0.135    | 70140     | 42460      | $0.406     |
| gpt-5.4 medium      | 500  | $0.127    | 71268     | 38883      | $0.381     |
| gpt-5.5 medium      | 250  | $0.239    | 36156     | 17879      | $0.717     |
| gpt-5.5 medium      | 375  | $0.347    | 53772     | 25689      | $1.040     |
| gpt-5.5 medium      | 437  | $0.414    | 62415     | 30972      | $1.241     |
| gpt-5.5 medium      | 444  | $0.406    | 63414     | 30027      | $1.218     |
| gpt-5.5 medium      | 452  | $0.434    | 64542     | 32607      | $1.301     |
| gpt-5.5 medium      | 468  | $0.435    | 66780     | 32404      | $1.306     |
| gpt-5.5 medium      | 500  | $0.444    | 71268     | 32498      | $1.331     |
<!-- AUTO:section-9.2:end -->

### 9.3 Latency Scaling (Time per Request at Each Row Count)

<!-- AUTO:section-9.3:start -->
| Config              | Rows | Time/req | Total Duration |
|---------------------|------|----------|----------------|
| claude-haiku-4.5 medium | 9    | 2s       | 2s             |
| claude-haiku-4.5 medium | 18   | 4s       | 4s             |
| claude-haiku-4.5 medium | 37   | 6s       | 6s             |
| claude-haiku-4.5 medium | 75   | 13s      | 13s            |
| claude-haiku-4.5 medium | 150  | 24s      | 24s            |
| claude-haiku-4.5 medium | 300  | 23s      | 23s            |
| claude-opus-4.5 medium | 150  | 27s      | 1.4m           |
| claude-opus-4.5 medium | 168  | 30s      | 1.5m           |
| claude-opus-4.5 medium | 177  | 32s      | 1.6m           |
| claude-opus-4.5 medium | 187  | 34s      | 1.7m           |
| claude-opus-4.5 medium | 225  | 32s      | 1.6m           |
| claude-opus-4.5 medium | 300  | 37s      | 1.9m           |
| claude-opus-4.6 high | 200  | 29s      | 1.5m           |
| claude-opus-4.6 high | 300  | 1.1m     | 3.3m           |
| claude-opus-4.6 high | 450  | 1.0m     | 3.1m           |
| claude-opus-4.6 high | 562  | 1.3m     | 3.8m           |
| claude-opus-4.6 high | 618  | 1.4m     | 4.2m           |
| claude-opus-4.6 high | 646  | 1.5m     | 4.5m           |
| claude-opus-4.6 high | 660  | 3.2m     | 9.5m           |
| claude-opus-4.6 high | 667  | 1.5m     | 4.5m           |
| claude-opus-4.6 high | 675  | 1.6m     | 4.7m           |
| claude-opus-4.6 medium | 6    | 2s       | 5s             |
| claude-opus-4.6 medium | 12   | 2s       | 5s             |
| claude-opus-4.6 medium | 25   | 4s       | 11s            |
| claude-opus-4.6 medium | 50   | 6s       | 17s            |
| claude-opus-4.6 medium | 100  | 12s      | 36s            |
| claude-opus-4.6 medium | 200  | 24s      | 1.2m           |
| claude-opus-4.7 medium | 12   | 2s       | 6s             |
| claude-opus-4.7 medium | 18   | 3s       | 9s             |
| claude-opus-4.7 medium | 25   | 5s       | 16s            |
| claude-opus-4.7 medium | 50   | 13s      | 39s            |
| claude-opus-4.7 medium | 100  | 24s      | 1.2m           |
| claude-opus-4.7 medium | 200  | 29s      | 1.5m           |
| claude-opus-4.8 high | 250  | 32s      | 1.6m           |
| claude-opus-4.8 high | 375  | 44s      | 2.2m           |
| claude-opus-4.8 high | 437  | 51s      | 2.5m           |
| claude-opus-4.8 high | 468  | 1.0m     | 3.1m           |
| claude-opus-4.8 high | 484  | 1.0m     | 3.0m           |
| claude-opus-4.8 high | 492  | 59s      | 3.0m           |
| claude-opus-4.8 high | 500  | 1.0m     | 3.1m           |
| claude-sonnet-4 medium | 150  | 40s      | 2.0m           |
| claude-sonnet-4 medium | 187  | 40s      | 2.0m           |
| claude-sonnet-4 medium | 196  | 43s      | 2.1m           |
| claude-sonnet-4 medium | 206  | 46s      | 2.3m           |
| claude-sonnet-4 medium | 225  | 47s      | 2.3m           |
| claude-sonnet-4 medium | 300  | 47s      | 2.4m           |
| claude-sonnet-4.5 medium | 150  | 59s      | 59s            |
| claude-sonnet-4.5 medium | 168  | 1.1m     | 1.1m           |
| claude-sonnet-4.5 medium | 177  | 1.4m     | 1.4m           |
| claude-sonnet-4.5 medium | 187  | 1.3m     | 1.3m           |
| claude-sonnet-4.5 medium | 225  | 1.8m     | 1.8m           |
| claude-sonnet-4.5 medium | 300  | 2.0m     | 2.0m           |
| gpt-4o medium       | 4    | 3s       | 3s             |
| gpt-4o medium       | 9    | 2s       | 2s             |
| gpt-4o medium       | 18   | 4s       | 4s             |
| gpt-4o medium       | 37   | 6s       | 6s             |
| gpt-4o medium       | 75   | 10s      | 10s            |
| gpt-4o medium       | 150  | 43s      | 43s            |
| gpt-4o medium       | 300  | 1.0m     | 1.0m           |
| gpt-4o-mini medium  | 6    | 5s       | 5s             |
| gpt-4o-mini medium  | 12   | 6s       | 6s             |
| gpt-4o-mini medium  | 25   | 10s      | 10s            |
| gpt-4o-mini medium  | 50   | 14s      | 14s            |
| gpt-5 high          | None | 45.2m    | 45.2m          |
| gpt-5 high          | 300  | 1.2m     | 3.7m           |
| gpt-5 high          | 450  | 4.8m     | 14.3m          |
| gpt-5 high          | 478  | 4.9m     | 14.8m          |
| gpt-5 high          | 492  | 45.2m    | 45.2m          |
| gpt-5 high          | 499  | 5.2m     | 15.6m          |
| gpt-5 high          | 506  | 6.5m     | 19.6m          |
| gpt-5 high          | 562  | 1.4m     | 4.2m           |
| gpt-5 medium        | 300  | 1.8m     | 1.8m           |
| gpt-5 medium        | 300  | 1.2m     | 3.6m           |
| gpt-5 medium        | 337  | 2.5m     | 2.5m           |
| gpt-5 medium        | 356  | 2.2m     | 2.2m           |
| gpt-5 medium        | 365  | 1.8m     | 1.8m           |
| gpt-5 medium        | 375  | 2.8m     | 2.8m           |
| gpt-5 medium        | 450  | 3.1m     | 3.1m           |
| gpt-5 medium        | 450  | 1.5m     | 4.5m           |
| gpt-5 medium        | 457  | 1.6m     | 4.9m           |
| gpt-5 medium        | 464  | 3.1m     | 9.3m           |
| gpt-5 medium        | 478  | 1.5m     | 4.6m           |
| gpt-5 medium        | 506  | 1.6m     | 4.9m           |
| gpt-5 medium        | 562  | 1.4m     | 4.2m           |
| gpt-5 medium        | 675  | 22.6m    | 45.1m          |
| gpt-5-mini medium   | 37   | 10s      | 29s            |
| gpt-5-mini medium   | 56   | 14s      | 43s            |
| gpt-5-mini medium   | 65   | 16s      | 48s            |
| gpt-5-mini medium   | 75   | 22s      | 1.1m           |
| gpt-5-mini medium   | 150  | 28s      | 1.4m           |
| gpt-5-mini medium   | 300  | 39s      | 2.0m           |
| gpt-5-mini medium   | 500  | 1.2m     | 3.5m           |
| gpt-5-mini medium   | 507  | 7.3m     | 21.8m          |
| gpt-5-mini medium   | 515  | 1.7m     | 5.0m           |
| gpt-5-mini medium   | 531  | 3.0m     | 9.1m           |
| gpt-5-mini medium   | 562  | 9.5m     | 28.6m          |
| gpt-5-mini medium   | 625  | 10.0m    | 30.0m          |
| gpt-5-mini medium   | 750  | 18.4m    | 36.8m          |
| gpt-5.2 medium      | 150  | 39s      | 39s            |
| gpt-5.2 medium      | 187  | 51s      | 51s            |
| gpt-5.2 medium      | 206  | 1.0m     | 1.0m           |
| gpt-5.2 medium      | 215  | 55s      | 55s            |
| gpt-5.2 medium      | 225  | 1.3m     | 1.3m           |
| gpt-5.2 medium      | 300  | 1.1m     | 1.1m           |
| gpt-5.4 medium      | 250  | 25s      | 1.3m           |
| gpt-5.4 medium      | 375  | 49s      | 2.4m           |
| gpt-5.4 medium      | 437  | 55s      | 2.8m           |
| gpt-5.4 medium      | 468  | 46s      | 2.3m           |
| gpt-5.4 medium      | 484  | 58s      | 2.9m           |
| gpt-5.4 medium      | 492  | 51s      | 2.6m           |
| gpt-5.4 medium      | 500  | 49s      | 2.4m           |
| gpt-5.5 medium      | 250  | 47s      | 2.4m           |
| gpt-5.5 medium      | 375  | 27s      | 1.3m           |
| gpt-5.5 medium      | 437  | 32s      | 1.6m           |
| gpt-5.5 medium      | 444  | 34s      | 1.7m           |
| gpt-5.5 medium      | 452  | 40s      | 2.0m           |
| gpt-5.5 medium      | 468  | 36s      | 1.8m           |
| gpt-5.5 medium      | 500  | 37s      | 1.9m           |
<!-- AUTO:section-9.3:end -->

### 9.4 Variance Analysis (Run-to-Run Consistency)

<!-- AUTO:section-9.4:start -->
| Config              | Rows | Precision Std | Recall Std | Runs Passed/Total |
|---------------------|------|---------------|------------|-------------------|
| gpt-5 high          | 562  | 0.5774        | 0.5774     | 2/3             |
| gpt-5 high          | 499  | 0.5774        | 0.5774     | 2/3             |
| claude-opus-4.7 medium | 200  | 0.0578        | 0.5003     | 0/3             |
| gpt-5-mini medium   | 750  | 0.0062        | 0.4912     | 0/2             |
| claude-opus-4.5 medium | 300  | 0.5774        | 0.4472     | 0/3             |
| claude-sonnet-4 medium | 300  | 0.5774        | 0.4024     | 0/3             |
| claude-opus-4.7 medium | 100  | 0.0814        | 0.3633     | 0/3             |
| claude-sonnet-4 medium | 225  | 0.0146        | 0.2624     | 1/3             |
| claude-sonnet-4 medium | 206  | 0.0000        | 0.2076     | 0/3             |
| gpt-5-mini medium   | 300  | 0.0000        | 0.0937     | 0/3             |
| claude-opus-4.5 medium | 187  | 0.0000        | 0.0641     | 2/3             |
| claude-opus-4.6 medium | 100  | 0.0000        | 0.0345     | 0/3             |
| gpt-5-mini medium   | 75   | 0.0000        | 0.0241     | 2/3             |
| gpt-5.5 medium      | 500  | 0.0000        | 0.0231     | 2/3             |
| gpt-5-mini medium   | 625  | 0.0000        | 0.0195     | 1/3             |
| gpt-5 medium        | 562  | 0.0000        | 0.0176     | 0/3             |
| gpt-5-mini medium   | 507  | 0.0000        | 0.0154     | 2/3             |
| gpt-5 medium        | 457  | 0.0000        | 0.0153     | 1/3             |
| gpt-5-mini medium   | 150  | 0.0000        | 0.0118     | 2/3             |
| gpt-5 medium        | 478  | 0.0041        | 0.0109     | 1/3             |
| gpt-5 medium        | 464  | 0.0000        | 0.0085     | 2/3             |
| claude-opus-4.6 medium | 200  | 0.0000        | 0.0085     | 0/3             |
| gpt-5.4 medium      | 500  | 0.0000        | 0.0077     | 2/3             |
| gpt-5 high          | 506  | 0.0000        | 0.0077     | 2/3             |
| gpt-5-mini medium   | 515  | 0.0000        | 0.0076     | 1/3             |
| gpt-5.5 medium      | 444  | 0.0000        | 0.0043     | 2/3             |
| gpt-5.5 medium      | 452  | 0.0000        | 0.0043     | 2/3             |
| gpt-5.5 medium      | 468  | 0.0000        | 0.0042     | 2/3             |
| claude-opus-4.8 high | 500  | 0.0000        | 0.0039     | 2/3             |
| gpt-5 medium        | 506  | 0.0000        | 0.0039     | 2/3             |
| gpt-5-mini medium   | 531  | 0.0000        | 0.0037     | 2/3             |
| gpt-5-mini medium   | 562  | 0.0000        | 0.0035     | 2/3             |
| gpt-5 medium        | 675  | 0.0000        | 0.0035     | 0/2             |
| claude-opus-4.5 medium | 225  | 0.0146        | 0.0000     | 1/3             |
| claude-opus-4.6 high | 675  | 0.0028        | 0.0000     | 2/3             |
| claude-opus-4.7 medium | 50   | 0.0426        | 0.0000     | 0/3             |
| claude-opus-4.7 medium | 25   | 0.0641        | 0.0000     | 2/3             |
| claude-opus-4.7 medium | 18   | 0.0962        | 0.0000     | 2/3             |
| claude-sonnet-4 medium | 196  | 0.0085        | 0.0000     | 2/3             |
<!-- AUTO:section-9.4:end -->

### 9.5 Efficiency Frontier (Rows/$ and Rows/sec)

<!-- AUTO:section-9.5:start -->
| Config              | Max Rows (passed) | Cost/req  | Time/req | Rows/$    | Rows/sec |
|---------------------|-------------------|-----------|----------|-----------|----------|
| gpt-4o-mini medium  | 6                 | $0.0001   | 5s       | 78947     | 1.2      |
| gpt-5-mini medium   | 500               | $0.017    | 1.2m     | 29194     | 7.1      |
| claude-haiku-4.5 medium | 9                 | $0.0014   | 2s       | 6233      | 4.0      |
| gpt-5.2 medium      | 215               | $0.046    | 55s      | 4651      | 3.9      |
| gpt-5 high          | 492               | $0.132    | 45.2m    | 3727      | 0.2      |
| gpt-5.4 medium      | 492               | $0.135    | 51s      | 3634      | 9.6      |
| gpt-4o medium       | 4                 | $0.0011   | 3s       | 3524      | 1.2      |
| gpt-5 medium        | 450               | $0.132    | 1.5m     | 3417      | 5.0      |
| claude-sonnet-4.5 medium | 168               | $0.121    | 1.1m     | 1385      | 2.5      |
| gpt-5.5 medium      | 437               | $0.414    | 32s      | 1056      | 13.5     |
| claude-sonnet-4 medium | 187               | $0.184    | 40s      | 1014      | 4.7      |
| claude-opus-4.7 medium | 12                | $0.012    | 2s       | 985       | 6.5      |
| claude-opus-4.6 medium | 6                 | $0.0064   | 2s       | 935       | 3.5      |
| claude-opus-4.6 high | 667               | $0.811    | 1.5m     | 823       | 7.3      |
| claude-opus-4.8 high | 492               | $0.721    | 59s      | 682       | 8.3      |
<!-- AUTO:section-9.5:end -->

### 9.6 Production Decision Matrix

<!-- AUTO:section-9.6:start -->
#### Fixed-Workload Comparison

Models that pass reliably at each workload size, sorted by cost:

**50 rows** (11 configs qualify)

| Config              | Cost/req  | Time/req | Tested At |
|---------------------|-----------|----------|-----------|
| gpt-5-mini medium   | $0.0022   | 14s      | 56 rows   |
| gpt-5.2 medium      | $0.032    | 39s      | 150 rows  |
| gpt-5 medium        | $0.050    | 1.8m     | 300 rows  |
| gpt-5.4 medium      | $0.070    | 25s      | 250 rows  |
| claude-sonnet-4.5 medium | $0.109    | 59s      | 150 rows  |
| gpt-5 high          | $0.123    | 1.2m     | 300 rows  |
| claude-sonnet-4 medium | $0.168    | 40s      | 150 rows  |
| gpt-5.5 medium      | $0.239    | 47s      | 250 rows  |

**100 rows** (11 configs qualify)

| Config              | Cost/req  | Time/req | Tested At |
|---------------------|-----------|----------|-----------|
| gpt-5-mini medium   | $0.017    | 1.2m     | 500 rows  |
| gpt-5.2 medium      | $0.032    | 39s      | 150 rows  |
| gpt-5 medium        | $0.050    | 1.8m     | 300 rows  |
| gpt-5.4 medium      | $0.070    | 25s      | 250 rows  |
| claude-sonnet-4.5 medium | $0.109    | 59s      | 150 rows  |
| gpt-5 high          | $0.123    | 1.2m     | 300 rows  |
| claude-sonnet-4 medium | $0.168    | 40s      | 150 rows  |
| gpt-5.5 medium      | $0.239    | 47s      | 250 rows  |

**150 rows** (11 configs qualify)

| Config              | Cost/req  | Time/req | Tested At |
|---------------------|-----------|----------|-----------|
| gpt-5-mini medium   | $0.017    | 1.2m     | 500 rows  |
| gpt-5.2 medium      | $0.032    | 39s      | 150 rows  |
| gpt-5 medium        | $0.050    | 1.8m     | 300 rows  |
| gpt-5.4 medium      | $0.070    | 25s      | 250 rows  |
| claude-sonnet-4.5 medium | $0.109    | 59s      | 150 rows  |
| gpt-5 high          | $0.123    | 1.2m     | 300 rows  |
| claude-sonnet-4 medium | $0.168    | 40s      | 150 rows  |
| gpt-5.5 medium      | $0.239    | 47s      | 250 rows  |

**200 rows** (8 configs qualify)

| Config              | Cost/req  | Time/req | Tested At |
|---------------------|-----------|----------|-----------|
| gpt-5-mini medium   | $0.017    | 1.2m     | 500 rows  |
| gpt-5.2 medium      | $0.049    | 1.0m     | 206 rows  |
| gpt-5 medium        | $0.050    | 1.8m     | 300 rows  |
| gpt-5.4 medium      | $0.070    | 25s      | 250 rows  |
| gpt-5 high          | $0.123    | 1.2m     | 300 rows  |
| gpt-5.5 medium      | $0.239    | 47s      | 250 rows  |
| claude-opus-4.6 high | $0.248    | 29s      | 200 rows  |
| claude-opus-4.8 high | $0.388    | 32s      | 250 rows  |

**300 rows** (7 configs qualify)

| Config              | Cost/req  | Time/req | Tested At |
|---------------------|-----------|----------|-----------|
| gpt-5-mini medium   | $0.017    | 1.2m     | 500 rows  |
| gpt-5 medium        | $0.050    | 1.8m     | 300 rows  |
| gpt-5.4 medium      | $0.119    | 49s      | 375 rows  |
| gpt-5 high          | $0.123    | 1.2m     | 300 rows  |
| gpt-5.5 medium      | $0.347    | 27s      | 375 rows  |
| claude-opus-4.6 high | $0.433    | 1.1m     | 300 rows  |
| claude-opus-4.8 high | $0.543    | 44s      | 375 rows  |

**400 rows** (7 configs qualify)

| Config              | Cost/req  | Time/req | Tested At |
|---------------------|-----------|----------|-----------|
| gpt-5-mini medium   | $0.017    | 1.2m     | 500 rows  |
| gpt-5.4 medium      | $0.129    | 55s      | 437 rows  |
| gpt-5 medium        | $0.132    | 1.5m     | 450 rows  |
| gpt-5 high          | $0.140    | 4.8m     | 450 rows  |
| gpt-5.5 medium      | $0.414    | 32s      | 437 rows  |
| claude-opus-4.6 high | $0.558    | 1.0m     | 450 rows  |
| claude-opus-4.8 high | $0.635    | 51s      | 437 rows  |

**500 rows** (2 configs qualify)

| Config              | Cost/req  | Time/req | Tested At |
|---------------------|-----------|----------|-----------|
| gpt-5-mini medium   | $0.017    | 1.2m     | 500 rows  |
| claude-opus-4.6 high | $0.679    | 1.3m     | 562 rows  |

#### Pareto-Optimal Configurations (>=100 rows, Non-Dominated)

Configs with >=100 rows where no other config is simultaneously better on all 3 axes:

| Config              | Max Rows | Cost/req  | Time/req |
|---------------------|----------|-----------|----------|
| claude-opus-4.6 high | 667      | $0.811    | 1.5m     |
| gpt-5-mini medium   | 500      | $0.017    | 1.2m     |
| gpt-5.4 medium      | 492      | $0.135    | 51s      |
| gpt-5.5 medium      | 437      | $0.414    | 32s      |
| gpt-5.2 medium      | 215      | $0.046    | 55s      |
| claude-sonnet-4 medium | 187      | $0.184    | 40s      |
| claude-opus-4.5 medium | 177      | $0.293    | 32s      |

#### Constraint-Based Recommendations

| Scenario                       | Winner              | Rows | Cost/req  | Time/req |
|--------------------------------|---------------------|------|-----------|----------|
| Budget <$0.10, latency <60s    | gpt-5.2 medium      | 215  | $0.046    | 55s      |
| Need 200+ rows, cheapest       | gpt-5-mini medium   | 500  | $0.017    | 1.2m     |
| Need 200+ rows, fastest        | gpt-5.5 medium      | 437  | $0.414    | 32s      |
| Need 400+ rows, fastest        | gpt-5.5 medium      | 437  | $0.414    | 32s      |
| Latency <2min, max rows        | claude-opus-4.6 high | 667  | $0.811    | 1.5m     |
| Best rows/$ efficiency         | gpt-5-mini medium   | 500  | $0.017    | 1.2m     |
<!-- AUTO:section-9.6:end -->

## 10. Data Verification

- All data generated by `06_aggregate_results.py` from source `scale_limit_result.json` files
- Time/req = single LLM API call time (iteration duration / verification runs)
- Costs = total test cost (all iterations combined)
- gpt-5-mini medium re-run confirmed 500 rows (original run found 389; bounds [500, 507])
- claude-opus-4.8 high confirmed 492 rows (bounds [492, 500]; $19.96 total; verified against Anthropic billing: $89.19 - $69.23 = $19.96)
- claude-sonnet-4 corrected: 187 rows, truncation, 25.1% (previously miscategorized as 168, comprehension)
- Calculation verifications:
  - gpt-5-mini effort improvement: (500 - 65) / 65 = 669%, 500 / 65 = 7.69 = 7.7x
  - gpt-5 effort improvement: (492 - 356) / 356 = 38%, (450 - 356) / 356 = 26%
  - Mini tier ratio: 500 / 6 = 83.3 = 83x
  - Full tier ratio: 356 / 4 = 89x
  - Opus 4.6 effort ratio: 667 / 6 = 111x

## 11. Sources

- `_SPEC_CSVScaleLimits.md [TBLF-SP01]` - Test framework specification
- `_TEST_CSVScaleLimits.md [TBLF-TP01]` - Test execution procedures
- `_INFO_LLM_MARKDOWN_PREFERENCES.md [LLMO-IN01]` - Format benchmarking research (TK-001)
- `_SPEC_LLM_CLIENT.md [LLMC-SP01]` - LLM client specification
- `.windsurf/skills/llm-evaluation/` - Original LLM evaluation scripts
- `_TestsAndResults/*/scale_limit_result.json` - Raw test result data

## 12. Document History

**[2026-05-30 17:39]**
- Added: claude-opus-4.8 high test result (492 rows, comprehension failure, $19.96)
- Changed: Test count 19/19 → 20/20
- Changed: All AUTO sections regenerated with new data point

**[2026-05-22 18:02]**
- Added: Section 9 "Deep Analysis" with 6 subsections (9.1-9.6) using AUTO markers
- Added: Per-iteration accuracy curves, cost/latency scaling, variance analysis
- Added: Production Decision Matrix (fixed-workload, Pareto frontier, constraint recommendations)
- Changed: Sections renumbered (old 9-11 now 10-12)
- Changed: Pareto frontier filtered to configs with >=100 rows
- Changed: Constraint recommendations use 2-min latency threshold

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
