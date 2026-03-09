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

## API Keys and Rate Limits

**.env file location**: `01_CSVScaleLimits/.env`

### OpenAI Rate Limits by Tier [VERIFIED]

Source: https://community.openai.com/t/increased-gpt-5-and-gpt-5-mini-rate-limits/1357840

**gpt-5**:
- Tier 1: 500K TPM (1.5M batch)
- Tier 2: 1M TPM (3M batch)
- Tier 3: 2M TPM
- Tier 4: 4M TPM

**gpt-5-mini**:
- Tier 1: 500K TPM (5M batch)

**gpt-4o / gpt-4o-mini**: ~500 RPM, 200K-2M TPM (tier dependent)

### Anthropic Rate Limits [VERIFIED]

Source: https://northflank.com/blog/claude-rate-limits-claude-code-pricing-cost

Anthropic uses tier-based restrictions:
- RPM (Requests Per Minute)
- TPM (Tokens Per Minute) 
- Daily token quota

Higher tiers after meeting spending thresholds.

### Tested Worker Limits (2026-01-26) [TESTED]

Source: `.windsurf/skills/llm-evaluation/LLM_EVALUATION_TESTED_MODELS.md`

Burst capacity tested via `find-workers-limit.py`:
- **gpt-5-nano**: 120+ workers, ~402K TPM
- **gpt-5-mini**: 120+ workers, ~164K TPM
- **claude-haiku-4-5**: 60+ workers, ~450K TPM
- **claude-sonnet-4-5**: 60+ workers, ~467K TPM
- **claude-opus-4-5**: 60+ workers, ~473K TPM

### Cascade Limitation [TESTED 2026-03-09]

**Windsurf Cascade can only run 3-4 background commands simultaneously.**

For Test 02 (35 parallel tests), use one of:
1. **PowerShell script** - `run_all_tests.ps1` runs all 35 in separate PowerShell jobs
2. **Manual terminals** - Open 35 terminal windows manually
3. **Batch execution** - Run 3-4 tests at a time through Cascade

### Parallel Execution Strategy

With 120+ workers tested for OpenAI and 60+ for Anthropic, **all 12 tests can run simultaneously**:

```
Terminal 1:  gpt-4o-mini (T01)      Terminal 7:  gpt-5 high (T07)
Terminal 2:  gpt-5-mini medium (T02) Terminal 8:  gpt-4o (T08)
Terminal 3:  gpt-5-mini low (T03)   Terminal 9:  gpt-5.2 (T09)
Terminal 4:  gpt-5-mini high (T04)  Terminal 10: claude-haiku (T10)
Terminal 5:  gpt-5 medium (T05)     Terminal 11: claude-sonnet (T11)
Terminal 6:  gpt-5 low (T06)        Terminal 12: claude-opus (T12)
```

**Total time: ~15-20 minutes** (single test duration) vs 3 hours sequential

**Check your tier**: 
- OpenAI: https://platform.openai.com/settings/organization/limits
- Anthropic: https://console.anthropic.com/settings/limits

## Workflows to Run on Resume

1. Run larger scale tests (100, 300, 600 rows)
2. Compare different models (gpt-5-mini vs others)
3. Test different tabular formats (CSV baseline established)