# TEST: CSV Scale Limits - Devil's Advocate Review

**Doc ID**: TBLF-TP01-RV01
**Goal**: Find flawed assumptions, logic errors, and hidden risks in the test plan
**Reviewed**: 2026-03-05 23:50
**Context**: Review of test plan for 8 models, 6 hypotheses, 12 configurations

## MUST-NOT-FORGET

1. Binary search finds ONE boundary, not the full degradation curve
2. Each test run costs real money (~$3 total estimate)
3. TK-001 prior data showed 43% failure rate at 600 rows (bimodal)
4. Single runs have high variance due to LLM non-determinism
5. Anthropic models use different methods (thinking vs effort) than OpenAI

## MUST-RESEARCH

1. **LLM benchmark reproducibility** - How many runs needed for statistically significant results?
2. **Binary search in noisy environments** - Does binary search work when outcomes are probabilistic?
3. **Cross-provider comparison validity** - Can OpenAI and Anthropic models be fairly compared?
4. **API rate limits and throttling** - Will batch runs hit rate limits?
5. **Cost estimation accuracy** - Are token estimates realistic for 300+ row CSVs?

## Critical Issues

### `TBLF-TP-RV-001` Binary Search Assumes Deterministic Outcomes

- **Location**: Section 3.1, entire binary search approach
- **What**: Binary search assumes a clear pass/fail boundary. But TK-001 showed bimodal behavior - at 600 rows, runs either succeed completely OR fail completely (43% failure rate).
- **Risk**: Binary search with n=1 per step will oscillate randomly at the boundary. The "scale limit" found will depend on luck, not actual model capability.
- **Evidence**: TK-001 v5: "bimodal behavior - runs either near-perfect or complete failure"
- **Suggested action**: 
  1. Use majority voting (3 runs per step) or
  2. Use probabilistic binary search (track success rates)
  3. Document that results have ~10% margin of error

### `TBLF-TP-RV-002` Cost Estimates Assume 300 Rows, But Search Goes Higher

- **Location**: Section 6.1
- **What**: Cost estimates assume ~5000 input tokens per iteration (300 rows * 15 tokens). But binary search will test higher row counts (450, 600+) as it searches upward.
- **Risk**: Actual costs could be 2-3x higher than estimates for models that pass at high row counts.
- **Evidence**: If gpt-5 handles 600 rows, that's 2x the tokens per iteration.
- **Suggested action**: Add 2x buffer to cost estimates, or note "estimates assume 300-row baseline"

### `TBLF-TP-RV-003` H5 Comparison May Be Invalid - Different Architectures

- **Location**: Section 2.2, H5 hypothesis
- **What**: H5 compares gpt-4o (temperature) vs gpt-5 (reasoning). But these are fundamentally different architectures, not just parameter differences.
- **Risk**: Comparing them is like comparing a sedan to a truck and concluding "trucks are better at hauling". The comparison doesn't isolate reasoning vs temperature - it conflates architecture, training data, and parameter count.
- **Evidence**: gpt-5 is a newer model generation with more parameters and different training.
- **Suggested action**: Either:
  1. Acknowledge this limitation explicitly
  2. Compare gpt-4.1 (temp) vs gpt-4.1 with reasoning_effort if available
  3. Rename H5 to "Newer models handle higher scale" (honest framing)

## High Priority

### `TBLF-TP-RV-004` No Baseline Validation Step in Automated Batch

- **Location**: Section 5.1 batch-config.json
- **What**: The batch config jumps straight to T02 (gpt-5-mini at 300 rows). If gpt-5-mini can't handle 300 rows at medium effort, the entire test suite produces garbage.
- **Risk**: Wasted money and time if baseline assumption is wrong.
- **Evidence**: INFO says TK-001 showed reliability at 300 rows, but that was a different test (not this exact prompt/data).
- **Suggested action**: Add explicit baseline validation: T01 must pass before T02-T12 run.

### `TBLF-TP-RV-005` Anthropic Models May Not Support `reasoning_effort`

- **Location**: Section 5.1, claude configurations use `"effort": "medium"`
- **What**: The batch config uses `reasoning_effort` for all models, but Anthropic models use different parameters (`thinking`, `effort` via beta header).
- **Risk**: Script may crash or silently ignore effort parameter for Claude models.
- **Evidence**: model-registry.json shows claude-opus-4-5 uses `"method": "effort"` with `"beta": "effort-2025-11-24"`, not `reasoning_effort`.
- **Suggested action**: Verify `llm_client.py` handles provider-specific effort parameters correctly.

### `TBLF-TP-RV-006` No Rate Limit Handling in Batch Execution

- **Location**: Section 4 (execution order), Section 5 (batch config)
- **What**: 12 test runs with ~10 iterations each = 120 API calls. No mention of rate limits or backoff.
- **Risk**: OpenAI allows ~60 requests/min on some tiers. Anthropic has similar limits. Batch may fail mid-run.
- **Suggested action**: Add delay between iterations or implement exponential backoff.

## Medium Priority

### `TBLF-TP-RV-007` Effort Level Comparison Only on 2 Models

- **Location**: Section 2.2
- **What**: H4 (effort affects scale) only tests gpt-5-mini and gpt-5. What about gpt-5.2 and Claude models?
- **Risk**: Results may not generalize. gpt-5.2 or Claude might show different effort-scale relationship.
- **Suggested action**: Either:
  1. Extend H4 testing to more models, or
  2. Document limitation: "H4 validated only on gpt-5 family"

### `TBLF-TP-RV-008` `--verify-runs 3` Not Implemented Yet

- **Location**: Section 4.2, command line examples
- **What**: Plan references `--verify-runs 3` flag, but this was just added as a CLI argument - the actual implementation (re-running at boundary) may not be complete.
- **Risk**: Plan depends on feature that may not work.
- **Suggested action**: Verify `03_find_scale_limit.py` actually implements verify-runs logic.

### `TBLF-TP-RV-009` No Abort Conditions for Catastrophic Failures

- **Location**: Entire test plan
- **What**: What if gpt-4o-mini fails at 50 rows in T01? Plan says "validate setup" but doesn't define what happens if validation fails.
- **Risk**: Operator may continue with broken setup, wasting money.
- **Suggested action**: Define explicit abort conditions: "If T01 fails below 30 rows, STOP and debug"

## Low Priority

### `TBLF-TP-RV-010` Output Folder Naming May Cause Collisions

- **Location**: Section 8.6
- **What**: Folder names like `gpt-5-mini_reasoning_effort_medium_max32768` don't include timestamp or run ID.
- **Risk**: Re-running tests will overwrite previous results.
- **Suggested action**: Add timestamp or run ID to folder names, or document that re-runs overwrite.

### `TBLF-TP-RV-011` No Data Retention Policy

- **Location**: Not mentioned
- **What**: 12 test runs will generate hundreds of response files, evaluation JSONs, etc.
- **Risk**: Storage bloat if not cleaned up.
- **Suggested action**: Add cleanup section or note expected storage (~50MB total).

## Industry Research Findings

### LLM Benchmark Reproducibility

- **Pattern found**: Most LLM benchmarks use n>=5 runs and report confidence intervals
- **How it applies**: Our n=1 binary search has high variance; results should include error bars
- **Source**: Standard practice in ML evaluation papers

### Binary Search in Probabilistic Settings

- **Pattern found**: "Noisy binary search" algorithms exist for probabilistic outcomes. Standard binary search can oscillate indefinitely.
- **How it applies**: Need to either increase n per step or use probabilistic bisection
- **Source**: Algorithms literature on stochastic search

### Cross-Provider Comparisons

- **Pattern found**: Fair LLM comparisons require matching token counts, not just model names
- **How it applies**: gpt-5 and claude-opus have different tokenizers - same text = different token counts
- **Source**: LLM leaderboard methodologies

## Recommendations

### Must Do

- [ ] Add explicit note that binary search results have ~10% variance
- [ ] Verify `03_find_scale_limit.py` implements `--verify-runs` logic
- [ ] Add abort conditions to Phase 1 validation

### Should Do

- [ ] Add 2x buffer to cost estimates
- [ ] Verify Anthropic effort handling in llm_client.py
- [ ] Add rate limit handling or delays between API calls

### Could Do

- [ ] Extend H4 testing to more models
- [ ] Add timestamp to output folder names
- [ ] Document storage requirements

## Summary: Key Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Binary search oscillates at boundary | High | High | n=3 per step or probabilistic search |
| Cost 2-3x higher than estimated | Medium | Medium | Add buffer, monitor during run |
| H5 comparison is architecturally confounded | High | Certain | Reframe hypothesis or acknowledge |
| Rate limits cause batch failure | Medium | Medium | Add delays between calls |
| Anthropic effort parameter incompatibility | High | Unknown | Test before batch run |

## Document History

**[2026-03-05 23:50]**
- Initial Devil's Advocate review
- 11 findings: 3 Critical, 3 High, 3 Medium, 2 Low
- Key risk: Binary search assumes deterministic outcomes but TK-001 showed bimodal behavior
