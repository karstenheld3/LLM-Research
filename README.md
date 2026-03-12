<DevSystem MarkdownTablesAllowed=true />

# LLM Tabular Data Extraction: Scale Limits Research

Research on maximum reliable row counts for LLM tabular data extraction across models.

## Research Summary

**Questions:**
1. What are the maximum reliable row counts for LLM filtered extraction from CSV tables? (Test 01)
2. Does input format affect LLM extraction scale limits? (Test 02)

*Extraction accuracy at scale serves as a practical proxy for tabular data comprehension capacity - models that can reliably extract filtered records demonstrate working comprehension of the underlying data.*

**Status:** Test 01: 12/12 complete | Test 02: 40/40 complete (March 2026)

## Key Findings

- **Reasoning models massively outperform temperature models** (83-89x better scale limits)
  - gpt-5-mini reliably extracts 150 matching records from 500 rows vs gpt-4o-mini failing at 6 rows (2 matches)
  - Reasoning architecture enables systematic data processing that temperature sampling cannot achieve

- **Higher reasoning effort dramatically increases scale limit** (up to 10x improvement)
  - gpt-5-mini: low → medium = 7.7x rows (65 → 500), 3.5x time (~1 → ~3.5 min), 5x cost ($0.007 → $0.034)
  - Diminishing returns for gpt-5: low → high = 38% more rows (356 → 492), 8x time (~2.4 → ~20 min), 6x cost ($0.05 → $0.28)
  - **Trade-off**: gpt-5-mini low processes 455 cells/min vs medium at 1000 cells/min. Medium is 2.2x faster per cell despite 3.5x longer total time.

- **Comprehension is the primary failure mode, not truncation**
  - 9/11 tests failed due to comprehension errors (attention degradation)
  - Average context utilization at failure: only 6.5% - context window is NOT the bottleneck

- **Scale limits vary 168x across models**
  - Best: gpt-5-mini high (675+ rows)
  - Worst: gpt-4o (4 rows)
  - This variance makes model selection critical for production use

- **Format choice causes up to 5.8x scale difference** (Test 02)
  - **csv_quoted is a safe default** - solid mid-tier performance across all models, no conversion cost
  - csv (RFC4180): -20% to -56% on GPT vs csv_quoted, but +5% to +36% on Claude
  - GPT optimal: yaml (+14% over csv_quoted on gpt-5-mini); Claude optimal: json (+55% on opus)
  - Avoid markdown_table on GPT (-67% to -75%) and xml on Claude (-31% to -48%)
  - Token efficiency does NOT predict scale (xml 2.12x tokens beats csv 1.00x on GPT)
  - Format preferences may change with model updates - csv_quoted future-proofs your pipeline

## Production Recommendations

**Response time is critical.** Users won't wait minutes for answers. Recommendations organized by latency tier.

**CPKC** = Cost Per Kilo Cells = cost / (rows × columns) × 1000.

### By Response Time (Primary Selection Criterion)

| Tier     | Time      | Model + Format                    | Scale    | CPKC     | Use Case                    |
|----------|-----------|-----------------------------------|----------|----------|-----------------------------|
| Fast     | ~1 min    | gpt-5.2 medium + csv_quoted       | 268 rows | $0.197   | Interactive, user-facing    |
| Fast     | ~1 min    | gpt-5.2 medium + xml              | 261 rows | $0.252   | Alternative format          |
| Fast     | ~1 min    | gpt-5.2 medium + json             | 241 rows | $0.237   | Most versatile format       |
| Fast     | ~1 min    | gpt-5.2 medium + csv              | 215 rows | $0.226   | Most compact format         |
| Fast     | ~1 min    | gpt-5-mini low + yaml             | 65 rows  | $0.015   | Small tables, lowest cost   |
| Moderate | ~1.4 min  | claude-sonnet medium + json       | 189 rows | $0.408   | Anthropic, most versatile   |
| Moderate | ~1.4 min  | claude-sonnet medium + csv        | 126 rows | $0.340   | Anthropic, most compact     |
| Moderate | ~1.6 min  | claude-opus medium + json         | 265 rows | $0.663   | Max Anthropic scale         |
| Moderate | ~2.4 min  | gpt-5 low + yaml                  | 333 rows | $0.180   | Larger tables, good balance |
| Moderate | ~2.4 min  | gpt-5 low + xml                   | 327 rows | $0.183   | Alternative format          |
| Moderate | ~2.4 min  | gpt-5 low + json                  | 249 rows | $0.212   | Most versatile format       |
| Moderate | ~2.4 min  | gpt-5 low + csv                   | 166 rows | $0.215   | Most compact format         |
| Batch    | ~3.5 min  | gpt-5-mini medium + yaml          | 500 rows | $0.034   | Background jobs, max scale  |
| Batch    | ~3.5 min  | gpt-5-mini medium + kv_colon_space| 500 rows | $0.037   | Alternative format          |
| Batch    | ~3.5 min  | gpt-5-mini medium + csv_quoted    | 437 rows | $0.033   | Best cost efficiency        |
| Batch    | ~3.5 min  | gpt-5-mini medium + json          | 335 rows | $0.043   | Most versatile format       |
| Batch    | ~3.5 min  | gpt-5-mini medium + csv           | 194 rows | $0.052   | Most compact format         |
| Avoid    | 10-20 min | gpt-5 medium/high                 | 450-492  | $0.26+   | Too slow for any use case   |

**Decision tree:**
1. Need <1 min response? → gpt-5.2 medium (268 rows) or gpt-5-mini low (65 rows)
2. Can tolerate ~2 min? → gpt-5 low (333 rows) - best scale/time ratio
3. Background processing? → gpt-5-mini medium (500 rows) - best scale/cost ratio

### Format Selection

**OpenAI:** yaml (+3% scale) or csv_quoted (best value). Avoid markdown_table (-59% scale).

**Anthropic:** json (+27% scale). Avoid xml (-38% scale).

### NOT Recommended

- gpt-5 medium/high (10-20 min - unacceptable latency)
- gpt-4o, gpt-4o-mini, claude-haiku (4-9 row limits - unusable)

### Test Data Structure

- **20 columns** per record: id, name, department, title, salary, clearance, rating, projects, location, start_date, email, phone, manager_id, team, level, bonus_pct, reviews, certifications, equipment, pto
- **7 columns extracted**: id, name, department, salary, clearance, rating, projects
- **Compound filter**: `clearance IN [Level 3, 4, 5] AND salary >= $150,000`
- **Adversarial content**: ~20% of values contain delimiter characters (colons, pipes, commas) to test parsing robustness
- **Format**: Quoted CSV with realistic employee-style data

### Per-Request Execution Times

Average time per single LLM API call across binary search iterations (varying row counts):

- **Fastest**: gpt-5.2 medium (~1 min), gpt-5-mini low (~1 min), claude-sonnet (~1.4 min)
- **Moderate**: gpt-5 low (~2.4 min), gpt-5-mini medium (~4 min)
- **Slowest**: gpt-5 medium (~10 min), gpt-5 high (~20 min)

Note: Times vary by row count. At scale limit, expect times near the upper range. Higher reasoning effort increases both scale limit AND execution time.

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
| **Reasoning** | Binary search found exact boundary at 500 rows - within predicted range |
| **Data** | gpt-5-mini medium: 500 rows (Precision=1.00, Recall=1.00, failed at 507) |

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
| **Data** | gpt-5-mini: low=65, medium=500, high=675+ (+938%). gpt-5: low=356, medium=450, high=492 (+38%) |

### H5: Reasoning Models > Temperature Models

| | |
|---|---|
| **Status** | ✅ STRONGLY SUPPORTED |
| **Hypothesis** | Reasoning models (gpt-5) outperform temperature models (gpt-4o) for tabular extraction |
| **Source** | [CoT Prompting](https://arxiv.org/abs/2201.11903) + [Zero-shot CoT](https://arxiv.org/abs/2205.11916) reasoning emergence |
| **Reasoning** | Massive performance gap makes temperature models unsuitable for tabular extraction |
| **Data** | Mini tier: gpt-5-mini (500) vs gpt-4o-mini (6) = **83x better**. Full tier: gpt-5 (356) vs gpt-4o (4) = **89x better** |

### H6: CSV Best Format

| | |
|---|---|
| **Status** | ❌ NOT SUPPORTED |
| **Hypothesis** | Quoted CSV is optimal format for LLM tabular extraction at scale |
| **Source** | TK-001 format benchmarks ([LLMO-IN01] §6.2); [CFPO](https://arxiv.org/abs/2502.04295) format impact theory |
| **Reasoning** | Format preferences are model-specific. CSV is mid-tier for most models. |
| **Data** | GPT-5-mini: yaml (500) > csv (194). Claude-opus: json (265) > csv (232). Best format varies by family. |

### H7: Format Preferences Differ by Model Family

| | |
|---|---|
| **Status** | ✅ CONFIRMED |
| **Hypothesis** | GPT and Claude have different optimal input formats |
| **Source** | [Microsoft/MIT 2024](https://arxiv.org/abs/2411.10541) - format preferences don't transfer between families |
| **Reasoning** | Rankings are inverted between GPT and Claude. Best format for one is often worst for other. |
| **Data** | GPT best: yaml/xml. Claude best: json. Up to 5.8x scale difference between best/worst format. |

### H8: Token Efficiency Predicts Scale

| | |
|---|---|
| **Status** | ❌ NOT SUPPORTED |
| **Hypothesis** | More compact formats (fewer tokens) enable higher scale limits |
| **Source** | Token efficiency theory; intuition that smaller input = more headroom |
| **Reasoning** | Structure aids comprehension more than compactness. xml (2.12x tokens) beats csv (1.00x) on GPT. |
| **Data** | GPT-5: xml (327) > csv (166) despite 2x token overhead. Claude: csv (232) > xml (182) - reversed. |

## Source Documents

**Test 01 (CSV Scale Limits):**
- [`_INFO_CSVScaleLimits.md`](_Sessions/_2026-03-05_TabularDataFormatsForLLMs/01_CSVScaleLimits/_INFO_CSVScaleLimits.md) - Full research documentation
- [`_TEST_CSVScaleLimits.md`](_Sessions/_2026-03-05_TabularDataFormatsForLLMs/01_CSVScaleLimits/_TEST_CSVScaleLimits.md) - Test plan and detailed analysis

**Test 02 (Format Comparison):**
- [`_INFO_FormatComparison.md`](_Sessions/_2026-03-05_TabularDataFormatsForLLMs/02_FormatComparison/_INFO_FormatComparison.md) - 8 formats × 5 models findings
- [`_TEST_FormatComparison.md`](_Sessions/_2026-03-05_TabularDataFormatsForLLMs/02_FormatComparison/_TEST_FormatComparison.md) - 40 test results with hypothesis evaluations

**Prior Research:**
- TK-001: Format benchmarking (March 2026)
