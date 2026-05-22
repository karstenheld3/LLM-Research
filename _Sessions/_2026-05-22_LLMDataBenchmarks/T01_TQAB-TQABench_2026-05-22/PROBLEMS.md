# Topic Problems: TQA-Bench

**Doc ID**: 2026-05-22_TQAB-TQABench-PROBLEMS

## Open

**TQAB-PR-0001: What exact serialization format does TQA-Bench use for tables?**
- **History**: Added 2026-05-22
- **Description**: Survey noted "likely markdown or linearized tables" but format is unconfirmed
- **Impact**: Determines comparability with our format-sensitive findings
- **Next Steps**: Read paper and code to confirm exact format

**TQAB-PR-0002: What are the per-model accuracy results across context sizes?**
- **History**: Added 2026-05-22
- **Description**: Need detailed accuracy breakdowns for each model at each context size (8K-64K)
- **Impact**: Direct comparison with our scale degradation curves
- **Next Steps**: Extract results tables from paper

**TQAB-PR-0003: Can TQA-Bench be extended to test format sensitivity?**
- **History**: Added 2026-05-22
- **Description**: If we adapt their pipeline to vary input format, we could validate our findings on multi-table tasks
- **Impact**: Novel experimental contribution
- **Next Steps**: Analyze code architecture for format injection points

## Resolved

(none)

## Deferred

(none)

## Problems Changes

**[2026-05-22 13:29]**
- Added: TQAB-PR-0001 through TQAB-PR-0003 (initial problem decomposition)
