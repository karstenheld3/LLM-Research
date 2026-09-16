# INFO: LLM Capability Testing Methodology

**Doc ID**: TBLF-IN04
**Goal**: Document the hypothesis-driven testing methodology developed for LLM capability research
**Timeline**: Created 2026-05-22

**Depends on:**
- `01_CSVScaleLimits/_SPEC_CSVScaleLimits.md [TBLF-SP01]` for test framework implementation
- `01_CSVScaleLimits/_TEST_CSVScaleLimits.md [TBLF-TP01]` for execution procedures
- `01_CSVScaleLimits/_INFO_01_CSVScaleLimits-TestResults.md [TBLF-IN02]` for result structure
- `01_CSVScaleLimits/_INFO_02_CSVScaleLimits-Findings.md [TBLF-IN03]` for analysis patterns

## Summary

- **4-document architecture** separates concerns: SPEC (what to build), TEST (how to run), INFO_01 (raw results), INFO_02 (findings and verdicts) [PROVEN]
- **Hypothesis-driven design**: Prior research generates testable predictions; tests confirm, refute, or partially support each hypothesis with labeled confidence [PROVEN]
- **Emergent hypothesis capture**: Unexpected patterns in test data generate new hypotheses (E1-E3) with testable predictions for follow-up [PROVEN]
- **Automated pipeline** connects test execution to documentation via JSON aggregation and AUTO markers in INFO_01 [PROVEN]
- **Binary search methodology** efficiently finds capability thresholds (~10 iterations vs 100+ linear) but produces probabilistic estimates, not precise boundaries [TESTED]
- **Critique-reconcile-verify cycle** stress-tests findings for statistical validity, reasoning errors, and production safety before finalizing [TESTED]

## Table of Contents

1. [Document Architecture](#1-document-architecture)
2. [Hypothesis Lifecycle](#2-hypothesis-lifecycle)
3. [Test Methodology](#3-test-methodology)
4. [Result Collection Pipeline](#4-result-collection-pipeline)
5. [Analysis and Evaluation](#5-analysis-and-evaluation)
6. [Quality Assurance](#6-quality-assurance)
7. [Lessons Learned](#7-lessons-learned)
8. [Replication Pattern](#8-replication-pattern)
9. [Sources](#9-sources)
10. [Document History](#10-document-history)

## 1. Document Architecture

Four documents with distinct responsibilities form the research unit:

```
┌──────────────────────────────────────────────────────────────────────┐
│  _SPEC_CSVScaleLimits.md [TBLF-SP01]                                 │
│  WHAT: Test framework specification                                  │
│  Contains: Domain objects, functional requirements, data structures,  │
│  pipeline flow, CLI interfaces, algorithms                           │
│  Audience: Implementer                                               │
└───────────────────────────────┬──────────────────────────────────────┘
                                │ implements
┌───────────────────────────────v──────────────────────────────────────┐
│  _TEST_CSVScaleLimits.md [TBLF-TP01]                                 │
│  HOW: Test execution procedures                                      │
│  Contains: Hypothesis-to-test mapping, execution phases, model list,  │
│  cost estimates, replication guide, verification checklist            │
│  Audience: Test operator                                             │
└───────────────────────────────┬──────────────────────────────────────┘
                                │ produces
┌───────────────────────────────v──────────────────────────────────────┐
│  _INFO_01_CSVScaleLimits-TestResults.md [TBLF-IN02]                  │
│  DATA: Automatically collected test results                          │
│  Contains: All configurations table, boundary details, per-iteration │
│  data, cost/latency curves, production decision matrix               │
│  Audience: Analyst (data reference)                                  │
│  Update method: Automated via 06_aggregate_results.py + AUTO markers │
└───────────────────────────────┬──────────────────────────────────────┘
                                │ analyzed in
┌───────────────────────────────v──────────────────────────────────────┐
│  _INFO_02_CSVScaleLimits-Findings.md [TBLF-IN03]                     │
│  KNOWLEDGE: Findings, verdicts, recommendations                      │
│  Contains: Key findings, hypothesis verdicts, detailed analysis,     │
│  unexpected findings, emergent hypotheses, open questions, caveats   │
│  Audience: Decision-maker                                            │
│  Update method: Manual analysis with verification labels             │
└──────────────────────────────────────────────────────────────────────┘
```

### 1.1 Why This Separation

The original approach used a single monolithic document that accumulated test results, analysis, and execution procedures. This created problems:

- Test results mixed with interpretation (hard to verify claims against data)
- Execution procedures buried under analysis (hard to replicate)
- Auto-generated content mixed with manual writing (merge conflicts)
- Document grew past 900 lines (cognitive overload)

The restructuring (2026-05-22) separated by update frequency and audience:
- SPEC: Rarely updated (framework stable)
- TEST: Updated when adding models or phases
- INFO_01: Updated automatically after each test run
- INFO_02: Updated manually after analysis cycles

### 1.2 Information Flow

```
Prior research (TK-001)
  │
  v
Hypotheses (H1-H6) ──> TEST (maps hypotheses to configurations)
  │                           │
  │                           v
  │                     SPEC (defines pipeline)
  │                           │
  │                           v
  │                     Execution (scripts produce JSON)
  │                           │
  │                           v
  │                     INFO_01 (automated aggregation)
  │                           │
  v                           v
INFO_02 (manual analysis: verdict per hypothesis)
  │
  v
Emergent hypotheses (E1-E3) ──> future test iterations
```

## 2. Hypothesis Lifecycle

### 2.1 Source: Prior Research

Hypotheses originate from prior empirical evidence. For CSV scale limits, the source was TK-001 benchmark (`_INFO_LLM_MARKDOWN_PREFERENCES.md [LLMO-IN01]`):

- Observed: 100% reliability at 300 records, 43% failure at 600
- Observed: Bimodal behavior (near-perfect OR complete failure)
- Attributed: Failures to "output token limits causing truncation"
- Measured: Quoted CSV ranked #3 of 10 formats

Each observation became a testable prediction:
- H1: Scale limit in 300-600 range (from reliability drop)
- H2: Cliff-like failure (from bimodal observation)
- H3: Truncation as primary failure mode (from prior attribution)
- H4: Higher effort extends limit (new variable, no prior data)
- H5: Reasoning models outperform temperature models (architectural hypothesis)

### 2.2 Hypothesis States

```
PROPOSED ──> DESIGNED ──> TESTED ──> VERDICT
   │              │           │          │
   │              │           │          ├─ SUPPORTED (High/Medium/Low confidence)
   │              │           │          ├─ NOT SUPPORTED
   │              │           │          ├─ PARTIALLY SUPPORTED
   │              │           │          └─ DEFERRED (blocked by dependency)
   │              │           │
   │              │           └─ Data collected, awaiting analysis
   │              │
   │              └─ Test configurations mapped in TEST doc
   │
   └─ Identified from prior research or observation
```

### 2.3 Verdict Criteria

Each hypothesis verdict requires:
1. **Prediction**: What the hypothesis predicts (specific, falsifiable)
2. **Evidence**: Exact data from INFO_01 (section, line, values)
3. **Calculation**: Reproducible arithmetic from evidence to conclusion
4. **Confidence label**: Based on evidence strength (Very High / High / Medium / Low)
5. **Verification label**: [ASSUMED] / [VERIFIED] / [TESTED] / [PROVEN]

### 2.4 Emergent Hypotheses

Patterns NOT predicted by original hypotheses generate emergent hypotheses (E-prefix). Qualification criteria:

- Must be observed in test data (not theoretical)
- Must NOT be a simple negation of an existing hypothesis
- Must have a testable prediction for follow-up

Examples from this research:
- **E1**: adaptive_thinking at medium effort skips reasoning (from catastrophic opus-4.6/4.7 failure)
- **E2**: Newer model versions do not guarantee better tabular comprehension (from gpt-5.2 < gpt-5)
- **E3**: Reasoning effort multiplier is model-family dependent (from 111x Claude vs 7.7x OpenAI)

Each emergent hypothesis includes:
- Evidence (what was observed)
- Mechanism (proposed explanation)
- Testable prediction (what would confirm/refute)

## 3. Test Methodology

### 3.1 Binary Search for Capability Thresholds

The core innovation: finding scale limits via binary search rather than exhaustive testing.

**Algorithm**:
1. Start at estimated threshold (from prior research)
2. Test with n=3 verification runs at current row count
3. If ALL 3 pass (Precision=1.00, Recall=1.00): increase rows (multiply by 1.5)
4. If ANY fail: decrease rows (halve the gap)
5. Once bounds established: bisect until gap <= tolerance (10 rows)
6. Report: confirmed capability = last passing point

**Efficiency**: ~10 iterations vs 100+ for linear search (at 10-row granularity over 1000-row range)

**Known limitations** (discovered during research):
- Stochastic function: LLM success is probabilistic, not deterministic step function
- n=3 provides weak statistical guarantee (~63% lower bound at 95% CI)
- 28% variance between independent runs of same binary search
- Results are "confirmed at X" (lower bound), not "fails at X+1" (precise boundary)

### 3.2 Controlled Variables

Fixed across all tests to isolate the independent variables:
- Data format: Quoted CSV
- Column count: 7 (of 20 total)
- Filter complexity: 2 conditions (IN list + threshold)
- Adversarial content: ~20% of records contain delimiter characters
- Evaluation method: Deterministic ID matching (regex: `EMP-\d{4}`)
- Seed: 42 (reproducible data generation)
- Verification runs: 3 per iteration

### 3.3 Independent Variables

Varied one at a time:
- Model (13 configurations tested)
- Reasoning effort level (low / medium / high)
- Row count (varied by binary search)

### 3.4 Evaluation: Deterministic ID Matching

Critical design decision: evaluate by comparing extracted employee IDs against ground truth, NOT by LLM judge.

Advantages over LLM-as-judge:
- Zero cost per evaluation
- Zero latency per evaluation
- Perfectly reproducible
- No evaluation model dependency
- Binary correctness (ID either present or not)

Metrics per run:
- Precision = TP / (TP + FP) - "of extracted records, how many were correct?"
- Recall = TP / (TP + FN) - "of expected records, how many were found?"
- F1 = harmonic mean of Precision and Recall
- Pass criteria: Precision=1.00 AND Recall=1.00 (all 3 runs)

## 4. Result Collection Pipeline

### 4.1 Automated Flow

```
03_find_scale_limit.py
  │
  ├─ Per iteration: Generate data → Execute LLM → Evaluate → Record
  │
  └─ Output: scale_limit_result.json (per model/config)
       │
       v
06_aggregate_results.py
  │
  ├─ Reads all scale_limit_result.json files
  ├─ Applies overrides.json (manual corrections)
  ├─ Generates all_results.json + all_results.md
  │
  └─ --update-file: Replaces AUTO-marked sections in INFO_01
       │
       v
_INFO_01_CSVScaleLimits-TestResults.md
  │
  ├─ Sections 5.1, 6.1, 6.2, 7, 8: AUTO-generated from aggregation
  └─ All other sections: Manual (methodology, metrics definitions, analysis)
```

### 4.2 AUTO Marker System

INFO_01 uses HTML comment markers to delineate auto-updated sections:

```html
<!-- AUTO:section-5-1:start -->
[content replaced by 06_aggregate_results.py]
<!-- AUTO:section-5-1:end -->
```

Manual content outside markers is preserved across updates. This enables:
- Running new tests without manual document editing
- Consistent formatting across all result tables
- Reproducible aggregation (same JSON input = same document output)

### 4.3 Override System

When tests produce anomalous results (cancelled runs, infrastructure errors), `overrides.json` provides manual corrections without re-running expensive tests:

```json
{
  "claude-opus-4.7_adaptive_thinking_high": {
    "note": "Cancelled after 8+ min reasoning, >$30 cost",
    "max_reliable_rows": "843+",
    "primary_failure_mode": "cancelled"
  }
}
```

## 5. Analysis and Evaluation

### 5.1 From Data to Findings

INFO_02 follows a structured analysis pattern:

1. **Key Findings** - Top-level observations (copy/paste-ready summary)
2. **Hypothesis Verdicts** - One-line verdict per hypothesis with confidence
3. **Detailed Analysis** - Per-hypothesis section with prediction, result, evidence, verdict
4. **Unexpected Findings** - Observations not predicted by any hypothesis
5. **Production Recommendations** - Actionable guidance derived from findings
6. **Emergent Hypotheses** - New testable predictions from unexpected patterns
7. **Open Questions** - What remains unknown after analysis
8. **Caveats and Limitations** - Explicit boundaries of what results can claim

### 5.2 Verification Label Progression

Every claim in INFO_02 carries a verification label indicating evidence strength:

- `[ASSUMED]` - Stated without verification (hypothesis stage)
- `[VERIFIED]` - Checked against source data (cross-referenced INFO_01)
- `[TESTED]` - Confirmed by running the test (direct experimental evidence)
- `[PROVEN]` - Validated in production use (not yet applicable for this research)

Labels are applied per-claim, not per-section. A section may contain both [VERIFIED] calculations and [ASSUMED] mechanistic explanations.

### 5.3 Cross-Reference Discipline

Every numerical claim in INFO_02 must reference its source in INFO_01:
- "(data: TBLF-IN02 section 5.2)" - specific table row
- "(data: TBLF-IN02 section 9.2)" - per-iteration cost data

This enables independent verification: any reader can trace a finding back to raw data.

## 6. Quality Assurance

### 6.1 Critique-Reconcile-Verify Cycle

After analysis is complete, three quality passes:

1. **`/critique`** (Devil's Advocate): Find flawed assumptions, logic errors, statistical overconfidence. Research industry alternatives. Produce `_REVIEW.md`.

2. **`/reconcile`** (Pragmatic Programmer): Assess each critique finding for real-world impact. Dismiss theoretical concerns, confirm genuine issues, propose minimal fixes.

3. **`/verify`** (Rules Compliance): Check document structure, cross-reference accuracy, formatting conventions.

### 6.2 Specific Improvements from This Cycle

Applied to INFO_02 after initial analysis:

- **Cost correction**: Production recommendations showed scale-limit costs ($0.017) instead of operating-point costs ($0.008). Fixed.
- **Statistical caveat**: Added precision note to hypothesis verdicts section. n=3 limitations made explicit at point-of-use, not just in buried caveats section.
- **Mechanism qualification**: "Comprehension failure" relabeled as exclusion category with "lost-in-the-middle" (Liu et al., 2023) as testable mechanism.
- **Efficiency metric clarity**: Cost comparisons changed from ambiguous total-test-cost framing to explicit per-request with rows/$ metric.

### 6.3 FAILS.md as Institutional Memory

Failures are recorded in `FAILS.md` with severity, root cause, and prevention rules. These are re-read before each session and inform MUST-NOT-FORGET lists. Key failures that shaped the methodology:

- `TBLF-FL-001`: Cryptic abbreviations in output (fix: use full words)
- `TBLF-FL-002`: Meaningless test case IDs (fix: use descriptive names)
- `TBLF-FL-003`: Log lines lacked context (fix: full disclosure principle)
- `TBLF-FL-005`: Column config mismatch between tests (fix: verify config before run)

## 7. Lessons Learned

### 7.1 What Worked

- **Binary search**: 10x more efficient than linear exploration
- **Deterministic evaluation**: Zero-cost, instant, perfectly reproducible
- **Automated aggregation**: New test results flow to documentation without manual editing
- **Hypothesis-first design**: Every test configuration maps to a specific hypothesis, preventing aimless exploration
- **Emergent hypothesis capture**: Structured section prevents losing unexpected insights
- **Phased execution** (cheapest first): Validates setup before expensive runs, catches bugs at $0.02 not $30

### 7.2 What Needed Iteration

- **Statistical precision**: Initial framing treated n=3 as "confirmed reliable." Critique revealed this only establishes >63% reliability at 95% CI. Reframed as "confirmed at" (lower bound) with explicit caveats.
- **Monolithic document**: Original single-document approach became unmanageable at 900+ lines. Restructured into 4 specialized documents.
- **Cost reporting**: Mixed total-test-cost with per-request-cost in early versions. Standardized to per-request with explicit annotation.
- **Failure mode categorization**: "Comprehension" initially used as precise diagnosis. Refined to exclusion category (non-truncation) with acknowledgement of multiple possible mechanisms.

### 7.3 What Would Be Different Next Time

- Start with 4-document structure from the beginning
- Use n=10+ at boundary points for production-grade claims
- Log thinking blocks from Claude to distinguish "skipped reasoning" from "insufficient reasoning"
- Test position-dependence of failures from the start (lost-in-the-middle analysis)

## 8. Replication Pattern

To apply this methodology to a new LLM capability question:

1. **Identify prior evidence** - What existing data suggests testable predictions?
2. **Formulate hypotheses** - 3-6 specific, falsifiable predictions with confidence
3. **Design evaluation** - Find a deterministic metric (avoid LLM-as-judge if possible)
4. **Specify pipeline** - SPEC document: generate → execute → evaluate → summarize
5. **Map tests** - TEST document: hypothesis → model × config matrix
6. **Automate collection** - Script outputs JSON; aggregator updates INFO_01
7. **Analyze manually** - INFO_02: verdict per hypothesis, emergent patterns, recommendations
8. **Quality-check** - /critique → /reconcile → /verify cycle
9. **Record failures** - FAILS.md entries inform future MUST-NOT-FORGET lists

## 9. Sources

- `01_CSVScaleLimits/_SPEC_CSVScaleLimits.md [TBLF-SP01]` - Test framework specification
- `01_CSVScaleLimits/_TEST_CSVScaleLimits.md [TBLF-TP01]` - Test execution procedures
- `01_CSVScaleLimits/_INFO_01_CSVScaleLimits-TestResults.md [TBLF-IN02]` - Automated result collection
- `01_CSVScaleLimits/_INFO_02_CSVScaleLimits-Findings.md [TBLF-IN03]` - Findings and analysis
- `FAILS.md` - Institutional memory of past failures
- Liu et al., 2023 - "Lost in the Middle: How Language Models Use Long Contexts" (referenced in critique cycle)

## 10. Document History

**[2026-05-22 18:41]**
- Initial document created
- Analyzed methodology from 01_CSVScaleLimits document ecosystem
- Documented: architecture, hypothesis lifecycle, test methodology, pipeline, analysis patterns, quality assurance, lessons learned
