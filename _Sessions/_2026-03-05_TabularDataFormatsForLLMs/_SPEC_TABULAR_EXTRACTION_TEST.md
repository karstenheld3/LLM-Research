# SPEC: Tabular Data Extraction Test Framework

**Doc ID (TDID)**: TBLF-SP01
**Feature**: tabular-extraction-test
**Goal**: Define end-to-end test framework for measuring LLM tabular data extraction limits
**Timeline**: Created 2026-03-05
**Target files**: `01_FindTabularDataScaleLimits_V1/_Scripts/*.py`, `01_FindTabularDataScaleLimits_V1/test-config-template.json`

**Depends on:**
- `PROBLEMS.md [TBLF-PR-001]` for scale limits research goal

## MUST-NOT-FORGET

- Quoted CSV format only (per user requirement)
- Pipeline must be fully configurable via JSON
- Each phase produces artifacts for next phase
- Evaluation uses deterministic ID matching (not LLM judge)
- Support parallel execution with configurable workers
- Include adversarial data patterns (colons, pipes, commas in values)
- Track token counts to detect context window limits

## Table of Contents

1. [Scenario](#1-scenario)
2. [Domain Objects](#2-domain-objects)
3. [Functional Requirements](#3-functional-requirements)
4. [Design Decisions](#4-design-decisions)
5. [Implementation Guarantees](#5-implementation-guarantees)
6. [Key Mechanisms](#6-key-mechanisms)
7. [Pipeline Flow](#7-pipeline-flow)
8. [Data Structures](#8-data-structures)
9. [Implementation Verification Checklist](#9-implementation-verification-checklist)
10. [Document History](#10-document-history)

## 1. Scenario

**Problem:** Need to determine scale limits (rows x columns) at which LLM tabular data extraction becomes unreliable. Prior research (LLMO-TK-001) showed reliability drops at 600 records, but this was format-dependent and used hardcoded evaluation.

**Solution:**
- Modular 4-phase pipeline: Generate → Execute → Evaluate → Summarize
- Configurable test instances with varying row/column counts
- Deterministic evaluation using ID matching (faster, cheaper, more reliable than LLM judge)
- Parallel execution with worker pool
- Confusion matrix metrics: True Positives (TP), False Positives (FP), False Negatives (FN), precision, recall, F1
- Token counting to detect context window limits

**What we don't want:**
- Monolithic scripts with hardcoded logic
- Manual expected-output files that must be maintained
- Tightly coupled phases that cannot run independently
- Format-specific evaluation logic

## 2. Domain Objects

### Test

A **Test** is a reusable test definition with shared scripts and configuration template.

**Storage:** `[REPO]/NN_[TestName]/`
**Definition:** `test-config-template.json`

**Key properties:**
- `test_name` - Human-readable test name
- `description` - What this test measures
- `default_config` - Default values for all configurable parameters

**Folder structure:**
```
01_FindTabularDataScaleLimits_V1/
├── _Scripts/
│   ├── 01_generate_data.py
│   ├── 02_execute_llm.py
│   ├── 03_evaluate_responses.py
│   └── 04_summarize_results.py
├── _PromptsAndTemplates/
│   └── task_prompt_template.md
└── test-config-template.json
```

### TestInstance

A **TestInstance** is a concrete test run with specific configuration overrides.

**Storage:** `[Test]/NNN_[model]_[configName]/`
**Definition:** `test-config.json`

**Key properties:**
- Inherits from parent test-config-template.json
- Overrides specific parameters for this instance
- Contains all phase output folders

**Folder structure:**
```
001_gpt-5-mini_100rows/
├── test-config.json
├── 01_InputData/
│   ├── data.csv
│   └── ground_truth.json
├── 02_Responses/
│   ├── run_01.md
│   ├── run_02.md
│   └── ...
├── 03_Evaluations/
│   ├── eval_01.json
│   ├── eval_02.json
│   └── ...
└── 04_Summaries/
    └── summary.json
```

### TestConfig

A **TestConfig** defines all parameters for a test instance.

**Schema:**
```json
{
  "test_name": "TabularExtraction_100rows_20cols",
  "description": "Extract filtered records from 100-row CSV",
  
  "data_generation": {
    "number_of_rows": 100,
    "number_of_columns": 20,
    "seed": 42,
    "include_adversarial_chars": true
  },
  
  "extraction_task": {
    "task_prompt": "task_prompt_template.md",
    "columns_to_extract": ["id", "name", "department", "salary", "clearance", "rating", "projects"],
    "filters": [
      {"column": "clearance", "operator": "in", "value": ["Level 3", "Level 4", "Level 5"]},
      {"column": "salary", "operator": "gte", "value": 150000}
    ]
  },
  
  "execution": {
    "model": "gpt-5-mini",
    "number_of_runs": 10,
    "number_of_workers": 5,
    "temperature": null,
    "reasoning_effort": null,
    "max_output_tokens": null,
    "max_context_tokens": 128000
  }
}
```

### GroundTruth

A **GroundTruth** is the expected extraction result, generated deterministically from fixed filters.

**Storage:** `[TestInstance]/01_InputData/ground_truth.json`

**Schema:**
```json
{
  "filters_applied": [
    {"column": "clearance", "operator": "in", "value": ["Level 3", "Level 4", "Level 5"]},
    {"column": "salary", "operator": "gte", "value": 150000}
  ],
  "columns_requested": ["id", "name", "department", "salary", "clearance", "rating", "projects"],
  "expected_records": [
    {"id": "EMP-0012", "name": "Alice Smith", ...},
    {"id": "EMP-0027", "name": "Bob Jones", ...}
  ],
  "expected_count": 12,
  "expected_ids": ["EMP-0012", "EMP-0027", ...]
}
```

### EvaluationResult

An **EvaluationResult** is the deterministic comparison of a response against ground truth.

**Storage:** `[TestInstance]/03_Evaluations/eval_NN.json`

**Schema:**
```json
{
  "run_id": 1,
  "response_file": "run_01.md",
  "extracted_ids": ["EMP-0012", "EMP-0027", ...],
  "metrics": {
    "true_positives": 10,
    "false_positives": 2,
    "false_negatives": 2,
    "precision": 0.833,
    "recall": 0.833,
    "f1": 0.833
  },
  "errors": [],
  "token_count": 4523
}
```

### Summary

A **Summary** aggregates all evaluation results for a test instance.

**Storage:** `[TestInstance]/04_Summaries/summary.json`

**Schema:**
```json
{
  "test_instance": "001_gpt-5-mini_100rows",
  "config": {...},
  "aggregate_metrics": {
    "runs_total": 10,
    "runs_passed": 8,
    "runs_failed": 2,
    "precision_mean": 0.92,
    "precision_std": 0.05,
    "precision_min": 0.80,
    "precision_max": 1.00,
    "recall_mean": 0.95,
    "f1_mean": 0.93,
    "perfect_extraction_rate": 0.60
  },
  "confusion_matrix_totals": {
    "true_positives": 95,
    "false_positives": 8,
    "false_negatives": 5
  },
  "run_results": [...]
}
```

## 3. Functional Requirements

**TBLF-FR-01: Data Generation**
- Generate CSV with configurable `number_of_rows` and `number_of_columns`
- Use quoted CSV format (all fields quoted)
- Generate realistic employee-style data (IDs, names, departments, salaries, dates)
- Include adversarial characters in data values (colons, pipes, commas, ampersands)
- Deterministic output via `seed` parameter
- Generate ground_truth.json using fixed filter criteria from config
- Calculate and store token count for generated prompt

**TBLF-FR-02: LLM Execution**
- Load task_prompt_template.md and render with CSV data, filters, columns
- Execute rendered prompt against configured model
- Run `number_of_runs` times
- Parallel execution with `number_of_workers` concurrent calls
- Support model-specific parameters: `temperature`, `reasoning_effort`, `max_output_tokens`
- Warn if prompt token count exceeds `max_context_tokens`
- Save each response to 02_Responses/run_NN.md
- Skip existing run files (resume support)

**TBLF-FR-03: Response Evaluation**
- For each response, parse output to extract employee IDs (regex: `EMP-\d{4}`)
- Compare extracted IDs against ground_truth.expected_ids
- Calculate per-run metrics: TP, FP, FN, precision, recall, F1 (acronyms defined in Section 1)
- Save evaluation to 03_Evaluations/eval_NN.json

**TBLF-FR-04: Result Summarization**
- Aggregate all evaluation results
- Calculate: mean/std/min/max for precision, recall, F1
- Calculate: perfect_extraction_rate (runs with 100% precision AND recall)
- Calculate: confusion matrix totals
- Output summary.json to 04_Summaries/

**TBLF-FR-05: Configuration Inheritance**
- TestInstance config inherits from Test template
- Instance config overrides template values
- Support partial override (only specify changed values)

**TBLF-FR-06: CLI Interface**
- Each script accepts: `--instance-path <path>` to locate test instance
- Scripts read test-config.json from instance path
- Scripts are idempotent (skip already-completed work)

## 4. Design Decisions

**TBLF-DD-01:** Quoted CSV format only. Rationale: Reduces variable count for initial scale testing. Other formats tested in separate test definitions.

**TBLF-DD-02:** Deterministic evaluation via regex ID matching. Rationale: Faster, cheaper, more reliable than LLM judge. Correct answers are enumerable (employee IDs), making deterministic comparison superior.

**TBLF-DD-03:** Ground truth generated with fixed filters from config. Rationale: Ensures reproducibility across runs, enables meaningful comparison of results.

**TBLF-DD-04:** Four separate scripts, one per phase. Rationale: Each phase can run independently, supports incremental execution, easier debugging and testing.

**TBLF-DD-05:** JSON configuration over CLI flags. Rationale: Reproducible test instances, self-documenting, version controllable.

**TBLF-DD-06:** Employee data domain with adversarial characters. Rationale: Familiar structure, natural filter criteria, and realistic parsing challenges (colons, pipes, commas in field values).

## 5. Implementation Guarantees

**TBLF-IG-01:** Data generation is deterministic given same seed value.

**TBLF-IG-02:** All scripts are idempotent - re-running skips completed work.

**TBLF-IG-03:** Pipeline phases can run independently if prior phase outputs exist.

**TBLF-IG-04:** Evaluation metrics use standard definitions: precision = TP/(TP+FP), recall = TP/(TP+FN).

**TBLF-IG-05:** Summary aggregation handles partial runs (some evaluations missing).

## 6. Key Mechanisms

### Configuration Inheritance

```python
def load_config(instance_path):
    template_path = instance_path.parent / "test-config-template.json"
    instance_config_path = instance_path / "test-config.json"
    
    template = json.load(template_path)
    instance = json.load(instance_config_path)
    
    return deep_merge(template, instance)  # instance overrides template
```

### Parallel Execution Pattern

```python
async def execute_runs(config, instance_path):
    semaphore = asyncio.Semaphore(config["execution"]["number_of_workers"])
    tasks = []
    
    for run_id in range(1, config["execution"]["number_of_runs"] + 1):
        output_file = instance_path / f"02_Responses/run_{run_id:02d}.md"
        if output_file.exists():
            continue  # Skip existing
        tasks.append(execute_single_run(semaphore, config, run_id, output_file))
    
    await asyncio.gather(*tasks)
```

### Deterministic Evaluation Pattern

```python
def evaluate_response(response_text, ground_truth):
    # Extract employee IDs from response using regex
    extracted_ids = set(re.findall(r'EMP-\d{4}', response_text))
    expected_ids = set(ground_truth["expected_ids"])
    
    tp = len(extracted_ids & expected_ids)
    fp = len(extracted_ids - expected_ids)
    fn = len(expected_ids - extracted_ids)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    return {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1}
```

## 7. Pipeline Flow

```
[01_generate_data.py]
├─> Read test-config.json
├─> Generate CSV with N rows x M columns (with adversarial chars)
├─> Apply fixed filters from config, identify matching records
├─> Calculate token count for full prompt
├─> Write 01_InputData/data.csv
└─> Write 01_InputData/ground_truth.json (includes expected_ids)

[02_execute_llm.py]
├─> Read test-config.json
├─> Load task_prompt_template.md, render with CSV + filters + columns
├─> Warn if token count exceeds max_context_tokens
├─> For each run (parallel with worker limit):
│   ├─> Call LLM API
│   └─> Write 02_Responses/run_NN.md
└─> Report: completed N of M runs

[03_evaluate_responses.py]
├─> Read test-config.json
├─> Load ground_truth.json
├─> For each response in 02_Responses/:
│   ├─> Extract employee IDs via regex
│   ├─> Compare against expected_ids
│   ├─> Calculate TP, FP, FN, precision, recall, F1
│   └─> Write 03_Evaluations/eval_NN.json
└─> Report: evaluated N responses

[04_summarize_results.py]
├─> Read test-config.json
├─> Load all 03_Evaluations/*.json
├─> Calculate aggregate metrics
├─> Write 04_Summaries/summary.json
└─> Print summary report to console
```

## 8. Data Structures

### Task Prompt Template

```markdown
# MANDATORY DATA EXTRACTION TASK

You MUST extract ALL matching employees. Do NOT truncate, summarize, or stop early.

## CRITICAL REQUIREMENTS

1. Output EVERY matching record - there may be 100+ matches
2. Do NOT stop until ALL matches are listed
3. Do NOT add any text before or after the numbered list
4. Do NOT use Python, code blocks, or scripts - output the list directly
5. If output is too long, continue anyway - completeness is mandatory

## Employee Database

{csv_data}

## Extraction Criteria (ALL must be true)

{filters}

## Output Format (MANDATORY)

{output_format}

## FINAL INSTRUCTION

Start outputting the numbered list NOW. Include ALL matching employees. Do NOT truncate.
```

### Sample Generated CSV (with adversarial characters)

```csv
"id","name","department","title","salary","clearance","rating","projects"
"EMP-0001","Alice O'Connor-Smith","Research & Development","Principal Scientist: AI","$185,000.00/year","Level 4: Top Secret","Exceeds Expectations: Top 20%","Project Aurora: Lead | Nexus: Contributor"
"EMP-0002","Bob Wei-Lin Jr.","Sales: Enterprise","Senior Account Exec, West","$165,000.00/year","Level 3: Secret","Exceptional: Top 5%","Q4 Push: Owner, Enterprise | SMB Expansion"
...
```

**Note:** Data includes colons (`:`), pipes (`|`), commas (`,`), and ampersands (`&`) within quoted field values to test LLM parsing robustness.

## 9. Scale Limit Finder

**TBLF-FR-06: Binary Search for Maximum Reliable Scale**

Automated tool to find the maximum number of rows where a model achieves 100% accuracy (Precision=1.00 AND Recall=1.00).

### Algorithm

```
1. Start with initial_rows (default: 500)
2. Run test at current row count
3. IF Precision=1.00 AND Recall=1.00:
   - Record as last_working_lower_bound
   - Multiply rows by 1.5 (go higher)
4. ELSE:
   - Record as last_failed_upper_bound
   - Halve rows (go lower)
5. Once both bounds established, use binary search:
   - new_test_rows = last_working_lower_bound + (last_failed_upper_bound - last_working_lower_bound) / 2
6. STOP when: last_failed_upper_bound - last_working_lower_bound <= 10
7. Report: Maximum reliable scale = last_working_lower_bound
```

### CLI Interface

```bash
python 05_find_scale_limit.py --test-path 01_FindTabularDataScaleLimits_V1 --initial-rows 500 --tolerance 10
```

**Arguments:**
- `--test-path` - Path to test folder containing `_Scripts/` and `test-config-template.json`
- `--initial-rows` - Starting row count (default: 500)
- `--tolerance` - Stop when bounds are within this many rows (default: 10)
- `--model` - Model to test (default: from template config)

### Output

Creates `scale_limit_result.json` in test folder:

```json
{
  "model": "gpt-5-mini",
  "max_reliable_rows": 340,
  "last_working_lower_bound": 340,
  "last_failed_upper_bound": 350,
  "search_history": [
    {"rows": 500, "precision": 0.85, "recall": 0.90, "passed": false},
    {"rows": 250, "precision": 1.00, "recall": 1.00, "passed": true},
    {"rows": 375, "precision": 0.95, "recall": 0.98, "passed": false},
    {"rows": 312, "precision": 1.00, "recall": 1.00, "passed": true},
    {"rows": 343, "precision": 1.00, "recall": 1.00, "passed": true},
    {"rows": 350, "precision": 0.98, "recall": 1.00, "passed": false}
  ],
  "total_api_calls": 12,
  "elapsed_time_seconds": 245.3
}
```

### Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    05_find_scale_limit.py                       │
├─────────────────────────────────────────────────────────────────┤
│ For each iteration:                                             │
│  1. Create temp instance folder: _temp_scale_test_NNNrows/      │
│  2. Update test-config.json with current row count              │
│  3. Run 01_generate_data.py                                     │
│  4. Run 02_execute_and_evaluate.py (single run sufficient)      │
│  5. Check if Precision=1.00 AND Recall=1.00                     │
│  6. Update bounds and calculate next row count                  │
│  7. Delete temp folder (keep only final result)                 │
└─────────────────────────────────────────────────────────────────┘
```

## 10. Implementation Verification Checklist

- [ ] `01_generate_data.py` generates valid quoted CSV with adversarial characters
- [ ] `01_generate_data.py` produces deterministic output with same seed
- [ ] `01_generate_data.py` applies fixed filters from config, creates ground_truth.json with expected_ids
- [ ] `01_generate_data.py` calculates and stores token count
- [ ] `02_execute_llm.py` renders prompt template with CSV, filters, columns
- [ ] `02_execute_llm.py` warns if token count exceeds max_context_tokens
- [ ] `02_execute_llm.py` runs parallel with worker limit
- [ ] `02_execute_llm.py` skips existing run files (idempotent)
- [ ] `02_execute_llm.py` supports temperature, reasoning_effort, max_output_tokens
- [ ] `03_evaluate_responses.py` extracts IDs via regex (deterministic, no LLM judge)
- [ ] `03_evaluate_responses.py` calculates TP, FP, FN, precision, recall, F1
- [ ] `04_summarize_results.py` aggregates all evaluations
- [ ] `04_summarize_results.py` calculates mean/std/min/max metrics
- [ ] `04_summarize_results.py` handles partial runs gracefully
- [ ] Configuration inheritance works (template + instance override)
- [ ] All scripts accept `--instance-path` CLI argument

## 11. Document History

**[2026-03-05 19:35]**
- Added: Scale Limit Finder (TBLF-FR-06) - binary search for max reliable rows

**[2026-03-05 18:00]**
- Changed: LLM judge replaced with deterministic ID matching (TBLF-RV-001)
- Changed: Random filters replaced with fixed filters in config (TBLF-RV-002)
- Added: Adversarial data patterns requirement (TBLF-RV-003)
- Changed: Token counting and context window tracking (TBLF-RV-004)
- Changed: 5 scripts reduced to 4, removed 02_render_prompts.py (TBLF-RV-006)
- Changed: Task prompt strengthened with MANDATORY language (TBLF-RV-007)
- Changed: Explicit column list instead of count (TBLF-RV-008)

**[2026-03-05 17:50]**
- Added: Implementation Verification Checklist (Section 9)
- Fixed: Expanded TP/FP/FN acronyms on first use

**[2026-03-05 17:45]**
- Initial specification created
