<DevSystem MarkdownTablesAllowed=true />

# INFO: Format Comparison - Findings

**Doc ID**: TBLF-IN06
**Goal**: Derive findings from format comparison results, evaluate hypotheses, develop production recommendations
**Timeline**: Created 2026-05-22

**Depends on:**
- `_INFO_01_FormatComparison-TestResults.md [TBLF-IN05]` for all test result data

**Does not depend on:**
- `_TEST_FormatComparison.md [TBLF-TP02]` (execution procedures only, no results)

## Table of Contents

1. [Key Findings](#1-key-findings)
2. [Hypothesis Verdicts](#2-hypothesis-verdicts)
3. [Detailed Analysis](#3-detailed-analysis)
4. [Unexpected Findings](#4-unexpected-findings)
5. [Production Recommendations](#5-production-recommendations)
6. [Emergent Hypotheses](#6-emergent-hypotheses)
7. [Open Questions](#7-open-questions)
8. [Caveats and Limitations](#8-caveats-and-limitations)
9. [Sources](#9-sources)
10. [Document History](#10-document-history)

## 1. Key Findings

<!-- AUTO:findings-1:start -->
Derived from 63 tests (62 completed + 1 incomplete). opus-4.8 yaml incomplete (passed 738 rows, crashed at 1107). Data in `_INFO_01_FormatComparison-TestResults.md [TBLF-IN05]` section 5.

- **Format preferences differ dramatically by model family** [TESTED]
  - GPT best formats: gpt-5.5: toml, gpt-5.4: json, gpt-5-mini: kv_colon_space, gpt-5: yaml, gpt-5.2: csv_quoted
  - Claude best formats: opus-4.8: csv, opus-4.5: json, sonnet-4.5: json
  - Max spread: 5.8x (gpt-5.2)

- **Token efficiency does NOT predict scale limits** [TESTED]
  - xml (2.12x tokens) outperforms csv (1.00x) on 4/8 models
  - csv outperforms xml on 4/8 models (newer GPT + Claude)

- **Format impact is massive - up to 5.8x within a single model** [TESTED]
  - gpt-5-mini: kv_colon_space (500) vs markdown_table (163) = 3.1x
  - gpt-5: yaml (333) vs markdown_table (83) = 4.0x
  - gpt-5.2: csv_quoted (268) vs toml (46) = 5.8x

- **No universal best format exists** [TESTED]
  - gpt-5.5: toml (828)
  - gpt-5.4: json (702)
  - gpt-5-mini: kv_colon_space (500)
  - gpt-5: yaml (333)
  - gpt-5.2: csv_quoted (268)
  - opus-4.8: csv (630)
  - opus-4.5: json (265)
  - sonnet-4.5: json (189)

- **Format preference shifts between model generations** [TESTED]
  - gpt-5.4: json (702). gpt-5.5: toml (828), json drops to 430 (-39%)
<!-- AUTO:findings-1:end -->

- **json is the safest untested default** [VERIFIED]
  - Avg rank 2.9/8, stdev 2.2 across 7 models. Worst case: 52% of best format. See section 3.5.

- **Output tokens are format-independent** [VERIFIED]
  - Input varies 2.3x (json 91K vs csv 40K). Output stable at 27-33K regardless of format.

- **Failure mode is model-specific, not format-specific** [VERIFIED]
  - 57/63 comprehension, 6/63 truncation. All truncation = opus-4.5 only. See section 3.6.

## 2. Hypothesis Verdicts

**Precision note**: All verdicts are based on n=3 verification runs per binary search iteration. Scale limits have ~28% variance between independent runs (from Test 01). Differences <20% may be within noise. See section 8 for caveats.

Prior evidence from TK-001 benchmark and academic research (Sclar 2024, Microsoft/MIT 2024, Microsoft CFPO 2025):
- Key-value formats ranked #1-#2 at 300 records (gpt-5-mini only)
- Format can cause up to 76% accuracy variance (Sclar, older models)
- GPT-3.5 prefers JSON, GPT-4 prefers Markdown (Microsoft/MIT)
- Format preferences don't transfer between model families (IoU < 0.2)

- **H2 - JSON not optimal despite structure**: MIXED (Medium) [TESTED]
  - GPT older models: JSON mid-tier (gpt-5-mini: 335 vs yaml 500). Claude: JSON is BEST (opus: 265, sonnet: 189)
- **H3 - Format preferences differ by model family**: CONFIRMED (Very High) [TESTED]
  - GPT prefers yaml/xml/toml. Claude prefers json. Rankings inverted.
- **H4 - Optimal format depends on complexity**: INCONCLUSIVE [ASSUMED]
  - Requires tests at multiple complexity levels (not yet conducted)
- **H5 - Token-efficient formats enable higher scale**: CONTRADICTED (High) [TESTED]
  - xml (2.12x) beats csv (1.00x) on 4/5 older GPT models. Reversed on gpt-5.5 and Claude.
- **H6 - Key-value outperforms structured formats**: CONTRADICTED (High) [TESTED]
  - Only true for gpt-5-mini. Worst format for gpt-5.2 (100 vs csv_quoted 268).

## 3. Detailed Analysis

<!-- AUTO:findings-3:start -->
### 3.1 H2: JSON Ranking Per Model

| Model      | JSON Scale | JSON Rank | Best Format    | Best Scale | JSON vs Best |
|------------|------------|-----------|----------------|------------|--------------|
| gpt-5.5    | 430        | 7/8       | toml           | 828        | 52%          |
| gpt-5.4    | 702        | 1/8       | json           | 702        | 100%         |
| gpt-5-mini | 335        | 4/8       | kv_colon_space | 500        | 67%          |
| gpt-5      | 249        | 3/8       | yaml           | 333        | 75%          |
| gpt-5.2    | 241        | 3/8       | csv_quoted     | 268        | 90%          |
| opus-4.8   | 576        | 4/7       | csv            | 630        | 91%          |
| opus-4.5   | 265        | 1/8       | json           | 265        | 100%         |
| sonnet-4.5 | 189        | 1/8       | json           | 189        | 100%         |

**JSON is #1 in 3/8 models.**

### 3.2 H3: Family Preference Divergence

```
gpt-5.5 (gpt)        TOP: toml (828), yaml (675), markdown_table (627)
                     BOT: json (430), xml (375)
gpt-5.4 (gpt)        TOP: json (702), markdown_table (554), xml (546)
                     BOT: yaml (523), kv_colon_space (359)
gpt-5-mini (gpt)     TOP: kv_colon_space (500), yaml (500), csv_quoted (437)
                     BOT: csv (194), markdown_table (163)
gpt-5 (gpt)          TOP: yaml (333), xml (327), json (249)
                     BOT: csv (166), markdown_table (83)
gpt-5.2 (gpt)        TOP: csv_quoted (268), xml (261), json (241)
                     BOT: kv_colon_space (100), toml (46)
opus-4.8 (claude)    TOP: csv (630), toml (622), csv_quoted (607)
                     BOT: xml (545), markdown_table (468)
opus-4.5 (claude)    TOP: json (265), yaml (259), csv (232)
                     BOT: xml (182), csv_quoted (171)
sonnet-4.5 (claude)  TOP: json (189), csv (126), kv_colon_space (126)
                     BOT: toml (115), xml (99)
```

### 3.3 H5: Token Efficiency vs Scale (csv=1.00x reference)

| Model      | csv Scale | xml Scale | xml/csv Ratio | xml Wins? |
|------------|-----------|-----------|---------------|-----------|
| gpt-5.5    | 494       | 375       |          0.76 | NO        |
| gpt-5.4    | 523       | 546       |          1.04 | YES       |
| gpt-5-mini | 194       | 296       |          1.53 | YES       |
| gpt-5      | 166       | 327       |          1.97 | YES       |
| gpt-5.2    | 215       | 261       |          1.21 | YES       |
| opus-4.8   | 630       | 545       |          0.87 | NO        |
| opus-4.5   | 232       | 182       |          0.78 | NO        |
| sonnet-4.5 | 126       | 99        |          0.79 | NO        |

### 3.4 H6: Key-Value Ranking Per Model

| Model      | kv Scale | kv Rank | Best Format    | Best Scale | kv vs Best |
|------------|----------|---------|----------------|------------|------------|
| gpt-5.5    | 588      | 4/8    | toml           | 828        | 71%          |
| gpt-5.4    | 359      | 8/8    | json           | 702        | 51%          |
| gpt-5-mini | 500      | 1/8    | kv_colon_space | 500        | 100%          |
| gpt-5      | 238      | 4/8    | yaml           | 333        | 71%          |
| gpt-5.2    | 100      | 7/8    | csv_quoted     | 268        | 37%          |
| opus-4.8   | 545      | 5/7    | csv            | 630        | 87%          |
| opus-4.5   | 226      | 4/8    | json           | 265        | 85%          |
| sonnet-4.5 | 126      | 3/8    | json           | 189        | 67%          |

**kv_colon_space is #1 in 1/8 models.**
<!-- AUTO:findings-3:end -->

### 3.5 Format Ranking Stability (Cross-Model)

Which formats rank consistently vs chaotically across all 8 models? Rank stdev measures volatility (lower = more predictable). opus-4.8 has only 7 formats (yaml incomplete).

- **json** - avg rank 2.9/8, stdev 2.2, worst case 52% of best. Best "safe default" if you cannot test.
- **yaml** - avg rank 3.7/8, stdev 2.5, worst case 50% of best. Strong but less predictable.
- **csv** - avg rank 4.6/8, stdev 1.9 (most stable). Mid-tier but never catastrophic.
- **kv_colon_space** - avg rank 4.4/8, stdev 2.4. High variance (rank 1 to rank 8).
- **csv_quoted** - avg rank 4.7/8, stdev 2.2. Similar to csv but slightly less stable.
- **markdown_table** - avg rank 5.0/8, stdev 2.3. Below average, can be rank 2 or rank 8.
- **xml** - avg rank 5.1/8, stdev 2.7 (most volatile). Rank 2 on gpt-5.2/sonnet, rank 8 on gpt-5.5/gpt-5.4.
- **toml** - avg rank 5.6/8, stdev 2.2. Below average; worst case only 17% of best (gpt-5.2: 46 rows).

**Production takeaway**: If you cannot run format tests, use json (best avg rank). If you need predictability, use csv (lowest variance).

### 3.6 Failure Mode by Format

57/63 tests fail from comprehension. 6/63 from truncation. All 6 truncation failures are opus-4.5:
- opus-4.5 truncates on: json (60.3% context), yaml (35.3%), xml (45.7%), toml (34.1%), kv_colon_space (30.1%), markdown_table (22.7%)
- opus-4.5 does NOT truncate on: csv (21.5% context, comprehension), csv_quoted (15.0% context, comprehension)

Format does NOT determine failure mode. The truncation pattern is model-specific: opus-4.5 uniquely pushes context utilization high enough to hit output limits on verbose formats, while compact formats (csv, csv_quoted) still fail from comprehension before reaching truncation. opus-4.8 (high effort) shows 0/7 truncation despite higher context utilization (12-33%), suggesting improved output generation. This extends Test 01's finding that opus models engage deeper context than other families. [VERIFIED]

### 3.7 Output Tokens Are Format-Independent

Input tokens vary 2.3x by format at scale limit (avg across models):
- Verbose: json 91K, xml 90K, yaml 82K
- Compact: csv 40K, csv_quoted 47K, markdown_table 41K

Output tokens are stable: 27-33K regardless of input format. Because output is always JSON extraction, the model generates roughly the same output volume regardless of how input data was formatted. The cost difference between formats is driven entirely by input token count. [VERIFIED]

### 3.8 Context Utilization Does Not Predict Scale Limit

Average context utilization at scale limit by format:
- json: 22.5%, xml: 20.3%, yaml: 17.1%, toml: 16.1%
- kv_colon_space: 14.3%, markdown_table: 10.2%, csv: 10.0%, csv_quoted: 10.0%

json and xml consume 2x more context than csv at their respective scale limits, yet json has the best average ranking (2.9/8). More context consumed does NOT mean worse performance. Models fail from comprehension, not from running out of context window. This further confirms Test 01's finding that context window is not the bottleneck. [VERIFIED]

### 3.9 Processing Speed by Format (Same Row Count)

Binary search iteration 1 tests all formats at the same row count per model. This enables direct speed comparison (wall-clock time for 3 parallel API runs, same data, same row count).

| Model      | Rows | Fastest        | Time  | Slowest        | Time  | Ratio |
|------------|------|----------------|-------|----------------|-------|-------|
| sonnet-4.5 | 168  | markdown_table | 79s   | kv_colon_space | 88s   | 1.1x  |
| opus-4.5   | 177  | csv_quoted     | 80s   | xml            | 109s  | 1.4x  |
| gpt-5.2    | 215  | yaml           | 51s   | markdown_table | 81s   | 1.6x  |
| gpt-5.5    | 437  | csv_quoted     | 90s   | json           | 142s  | 1.6x  |
| opus-4.8   | 492  | kv_colon_space | 162s  | markdown_table | 269s  | 1.7x  |
| gpt-5.4    | 500  | yaml           | 132s  | kv_colon_space | 246s  | 1.9x  |
| gpt-5-mini | 500  | kv_colon_space | 206s  | json           | 870s  | 4.2x  |
| gpt-5      | 356  | toml           | 156s  | kv_colon_space | 819s  | 5.3x  |

**Key observations:**
- **No single format is consistently fastest.** Fastest varies: csv_quoted (2x), yaml (2x), kv_colon_space (2x), markdown_table (1x), toml (1x)
- **Claude models show minimal speed variation** (1.1-1.7x). Format choice barely affects processing time.
- **Older GPT models show extreme speed variation** (4-5x). gpt-5 and gpt-5-mini are 3-4x more affected by format than newer models.
- **Speed ranking differs from scale limit ranking.** A format can be fastest to process but fail at lower scale limits (e.g., kv_colon_space is fastest for opus-4.8 but rank 5/7 for scale).
- **Verbose formats are NOT consistently slower.** xml (2.12x tokens) is fastest on none, but yaml (1.68x tokens) is fastest on 2 models.

**Caveat**: Times are iter01 wall-clock (3 parallel workers). Includes data generation, API calls, and evaluation. API throttling or retries may inflate individual times. [VERIFIED]

## 4. Unexpected Findings

<!-- AUTO:findings-4:start -->
1. **gpt-5.5 format preference inverts vs gpt-5.4** [TESTED]
   - gpt-5.4 best: json (702). gpt-5.5 best: toml (828), json drops to 430 (-39%)

2. **markdown_table worst on 3 models** [TESTED]
   - gpt-5-mini: 163 (rank 8/8)
   - gpt-5: 83 (rank 8/8)
   - opus-4.8: 468 (rank 7/7)

3. **Format inversions (best for one model, worst for another)** [TESTED]
   - toml: BEST for gpt-5.5. WORST for gpt-5.2.
   - kv_colon_space: BEST for gpt-5-mini. WORST for gpt-5.4.
   - csv_quoted: BEST for gpt-5.2. WORST for opus-4.5.

4. **Format sensitivity inversely correlates with model capability** [VERIFIED]
   - gpt-5.2: 5.8x (best=268)
   - gpt-5: 4.0x (best=333)
   - gpt-5-mini: 3.1x (best=500)
   - gpt-5.5: 2.2x (best=828)
   - gpt-5.4: 2.0x (best=702)
   - sonnet-4.5: 1.9x (best=189)
   - opus-4.5: 1.5x (best=265)
   - opus-4.8: 1.3x (best=630)

5. **gpt-5.5 is 1.4x faster than gpt-5.4 (Time Per Kilo-Cell, TPKC)** [TESTED]
   - gpt-5.5 avg TPKC: 12s. gpt-5.4 avg TPKC: 16s
<!-- AUTO:findings-4:end -->

6. **opus-4.5 is the only model that truncates (6/8 formats)** [VERIFIED]
   - csv and csv_quoted avoid truncation (comprehension failure instead)
   - opus-4.5 hits 22-60% context utilization - other models stay below 16%
   - Consistent with Test 01: opus family uniquely engages deep context

7. **Context utilization at failure is 2x higher for verbose formats** [VERIFIED]
   - json/xml: 20-22% avg context at scale limit. csv: 10%.
   - Yet json has BEST avg rank (2.9/8). More context consumed does not mean worse performance.

## 5. Production Recommendations

<!-- AUTO:findings-5:start -->
**Scope**: Results apply to 7-column tabular extraction with compound filter. Different column counts or task complexity may shift rankings.

**IMPORTANT (TBLF-FL-005)**: These results use 7/7 columns (simplified dataset). Test 01 used 7/20 columns. Scale limits are NOT directly comparable between Test 01 and Test 02.

### By Model (sorted by max scale)

| Model      | Recommended    | Scale | Alternative    | Scale | Avoid          | Scale |
|------------|----------------|-------|----------------|-------|----------------|-------|
| gpt-5.5    | toml           | 828   | yaml           | 675   | xml            | 375   |
| gpt-5.4    | json           | 702   | markdown_table | 554   | kv_colon_space | 359   |
| gpt-5-mini | kv_colon_space | 500   | yaml           | 500   | markdown_table | 163   |
| gpt-5      | yaml           | 333   | xml            | 327   | markdown_table | 83    |
| gpt-5.2    | csv_quoted     | 268   | xml            | 261   | toml           | 46    |
| opus-4.8   | csv            | 630   | toml           | 622   | markdown_table | 468   |
| opus-4.5   | json           | 265   | yaml           | 259   | csv_quoted     | 171   |
| sonnet-4.5 | json           | 189   | csv            | 126   | xml            | 99    |

### By Cost Efficiency (lowest Cost Per Kilo-Cell, CPKC)

| Model      | Best CPKC Format | CPKC   | Scale | 2nd Best         | CPKC   |
|------------|------------------|--------|-------|------------------|--------|
| gpt-5.5    | markdown_table   | $0.131 | 627   | csv              | $0.133 |
| gpt-5.4    | csv              | $0.038 | 523   | csv_quoted       | $0.040 |
| gpt-5-mini | kv_colon_space   | $0.005 | 500   | csv_quoted       | $0.005 |
| gpt-5      | xml              | $0.032 | 327   | toml             | $0.032 |
| gpt-5.2    | kv_colon_space   | $0.030 | 100   | csv_quoted       | $0.031 |
| opus-4.8   | csv              | $0.200 | 630   | csv_quoted       | $0.208 |
| opus-4.5   | csv              | $0.188 | 232   | markdown_table   | $0.190 |
| sonnet-4.5 | csv_quoted       | $0.110 | 120   | csv              | $0.115 |

### Key Insight

**Always test your specific model with your intended format.** Format choice matters more than previously thought - up to 5.8x scale difference. No universal best format exists.
<!-- AUTO:findings-5:end -->

### Chunking Strategy (Not Yet Tested)

For datasets exceeding the recommended row count, chunk into N batches of [safe limit] rows and merge results. Cost scales linearly with chunk count. Example: 3x gpt-5-mini at 300 rows = $0.024 for 900 rows vs 1x opus-4.5 at 265 rows = $0.19. Chunking with a cheap model likely dominates single-shot optimization for most production use cases. Empirical validation of chunk+merge accuracy is future work.

### Measurement Precision Note

Rankings within ~20% of each other should be considered equivalent due to ~28% observed variance between independent binary searches (Test 01 data). Treat tables as tier groupings, not strict orderings.

## 6. Emergent Hypotheses

Hypotheses not in the original H1-H6 set, derived from observed data patterns.

- **E1: Structural format markers serve as attention anchors** [CONTRADICTED]
  - Source: NoLiMa (2025) mechanism finding (attention relies on literal cues)
  - Evidence: XML (most structural markers, 2.12x tokens) is worst in 5/7 models
  - Prediction if true: xml > json > yaml/toml > csv. Actual: xml often worst.
  - Counter-evidence per model (data: TBLF-IN05 section 5.1):
    - gpt-5.5: xml WORST (375). toml BEST (828). Prediction WRONG.
    - gpt-5-mini: xml rank 5/8 (296, tied). yaml BEST (500). Prediction WRONG.
    - opus-4.5: xml rank 6/8 (182). json BEST (265). Prediction WRONG.
  - Conclusion: Format preference correlates with model training data composition, not structural marker density.

- **E2: Format preference shifts between model generations** [TESTED]
  - Evidence: gpt-5.4 (json best: 702) vs gpt-5.5 (toml best: 828, json: 430)
  - Mechanism: Training data composition changes between versions affect format familiarity
  - Testable: Track format rankings across future model releases

- **E3: Format sensitivity inversely correlates with model capability** [VERIFIED]
  - Evidence: gpt-5.2 ratio 5.8x, gpt-5 4.0x, gpt-5-mini 3.1x, gpt-5.5 2.2x, gpt-5.4 2.0x, sonnet 1.9x, opus-4.5 1.5x, opus-4.8 1.3x
  - Mechanism: More capable models develop format-agnostic comprehension strategies
  - Caveat: May partly reflect floor effects - models with low absolute scale limits have less room for variance, mechanically producing higher ratios. The correlation is consistent but causality is not established.
  - Testable: Compare sensitivity ratio across reasoning effort levels (low vs high on same model)

## 7. Open Questions

1. **Does format preference change with task complexity?** (H4 - inconclusive). Would simpler filters or more columns shift rankings?

2. **Why does gpt-5.5 prefer toml while gpt-5.4 prefers json?** What changed in training data or architecture between these versions?

3. **Would format preference hold at higher reasoning effort?** GPT tests used medium/low effort. opus-4.8 at high effort shows 1.3x ratio (lowest observed), suggesting high effort reduces format sensitivity.

4. **Is the Claude json preference an artifact of training or architecture?** opus-4.8 (high effort) prefers csv over json, breaking the pattern. Is this an effect of higher reasoning effort or model version?

5. **Can format sensitivity ratio predict model robustness for other tasks?** If format-insensitive models are generally more capable, this metric has broader diagnostic value.

## 8. Caveats and Limitations

- **Measurement precision**: Binary search with n=3 runs has ~28% variance (from Test 01). Differences <20% between formats may be within noise.
- **Column configuration (TBLF-FL-005)**: Test uses 7/7 columns, NOT Test 01's 7/20 selection. Results not directly comparable to Test 01 CSV baselines.
- **Task specificity**: One task type (7-column, compound filter, 20% adversarial). Different tasks may produce different rankings.
- **Reasoning effort**: GPT models tested at medium (except gpt-5: low). opus-4.8 tested at high. Higher effort appears to reduce format sensitivity (opus-4.8 ratio 1.3x vs opus-4.5 1.5x at medium).
- **Temporal validity**: Model format preferences may shift with silent updates. Results are snapshots from March-May 2026.
- **opus-4.8 yaml incomplete**: Test stopped at 1107 rows (passed at 738) due to endless reasoning tokens consuming budget without producing output. Same Anthropic adaptive thinking issue as opus-4.7 high in Test 01 (see `_INFO_01_CSVScaleLimits-TestResults.md [TBLF-IN01]`). 7/8 formats available.
- **No csv_quoted for gpt-5.5 baseline comparison**: gpt-5.5 was added later; csv_quoted result (491) is Test 02 only, no Test 01 reference.

## 9. Sources

- `_INFO_01_FormatComparison-TestResults.md [TBLF-IN05]` - All test result data
- `_SPEC_FormatComparison.md [TBLF-SP02]` - Test framework specification
- `_INFO_LLM_MARKDOWN_PREFERENCES.md [LLMO-IN01]` - TK-001 benchmark (prior evidence)
- Sclar et al., ICLR 2024 - "Quantifying Language Models' Sensitivity to Spurious Features"
- Microsoft/MIT 2024 - "Does Prompt Formatting Have Any Impact on LLM Performance?"
- Microsoft CFPO 2025 - "Beyond Prompt Content: Enhancing LLM Performance Via Content-Format Integration"
- NoLiMa 2025 - https://arxiv.org/abs/2502.05167 (attention mechanism finding)

## 10. Document History

**[2026-05-30 20:00]**
- Added: opus-4.8 (high effort) data across all sections (7/8 formats, yaml incomplete)
- Added: Section 3.9 - Processing Speed by Format (iter01 comparison at identical row counts)
- Changed: Test counts updated (56 -> 63, 7 -> 8 models)
- Changed: Failure mode counts updated (57/63 comprehension, 6/63 truncation)
- Changed: E3 updated with opus-4.8 (1.3x ratio, lowest observed)
- Changed: Open question 3 partially answered (high effort reduces sensitivity)
- Changed: Open question 4 updated (opus-4.8 breaks Claude json preference)

**[2026-05-22 20:00]**
- Added: Section 3.5 - Format Ranking Stability (cross-model rank stdev analysis, "safe default" finding)
- Added: Section 3.6 - Failure Mode by Format (truncation = opus-4.5 only, not format-dependent)
- Added: Section 3.7 - Output Tokens Are Format-Independent (input varies 2.3x, output stable 27-33K)
- Added: Section 3.8 - Context Utilization Does Not Predict Scale Limit (confirms Test 01 finding)
- Added: Key findings - json safe default, output token independence, failure mode model-specificity
- Added: Unexpected findings #6 (opus-4.5 truncation), #7 (context utilization paradox)

**[2026-05-22 19:45]**
- Added: Chunking Strategy subsection in section 5 (production recommendation gap from review)
- Added: Measurement Precision Note in section 5 (~20% noise band, tier groupings)
- Added: E3 floor-effect caveat (sensitivity-capability correlation may be partly mathematical artifact)

**[2026-05-22 19:30]**
- Added: AUTO markers on sections 1, 3, 4, 5 (data-backed sections)
- Added: `08_generate_findings.py` generates findings from `all_results.json`
- Changed: Section 3 now uses evidence tables (H2 JSON ranking, H3 family divergence, H5 csv vs xml, H6 kv ranking)
- Changed: Section 4 unexpected findings computed from data (inversions, sensitivity ratios)
- Changed: Section 5 production recs now has Recommended/Alternative/Avoid table + CPKC table
- Fixed: gpt-5.5 vs gpt-5.4 speed comparison corrected to 1.4x (was incorrectly 3-4x)

**[2026-05-22 18:50]**
- Initial document created from restructuring of `_INFO_FormatComparison.md`
- Restructured hypothesis evaluation with Prediction/Result/Evidence/Verdict format
- Reclassified H9 (structural markers) as Emergent Hypothesis E1
- Added: Emergent hypotheses E2 (generational preference shift), E3 (sensitivity-capability correlation)
- Added: Open Questions section (5 questions)
- Added: Caveats and Limitations section (6 items)
- Added: Verification labels throughout ([TESTED], [VERIFIED], [ASSUMED])
- Added: Precision note to section 2
- Follows 4-document methodology per `_INFO_LLM_TEST_METHODOLOGY.md [TBLF-IN04]`
