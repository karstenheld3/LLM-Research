<DevSystem MarkdownTablesAllowed=true />

# INFO: Format Comparison (CSV vs kv_colon)

**Doc ID**: TBLF-IN02
**Goal**: Compare scale limits between CSV and kv_colon formats for LLM tabular extraction
**Timeline**: Created 2026-03-09

## Summary

**Research Question:** Does input format (CSV vs kv_colon) affect LLM extraction scale limits?

**Hypothesis:** CSV format may enable higher scale limits due to:
- Smaller token footprint (1.43x more compact than kv_colon)
- Familiar training data distribution
- Single-line record structure aids attention

**Test Design:**
- Same extraction task as Test 01 (CSVScaleLimits)
- Same data generation (7 columns, adversarial chars, compound filter)
- Two formats: CSV (baseline) vs kv_colon
- 5 models from Test 01 production recommendations

### Format Size Comparison (300 rows)

| Format     | Size (bytes) | Relative | Token Estimate |
|------------|-------------|----------|----------------|
| csv_quoted | 156,113     | 1.00x    | ~39K           |
| kv_colon   | 211,274     | 1.35x    | ~53K           |

### Test Matrix

| Model         | Effort | CSV Scale Limit (T01) | kv_colon Scale Limit |
|---------------|--------|----------------------|---------------------|
| gpt-5-mini    | medium | 500                  | TBD                 |
| gpt-5         | low    | 356                  | TBD                 |
| gpt-5.2       | medium | 215                  | TBD                 |
| claude-opus   | medium | 177                  | TBD                 |
| claude-sonnet | medium | 168                  | TBD                 |

**Total tests:** 5 models × 1 format (kv_colon) = 5 new tests
(CSV baselines already established in Test 01)

## Format Examples

### CSV (quoted)
```
"id","name","department","salary","clearance","rating","projects"
"EMP-0001","Sarah Mitchell-Reynolds","Research & Development","$185,000","Level 4: Top Secret","Exceeds Expectations: Top 20%","Project Aurora: Lead | Nexus: Contributor"
```

### kv_colon
```
### Record 1
Id:EMP-0001
Name:Sarah Mitchell-Reynolds
Department:Research & Development
Salary:$185,000
Clearance:Level 4: Top Secret
Rating:Exceeds Expectations: Top 20%
Projects:Project Aurora: Lead | Nexus: Contributor
```

## Methodology

1. Use same binary search algorithm as Test 01
2. Same success criteria: Precision=1.00 AND Recall=1.00 across 3 runs
3. Same filter conditions and column selection
4. Compare scale limits between formats for each model

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

**[2026-03-09 19:42]**
- Initial document created
- Test matrix defined: 5 models × kv_colon format
