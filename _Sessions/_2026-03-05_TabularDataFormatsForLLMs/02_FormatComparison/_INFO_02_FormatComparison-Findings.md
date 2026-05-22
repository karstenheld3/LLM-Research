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

Derived from 56/56 completed tests. Data in `_INFO_01_FormatComparison-TestResults.md [TBLF-IN05]` section 5.

- **Format preferences differ dramatically by model family** [TESTED]
  - GPT models prefer yaml/xml/toml; Claude models prefer json
  - Best format for one family can be worst for another (up to 5.8x difference)
- **Token efficiency does NOT predict scale limits** [TESTED]
  - xml (2.12x tokens) outperforms csv (1.00x) on 4/5 older GPT models by 1.2-2.0x
  - Reversal on gpt-5.5 and Claude: csv beats xml by 1.3x
- **Format impact is massive - up to 5.8x within a single model** [TESTED]
  - gpt-5.2: csv_quoted (268) vs toml (46) = 5.8x
  - gpt-5: yaml (333) vs markdown_table (83) = 4.0x
- **No universal "best format" exists** [TESTED]
  - gpt-5.5: toml best. gpt-5.4: json best. gpt-5-mini: yaml/kv best. Claude: json best.
- **Format preference shifts between model generations** [TESTED]
  - gpt-5.4 prefers json (702). gpt-5.5 prefers toml (828), json drops to 430 (-39%)

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

### 3.1 H2: JSON Not Universally Optimal

**Prediction**: Based on Microsoft/MIT 2024, JSON may not be optimal despite providing clear structure.

**Result**: Model-dependent. JSON is optimal for Claude but mid-tier for older GPT models. [TESTED]

**Evidence** (data: TBLF-IN05 section 5.3):
- gpt-5.5: json = 430 (rank 7/8, 52% of best)
- gpt-5.4: json = 702 (rank 1/8, best format)
- gpt-5-mini: json = 335 (rank 4/8, 67% of best)
- gpt-5: json = 249 (rank 3/8, 75% of best)
- gpt-5.2: json = 241 (rank 3/8, 90% of best)
- opus-4.5: json = 265 (rank 1/8, best format)
- sonnet-4.5: json = 189 (rank 1/8, best format)

**Verdict**: MIXED. JSON is best for Claude models and gpt-5.4, but mid-tier for other GPT models. No single format is universally optimal. [TESTED]

### 3.2 H3: Model Family Format Preferences Differ

**Prediction**: Based on Microsoft/MIT 2024 (IoU < 0.2 between GPT-3.5 and GPT-4 preferences).

**Result**: CONFIRMED. GPT and Claude have inverted format preferences. [TESTED]

**Evidence** (data: TBLF-IN05 section 5.3):
```
GPT top formats:     yaml, toml, xml (structured, verbose)
Claude top formats:  json (structured, moderate verbosity)
GPT worst formats:   markdown_table (except gpt-5.4)
Claude worst format: xml, csv_quoted
```

Key inversions:
- xml: Best for gpt-5 (rank 2) and gpt-5.2 (rank 2). Worst for Claude (rank 7-8).
- json: Best for Claude (rank 1). Rank 7 on gpt-5.5.
- csv_quoted: Best for gpt-5.2 (rank 1). Worst for opus-4.5 (rank 8).

**Verdict**: CONFIRMED. Format preferences are model-family specific. Rankings invert between GPT and Claude. Even within GPT, preferences shift across generations (gpt-5.4 json vs gpt-5.5 toml). [TESTED]

### 3.3 H5: Token Efficiency Does Not Predict Scale

**Prediction**: If token efficiency determines scale, csv (1.00x) should outperform xml (2.12x) by ~2x.

**Result**: CONTRADICTED for older GPT models. Token-inefficient xml outperforms csv. [TESTED]

**Evidence** (data: TBLF-IN05 section 5.4):
- gpt-5-mini: csv (194) < xml (296) - xml 1.5x better despite 2.12x more tokens
- gpt-5: csv (166) < xml (327) - xml 2.0x better
- gpt-5.2: csv (215) < xml (261) - xml 1.2x better
- gpt-5.4: csv (523) < xml (546) - xml 1.04x better
- gpt-5.5: csv (494) > xml (375) - REVERSAL: csv 1.3x better on newest model
- opus-4.5: csv (232) > xml (182) - csv 1.3x better
- sonnet-4.5: csv (126) > xml (99) - csv 1.3x better

**Insight**: Structure aids comprehension more than compactness for older GPT models. But gpt-5.5 and Claude models reverse this pattern, suggesting newer/Claude models handle compact formats better.

**Verdict**: CONTRADICTED. Token efficiency does not predict scale. Structural clarity matters more for older GPT; newer models and Claude handle compact formats better. [TESTED]

### 3.4 H6: Key-Value Does Not Universally Outperform

**Prediction**: Based on TK-001 benchmark where key-value ranked #1-#2 at 300 records.

**Result**: CONTRADICTED. TK-001 finding was specific to gpt-5-mini at 300 records. [TESTED]

**Evidence** (data: TBLF-IN05 section 5.3):
- gpt-5-mini: kv (500) = BEST (tied with yaml). Confirms TK-001.
- gpt-5.5: kv (588) rank 4/8 - mid-tier
- gpt-5.4: kv (359) = WORST format
- gpt-5: kv (238) rank 4/8 - below yaml (333) and xml (327)
- gpt-5.2: kv (100) rank 7/8 - near worst
- opus-4.5: kv (226) rank 4/8
- sonnet-4.5: kv (126) rank 2-4/8 (tied with csv, markdown)

**Verdict**: CONTRADICTED. Key-value only outperforms for gpt-5-mini. Can be the worst format for other models (gpt-5.4: 359 vs json 702 = 51%). [TESTED]

## 4. Unexpected Findings

1. **gpt-5.5 format preference completely inverts vs gpt-5.4** [TESTED]
   - gpt-5.4 best: json (702). gpt-5.5 best: toml (828), json drops to 430 (-39%)
   - Format preference instability across a single generation gap

2. **markdown_table consistently worst on older GPT** [TESTED]
   - gpt-5-mini: 163 (rank 8/8). gpt-5: 83 (rank 8/8).
   - Despite being a common LLM output format, it hurts comprehension at scale

3. **csv_quoted best for gpt-5.2 but worst for opus-4.5** [TESTED]
   - gpt-5.2: 268 (rank 1/8). opus-4.5: 171 (rank 8/8).
   - Maximum inversion: format that's best for one model is literally worst for another

4. **Format sensitivity correlates inversely with model capability** [VERIFIED]
   - Strongest: gpt-5.2 (5.8x ratio). Weakest: opus-4.5 (1.5x ratio)
   - More capable models are more robust to format changes

5. **gpt-5.5 is 3-4x faster per request than gpt-5.4** [TESTED]
   - TPKC: 10-16s (gpt-5.5) vs 35-52s (gpt-5.4) across all formats
   - Speed improvement alongside format preference shift

## 5. Production Recommendations

**Scope**: Results apply to 7-column tabular extraction with compound filter. Different column counts or task complexity may shift rankings.

**IMPORTANT (TBLF-FL-005)**: These results use 7/7 columns (simplified dataset). Test 01 used 7/20 columns. Scale limits are NOT directly comparable between Test 01 and Test 02.

### By Model Family

**GPT Models (newer - gpt-5.4, gpt-5.5):**
- gpt-5.5: Use **toml** (828 rows) or **yaml** (675 rows)
- gpt-5.4: Use **json** (702 rows)
- Avoid generalizing preferences across generations

**GPT Models (older - gpt-5-mini, gpt-5, gpt-5.2):**
- Use **yaml** for maximum scale (gpt-5-mini: 500, gpt-5: 333)
- Use **csv_quoted** for gpt-5.2 specifically (268 rows)
- Avoid markdown_table (consistently worst: 83-163 rows)

**Claude Models:**
- Use **json** for maximum scale (opus: 265, sonnet: 189)
- csv is good second choice (opus: 232, sonnet: 126)
- Avoid xml (worst for both: opus 182, sonnet 99)

### Key Insight

**Always test your specific model with your intended format.** Format choice matters more than previously thought - up to 5.8x scale difference. No universal best format exists.

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
  - Evidence: gpt-5.2 ratio 5.8x, gpt-5 4.0x, gpt-5-mini 3.1x, gpt-5.5 2.2x, gpt-5.4 2.0x, sonnet 1.9x, opus 1.5x
  - Mechanism: More capable models develop format-agnostic comprehension strategies
  - Testable: Compare sensitivity ratio across reasoning effort levels (low vs high on same model)

## 7. Open Questions

1. **Does format preference change with task complexity?** (H4 - inconclusive). Would simpler filters or more columns shift rankings?

2. **Why does gpt-5.5 prefer toml while gpt-5.4 prefers json?** What changed in training data or architecture between these versions?

3. **Would format preference hold at higher reasoning effort?** All GPT tests used medium/low effort. Would high effort reduce format sensitivity?

4. **Is the Claude json preference an artifact of training or architecture?** Would other Anthropic models (haiku, opus-4.6 high) show the same preference?

5. **Can format sensitivity ratio predict model robustness for other tasks?** If format-insensitive models are generally more capable, this metric has broader diagnostic value.

## 8. Caveats and Limitations

- **Measurement precision**: Binary search with n=3 runs has ~28% variance (from Test 01). Differences <20% between formats may be within noise.
- **Column configuration (TBLF-FL-005)**: Test uses 7/7 columns, NOT Test 01's 7/20 selection. Results not directly comparable to Test 01 CSV baselines.
- **Task specificity**: One task type (7-column, compound filter, 20% adversarial). Different tasks may produce different rankings.
- **Reasoning effort**: GPT models tested at medium (except gpt-5: low). Higher effort may change format sensitivity.
- **Temporal validity**: Model format preferences may shift with silent updates. Results are snapshots from March-May 2026.
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
