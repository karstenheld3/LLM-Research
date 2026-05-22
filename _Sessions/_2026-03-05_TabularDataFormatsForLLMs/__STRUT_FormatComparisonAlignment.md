# STRUT: Align Format Comparison with Test Methodology

**Goal**: Restructure 02_FormatComparison to follow the 4-document architecture and analysis patterns defined in `_INFO_LLM_TEST_METHODOLOGY.md [TBLF-IN04]`

**Context**: Test 02 currently uses a monolithic INFO document mixing results and findings. The TEST document contains a full results table. No automated pipeline, no verification labels, no emergent hypotheses section, no caveats. Doc ID TBLF-IN02 collides with Test 01's restructured results document.

## MUST-NOT-FORGET

- Doc ID TBLF-IN02 is already used by `01_CSVScaleLimits/_INFO_01_CSVScaleLimits-TestResults.md`. Assign new IDs.
- H9 (structural markers) emerged DURING testing - classify as emergent hypothesis (E-prefix)
- TBLF-FL-005 (column config mismatch) must remain prominently noted
- Do NOT re-run any tests. This is document restructuring only.
- Preserve all existing data and findings - restructure, do not discard
- 56/56 tests complete - no data collection needed

## Gap Analysis

Current state vs TBLF-IN04 methodology:

- **No INFO_01/INFO_02 split**: Single `_INFO_FormatComparison.md` mixes results and analysis
- **Results in TEST doc**: `_TEST_FormatComparison.md` contains full results table (violation)
- **No automated pipeline**: `_Scripts/` empty, no aggregation script, no AUTO markers
- **Flat hypothesis evaluation**: Missing structured Prediction/Result/Evidence/Verdict format
- **No verification labels**: Claims lack [ASSUMED]/[VERIFIED]/[TESTED] markers
- **Mixed hypothesis types**: H9 emerged during testing but listed alongside original H1-H6
- **No caveats section**: Measurement limitations undocumented
- **No open questions section**: Follow-up research not captured
- **No critique/reconcile/verify**: Quality assurance cycle not applied
- **Doc ID collision**: TBLF-IN02 used by both Test 01 and Test 02

## Plan

[x] P1 [RESTRUCTURE]: Split documents and fix identifiers
├─ Objectives:
│   ├─ [ ] 4-document structure established ← P1-D1, P1-D2, P1-D3
│   └─ [ ] No Doc ID collisions ← P1-D4
├─ Strategy: Create INFO_01 (results) and INFO_02 (findings) from existing monolithic INFO. Move results table from TEST to INFO_01. Assign new Doc IDs.
│   - New IDs: TBLF-IN05 (FormatComparison results), TBLF-IN06 (FormatComparison findings)
│   - SPEC (TBLF-SP02) and TEST (TBLF-TP02) keep existing IDs
├─ [x] P1-S1 [CREATE](_INFO_01_FormatComparison-TestResults.md [TBLF-IN05]) with results table from TEST doc + format examples + methodology
├─ [x] P1-S2 [CREATE](_INFO_02_FormatComparison-Findings.md [TBLF-IN06]) with hypothesis verdicts, analysis, recommendations from INFO doc
├─ [x] P1-S3 [UPDATE](_TEST_FormatComparison.md) - remove results table, add cross-references to INFO_01/INFO_02
├─ [x] P1-S4 [UPDATE](old _INFO_FormatComparison.md) - replace content with redirect notice to new documents
├─ [x] P1-S5 [UPDATE](ID-REGISTRY.md) - register TBLF-IN05, TBLF-IN06, fix TBLF-IN02 collision
├─ Deliverables:
│   ├─ [x] P1-D1: _INFO_01_FormatComparison-TestResults.md exists with all result data
│   ├─ [x] P1-D2: _INFO_02_FormatComparison-Findings.md exists with analysis
│   ├─ [x] P1-D3: _TEST_FormatComparison.md contains only execution procedures
│   └─ [x] P1-D4: ID-REGISTRY.md updated, no collisions
└─> Transitions:
    - P1-D1 - P1-D4 checked → P2 [ENHANCE]

[x] P2 [ENHANCE]: Apply TBLF-IN04 analysis patterns to findings document
├─ Objectives:
│   ├─ [ ] Structured hypothesis evaluation with evidence chains ← P2-D1
│   ├─ [ ] Emergent hypotheses separated from original ← P2-D2
│   └─ [ ] Quality signals present (labels, caveats, questions) ← P2-D3, P2-D4
├─ Strategy: Transform flat hypothesis table into detailed per-hypothesis analysis sections. Reclassify H9 as emergent. Add verification labels, caveats, open questions.
├─ [x] P2-S1 [RESTRUCTURE](hypothesis verdicts section) - add Prediction/Result/Evidence/Verdict per hypothesis
├─ [x] P2-S2 [ADD](verification labels) - [TESTED] on data-backed claims, [VERIFIED] on cross-referenced calculations
├─ [x] P2-S3 [RECLASSIFY](H9 as E1) - structural markers hypothesis emerged during testing, move to Emergent Hypotheses section
├─ [x] P2-S4 [ADD](Caveats and Limitations section) - measurement precision, column config mismatch (TBLF-FL-005), task specificity, model temporal validity
├─ [x] P2-S5 [ADD](Open Questions section) - format-complexity interaction (H4 inconclusive), training data composition theory, position effects
├─ [x] P2-S6 [ADD](Precision note to verdicts section) - bridge to caveats, clarify confidence
├─ Deliverables:
│   ├─ [x] P2-D1: Each hypothesis has Prediction/Result/Evidence/Verdict structure
│   ├─ [x] P2-D2: Emergent hypotheses section with E-prefix
│   ├─ [x] P2-D3: Verification labels on all claims
│   └─ [x] P2-D4: Caveats, open questions, precision note present
└─> Transitions:
    - P2-D1 - P2-D4 checked → P3 [VERIFY]

[x] P3 [VERIFY]: Quality assurance
├─ Objectives:
│   └─ [ ] All documents pass /verify ← P3-D1, P3-D2
├─ Strategy: Run /verify on new INFO_01 and INFO_02. Fix any issues found.
├─ [x] P3-S1 [VERIFY](INFO_01 - results document)
├─ [x] P3-S2 [VERIFY](INFO_02 - findings document)
├─ [x] P3-S3 [FIX](filter description corrected: was "department=Engineering AND salary>75000", actual: "clearance IN [Level 3-5] AND salary >= 150000")
├─ [x] P3-S4 [COMMIT](all changes)
├─ Deliverables:
│   ├─ [x] P3-D1: INFO_01 passes verification
│   └─ [x] P3-D2: INFO_02 passes verification
└─> Transitions:
    - P3-D1, P3-D2 checked → [END]
