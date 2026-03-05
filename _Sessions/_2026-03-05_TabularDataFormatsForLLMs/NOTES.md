# Session Notes

## Session Info

- **Started**: 2026-03-05
- **Goal**: Research which tabular data format can be most effectively read, understood, and processed by LLMs

## User Prompt (Verbatim)

> which tabular data format can be most effectively read and understood and processed by llms

## Current Phase

**Phase**: EXPLORE
**Workflow**: /deep-research (pending)
**Assessment**: RESEARCH - need empirical data on LLM tabular data comprehension

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
│   ├── _SromptsAndTemplates/                  # Shared test scripts
│   ├── test-config.json          # Common test configuration
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

## Important Findings

## Related Research

See `IPPS/_PrivateSessions/_2026-03-04_LLMMarkdownOptimization/TASKS_FORMAT_TESTING.md` for prior benchmark:
- TK-001 tested 10 formats at 300 records
- Finding: `::` separator optimal, XML/Markdown tables highest variance
- Key-value and CSV most reliable

## Workflows to Run on Resume

1. Continue research on tabular format effectiveness
