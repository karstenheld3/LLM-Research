# SPEC: Format Comparison Test Framework

**Doc ID**: TBLF-SP02
**Feature**: format-comparison-test
**Goal**: Define test framework for comparing LLM extraction scale limits across 8 input formats
**Timeline**: Created 2026-03-09
**Target files**: `02_FormatComparison/_Scripts/*.py`, `02_FormatComparison/test-config-template-*.json`

**Depends on:**
- `_SPEC_CSVScaleLimits.md [TBLF-SP01]` for base test framework design
- `_INFO_CSVScaleLimits.md [TBLF-IN01]` for CSV baseline scale limits

## MUST-NOT-FORGET

- Same data generation logic as Test 01 (same seed, columns, filters, adversarial chars)
- 8 formats: kv_colon_space, markdown_table, csv_quoted, csv_raw, json, xml, yaml, toml
- Excluded: kv_colon, kv_double_colon (per user request)
- Use exact same extraction task and evaluation criteria
- Per-request costs and times (not total test costs)
- 5 models: gpt-5-mini medium, gpt-5 low, gpt-5.2 medium, claude-opus medium, claude-sonnet medium
- Compare against CSV baselines from Test 01 (do not re-run CSV tests)
- Start binary search at CSV baseline scale limit (faster convergence)

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

**Problem:** Test 01 established CSV scale limits, but does input format affect scale limits? Different formats use varying token counts (1.0x to 2.1x of CSV baseline) - does token efficiency correlate with scale limits, or do structured formats aid comprehension?

**Solution:**
- Extend Test 01 framework with format parameter in data generation
- Generate identical data in 8 formats (excluding kv_colon, kv_double_colon)
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
- `csv_quoted` - Quoted CSV (Test 01 baseline)
- `csv_raw` - Unquoted CSV
- `kv_colon_space` - Key: value pairs with space after colon
- `markdown_table` - Markdown table format
- `json` - JSON array of objects
- `xml` - XML with record elements
- `yaml` - YAML list of records
- `toml` - TOML array of tables

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
- Run format tests for 5 models, 7 new formats
- Compare scale limits against CSV baseline for same model

**TBLF-FR-14: Baseline-Start Optimization**
- Start binary search at known CSV baseline scale limit (not default 300)
- CSV baselines: gpt-5-mini=500, gpt-5=356, gpt-5.2=215, claude-opus=177, claude-sonnet=168
- Use `--initial-rows` parameter with baseline value
- Faster convergence: skip iterations below known working scale

**TBLF-FR-13: Test Matrix**
Models to test (from Test 01 production recommendations):
- gpt-5-mini, reasoning_effort=medium (CSV baseline: 500 rows)
- gpt-5, reasoning_effort=low (CSV baseline: 356 rows)
- gpt-5.2, reasoning_effort=medium (CSV baseline: 215 rows)
- claude-opus, thinking=medium (CSV baseline: 177 rows)
- claude-sonnet, thinking=medium (CSV baseline: 168 rows)

## 4. Design Decisions

**TBLF-DD-10:** 8 formats tested (excluding kv_colon, kv_double_colon). Rationale: Cover range from compact (csv_raw) to verbose (xml) to test token efficiency vs comprehension hypothesis.

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

### Token/Size Comparison (300 rows, from POC analysis)

- **csv_raw** - 148 KB - 1.00x (baseline)
- **csv_quoted** - 156 KB - 1.06x
- **markdown_table** - 197 KB - 1.33x
- **kv_colon_space** - 217 KB - 1.47x
- **toml** - 235 KB - 1.59x
- **yaml** - 249 KB - 1.68x
- **json** - 269 KB - 1.82x
- **xml** - 314 KB - 2.12x

### Format Examples

**csv_quoted (Test 01 baseline):**
```
"id","name","department","salary",...
"EMP-0001","Sarah Mitchell-Reynolds","Research & Development","$185,000",...
```

**csv_raw:**
```
id,name,department,salary,...
EMP-0001,Sarah Mitchell-Reynolds,Research & Development,$185,000,...
```

**kv_colon_space:**
```
### Record 1
Id: EMP-0001
Name: Sarah Mitchell-Reynolds
Department: Research & Development
Salary: $185,000
```

**markdown_table:**
```
| id | name | department | salary |
|----|------|------------|--------|
| EMP-0001 | Sarah Mitchell-Reynolds | Research & Development | $185,000 |
```

**json:**
```json
[{"id": "EMP-0001", "name": "Sarah Mitchell-Reynolds", "department": "Research & Development", "salary": "$185,000"}]
```

**xml:**
```xml
<records>
  <record>
    <id>EMP-0001</id>
    <name>Sarah Mitchell-Reynolds</name>
  </record>
</records>
```

**yaml:**
```yaml
- id: EMP-0001
  name: Sarah Mitchell-Reynolds
  department: Research & Development
```

**toml:**
```toml
[[records]]
id = "EMP-0001"
name = "Sarah Mitchell-Reynolds"
```

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
- [ ] `01_generate_data.py` implements all 8 format functions
- [ ] Format functions: csv_quoted, csv_raw, kv_colon_space, markdown_table, json, xml, yaml, toml
- [ ] All format functions preserve adversarial characters
- [ ] Same seed produces identical records for all formats
- [ ] `02_execute_and_evaluate.py` loads data.csv, data.txt, data.json, data.xml, data.yaml, data.toml, data.md
- [ ] Prompt template uses `{data}` placeholder
- [ ] `03_find_scale_limit.py` works unchanged with all formats
- [ ] Test configs exist for all 8 formats x 5 models = 40 tests (minus csv_quoted baseline = 35 new tests)
- [ ] Results comparable to Test 01 CSV baselines

## 10. Document History

**[2026-03-09 19:48]**
- Changed: Scope expanded from kv_colon only to 8 formats
- Added: csv_raw, kv_colon_space, markdown_table, json, xml, yaml, toml
- Removed: kv_colon, kv_double_colon (per user request)
- Updated: Test matrix 8 formats x 5 models = 35 new tests

**[2026-03-09 19:46]**
- Initial specification created
- Defined format comparison scope: CSV vs kv_colon
- Test matrix: 5 models from production recommendations
- Extended Test 01 framework with output_format parameter
