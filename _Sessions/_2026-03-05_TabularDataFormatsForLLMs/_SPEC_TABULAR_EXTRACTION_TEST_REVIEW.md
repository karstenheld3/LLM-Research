# _SPEC_TABULAR_EXTRACTION_TEST_REVIEW.md

**Doc ID**: TBLF-SP01-RV01
**Goal**: Identify design flaws by comparing SPEC against working POC solution
**Reviewed**: 2026-03-05 17:55
**Context**: Compared TBLF-SP01 against working POC at `IPPS/_PrivateSessions/_2026-03-04_LLMMarkdownOptimization/poc`

## Table of Contents

1. [Critical Issues](#critical-issues)
2. [High Priority](#high-priority)
3. [Medium Priority](#medium-priority)
4. [Low Priority](#low-priority)
5. [Industry Research Findings](#industry-research-findings)
6. [Recommendations](#recommendations)
7. [Document History](#document-history)

## Critical Issues

### `TBLF-RV-001` LLM Judge is Wrong Tool for This Task

- **Location**: TBLF-DD-02, TBLF-FR-04, Section 6 (Key Mechanisms)
- **What**: SPEC proposes using LLM judge to evaluate extraction results. POC uses deterministic regex matching on EmployeeID.
- **Risk**: 
  - LLM judges are unreliable when correct answers ARE known and enumerable (this case)
  - Adds cost, latency, and non-determinism to evaluation
  - Judge can be fooled by formatting tricks while missing actual errors
  - Creates circular dependency: testing LLM with LLM
- **Evidence**: 
  - POC works reliably with simple regex: `$_ -match '(EMP-\d{4}-\d{4})'`
  - Industry research confirms: "When correct answers are known and enumerable, such as math problems, factual queries with verifiable answers... traditional metrics or rule-based checking is more reliable and cheaper than LLM judges" (Weights & Biases)
- **Suggested action**: Replace LLM judge with deterministic evaluation. Parse LLM output for expected record IDs. This is a **fundamental design flaw**.

### `TBLF-RV-002` Random Filter Generation Breaks Reproducibility

- **Location**: TBLF-FR-01, GroundTruth domain object
- **What**: SPEC proposes "Auto-generate ground_truth.json with **random** filter criteria". POC uses **fixed** filter criteria (SecurityClearance Level 3-5 AND Salary >= $150k).
- **Risk**:
  - Different runs produce different expected results
  - Cannot compare results across test instances
  - Debugging failures requires reconstructing exact random state
  - Violates benchmarking best practice: tests should be deterministic
- **Evidence**: 
  - POC `generate-tk001-prompts.py` lines 27-46: Fixed filters, deterministic expected output
  - Research: "For high-throughput production systems... relying on a single LLM judge makes evaluation brittle"
- **Suggested action**: Use fixed, well-documented filter criteria per test definition. Random seeds are fine for data generation, not for filter selection.

## High Priority

### `TBLF-RV-003` Missing Adversarial Data Patterns

- **Location**: TBLF-FR-01 (Data Generation), Section 8 (Data Structures)
- **What**: SPEC generates "realistic employee-style data" but doesn't mention adversarial patterns. POC deliberately includes confusing characters (colons, pipes, commas) in data values to test parser robustness.
- **Risk**: Tests may pass on clean data but fail on real-world data with special characters
- **Evidence**: POC `generate-tk001-data.py` lines 31-102 includes:
  - `"Research & Development"`, `"Sales: Enterprise"`, `"Human Resources | Talent"`
  - `"Principal Scientist: AI"`, `"VP | People Ops"`
  - `"Building A, Floor 3 | Desk 101"`, `"$385,000.00/year"`
- **Suggested action**: Add explicit requirement for adversarial data patterns in TBLF-FR-01. List specific confusing characters to include.

### `TBLF-RV-004` No Token Limit / Context Window Consideration

- **Location**: Entire SPEC
- **What**: SPEC aims to test "scale limits" but doesn't address token/context window limits. A 1000-row CSV may exceed model context window before extraction accuracy degrades.
- **Risk**: 
  - Test may fail due to token truncation, not extraction accuracy
  - Cannot distinguish "model can't extract" from "data was truncated"
  - Different models have different context limits
- **Evidence**: Not mentioned anywhere in SPEC. POC tested with 50-300 records staying within safe limits.
- **Suggested action**: Add requirement to calculate and log token count per prompt. Add TBLF-FR-XX for token budget tracking. Define maximum token threshold per model.

### `TBLF-RV-005` Ground Truth Verification Gap

- **Location**: TBLF-FR-01, TBLF-IG-01
- **What**: SPEC says ground truth is "auto-generated" but doesn't specify how to verify it's correct. If filter logic has bugs, all tests will use wrong expected values.
- **Risk**: Silent test failures - everything looks green but expected output is wrong
- **Evidence**: POC `generate-tk001-prompts.py` includes explicit filter logic (lines 27-46) that can be manually verified. SPEC delegates to "random" filter generation.
- **Suggested action**: Add explicit verification step: generate ground truth, manually verify sample records match filter criteria.

## Medium Priority

### `TBLF-RV-006` Over-Engineering: 5 Scripts vs 2+1

- **Location**: Test domain object, folder structure
- **What**: SPEC proposes 5 separate scripts. POC achieves same result with 2 generation scripts + 1 runner script.
- **Risk**: 
  - More scripts = more maintenance burden
  - Inter-script dependencies increase failure points
  - Overkill for a benchmark test
- **Evidence**: POC is simpler and works. SPEC adds `02_render_prompts.py` (could be inline), separates evaluation into own script (could be a function).
- **Suggested action**: Consider consolidating. Data generation + prompt rendering could be one script. Evaluation could be a module, not separate script.

### `TBLF-RV-007` Missing Output Format Specification

- **Location**: Task Prompt Template, TBLF-FR-04
- **What**: SPEC shows expected output format but doesn't specify how strictly it should match. POC uses explicit "MANDATORY" language and "CRITICAL REQUIREMENTS".
- **Risk**: LLM may produce valid extractions in unexpected format, causing false negatives
- **Evidence**: POC prompt (lines 1-11) includes:
  - "You MUST extract ALL matching employees"
  - "Do NOT truncate, summarize, or stop early"
  - "Do NOT add any text before or after the numbered list"
- **Suggested action**: Strengthen task prompt template with explicit constraints and mandatory language.

### `TBLF-RV-008` Unclear Column Selection Logic

- **Location**: TestConfig schema, TBLF-FR-01
- **What**: SPEC says "columns_to_extract": 7 but doesn't specify WHICH 7 columns or how they're selected.
- **Risk**: Random column selection could produce inconsistent tests
- **Evidence**: POC explicitly requests: EmployeeID, FullName, Department, Salary, SecurityClearance, PerformanceRating, Projects
- **Suggested action**: Either specify fixed column list per test, or document column selection algorithm.

## Low Priority

### `TBLF-RV-009` Missing Error Recovery in Pipeline

- **Location**: Pipeline Flow section
- **What**: SPEC shows happy path but doesn't address partial failures.
- **Risk**: If 03_execute_llm.py fails on run 7/10, what happens to runs 1-6?
- **Suggested action**: Add error handling requirements. Consider transaction-like behavior or explicit failure modes.

### `TBLF-RV-010` No Warm-up Run Consideration

- **Location**: TBLF-FR-03
- **What**: First LLM API call may have higher latency due to cold start. This could affect timing metrics.
- **Suggested action**: Consider adding warm-up run option, or documenting that first run may be an outlier.

## Industry Research Findings

### LLM-as-Judge Reliability

- **Pattern found**: LLM judges are unreliable for tasks where correct answers are enumerable. They exhibit position bias, verbosity bias, and can be fooled by formatting.
- **How it applies**: SPEC proposes LLM judge for extraction evaluation where correct answers ARE enumerable (specific employee IDs). This is the exact case where deterministic evaluation is superior.
- **Source**: Weights & Biases "Exploring LLM-as-a-Judge" (2025)

### Key quote

> "When correct answers are known and enumerable, such as math problems, factual queries with verifiable answers, or code that must pass tests, traditional metrics or rule-based checking is more reliable and cheaper than LLM judges."

### Alternatives Considered

- **Deterministic regex/parsing (POC approach)**: Pros: Fast, reliable, reproducible, zero cost. Cons: May miss format variations. **Verdict: Better for this use case.**
- **LLM judge (SPEC approach)**: Pros: Handles format variations. Cons: Slow, costly, non-deterministic, can be fooled. **Verdict: Wrong tool for structured data extraction testing.**
- **Hybrid approach**: Deterministic primary + LLM judge for edge cases. Pros: Best of both. Cons: Added complexity.

## Recommendations

### Must Do

- [ ] Replace LLM judge with deterministic evaluation (TBLF-RV-001)
- [ ] Use fixed filter criteria instead of random (TBLF-RV-002)
- [ ] Add adversarial data patterns requirement (TBLF-RV-003)
- [ ] Add token counting and context window tracking (TBLF-RV-004)

### Should Do

- [ ] Add ground truth verification step (TBLF-RV-005)
- [ ] Strengthen task prompt with mandatory language (TBLF-RV-007)
- [ ] Specify exact columns to extract (TBLF-RV-008)

### Could Do

- [ ] Consolidate 5 scripts to 3 (TBLF-RV-006)
- [ ] Add error recovery requirements (TBLF-RV-009)
- [ ] Add warm-up run option (TBLF-RV-010)

## Document History

**[2026-03-05 17:55]**
- Initial review created
- Compared against POC at `IPPS/_PrivateSessions/_2026-03-04_LLMMarkdownOptimization/poc`
- Conducted industry research on LLM-as-Judge patterns
