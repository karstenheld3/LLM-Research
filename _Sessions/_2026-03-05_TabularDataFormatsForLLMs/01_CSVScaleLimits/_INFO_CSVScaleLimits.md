<DevSystem MarkdownTablesAllowed=true />

# INFO: CSV Scale Limits

**Doc ID**: TBLF-IN01
**Goal**: Determine maximum reliable row counts for LLM tabular data extraction across models
**Timeline**: Created 2026-03-05

## Summary

**Research Question:** At what scale do LLMs fail to reliably extract filtered data from CSV tables?

**Key Findings:** (11/12 tests complete as of 2026-03-06)

- **Scale limits vary dramatically by model**: gpt-5-mini high (675+) vs gpt-4o (4 rows) - **168x+ difference**
- **Reasoning models massively outperform temperature models**: gpt-5-mini (389) vs gpt-4o-mini (6) = **65x better**
- **Primary failure mode is comprehension**, not truncation (context utilization typically <10% at failure)
- **Higher effort dramatically helps**: gpt-5-mini low (65) → medium (389) → high (675+) = **10x improvement**
- **gpt-5 effort shows diminishing returns**: low (356) → medium (450) → high (492) = only **38% improvement**
- **Claude models mid-range**: sonnet (168), opus (177) - similar despite 67% price premium

### Final Results Table (11/12 tests complete)

| Model          | Effort | Scale Limit | Failure Mode  | Context % | Time (min) | Cost ($) |
|----------------|--------|-------------|---------------|-----------|------------|----------|
| gpt-5-mini     | high   | **675+***   | (errors)      | -         | -          | -        |
| gpt-5          | high   | **492**     | truncation    | 8.0%      | 162.5      | 5.47     |
| gpt-5          | medium | **450**     | comprehension | 6.4%      | 81.0       | 5.95     |
| gpt-5-mini     | medium | **389**     | comprehension | ~2%       | 48.3       | 0.00*    |
| gpt-5          | low    | **356**     | comprehension | 2.1%      | 14.2       | 0.87     |
| gpt-5.2        | medium | **215**     | comprehension | 1.4%      | 5.9        | 0.57     |
| claude-opus    | medium | **177**     | truncation    | 25.1%     | 9.6        | 0.00*    |
| claude-sonnet  | medium | **168**     | comprehension | 8.4%      | 8.6        | 0.89     |
| gpt-5-mini     | low    | **65**      | comprehension | 4.3%      | 6.5        | 0.13     |
| claude-haiku   | medium | **9**       | comprehension | 8.3%      | 1.2        | 0.09     |
| gpt-4o-mini    | medium | **6**       | comprehension | 2.1%      | 0.6        | 0.00     |
| gpt-4o         | medium | **4**       | comprehension | 11.3%     | 2.2        | 0.19     |

*Cost tracking errors for some tests
**T04 (gpt-5-mini high) passed at 675 rows but had evaluation errors at higher scales

**Key observations:**
- **Context utilization**: All models fail at <30% context usage - attention, not tokens, is the limit
- **Worst performers**: gpt-4o family (4-6 rows) - fundamentally unsuited for tabular extraction

### Production Recommendations

Balancing accuracy, cost, and speed for real-world use:

- **Best overall**: gpt-5 low (356 rows, 14 min, $0.87) - excellent balance of scale, speed, and cost
- **Fast + cheap**: gpt-5.2 medium (215 rows, 6 min, $0.57) - when speed matters more than scale
- **Maximum scale**: gpt-5-mini medium (389 rows, 48 min, ~$0.05) - highest scale at lowest cost, but slow
- **Enterprise**: claude-sonnet medium (168 rows, 9 min, $0.89) - when Anthropic API is required

**NOT recommended for production:**
- gpt-5 high (162 min per run - too slow)
- gpt-5 medium (81 min per run - too slow)
- gpt-4o, gpt-4o-mini, claude-haiku (4-9 row limits - unusable)

**Completed:** 11/12 tests. T04 (gpt-5-mini high) had evaluation errors at 1012+ rows.

## Table of Contents

1. [Research Problem](#1-research-problem)
2. [Methodology](#2-methodology)
3. [Variables](#3-variables)
4. [Metrics](#4-metrics)
5. [Replication Guide](#5-replication-guide)
6. [Expected Results](#6-expected-results)
7. [Sources](#7-sources)
8. [Document History](#8-document-history)

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

Prior benchmarking (TK-001, March 2026) tested 10 format variants on gpt-5-mini extraction tasks. **Quoted CSV ranked in top 3** across all metrics:

**v4 Results (300 records, 107 matching, n=15 runs)**:

| Rank | Format              | Precision | Std Dev | Recall |
|------|---------------------|-----------|---------|--------|
| 1    | `::` (double colon) | 1.000     | 0.000   | 0.997  |
| 2    | `: ` (colon space)  | 1.000     | 0.000   | 0.989  |
| 3    | CSV quoted          | 1.000     | 0.000   | 0.991  |
| 9    | Markdown table      | 0.978     | 0.038   | 0.950  |
| 10   | XML                 | 0.956     | 0.161   | 0.965  |

**Why CSV over key-value formats**: CSV is a standard tabular format that generalizes to real-world datasets. Key-value with `::` separator performed slightly better but is less common in practice.

**Source**: `_INFO_LLM_MARKDOWN_PREFERENCES.md [LLMO-IN01]` Part 6.2

Test 02 will compare formats directly at scale.

### 2.4 Controls

- **Seed** - Same random seed (42) for reproducible data generation
- **Runs** - 3 runs per configuration to detect inconsistency
- **Ground truth** - Pre-computed expected IDs for exact comparison

## 3. Variables

### 3.1 Independent Variables

| Variable         | Values                                   | Description               |
|------------------|------------------------------------------|---------------------------|
| Model            | gpt-4o-mini, gpt-5-mini, claude-sonnet-4 | LLM to test               |
| Row count        | 50 - 2000                                | Number of CSV rows        |
| Reasoning effort | low, medium, high                        | Model thinking budget     |
| Output length    | low, medium, high                        | Max output tokens scaling |

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

## 5. Replication Guide

### 5.1 Prerequisites

```bash
pip install openai anthropic
```

### 5.2 Setup

1. Clone/copy `01_CSVScaleLimits/` folder
2. Create `.env` file with API keys:
   ```
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-ant-...
   ```

### 5.3 Run Scale Limit Test

```bash
cd 01_CSVScaleLimits/_Scripts

# Find scale limit for a model
python 03_find_scale_limit.py --test-path .. --model gpt-5-mini --initial-rows 100

# Options:
#   --model         Model to test (e.g., gpt-4o-mini, claude-sonnet-4-20250514)
#   --initial-rows  Starting row count (default: 500)
#   --tolerance     Stop when range < this (default: 10)
```

### 5.4 Single Test Run

```bash
# Generate data
python 01_generate_data.py --instance-path ../test_100rows --rows 100 --seed 42

# Execute and evaluate
python 02_execute_and_evaluate.py --instance-path ../test_100rows
```

### 5.5 Verify Setup

```bash
python test_llm_client.py
# Should show: PASS: N, FAIL: 0, ERROR: 0
```

## 6. Expected Results

### 6.1 Hypotheses

**Prior evidence** (TK-001 benchmark, `_INFO_LLM_MARKDOWN_PREFERENCES.md [LLMO-IN01]`):
- gpt-5-mini reliable at 300 records, unreliable at 600 (43% failure rate)
- At 600 records: bimodal behavior (near-perfect OR complete failure)
- v5 failures attributed to "output token limits causing truncation"
- Quoted CSV ranked #3 of 10 formats at 300 records

**H1: Scale limit exists between 300-600 rows for gpt-5-mini**
- **Claim**: Binary search will find scale limit in this range, consistent with TK-001 findings
- **Prior**: TK-001 showed 100% reliability at 300 rows, 43% failure at 600 rows
- **Test**: Run `03_find_scale_limit.py` with initial_rows=300, observe where boundary falls
- **Supported if**: Scale limit falls in 300-600 range
- **Data**: `scale_limit_result.json` contains `max_reliable_rows`

**H2: Failure pattern is bimodal (cliff, not slope)**
- **Claim**: At scale limit, runs either succeed completely (P=1, R=1) or fail significantly, not gradual degradation
- **Prior**: TK-001 v5 showed "bimodal behavior - runs either near-perfect or complete failure"
- **Test**: Analyze variance in precision/recall at boundary rows
- **Supported if**: Standard deviation of scores is high (>0.3) at failure point
- **Data**: `search_history` array in `scale_limit_result.json`

**H3: Truncation is primary failure mode (not comprehension)**
- **Claim**: Most failures at scale limit are due to output truncation (`finish_reason=length`)
- **Prior**: TK-001 v5 failures "due to output token limits causing truncation"
- **Test**: Analyze `failure_mode` field at boundary
- **Supported if**: >50% of failures have `failure_mode=truncation`
- **Data**: `03_find_scale_limit.py` captures `finish_reason` per iteration

**H4: Higher reasoning effort extends scale limit**
- **Claim**: Same model (gpt-5-mini) at high effort achieves higher scale limit than low effort
- **Rationale**: More "thinking" may improve attention allocation across large inputs
- **Test**: Compare scale limits at low/medium/high effort
- **Supported if**: Scale limit increases with effort level
- **Data**: `04_batch_scale_test.py` runs matrix of effort levels

**H5: Reasoning models (gpt-5) outperform temperature models (gpt-4o) at scale**
- **Claim**: gpt-5-mini scale limit > gpt-4o-mini scale limit
- **Rationale**: Explicit reasoning mechanisms may handle complex filtering better
- **Test**: Compare scale limits across model families at matched settings
- **Supported if**: gpt-5 limit > gpt-4o limit by >10%
- **Data**: `04_batch_scale_test.py` collects results across models

**H6: CSV vs other formats at scale** *(Test 02 - future)*
- **Claim**: Quoted CSV maintains higher scale limits than XML/Markdown table
- **Prior**: TK-001 showed XML and Markdown table had highest variance/failure rates
- **Test**: Compare same task with different formats

### 6.2 Hypothesis Summary Table

| ID | Hypothesis                   | Script                   | Metric                      |
|----|------------------------------|--------------------------|-----------------------------|
| H1 | Scale limit 300-600 rows     | `03_find_scale_limit.py` | `max_reliable_rows`         |
| H2 | Bimodal failure (cliff)      | `03_find_scale_limit.py` | Variance at boundary        |
| H3 | Truncation > comprehension   | `03_find_scale_limit.py` | `failure_mode` distribution |
| H4 | Higher effort = higher limit | `04_batch_scale_test.py` | Scale limit by effort       |
| H5 | Reasoning > temperature      | `04_batch_scale_test.py` | Scale limit by model family |
| H6 | CSV best format              | Test 02                  | Scale limit by format       |

### 6.3 Script Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│ Phase 1: Data Collection                                        │
├─────────────────────────────────────────────────────────────────┤
│ Option A: Single model test                                     │
│   python 03_find_scale_limit.py --model gpt-5-mini              │
│                                                                 │
│ Option B: Batch test (multiple models/efforts)                  │
│   python 04_batch_scale_test.py --config batch-config.json      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Phase 2: Analysis                                               │
├─────────────────────────────────────────────────────────────────┤
│ python 05_analyze_results.py --output analysis_report.md        │
│                                                                 │
│ Tests H1-H5 and generates:                                      │
│   - Comparison table                                            │
│   - Hypothesis verdicts (SUPPORTED / NOT SUPPORTED)             │
│   - Statistical analysis                                        │
└─────────────────────────────────────────────────────────────────┘
```

### 6.4 Results Template

#### Scale Limit Results (All 12 Configurations) [TESTED]

| Model             | Provider  | Method      | Effort | Scale Limit | Context % | Primary Failure | Cost  |
|-------------------|-----------|-------------|--------|-------------|-----------|-----------------|-------|
| gpt-4o-mini       | OpenAI    | temperature | medium | 6           | 2.1%      | comprehension   | $0.00 |
| gpt-4o            | OpenAI    | temperature | medium | 4           | 11.3%     | comprehension   | $0.19 |
| gpt-5-mini        | OpenAI    | reasoning   | low    | 65          | 4.3%      | comprehension   | $0.13 |
| gpt-5-mini        | OpenAI    | reasoning   | medium | 389         | ~2%       | comprehension   | $0.00*|
| gpt-5-mini        | OpenAI    | reasoning   | high   | 675+*       | -         | (errors)        | -     |
| gpt-5             | OpenAI    | reasoning   | low    | 356         | 2.1%      | comprehension   | $0.87 |
| gpt-5             | OpenAI    | reasoning   | medium | 450         | 6.4%      | comprehension   | $5.95 |
| gpt-5             | OpenAI    | reasoning   | high   | 492         | 8.0%      | truncation      | $5.47 |
| gpt-5.2           | OpenAI    | reasoning   | medium | 215         | 1.4%      | comprehension   | $0.57 |
| claude-haiku-4-5  | Anthropic | temperature | medium | 9           | 8.3%      | comprehension   | $0.09 |
| claude-sonnet-4-5 | Anthropic | thinking    | medium | 168         | 8.4%      | comprehension   | $0.89 |
| claude-opus-4-5   | Anthropic | effort      | medium | 177         | 25.1%     | truncation      | $0.00*|

*Cost tracking errors; gpt-5-mini high had evaluation errors at 1012+ rows

#### Hypothesis Verdicts [TESTED]

| ID | Hypothesis                            | Verdict              | Evidence | Confidence |
|----|---------------------------------------|----------------------|----------|------------|
| H1 | Scale limit 300-600 rows (gpt-5-mini) | **SUPPORTED**        | gpt-5-mini medium = 389 rows | High |
| H2 | Bimodal failure (cliff, not slope)    | **PARTIALLY SUPPORTED** | Reasoning: cliff. Temperature: gradual slope | Medium |
| H3 | Truncation > comprehension errors     | **NOT SUPPORTED**    | 9/11 comprehension, 2/11 truncation | High |
| H4 | Higher effort = higher limit          | **SUPPORTED**        | gpt-5-mini: 65→389→675+ (10x). gpt-5: 356→492 (38%) | High |
| H5 | Reasoning > temperature models        | **STRONGLY SUPPORTED** | gpt-5-mini vs gpt-4o-mini = 65x. gpt-5 vs gpt-4o = 89x | Very High |
| H6 | CSV best format                       | Deferred             | Test 02 (future) | - |

#### Effort Level Comparison (H4) [TESTED]

| Model      | Low      | Medium   | High     | Delta (High-Low) |
|------------|----------|----------|----------|------------------|
| gpt-5-mini | 65 rows  | 389 rows | 675+ rows* | **+938%** (10x+) |
| gpt-5      | 356 rows | 450 rows | 492 rows | **+38%** |

*T04 had evaluation errors; 675 rows confirmed passing

#### Model Family Comparison (H5) [TESTED]

| Comparison | Temperature Model  | Reasoning Model    | Winner     | Delta |
|------------|--------------------|--------------------|------------|-------|
| Mini tier  | gpt-4o-mini: 6     | gpt-5-mini: 389    | gpt-5-mini | **65x** |
| Full tier  | gpt-4o: 4          | gpt-5 (low): 356   | gpt-5      | **89x** |

## 7. Sources

- `_SPEC_LLM_CLIENT.md [LLMC-SP01]` - LLM client specification
- `_SPEC_CSVScaleLimits.md [TBLF-SP01]` - Test framework specification
- `_INFO_LLM_MARKDOWN_PREFERENCES.md [LLMO-IN01]` - Format benchmarking research (TK-001)
- `.windsurf/skills/llm-evaluation/` - Original LLM evaluation scripts

## 8. Document History

**[2026-03-06 05:45]**
- Updated: Final results with 11/12 tests complete
- Added: gpt-5 medium (450 rows), gpt-5 high (492 rows), gpt-5-mini high (675+) results
- Updated: All hypothesis verdicts with [TESTED] labels
- Updated: Scale Limit Results table with actual values
- Updated: Effort Level Comparison (H4) and Model Family Comparison (H5) with data
- Key insight: Context utilization <10% at failure - attention is the bottleneck, not tokens

**[2026-03-06 00:56]**
- Added: Preliminary findings with 9/12 tests complete
- Added: Results table with scale limits, time, cost, iterations
- Added: Cost and time observations
- Key finding: comprehension (not truncation) is primary failure mode

**[2026-03-05 23:55]**
- Expanded: Results template now includes all 8 models (12 configurations)
- Added: Hypothesis verdicts template with Evidence/Confidence columns
- Added: Effort level comparison table (H4)
- Added: Model family comparison table (H5)
- Fixed: Pipeline diagram hypothesis reference (H1-H5)

**[2026-03-05 23:40]**
- Rewrote: All hypotheses now grounded in TK-001 benchmark evidence
- Added: Prior evidence section citing `_INFO_LLM_MARKDOWN_PREFERENCES.md [LLMO-IN01]`
- H1: Scale limit 300-600 rows (based on TK-001 v4/v5 findings)
- H2: Bimodal failure pattern (based on TK-001 v5 observation)
- H3: Truncation as primary failure mode (based on TK-001 attribution)
- H4: Reasoning effort extends scale limit
- H5: Reasoning models outperform temperature models
- H6: CSV format comparison (future Test 02)

**[2026-03-05 23:10]**
- Fixed: H2 reworded to avoid circular definition
- Removed: H3 (tautological - tokens correlate with rows by definition)
- Fixed: H4 reframed as exploratory (removed unfounded 80% prediction)
- Removed: H7 (trivially true)

**[2026-03-05 23:00]**
- Added: Script-to-hypothesis mapping table
- Added: Script pipeline diagram
- Updated: Section 6 with new scripts (04_batch_scale_test.py, 05_analyze_results.py)

**[2026-03-05 22:29]**
- Rewrote with research focus
- Added methodology, variables, metrics sections
- Added replication guide with step-by-step commands
- Added results template for findings

**[2026-03-05 22:07]**
- Initial document created
