<DevSystem MarkdownTablesAllowed=true />

# Problems Found - Devil's Advocate Review

**Reviewed**: 2026-05-22 19:00
**Context**: Full methodology critique of tabular data format research (Test 01 + Test 02), pipeline design, and production recommendation validity
**Scope**: Approach, reasoning, scientific validity, practical usefulness

## MUST-NOT-FORGET

1. TBLF-FL-005: Column config mismatch (7/7 vs 7/20) invalidates cross-test comparisons
2. n=3 runs per binary search iteration, ~28% observed variance between independent runs
3. One task type across all 75 tests (7-column, compound filter, 20% adversarial)
4. User question: overengineered? Will it produce usable real-world recommendations?
5. Model versions change silently; format preferences shift between generations

## MUST-RESEARCH

1. **Statistical validity with n=3** - Anthropic (2024) and Bowyer et al. (2025) show CLT invalid for small n
2. **Binary search as eval methodology** - Novel approach, no precedent in LLM evaluation literature
3. **Format sensitivity** - Sclar (ICLR 2024) confirms format matters (up to 76% variance on older models)
4. **Production chunking patterns** - Standard practice is chunk+merge, not single-shot at scale
5. **Benchmark reproducibility** - Miller (2024) shows evaluations need standard errors and power analysis

## Industry Research Findings

**Source: Miller (2024) "A Statistical Approach to Language Model Evaluations" (Anthropic)**
- LLM evaluations MUST report standard errors alongside results
- CLT-based confidence intervals are "overly confident" for small n (Bowyer et al. 2025 recommends "a few hundred datapoints")
- When comparing models, paired difference analysis yields more confident results than separate aggregate scores
- Power analysis should determine sample size BEFORE running experiments

**Source: Sclar et al. (ICLR 2024) "Quantifying Language Models' Sensitivity to Spurious Features"**
- Confirms format sensitivity is real (up to 76% accuracy variance from formatting alone)
- BUT: tested on classification/QA tasks, not structured extraction at scale
- Key insight: sensitivity decreases with model capability - consistent with E3 finding

**Source: Production LLM extraction patterns (LlamaIndex, Unstract, community)**
- Chunking is standard for documents exceeding context windows
- JSON mode / structured output is preferred over free-text extraction
- Nobody in production cares about "scale limit" - they chunk to fit comfortably within 30-50% context

## Critical Issues

### C1: "Scale Limit" Is Not a Meaningful Scientific Metric

**SOCAS-ID**: SOCAS-LOG-C1
**Severity**: CRITICAL
**Category**: Flawed Methodology

The "scale limit" (max reliable rows via binary search) is treated as a stable property of a model+format pair. It is not. It is a noisy measurement of the entire system: model + format + prompt + data seed + column schema + filter logic + adversarial content + output token limit + reasoning effort.

**Why this matters**: The 5.8x format spread (gpt-5.2: csv_quoted 268 vs toml 46) could be partially or entirely explained by:
- Prompt wording interacting differently with formats
- Specific adversarial content in seed=42 data triggering format-specific parse errors
- Token count differences (XML uses 2.12x tokens, providing more redundancy)
- Random variance amplified by the binary search stopping criterion

**The metric confuses "where does the binary search stop" with "inherent format capability."** A different prompt, different seed, or different column schema could produce entirely different rankings.

### C2: n=3 Per Iteration Makes Most Comparisons Statistically Meaningless

**SOCAS-ID**: SOCAS-LOG-C2
**Severity**: CRITICAL
**Category**: Statistical Validity

With n=3 verification runs and ~28% measured variance between independent binary searches:

- A model with 80% reliability at N rows passes 3/3 runs with P=0.51. The binary search treats this as "reliable."
- Minimum detectable effect with n=3 is far larger than most format differences being compared
- Example: gpt-5.2 csv_quoted (268) vs xml (261) = 2.7% difference. With 28% variance, this is **indistinguishable from noise**. Yet csv_quoted is declared "BEST."
- Example: gpt-5.5 csv (494) vs csv_quoted (491) = 0.6% difference. Listed as different ranks in tables.

**Per Anthropic's own evaluation paper**: "If the value of n is small, then the CLT-based standard error expression is overly confident." No standard errors are reported anywhere in either INFO document.

**What would be needed**: Either (a) run n=10-30 per iteration, or (b) report confidence intervals and stop making rank-order claims within the noise band.

### C3: Single Task Type Makes Format Rankings Non-Generalizable

**SOCAS-ID**: SOCAS-LOG-C3
**Severity**: CRITICAL
**Category**: External Validity

All 75 tests use: 7 columns, compound filter (clearance IN [3,4,5] AND salary >= 150K), 20% adversarial content, seed=42. The findings claim format rankings for "production use" but:

- Different column counts (5 vs 50 vs 500) will change which formats hit token limits first
- Different filter complexity (simple lookup vs multi-condition vs aggregation) stress different model capabilities
- Different data types (all-numeric, all-text, mixed) may favor different formats
- The adversarial content (20%) is a specific challenge that may interact with formats differently

**H4 (format depends on complexity) is listed as INCONCLUSIVE**, yet the recommendations ignore this entirely. "Use toml for gpt-5.5" is advice for exactly one task shape.

## High Priority

### H1: Production Recommendations Ignore Chunking (The Actual Solution)

**SOCAS-ID**: SOCAS-LOG-H1
**Severity**: HIGH
**Category**: Practical Relevance

Production systems don't care about single-shot scale limits. They chunk:
- 1000-row table -> 3 x 333-row chunks -> merge results
- This is acknowledged in Open Question #4 but NEVER tested

This means the entire cost/time optimization is wrong:
- A cheap model (gpt-5-mini, $0.008/req) chunking 3x at 300 rows = $0.024 for 900 rows
- An expensive model (opus-4.6 high, $0.81/req) single-shot at 667 rows = $0.81
- The cheap chunked approach is 34x cheaper and handles more rows

The Pareto analysis, production profiles, and CPKC metric are all computed for single-shot only. In production, the optimal strategy is almost certainly "cheapest reliable model + chunking."

### H2: Model Version Instability Makes Specific Recommendations Ephemeral

**SOCAS-ID**: SOCAS-LOG-H2
**Severity**: HIGH
**Category**: Temporal Validity

The data shows gpt-5.4 prefers json (702), gpt-5.5 prefers toml (828, json drops 39%). This proves that any specific model+format recommendation expires with the next model version. The findings acknowledge this but then still publish specific recommendations.

**Shelf life of these recommendations**: Unknown. Could be weeks (silent API updates) to months (version bumps). The only durable finding is "format matters, test your setup" - which requires ~1 hour of testing per model, not a 75-test research project.

### H3: TBLF-FL-005 Is Still Active - Cross-Test Conclusions Are Invalid

**SOCAS-ID**: SOCAS-LOG-H3
**Severity**: HIGH
**Category**: Data Integrity

Test 01 uses 7/20 columns (selecting 7 from 20 available). Test 02 uses 7/7 columns. This means:
- Test 01 CSV baseline (gpt-5-mini: 500) is NOT comparable to Test 02 csv results (gpt-5-mini: 194)
- The Test 01 "H6: CSV best format?" hypothesis cannot be evaluated using Test 02 data
- Any statement about "CSV performance relative to other formats" that references Test 01 data is invalid

The fix (re-run all 56 tests with 7/20 columns) has not been implemented. This is a known open issue.

## Medium Priority

### M1: Format Comparison Conflates Format With Token Count

**SOCAS-ID**: SOCAS-LOG-M1
**Severity**: MEDIUM
**Category**: Confounding Variable

XML uses 2.12x the tokens of CSV for the same data. When XML "outperforms" CSV (e.g., gpt-5: xml 327 vs csv 166), this could mean:
- XML structure genuinely aids comprehension (format effect)
- Extra tokens provide redundancy that helps the model (token count effect)
- XML tokenization is more efficient for this model (tokenizer effect)

Without a control (e.g., testing CSV with padding to match XML token count), "format preference" is confounded with "token budget allocation preference." The H5 analysis acknowledges this indirectly but doesn't propose the control experiment.

### M2: Pipeline Complexity Exceeds Scientific Rigor

**SOCAS-ID**: SOCAS-LOG-M2
**Severity**: MEDIUM
**Category**: Overengineering

The infrastructure includes: 4-document methodology, 8+ Python scripts, PowerShell orchestration, AUTO markers, template systems, aggregation pipeline, findings generation pipeline, multiple JSON schemas, overrides.json, model registries.

This produces well-formatted documents, but the scientific content has fundamental issues (C1-C3). A Jupyter notebook with plots would produce the same analytical value with 10x less code. The pipeline makes it easy to re-run aggregation, but you can't aggregate your way out of a methodology problem.

**The pipeline is well-built for what it does.** The question is whether what it does justifies its complexity.

### M3: Emergent Hypothesis E3 (Sensitivity-Capability Correlation) Is Circular

**SOCAS-ID**: SOCAS-LOG-M3
**Severity**: MEDIUM
**Category**: Logic Error

E3 claims: "Format sensitivity inversely correlates with model capability." Evidence: gpt-5.2 has 5.8x ratio (low capability), opus-4.5 has 1.5x (high capability).

But "capability" here is defined BY the scale limit, and sensitivity ratio IS the spread of scale limits. A model with uniformly low scale limits across formats has low sensitivity AND low capability. This is a mathematical relationship, not a causal finding. It's like saying "the range of exam scores inversely correlates with the minimum exam score" - trivially true when all scores are small.

## Questions That Need Answers

1. **Would a different random seed change the format rankings?** Seed=42 is used throughout. If seed=43 produces different rankings, the findings are artifacts of the specific data, not format properties.

2. **What is the actual reliability at the "confirmed" row count?** If the model passes 3/3 at N rows, the reliability could be anywhere from ~70% (P(3/3)=0.34) to 99%+ (P(3/3)=0.97). What's the true reliability? 10-30 runs at the confirmed point would answer this.

3. **Does chunking eliminate the need for format optimization?** If 3x chunks with the cheapest model beats single-shot with the best format, the entire format comparison is academically interesting but practically irrelevant.

4. **What's the minimum test battery for a practitioner?** If "always test your model+format" is the only valid recommendation, how many tests does a practitioner need? 3 formats x 1 model x n=5 = 15 runs? That's a much simpler recommendation than this project suggests.

## What IS Valid and Valuable

Despite the above, several findings survive scrutiny:

1. **Format matters significantly** (5.8x observed, even accounting for noise the effect is clearly large) - confirmed by Sclar (2024) independently
2. **No universal best format** - durable finding, unlikely to change
3. **Temperature models unsuitable for structured extraction** (83x difference) - effect too large to be noise
4. **Reasoning effort matters enormously** (111x for Claude Opus) - effect too large to be noise
5. **Claude adaptive_thinking at medium effort is catastrophic** - specific, actionable, verified with API-level explanation
6. **Format preference is model-family specific** (GPT vs Claude inversions) - consistent pattern across enough models to be credible
7. **The research question itself is valuable** - few have systematically tested this

## Verdict: Overengineered? Usable?

**Overengineered**: Yes, the documentation/pipeline infrastructure exceeds the scientific rigor. The 4-document methodology + AUTO markers + aggregation scripts are well-built engineering for a research project that lacks statistical controls. A simpler setup with better statistics would produce stronger conclusions.

**Usable production recommendations**: Partially.
- **Durable** (use these): Format matters, test your model, avoid temperature models, reasoning effort matters, no universal best format
- **Ephemeral** (treat as hints): Specific model+format pairings, row count limits, cost projections
- **Missing** (needed for production): Chunking comparison, multi-task validation, confidence intervals, different column schemas

## Document History

**[2026-05-22 19:00]**
- Initial review: Full methodology critique covering statistical validity, metric definition, task generalizability, production relevance, and overengineering assessment

