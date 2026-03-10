# Failure Log

**Goal**: Document failures, mistakes, and lessons learned to prevent repetition

## Table of Contents

1. [Active Issues](#active-issues)
2. [Resolved Issues](#resolved-issues)
3. [Document History](#document-history)

## Active Issues

### 2026-03-10 - Test Configuration

#### [HIGH] `TBLF-FL-005` Test 02 Column Configuration Mismatch

- **When**: 2026-03-10 07:47
- **Where**: `02_FormatComparison/_Scripts/01_generate_data.py` - data generation setup
- **What**: Test 02 used 7 out of 7 columns instead of replicating Test 01's 7 out of 20 columns configuration. This invalidates all baseline comparisons between Test 01 and Test 02 results.
- **Why it went wrong**:
  1. Did not verify Test 01's exact column configuration before implementing Test 02
  2. Assumed "7 columns" meant using all available columns, not selecting 7 from a larger set
  3. Failed to read Test 01 config files to understand the exact setup
  4. No cross-verification step between Test 01 and Test 02 configurations
- **Evidence**: Test 01 baseline data shows different scale limits than Test 02 csv_quoted results for same models, indicating different test conditions
- **Suggested fix**: 
  1. Review Test 01 configuration to identify exact 20 columns and which 7 were selected
  2. Update Test 02 data generation to match
  3. Re-run all 40 tests with correct configuration
  4. Add configuration verification step to test setup procedures

**Configuration comparison**:
```
Test 01: 7 columns selected FROM 20 available columns
Test 02: 7 columns selected FROM 7 available columns (WRONG)

Result: Baseline comparisons invalid - different data complexity
```

### 2026-03-06 - Terminal Management

#### [MEDIUM] `TBLF-FL-004` Launching Terminals Without Checking Existing Ones

- **When**: 2026-03-06 01:06
- **Where**: Agent workflow - `run_command` tool usage
- **What**: Agent repeatedly launched new background terminals for tests without first checking if existing terminals were still running. This led to 3+ orphaned terminals and attempted duplicate test runs (gpt-5 medium/high were already running as IDs 237/238 when agent tried to launch again as IDs 343/344).
- **Why it went wrong**:
  1. Did not use `command_status` to check if previous background commands were still running
  2. Assumed previous terminals had completed or been cancelled
  3. Did not maintain awareness of active command IDs across conversation
- **Evidence**: User reported "you are already running 3 terminals!"
- **Suggested fix**: Before launching new background commands, always:
  1. Check status of any known background command IDs
  2. Wait for completion or confirm cancellation
  3. Only then launch new commands

**Code pattern to follow**:
```python
# Before launching new tests:
# 1. Check existing command status
command_status(CommandId=last_command_id)

# 2. If still RUNNING, either wait or ask user
# 3. Only launch new if previous is DONE or CANCELED
```

### 2026-03-05 - Logging Output

#### [HIGH] `TBLF-FL-003` Not Following Full Disclosure Principle

- **When**: 2026-03-05 19:01
- **Where**: `01_CSVScaleLimits/_Scripts/02_execute_and_evaluate.py` - entire logging approach
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
- **Where**: `01_CSVScaleLimits/_Scripts/02_execute_and_evaluate.py` line 117, 223
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
- **Where**: `01_CSVScaleLimits/_Scripts/02_execute_and_evaluate.py` line 165
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

**[2026-03-10 07:47]**
- Added: TBLF-FL-005 - Test 02 column configuration mismatch (7/7 vs 7/20)

**[2026-03-05 19:01]**
- Added: TBLF-FL-003 - Not following Full Disclosure principle

**[2026-03-05 18:57]**
- Added: TBLF-FL-002 - Meaningless TC-XX test case IDs

**[2026-03-05 18:56]**
- Added: TBLF-FL-001 - Cryptic abbreviations in logging output
