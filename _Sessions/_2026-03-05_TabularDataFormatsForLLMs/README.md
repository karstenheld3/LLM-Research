# Tabular Data Formats for LLMs

## Research Background

### The Format Problem

Recent research reveals that **prompt formatting significantly impacts LLM performance** - with up to 76 accuracy points variance from minor format changes alone (Sclar et al., ICLR 2024). This finding has profound implications for how we present tabular data to language models.

**Key research findings:**

- **Format variance is massive**: 20-65% accuracy difference on GSM8K from format changes alone (CFPO, Microsoft Research 2025)
- **No universal best format**: Format preferences don't transfer between models - what works for GPT-4 may fail for Claude
- **Scale matters**: Models reliable at 300 records become unreliable at 600 records (internal benchmark, 2026)
- **Separator style is overrated**: Despite academic claims, `:` vs `: ` vs `::` showed no measurable difference on modern frontier models

### Relevant Academic Papers

| Paper | Key Finding |
|-------|-------------|
| Sclar et al. ICLR 2024 | Format changes cause up to 76pt accuracy swings |
| Microsoft/MIT 2024 | Format preferences don't transfer across model families |
| LIFBench 2024 | Instruction-following degrades before recognition in long contexts |
| CFPO 2025 | Content-format integration outperforms either alone |

### What Our Benchmark Discovered

Testing 10 format variants (key-value, CSV, JSON, XML, YAML, Markdown tables) on data extraction tasks:

**At 300 records (reliable zone):**
- Best formats: Key-value with `::`, quoted CSV - 100% precision, zero variance
- Worst formats: XML (16% std dev), Markdown tables (4% std dev)
- Structured formats (XML, YAML) did NOT outperform simple key-value

**At 600 records (unreliable zone):**
- 43% failure rate across ALL formats
- Bimodal behavior: runs either near-perfect or complete failure
- Failure mode: output truncation, not comprehension errors

## Why This Matters

### Use Case 1: Enterprise Data Extraction

When extracting structured data from large tables (employee records, financial data, inventory):
- Need to know maximum safe row count per API call
- Must choose optimal format for reliability
- Cost implications: failed extractions waste tokens

### Use Case 2: RAG Systems with Tabular Data

Retrieval-augmented generation often returns tabular chunks:
- Format choice affects extraction accuracy
- Scale limits determine chunking strategy
- Wrong format = hallucinated or missing data

### Use Case 3: Automated Report Generation

LLMs processing CSV/Excel data for reports:
- Understanding scale limits prevents silent failures
- Format selection affects consistency across runs
- Critical for production systems requiring 100% accuracy

## Empirical Testing Approach

### Research Question

**At what scale do LLMs fail to reliably extract filtered data from CSV tables?**

### Methodology

We use **binary search** to efficiently find the reliability boundary:

1. Start at initial row count (e.g., 100 rows)
2. Run extraction task, evaluate precision/recall
3. **PASS** (100% accuracy): Increase by 1.5x
4. **FAIL**: Try midpoint between last pass and fail
5. Converge when range < 10 rows

### Task Design

The extraction task tests multiple LLM capabilities:
- **Parsing**: Read quoted CSV with adversarial characters (embedded commas, pipes, colons)
- **Filtering**: Apply compound filter (e.g., `clearance IN [Level 3,4,5] AND salary >= $150k`)
- **Output**: Return matching records with specific columns

### Metrics

- **Precision**: Correct matches / Total extracted (no false positives)
- **Recall**: Correct matches / Total expected (no missed records)
- **Scale Limit**: Maximum rows where precision AND recall = 1.00 across 3 runs

### Replication

```bash
# Setup
cd 01_CSVScaleLimits/_Scripts
pip install openai anthropic

# Create .env with API keys
echo "OPENAI_API_KEY=sk-..." > ../.env
echo "ANTHROPIC_API_KEY=sk-ant-..." >> ../.env

# Verify setup
python test_llm_client.py

# Run scale limit test
python 03_find_scale_limit.py --test-path .. --model gpt-5-mini --initial-rows 100
```

## Repository Structure

```
_Sessions/_2026-03-05_TabularDataFormatsForLLMs/
├── README.md                              # This file
├── 01_CSVScaleLimits/                     # Scale limit testing
│   ├── _SPEC_CSVScaleLimits.md
│   ├── _INFO_CSVScaleLimits.md
│   └── _Scripts/
│       ├── llm_client.py                  # Unified LLM client
│       ├── 01_generate_data.py            # CSV + ground truth generator
│       ├── 02_execute_and_evaluate.py     # Parallel LLM calls + evaluation
│       └── 03_find_scale_limit.py         # Binary search orchestrator
├── _SPEC_LLM_CLIENT.md                    # LLM client specification
└── PROGRESS.md                            # Session progress tracking
```

## References

### Academic Sources
- Sclar et al. (2024). "Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design." ICLR 2024. arXiv:2310.11324
- Microsoft/MIT (2024). "Does Prompt Formatting Have Any Impact on LLM Performance?" arXiv:2411.10541
- LIFBench (2024). "Evaluating the Instruction Following Performance of LLMs in Long Context." arXiv:2411.07037
- CFPO (2025). "Beyond Prompt Content: Enhancing LLM Performance via Content-Format Integration." arXiv:2502.04295

### Internal Research
- `_INFO_LLM_MARKDOWN_PREFERENCES.md` - Comprehensive format research synthesis
- TK-001 Benchmark - 10 format variants, 15 runs each, 50-600 records
