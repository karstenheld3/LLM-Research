# SPEC: Unified LLM Client

**Doc ID (TDID)**: LLMC-SP01
**Feature**: llm-client
**Goal**: Define a unified, model-agnostic LLM client module for programmatic use with parallel workers
**Timeline**: Created 2026-03-05
**Target file**: `.windsurf/skills/llm-evaluation/llm_client.py`

**Depends on:**
- `model-registry.json` for model configurations and prefix matching
- `model-parameter-mapping.json` for effort level mappings
- `model-pricing.json` for cost calculation (from llm-transcription skill)

**Does not depend on:**
- `evaluate-answers.py` (separate evaluation concern)
- `find-workers-limit.py` (separate rate limit concern)

## MUST-NOT-FORGET

- Re-use existing JSON config files from `.windsurf/skills/llm-evaluation/`
- Support both OpenAI and Anthropic providers transparently
- Handle 4 different parameter methods: temperature, reasoning_effort, effort, thinking
- Anthropic constraint: max_tokens MUST be greater than thinking.budget_tokens
- OpenAI uses `max_completion_tokens` for gpt-5/o1/o3/o4, `max_tokens` for older models
- Retry with exponential backoff on transient failures
- Support both image and text input types
- Prompt caching differs: OpenAI automatic, Anthropic requires explicit cache_control

## Table of Contents

1. [Scenario](#1-scenario)
2. [Context](#2-context)
3. [Domain Objects](#3-domain-objects)
4. [Functional Requirements](#4-functional-requirements)
5. [Design Decisions](#5-design-decisions)
6. [Implementation Guarantees](#6-implementation-guarantees)
7. [Key Mechanisms](#7-key-mechanisms)
8. [Action Flow](#8-action-flow)
9. [Data Structures](#9-data-structures)
10. [Edge Cases](#10-edge-cases)
11. [Implementation Details](#11-implementation-details)
12. [Document History](#12-document-history)

## 1. Scenario

**Problem:** Multiple LLM providers (OpenAI, Anthropic) have different APIs, parameter names, and model-specific behaviors. Each model family uses different mechanisms for controlling output quality (temperature vs reasoning_effort vs thinking budgets). Scripts that call LLMs must handle all these variations.

**Solution:**
- Single importable module with `LLMClient` class
- Auto-detects provider from model ID
- Abstracted "effort level" system that maps to correct API parameters per model
- External JSON configs for model registry and parameter mappings
- Thread-safe for use with parallel workers
- Consistent return format regardless of provider

**What we don't want:**
- Hardcoded model lists in script code
- Provider-specific code paths scattered throughout calling scripts
- Manual temperature/reasoning_effort selection per model
- Duplicate API handling logic in multiple scripts

## 2. Context

The `llm-evaluation` skill contains scripts for LLM evaluation pipelines. The core LLM calling functionality is duplicated across `call-llm.py` and `call-llm-batch.py`. This spec defines a unified `llm_client.py` that extracts and consolidates all LLM calling logic.

The script must re-use existing JSON configuration files:
- `model-registry.json` - Model properties, limits, and prefix-based config lookup
- `model-parameter-mapping.json` - Effort level definitions and mappings

## 3. Domain Objects

### Provider

A **Provider** represents an LLM API provider.

**Supported providers:**
- `openai` - OpenAI API (gpt-*, o1-*, o3-*, o4-*)
- `anthropic` - Anthropic API (claude-*)

### Model

A **Model** represents a specific LLM model with its capabilities.

**Key properties:**
- `model_id` - API model identifier (e.g., "gpt-5-mini", "claude-sonnet-4-20250514")
- `provider` - Provider name ("openai" or "anthropic")
- `method` - Parameter method ("temperature", "reasoning_effort", "effort", "thinking")
- `max_output` - Maximum output tokens
- `temp_max` - Maximum temperature value (for temperature method)
- `thinking_max` - Maximum thinking budget tokens (for thinking method)
- `seed` - Whether seed parameter is supported (boolean)

### EffortLevel

An **EffortLevel** represents a unified abstraction for model behavior control.

**Valid levels:** `none`, `minimal`, `low`, `medium`, `high`, `xhigh`

**Mappings per level:**
- `temperature_factor` - Multiplier for model's temp_max (0.0 to 0.5)
- `openai_reasoning_effort` - OpenAI reasoning_effort value ("none" to "xhigh")
- `anthropic_thinking_factor` - Multiplier for model's thinking_max (0.0 to 1.0)
- `output_length_factor` - Multiplier for model's max_output (0.25 to 1.0)

### APIParams

**APIParams** represents the computed API call parameters.

**Key properties:**
- `temperature` - Temperature value (if method=temperature)
- `reasoning_effort` - OpenAI reasoning effort (if method=reasoning_effort)
- `effort` - Anthropic effort (if method=effort)
- `thinking` - Anthropic thinking config (if method=thinking)
- `max_tokens` - Maximum output tokens
- `seed` - Random seed (optional, OpenAI only)

### InputType

An **InputType** represents the type of input content.

**Valid types:**
- `image` - Image file (.jpg, .jpeg, .png, .gif, .webp)
- `text` - Text file (.txt, .md, .json, .py, .html, .xml, .csv)

### LLMResponse

An **LLMResponse** represents the unified response from any LLM call.

**Key properties:**
- `text` - Response text content
- `usage` - Token usage object
- `model` - Actual model ID used
- `finish_reason` - Why generation stopped ("stop", "length", "max_tokens")

### Usage

A **Usage** object tracks token consumption.

**Key properties:**
- `input_tokens` - Tokens in prompt
- `output_tokens` - Tokens in response
- `cached_tokens` - Cached input tokens (OpenAI)
- `cache_read_tokens` - Cache read tokens (Anthropic)
- `cache_write_tokens` - Cache write tokens (Anthropic)

### Pricing

A **Pricing** entry defines cost per million tokens for a model.

**Storage:** `model-pricing.json`

**Key properties:**
- `input_per_1m` - Cost per 1M input tokens (USD)
- `output_per_1m` - Cost per 1M output tokens (USD)
- `currency` - Currency code (always "USD")

### Cost

A **Cost** object tracks monetary cost of an API call.

**Key properties:**
- `input_cost` - Cost for input tokens
- `output_cost` - Cost for output tokens
- `total_cost` - Sum of input and output cost
- `currency` - Currency code

## 4. Functional Requirements

**LLMC-FR-01: Provider Auto-Detection**
- Detect provider from model ID prefix
- OpenAI prefixes: `gpt-`, `o1-`, `o3-`, `o4-`, `davinci`, `curie`, `babbage`, `ada`
- Anthropic prefixes: `claude-`
- Error if model ID does not match any known prefix

**LLMC-FR-02: Model Config Lookup**
- Load model config from `model-registry.json`
- Use prefix matching on `model_id_startswith` array
- Return first matching entry (order matters - more specific prefixes first)
- Error with list of known prefixes if no match found

**LLMC-FR-03: API Parameter Building**
- Accept effort levels: `--temperature`, `--reasoning-effort`, `--output-length`
- Map effort levels to actual API parameters based on model's `method`
- Temperature method: `temperature = temperature_factor * temp_max`
- Reasoning effort method: `reasoning_effort = openai_reasoning_effort`
- Effort method: `effort = openai_reasoning_effort` (Anthropic beta)
- Thinking method: `thinking.budget_tokens = anthropic_thinking_factor * thinking_max`
- Output length: `max_tokens = output_length_factor * max_output`

**LLMC-FR-04: Anthropic Thinking Constraint**
- When thinking is enabled (budget_tokens > 0), max_tokens MUST exceed thinking budget
- Auto-adjust: `max_tokens = thinking_budget + 1024` if constraint violated
- Log warning when auto-adjustment occurs

**LLMC-FR-05: OpenAI Token Parameter Selection**
- Use `max_completion_tokens` for: gpt-5*, o1-*, o3-*, o4-*
- Use `max_tokens` for: gpt-3.5*, gpt-4*, older models
- Detection: check if model contains "gpt-5", "o1-", "o3-", or "o4-"

**LLMC-FR-06: Seed Parameter Handling**
- Accept optional `--seed` parameter
- Only apply seed if model config has `seed: true`
- Log warning if seed provided but model does not support it

**LLMC-FR-07: API Key Loading**
- Load API keys from `.env` or key=value file
- Support `OPENAI_API_KEY` for OpenAI
- Support `ANTHROPIC_API_KEY` for Anthropic
- Skip empty lines and lines starting with `#`
- Error if required key not found

**LLMC-FR-08: Input Type Detection**
- Detect input type from file extension
- Image extensions: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
- Text extensions: `.txt`, `.md`, `.json`, `.py`, `.html`, `.xml`, `.csv`
- Error if extension not recognized

**LLMC-FR-09: Image Encoding**
- Encode image files to base64
- Determine media type from extension (.jpg/.jpeg -> image/jpeg, etc.)
- Include in API call as image content block

**LLMC-FR-10: Text Input Handling**
- Read text file content as UTF-8
- Append to prompt with separator: `{prompt}\n\n---\n\n{text_content}`

**LLMC-FR-11: Retry with Backoff**
- Retry failed API calls up to 3 times
- Exponential backoff: 1s, 2s, 4s between retries
- Log retry attempts
- Raise final error after all retries exhausted

**LLMC-FR-12: OpenAI API Call**
- Build messages array with user role
- Handle image content as `image_url` type with base64 data URL
- Apply temperature, reasoning_effort, seed as applicable
- Extract response text from `choices[0].message.content`
- Extract usage from `response.usage`
- Extract cached tokens from `prompt_tokens_details.cached_tokens` if present
- Extract system_fingerprint if present

**LLMC-FR-13: Anthropic API Call**
- Build messages array with user role
- Handle image content as `image` type with base64 source
- Apply temperature, thinking as applicable
- Extract response text from first text block in `response.content`
- Extract usage including cache_creation_input_tokens and cache_read_input_tokens

**LLMC-FR-14: Prompt Caching (Anthropic)**
- When enabled, use system message with `cache_control: {type: "ephemeral"}`
- Move prompt to system message, add generic user message
- Cache images in user content with cache_control

**LLMC-FR-15: Prompt Caching (OpenAI)**
- Log info that OpenAI caching is automatic
- No API changes required

**LLMC-FR-16: Unified Response Format**
- Return consistent dict regardless of provider
- Required fields: `text`, `usage`, `model`, `finish_reason`
- Usage must have: `input_tokens`, `output_tokens`
- Optional usage fields: `cached_tokens`, `cache_read_tokens`, `cache_write_tokens`
- `finish_reason` values: `stop` (normal), `length` (truncated at max_tokens)

**LLMC-FR-17: Thread Safety**
- LLMClient instances are thread-safe for use with ThreadPoolExecutor
- Thread safety achieved via immutable instance state after `__init__`
- Each worker can use same client instance (recommended) or create its own
- No shared mutable state between calls

**LLMC-FR-18: Client Reuse**
- Single LLMClient instance can make multiple calls
- API client created once during initialization
- Configs loaded once and cached

**LLMC-FR-19: Call Method**
- `client.call(prompt: str) -> dict` - Main API for LLM calls
- Returns unified response dict with text, usage, model, finish_reason
- Handles retry internally

**LLMC-FR-20: Client Info Method**
- `client.get_info() -> dict` - Return client configuration
- Returns: model, provider, method, api_params

**LLMC-FR-21: Pricing Config Loading**
- Load pricing from `model-pricing.json`
- Lookup by provider and model prefix
- Fall back to exact model match if prefix not found

**LLMC-FR-22: Cost Calculation**
- Calculate cost from usage tokens and pricing config
- Formula: `input_cost = (input_tokens / 1_000_000) * input_per_1m`
- Formula: `output_cost = (output_tokens / 1_000_000) * output_per_1m`
- Formula: `total_cost = input_cost + output_cost`

**LLMC-FR-23: Cost Reporting**
- Include cost in response when `--show-cost` flag is set
- Include cost in metadata JSON when `--write-json-metadata` is set
- Log cost to stderr: "Cost: $X.XXXX (input: $X.XXXX, output: $X.XXXX)"

**LLMC-FR-24: Unknown Model Pricing**
- If model not found in pricing config, log warning
- Continue without cost calculation (cost fields omitted from output)

**LLMC-FR-25: Response Format**
- Accept `--response-format` parameter: `text` (default), `json`
- JSON format returns structured output with text, usage, model fields

**LLMC-FR-26: Model Name Sanitization**
- Sanitize model name for file paths: replace `/` and `:` with `_`
- Used in output filenames and metadata files

**LLMC-FR-27: System Fingerprint (OpenAI)**
- Extract `system_fingerprint` from OpenAI response if present
- Include in response metadata

**LLMC-FR-28: Script Directory Resolution**
- Resolve config file paths relative to script location
- Use `Path(__file__).parent` to find JSON configs

### Module API for Parallel Workers

**LLMC-FR-29: LLMClient Class**
- Constructor: `LLMClient(model: str, reasoning_effort: str = 'medium', output_length: str = 'high', api_key: str = None, timeout: int = 300)`
- Automatically loads configs from module directory
- Creates appropriate provider client (OpenAI or Anthropic)
- `timeout` parameter sets request timeout in seconds (default 300s for long generations)

**LLMC-FR-30: Standalone Functions**
- `get_model_config(model: str) -> dict` - Get model config without creating client
- `build_api_params(model, reasoning_effort, output_length, seed) -> tuple` - Build params without client
- `create_client(provider: str, api_key: str = None)` - Create raw provider client

**LLMC-FR-31: Environment Variable Fallback**
- Precedence order: `api_key` parameter > environment variable
- If `api_key` not provided, check `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` env vars
- Error if required key not found in either location

**LLMC-FR-32: Config Path Resolution**
- Configs loaded from same directory as `llm_client.py`
- Use `Path(__file__).parent` for reliable resolution
- Works when imported from any location

**LLMC-FR-33: Parallel Worker Compatibility**
- Safe to use with `ThreadPoolExecutor` or `concurrent.futures`
- Safe to use with `asyncio` via `run_in_executor`
- No global state that could cause race conditions

## 5. Design Decisions

**LLMC-DD-01:** Use prefix matching for model config lookup. Rationale: Model IDs include version dates (e.g., "claude-sonnet-4-20250514") that change frequently. Prefix matching ("claude-sonnet-4") is more maintainable.

**LLMC-DD-02:** Unified effort levels across providers. Rationale: "medium" effort means the same thing regardless of whether the model uses temperature (0.7) or reasoning_effort ("medium") or thinking budget (10000 tokens).

**LLMC-DD-03:** Configs may be embedded or loaded from external JSON. Rationale: Embedded configs provide single-file portability for research scripts. External JSON is preferable for production systems requiring frequent model updates.

**LLMC-DD-04:** More specific prefixes listed first in registry. Rationale: "gpt-5-pro" must match before "gpt-5" for correct config lookup.

**LLMC-DD-05:** Importable module, not CLI script. Rationale: Must be usable with ThreadPoolExecutor for parallel API calls. CLI wrappers can be built on top if needed.

**LLMC-DD-06:** Config format matches existing skill JSON files. Rationale: Whether embedded or loaded externally, config structure must match `model-registry.json` and `model-parameter-mapping.json` schemas for consistency.

## 6. Implementation Guarantees

**LLMC-IG-01:** All API calls wrapped in retry_with_backoff

**LLMC-IG-02:** Response always contains text, usage.input_tokens, usage.output_tokens, model

**LLMC-IG-03:** Anthropic thinking constraint always enforced (auto-adjust if violated)

**LLMC-IG-04:** Unknown model prefix results in clear error with list of known prefixes

**LLMC-IG-05:** Missing API key results in clear error with required key name

**LLMC-IG-06:** File encoding always UTF-8

**LLMC-IG-07:** Output directory created if needed (--output-file)

## 7. Key Mechanisms

### Prefix Matching Algorithm

```
for each entry in model_id_startswith:
  if model.startswith(entry.prefix):
    return entry
error("Unknown model, known prefixes: ...")
```

Order in JSON matters - more specific prefixes must come first.

### Effort Level Mapping

```
CLI Input          Method          API Parameter
--temperature=high + temperature -> temperature=0.5 * temp_max
--reasoning-effort=high + reasoning_effort -> reasoning_effort="high"
--reasoning-effort=high + effort -> effort="high" (Anthropic beta)
--reasoning-effort=high + thinking -> thinking.budget_tokens=0.32 * thinking_max
--output-length=high + any -> max_tokens=1.0 * max_output
```

### Token Parameter Selection (OpenAI)

```
if "gpt-5" in model or "o1-" in model or "o3-" in model or "o4-" in model:
  use max_completion_tokens
else:
  use max_tokens
```

## 8. Action Flow

```
User runs llm_client.py --model X --prompt-file Y
├─> load_api_keys(keys_file)
│   └─> Parse .env format, extract OPENAI_API_KEY or ANTHROPIC_API_KEY
├─> load_configs(script_dir)
│   ├─> Load model-parameter-mapping.json
│   └─> Load model-registry.json
├─> build_api_params(model, mapping, registry, effort_levels)
│   ├─> get_model_config(model, registry)
│   │   └─> Prefix match in model_id_startswith
│   ├─> Map effort levels to API params based on method
│   ├─> Enforce Anthropic thinking constraint
│   └─> Return (params, method, provider)
├─> detect_file_type(input_file) if provided
│   └─> Return 'image' or 'text'
├─> Load/encode input content
│   ├─> Image: encode_image_to_base64(), get_image_media_type()
│   └─> Text: read_text(), append to prompt
├─> create_client(provider, keys)
│   ├─> OpenAI: OpenAI(api_key=...)
│   └─> Anthropic: Anthropic(api_key=...)
├─> retry_with_backoff(call_fn)
│   ├─> call_openai() or call_anthropic()
│   └─> Return unified response dict
└─> Output response
    ├─> Write to --output-file or stdout
    └─> Write .meta.json if --write-json-metadata
```

## 9. Data Structures

### model-registry.json (existing, re-use)

```json
{
  "_version": "1.2.0",
  "model_id_startswith": [
    {
      "prefix": "gpt-4o",
      "provider": "openai",
      "method": "temperature",
      "max_input": 128000,
      "max_output": 16384,
      "temp_max": 2.0,
      "seed": true
    },
    {
      "prefix": "gpt-5",
      "provider": "openai",
      "method": "reasoning_effort",
      "max_output": 32768,
      "effort": ["minimal", "low", "medium", "high"],
      "default": "medium",
      "seed": false
    },
    {
      "prefix": "claude-sonnet-4",
      "provider": "anthropic",
      "method": "thinking",
      "max_output": 8192,
      "thinking_max": 100000
    }
  ]
}
```

### model-parameter-mapping.json (existing, re-use)

```json
{
  "_version": "2.1.0",
  "effort_levels": ["none", "minimal", "low", "medium", "high", "xhigh"],
  "defaults": {
    "temperature": "medium",
    "reasoning_effort": "medium",
    "output_length": "medium"
  },
  "effort_mapping": {
    "none":    { "temperature_factor": 0.0,  "openai_reasoning_effort": "none",    "anthropic_thinking_factor": 0.0,  "output_length_factor": 0.25 },
    "minimal": { "temperature_factor": 0.1,  "openai_reasoning_effort": "minimal", "anthropic_thinking_factor": 0.01, "output_length_factor": 0.5 },
    "low":     { "temperature_factor": 0.2,  "openai_reasoning_effort": "low",     "anthropic_thinking_factor": 0.04, "output_length_factor": 0.5 },
    "medium":  { "temperature_factor": 0.35, "openai_reasoning_effort": "medium",  "anthropic_thinking_factor": 0.1,  "output_length_factor": 0.75 },
    "high":    { "temperature_factor": 0.5,  "openai_reasoning_effort": "high",    "anthropic_thinking_factor": 0.32, "output_length_factor": 1.0 },
    "xhigh":   { "temperature_factor": 0.5,  "openai_reasoning_effort": "xhigh",   "anthropic_thinking_factor": 1.0,  "output_length_factor": 1.0 }
  }
}
```

### LLMResponse (unified output)

```json
{
  "text": "The response content...",
  "usage": {
    "input_tokens": 1500,
    "output_tokens": 500,
    "cached_tokens": 0,
    "cache_read_tokens": 0,
    "cache_write_tokens": 0
  },
  "model": "gpt-5-mini",
  "finish_reason": "stop",
  "system_fingerprint": "fp_abc123"
}
```

### model-pricing.json (existing, re-use from llm-transcription)

```json
{
  "pricing": {
    "openai": {
      "gpt-5-mini": {"input_per_1m": 0.25, "output_per_1m": 2.00, "currency": "USD"},
      "gpt-5": {"input_per_1m": 1.25, "output_per_1m": 10.00, "currency": "USD"},
      "gpt-4o": {"input_per_1m": 2.50, "output_per_1m": 10.00, "currency": "USD"}
    },
    "anthropic": {
      "claude-sonnet-4-20250514": {"input_per_1m": 3.00, "output_per_1m": 15.00, "currency": "USD"},
      "claude-3-5-haiku-20241022": {"input_per_1m": 0.80, "output_per_1m": 4.00, "currency": "USD"}
    }
  },
  "last_updated": "2026-01-24",
  "sources": ["https://platform.openai.com/docs/pricing", "https://docs.anthropic.com/en/docs/about-claude/models/pricing"]
}
```

### Metadata file (.meta.json)

```json
{
  "model": "gpt-5-mini",
  "usage": { "input_tokens": 1500, "output_tokens": 500 },
  "cost": { "input_cost": 0.000375, "output_cost": 0.001, "total_cost": 0.001375, "currency": "USD" },
  "timestamp": "2026-03-05T21:30:00Z",
  "input_file": "data.csv",
  "prompt_file": "prompt.md"
}
```

## 10. Edge Cases

**LLMC-EC-01: Unknown Model Prefix**
- Input: `--model unknown-model-xyz`
- Behavior: Error with message listing all known prefixes from model_id_startswith

**LLMC-EC-02: Missing API Key**
- Input: Provider is anthropic but ANTHROPIC_API_KEY not in keys file
- Behavior: Error "[ERROR] ANTHROPIC_API_KEY not found in keys file"

**LLMC-EC-03: Unsupported File Extension**
- Input: `--input-file data.xyz`
- Behavior: Error listing supported extensions

**LLMC-EC-04: Seed on Non-Supporting Model**
- Input: `--model gpt-5-mini --seed 42` (gpt-5 has seed=false)
- Behavior: Log warning, ignore seed, continue with call

**LLMC-EC-05: Anthropic Thinking Budget Exceeds Max Tokens**
- Input: Model with thinking_max=100000, output_length=low (factor=0.5, max_output=8192 -> 4096 tokens)
- Result: thinking_budget = 0.1 * 100000 = 10000, max_tokens = 4096
- Behavior: Auto-adjust max_tokens to 10000 + 1024 = 11024, log warning

**LLMC-EC-06: Empty Input File**
- Input: `--input-file empty.txt` (0 bytes)
- Behavior: Proceed with prompt only (text appended is empty string)

**LLMC-EC-07: API Rate Limit Error**
- Behavior: Retry with backoff (1s, 2s, 4s), raise after 3 failures

**LLMC-EC-08: API Timeout**
- Behavior: Retry with backoff, raise after 3 failures

**LLMC-EC-09: Truncated Response**
- Finish reason is "length" or "max_tokens"
- Behavior: Return response as-is, caller must check finish_reason

**LLMC-EC-10: Keys File Not Found**
- Input: `--keys-file nonexistent.env`
- Behavior: Error "[ERROR] Keys file not found: nonexistent.env"

**LLMC-EC-11: Prompt File Not Found**
- Input: `--prompt-file nonexistent.md`
- Behavior: Error "[ERROR] Prompt file not found: nonexistent.md"

**LLMC-EC-12: Output Directory Does Not Exist**
- Input: `--output-file deep/nested/dir/output.md`
- Behavior: Create parent directories, write file

**LLMC-EC-13: Workers Set to Zero (Batch)**
- Input: `--workers 0`
- Behavior: Log warning, default to 1 worker

**LLMC-EC-14: No Files in Input Folder (Batch)**
- Input: Empty input folder
- Behavior: Error "[ERROR] No files found in {folder}"

**LLMC-EC-15: Resume with Existing Outputs (Batch)**
- Input: Output file already exists for a specific run
- Behavior: Skip that run unless --force specified

**LLMC-EC-16: Model Not in Pricing Config**
- Input: Model "gpt-5.3-beta" not listed in model-pricing.json
- Behavior: Log warning "[WARN] No pricing found for gpt-5.3-beta", omit cost from output

**LLMC-EC-17: Pricing File Not Found**
- Input: model-pricing.json does not exist
- Behavior: Log warning, continue without cost calculation

## 11. Implementation Details

### Module API

```python
from llm_client import LLMClient, get_model_config, build_api_params

# Basic usage
client = LLMClient("gpt-5-mini")
response = client.call("Extract all employee IDs from this data...")
print(response["text"])

# With custom effort levels
client = LLMClient("gpt-5-mini", reasoning_effort="high", output_length="high")

# With explicit API key
client = LLMClient("claude-sonnet-4-20250514", api_key="sk-...")

# Get client info
info = client.get_info()
# {"model": "gpt-5-mini", "provider": "openai", "method": "reasoning_effort", "api_params": {...}}

# Standalone functions (no client needed)
config = get_model_config("gpt-5-mini")
params, method, provider = build_api_params("gpt-5-mini", "medium", "high")
```

### Usage with Parallel Workers

```python
from concurrent.futures import ThreadPoolExecutor
from llm_client import LLMClient

client = LLMClient("gpt-5-mini", reasoning_effort="medium")

def process_item(prompt):
    return client.call(prompt)

with ThreadPoolExecutor(max_workers=5) as executor:
    prompts = ["prompt1...", "prompt2...", "prompt3..."]
    results = list(executor.map(process_item, prompts))
```

### Effort Levels

Valid levels: `none`, `minimal`, `low`, `medium`, `high`, `xhigh`
```

### Class and Function Signatures

```python
# Main class
class LLMClient:
    def __init__(self, model: str, reasoning_effort: str = 'medium', 
                 output_length: str = 'high', api_key: str = None)
    def call(self, prompt: str) -> dict
    def get_info(self) -> dict
    
    # Instance attributes
    model: str
    provider: str
    method: str
    api_params: dict
    client: OpenAI | Anthropic

# Public standalone functions (can be used without LLMClient)
def get_model_config(model: str) -> dict
def build_api_params(model: str, reasoning_effort: str = 'medium',
                     output_length: str = 'high', seed: int = None) -> tuple[dict, str, str]
def create_client(provider: str, api_key: str = None) -> OpenAI | Anthropic

# Internal functions (used by LLMClient)
def retry_with_backoff(fn, retries=3, backoff=(1, 2, 4))
def call_llm(client, model: str, prompt: str, api_params: dict, provider: str) -> dict

# Pricing functions
def load_pricing(pricing_file: Path = None) -> dict
def get_model_pricing(model: str, provider: str, pricing: dict) -> dict | None
def calculate_cost(usage: dict, pricing: dict) -> dict
```

### Exceptions

- `ValueError` - Unknown model prefix, missing API key
- `RuntimeError` - API error after all retries exhausted

### Dependencies

- `openai` - OpenAI Python SDK
- `anthropic` - Anthropic Python SDK
- Standard library: `os`, `sys`, `json`, `time`, `pathlib`

## 12. Document History

**[2026-03-05 21:49]**
- Fixed: DD-03, DD-06 - Allow embedded configs for portability (LLMC-RV-002)
- Fixed: FR-16 - Make finish_reason required for truncation detection (LLMC-RV-008)
- Fixed: FR-31 - Add API key precedence order (LLMC-RV-005)
- Fixed: FR-29 - Add timeout parameter with 300s default (LLMC-RV-007)
- Fixed: FR-17 - Document thread safety mechanism (LLMC-RV-001)

**[2026-03-05 21:46]**
- Changed: From CLI script to importable module with LLMClient class
- Changed: FR-17 to FR-20 from CLI args to thread safety and module API
- Changed: FR-29 to FR-33 from batch CLI to module API for parallel workers
- Changed: Function signatures to class-based API
- Removed: CLI arguments section
- Added: Module API usage examples with ThreadPoolExecutor

**[2026-03-05 21:45]**
- Added: Response format (LLMC-FR-25)
- Added: Model name sanitization (LLMC-FR-26)
- Added: System fingerprint (LLMC-FR-27)
- Added: Script directory resolution (LLMC-FR-28)

**[2026-03-05 21:41]**
- Added: Pricing config loading (LLMC-FR-21)
- Added: Cost calculation (LLMC-FR-22)
- Added: Cost reporting (LLMC-FR-23)
- Added: Unknown model pricing handling (LLMC-FR-24)
- Added: Pricing and Cost domain objects
- Added: model-pricing.json data structure
- Added: Edge cases LLMC-EC-16, LLMC-EC-17
- Added: --show-cost and --pricing-file CLI args
- Added: Pricing function signatures

**[2026-03-05 21:35]**
- Initial specification created from analysis of llm-evaluation skill scripts
