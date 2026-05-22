<DevSystem MarkdownTablesAllowed=true />

# INFO: CSV Scale Limits - Findings

**Doc ID**: TBLF-IN03
**Goal**: Derive findings from test results, map to hypotheses, develop emergent hypotheses
**Timeline**: Created 2026-05-22

**Depends on:**
- `_INFO_01_CSVScaleLimits-TestResults.md [TBLF-IN02]` for all test result data

**Does not depend on:**
- `_TEST_CSVScaleLimits.md [TBLF-TP01]` (execution procedures only, no results)

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

Derived from 19/19 completed tests. Data in `_INFO_01_CSVScaleLimits-TestResults.md [TBLF-IN02]` section 5.

- **Claude opus-4.6 high = new confirmed leader**
  - 667 rows at 55.4% context utilization
- **adaptive_thinking at medium effort is catastrophic**
  - opus-4.6 (6 rows), opus-4.7 (12 rows) - worse than gpt-4o
- **Effort multiplier extreme on Claude Opus 4.6**
  - medium (6) to high (667) = 111x improvement
- **Reasoning models massively outperform temperature models**
  - gpt-5-mini (500 rows) vs gpt-4o-mini (6 rows) = 83x
- **Scale limits vary 210x+ across models**
  - Best: opus-4.7 high (843+) vs Worst: gpt-4o (4)
- **Comprehension is primary failure mode, not truncation**
  - 15/18 tests failed due to comprehension errors
- **Context window is NOT the bottleneck**
  - Most failures occur at <10% context utilization

## 2. Hypothesis Verdicts

Prior evidence from TK-001 benchmark (`_INFO_LLM_MARKDOWN_PREFERENCES.md [LLMO-IN01]`):
- gpt-5-mini reliable at 300 records, unreliable at 600 (43% failure rate)
- At 600 records: bimodal behavior (near-perfect OR complete failure)
- v5 failures attributed to "output token limits causing truncation"
- Quoted CSV ranked #3 of 10 formats at 300 records

- **H1 - Scale limit 300-600 rows**: SUPPORTED (High)
  - gpt-5-mini medium = 500 rows (re-run; original 389 also in range)
- **H2 - Bimodal failure (cliff)**: PARTIALLY SUPPORTED (Medium)
  - Reasoning: cliff (100% to 0%). Temperature: gradual slope
- **H3 - Truncation > comprehension**: NOT SUPPORTED (High)
  - Comprehension = 15/18 tests. Truncation: gpt-5 high, claude-opus-4.5
- **H4 - Higher effort = higher limit**: SUPPORTED (High)
  - gpt-5-mini: 65 to 500 (+669%). gpt-5: 356 to 492 (+38%)
- **H5 - Reasoning > temperature**: STRONGLY SUPPORTED (Very High)
  - Mini: 83x better. Full: 89x better
- **H6 - CSV best format**: Deferred
  - Test 02 (future)

## 3. Detailed Analysis

### 3.1 H1: Scale Limit 300-600 Rows

**Prediction**: Based on TK-001 prior data showing 100% reliability at 300 rows and 43% failure at 600 rows.

**Result**: gpt-5-mini medium achieved 500 rows scale limit (re-run; original run found 389).

**Evidence** (data: TBLF-IN02 section 5.2):
- Passed at 500 rows (Precision=1.00, Recall=1.00, 3/3 runs)
- Failed at 507 rows (Precision=1.00, Recall=0.9733 - missed records)
- Binary search converged with bounds [500, 507]

**Verdict**: SUPPORTED. Scale limit falls within predicted 300-600 range (closer to upper bound on re-run). [TESTED]

### 3.2 H2: Bimodal Failure Pattern

**Prediction**: At scale limit, runs either succeed completely or fail significantly (cliff, not slope).

**Result**: Model-dependent behavior observed.

**Reasoning models (gpt-5 family)** - cliff behavior (data: TBLF-IN02 section 8.5):
- gpt-5-mini medium: 500 rows = 100% accuracy, 507 rows = partial extraction failure
- Transition from perfect to degraded within 7 rows (<2% range)

**Temperature models (gpt-4o family)** - gradual slope (data: TBLF-IN02 section 8.5):
- gpt-4o at 300 rows: Precision=0.47, Recall=0.71
- gpt-4o at 75 rows: Precision=0.65, Recall=0.63
- Gradual degradation across scale range

**Verdict**: PARTIALLY SUPPORTED. Reasoning models exhibit cliff behavior; temperature models degrade gradually. [TESTED]

### 3.3 H3: Truncation vs Comprehension

**Prediction**: Based on TK-001 attribution, truncation expected as primary failure mode.

**Result**: Comprehension is primary failure mode (15/17 tests with clear failure modes). [VERIFIED]

**Key Insight**: Context windows are NOT the bottleneck. Models fail at <5-16% context utilization on average (data: TBLF-IN02 section 6.1). Exception: claude-opus-4.6 high reaches 55.4% - the only model to use >30% of its context before failure. [VERIFIED]

**Verdict**: NOT SUPPORTED. TK-001 attribution was incorrect. Comprehension (attention degradation) is the true failure mode (15/17 completed tests; 2 truncation). [TESTED]

### 3.4 H4: Effort Level Impact

**Prediction**: Higher reasoning effort extends scale limit.

**Result**: DRAMATIC improvement with higher effort. [VERIFIED]

Calculations (verified in TBLF-IN02 section 9):
- gpt-5-mini: (500 - 65) / 65 = 669%, 500 / 65 = 7.7x [VERIFIED]
- gpt-5: (492 - 356) / 356 = 38%, (450 - 356) / 356 = 26% [VERIFIED]

Key insights:
1. **gpt-5-mini shows dramatic improvement** (7.7x from low to medium) while **gpt-5 shows moderate improvement** (38% from low to high)
2. **Diminishing returns at higher tiers**: gpt-5 medium to high adds only 42 rows (+9%) but costs 6x more time
3. **Cost efficiency varies**: gpt-5 low ($0.44) delivers 356 rows; gpt-5 high ($2.74) delivers only 136 more rows
4. **Claude Opus effort sensitivity is extreme**: opus-4.6 = 111x (6 to 667), opus-4.7 = 70x+ (12 to 843+). Dwarfs OpenAI models.

**Verdict**: SUPPORTED. Higher effort increases scale limit. Effect is extreme on Claude Opus: 111x on 4.6 (dwarfing gpt-5-mini's 7.7x and gpt-5's 1.4x). [TESTED]

### 3.5 H5: Reasoning vs Temperature Models

**Prediction**: Reasoning models (gpt-5) outperform temperature models (gpt-4o).

**Result**: MASSIVE performance difference. [VERIFIED]

Calculations (data: TBLF-IN02 section 8.1, 8.2):
- Mini tier: 500 / 6 = 83x
- Full tier: 356 / 4 = 89x

**Insight**: Temperature-based models are fundamentally unsuited for tabular extraction tasks at any meaningful scale. The reasoning mechanism appears essential for maintaining attention across structured data.

**Caveat**: These are different model architectures, not isolated mechanism comparisons. However, the 83-89x difference is too large to attribute to architecture alone.

**Verdict**: STRONGLY SUPPORTED. Reasoning models dramatically outperform temperature models for tabular extraction. [TESTED]

## 4. Unexpected Findings

1. **Claude adaptive_thinking at medium effort is catastrophically broken** [TESTED]
   - opus-4.6 regresses from 177 (opus-4.5 thinking) to 6 rows
   - opus-4.7 achieves only 12 rows
   - Both produce false positives (precision <1.0) unlike older models which only missed records
   - Suggests adaptive_thinking medium fundamentally changes how these models approach structured data

2. **Claude opus-4.6 high effort = highest confirmed result** [TESTED]
   - 667 rows with 55.4% context utilization
   - Only model to use >30% of context before failure
   - Suggests high-effort adaptive_thinking enables genuine deep comprehension rather than surface-level pattern matching

3. **111x effort multiplier on Claude Opus 4.6** [TESTED]
   - medium (6) to high (667)
   - Far exceeds gpt-5-mini's 7.7x and gpt-5's 1.4x multipliers
   - The adaptive_thinking mechanism appears binary - nearly useless at medium, exceptional at high

4. **gpt-5.2 underperforms gpt-5** [VERIFIED]
   - Scale limit 215 vs 356 (gpt-5 low). Newer is not always better for specific tasks.

5. **gpt-5.5 underperforms gpt-5.4** [TESTED]
   - Scale limit 437 vs 492 (-11%). Despite 2x pricing ($5/$30 vs $2.5/$15).
   - Confirms newer/pricier does not guarantee better tabular comprehension.

6. **Claude sonnet-4.5 = sonnet-4** [TESTED]
   - Both achieve exactly 168 rows. No generational improvement for tabular extraction despite model upgrade.

7. **Context utilization mostly irrelevant** [VERIFIED]
   - Most models fail at <10% context utilization.
   - Exception: claude-opus-4.6 high reaches 55.4%, suggesting high-effort thinking genuinely engages more of the context window.

8. **Cost efficiency varies wildly** [VERIFIED]
   - Best: gpt-5-mini medium - 500 rows for ~$0.40
   - Worst: claude-opus-4.6 medium - 6 rows for $1.12 (0.05 rows/$0.01)

## 5. Production Recommendations

**Note**: 2 min/request is assumed as the maximum acceptable production latency for this research.

Best combinations for single-shot production use (per-request values):

- **Balanced** - gpt-5-mini medium, 300 rows
  - ~$0.06/request, ~3.5 min/request. Good scale, cheap but above 2 min threshold
- **Speed** - gpt-5 low, 300 rows
  - ~$0.05/request, ~2.4 min/request. High scale, borderline acceptable latency
- **Budget** - gpt-5-mini low, 50 rows
  - ~$0.01/request, ~1 min/request. Minimal cost, small datasets

No tested model achieves both high scale (300+ rows) and sub-2-min latency. For latency-critical use, chunk into smaller batches (50-100 rows) with gpt-5-mini low (~1 min/request).

Realistic boundaries:
- **Maximum reliable scale**: 400 rows (gpt-5 high, 80% of 492 limit)
- **Recommended production scale**: 300 rows (safe margin for all models)
- **Minimum viable scale**: 50 rows (even low-effort models reliable here)
- **Cost range**: $0.01-$0.27 per single extraction
- **Time range**: 1-20 minutes per single extraction

Safe operating limits:
- gpt-5-mini medium: 300 rows (60% of limit)
- gpt-5 low: 300 rows (84% of limit)
- Claude sonnet/opus: 150 rows (85% of limit)
- gpt-4o/gpt-4o-mini: NOT RECOMMENDED for tabular extraction

DO NOT USE for tabular extraction:
- gpt-4o, gpt-4o-mini (scale limits 4-6 rows)
- claude-haiku (scale limit 9 rows)
- Any temperature-based model without reasoning capability

## 6. Emergent Hypotheses

Hypotheses not in the original H1-H6 set, derived from observed data patterns:

- **E1: adaptive_thinking medium is fundamentally broken for structured data** [TESTED]
  - Evidence: opus-4.6 regresses from 177 (opus-4.5) to 6 rows. opus-4.7 = 12 rows.
  - Mechanism: Both produce false positives (precision <1.0), suggesting hallucination rather than attention loss
  - Testable: Run same task with opus-4.5 thinking vs opus-4.6 adaptive_thinking at matched token budgets

- **E2: Context utilization is irrelevant to scale limits** [VERIFIED]
  - Evidence: 14/17 models fail at <10% context. Only opus-4.6 high (55.4%) uses substantial context.
  - Mechanism: Attention degradation occurs long before context window fills
  - Testable: Compare models with 200K vs 128K context windows on same task

- **E3: Newer model versions do not guarantee better tabular comprehension** [TESTED]
  - Evidence: gpt-5.2 < gpt-5, gpt-5.5 < gpt-5.4, sonnet-4.5 = sonnet-4
  - Mechanism: General model improvements may not target structured data processing
  - Testable: Track scale limits across future model releases

- **E4: Reasoning effort multiplier is model-family dependent** [TESTED]
  - Evidence: OpenAI = 1.4x-7.7x improvement. Claude Opus = 70x-111x improvement.
  - Mechanism: adaptive_thinking may have binary activation (off at medium, full at high)
  - Testable: Test Claude models at effort levels between medium and high (if API allows)

## 7. Open Questions

1. **Why does adaptive_thinking medium produce false positives?** Other models only miss records (recall drops). adaptive_thinking medium also adds wrong records (precision drops). What mechanism causes this?

2. **Why does opus-4.6 high use 55.4% context while other models use <10%?** Is this a property of the high-effort adaptive_thinking mechanism? Does it correlate with the 111x improvement?

3. **Is the gpt-5 -> gpt-5.2 regression specific to tabular extraction?** Or does gpt-5.2 generally perform worse on structured data tasks?

4. **Would chunking + reassembly beat single-shot at 300+ rows?** E.g., split 600 rows into 2x300 batches with gpt-5-mini medium, merge results. Trade-off: 2x cost, 2x time, but guaranteed accuracy.

5. **Do different CSV structures affect scale limits?** Current test uses 7 columns with adversarial content. Would simpler data (fewer columns, no adversarial content) extend limits?

## 8. Caveats and Limitations

- **Result variance**: Binary search results have ~10% margin due to LLM non-determinism. Use `--verify-runs 3` to increase confidence.
- **Cost estimates**: Estimates assume 300-row baseline. Actual costs may be 2x higher if models scale to 600+ rows.
- **H5 confounding**: H5 compares gpt-4o (temperature) vs gpt-5 (reasoning), but these are different architectures. Results show "newer reasoning models perform better" rather than isolating the reasoning mechanism.
- **Production latency threshold**: The 2 min/request limit is a research assumption. Actual production requirements vary by use case.

## 9. Sources

- `_INFO_01_CSVScaleLimits-TestResults.md [TBLF-IN02]` - All test result data
- `_SPEC_CSVScaleLimits.md [TBLF-SP01]` - Test framework specification
- `_INFO_LLM_MARKDOWN_PREFERENCES.md [LLMO-IN01]` - Format benchmarking research (TK-001)

## 10. Document History

**[2026-05-22 16:40]**
- Initial document created from restructuring of `_INFO_CSVScaleLimits.md [TBLF-IN01]` and `_TEST_CSVScaleLimits.md [TBLF-TP01]`
- Contains: key findings, H1-H6 verdicts, detailed analysis, unexpected findings, production recommendations
- Added: Emergent Hypotheses section (E1-E4) derived from test data patterns
- Added: Open Questions section with 5 research questions
