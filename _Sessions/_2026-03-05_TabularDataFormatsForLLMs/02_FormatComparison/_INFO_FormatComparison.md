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

**Prior Research Findings** (from TK-001 benchmark at 300 records, gpt-5-mini):
- Key-value formats outperform structured formats (XML, markdown tables have highest variance)
- Separator style (`:` vs `: ` vs `::`) shows no measurable difference on modern models
- CSV (quoted and raw) achieves near-perfect precision (99.9-100%)
- XML has highest variance (Std 0.161) and 1/15 failure rate
- Scale threshold: model reliable at 300 records, unreliable at 600+

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

## Prior Research: TK-001 Format Ranking (300 records, n=15)

**Source:** `IPPS/_PrivateSessions/_2026-03-04_LLMMarkdownOptimization/_INFO_LLM_MARKDOWN_PREFERENCES.md [LLMO-IN01]`

| Rank | Format | Precision | Std Dev | Recall |
|------|--------|-----------|---------|--------|
| 1 | `::` (double colon) | 1.000 | 0.000 | 0.997 |
| 2 | `: ` (colon space) | 1.000 | 0.000 | 0.989 |
| 3 | CSV quoted | 1.000 | 0.000 | 0.991 |
| 4 | TOML | 0.999 | 0.003 | 0.988 |
| 5 | `:` (colon) | 0.999 | 0.003 | 0.998 |
| 6 | CSV raw | 0.999 | 0.002 | 0.953 |
| 7 | JSON | 0.998 | 0.004 | 0.979 |
| 8 | YAML | 0.991 | 0.006 | 0.991 |
| 9 | Markdown table | 0.978 | 0.038 | 0.950 |
| 10 | XML | 0.956 | 0.161 | 0.965 |

**Key insight:** Format TYPE matters more than token efficiency. Key-value formats outperform structured formats (XML, YAML) despite intuition.

## Academic Research Context

**Sclar et al. ICLR 2024** (arXiv:2310.11324):
- Up to 76 accuracy points variance from minor format changes
- Separators claimed highest impact (43% weak, 22% strong difference)
- [CONTRADICTED by TK-001]: Modern frontier models show no separator sensitivity

**Microsoft/MIT 2024** (arXiv:2411.10541):
- 200-300% improvement possible by switching formats
- Format preferences don't transfer between model families
- GPT-4 more robust than GPT-3.5 to format changes

**OpenAI GPT-4.1 Guide**:
- JSON performs poorly for document contexts
- XML works well for long context
- Markdown recommended as starting point

## Expected Outcomes

**If CSV outperforms other formats:**
- Confirms token efficiency matters for scale
- Supports CSV as optimal production format

**If key-value formats match or exceed CSV:**
- Confirms TK-001 finding that format TYPE > token count
- Key-value structure aids extraction comprehension

## Source Documents

- Test 01: `_INFO_CSVScaleLimits.md [TBLF-IN01]` - CSV baseline results
- Format Research: `IPPS/_PrivateSessions/_2026-03-04_LLMMarkdownOptimization/_INFO_LLM_MARKDOWN_PREFERENCES.md [LLMO-IN01]` - TK-001 benchmark, academic papers
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
