# Tabular Extraction Test Approach Review

**Doc ID**: TBLF-SP01-RV02
**Goal**: Self-critique - identify methodological flaws attackers could exploit
**Reviewed**: 2026-03-05 18:15

## Critical Issues

### `TBLF-RV-011` Output Truncation - Missing max_output_tokens

- **What**: Config has `"max_output_tokens": null` - NO explicit limit passed to API
- **Evidence**: LLM output 74 lines when 93 expected
- **Risk**: Results INVALID - measuring truncation, not extraction accuracy
- **Attack**: "You didn't set max_output_tokens, of course it truncated"
- **Fix**: Set `max_output_tokens: 16384`, re-run benchmark

### `TBLF-RV-012` Ambiguous AND Logic in Filter Description

- **What**: 
  - POC: "**BOTH** must be true" (explicit)
  - Mine: "(ALL must be true)" (ambiguous)
- **Evidence**: 43 false positives - model applied OR instead of AND
- **Attack**: "Your prompt was ambiguous"
- **Fix**: Use "BOTH must be true", number criteria explicitly

## High Priority

### `TBLF-RV-013` No Truncation Detection

- **What**: No check for `finish_reason == "length"` 
- **Risk**: Truncated responses evaluated as "poor extraction"
- **Fix**: Store finish_reason, flag truncated as invalid

### `TBLF-RV-014` Dynamic Filter Rendering Ambiguity

- **What**: My render: `- clearance contains one of: Level 3, Level 4, Level 5` (no quotes)
- **POC**: `SecurityClearance contains "Level 3", "Level 4", or "Level 5"` (quoted)
- **Fix**: Quote filter values, match POC style

### `TBLF-RV-015` No Baseline Comparison

- **What**: No 50-row baseline to compare degradation
- **Attack**: "Your baseline is broken, scale has nothing to do with it"
- **Fix**: Run baseline at 50 rows first

## Research Findings

**Source**: ATLASSC.NET "LLM-Driven Information Extraction: Output Token Limitation"

- "Missing spans" = **60% of LLM extraction errors**
- "Silent Failure" - model omits entities without warning
- Our 74/93 (21% missing) matches this pattern exactly

## Vulnerability Summary

| Attack Vector | Severity | Exposed? |
|---------------|----------|----------|
| max_output_tokens not set | CRITICAL | YES |
| Ambiguous AND/OR logic | HIGH | YES |
| No truncation detection | HIGH | YES |
| No baseline comparison | MEDIUM | YES |

## Conclusion

**Current results (F1=0.28) are NOT PUBLISHABLE.** Results reflect truncation and prompt ambiguity, not model capability.

### Must Fix Before Re-run

1. Set `max_output_tokens: 16384`
2. Change to "BOTH must be true" 
3. Add truncation detection
4. Run 50-row baseline first
5. Quote filter values

## Document History

**[2026-03-05 18:15]**
- Initial self-critique comparing against POC prompts
