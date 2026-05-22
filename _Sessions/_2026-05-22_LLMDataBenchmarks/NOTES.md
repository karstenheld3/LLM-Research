# Session Notes

**Doc ID**: 2026-05-22_LLMDataBenchmarks-NOTES

## Initial Request

````text
I want to conduct a research consisting of multiple deep-research calls about benchmarks on the internet that measure the data handling capability of the models tested here. Primarily only Open AI and Anthropic.

Identify topics that we deep-research individually and later combine findings to identify more hypotheses that we can confirm or contradict by our own research results.

Look specifically how Open ai and Anthropic are benchmarking their models.

We will research each benchmark methodology independently. For now we just need an overview of all llm data processing and analysis benchmarks out there.

DO NOT include benchmarks that measure non-reasoning models. We only need the ones like our tests that are deep, replicatable and mind the data format and reasoning effort settings.
````

## Session Info

- **Started**: 2026-05-22
- **Goal**: Research external LLM data processing benchmarks (OpenAI/Anthropic) to identify hypotheses testable with our TabularDataFormats methodology
- **Operation Mode**: IMPL-ISOLATED
- **Output Location**: This session folder
- **Related Session**: `_2026-03-05_TabularDataFormatsForLLMs` (source of empirical findings)

## Current Phase

**Phase**: EXPLORE
**Workflow**: `/deep-research` (benchmark survey)
**Assessment**: Prompt prepared, ready for execution

## IMPORTANT: Cascade Agent Instructions

- Only include benchmarks relevant to reasoning models (gpt-5 family, Claude thinking models)
- Exclude benchmarks for non-reasoning models (gpt-4o, base models without CoT)
- Focus on benchmarks that test: data extraction, tabular comprehension, structured data processing
- Must be replicatable with known methodology
- Must consider data format and/or reasoning effort as variables
- Each benchmark methodology gets its own deep-research call
- Final synthesis combines findings into testable hypotheses

## Key Decisions

- Research as standalone session (not topic folder inside TabularDataFormats session)
- Topic ID: `DATBMRS` registered in ID-REGISTRY.md

## Important Findings

From `_INFO_BenchmarkSurvey.md [DATBMRS-IN02]`:

- NO benchmark tests input FORMAT as independent variable - our 8-format comparison is unique
- NO benchmark uses binary search for scale limits - all use fixed difficulty
- Only OpenAI/Anthropic system cards test reasoning effort - no independent benchmark does
- Most benchmarks tested GPT-4o era models, NOT gpt-5 family reasoning models
- NoLiMa: 10/12 models effective length <= 2K tokens despite claiming 128K (validates our finding)
- Anthropic: accuracy scales LOGARITHMICALLY with thinking tokens (matches our concave effort curve)

## Recommended Deep-Dives (prioritized)

1. **TQA-Bench** `[TQAB]` - Most comparable. Run with gpt-5 + re-serialize tables in our 8 formats. Hypothesis: "Does format sensitivity persist on multi-table join tasks?"
2. **NoLiMa** - Explains our primary failure mode. Hypothesis: "Do models extract data via pattern matching or semantic understanding?"
3. **OpenAI effort curves** - Replicate GPQA Diamond at all effort levels. Hypothesis: "Is effort-scaling steeper for data extraction than for reasoning tasks?"
4. **Anthropic budget_tokens** - Test our tasks with explicit budgets. Hypothesis: "Does data extraction follow log-scaling law?"
5. **BABILong** - Embed our task in varying context. Hypothesis: "Does our attention bottleneck match their degradation curve?"

## Topic Registry

- `DATBMRS` - LLM Data Processing Benchmarks (external research)

## Topic Folders

- T01_TQAB-TQABench_2026-05-22: Deep research on TQA-Bench benchmark (MCPI)
- T02_NOLIMA-NoLiMaBenchmark_2026-05-22: NoLiMa deep-research (7 INFO files, complete)

## Step Folders

Research will proceed as sequential deep-research steps:

- **S01** - Overview: identify all relevant benchmarks (prompt prepared)
- **S02+** - Individual deep-research per benchmark methodology

## Bug List

- (none)

## Significant Prompts Log

- `_PROMPT_InitialBenchmarkSurvey.md` - Main deep-research prompt for benchmark landscape survey
