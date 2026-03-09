<DevSystem MarkdownTablesAllowed=true />

# INFO: Format Comparison (8 Formats)

**Doc ID**: TBLF-IN02
**Goal**: Compare scale limits across 8 input formats for LLM tabular extraction
**Timeline**: Created 2026-03-09

## Summary

**Research Question:** Does input format affect LLM extraction scale limits?

**Hypothesis:** Token-efficient formats may enable higher scale limits, but structured formats may aid comprehension:
- csv_raw is most compact (1.00x baseline)
- xml is most verbose (2.12x baseline)
- Structured formats (json, yaml) may aid parsing despite larger size

**Test Design:**
- Same extraction task as Test 01 (CSVScaleLimits)
- Same data generation (7 columns, adversarial chars, compound filter)
- 8 formats: csv_quoted, csv_raw, kv_colon_space, markdown_table, json, xml, yaml, toml
- Excluded: kv_colon, kv_double_colon
- 5 models from Test 01 production recommendations

### Format Size Comparison (300 rows)

| Format         | Size (KB) | Relative |
|----------------|-----------|----------|
| csv_raw        | 148       | 1.00x    |
| csv_quoted     | 156       | 1.06x    |
| markdown_table | 197       | 1.33x    |
| kv_colon_space | 217       | 1.47x    |
| toml           | 235       | 1.59x    |
| yaml           | 249       | 1.68x    |
| json           | 269       | 1.82x    |
| xml            | 314       | 2.12x    |

### Test Matrix

**Models (5):** gpt-5-mini medium, gpt-5 low, gpt-5.2 medium, claude-opus medium, claude-sonnet medium

**Formats (7 new):** csv_raw, kv_colon_space, markdown_table, json, xml, yaml, toml
(csv_quoted baseline from Test 01)

**Total tests:** 5 models × 7 formats = 35 new tests

## Format Examples

### CSV (quoted)
```
"id","name","department","salary","clearance","rating","projects"
"EMP-0001","Sarah Mitchell-Reynolds","Research & Development","$185,000","Level 4: Top Secret","Exceeds Expectations: Top 20%","Project Aurora: Lead | Nexus: Contributor"
```

### kv_colon_space
```
### Record 1
Id: EMP-0001
Name: Sarah Mitchell-Reynolds
Department: Research & Development
Salary: $185,000
Clearance: Level 4: Top Secret
```

## Methodology

1. Use same binary search algorithm as Test 01
2. **Start at CSV baseline** (faster convergence):
   - gpt-5-mini medium: start at 500 rows
   - gpt-5 low: start at 356 rows
   - gpt-5.2 medium: start at 215 rows
   - claude-opus medium: start at 177 rows
   - claude-sonnet medium: start at 168 rows
3. Same success criteria: Precision=1.00 AND Recall=1.00 across 3 runs
4. Same filter conditions and column selection
5. Compare scale limits between formats for each model

## Expected Outcomes

**If CSV outperforms kv_colon:**
- Confirms token efficiency matters for scale
- Supports CSV as optimal production format

**If kv_colon matches or exceeds CSV:**
- Suggests format structure (key:value) aids comprehension
- Opens consideration for alternative formats

## Source Documents

- Test 01: `_INFO_CSVScaleLimits.md [TBLF-IN01]` - CSV baseline results
- POC: `IPPS/_PrivateSessions/_2026-03-04_LLMMarkdownOptimization/poc` - Format samples

## Document History

**[2026-03-09 19:48]**
- Changed: Scope expanded from kv_colon only to 8 formats
- Added: csv_raw, kv_colon_space, markdown_table, json, xml, yaml, toml
- Removed: kv_colon, kv_double_colon (per user request)
- Updated: Test matrix 7 formats x 5 models = 35 new tests

**[2026-03-09 19:42]**
- Initial document created
- Test matrix defined: 5 models x kv_colon format
