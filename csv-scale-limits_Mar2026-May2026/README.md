# CSV Scale Limits (Mar 2026 - May 2026)

## Research Question

What are the scale limits of LLMs when extracting tabular data from CSV format? At what row count does accuracy degrade significantly?

## Timespan

March 2026 - May 2026 (derived from test result file timestamps)

## Status

Complete

## Key Findings

See `results/` folder for detailed test results and findings.

## Reproduction

1. Copy `config/env-file-template.txt` to `.env` and fill in API keys
2. Run `scripts/01_generate_data.py` to generate test data
3. Run `scripts/02_execute_and_evaluate.py` to execute tests
4. Run `scripts/03_find_scale_limit.py` to analyze results
5. See `spec.md` and `test-plan.md` for full methodology
