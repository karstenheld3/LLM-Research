# LLM Tabular Data Extraction: Scale Limits Research

Research on maximum reliable row counts for LLM tabular data extraction across models.

## Research Summary

**Question:** At what scale do LLMs fail to reliably extract filtered data from CSV tables?

**Status:** 11/12 tests complete (March 2026)

## Hypothesis Results

### H1: Scale Limit 300-600 Rows

| | |
|---|---|
| **Status** | ✅ SUPPORTED |
| **Hypothesis** | gpt-5-mini can reliably process 300-600 CSV rows for extraction tasks |
| **Source** | TK-001 benchmark showing 100% reliability at 300 rows, 43% failure at 600 rows |
| **Reasoning** | Binary search found exact boundary at 389 rows - within predicted range |
| **Data** | gpt-5-mini medium: 389 rows (Precision=1.00, Recall=1.00 at 378 rows, failed at 395) |

### H2: Bimodal Failure Pattern (Cliff, Not Slope)

| | |
|---|---|
| **Status** | ⚠️ PARTIALLY SUPPORTED |
| **Hypothesis** | At scale limit, models either succeed completely or fail significantly (cliff behavior) |
| **Source** | TK-001 v5 observation of sudden accuracy drops |
| **Reasoning** | Behavior differs by model type - reasoning models show cliff, temperature models show slope |
| **Data** | gpt-5-mini: 100%→0% within 17 rows. gpt-4o: gradual degradation (P=0.89→0.47 over range) |

### H3: Truncation > Comprehension Errors

| | |
|---|---|
| **Status** | ❌ NOT SUPPORTED |
| **Hypothesis** | Output truncation is the primary failure mode at scale |
| **Source** | TK-001 attribution to output length limits |
| **Reasoning** | Comprehension failures dominate; context utilization <10% at failure proves attention is the bottleneck |
| **Data** | 9/11 tests failed due to comprehension, 2/11 truncation. Average context usage at failure: 6.5% |

### H4: Higher Effort = Higher Scale Limit

| | |
|---|---|
| **Status** | ✅ SUPPORTED |
| **Hypothesis** | Higher reasoning effort extends the scale limit |
| **Source** | Hypothesis based on reasoning model architecture |
| **Reasoning** | Dramatic improvement for gpt-5-mini (10x), diminishing returns for gpt-5 (38%) |
| **Data** | gpt-5-mini: low=65, medium=389, high=675+ (+938%). gpt-5: low=356, medium=450, high=492 (+38%) |

### H5: Reasoning Models > Temperature Models

| | |
|---|---|
| **Status** | ✅ STRONGLY SUPPORTED |
| **Hypothesis** | Reasoning models (gpt-5) outperform temperature models (gpt-4o) for tabular extraction |
| **Source** | Architectural differences between model families |
| **Reasoning** | Massive performance gap makes temperature models unsuitable for tabular extraction |
| **Data** | Mini tier: gpt-5-mini (389) vs gpt-4o-mini (6) = **65x better**. Full tier: gpt-5 (356) vs gpt-4o (4) = **89x better** |

### H6: CSV Best Format

| | |
|---|---|
| **Status** | ⏳ DEFERRED |
| **Hypothesis** | Quoted CSV is optimal format for LLM tabular extraction at scale |
| **Source** | TK-001 format benchmarks (CSV ranked #3 of 10 formats) |
| **Reasoning** | Test 02 will compare formats directly at scale limits |
| **Data** | Pending future test |

## Key Findings

| Finding | Impact |
|---------|--------|
| Reasoning models massively outperform temperature | 65-89x better scale limits |
| Higher effort dramatically increases limit | Up to 10x improvement |
| Comprehension is primary failure mode | Context window is NOT the bottleneck |
| Scale limits vary 168x across models | Best: 675+ rows, Worst: 4 rows |

## Production Recommendations

| Priority | Model | Effort | Safe Scale | Cost |
|----------|-------|--------|------------|------|
| Quality | gpt-5 | high | 400 rows | ~$5.50 |
| Balanced | gpt-5 | low | 300 rows | ~$0.90 |
| Budget | gpt-5-mini | medium | 300 rows | ~$0.05 |

**DO NOT USE:** gpt-4o, gpt-4o-mini, claude-haiku (4-9 row limits)

## Source Documents

- [`_INFO_CSVScaleLimits.md`](_Sessions/_2026-03-05_TabularDataFormatsForLLMs/01_CSVScaleLimits/_INFO_CSVScaleLimits.md) - Full research documentation
- [`_TEST_CSVScaleLimits.md`](_Sessions/_2026-03-05_TabularDataFormatsForLLMs/01_CSVScaleLimits/_TEST_CSVScaleLimits.md) - Test plan and detailed analysis
- TK-001: Prior format benchmarking (March 2026)
