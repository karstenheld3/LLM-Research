# Session Progress

## Phase Plan

- [x] **EXPLORE** - complete - Research tabular format effectiveness for LLMs
- [x] **DESIGN** - complete - Define test methodology and benchmarks
- [x] **IMPLEMENT** - complete - Test 01 (20/20 CSV scale limits), Test 02 (56/56 format comparison)
- [x] **REFINE** - complete - Findings documents, critique/reconcile/verify cycle
- [ ] **DELIVER** - pending - Final summary, session finalization

## STRUT: Restructure CSV Scale Limit Documents

**Goal**: Separate raw test data from interpretation. Create clean data/findings pipeline.

[x] P1 [ANALYZE]: Map content to new structure
├─ Objectives:
│   └─ [x] Content mapping complete ← P1-D1, P1-D2
├─ Strategy: Read all source docs, categorize every section as DATA or INTERPRETATION
├─ [x] P1-S1 [READ](TEST sections, classify each as EXECUTION / DATA / INTERPRETATION)
├─ [x] P1-S2 [READ](INFO sections, classify each as METHODOLOGY / DATA / INTERPRETATION)
├─ [x] P1-S3 [MAP](content to target docs: TEST, INFO_01, INFO_02)
├─ Deliverables:
│   ├─ [x] P1-D1: Content mapping for TEST (what stays, what moves)
│   └─ [x] P1-D2: Content mapping for INFO_01 and INFO_02
└─> Transitions:
    - P1-D1, P1-D2 checked → [CONSULT]

[x] P2 [CREATE]: Build INFO_01 (raw data) and INFO_02 (findings)
├─ Objectives:
│   ├─ [x] INFO_01 contains 100% of test result data ← P2-D1
│   └─ [x] INFO_02 contains all findings and hypothesis work ← P2-D2
├─ Strategy: Create docs from mapped content, verify no data lost
├─ [x] P2-S1 [CREATE](INFO_01: header, methodology from old INFO secs 1-5, results table, failure mode table, effort data, tier data, search histories)
├─ [x] P2-S2 [CREATE](INFO_02: header, key findings, H1-H6 verdicts, detailed analysis, unexpected findings, production recommendations, emergent hypotheses, open questions)
├─ [x] P2-S3 [VERIFY](INFO_01 has zero interpretation language)
├─ [x] P2-S4 [VERIFY](INFO_02 cites INFO_01 for all data references)
├─ Deliverables:
│   ├─ [x] P2-D1: _INFO_01_CSVScaleLimits-TestResults.md [TBLF-IN02] created
│   └─ [x] P2-D2: _INFO_02_CSVScaleLimits-Findings.md [TBLF-IN03] created
└─> Transitions:
    - P2-D1, P2-D2 checked → P3 [REFACTOR]

[x] P3 [REFACTOR]: Strip TEST, archive old INFO
├─ Objectives:
│   ├─ [x] TEST contains only execution instructions ← P3-D1
│   └─ [x] Old INFO archived ← P3-D2, P3-D3
├─ Strategy: Remove results/analysis from TEST, update cross-references, archive old INFO
├─ [x] P3-S1 [REMOVE](Executive Summary, Detailed Analysis, Unexpected Findings from TEST)
├─ [x] P3-S2 [ADD](cross-references to INFO_01 and INFO_02 in TEST header)
├─ [x] P3-S3 [UPDATE](SPEC depends-on references if needed)
├─ [x] P3-S4 [ARCHIVE](old _INFO_CSVScaleLimits.md - rename with _old suffix or delete)
├─ [x] P3-S5 [UPDATE](document histories in all modified docs)
├─ [x] P3-S6 [COMMIT]
├─ Deliverables:
│   ├─ [x] P3-D1: TEST stripped to execution-only
│   ├─ [x] P3-D2: Old INFO archived
│   └─ [x] P3-D3: All cross-references updated
└─> Transitions:
    - P3-D1, P3-D2, P3-D3 checked → [END]

## To Do

- [ ] Test chunking strategy (chunk+merge vs single-shot) - highest-value next experiment
- [ ] Fix TBLF-FL-005 (re-run Test 02 with 7/20 columns to match Test 01)
- [ ] Test format preference at higher reasoning effort levels

## In Progress

(none)

## Done

- [x] Run claude-opus-4-8 high scale limit test (2026-05-30)
  - Result: 492 rows (comprehension failure, 12.4% context, $19.96 total)
  - Boundary: [492, 500]. Verified against Anthropic billing ($89.19 - $69.23 = $19.96)
  - Notable: Regresses below opus-4.6 (667) and opus-4.7 (843+) at same effort level
  - INFO_01 and INFO_02 updated with new data point

- [x] Automate findings generation for Format Comparison
  - Created `08_generate_findings.py` (reads `all_results.json`, generates 4 AUTO sections)
  - Added to `run_pipeline.ps1` as step 3/4
  - Sections: key findings, hypothesis evidence tables, unexpected findings, production recommendations
- [x] Devil's Advocate review of full methodology (`_PROBLEMS_REVIEW.md`)
  - 3 confirmed: n=3 precision, chunking gap, E3 circularity
  - 5 disputed (already addressed or overstated), 1 dismissed (pipeline not overengineered for ongoing research)
- [x] Reconciliation: implemented 3 confirmed findings
  - Added Chunking Strategy + Measurement Precision Note to both INFO_02 files
  - Added floor-effect caveat to E3
- [x] Verify: fixed CPKC/TPKC acronym expansion, wrong Open Question #3 reference
- [x] Align Format Comparison with 4-document methodology (STRUT complete)
  - Split `_INFO_FormatComparison.md` into `_INFO_01` (results) + `_INFO_02` (findings)
  - Created `06_aggregate_results.py` + `run_pipeline.ps1` for automated pipeline
  - Added AUTO markers, overrides.json, verification labels, caveats, emergent hypotheses
  - Fixed filter description mismatch, Doc ID collision (TBLF-IN02 -> TBLF-IN05/IN06)

## Previously Done

- [x] Created _SPEC_CSVScaleLimits.md [TBLF-SP01]
- [x] Critique via /critique - compared against working POC
- [x] Reconcile via /reconcile - prioritized findings
- [x] Implemented approved findings (RV-001 through RV-008)
- [x] Implemented 4-script pipeline (generate, execute, evaluate, summarize)
- [x] Combined execute+evaluate into single parallel script (02_execute_and_evaluate.py)
- [x] Fixed max_tokens -> max_completion_tokens for gpt-5 models
- [x] Fixed Python coding style (2-space indent, single-line imports)
- [x] Fixed logging to comply with LOG-SC rules (headers, counters, status patterns)
- [x] Created quick test instance: 002_gpt-5-mini_20rows (20 rows, 2 runs)
- [x] Test run: 20 rows, gpt-5-mini, 2 runs
  - Result: F1=1.00, P=1.00, R=1.00 (100% accuracy)
  - Finding: Model handles AND filter logic correctly at small scale

## Tried But Not Used
