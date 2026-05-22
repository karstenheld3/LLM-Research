# Topic Notes: TQA-Bench Deep Research

**Doc ID**: 2026-05-22_TQAB-TQABench-NOTES

## Topic Info

- **Started**: 2026-05-22
- **Goal**: Exhaustive research on TQA-Bench benchmark - methodology, model results, replicability, relevance to our tabular format research
- **Operation Mode**: IMPL-ISOLATED
- **Strategy**: MCPI (exhaustive)
- **Domain**: SOFTWARE
- **Parent Session**: `_2026-05-22_LLMDataBenchmarks`

## Current Phase

**Phase**: DELIVER (complete)
**Workflow**: `/deep-research` (MCPI) - finished

## Key URLs

- Paper: https://arxiv.org/abs/2411.19504
- Code: https://github.com/Relaxed-System-Lab/TQA-Bench

## Topic Registry

- `TQAB` - TQA-Bench benchmark (multi-table QA with scalable context)

## Important Findings

- TQA-Bench DOES test format (Markdown vs CSV) - corrected our initial survey
- Markdown outperforms CSV by 5.74pp for GPT-4o at 8K tokens
- Scale degradation: GPT-4o 78.7% (8K) to 63.4% (64K) - gradual, not binary cliff
- No reasoning models tested (paper predates o1/o3/gpt-5)
- Code is fully open, dataset downloadable, GPL-3.0 license
- 5 testable hypotheses generated for our pipeline

## Bug List

- (none)
