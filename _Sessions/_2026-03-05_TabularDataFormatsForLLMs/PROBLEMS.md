# Session Problems

## Open

### TBLF-PR-001: Scale limits per format unknown

**Status**: Open
**Description**: Prior research (LLMO-TK-001) showed model reliability drops at 600 records, but this may vary by format
**Impact**: Need to establish safe operating limits per format

### TBLF-PR-002: Unknown optimal tabular format for LLMs

**Status**: Open
**Description**: Need to determine which tabular data format (CSV, JSON, XML, Markdown tables, etc.) LLMs can most effectively read, understand, and process
**Impact**: Format choice affects extraction accuracy, processing reliability, and token efficiency

### TBLF-PR-003: Model-specific format preferences

**Status**: Open
**Description**: Claude, GPT, Gemini may have different format preferences
**Impact**: Recommendations may need model-specific variants

### TBLF-PR-004: Format effectiveness may vary by task type

**Status**: Open
**Description**: Different formats may excel at different tasks (lookup vs aggregation vs filtering)
**Impact**: Recommendations may need to be task-specific

## Resolved

### TBLF-PR-005: Logging not compliant with LOG-SC rules

**Status**: Resolved
**Description**: Script output used cryptic abbreviations, meaningless IDs, missing context
**Resolution**: Fixed logging to follow Full Disclosure principle - each line self-contained with model, rows, expected records. Added `[ x / y ]` prefix to Report lines for parallel execution traceability.
**Related**: TBLF-FL-001, TBLF-FL-002, TBLF-FL-003 in FAILS.md

## Deferred

### TBLF-PR-006: H6 - CSV vs other formats at scale (Test 02)

**Status**: Deferred
**Hypothesis**: Quoted CSV maintains higher scale limits than XML/Markdown table
**Prior Evidence**: TK-001 showed XML and Markdown table had highest variance/failure rates at 300 rows
**Test Required**: Compare same extraction task with different formats (CSV, XML, JSON, Markdown table, key-value)
**Impact**: Determines optimal format recommendation for production use
**Blocked By**: Test 01 (scale limits) must complete first to establish baseline methodology
