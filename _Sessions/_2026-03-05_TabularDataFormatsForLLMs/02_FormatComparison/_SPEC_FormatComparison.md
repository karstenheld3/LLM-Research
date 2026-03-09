# SPEC: Format Comparison Test Framework

**Doc ID**: TBLF-SP02
**Feature**: format-comparison-test
**Goal**: Define test framework for comparing LLM extraction scale limits across input formats (CSV vs kv_colon)
**Timeline**: Created 2026-03-09
**Target files**: `02_FormatComparison/_Scripts/*.py`, `02_FormatComparison/test-config-template-*.json`

**Depends on:**
- `_SPEC_CSVScaleLimits.md [TBLF-SP01]` for base test framework design
- `_INFO_CSVScaleLimits.md [TBLF-IN01]` for CSV baseline scale limits

## MUST-NOT-FORGET

- Same data generation logic as Test 01 (same seed, columns, filters, adversarial chars)
- Only output format changes (CSV vs kv_colon)
- Use exact same extraction task and evaluation criteria
- Per-request costs and times (not total test costs)
- 5 models: gpt-5-mini medium, gpt-5 low, gpt-5.2 medium, claude-opus medium, claude-sonnet medium
- Compare against CSV baselines from Test 01 (do not re-run CSV tests)

## Table of Contents

1. [Scenario](#1-scenario)
2. [Domain Objects](#2-domain-objects)
3. [Functional Requirements](#3-functional-requirements)
4. [Design Decisions](#4-design-decisions)
5. [Implementation Guarantees](#5-implementation-guarantees)
6. [Key Mechanisms](#6-key-mechanisms)
7. [Format Specifications](#7-format-specifications)
8. [Pipeline Flow](#8-pipeline-flow)
9. [Implementation Verification Checklist](#9-implementation-verification-checklist)
10. [Document History](#10-document-history)

## 1. Scenario

**Problem:** Test 01 established CSV scale limits, but does input format affect scale limits? The kv_colon format uses 1.43x more tokens for same data - does this reduce scale limits proportionally, or does the structured key:value format aid comprehension?

**Solution:**
- Extend Test 01 framework with format parameter in data generation
- Generate identical data in kv_colon format
- Run scale limit finder for 5 production-recommended models
- Compare scale limits against CSV baselines from Test 01

**What we don't want:**
- Re-running CSV tests (baselines already established)
- Different data generation logic (must be identical except format)
- Different evaluation criteria (same ID matching, same filters)
- New models not in production recommendations

## 2. Domain Objects

### DataFormat

A **DataFormat** specifies the output format for generated test data.

**Supported formats:**
- `csv` - Quoted CSV (Test 01 baseline)
- `kv_colon` - Key:value pairs with record headers

**Schema (in test-config.json):**
```json
{
  "data_generation": {
    "output_format": "kv_colon"
  }
}
```

### TestConfig (Extended)

Extends Test 01 TestConfig with `output_format` field.

**Schema:**
```json
{
  "test_name": "FormatComparison_KVColon",
  "description": "Extract filtered records from kv_colon data",
  
  "data_generation": {
    "number_of_rows": 100,
    "number_of_columns": 7,
    "seed": 42,
    "include_adversarial_chars": true,
    "output_format": "kv_colon"
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
    "number_of_runs": 3,
    "number_of_workers": 3,
    "reasoning_effort": "medium",
    "max_output_tokens": 16384,
    "max_context_tokens": 128000
  }
}
```

## 3. Functional Requirements

**TBLF-FR-10: Multi-Format Data Generation**
- Support `output_format` parameter in config: `csv`, `kv_colon`
- CSV format: quoted, one record per line (existing behavior)
- kv_colon format: `### Record N` header, `Key:Value` pairs, blank line separator
- Same data generation logic (same seed produces same records)
- Output file: `data.csv` for CSV, `data.txt` for kv_colon

**TBLF-FR-11: Format-Agnostic Execution**
- Load data from `data.csv` OR `data.txt` (whichever exists)
- Prompt template uses `{data}` placeholder (not format-specific)
- Same evaluation logic (ID extraction via regex)

**TBLF-FR-12: Baseline Comparison**
- Do NOT re-run CSV tests (use Test 01 results)
- Run kv_colon tests for 5 models only
- Compare scale limits: CSV vs kv_colon for same model

**TBLF-FR-13: Test Matrix**
Models to test (from Test 01 production recommendations):
- gpt-5-mini, reasoning_effort=medium (CSV baseline: 500 rows)
- gpt-5, reasoning_effort=low (CSV baseline: 356 rows)
- gpt-5.2, reasoning_effort=medium (CSV baseline: 215 rows)
- claude-opus, thinking=medium (CSV baseline: 177 rows)
- claude-sonnet, thinking=medium (CSV baseline: 168 rows)

## 4. Design Decisions

**TBLF-DD-10:** kv_colon format only for initial comparison. Rationale: Most distinct from CSV while still human-readable. Other formats (JSON, XML, YAML) tested in future if kv_colon shows significant difference.

**TBLF-DD-11:** Same seed, columns, filters as Test 01. Rationale: Only format changes - enables direct comparison of scale limits.

**TBLF-DD-12:** Use Test 01 CSV baselines, don't re-run. Rationale: CSV tests already complete, expensive to re-run, results stable.

**TBLF-DD-13:** Column labels in kv_colon use TitleCase without underscores. Rationale: More natural key names (e.g., `Salary` not `salary`).

## 5. Implementation Guarantees

**TBLF-IG-10:** Same seed produces identical record data regardless of output format.

**TBLF-IG-11:** kv_colon format preserves all adversarial characters from data.

**TBLF-IG-12:** Evaluation uses same ID regex pattern for both formats.

**TBLF-IG-13:** Scale limit finder uses same algorithm (binary search, 3 runs per iteration).

## 6. Key Mechanisms

### Format Output Functions

```python
def format_as_csv(records: list, columns: list) -> str:
    """Format records as quoted CSV."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(records)
    return output.getvalue()

def format_as_kv_colon(records: list, columns: list) -> str:
    """Format records as key:value pairs."""
    lines = []
    for i, record in enumerate(records, 1):
        lines.append(f"### Record {i}")
        for col in columns:
            label = col.replace("_", " ").title().replace(" ", "")
            lines.append(f"{label}:{record[col]}")
        lines.append("")  # Blank line between records
    return "\n".join(lines)
```

### Format-Agnostic Data Loading

```python
def load_data(instance_path: Path) -> str:
    """Load data from CSV or TXT (kv_colon) format."""
    csv_path = instance_path / "01_InputData" / "data.csv"
    txt_path = instance_path / "01_InputData" / "data.txt"
    
    if csv_path.exists():
        return csv_path.read_text(encoding="utf-8")
    elif txt_path.exists():
        return txt_path.read_text(encoding="utf-8")
    else:
        raise FileNotFoundError("No data.csv or data.txt found")
```

## 7. Format Specifications

### CSV Format (Baseline from Test 01)

```csv
"id","name","department","salary","clearance","rating","projects"
"EMP-0001","Sarah Mitchell-Reynolds","Research & Development","$185,000","Level 4: Top Secret","Exceeds Expectations: Top 20%","Project Aurora: Lead | Nexus: Contributor"
"EMP-0002","James O'Connor","Sales: Enterprise","$165,000","Level 3: Secret","Exceptional: Top 5%","Q4 Push: Owner, Enterprise | SMB Expansion"
```

**Characteristics:**
- Header row with column names
- One record per line
- All fields quoted
- Adversarial chars preserved within quotes
- Size: ~156 KB for 300 rows

### kv_colon Format

```
### Record 1
Id:EMP-0001
Name:Sarah Mitchell-Reynolds
Department:Research & Development
Salary:$185,000
Clearance:Level 4: Top Secret
Rating:Exceeds Expectations: Top 20%
Projects:Project Aurora: Lead | Nexus: Contributor

### Record 2
Id:EMP-0002
Name:James O'Connor
Department:Sales: Enterprise
Salary:$165,000
Clearance:Level 3: Secret
Rating:Exceptional: Top 5%
Projects:Q4 Push: Owner, Enterprise | SMB Expansion
```

**Characteristics:**
- `### Record N` header per record
- `Key:Value` format (no space after colon)
- Column names as TitleCase labels
- Blank line between records
- Adversarial chars appear after first colon (delimiter ambiguity)
- Size: ~211 KB for 300 rows (1.35x CSV)

### Token Comparison (300 rows)

| Format | Size | Est. Tokens | Relative |
|--------|------|-------------|----------|
| csv | 156 KB | ~39K | 1.00x |
| kv_colon | 211 KB | ~53K | 1.35x |

## 8. Pipeline Flow

```
[01_generate_data.py] (modified)
├─> Read test-config.json
├─> Generate N records with seed (same as Test 01)
├─> Get output_format from config (default: csv)
├─> IF kv_colon: format_as_kv_colon() -> data.txt
│   ELSE: format_as_csv() -> data.csv
├─> Apply fixed filters, create ground_truth.json
└─> Calculate token count

[02_execute_and_evaluate.py] (modified)
├─> Read test-config.json
├─> Load data from data.csv OR data.txt
├─> Render prompt with {data} placeholder
├─> Execute LLM, evaluate (same as Test 01)
└─> Save results

[03_find_scale_limit.py] (unchanged)
├─> Binary search for max reliable rows
├─> Uses output_format from config
└─> Saves scale_limit_result.json
```

## 9. Implementation Verification Checklist

- [ ] `01_generate_data.py` supports `output_format` config parameter
- [ ] `01_generate_data.py` outputs `data.txt` for kv_colon format
- [ ] `format_as_kv_colon()` uses `### Record N` headers
- [ ] `format_as_kv_colon()` uses `Key:Value` format (TitleCase labels)
- [ ] `format_as_kv_colon()` preserves adversarial characters
- [ ] Same seed produces identical records for both formats
- [ ] `02_execute_and_evaluate.py` loads data.csv OR data.txt
- [ ] Prompt template uses `{data}` placeholder
- [ ] `03_find_scale_limit.py` works unchanged with kv_colon data
- [ ] Test configs exist for all 5 models
- [ ] Results comparable to Test 01 CSV baselines

## 10. Document History

**[2026-03-09 19:46]**
- Initial specification created
- Defined format comparison scope: CSV vs kv_colon
- Test matrix: 5 models from production recommendations
- Extended Test 01 framework with output_format parameter
