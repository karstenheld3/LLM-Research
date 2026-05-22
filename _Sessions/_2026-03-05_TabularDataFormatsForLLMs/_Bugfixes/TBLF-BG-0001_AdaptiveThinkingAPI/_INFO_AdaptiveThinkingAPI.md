# INFO: Anthropic Adaptive Thinking API for Opus 4-7

**Doc ID**: TBLF-BG-0001-IN01
**Goal**: Document the API difference between thinking modes and the fix applied to llm_client.py

## Background

Anthropic's Extended Thinking API has two modes:

- **Manual mode** (`type: "enabled"`): Client specifies `budget_tokens` for thinking. Supported on Sonnet 4, Sonnet 4.5, Opus 4.5, Haiku 4.5.
- **Adaptive mode** (`type: "adaptive"`): Model decides whether and how much to think. Effort controlled via `output_config.effort`. Required on Opus 4-7, deprecated-but-working on Opus 4-6.

## API Formats

### Manual (legacy, pre-Opus 4-7)

```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    messages=[...]
)
```

### Adaptive (Opus 4-7, Opus 4-6)

```python
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=16000,
    thinking={"type": "adaptive"},
    extra_body={"output_config": {"effort": "medium"}},
    messages=[...]
)
```

Note: `output_config` is a top-level API parameter but not yet available as a keyword argument in the installed SDK version. Using `extra_body` for compatibility.

## Effort Levels

Anthropic supports: `"low"`, `"medium"`, `"high"`, `"max"`

Mapping defined in `model-parameter-mapping.json` as `anthropic_adaptive_effort` field:
- none, minimal, low -> "low"
- medium -> "medium"
- high -> "high"
- xhigh -> "max"

This mirrors how OpenAI reasoning effort is handled via `openai_reasoning_effort` - same pattern, config-driven, no hardcoded remaps in code.

## Model Support Matrix

- **claude-opus-4-7**: Adaptive only (manual returns 400 error)
- **claude-opus-4-6**: Adaptive required (manual deprecated, still works but shouldn't be used)
- **claude-sonnet-4-6**: Both manual and adaptive (plus interleaved mode)
- **claude-sonnet-4-20250514**: Manual (thinking with budget_tokens)
- **claude-sonnet-4-5-20250929**: Manual (thinking with budget_tokens)
- **claude-opus-4-5-20251101**: Both manual and adaptive
- **claude-haiku-4-5-20251001**: Both (but test uses temperature method)

## Changes Made

### model-registry.json

Added prefix entries (order matters - more specific before generic):

```json
{ "prefix": "claude-opus-4-7", "provider": "anthropic", "method": "adaptive_thinking",
  "max_input": 1000000, "max_output": 128000, "effort": ["low", "medium", "high", "max"] },
{ "prefix": "claude-opus-4-6", "provider": "anthropic", "method": "adaptive_thinking",
  "max_input": 200000, "max_output": 128000, "effort": ["low", "medium", "high", "max"] },
```

### model-parameter-mapping.json (v2.2.0)

Added `anthropic_adaptive_effort` field to each effort level:

```json
"none":    { ..., "anthropic_adaptive_effort": "low",    ... },
"minimal": { ..., "anthropic_adaptive_effort": "low",    ... },
"low":     { ..., "anthropic_adaptive_effort": "low",    ... },
"medium":  { ..., "anthropic_adaptive_effort": "medium", ... },
"high":    { ..., "anthropic_adaptive_effort": "high",   ... },
"xhigh":   { ..., "anthropic_adaptive_effort": "max",    ... }
```

### llm_client.py - build_api_params()

Single-line config lookup (same pattern as all other methods):

```python
elif method == 'adaptive_thinking':
    params['thinking'] = {'type': 'adaptive'}
    params['anthropic_effort'] = effort_map[reasoning_effort]['anthropic_adaptive_effort']
```

### llm_client.py - _call_anthropic()

Updated thinking block handling:

```python
if 'thinking' in api_params:
    thinking_config = api_params['thinking']
    if thinking_config.get('type') == 'adaptive':
        call_params['thinking'] = thinking_config
        if 'anthropic_effort' in api_params:
            call_params['extra_body'] = {'output_config': {'effort': api_params['anthropic_effort']}}
    elif thinking_config.get('budget_tokens', 0) > 0:
        call_params['thinking'] = thinking_config
```

## SDK Note

The `anthropic` SDK 0.104.0+ supports `output_config` as a direct parameter. If SDK is upgraded, change `extra_body` to direct parameter:

```python
# After SDK upgrade:
call_params['output_config'] = {'effort': api_params['anthropic_effort']}
```

## Reference

Source: `E:\Dev\KarstensWorkspace\docs\Anthropic\Anthropic_API_2026-05-22\_INFO_ANTAPI-IN13_EXTENDED_THINKING.md`

## Document History

**[2026-05-22 15:19]**
- Updated: build_api_params() now uses config-driven lookup (anthropic_adaptive_effort field)
- Updated: model-parameter-mapping.json v2.2.0 with explicit effort mapping
- Removed: Hardcoded effort_remap dict in code

**[2026-05-22 12:15]**
- Initial documentation created
