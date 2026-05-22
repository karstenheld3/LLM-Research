<DevSystem MarkdownTablesAllowed=true />

# LLM Tabular Data Extraction: Scale Limits Research

Research on maximum reliable row counts for LLM tabular data extraction across models.

## Research Summary

**Questions:**
1. What are the maximum reliable row counts for LLM filtered extraction from CSV tables? (Test 01)
2. Does input format affect LLM extraction scale limits? (Test 02)

*Extraction accuracy at scale serves as a practical proxy for tabular data comprehension capacity - models that can reliably extract filtered records demonstrate working comprehension of the underlying data.*

**Status:** Test 01: 14/14 complete | Test 02: 56/56 complete (May 2026)

## Key Findings

- **Reasoning models massively outperform temperature models** (83-89x better scale limits)
  - gpt-5-mini reliably extracts 150 matching records from 500 rows vs gpt-4o-mini failing at 6 rows (2 matches)
  - Reasoning architecture enables systematic data processing that temperature sampling cannot achieve

- **Higher reasoning effort dramatically increases scale limit** (up to 10x improvement)
  - gpt-5-mini: low → medium = 7.7x rows (65 → 500), 3.5x time (~1 → ~3.5 min), 5x cost ($0.004 → $0.017)
  - Diminishing returns for gpt-5: low → high = 38% more rows (356 → 492), 8x time (~2.4 → ~20 min), 6x cost ($0.03 → $0.14)
  - **Trade-off**: gpt-5-mini low processes 455 cells/min vs medium at 1000 cells/min. Medium is 2.2x faster per cell despite 3.5x longer total time.

- **Comprehension is the primary failure mode, not truncation**
  - 9/11 tests failed due to comprehension errors (attention degradation)
  - Average context utilization at failure: only 6.5% - context window is NOT the bottleneck

- **Scale limits vary 207x across models**
  - Best: gpt-5.5 medium with toml format (828 rows)
  - Worst: gpt-4o (4 rows)
  - This variance makes model selection critical for production use

- **Newer/pricier models can regress on specific formats**
  - gpt-5.5 CSV extraction (437 rows) underperforms gpt-5.4 (492 rows) by 11% (Test 01)
  - But gpt-5.5 with toml (828 rows) exceeds gpt-5.4 json (702 rows) by 18% (Test 02)
  - gpt-5.5 costs 2x more ($5/$30 vs $2.5/$15 per 1M tokens)
  - Format selection is critical: wrong format loses the advantage, right format unlocks it

- **gpt-5.5 medium with toml achieves highest scale** (Test 02)
  - toml: 828 rows (best overall across all models)
  - yaml: 675, markdown_table: 627, kv_colon_space: 588
  - csv/csv_quoted: ~493, json: 430, xml: 375 (worst)
  - Completely different ranking from gpt-5.4 (json best at 702, toml mid-tier at 523)

- **Format choice causes up to 5.8x scale difference** (Test 02)
  - **csv_quoted is a safe default** - solid mid-tier performance across all models, no conversion cost
  - Each model generation has different optimal format (see Format Selection below)
  - Token efficiency does NOT predict scale (xml 2.12x tokens beats csv 1.00x on older GPT)
  - Format preferences shift with model updates - benchmark before committing to a format

## Production Recommendations

**Response time is critical.** Users won't wait minutes for answers. Recommendations organized by latency tier.

**CPKC** = Cost Per Kilo Cells = cost / (rows × columns) × 1000.

> **Note**: Costs updated March 2026 to reflect OpenAI's 50% price reduction (announced ~March 10, 2026). Anthropic prices unchanged.

### By Response Time (Primary Selection Criterion)

| Tier     | Time      | Model + Format                    | Scale    | CPKC     | Use Case                    |
|----------|-----------|-----------------------------------|----------|----------|-----------------------------|
| Fast     | ~1.2 min  | gpt-5.5 medium + toml             | 828 rows | $0.131   | **Max scale overall**       |
| Fast     | ~1.0 min  | gpt-5.5 medium + yaml             | 675 rows | $0.142   | Second-best scale           |
| Fast     | ~0.7 min  | gpt-5.5 medium + markdown_table   | 627 rows | $0.132   | Fastest high-scale          |
| Fast     | ~0.8 min  | gpt-5.5 medium + kv_colon_space   | 588 rows | $0.126   | Simple format, good scale   |
| Fast     | ~0.6 min  | gpt-5.5 medium + csv_quoted       | 491 rows | $0.125   | No conversion cost          |
| Fast     | ~1 min    | gpt-5.2 medium + csv_quoted       | 268 rows | $0.101   | Budget option, user-facing  |
| Fast     | ~1 min    | gpt-5-mini low + yaml             | 65 rows  | $0.008   | Small tables, lowest cost   |
| Moderate | ~1.4 min  | claude-sonnet medium + json       | 189 rows | $0.408   | Anthropic, most versatile   |
| Moderate | ~1.6 min  | claude-opus medium + json         | 265 rows | $0.663   | Max Anthropic scale         |
| Moderate | ~2.9 min  | gpt-5.4 medium + json             | 702 rows | $0.189   | Legacy max (pre-gpt-5.5)    |
| Moderate | ~2.4 min  | gpt-5 low + yaml                  | 333 rows | $0.090   | Budget, larger tables       |
| Batch    | ~3.5 min  | gpt-5-mini medium + yaml          | 500 rows | $0.017   | Background jobs, best CPKC  |
| Batch    | ~3.5 min  | gpt-5-mini medium + kv_colon_space| 500 rows | $0.020   | Alternative format          |
| Batch    | ~3.5 min  | gpt-5-mini medium + csv_quoted    | 437 rows | $0.016   | Best cost efficiency        |
| Avoid    | 10-20 min | gpt-5 medium/high                 | 450-492  | $0.13+   | Too slow for any use case   |

**Decision tree:**
1. Need max scale + fast? → gpt-5.5 medium + toml (828 rows, ~1.2 min)
2. Need <1 min response? → gpt-5.5 medium + markdown_table (627 rows, ~0.7 min)
3. Need low cost? → gpt-5.2 medium (268 rows) or gpt-5-mini low (65 rows)
4. Background processing? → gpt-5-mini medium + yaml (500 rows, $0.017 CPKC)

### Format Selection

**gpt-5.5:** toml (+68% vs csv_quoted). Avoid xml (-24%) and json (-12%).

**Older GPT (5-mini, 5, 5.2):** yaml (+14% vs csv_quoted). Avoid markdown_table (-59%).

**gpt-5.4:** json (+34% vs csv_quoted). Avoid kv_colon_space (-31%).

**Anthropic:** json (+27% scale). Avoid xml (-38% scale).

**Safe default (all models):** csv_quoted - mid-tier everywhere, no format conversion cost.

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

Hypotheses derive from three sources:

1. **TK-001 Internal Benchmark** (March 2026) - Prior format comparison testing 10 variants on gpt-5-mini extraction tasks. Documented in `_INFO_LLM_MARKDOWN_PREFERENCES.md [LLMO-IN01]`.

2. **Academic Literature** - Theoretical foundations from peer-reviewed research:
   - [Chain-of-Thought Prompting](https://arxiv.org/abs/2201.11903) (Wei et al., NeurIPS 2022) - Reasoning improves complex tasks
   - [LIFBench](https://arxiv.org/abs/2411.07037) (Wu et al., 2024) - Long-context instruction following degrades at scale
   - [Does Prompt Formatting Impact LLM?](https://arxiv.org/abs/2411.10541) (He et al., Microsoft/MIT 2024) - Format affects performance up to 40%
   - [CFPO](https://arxiv.org/abs/2502.04295) (Liu et al., Microsoft Research 2025) - Content-format integration

3. **External Benchmarks** - Corroborating evidence from independent evaluations:
   - [TQA-Bench](https://arxiv.org/abs/2411.19504) (Qiu et al., 2024) - Multi-table QA with format comparison (Markdown vs CSV). Confirms CSV suboptimal (H6), model family drives format preference (H7), temperature models degrade gradually not cliff-like (H2). Models tested: GPT-4o, GPT-4o-mini, open-source 7B-8B. No reasoning models.
   - [NoLiMa](https://arxiv.org/abs/2502.05167) (Modarressi et al., ICML 2025) - Long-context evaluation beyond literal matching. Proves attention is the bottleneck not truncation (H3), reasoning helps but with diminishing returns at scale (H4), reasoning models maintain attention better (H5). Models tested: GPT-4o/4.1, o1/o3/o3-mini/o4-mini, Claude 3.5 Sonnet, Gemini 2.5. No gpt-5 family.

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
| **Data** | gpt-5.5: toml (828) > csv (494). gpt-5-mini: yaml (500) > csv (194). Claude-opus: json (265) > csv (232). |

### H7: Format Preferences Differ by Model Family

| | |
|---|---|
| **Status** | ✅ CONFIRMED |
| **Hypothesis** | GPT and Claude have different optimal input formats |
| **Source** | [Microsoft/MIT 2024](https://arxiv.org/abs/2411.10541) - format preferences don't transfer between families |
| **Reasoning** | Rankings are inverted between GPT and Claude. Even within GPT, each generation has different preferences. |
| **Data** | gpt-5.5 best: toml. gpt-5.4 best: json. Older GPT best: yaml/xml. Claude best: json. Up to 5.8x difference. |

### H8: Token Efficiency Predicts Scale

| | |
|---|---|
| **Status** | ❌ NOT SUPPORTED |
| **Hypothesis** | More compact formats (fewer tokens) enable higher scale limits |
| **Source** | Token efficiency theory; intuition that smaller input = more headroom |
| **Reasoning** | Structure aids comprehension more than compactness. xml (2.12x tokens) beats csv (1.00x) on older GPT. |
| **Data** | gpt-5: xml (327) > csv (166) despite 2x tokens. gpt-5.5: csv (494) > xml (375) - reversed like Claude. |

### H9: Structural Format Markers Serve as Attention Anchors

| | |
|---|---|
| **Status** | ❌ CONTRADICTED |
| **Hypothesis** | Formats with distinctive structural markers (keys, tags, delimiters) improve comprehension by providing attention anchor points that guide the model to relevant data |
| **Source** | [NoLiMa](https://arxiv.org/abs/2502.05167) mechanism finding: attention relies on literal cues; format markers create such cues |
| **Reasoning** | XML (most markers, 2.12x tokens) is worst in 5/7 models. Format preferences shift between model generations (gpt-5.4: json, gpt-5.5: toml), indicating training data composition drives preference, not structural properties. |
| **Data** | XML worst: gpt-5.5 (375), gpt-5-mini (163), gpt-5.2 (89), opus (164), sonnet (99). XML 2nd only on gpt-5.4 (609) and gpt-5 (327). |

### H10: Comprehension Benchmark Scores Predict Extraction Scale Limits

| | |
|---|---|
| **Status** | UNTESTED |
| **Hypothesis** | A model's effective comprehension length (measured by any semantic understanding benchmark) correlates with its maximum reliable extraction scale |
| **Source** | [NoLiMa](https://arxiv.org/abs/2502.05167): effective length metric; our Test 01 scale limits; shared pattern of failure far below claimed context window |
| **Reasoning** | Both extraction and comprehension fail at the same bottleneck (attention degradation). Models with stronger attention should excel at both tasks proportionally. |
| **Prediction** | Strong positive correlation (r > 0.7) between comprehension benchmark effective lengths and our scale limit breakpoints across models. |

## Source Documents

**Test 01 (CSV Scale Limits):**
- [`_INFO_CSVScaleLimits.md`](_Sessions/_2026-03-05_TabularDataFormatsForLLMs/01_CSVScaleLimits/_INFO_CSVScaleLimits.md) - Full research documentation
- [`_TEST_CSVScaleLimits.md`](_Sessions/_2026-03-05_TabularDataFormatsForLLMs/01_CSVScaleLimits/_TEST_CSVScaleLimits.md) - Test plan and detailed analysis

**Test 02 (Format Comparison):**
- [`_INFO_FormatComparison.md`](_Sessions/_2026-03-05_TabularDataFormatsForLLMs/02_FormatComparison/_INFO_FormatComparison.md) - 8 formats × 7 models findings
- [`_TEST_FormatComparison.md`](_Sessions/_2026-03-05_TabularDataFormatsForLLMs/02_FormatComparison/_TEST_FormatComparison.md) - 56 test results with hypothesis evaluations

**Prior Research:**
- TK-001: Format benchmarking (March 2026)

**Papers Screened** (`Papers/`):
- [Chain-of-Thought Prompting Elicits Reasoning in LLMs](https://arxiv.org/abs/2201.11903) (Wei et al., 2022)
- [Training Language Models to Follow Instructions with Human Feedback](https://arxiv.org/abs/2203.02155) (Ouyang et al., 2022)
- [Self-Consistency Improves Chain-of-Thought Reasoning](https://arxiv.org/abs/2203.11171) (Wang et al., 2022)
- [Least-to-Most Prompting Enables Complex Reasoning in LLMs](https://arxiv.org/abs/2205.10625) (Zhou et al., 2022)
- [Large Language Models Are Zero-Shot Reasoners](https://arxiv.org/abs/2205.11916) (Kojima et al., 2022)
- [Instruction-Following Evaluation for Large Language Models](https://arxiv.org/abs/2311.07911) (Zhou et al., 2023)
- [Chain-of-Thought Reasoning Without Prompting](https://arxiv.org/abs/2402.10200) (Wang & Zhou, 2024)
- [Efficient Prompting Methods for LLMs - A Survey](https://arxiv.org/abs/2404.01077) (2024)
- [Quantifying Language Models Sensitivity to Spurious Features in Prompt Design](https://arxiv.org/abs/2310.11324) (2024)
- [The Instruction Hierarchy - Training LLMs to Prioritize Privileged Instructions](https://arxiv.org/abs/2404.13208) (2024)
- [Prompt Compression for Large Language Models - A Survey](https://arxiv.org/abs/2410.12388) (2024)
- [LIFBench - Evaluating Instruction Following in Long Context](https://arxiv.org/abs/2411.07037) (Wu et al., 2024)
- [Does Prompt Formatting Have Any Impact on LLM Performance?](https://arxiv.org/abs/2411.10541) (He et al., Microsoft/MIT 2024)
- [TQA-Bench - Evaluating LLMs for Multi-Table QA with Scalable Context](https://arxiv.org/abs/2411.19504) (Qiu et al., 2024)
- [Beyond Prompt Content - Enhancing LLM Performance via Content-Format Integration](https://arxiv.org/abs/2502.04295) (Liu et al., Microsoft Research 2025)
- [NoLiMa - Long-Context Evaluation Beyond Literal Matching](https://arxiv.org/abs/2502.05167) (Modarressi et al., ICML 2025)
- [IHEval - Evaluating Instruction Hierarchy Following](https://arxiv.org/abs/2502.08745) (2025)
- [Incorporating Token Usage into Prompting Strategy Evaluation](https://arxiv.org/abs/2505.14880) (2025)
