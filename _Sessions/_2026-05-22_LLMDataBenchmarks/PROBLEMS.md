# Session Problems

**Doc ID**: 2026-05-22_LLMDataBenchmarks-PROBLEMS

## Open

**DATBMRS-PR-0001: Unknown landscape of LLM data processing benchmarks**
- **History**: Added 2026-05-22 12:45
- **Description**: No comprehensive overview exists of benchmarks that specifically measure reasoning model data handling capability (extraction, filtering, comprehension at scale)
- **Impact**: Cannot correlate our findings with external benchmarks or identify gaps in our methodology
- **Next Steps**: Execute deep-research with `_PROMPT_InitialBenchmarkSurvey.md`

**DATBMRS-PR-0002: How do OpenAI and Anthropic benchmark their own models for data tasks?**
- **History**: Added 2026-05-22 12:45
- **Description**: Need to identify OpenAI's and Anthropic's internal/published benchmark methodologies for evaluating data processing capability of reasoning models
- **Impact**: Their methodologies may reveal variables we haven't tested, or our results may contradict their claims
- **Next Steps**: Research OpenAI model cards, Anthropic technical reports for benchmark details

**DATBMRS-PR-0003: Which external benchmarks test format sensitivity?**
- **History**: Added 2026-05-22 12:45
- **Description**: Our Test 02 found up to 5.8x scale difference based on input format. Need to find if any external benchmark measures this variable
- **Impact**: If no benchmark tests format sensitivity, our research fills a gap. If some do, we can compare methodologies
- **Next Steps**: Filter benchmark landscape for format-aware evaluations

**DATBMRS-PR-0004: Which benchmarks test reasoning effort / thinking budget impact?**
- **History**: Added 2026-05-22 12:45
- **Description**: Our Test 01 showed 10x improvement from low to high effort (gpt-5-mini). Need to find external benchmarks that vary this parameter
- **Impact**: Validates or contradicts our effort-scaling findings
- **Next Steps**: Search for benchmarks that parameterize CoT depth or thinking budget

**DATBMRS-PR-0005: Identify testable hypotheses from benchmark comparison**
- **History**: Added 2026-05-22 12:45
- **Description**: After gathering benchmark data, synthesize findings into hypotheses we can test with our existing pipeline
- **Impact**: Drives next round of experiments (Test 03+)
- **Next Steps**: Blocked by DATBMRS-PR-0001 through DATBMRS-PR-0004

## Resolved

(none)

## Deferred

(none)

## Problems Changes

**[2026-05-22 12:45]**
- Added: DATBMRS-PR-0001 through DATBMRS-PR-0005 (initial problem decomposition)
