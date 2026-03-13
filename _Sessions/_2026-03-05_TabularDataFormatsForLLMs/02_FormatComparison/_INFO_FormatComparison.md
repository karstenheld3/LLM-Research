<DevSystem MarkdownTablesAllowed=true />

# INFO: Format Comparison (8 Formats)

**Doc ID**: TBLF-IN02
**Goal**: Compare scale limits across 8 input formats for LLM tabular extraction
**Timeline**: Created 2026-03-09

## Summary

**Research Question:** Does input format affect LLM extraction scale limits?

**Status:** 48/48 tests complete (2026-03-12)

### Key Findings

1. **Format preferences differ dramatically by model family** (H3 CONFIRMED)
   - Older GPT models prefer: yaml, xml, kv_colon_space
   - gpt-5.4 and Claude models prefer: json
   - Best format for one family can be worst for another

2. **Token efficiency does NOT predict scale limits** (H5 CONTRADICTED)
   - xml (2.12x tokens) outperforms csv (1.00x) on GPT models by 1.5-2x
   - csv only outperforms xml on Claude models
   - Structure aids comprehension more than compactness

3. **JSON is NOT universally optimal** (H2 MIXED)
   - JSON is best for Claude (opus: 265, sonnet: 189) and gpt-5.4 (702)
   - JSON is mid-tier for older GPT (gpt-5-mini: 335 vs yaml: 500)

4. **Key-value format results are model-specific** (H6 CONTRADICTED)
   - kv_colon_space ties for best on gpt-5-mini (500)
   - kv_colon_space is worst on gpt-5.2 (100 vs csv_quoted: 268)

### Best Format Per Model

| Model        | Best Format | Scale | Worst Format   | Scale | Ratio |
|--------------|-------------|-------|----------------|-------|-------|
| gpt-5.4      | json        | 702   | kv_colon_space | 359   | 2.0x  |
| gpt-5-mini   | yaml/kv     | 500   | markdown_table | 163   | 3.1x  |
| gpt-5        | yaml        | 333   | markdown_table | 83    | 4.0x  |
| gpt-5.2      | csv_quoted  | 268   | toml           | 46    | 5.8x  |
| opus-4.5     | json        | 265   | csv_quoted     | 171   | 1.5x  |
| sonnet-4.5   | json        | 189   | xml            | 99    | 1.9x  |

**IMPORTANT**: Test 02 uses simplified dataset (7/7 columns) vs Test 01 (7/20 columns). Results not directly comparable to Test 01 baselines. See `TBLF-FL-005`.

### Test Design

- 8 formats: csv_quoted, csv, kv_colon_space, markdown_table, json, xml, yaml, toml
- 6 models: gpt-5.4 medium, gpt-5-mini medium, gpt-5 low, gpt-5.2 medium, claude-opus medium, claude-sonnet medium
- Binary search with 3 runs per scale point
- Filter: department="Engineering" AND salary>75000

### Hypothesis Evaluation (Test 02 Results)

- **H1**
  - **Hypothesis**: Separator style affects scale
  - **Source**: Sclar et al. 2024
  - **Status**: CONTRADICTED
  - **Evidence**: TK-001: no measurable difference on modern models
- **H2**
  - **Hypothesis**: JSON not optimal despite structure
  - **Source**: Microsoft/MIT 2024
  - **Status**: MIXED
  - **Evidence**: GPT: JSON mid-tier (335 vs yaml 500). Claude: JSON is BEST (265, 189)
- **H3**
  - **Hypothesis**: Format preferences differ by family
  - **Source**: Microsoft/MIT 2024
  - **Status**: **CONFIRMED**
  - **Evidence**: GPT prefers yaml/xml. Claude prefers json. Rankings inverted.
- **H4**
  - **Hypothesis**: Optimal format depends on complexity
  - **Source**: Microsoft CFPO 2025
  - **Status**: INCONCLUSIVE
  - **Evidence**: Requires tests at multiple complexity levels
- **H5**
  - **Hypothesis**: Token-efficient formats enable higher scale
  - **Source**: Token efficiency theory
  - **Status**: **CONTRADICTED**
  - **Evidence**: xml (2.12x) beats csv (1.00x) on GPT by 1.5-2x
- **H6**
  - **Hypothesis**: Key-value outperforms structured
  - **Source**: TK-001 benchmark
  - **Status**: **CONTRADICTED**
  - **Evidence**: Only true for gpt-5-mini. Worst format for gpt-5.2

### Detailed Evidence

**H3 - Format preferences differ by model family:**
```
GPT-5-mini best:  yaml (500), kv_colon_space (500)
GPT-5 best:       yaml (333), xml (327)
GPT-5.2 best:     csv_quoted (268), xml (261)
Claude-opus best: json (265), yaml (259)
Claude-sonnet:    json (189), csv (126)
```
GPT models consistently rank yaml/xml high; Claude models rank json highest.

**H5 - Token efficiency vs scale (csv 1.00x vs xml 2.12x):**
```
gpt-5-mini: csv (194) < xml (296) - xml 1.5x better despite 2x tokens
gpt-5:      csv (166) < xml (327) - xml 2.0x better
gpt-5.2:    csv (215) < xml (261) - xml 1.2x better
claude-opus: csv (232) > xml (182) - csv 1.3x better
claude-sonnet: csv (126) > xml (99) - csv 1.3x better
```
Token efficiency predicts scale for Claude but NOT for GPT.

**H6 - Key-value vs structured formats:**
```
gpt-5-mini: kv (500) > json (335), xml (296) - CONFIRMED
gpt-5:      kv (238) < yaml (333), xml (327) - CONTRADICTED
gpt-5.2:    kv (100) << csv_quoted (268) - CONTRADICTED (worst format)
claude-opus: kv (226) < json (265) - CONTRADICTED
claude-sonnet: kv (126) < json (189) - CONTRADICTED
```
Only gpt-5-mini confirms TK-001 finding. Other models contradict.

### Format Size Comparison (300 rows)

| Format         | Size (KB) | Relative |
|----------------|-----------|----------|
| csv_raw        | 148       | 1.00x    |
| csv_quoted     | 156       | 1.06x    |
| markdown_table | 197       | 1.33x    |
| kv_colon_space | 217       | 1.47x    |
| toml           | 235       | 1.59x    |
| yaml           | 249       | 1.68x    |
| json           | 269       | 1.82x    |
| xml            | 314       | 2.12x    |

### Test Matrix

**Models (5):** gpt-5-mini medium, gpt-5 low, gpt-5.2 medium, claude-opus medium, claude-sonnet medium

**Formats (7 new):** csv_raw, kv_colon_space, markdown_table, json, xml, yaml, toml
(csv_quoted baseline from Test 01)

**Total tests:** 5 models × 7 formats = 35 new tests

## Format Examples

### CSV (quoted)
```
"id","name","department","salary","clearance","rating","projects"
"EMP-0001","Sarah Mitchell-Reynolds","Research & Development","$185,000","Level 4: Top Secret","Exceeds Expectations: Top 20%","Project Aurora: Lead | Nexus: Contributor"
```

### kv_colon_space
```
### Record 1
Id: EMP-0001
Name: Sarah Mitchell-Reynolds
Department: Research & Development
Salary: $185,000
Clearance: Level 4: Top Secret
```

## Methodology

1. Use same binary search algorithm as Test 01
2. **Start at CSV baseline** (faster convergence):
   - gpt-5-mini medium: start at 500 rows
   - gpt-5 low: start at 356 rows
   - gpt-5.2 medium: start at 215 rows
   - claude-opus medium: start at 177 rows
   - claude-sonnet medium: start at 168 rows
3. Same success criteria: Precision=1.00 AND Recall=1.00 across 3 runs
4. Same filter conditions and column selection
5. Compare scale limits between formats for each model

## Prior Research: TK-001 Format Ranking (300 records, n=15)

**Source:** `IPPS/_PrivateSessions/_2026-03-04_LLMMarkdownOptimization/_INFO_LLM_MARKDOWN_PREFERENCES.md [LLMO-IN01]`

| Rank | Format              | Precision | Std Dev | Recall |
|------|---------------------|-----------|---------|--------|
| 1    | `::` (double colon) | 1.000     | 0.000   | 0.997  |
| 2    | `: ` (colon space)  | 1.000     | 0.000   | 0.989  |
| 3    | CSV quoted          | 1.000     | 0.000   | 0.991  |
| 4    | TOML                | 0.999     | 0.003   | 0.988  |
| 5    | `:` (colon)         | 0.999     | 0.003   | 0.998  |
| 6    | CSV raw             | 0.999     | 0.002   | 0.953  |
| 7    | JSON                | 0.998     | 0.004   | 0.979  |
| 8    | YAML                | 0.991     | 0.006   | 0.991  |
| 9    | Markdown table      | 0.978     | 0.038   | 0.950  |
| 10   | XML                 | 0.956     | 0.161   | 0.965  |

**Key insight:** Format TYPE matters more than token efficiency. Key-value formats outperform structured formats (XML, YAML) despite intuition.

## Academic Research Context

### Primary Papers (Format Impact)

**1. Sclar et al. ICLR 2024** - "Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design"
- arXiv: https://arxiv.org/abs/2310.11324
- Local: `Papers/2024-04-16_QuantifyingLanguageModelsSensitivityToSpuriousFeaturesInPromptDesign_2310.11324v2.md`
- **Scope:** Prompt TEMPLATE formatting (separators, spacing, casing), NOT data representation formats
- **Models tested:** LLaMA-2-{7B,13B,70B}, Falcon-7B, GPT-3.5-Turbo
- **Key findings:**
  - Up to 76 accuracy points variance from template format changes (LLaMA-2-13B)
  - Median spread 7.5 accuracy points across 53 tasks
  - Separators (S₁) highest impact: 43% weak diff, 22% strong diff
  - Casing lowest impact: 3% weak diff, 0% strong diff
  - Sensitivity NOT eliminated by: model size, instruction tuning, more few-shot examples
  - Model comparison trends can be REVERSED by choosing different formats
- **Testable hypothesis for our research:**
  - H1: Separator style (`:` vs `: `) affects scale limits (test via kv_colon_space)
  - [CONTRADICTED by TK-001]: gpt-5-mini showed NO separator sensitivity at 300 rows
- **Limitation:** Paper tested older models (LLaMA-2, 2023); may not apply to frontier models (GPT-5, Claude-4)

**2. Microsoft/MIT 2024** - "Does Prompt Formatting Have Any Impact on LLM Performance?"
- arXiv: https://arxiv.org/abs/2411.10541
- Local: `Papers/2024-11-15_DoesPromptFormattingHaveAnyImpactOnLLMPerformance_2411.10541v1.md`
- **Scope:** Prompt FORMAT (Plain text, Markdown, YAML, JSON) on GPT-3.5/GPT-4
- **Models tested:** GPT-3.5-turbo, GPT-3.5-turbo-16k, GPT-4-32k, GPT-4-1106-preview
- **Tasks:** MMLU, HumanEval, NER Finance, CODEXGLUE, HumanEval-X, FIND
- **Key findings:**
  - Up to 40% variance for GPT-3.5-turbo depending on format
  - 200-300% improvement possible (FIND: Markdown→Plain text)
  - GPT-3.5 prefers JSON, GPT-4 prefers Markdown
  - Format preferences don't transfer between families (IoU < 0.2)
  - Same sub-series share preferences (IoU > 0.7)
  - GPT-4 more robust and consistent than GPT-3.5
  - Only 16% identical responses between Markdown/JSON for GPT-3.5
- **Testable hypotheses for our research:**
  - H2: JSON may not be optimal despite structure (GPT-4 preferred Markdown)
  - H3: Format preferences differ by model family (test GPT-5 vs Claude)
- **Directly relevant:** Tests actual data formats (JSON, YAML, Markdown) not just separators

**3. Microsoft CFPO 2025** - "Beyond Prompt Content: Enhancing LLM Performance Via Content-Format Integration"
- arXiv: https://arxiv.org/abs/2502.04295
- Local: `Papers/2025-02-06_BeyondPromptContent-EnhancingLLMPerformanceViaContent-FormatIntegration_2502.04295v3.md`
- **Scope:** Joint optimization of prompt CONTENT + FORMAT
- **Models tested:** Open-source LLMs (LLaMA-3-1.8B, etc.)
- **Tasks:** GSM8K (math reasoning)
- **Format renderers tested:** Plain Text, Markdown, HTML, LaTeX, XML, JSON
- **Key findings:**
  - 20-65% accuracy variance from format alone on GSM8K
  - Different LLMs have distinct format preferences (model-specific biases)
  - Optimal format varies by prompt content (content-format interdependence)
  - Joint content-format optimization outperforms content-only
- **Testable hypothesis for our research:**
  - H4: Optimal format depends on content complexity (test with varying row counts)
- **Directly relevant:** Tests actual data formats (JSON, XML, Markdown) for prompt rendering

### Supporting Papers (Long Context, Instruction Following)

**4. ECNU/iQIYI LIFBench 2024** - "Evaluating Instruction Following Performance in Long Context"
- arXiv: https://arxiv.org/abs/2411.07037
- Local: `Papers/2024-11-11_LIFBench-EvaluatingTheInstructionFollowingPerformanceOfLLMsInLongContext_2411.07037v1.md`
- **Scope:** Instruction-following STABILITY in long context (4k-128k tokens), NOT data format comparison
- **Models tested:** 20 LLMs including GPT-4o, GPT-4, Qwen, Llama, C4AI
- **Six capabilities measured:** Format, Number, Original content, Logic, Recognition, Spatial
- **Key findings:**
  - Format (Fmt) capability **most stable** across models - tightest clustering
  - Recognition (Recog) **degrades most** with increasing context
  - Performance drops as context length increases (all models)
  - GPT-4o best overall (0.758), still significant room for improvement
  - Instruction-tuned models outperform base models significantly
- **Relevance to our research:**
  - Context length degradation supports testing scale limits
  - "Format stable" refers to OUTPUT format instructions, NOT input data format
- **Limitation:** Does not test CSV vs JSON vs XML for data representation

## Production Recommendations

**Based on Test 02 results (40/40 tests, 2026-03-10):**

### By Model Family

**GPT Models:**
- Use **yaml** or **xml** for maximum scale
- Avoid markdown_table (consistently worst)
- csv_quoted is safe middle-ground choice

**Claude Models:**
- Use **json** for maximum scale
- csv is good second choice
- Avoid xml (worst for both opus and sonnet)

### Cost-Efficiency (CPKC - Cost Per Kilo Cells)

| Model           | Best CPKC Format | CPKC   | Scale |
|-----------------|------------------|--------|-------|
| gpt-5-mini      | csv_quoted       | $0.033 | 437   |
| gpt-5-mini      | yaml             | $0.034 | 500   |
| gpt-5           | yaml             | $0.180 | 333   |
| gpt-5.2         | toml             | $0.373 | 46    |
| claude-opus     | csv              | $0.566 | 232   |
| claude-sonnet   | csv              | $0.340 | 126   |

**Best overall value:** gpt-5-mini with csv_quoted ($0.033/KC) or yaml ($0.034/KC, +14% scale)

### Key Insight

Format choice matters more than previously thought - up to **5.8x scale difference** between best and worst format on gpt-5.2. Always test your target model with your intended format.

## Source Documents

- Test 01: `_INFO_CSVScaleLimits.md [TBLF-IN01]` - CSV baseline results
- Format Research: `IPPS/_PrivateSessions/_2026-03-04_LLMMarkdownOptimization/_INFO_LLM_MARKDOWN_PREFERENCES.md [LLMO-IN01]` - TK-001 benchmark, academic papers
- POC: `IPPS/_PrivateSessions/_2026-03-04_LLMMarkdownOptimization/poc` - Format samples

## Document History

**[2026-03-10 08:40]**
- Added: Test 02 results (40/40 tests complete)
- Added: Hypothesis evaluations with evidence
- Added: Best format per model table
- Added: Production recommendations
- Added: Cost-efficiency analysis (CPKC)
- Changed: Summary rewritten with key findings

**[2026-03-09 19:48]**
- Changed: Scope expanded from kv_colon only to 8 formats
- Added: csv_raw, kv_colon_space, markdown_table, json, xml, yaml, toml
- Removed: kv_colon, kv_double_colon (per user request)
- Updated: Test matrix 7 formats x 5 models = 35 new tests

**[2026-03-09 19:42]**
- Initial document created
- Test matrix defined: 5 models x kv_colon format
