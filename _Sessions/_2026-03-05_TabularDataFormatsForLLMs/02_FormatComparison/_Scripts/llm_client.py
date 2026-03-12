#!/usr/bin/env python3
"""
llm_client.py - Unified LLM client with model-aware parameter handling.

Loads configuration from JSON files:
- model-registry.json: Model properties (provider, method, max_output, max_input)
- model-parameter-mapping.json: Effort level mappings

Supports:
- OpenAI: gpt-4o, gpt-4.1, gpt-5, o1, o3 (temperature or reasoning_effort)
- Anthropic: claude-3.5, claude-3.7, claude-4, claude-4.5 (temperature or thinking)
"""

import os, sys, json, time
from pathlib import Path


# Load JSON config files from same directory as this script
_SCRIPT_DIR = Path(__file__).parent

def _load_json_config(filename: str) -> dict:
  """Load JSON config from script directory."""
  config_path = _SCRIPT_DIR / filename
  if not config_path.exists():
    raise FileNotFoundError(f"Config file not found: {config_path}")
  with open(config_path, "r", encoding="utf-8") as f:
    return json.load(f)

# Load configs at module import time
_MODEL_REGISTRY = _load_json_config("model-registry.json")
_PARAMETER_MAPPING = _load_json_config("model-parameter-mapping.json")
_MODEL_PRICING = _load_json_config("model-pricing.json")

# Extract commonly used values
EFFORT_LEVELS = _PARAMETER_MAPPING.get("effort_levels", ['none', 'minimal', 'low', 'medium', 'high', 'xhigh'])
EFFORT_MAPPING = _PARAMETER_MAPPING.get("effort_mapping", {})
MODEL_REGISTRY = {"model_id_startswith": _MODEL_REGISTRY.get("model_id_startswith", [])}
MODEL_PRICING = _MODEL_PRICING.get("pricing", {})


def get_model_config(model: str) -> dict:
  """
  Return model config from registry using prefix matching.
  
  Normalizes JSON field names to internal names:
  - max_input -> max_context (for consistency)
  """
  for entry in MODEL_REGISTRY['model_id_startswith']:
    if model.startswith(entry['prefix']):
      config = entry.copy()
      # Normalize field names from JSON
      if 'max_input' in config and 'max_context' not in config:
        config['max_context'] = config['max_input']
      # Default max_context if not specified
      if config.get('max_context') is None:
        config['max_context'] = 1000000  # Default for models without explicit limit
      return config
  known = [e['prefix'] for e in MODEL_REGISTRY['model_id_startswith']]
  raise ValueError(f"Unknown model: {model}. Known prefixes: {known}")


def estimate_tokens(text: str) -> int:
  """Rough token estimate: ~4 chars per token for English text."""
  return len(text) // 4


def check_context_fit(model: str, prompt: str, expected_output_tokens: int = 0) -> dict:
  """
  Check if prompt + expected output fits in model's context window.
  
  Returns: {
    "fits": bool,
    "input_tokens": int (estimated),
    "output_tokens": int,
    "total_tokens": int,
    "max_context": int,
    "remaining": int,
    "warning": str or None
  }
  """
  config = get_model_config(model)
  max_context = config.get("max_context", 128000)
  max_output = config.get("max_output", 16384)
  
  input_tokens = estimate_tokens(prompt)
  output_tokens = min(expected_output_tokens, max_output) if expected_output_tokens > 0 else max_output
  total = input_tokens + output_tokens
  remaining = max_context - total
  
  warning = None
  if remaining < 0:
    warning = f"Exceeds context by {-remaining} tokens"
  elif remaining < max_context * 0.1:
    warning = f"Near context limit ({remaining} tokens remaining)"
  
  return {
    "fits": remaining >= 0,
    "input_tokens": input_tokens,
    "output_tokens": output_tokens,
    "total_tokens": total,
    "max_context": max_context,
    "remaining": remaining,
    "warning": warning
  }


def get_model_pricing(model: str, provider: str = None) -> dict:
  """
  Get pricing for a model from the pricing registry.
  
  Uses exact match first, then prefix matching.
  Returns: {"input_per_1m": float, "output_per_1m": float, "currency": str} or None
  """
  if provider is None:
    config = get_model_config(model)
    provider = config.get("provider", "openai")
  
  provider_pricing = MODEL_PRICING.get(provider, {})
  
  # Exact match first
  if model in provider_pricing:
    return provider_pricing[model]
  
  # Prefix match (find longest matching prefix)
  best_match = None
  best_len = 0
  for price_model in provider_pricing:
    if model.startswith(price_model) and len(price_model) > best_len:
      best_match = price_model
      best_len = len(price_model)
  
  if best_match:
    return provider_pricing[best_match]
  
  return None


def calculate_cost(usage: dict, model: str, provider: str = None) -> dict:
  """
  Calculate cost in USD based on token usage and model pricing.
  
  Args:
    usage: {"input_tokens": int, "output_tokens": int}
    model: Model ID
    provider: Provider name (auto-detected if None)
  
  Returns: {
    "input_cost": float,
    "output_cost": float, 
    "total_cost": float,
    "currency": str,
    "pricing_found": bool
  }
  """
  pricing = get_model_pricing(model, provider)
  
  if pricing is None:
    return {
      "input_cost": 0.0,
      "output_cost": 0.0,
      "total_cost": 0.0,
      "currency": "USD",
      "pricing_found": False
    }
  
  input_tokens = usage.get("input_tokens", 0)
  output_tokens = usage.get("output_tokens", 0)
  
  input_cost = (input_tokens / 1_000_000) * pricing.get("input_per_1m", 0)
  output_cost = (output_tokens / 1_000_000) * pricing.get("output_per_1m", 0)
  
  return {
    "input_cost": round(input_cost, 6),
    "output_cost": round(output_cost, 6),
    "total_cost": round(input_cost + output_cost, 6),
    "currency": pricing.get("currency", "USD"),
    "pricing_found": True
  }


def calculate_output_tokens(num_expected_records: int, tokens_per_record: int = 50, buffer: float = 1.5) -> int:
  """
  Calculate required max_tokens based on expected output size.
  
  Args:
    num_expected_records: Number of records expected in output
    tokens_per_record: Estimated tokens per output record (default 50)
    buffer: Safety multiplier (default 1.5x)
  
  Returns: Recommended max_tokens value
  """
  base = num_expected_records * tokens_per_record
  return int(base * buffer)


def build_api_params(model: str, reasoning_effort: str = 'medium', 
                     output_length: str = 'high', verbosity: str = None, seed: int = None) -> tuple:
  """
  Build API parameters based on model type and effort levels.
  
  Returns: (params, method, provider)
  """
  model_config = get_model_config(model)
  effort_map = EFFORT_MAPPING
  params = {}
  
  method = model_config.get('method', 'temperature')
  provider = model_config.get('provider', 'openai')
  
  if method == 'temperature':
    factor = effort_map[reasoning_effort]['temperature_factor']
    params['temperature'] = factor * model_config.get('temp_max', 2.0)
  elif method == 'reasoning_effort':
    effort_value = effort_map[reasoning_effort]['openai_reasoning_effort']
    supported = model_config.get('effort', [])
    if effort_value not in supported and supported:
      fallback_map = {'none': 'minimal', 'minimal': 'low'}
      if effort_value in fallback_map and fallback_map[effort_value] in supported:
        effort_value = fallback_map[effort_value]
    params['reasoning_effort'] = effort_value
    if verbosity:
      params['verbosity'] = effort_map[verbosity]['openai_verbosity']
  elif method == 'effort':
    params['effort'] = effort_map[reasoning_effort]['openai_reasoning_effort']
  elif method == 'thinking':
    factor = effort_map[reasoning_effort]['anthropic_thinking_factor']
    budget = int(factor * model_config.get('thinking_max', 100000))
    if budget > 0:
      params['thinking'] = {'type': 'enabled', 'budget_tokens': budget}
  
  output_factor = effort_map[output_length]['output_length_factor']
  max_output = model_config.get('max_output', 16384)
  params['max_tokens'] = int(output_factor * max_output)
  
  # Anthropic constraint: max_tokens must be > thinking.budget_tokens
  if 'thinking' in params and params['thinking'].get('budget_tokens', 0) > 0:
    thinking_budget = params['thinking']['budget_tokens']
    if params['max_tokens'] <= thinking_budget:
      params['max_tokens'] = thinking_budget + 1024
  
  if seed is not None:
    if model_config.get('seed', False):
      params['seed'] = seed
  
  return params, method, provider


def retry_with_backoff(fn, retries=3, backoff=(1, 2, 4)):
  """Retry function with exponential backoff."""
  last_error = None
  for attempt in range(retries):
    try:
      return fn()
    except Exception as e:
      last_error = e
      if attempt < retries - 1:
        wait = backoff[attempt] if attempt < len(backoff) else backoff[-1]
        time.sleep(wait)
  raise last_error


def create_client(provider: str, api_key: str = None, timeout: int = 300):
  """
  Create API client for the given provider.
  
  Precedence: api_key parameter > environment variable
  """
  if provider == 'openai':
    from openai import OpenAI
    key = api_key or os.environ.get('OPENAI_API_KEY')
    if not key:
      raise ValueError("OPENAI_API_KEY not found")
    return OpenAI(api_key=key, timeout=timeout)
  elif provider == 'anthropic':
    from anthropic import Anthropic
    key = api_key or os.environ.get('ANTHROPIC_API_KEY')
    if not key:
      raise ValueError("ANTHROPIC_API_KEY not found")
    return Anthropic(api_key=key, timeout=timeout)
  else:
    raise ValueError(f"Unknown provider: {provider}")


def call_llm(client, model: str, prompt: str, api_params: dict, provider: str) -> dict:
  """
  Call LLM API with the given parameters.
  
  Returns: {"text": str, "usage": dict, "model": str, "finish_reason": str}
  """
  if provider == 'openai':
    return _call_openai(client, model, prompt, api_params)
  else:
    return _call_anthropic(client, model, prompt, api_params)


def _call_openai_responses(client, model: str, prompt: str, api_params: dict) -> dict:
  """Call OpenAI Responses API for reasoning models with verbosity support."""
  call_params = {'model': model, 'input': prompt}
  
  if 'reasoning_effort' in api_params:
    call_params['reasoning'] = {'effort': api_params['reasoning_effort']}
  
  if 'verbosity' in api_params:
    call_params['text'] = {'verbosity': api_params['verbosity']}
  
  if 'max_tokens' in api_params:
    call_params['max_output_tokens'] = api_params['max_tokens']
  
  response = client.responses.create(**call_params)
  
  output_text = ""
  for item in response.output:
    if hasattr(item, 'content') and item.content is not None:
      for content in item.content:
        if hasattr(content, 'text'):
          output_text += content.text
  
  return {
    "text": output_text,
    "usage": {
      "input_tokens": response.usage.input_tokens,
      "output_tokens": response.usage.output_tokens
    },
    "model": response.model,
    "finish_reason": "stop"
  }


def _call_openai_chat(client, model: str, prompt: str, api_params: dict) -> dict:
  """Call OpenAI Chat Completions API for temperature models."""
  messages = [{"role": "user", "content": prompt}]
  call_params = {'model': model, 'messages': messages}
  
  if 'temperature' in api_params:
    call_params['temperature'] = api_params['temperature']
  if 'seed' in api_params:
    call_params['seed'] = api_params['seed']
  
  call_params['max_tokens'] = api_params.get('max_tokens', 16384)
  
  response = client.chat.completions.create(**call_params)
  
  text = response.choices[0].message.content or ""
  
  return {
    "text": text,
    "usage": {
      "input_tokens": response.usage.prompt_tokens,
      "output_tokens": response.usage.completion_tokens
    },
    "model": response.model,
    "finish_reason": response.choices[0].finish_reason
  }


def _call_openai(client, model: str, prompt: str, api_params: dict) -> dict:
  """Call OpenAI API - routes to Responses API for reasoning models, Chat for temperature."""
  if 'reasoning_effort' in api_params:
    return _call_openai_responses(client, model, prompt, api_params)
  else:
    return _call_openai_chat(client, model, prompt, api_params)


def _call_anthropic(client, model: str, prompt: str, api_params: dict) -> dict:
  """Call Anthropic API."""
  call_params = {
    'model': model,
    'max_tokens': api_params.get('max_tokens', 8192),
    'messages': [{"role": "user", "content": prompt}]
  }
  
  if 'temperature' in api_params:
    call_params['temperature'] = api_params['temperature']
  
  if 'thinking' in api_params and api_params['thinking'].get('budget_tokens', 0) > 0:
    call_params['thinking'] = api_params['thinking']
  
  # Handle effort parameter for claude-opus-4-5 (requires beta header)
  betas = []
  if 'effort' in api_params:
    betas.append('effort-2025-11-24')
    call_params['effort'] = api_params['effort']
  
  if betas:
    call_params['betas'] = betas
  
  response = client.messages.create(**call_params)
  
  text_content = ""
  for block in response.content:
    if hasattr(block, 'text'):
      text_content = block.text
      break
  
  return {
    "text": text_content,
    "usage": {
      "input_tokens": response.usage.input_tokens,
      "output_tokens": response.usage.output_tokens
    },
    "model": response.model,
    "finish_reason": response.stop_reason
  }


class LLMClient:
  """
  High-level LLM client with automatic model detection and parameter handling.
  
  Thread-safe for use with ThreadPoolExecutor - immutable state after __init__.
  """
  
  def __init__(self, model: str, reasoning_effort: str = 'medium', 
               output_length: str = 'high', verbosity: str = None, api_key: str = None, timeout: int = 300):
    self.model = model
    self.timeout = timeout
    self.model_config = get_model_config(model)
    self.api_params, self.method, self.provider = build_api_params(
      model, reasoning_effort, output_length, verbosity
    )
    self.client = create_client(self.provider, api_key, timeout)
  
  def call(self, prompt: str, max_tokens: int = None) -> dict:
    """
    Call the LLM with the given prompt.
    
    Args:
      prompt: The prompt to send
      max_tokens: Override max_tokens (for dynamic scaling). If None, uses default.
    """
    params = self.api_params.copy()
    if max_tokens is not None:
      model_max = self.model_config.get("max_output", 32768)
      params["max_tokens"] = min(max_tokens, model_max)
    return retry_with_backoff(
      lambda: call_llm(self.client, self.model, prompt, params, self.provider)
    )
  
  def check_context(self, prompt: str, expected_output_tokens: int = 0) -> dict:
    """Check if prompt fits in context window."""
    return check_context_fit(self.model, prompt, expected_output_tokens)
  
  def get_info(self) -> dict:
    """Return client configuration info."""
    return {
      "model": self.model,
      "provider": self.provider,
      "method": self.method,
      "api_params": self.api_params,
      "max_context": self.model_config.get("max_context", 128000),
      "max_output": self.model_config.get("max_output", 16384)
    }
