# Failure Log

**Goal**: Document failures, mistakes, and lessons learned to prevent repetition

## Table of Contents

1. [Active Issues](#active-issues)
2. [Resolved Issues](#resolved-issues)
3. [Document History](#document-history)

## Active Issues

### 2026-03-05 - Logging Output

#### [HIGH] `TBLF-FL-003` Not Following Full Disclosure Principle

- **When**: 2026-03-05 19:01
- **Where**: `01_FindTabularDataScaleLimits_V1/_Scripts/02_execute_and_evaluate.py` - entire logging approach
- **What**: Agent repeatedly failed to understand logging principles despite having LOGGING-RULES.md available. Changed "TC-01" to "run 1" - equally meaningless. Logs lack context needed to understand without looking elsewhere.
- **Why it went wrong**: 
  1. Copied syntax patterns without understanding underlying principles
  2. Did not apply "Full Disclosure" - each line should be understandable without context
  3. Did not apply "Visible Structure" - logs should reveal workflow mechanics
  4. Focused on cosmetic fixes instead of asking: "What would a reader need to know?"
- **Evidence**: `[ 1 / 2 ] LLM extraction run 1...` - What model? What data? What prompt?
- **Suggested fix**: Include all context in the log line itself: model, rows, prompt file

**Principle violated** (LOG-GN Full Disclosure):
> "Each log line should be understandable without context. Include the subject (what), the action (verb), and the target (where/which)."

#### [MEDIUM] `TBLF-FL-002` Meaningless Test Case IDs

- **When**: 2026-03-05 18:57
- **Where**: `01_FindTabularDataScaleLimits_V1/_Scripts/02_execute_and_evaluate.py` line 117, 223
- **What**: Used `TC-01`, `TC-02` test case IDs that mean nothing to a QA engineer reading the log
- **Why it went wrong**: Blindly copied LOG-SC-03 format without understanding the principle. LOG-SC rules state "log output alone must be sufficient to diagnose the problem" - meaningless IDs violate this.
- **Evidence**: Output: `[ 1 / 2 ] TC-01: Executing...` - what is TC-01?
- **Suggested fix**: Use descriptive names: `LLM extraction run 1`

**Code example**:
```python
# Before (wrong - meaningless ID)
print(f"[ {run_id} / {total_runs} ] TC-{run_id:02d}: Executing...")

# After (correct - descriptive)
print(f"[ {run_id} / {total_runs} ] LLM extraction run {run_id}...")
```

#### [MEDIUM] `TBLF-FL-001` Cryptic Abbreviations in Script Output

- **When**: 2026-03-05 18:56
- **Where**: `01_FindTabularDataScaleLimits_V1/_Scripts/02_execute_and_evaluate.py` line 165
- **What**: Used cryptic abbreviations `P=1.00 R=1.00 F1=1.00` in logging output without any rule justification
- **Why it went wrong**: Agent invented abbreviations for "Precision", "Recall", "F1" without checking if this was allowed by DevSystem rules. No rule permits shortening these terms.
- **Evidence**: Output line: `OK. P=1.00 R=1.00 F1=1.00`
- **Suggested fix**: Use full words: `Precision=1.00 Recall=1.00 F1-Score=1.00` (F1 alone is also cryptic)

**Code example**:
```python
# Before (wrong - cryptic)
print(f"  {status} P={metrics['precision']:.2f} R={metrics['recall']:.2f} F1={metrics['f1']:.2f}")

# After (correct - clear)
print(f"  {status} Precision={metrics['precision']:.2f} Recall={metrics['recall']:.2f} F1={metrics['f1']:.2f}")
```

## Resolved Issues

(none yet)

## Document History

**[2026-03-05 19:01]**
- Added: TBLF-FL-003 - Not following Full Disclosure principle

**[2026-03-05 18:57]**
- Added: TBLF-FL-002 - Meaningless TC-XX test case IDs

**[2026-03-05 18:56]**
- Added: TBLF-FL-001 - Cryptic abbreviations in logging output
