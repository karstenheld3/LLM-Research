# Bug: TBLF-BG-0001 - claude-opus-4-7 Requires Adaptive Thinking API

**Doc ID**: TBLF-BG-0001
**Goal**: Document and fix API incompatibility for claude-opus-4-7 thinking mode

## Problem

**Status**: Resolved
**Reported**: 2026-05-22 12:07
**Resolved**: 2026-05-22 12:15

**Verbatim error**:
````
Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error',
'message': '"thinking.type.enabled" is not supported for this model. Use
"thinking.type.adaptive" and "output_config.effort" to control thinking behavior.'},
'request_id': 'req_011CbHRXnbqJkufLYijYDmgS'}
````

**Root Cause**: `llm_client.py` sent `thinking: {type: 'enabled', budget_tokens: N}` for all models matching the `claude-opus-4` prefix. Claude Opus 4-7 (and 4-6 deprecated) no longer support this format. They require `thinking: {type: 'adaptive'}` with `output_config: {effort: 'low'|'medium'|'high'|'max'}`.

**Impact**: Scale limit test for claude-opus-4-7 failed immediately (3 consecutive errors in 16 seconds, $0 cost). No data loss.

## Solution

**Summary**: Added `adaptive_thinking` method to `llm_client.py` and specific prefix entries in `model-registry.json` for opus-4-7 and opus-4-6.

**Changed files**:
- `01_CSVScaleLimits/_Scripts/llm_client.py` - Added `adaptive_thinking` method in `build_api_params()` and `extra_body` handling in `_call_anthropic()`
- `01_CSVScaleLimits/_Scripts/model-registry.json` - Added prefix entries for `claude-opus-4-7` and `claude-opus-4-6` with `method: "adaptive_thinking"`

## Impacted Functionality

- `03_find_scale_limit.py` - Uses LLMClient; now works with opus-4-7
- `02_execute_and_evaluate.py` - Uses LLMClient; now works with opus-4-7
- `test_llm_client.py` - Should add opus-4-7 to test matrix
- All other models - NOT impacted (prefix matching is order-dependent; specific prefixes checked first)

## Verification

- `.tmp_test_opus.py` confirmed both `claude-opus-4-7` and `claude-opus-4-6` respond correctly with adaptive thinking
- `test_llm_client.py` passed 12/12 for all existing models (no regression)

## Document History

**[2026-05-22 12:15]**
- Created: Full bug documentation after fix verified
