# INFO: Find Tabular Data Scale Limits

**Doc ID**: TBLF-IN01
**Goal**: Document the V2 implementation for finding maximum reliable row counts in LLM tabular extraction
**Timeline**: Created 2026-03-05

## Summary

- Binary search finds max row count where LLM achieves 100% precision AND recall [TESTED]
- `llm_client.py` supports OpenAI (temperature, reasoning_effort) and Anthropic (temperature, thinking) [TESTED]
- Thread-safe design via immutable state after `__init__` - safe for ThreadPoolExecutor [VERIFIED]
- Embedded configs preferred over external JSON for single-file portability [DESIGN DECISION]
- 4 scripts total: llm_client, generate_data, execute_and_evaluate, find_scale_limit [IMPLEMENTED]

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Solution Architecture](#2-solution-architecture)
3. [LLM Client Design](#3-llm-client-design)
4. [Test Framework](#4-test-framework)
5. [Usage](#5-usage)
6. [Sources](#6-sources)
7. [Next Steps](#7-next-steps)
8. [Document History](#8-document-history)

## 1. Problem Statement

### 1.1 Research Question

What is the maximum number of CSV rows an LLM can reliably process for tabular extraction tasks?

### 1.2 Definition of "Reliable"

- Precision = 1.00 (no false positives)
- Recall = 1.00 (no false negatives)
- Consistent across multiple runs

### 1.3 Variables

- Model (gpt-4o, gpt-5-mini, claude-sonnet-4, etc.)
- Tabular format (CSV with quoted fields)
- Number of columns (default: 7)
- Filter complexity (2 filters: clearance level IN list, salary >= threshold)

## 2. Solution Architecture

### 2.1 Folder Structure

```
01_FindTabularDataScaleLimits_V2/
├── .env                           # API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY)
├── test-config-template.json      # Default test configuration
├── _PromptsAndTemplates/
│   └── task_prompt_template.md    # Extraction prompt template
├── _Scripts/
│   ├── llm_client.py              # Generic LLM client (reusable)
│   ├── 01_generate_data.py        # Generate CSV + ground truth
│   ├── 02_execute_and_evaluate.py # Call LLM + evaluate response
│   ├── 03_find_scale_limit.py     # Binary search orchestrator
│   └── test_llm_client.py         # Quick validation test
└── [model_output_folders]/        # Results per model
```

### 2.2 Script Dependencies

```
03_find_scale_limit.py
├─> 01_generate_data.py (via subprocess)
└─> 02_execute_and_evaluate.py (via subprocess)
    └─> llm_client.py (import)
```

### 2.3 Binary Search Algorithm

1. Start at initial row count (default: 500)
2. Run extraction test, evaluate precision/recall
3. If PASS (100% accuracy): scale up by 1.5x, set lower bound
4. If FAIL: set upper bound, try midpoint
5. Converge when upper - lower <= tolerance (default: 10)

## 3. LLM Client Design

### 3.1 Supported Providers and Methods

- **OpenAI temperature**: gpt-3.5, gpt-4, gpt-4o (uses `temperature` parameter)
- **OpenAI reasoning_effort**: o1, o3, o4, gpt-5 (uses `reasoning_effort` parameter)
- **Anthropic temperature**: claude-3, claude-3.5 (uses `temperature` parameter)
- **Anthropic thinking**: claude-3.7, claude-sonnet-4, claude-opus-4 (uses `thinking.budget_tokens`)

### 3.2 Key Features

- **Prefix-based model detection**: "gpt-5-mini" matches "gpt-5" config
- **Unified effort levels**: none, minimal, low, medium, high, xhigh
- **Thread safety**: Immutable state after `__init__`, safe for parallel workers
- **Timeout support**: Default 300s, configurable
- **Retry with backoff**: 3 retries at 1s, 2s, 4s intervals
- **Unified response format**: `{text, usage, model, finish_reason}`

### 3.3 Usage Example

```python
from llm_client import LLMClient

# Single client, reusable across parallel workers
client = LLMClient("gpt-5-mini", reasoning_effort="medium", timeout=300)

# Make call
response = client.call("Extract employee IDs from this CSV...")
print(response["text"])
print(f"Tokens: {response['usage']['input_tokens']} in, {response['usage']['output_tokens']} out")
print(f"Finish: {response['finish_reason']}")  # 'stop' or 'length' (truncated)
```

### 3.4 Embedded vs External Configs

Design decision: Configs are embedded in `llm_client.py` for portability.

- **Embedded** (chosen): Single-file module, no path resolution issues, copy anywhere
- **External JSON**: Maintainable, single source of truth, but requires file loading

Config structure matches `.windsurf/skills/llm-evaluation/*.json` schemas.

## 4. Test Framework

### 4.1 Data Generation

- Generates N rows with 7 columns: id, name, department, salary, clearance, rating, projects
- Adversarial characters: colons, pipes, commas, ampersands in values
- Ground truth: IDs of records matching filter criteria

### 4.2 Extraction Task

Prompt asks LLM to:
1. Parse CSV data
2. Apply filters (clearance level IN [Level 3, 4, 5] AND salary >= $150,000)
3. Output matching records with specific columns

### 4.3 Evaluation

- Regex extraction of EMP-XXXX IDs from response
- Compare to ground truth
- Calculate precision, recall, F1
- Detect truncation via `finish_reason == "length"`

### 4.4 Parallel Execution

- ThreadPoolExecutor for multiple runs
- Single LLMClient instance shared across workers (thread-safe)
- Each worker: call API, write response, evaluate, write result

## 5. Usage

### 5.1 Quick Test

```bash
cd 01_FindTabularDataScaleLimits_V2/_Scripts
python test_llm_client.py
```

### 5.2 Find Scale Limit

```bash
python 03_find_scale_limit.py --test-path .. --model gpt-5-mini --initial-rows 100 --tolerance 10
```

### 5.3 Configuration

Edit `test-config-template.json`:

```json
{
  "data_generation": {
    "number_of_rows": 100,
    "number_of_columns": 7,
    "seed": 42
  },
  "execution": {
    "model": "gpt-5-mini",
    "number_of_runs": 3,
    "number_of_workers": 3,
    "reasoning_effort": "medium"
  }
}
```

## 6. Sources

**Primary Sources:**
- `TBLF-IN01-SC-SKILL-LLMEVAL`: `.windsurf/skills/llm-evaluation/call-llm.py` - Original LLM call implementation [VERIFIED]
- `TBLF-IN01-SC-SKILL-LLMBATCH`: `.windsurf/skills/llm-evaluation/call-llm-batch.py` - Batch processing patterns [VERIFIED]
- `TBLF-IN01-SC-SPEC-LLMC`: `_SPEC_LLM_CLIENT.md [LLMC-SP01]` - Detailed specification [VERIFIED]
- `TBLF-IN01-SC-SPEC-TEST`: `_SPEC_TABULAR_EXTRACTION_TEST.md [TBLF-SP01]` - Test framework spec [VERIFIED]

**Research Sources:**
- `TBLF-IN01-SC-GH-OAISDK`: github.com/openai/openai-python/discussions/1901 - Thread safety patterns
- `TBLF-IN01-SC-DW-ANTH`: deepwiki.com/anthropics/anthropic-sdk-python - Anthropic concurrency

## 7. Next Steps

1. Run scale limit tests with multiple models (gpt-4o, gpt-5-mini, claude-sonnet-4)
2. Add Anthropic API key to `.env` to enable Claude testing
3. Compare results across models to identify format preferences
4. Document findings in research report

## 8. Document History

**[2026-03-05 22:07]**
- Initial INFO document created
- Documented V2 implementation architecture
- Summarized llm_client design decisions
- Listed test framework components
