# Session Problems

## Open

### TBLF-PR-001: Unknown optimal tabular format for LLMs

**Status**: Open
**Description**: Need to determine which tabular data format (CSV, JSON, XML, Markdown tables, etc.) LLMs can most effectively read, understand, and process
**Impact**: Format choice affects extraction accuracy, processing reliability, and token efficiency

### TBLF-PR-002: Format effectiveness may vary by task type

**Status**: Open
**Description**: Different formats may excel at different tasks (lookup vs aggregation vs filtering)
**Impact**: Recommendations may need to be task-specific

### TBLF-PR-003: Scale limits per format unknown

**Status**: Open
**Description**: Prior research (LLMO-TK-001) showed model reliability drops at 600 records, but this may vary by format
**Impact**: Need to establish safe operating limits per format

### TBLF-PR-004: Model-specific format preferences

**Status**: Open
**Description**: Claude, GPT, Gemini may have different format preferences
**Impact**: Recommendations may need model-specific variants

## Resolved

## Deferred
