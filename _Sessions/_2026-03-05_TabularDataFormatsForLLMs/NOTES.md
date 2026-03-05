# Session Notes

## Session Info

- **Started**: 2026-03-05
- **Goal**: Research which tabular data format can be most effectively read, understood, and processed by LLMs

## User Prompt (Verbatim)

> which tabular data format can be most effectively read and understood and processed by llms

## Current Phase

**Phase**: IMPLEMENT
**Next**: Continue testing
**Assessment**: Pipeline working, logging compliant

## Research Questions

1. Which tabular formats do LLMs handle best? (CSV, JSON, XML, YAML, Markdown tables, etc.)
2. How does format choice affect extraction accuracy?
3. Does format performance vary by task type? (lookup, aggregation, filtering)
4. What scale limits exist per format?
5. Are there model-specific preferences?

## Test Structure

Tests are collections of configurable scripts that produce and process data.

```
[REPO]/
├── _Sessions/                    # Session tracking
├── 01_TestA/                     # Test folder (NN_ prefix)
│   ├── _Scripts/                  # Shared test scripts
│   ├── _PromptsAndTemplates/                 # Prompt templates
│   ├── test-config-template.json          # Common test configuration template
│   ├── 001_gpt-5-mini_configA/             # Test instance
│   │   ├── test-config.json      # Instance-specific config
│   │   ├── 01_InputData/         # Workflow step (NN_ prefix)
│   │   ├── 02_PromptsAndTemplates/
│   │   ├── 03_Responses/
│   │   ├── 04_ResponseEvaluations/
│   │   └── 05_Summaries/
│   └── 002_gpt-5-mini_configB/
│       └── ...
├── 02_TestB/
│   └── ...
└── README.md
```

**Naming conventions:**
- Test folders: `NN_[TestName]` (e.g., `01_TabularFormatExtraction`)
- Workflow step folders: `NN_[StepName]` (e.g., `02_PromptsAndTemplates`)
- Test instances contain their own `test-config.json` overrides

## Key Decisions

- Use `max_completion_tokens` for gpt-5 models (not `max_tokens`)
- 20 rows / 2 runs is sufficient for quick validation tests

## Important Findings

- [TESTED] gpt-5-mini achieves 100% accuracy (P=1.00, R=1.00, F1=1.00) on 20 rows with AND filter logic
- [TESTED] Logging must follow Full Disclosure principle - each line self-contained
- [TESTED] Parallel execution requires `[ x / y ]` prefix on Report lines (results arrive out of order)

## Related Research

See `IPPS/_PrivateSessions/_2026-03-04_LLMMarkdownOptimization/TASKS_FORMAT_TESTING.md` for prior benchmark:
- TK-001 tested 10 formats at 300 records
- Finding: `::` separator optimal, XML/Markdown tables highest variance
- Key-value and CSV most reliable

## Workflows to Run on Resume

1. Run larger scale tests (100, 300, 600 rows)
2. Compare different models (gpt-5-mini vs others)
3. Test different tabular formats (CSV baseline established)
