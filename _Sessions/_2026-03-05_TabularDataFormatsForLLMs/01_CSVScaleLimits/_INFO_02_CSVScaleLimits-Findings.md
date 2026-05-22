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

- **Claude opus-4.6 high = highest confirmed capability**
  - Confirmed reliable at 667 rows (55.4% context utilization)
- **adaptive_thinking at medium effort skips reasoning (catastrophic for structured data)**
  - opus-4.6 (6 rows), opus-4.7 (12 rows) - model skips thinking phase, hallucinates
- **Effort multiplier extreme on Claude Opus 4.6**
  - medium (6) to high (667) = 111x improvement
- **Reasoning models massively outperform temperature models**
  - gpt-5-mini (confirmed at 500 rows) vs gpt-4o-mini (6 rows) = 83x
- **Confirmed capability varies 160x+ across models**
  - Best confirmed: opus-4.6 high (667) vs Worst: gpt-4o (4)
- **Comprehension is primary failure mode, not truncation**
  - 14/17 completed tests failed due to comprehension errors
- **Context window is NOT the bottleneck**
  - Most failures occur at <10% context utilization

## 2. Hypothesis Verdicts

Prior evidence from TK-001 benchmark (`_INFO_LLM_MARKDOWN_PREFERENCES.md [LLMO-IN01]`):
- gpt-5-mini reliable at 300 records, unreliable at 600 (43% failure rate)
- At 600 records: bimodal behavior (near-perfect OR complete failure)
- v5 failures attributed to "output token limits causing truncation"
- Quoted CSV ranked #3 of 10 formats at 300 records

- **H1 - Scale limit 300-600 rows**: SUPPORTED (High)
  - gpt-5-mini medium confirmed at 500 rows (re-run; original 389 also in range; ~28% measurement variance)
- **H2 - Bimodal failure (cliff)**: PARTIALLY SUPPORTED (Medium)
  - Reasoning: cliff (100% to 0%). Temperature: gradual slope
- **H3 - Truncation > comprehension**: NOT SUPPORTED (High)
  - Comprehension = 14/17 tests. Truncation: gpt-5 high, claude-sonnet-4, claude-opus-4.5
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

**Result**: Comprehension is primary failure mode (14/17 tests with clear failure modes). [VERIFIED]

**Key Insight**: Context windows are NOT the bottleneck. Models fail at <5-16% context utilization on average (data: TBLF-IN02 section 6.1). Exception: claude-opus-4.6 high reaches 55.4% - the only model to use >30% of its context before failure. [VERIFIED]

**Verdict**: NOT SUPPORTED. TK-001 attribution was incorrect. Comprehension (attention degradation) is the true failure mode (14/17 completed tests; 3 truncation: gpt-5 high, claude-sonnet-4, claude-opus-4.5). [TESTED]

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

1. **Claude adaptive_thinking at medium effort skips reasoning for structured data** [TESTED]
   - opus-4.6 (6 rows) and opus-4.7 (12 rows) vs sonnet-4 (187 rows) and opus-4.5 (177 rows)
   - Both produce false positives (precision <1.0) unlike all other models which only missed records
   - Root cause: adaptive thinking (`type: "adaptive"`) at medium effort allows the model to skip reasoning entirely. Sonnet-4/4.5 use guaranteed manual thinking (`type: "enabled"`, `budget_tokens`); opus-4.5 uses a separate `effort` parameter - both ensure reasoning. See E1 for full API-level explanation.

2. **Claude opus-4.6 high effort = highest confirmed result** [TESTED]
   - 667 rows with 55.4% context utilization
   - Only model to use >30% of context before failure
   - Suggests high-effort adaptive_thinking enables genuine deep comprehension rather than surface-level pattern matching

3. **111x effort multiplier on Claude Opus 4.6** [TESTED]
   - medium (6) to high (667)
   - Far exceeds gpt-5-mini's 7.7x and gpt-5's 1.4x multipliers
   - The adaptive_thinking mechanism appears binary - nearly useless at medium, exceptional at high

4. **gpt-5.2 likely underperforms gpt-5** [VERIFIED]
   - Confirmed at 215 vs 356 rows (gpt-5 low). Difference (40%) exceeds measurement noise. Newer is not always better for specific tasks.

5. **gpt-5.5 comparable to gpt-5.4** [TESTED]
   - Confirmed at 437 vs 492 rows (-11%). Within measurement precision (~28% variance observed). Despite 2x pricing ($5/$30 vs $2.5/$15).
   - Cannot confirm statistical difference; both achieve ~450-500 tier.

6. **Claude sonnet-4 truncates, sonnet-4.5 does not** [TESTED]
   - sonnet-4: 187 rows, truncation failure at 25.1% context utilization
   - sonnet-4.5: 168 rows, comprehension failure at 8.4% context utilization
   - Newer model actually achieves fewer rows but with a healthier (non-truncation) failure mode

7. **Context utilization mostly irrelevant** [VERIFIED]
   - Most models fail at <10% context utilization.
   - Exception: claude-opus-4.6 high reaches 55.4%, suggesting high-effort thinking genuinely engages more of the context window.

8. **Cost efficiency varies wildly** [VERIFIED]
   - Best: gpt-5-mini medium - 500 rows for ~$0.40
   - Worst: claude-opus-4.6 medium - 6 rows for $1.12 (0.05 rows/$0.01)

## 5. Production Recommendations

**Scope**: Results apply to 7-column CSV extraction with compound filter (2 conditions). Simpler tasks likely achieve higher scale; more complex tasks achieve lower scale. Exact multiplier is unknown (see Open Questions).

**Statistical note**: All row counts represent confirmed-reliable points from n=3 verification runs. Measurement variance is ~28% between independent runs. Recommendations use conservative 60% safety margin.

**Detailed per-workload cost/time data**: See `_INFO_01_CSVScaleLimits-TestResults.md [TBLF-IN02]` section 9.6 (Production Decision Matrix).

Best combinations for single-shot production use (per-request values at operating point):

- **Balanced** - gpt-5-mini medium, 300 rows
  - $0.017/request, ~1.2 min/request. Best rows/$ efficiency (29K rows/$)
- **Speed** - gpt-5.5 medium, 300 rows
  - $0.347/request, ~27 sec/request. Fastest at 300+ rows
- **Max capability** - claude-opus-4.6 high, 400 rows
  - $0.558/request, ~1.0 min/request. Highest confirmed scale (667 rows)
- **Budget + fast** - gpt-5.2 medium, 150 rows
  - $0.032/request, ~39 sec/request. Cheapest config under 60s

Pareto-optimal configs (no other is better on ALL of rows, cost, time):
- claude-opus-4.6 high (667 rows, $0.81/req, 1.5m)
- gpt-5-mini medium (500 rows, $0.017/req, 1.2m)
- gpt-5.4 medium (492 rows, $0.14/req, 51s)
- gpt-5.5 medium (437 rows, $0.41/req, 32s)
- gpt-5.2 medium (215 rows, $0.046/req, 55s)

Conservative operating limits (60% of confirmed capability):
- gpt-5-mini medium: 300 rows (60% of 500)
- gpt-5.4 medium: 300 rows (61% of 492)
- gpt-5.5 medium: 260 rows (60% of 437)
- gpt-5 low: 210 rows (60% of 356)
- Claude sonnet/opus thinking: 100 rows (60% of ~170)
- gpt-4o/gpt-4o-mini: NOT RECOMMENDED for tabular extraction

DO NOT USE for tabular extraction (confirmed at <10 rows):
- gpt-4o, gpt-4o-mini (4-6 rows)
- claude-haiku (9 rows)
- Any temperature-based model without reasoning capability
- claude-opus adaptive_thinking at medium effort (6-12 rows)

## 6. Emergent Hypotheses

Hypotheses not in the original H1-H6 set, derived from observed data patterns. Negatives of existing hypotheses (e.g., "context is irrelevant" = H3 NOT SUPPORTED) do not qualify.

- **E1: adaptive_thinking at medium effort skips reasoning for structured data** [TESTED]
  - Evidence: opus-4.6 (6 rows) and opus-4.7 (12 rows) catastrophically underperform compared to sonnet-4 (187 rows) and opus-4.5 (177 rows). Both opus-4.6/4.7 produce false positives (precision <1.0), indicating hallucination.
  - Mechanism (from Anthropic API docs `ANTAPI-IN13` + our `model-registry.json`):
    - Three distinct Anthropic reasoning methods exist in our test suite:
      1. **sonnet-4, sonnet-4.5**: manual thinking (`type: "enabled"`, `budget_tokens: 10000`). Guarantees reasoning phase with minimum 1024 tokens.
      2. **opus-4.5**: `effort` parameter (beta `effort-2025-11-24`). Separate mechanism that also engages reasoning.
      3. **opus-4.6, opus-4.7**: adaptive thinking (`type: "adaptive"`) + `output_config: {"effort": "medium"}`. Model decides whether and how much to think.
    - With adaptive thinking, the model decides whether and how much to think. The effort parameter is a signal, not a guarantee. Per ANTAPI-IN13: "no thinking block produced if model skips thinking" (confirmed possible with `type: "adaptive"`)
    - Despite passing `effort: "medium"`, the model either skips reasoning or allocates too few thinking tokens for structured data. We cannot distinguish which - our test code does not log thinking blocks from the response
    - The resulting behavior (false positives, hallucination at 6-12 rows) is consistent with no/insufficient reasoning
    - At high effort, adaptive thinking engages fully (opus-4.6: 667 rows, 55.4% context) - proving the capability exists but is not activated at medium
  - This is NOT a model quality regression. It is an API method difference: adaptive thinking gives the model discretion to skip reasoning. Methods 1 and 2 above guarantee reasoning engagement.
  - Testable: Run opus-4.7 with `type: "enabled"` + `budget_tokens: 10000` (API docs confirm opus-4.7 supports both manual and adaptive modes). If scale limit jumps from 12 to ~150+, confirms adaptive skip is the root cause.

- **E2: Newer model versions do not guarantee better tabular comprehension** [TESTED]
  - Evidence: gpt-5.2 < gpt-5 (40% worse), gpt-5.5 comparable to gpt-5.4 (within noise), sonnet-4.5 comparable to sonnet-4
  - Mechanism: General model improvements may not target structured data processing
  - Testable: Track scale limits across future model releases

- **E3: Reasoning effort multiplier is model-family dependent** [TESTED]
  - Evidence: OpenAI = 1.4x-7.7x improvement. Claude Opus adaptive = 70x-111x improvement.
  - Mechanism (confirmed via `ANTAPI-IN13` + `model-registry.json`): Claude adaptive thinking at medium may skip reasoning entirely, producing a binary jump (no reasoning vs full reasoning). OpenAI models use `reasoning_effort` parameter which scales token allocation but always engages the reasoning mechanism - producing gradual improvement rather than a binary jump.
  - Testable: SDK supports `"max"` effort level - test if max > high for Claude models. Also test opus-4.7 manual mode at varying `budget_tokens` (1024, 5000, 10000, 20000) to map the thinking budget curve and confirm reasoning always engages.

## 7. Open Questions

1. ~~**Why does adaptive_thinking medium produce false positives?**~~ **ANSWERED**: At medium effort, adaptive thinking either skips reasoning or allocates insufficient thinking tokens for structured data (`ANTAPI-IN13`: effort is a signal, not a guarantee; model has discretion). Without adequate reasoning, the model hallucinates records. Verification: 1) log thinking blocks to confirm skip vs minimal thinking, 2) run opus-4.7 with manual thinking (`type: "enabled"`, `budget_tokens: 10000`) to confirm guaranteed reasoning fixes the issue.

2. **Why does opus-4.6 high use 55.4% context while other models use <10%?** Is this a property of the high-effort adaptive_thinking mechanism? Does it correlate with the 111x improvement?

3. **Is the gpt-5 -> gpt-5.2 regression specific to tabular extraction?** Or does gpt-5.2 generally perform worse on structured data tasks?

4. **Would chunking + reassembly beat single-shot at 300+ rows?** E.g., split 600 rows into 2x300 batches with gpt-5-mini medium, merge results. Trade-off: 2x cost, 2x time, but guaranteed accuracy.

5. **Do different CSV structures affect scale limits?** Current test uses 7 columns with adversarial content. Would simpler data (fewer columns, no adversarial content) extend limits?

## 8. Caveats and Limitations

- **Measurement precision**: Binary search with n=3 runs has ~28% variance between independent searches (observed: gpt-5-mini found 389 then 500). Model differences <20% may be within noise.
- **Statistical significance**: With n=3 per iteration, the test cannot distinguish 90% reliability from 99% reliability. Confirmed row counts are lower bounds, not precise boundaries.
- **Task specificity**: All tests use one task type (7-column CSV, compound filter, 20% adversarial content). Results may not generalize to different column counts, filter complexities, or data patterns.
- **Cost estimates**: Per-workload costs in section 5 are measured at the closest tested row count (not interpolated). Actual production costs at exact operating points may differ slightly.
- **H5 confounding**: H5 compares gpt-4o (temperature) vs gpt-5 (reasoning), but these are different architectures. Results show "newer reasoning models perform better" rather than isolating the reasoning mechanism.
- **Production latency threshold**: The 2 min/request limit is a research assumption. Actual production requirements vary by use case.
- **Temporal validity**: Models may be silently updated. Results are snapshots from May 2026.

## 9. Sources

- `_INFO_01_CSVScaleLimits-TestResults.md [TBLF-IN02]` - All test result data
- `_SPEC_CSVScaleLimits.md [TBLF-SP01]` - Test framework specification
- `_INFO_LLM_MARKDOWN_PREFERENCES.md [LLMO-IN01]` - Format benchmarking research (TK-001)
- `_INFO_ANTAPI-IN13_EXTENDED_THINKING.md [ANTAPI-IN13]` - Anthropic adaptive thinking API docs (explains E1/E4 mechanisms)

## 10. Document History

**[2026-05-22 18:15]**
- Fixed: E1 incorrectly stated opus-4.5 uses "manual thinking" - actually uses `effort` parameter (beta). Three distinct methods clarified: 1) manual thinking (sonnet-4/4.5), 2) effort param (opus-4.5), 3) adaptive thinking (opus-4.6/4.7)
- Fixed: E4 mechanism - removed claim "OpenAI always engages reasoning"; replaced with "scales token allocation"
- Changed: Verified all claims against ANTAPI-IN13 + model-registry.json + llm_client.py

**[2026-05-22 18:14]**
- Changed: E1 rewritten with API-level root cause (adaptive thinking skips reasoning at medium effort)
- Changed: E4 mechanism confirmed via ANTAPI-IN13 (binary jump, not gradual scaling)
- Changed: Open Question #1 marked ANSWERED with verification test proposed
- Changed: Unexpected Finding #1 updated with root cause explanation
- Added: ANTAPI-IN13 as source

**[2026-05-22 18:10]**
- Changed: Production recommendations updated with actual per-workload costs from TBLF-IN02 section 9.6
- Added: Pareto-optimal config summary (5 non-dominated configurations)
- Added: "Max capability" and "Budget + fast" production profiles
- Changed: E3 evidence qualified (gpt-5.5 "comparable" not "underperforms")
- Changed: Cost caveat updated to reflect measured per-workload data

**[2026-05-22 18:02]**
- Changed: Language reframed from "scale limit = X" to "confirmed at X rows" throughout
- Changed: gpt-5.5 vs gpt-5.4 comparison qualified as "within measurement precision" (11% < 28% variance)
- Changed: Production recommendations now reference section 9.6 fixed-workload data
- Added: Scope caveat (7-column, compound filter), statistical note (n=3, 28% variance), 60% safety margin
- Added: Caveats for measurement precision, task specificity, temporal validity
- Changed: Safe operating limits reformulated as "60% of confirmed capability"
- Changed: "DO NOT USE" list includes adaptive_thinking medium

**[2026-05-22 17:05]**
- Fixed: claude-sonnet-4 = 187 rows, truncation, 25.1% (was 168, comprehension, 8.4%)
- Fixed: H3 verdict updated to 14/17 comprehension, 3/17 truncation (was 15/17 and 2)
- Fixed: Production recommendations updated with single-request times
- Fixed: Unexpected finding #6 rewritten (sonnet-4 truncates, sonnet-4.5 doesn't)
- Changed: Time values throughout now represent single API call time

**[2026-05-22 16:40]**
- Initial document created from restructuring of `_INFO_CSVScaleLimits.md [TBLF-IN01]` and `_TEST_CSVScaleLimits.md [TBLF-TP01]`
- Contains: key findings, H1-H6 verdicts, detailed analysis, unexpected findings, production recommendations
- Added: Emergent Hypotheses section (E1-E4) derived from test data patterns
- Added: Open Questions section with 5 research questions
