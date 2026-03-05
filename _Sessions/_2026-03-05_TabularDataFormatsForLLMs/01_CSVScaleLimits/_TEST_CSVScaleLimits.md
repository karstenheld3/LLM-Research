<DevSystem MarkdownTablesAllowed=true />

# TEST: CSV Scale Limits

**Doc ID**: TBLF-TP01
**Goal**: Efficiently test 6 hypotheses across 8 models to find scale limits for LLM tabular extraction
**Timeline**: Created 2026-03-05, 1 update, date range 2026-03-05
**Target file**: `04_batch_scale_test.py`, `05_analyze_results.py`

**Depends on:**
- `_INFO_CSVScaleLimits.md [TBLF-IN01]` for hypotheses and prior evidence
- `_SPEC_CSVScaleLimits.md [TBLF-SP01]` for test framework specification

## MUST-NOT-FORGET

- Run cheapest models first to validate setup before expensive runs
- gpt-5-mini is baseline (TK-001 prior data exists)
- Each model run costs real money - validate setup with dry-run first
- Binary search is efficient (~10 iterations vs 100+ linear)
- Capture all metrics even if hypothesis only needs subset

## Caveats and Limitations

- **Result variance**: Binary search results have ~10% margin due to LLM non-determinism. Use `--verify-runs 3` to increase confidence.
- **Cost estimates**: Estimates assume 300-row baseline. Actual costs may be 2x higher if models scale to 600+ rows.
- **H5 confounding**: H5 compares gpt-4o (temperature) vs gpt-5 (reasoning), but these are different architectures. Results show "newer reasoning models perform better" rather than isolating the reasoning mechanism.

## Table of Contents

1. [Overview](#1-overview)
2. [Test Models](#2-test-models)
3. [Hypothesis Testing Strategy](#3-hypothesis-testing-strategy)
4. [Test Execution Order](#4-test-execution-order)
5. [Test Configurations](#5-test-configurations)
6. [Estimated Costs](#6-estimated-costs)
7. [Test Phases](#7-test-phases)
8. [Replication Guide](#8-replication-guide)
9. [Verification Checklist](#9-verification-checklist)
10. [Document History](#10-document-history)

## 1. Overview

This test plan validates 6 hypotheses about LLM scale limits for tabular data extraction:

| ID | Hypothesis | Models Required | Effort Levels |
|----|------------|-----------------|---------------|
| H1 | Scale limit 300-600 rows | gpt-5-mini (baseline) | medium |
| H2 | Bimodal failure pattern | All models | medium |
| H3 | Truncation > comprehension | All models | medium |
| H4 | Higher effort = higher limit | gpt-5-mini, gpt-5 | low, medium, high |
| H5 | Reasoning > temperature | gpt-4o vs gpt-5, gpt-4o-mini vs gpt-5-mini | medium |
| H6 | CSV best format | (Test 02 - future) | - |

**Key insight**: H2 and H3 data is captured during H1 runs - no separate tests needed.

## 2. Test Models

### 2.1 Model List (Ordered by Cost)

| Tier | Model ID | Provider | Method | Cost (in/out per 1M) | Priority |
|------|----------|----------|--------|----------------------|----------|
| 1 | gpt-4o-mini | OpenAI | temperature | $0.15 / $0.60 | Setup validation |
| 2 | gpt-5-mini | OpenAI | reasoning_effort | $0.25 / $2.00 | **Baseline** (TK-001) |
| 3 | claude-haiku-4-5-20251001 | Anthropic | temperature | $1.00 / $5.00 | Cheapest Anthropic |
| 4 | gpt-5 | OpenAI | reasoning_effort | $1.25 / $10.00 | Full-size reasoning |
| 5 | gpt-5.2 | OpenAI | reasoning_effort | $1.75 / $14.00 | Latest OpenAI |
| 6 | gpt-4o | OpenAI | temperature | $2.50 / $10.00 | Temperature baseline |
| 7 | claude-sonnet-4-5-20250929 | Anthropic | thinking | $3.00 / $15.00 | Mid Anthropic |
| 8 | claude-opus-4-5-20251101 | Anthropic | effort | $5.00 / $25.00 | Top Anthropic |

### 2.2 Model Groupings for Hypothesis Testing

**H4 (Effort levels)** - Test on 2 models:
- gpt-5-mini: low, medium, high
- gpt-5: low, medium, high

**H5 (Reasoning vs Temperature)** - Paired comparisons:
- gpt-4o-mini (temp) vs gpt-5-mini (reasoning) - mini tier
- gpt-4o (temp) vs gpt-5 (reasoning) - full tier

## 3. Hypothesis Testing Strategy

### 3.1 Data Collection Efficiency

```
┌─────────────────────────────────────────────────────────────────┐
│ Single binary search run collects data for H1, H2, H3           │
├─────────────────────────────────────────────────────────────────┤
│ Output: scale_limit_result.json contains:                       │
│   - max_reliable_rows (H1)                                      │
│   - search_history with precision/recall variance (H2)          │
│   - failure_mode per iteration (H3)                             │
│   - context_utilization_at_failure_pct                          │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Test Matrix

| Test ID | Model | Effort | Hypotheses Tested | Est. Iterations |
|---------|-------|--------|-------------------|-----------------|
| T01 | gpt-4o-mini | medium | Setup validation | ~10 |
| T02 | gpt-5-mini | medium | H1, H2, H3 (baseline) | ~10 |
| T03 | gpt-5-mini | low | H4 | ~10 |
| T04 | gpt-5-mini | high | H4 | ~10 |
| T05 | gpt-5 | medium | H2, H3, H5 | ~10 |
| T06 | gpt-5 | low | H4 | ~10 |
| T07 | gpt-5 | high | H4 | ~10 |
| T08 | gpt-4o | medium | H2, H3, H5 | ~10 |
| T09 | gpt-5.2 | medium | H2, H3 | ~10 |
| T10 | claude-haiku-4-5-20251001 | medium | H2, H3 | ~10 |
| T11 | claude-sonnet-4-5-20250929 | medium | H2, H3 | ~10 |
| T12 | claude-opus-4-5-20251101 | medium | H2, H3 | ~10 |

**Total: 12 test runs, ~120 iterations**

## 4. Test Execution Order

### 4.1 Phase 1: Setup Validation (1 run)

**Goal**: Verify scripts work before spending money on expensive models

```bash
# Dry run with cheapest model, small scale
python 03_find_scale_limit.py \
  --test-path .. \
  --model gpt-4o-mini \
  --initial-rows 50 \
  --tolerance 20
```

**Pass criteria**: 
- Script completes without error
- Results file created
- At least one PASS and one FAIL observed

### 4.2 Phase 2: Baseline (H1, H2, H3) - 1 run

**Goal**: Establish gpt-5-mini baseline, validate against TK-001 prior data

```bash
python 03_find_scale_limit.py \
  --test-path .. \
  --model gpt-5-mini \
  --initial-rows 300 \
  --tolerance 10 \
  --verify-runs 3
```

**Expected**: Scale limit in 300-600 range (per TK-001)

### 4.3 Phase 3: Effort Level Testing (H4) - 5 runs

**Goal**: Test if higher effort = higher scale limit

```bash
# gpt-5-mini at low effort
python 03_find_scale_limit.py --test-path .. --model gpt-5-mini \
  --initial-rows 300 --tolerance 10 --reasoning-effort low

# gpt-5-mini at high effort  
python 03_find_scale_limit.py --test-path .. --model gpt-5-mini \
  --initial-rows 300 --tolerance 10 --reasoning-effort high

# gpt-5 at low, medium, high (3 runs)
# ... same pattern
```

### 4.4 Phase 4: Cross-Model Comparison (H5) - 2 runs

**Goal**: Compare reasoning vs temperature models

```bash
# gpt-4o (temperature model)
python 03_find_scale_limit.py --test-path .. --model gpt-4o \
  --initial-rows 300 --tolerance 10

# Compare with gpt-5 from Phase 3
```

### 4.5 Phase 5: Remaining Models - 4 runs

**Goal**: Complete coverage of all requested models

```bash
# Run in cost order (cheapest first)
python 03_find_scale_limit.py --test-path .. --model gpt-5.2 ...
python 03_find_scale_limit.py --test-path .. --model claude-haiku-4-5-20251001 ...
python 03_find_scale_limit.py --test-path .. --model claude-sonnet-4-5-20250929 ...
python 03_find_scale_limit.py --test-path .. --model claude-opus-4-5-20251101 ...
```

### 4.6 Phase 6: Analysis

```bash
python 05_analyze_results.py --test-path .. --output analysis_report.md
```

### 4.7 Parallel Execution (All 12 Tests Simultaneously)

Tested worker limits allow running all tests in parallel:
- **OpenAI**: 120+ concurrent workers tested
- **Anthropic**: 60+ concurrent workers tested

Source: `.windsurf/skills/llm-evaluation/LLM_EVALUATION_TESTED_MODELS.md`

**Run in 12 separate terminals:**

```
cd E:\Dev\LLM-Research\_Sessions\_2026-03-05_TabularDataFormatsForLLMs\01_CSVScaleLimits\_Scripts

# Terminal 1 (T01)
python 03_find_scale_limit.py --test-path .. --model gpt-4o-mini --initial-rows 50 --tolerance 20

# Terminal 2 (T02) - baseline
python 03_find_scale_limit.py --test-path .. --model gpt-5-mini --initial-rows 300 --tolerance 10 --verify-runs 3

# Terminal 3 (T03)
python 03_find_scale_limit.py --test-path .. --model gpt-5-mini --initial-rows 300 --tolerance 10 --reasoning-effort low

# Terminal 4 (T04)
python 03_find_scale_limit.py --test-path .. --model gpt-5-mini --initial-rows 300 --tolerance 10 --reasoning-effort high

# Terminal 5 (T05)
python 03_find_scale_limit.py --test-path .. --model gpt-5 --initial-rows 300 --tolerance 10

# Terminal 6 (T06)
python 03_find_scale_limit.py --test-path .. --model gpt-5 --initial-rows 300 --tolerance 10 --reasoning-effort low

# Terminal 7 (T07)
python 03_find_scale_limit.py --test-path .. --model gpt-5 --initial-rows 300 --tolerance 10 --reasoning-effort high

# Terminal 8 (T08)
python 03_find_scale_limit.py --test-path .. --model gpt-4o --initial-rows 300 --tolerance 10

# Terminal 9 (T09)
python 03_find_scale_limit.py --test-path .. --model gpt-5.2 --initial-rows 300 --tolerance 10

# Terminal 10 (T10)
python 03_find_scale_limit.py --test-path .. --model claude-haiku-4-5-20251001 --initial-rows 300 --tolerance 10

# Terminal 11 (T11)
python 03_find_scale_limit.py --test-path .. --model claude-sonnet-4-5-20250929 --initial-rows 300 --tolerance 10

# Terminal 12 (T12)
python 03_find_scale_limit.py --test-path .. --model claude-opus-4-5-20251101 --initial-rows 300 --tolerance 10
```

**Total time: ~15-20 minutes** (single test duration) vs ~3 hours sequential

## 5. Test Configurations

### 5.1 batch-config.json for Full Run

```json
{
  "test_path": "..",
  "initial_rows": 300,
  "tolerance": 10,
  "verify_runs": 3,
  "configurations": [
    {"model": "gpt-4o-mini", "effort": "medium"},
    {"model": "gpt-5-mini", "effort": "low"},
    {"model": "gpt-5-mini", "effort": "medium"},
    {"model": "gpt-5-mini", "effort": "high"},
    {"model": "gpt-5", "effort": "low"},
    {"model": "gpt-5", "effort": "medium"},
    {"model": "gpt-5", "effort": "high"},
    {"model": "gpt-5.2", "effort": "medium"},
    {"model": "gpt-4o", "effort": "medium"},
    {"model": "claude-haiku-4-5-20251001", "effort": "medium"},
    {"model": "claude-sonnet-4-5-20250929", "effort": "medium"},
    {"model": "claude-opus-4-5-20251101", "effort": "medium"}
  ]
}
```

### 5.2 Minimal Config (Budget-Conscious)

For quick validation of core hypotheses:

```json
{
  "configurations": [
    {"model": "gpt-4o-mini", "effort": "medium"},
    {"model": "gpt-5-mini", "effort": "low"},
    {"model": "gpt-5-mini", "effort": "medium"},
    {"model": "gpt-5-mini", "effort": "high"},
    {"model": "gpt-4o", "effort": "medium"}
  ]
}
```

## 6. Estimated Costs

### 6.1 Per-Run Cost Estimate

Assumptions:
- ~10 iterations per run
- ~5000 input tokens per iteration (300 rows * ~15 tokens/row + prompt overhead)
- ~2000 output tokens per iteration
- Total per run: ~50K input, ~20K output

| Model | Input Cost | Output Cost | Per Run |
|-------|------------|-------------|---------|
| gpt-4o-mini | $0.008 | $0.012 | **$0.02** |
| gpt-5-mini | $0.013 | $0.040 | **$0.05** |
| claude-haiku-4-5 | $0.050 | $0.100 | **$0.15** |
| gpt-5 | $0.063 | $0.200 | **$0.26** |
| gpt-5.2 | $0.088 | $0.280 | **$0.37** |
| gpt-4o | $0.125 | $0.200 | **$0.33** |
| claude-sonnet-4-5 | $0.150 | $0.300 | **$0.45** |
| claude-opus-4-5 | $0.250 | $0.500 | **$0.75** |

### 6.2 Total Cost Estimate

| Phase | Runs | Est. Cost |
|-------|------|-----------|
| 1. Setup validation | 1 | $0.02 |
| 2. Baseline (gpt-5-mini) | 1 | $0.05 |
| 3. Effort testing (6 runs) | 6 | $0.60 |
| 4. Cross-model (2 runs) | 2 | $0.60 |
| 5. Remaining models (4 runs) | 4 | $1.70 |
| **Total** | **14** | **~$3.00** |

Note: Actual costs may vary based on scale limits found.

## 7. Test Phases

### Phase 1: Setup Validation
- **Duration**: 5-10 minutes
- **Cost**: ~$0.02
- **Gate**: Must complete successfully before Phase 2

### Phase 2: Baseline
- **Duration**: 15-20 minutes
- **Cost**: ~$0.05
- **Gate**: Scale limit must fall in expected 300-600 range

### Phase 3: Effort Testing
- **Duration**: 60-90 minutes
- **Cost**: ~$0.60
- **Gate**: Data collected for all effort levels

### Phase 4: Cross-Model
- **Duration**: 30-45 minutes
- **Cost**: ~$0.60
- **Gate**: gpt-4o and gpt-5 both complete

### Phase 5: Full Coverage
- **Duration**: 60-90 minutes
- **Cost**: ~$1.70
- **Gate**: All 8 models tested

### Phase 6: Analysis
- **Duration**: 5 minutes
- **Cost**: $0
- **Output**: `analysis_report.md` with hypothesis verdicts

## 8. Replication Guide

### 8.1 Prerequisites

```bash
pip install openai anthropic
```

### 8.2 API Keys

Create `.env` file in `01_CSVScaleLimits/`:

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### 8.3 Verify Setup

```bash
cd 01_CSVScaleLimits/_Scripts
python test_llm_client.py
# Expected: All models show PASS
```

### 8.4 Run Full Test Suite

**Option A: Batch (recommended)**

```bash
python 04_batch_scale_test.py --config ../batch-config.json
```

**Option B: Manual (phase by phase)**

```bash
# Phase 1: Validate
python 03_find_scale_limit.py --test-path .. --model gpt-4o-mini --initial-rows 50 --tolerance 20

# Phase 2: Baseline
python 03_find_scale_limit.py --test-path .. --model gpt-5-mini --initial-rows 300 --tolerance 10

# Continue with remaining phases...
```

### 8.5 Analyze Results

```bash
python 05_analyze_results.py --test-path .. --output ../analysis_report.md
```

### 8.6 Expected Output Files

```
01_CSVScaleLimits/
├── gpt-4o-mini_temperature_medium_max16384/
│   └── scale_limit_result.json
├── gpt-5-mini_reasoning_effort_low_max32768/
│   └── scale_limit_result.json
├── gpt-5-mini_reasoning_effort_medium_max32768/
│   └── scale_limit_result.json
├── ... (one folder per configuration)
└── analysis_report.md
```

## 9. Verification Checklist

### Pre-Test
- [ ] API keys configured in `.env`
- [ ] `test_llm_client.py` passes for all target models
- [ ] `batch-config.json` created with correct model IDs

### Phase 1
- [ ] T01 (gpt-4o-mini) completes without error
- [ ] Results folder and JSON created

### Phase 2
- [ ] T02 (gpt-5-mini baseline) completes
- [ ] Scale limit in 300-600 range (validates H1)

### Phase 3
- [ ] T03, T04 (gpt-5-mini low/high) complete
- [ ] T05, T06, T07 (gpt-5 all efforts) complete

### Phase 4
- [ ] T08 (gpt-4o) completes
- [ ] H5 data available (reasoning vs temperature)

### Phase 5
- [ ] T09-T12 (remaining models) complete
- [ ] All 8 requested models have results

### Phase 6
- [ ] `05_analyze_results.py` runs successfully
- [ ] `analysis_report.md` generated
- [ ] All hypotheses have verdicts

### Post-Test
- [ ] Results committed to repository
- [ ] Cost tracking matches estimates (within 2x)

## 10. Document History

**[2026-03-06 00:08]**
- Added: Section 4.7 Parallel Execution with all 12 terminal commands
- Based on tested worker limits (120+ OpenAI, 60+ Anthropic)
- Total time: ~15-20 min vs ~3 hours sequential

**[2026-03-06 00:00]**
- Added: Caveats and Limitations section (variance, cost, H5 confounding)
- Source: /reconcile review findings

**[2026-03-05 23:58]**
- Fixed: Timeline field format
- Fixed: Phase 3 run count (4 -> 5)

**[2026-03-05 23:50]**
- Initial test plan created
- 8 models, 6 hypotheses, 12 test configurations
- Estimated cost: ~$3.00
- Phased execution for efficient validation
