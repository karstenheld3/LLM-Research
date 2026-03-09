# LLM Tabular Data Extraction: Scale Limits Research

Research on maximum reliable row counts for LLM tabular data extraction across models.

## Research Summary

**Question:** At what scale do LLMs fail to reliably extract filtered data from CSV tables?

**Status:** 11/12 tests complete (March 2026)

## Key Findings

- **Reasoning models massively outperform temperature models** (65-89x better scale limits)
  - gpt-5-mini extracts 389 rows reliably vs gpt-4o-mini at only 6 rows
  - Reasoning architecture enables systematic data processing that temperature sampling cannot achieve

- **Higher reasoning effort dramatically increases scale limit** (up to 10x improvement)
  - gpt-5-mini: low=65 → medium=389 → high=675+ rows
  - Diminishing returns for larger models: gpt-5 shows only 38% improvement across effort levels

- **Comprehension is the primary failure mode, not truncation**
  - 9/11 tests failed due to comprehension errors (attention degradation)
  - Average context utilization at failure: only 6.5% - context window is NOT the bottleneck

- **Scale limits vary 168x across models**
  - Best: gpt-5-mini high (675+ rows)
  - Worst: gpt-4o (4 rows)
  - This variance makes model selection critical for production use

## Production Recommendations

| Priority | Model | Effort | Safe Scale | Cost |
|----------|-------|--------|------------|------|
| Quality | gpt-5 | high | 400 rows | ~$5.50 |
| Balanced | gpt-5 | low | 300 rows | ~$0.90 |
| Budget | gpt-5-mini | medium | 300 rows | ~$0.05 |

**DO NOT USE:** gpt-4o, gpt-4o-mini, claude-haiku (4-9 row limits)

## Hypothesis Sources

Hypotheses derive from two sources:

1. **TK-001 Internal Benchmark** (March 2026) - Prior format comparison testing 10 variants on gpt-5-mini extraction tasks. Documented in `_INFO_LLM_MARKDOWN_PREFERENCES.md [LLMO-IN01]`.

2. **Academic Literature** - Theoretical foundations from peer-reviewed research:
   - [Chain-of-Thought Prompting](https://arxiv.org/abs/2201.11903) (Wei et al., NeurIPS 2022) - Reasoning improves complex tasks
   - [LIFBench](https://arxiv.org/abs/2411.07037) (Wu et al., 2024) - Long-context instruction following degrades at scale
   - [Does Prompt Formatting Impact LLM?](https://arxiv.org/abs/2411.10541) (He et al., Microsoft/MIT 2024) - Format affects performance up to 40%
   - [CFPO](https://arxiv.org/abs/2502.04295) (Liu et al., Microsoft Research 2025) - Content-format integration

## Hypothesis Results

### H1: Scale Limit 300-600 Rows

| | |
|---|---|
| **Status** | ✅ SUPPORTED |
| **Hypothesis** | gpt-5-mini can reliably process 300-600 CSV rows for extraction tasks |
| **Source** | TK-001 v4/v5: 100% reliability at 300 rows, 43% failure at 600 rows ([LLMO-IN01] §6.2) |
| **Reasoning** | Binary search found exact boundary at 389 rows - within predicted range |
| **Data** | gpt-5-mini medium: 389 rows (Precision=1.00, Recall=1.00 at 378 rows, failed at 395) |

### H2: Bimodal Failure Pattern (Cliff, Not Slope)

| | |
|---|---|
| **Status** | ⚠️ PARTIALLY SUPPORTED |
| **Hypothesis** | At scale limit, models either succeed completely or fail significantly (cliff behavior) |
| **Source** | TK-001 v5: bimodal behavior at 600 rows ([LLMO-IN01] §6.2) |
| **Reasoning** | Behavior differs by model type - reasoning models show cliff, temperature models show slope |
| **Data** | gpt-5-mini: 100%→0% within 17 rows. gpt-4o: gradual degradation (P=0.89→0.47 over range) |

### H3: Truncation > Comprehension Errors

| | |
|---|---|
| **Status** | ❌ NOT SUPPORTED |
| **Hypothesis** | Output truncation is the primary failure mode at scale |
| **Source** | TK-001 attribution (later disproved); [LIFBench](https://arxiv.org/abs/2411.07037) context degradation theory |
| **Reasoning** | Comprehension failures dominate; context utilization <10% at failure proves attention is the bottleneck |
| **Data** | 9/11 tests failed due to comprehension, 2/11 truncation. Average context usage at failure: 6.5% |

### H4: Higher Effort = Higher Scale Limit

| | |
|---|---|
| **Status** | ✅ SUPPORTED |
| **Hypothesis** | Higher reasoning effort extends the scale limit |
| **Source** | [Chain-of-Thought](https://arxiv.org/abs/2201.11903) reasoning theory; model architecture hypothesis |
| **Reasoning** | Dramatic improvement for gpt-5-mini (10x), diminishing returns for gpt-5 (38%) |
| **Data** | gpt-5-mini: low=65, medium=389, high=675+ (+938%). gpt-5: low=356, medium=450, high=492 (+38%) |

### H5: Reasoning Models > Temperature Models

| | |
|---|---|
| **Status** | ✅ STRONGLY SUPPORTED |
| **Hypothesis** | Reasoning models (gpt-5) outperform temperature models (gpt-4o) for tabular extraction |
| **Source** | [CoT Prompting](https://arxiv.org/abs/2201.11903) + [Zero-shot CoT](https://arxiv.org/abs/2205.11916) reasoning emergence |
| **Reasoning** | Massive performance gap makes temperature models unsuitable for tabular extraction |
| **Data** | Mini tier: gpt-5-mini (389) vs gpt-4o-mini (6) = **65x better**. Full tier: gpt-5 (356) vs gpt-4o (4) = **89x better** |

### H6: CSV Best Format

| | |
|---|---|
| **Status** | ⏳ DEFERRED |
| **Hypothesis** | Quoted CSV is optimal format for LLM tabular extraction at scale |
| **Source** | TK-001 format benchmarks ([LLMO-IN01] §6.2); [CFPO](https://arxiv.org/abs/2502.04295) format impact theory |
| **Reasoning** | Test 02 will compare formats directly at scale limits |
| **Data** | Pending future test |

## Source Documents

- [`_INFO_CSVScaleLimits.md`](_Sessions/_2026-03-05_TabularDataFormatsForLLMs/01_CSVScaleLimits/_INFO_CSVScaleLimits.md) - Full research documentation
- [`_TEST_CSVScaleLimits.md`](_Sessions/_2026-03-05_TabularDataFormatsForLLMs/01_CSVScaleLimits/_TEST_CSVScaleLimits.md) - Test plan and detailed analysis
- TK-001: Prior format benchmarking (March 2026)
