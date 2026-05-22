---
description: Autonomous loop until goal reached
---

# Go Workflow

Autonomous execution loop using `/recap` and `/continue`.

## Required Reading

- `rules/devsystem-core.md` - Workflow Reference lists all available workflows and skills

## MUST-NOT-FORGET

- Check if goal already reached (Step 1) before any work
- Log blockers to PROBLEMS.md immediately
- Run `/verify` before declaring goal reached
- Never sacrifice requirements - implement 100%
- No shortcuts, no lazy programming

## Step 1: Completion Check

Check if goal is already reached:

1. Read STRUT plan (PROGRESS.md or session document)
2. Run `/verify` to check:
   - All Deliverables in final phase checked?
   - Final Transition points to `[END]`?

If complete:
```
Goal already reached. No further work needed.
```
Stop. Do not re-verify on subsequent `/go` calls.

If not complete: Proceed to Step 2.

## Step 2: Recap

Run `/recap` to determine:
- Last completed action
- Current state
- Any blockers

## Step 3: Pre-Flight Check

1. Gather more context if unclear
2. Verify stop/acceptance criteria exist
3. Make internal MUST-NOT-FORGET list from conversation
4. List all scripts and skills needed for task completion

## Step 4: Execute

Run `/continue` to:
- Execute next task from plan
- Update progress
- Check for completion

## Step 5: Loop

```
iteration_count = 0
WHILE goal not reached AND iteration_count < 5:
    iteration_count += 1
    /recap
    /continue
    
    IF iteration_count >= 5:
        Ask user: "Reached 5 iterations. Continue?"
    
    IF blocker:
        Log to PROBLEMS.md with [BLOCKER] id
        /write-info `.tmp_INFO_[BLOCKER].md` (root cause analysis)
        /critique -> /reconcile -> /write-tasks-plan `.tmp_TASK_[BLOCKER].md`
        /verify -> /implement -> /verify
```

## Stopping Conditions

- All tasks complete (final Transition = `[END]` checked)
- Blocker requires user input
- User interruption
- Retry limit exceeded (5 attempts for MEDIUM/HIGH complexity)

## Idempotent Behavior

Multiple `/go` commands on completed work:

1. First `/go` after completion: Output "Goal already reached" message
2. Subsequent `/go`: Same message, no re-verification, no action

This prevents:
- Wasted tokens on redundant verification
- Misinterpreting queued `/go` as dissatisfaction
- Overengineering completed deliverables