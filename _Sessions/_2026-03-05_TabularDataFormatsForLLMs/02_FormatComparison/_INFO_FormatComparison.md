<DevSystem MarkdownTablesAllowed=true />

# INFO: Format Comparison (8 Formats)

**Doc ID**: TBLF-IN02
**Goal**: Compare scale limits across 8 input formats for LLM tabular extraction
**Timeline**: Created 2026-03-09

## Summary

**Research Question:** Does input format affect LLM extraction scale limits?

**Hypothesis:** Token-efficient formats may enable higher scale limits, but structured formats may aid comprehension:
- csv_raw is most compact (1.00x baseline)
- xml is most verbose (2.12x baseline)
- Structured formats (json, yaml) may aid parsing despite larger size

**Prior Research Findings** (from TK-001 benchmark at 300 records, gpt-5-mini):
- Key-value formats outperform structured formats (XML, markdown tables have highest variance)
- Separator style (`:` vs `: ` vs `::`) shows no measurable difference on modern models
- CSV (quoted and raw) achieves near-perfect precision (99.9-100%)
- XML has highest variance (Std 0.161) and 1/15 failure rate
- Scale threshold: model reliable at 300 records, unreliable at 600+

**Test Design:**
- Same extraction task as Test 01 (CSVScaleLimits)
- Same data generation (7 columns, adversarial chars, compound filter)
- 8 formats: csv_quoted, csv_raw, kv_colon_space, markdown_table, json, xml, yaml, toml
- Excluded: kv_colon, kv_double_colon
- 5 models from Test 01 production recommendations

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

| Rank | Format | Precision | Std Dev | Recall |
|------|--------|-----------|---------|--------|
| 1 | `::` (double colon) | 1.000 | 0.000 | 0.997 |
| 2 | `: ` (colon space) | 1.000 | 0.000 | 0.989 |
| 3 | CSV quoted | 1.000 | 0.000 | 0.991 |
| 4 | TOML | 0.999 | 0.003 | 0.988 |
| 5 | `:` (colon) | 0.999 | 0.003 | 0.998 |
| 6 | CSV raw | 0.999 | 0.002 | 0.953 |
| 7 | JSON | 0.998 | 0.004 | 0.979 |
| 8 | YAML | 0.991 | 0.006 | 0.991 |
| 9 | Markdown table | 0.978 | 0.038 | 0.950 |
| 10 | XML | 0.956 | 0.161 | 0.965 |

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

## Expected Outcomes

**If CSV outperforms other formats:**
- Confirms token efficiency matters for scale
- Supports CSV as optimal production format

**If key-value formats match or exceed CSV:**
- Confirms TK-001 finding that format TYPE > token count
- Key-value structure aids extraction comprehension

## Source Documents

- Test 01: `_INFO_CSVScaleLimits.md [TBLF-IN01]` - CSV baseline results
- Format Research: `IPPS/_PrivateSessions/_2026-03-04_LLMMarkdownOptimization/_INFO_LLM_MARKDOWN_PREFERENCES.md [LLMO-IN01]` - TK-001 benchmark, academic papers
- POC: `IPPS/_PrivateSessions/_2026-03-04_LLMMarkdownOptimization/poc` - Format samples

## Document History

**[2026-03-09 19:48]**
- Changed: Scope expanded from kv_colon only to 8 formats
- Added: csv_raw, kv_colon_space, markdown_table, json, xml, yaml, toml
- Removed: kv_colon, kv_double_colon (per user request)
- Updated: Test matrix 7 formats x 5 models = 35 new tests

**[2026-03-09 19:42]**
- Initial document created
- Test matrix defined: 5 models x kv_colon format
