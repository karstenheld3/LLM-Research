# Format Comparison (Mar 2026 - May 2026)

## Research Question

How do different tabular data formats (CSV, JSON, YAML, XML, TOML, Markdown, KV) compare in LLM extraction accuracy at scale?

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
4. See `spec.md` and `test-plan.md` for full methodology
