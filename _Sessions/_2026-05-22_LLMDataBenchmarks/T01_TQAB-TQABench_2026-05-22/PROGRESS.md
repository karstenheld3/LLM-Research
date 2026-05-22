# Topic Progress: TQA-Bench

**Doc ID**: 2026-05-22_TQAB-TQABench-PROGRESS

## Phase Plan

- [x] **Phase 1** - done - Preflight (decompose, sources, assumptions)
- [x] **Phase 2** - done - Planning (summary, template, TASKS)
- [x] **Phase 3** - done - Research (topic files with model results)
- [x] **Phase 4** - done - Final verification, download data

## To Do

(none remaining)

## In Progress

(none)

## Done

- [x] Topic folder created
- [x] Initial problems identified from survey findings
- [x] Collected 7 sources (paper HTML, GitHub repo, code files, EmergentMind)
- [x] Read full paper (all sections) via arxiv HTML
- [x] Analyzed code: serialization (database.py), evaluation (utils.py), prompts
- [x] Extracted model results: 22 models, GPT-4o 78.7%→63.4% (8K→64K)
- [x] CRITICAL: Discovered TQA-Bench DOES test format (Markdown vs CSV) - corrected survey
- [x] Created 6 INFO files (summary, sources, methodology, format results, model results, replication)
- [x] Corrected parent `_INFO_BenchmarkSurvey.md` (3 lines updated)
- [x] Created `_DOWNLOADS_gitignore/README.md` with dataset download links

## Progress Changes

**[2026-05-22 13:40]**
- Completed all 4 phases of deep research
- Major finding: TQA-Bench tests format (Markdown vs CSV) - our initial survey was wrong
- 5 hypotheses generated for future experiments
- Relevance score: 9/10

**[2026-05-22 13:29]**
- Created topic folder with tracking files
