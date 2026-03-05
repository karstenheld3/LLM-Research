#!/usr/bin/env python3
"""
llm_client.py - Unified LLM client with model-aware parameter handling.

Copied from .windsurf/skills/llm-evaluation/call-llm.py with adaptations for
tabular data extraction testing.

Supports:
- OpenAI: gpt-4o, gpt-4.1, gpt-5, o1, o3 (temperature or reasoning_effort)
- Anthropic: claude-3.5, claude-3.7, claude-4, claude-4.5 (temperature or thinking)
"""

import os, sys, json, time
from pathlib import Path


EFFORT_LEVELS = ['none', 'minimal', 'low', 'medium', 'high', 'xhigh']

MODEL_REGISTRY = {
  "model_id_startswith": [
    {"prefix": "gpt-3.5", "provider": "openai", "method": "temperature", "max_output": 4096, "temp_max": 2.0, "seed": True},
    {"prefix": "gpt-4o", "provider": "openai", "method": "temperature", "max_output": 16384, "temp_max": 2.0, "seed": True},
    {"prefix": "gpt-4.1", "provider": "openai", "method": "temperature", "max_output": 32768, "temp_max": 2.0, "seed": True},
    {"prefix": "gpt-4", "provider": "openai", "method": "temperature", "max_output": 8192, "temp_max": 2.0, "seed": True},
    {"prefix": "o1", "provider": "openai", "method": "reasoning_effort", "max_output": 32768, "seed": False},
    {"prefix": "o3", "provider": "openai", "method": "reasoning_effort", "max_output": 32768, "seed": False},
    {"prefix": "o4", "provider": "openai", "method": "reasoning_effort", "max_output": 32768, "seed": False},
    {"prefix": "gpt-5-pro", "provider": "openai", "method": "reasoning_effort", "max_output": 32768, "seed": False},
    {"prefix": "gpt-5.1", "provider": "openai", "method": "reasoning_effort", "max_output": 32768, "seed": False},
    {"prefix": "gpt-5.2", "provider": "openai", "method": "reasoning_effort", "max_output": 32768, "seed": False},
    {"prefix": "gpt-5", "provider": "openai", "method": "reasoning_effort", "max_output": 32768, "seed": False},
    {"prefix": "claude-opus-4.5", "provider": "anthropic", "method": "effort", "max_output": 8192},
    {"prefix": "claude-opus-4", "provider": "anthropic", "method": "thinking", "max_output": 8192, "thinking_max": 100000},
    {"prefix": "claude-sonnet-4.5", "provider": "anthropic", "method": "thinking", "max_output": 16384, "thinking_max": 100000},
    {"prefix": "claude-sonnet-4", "provider": "anthropic", "method": "thinking", "max_output": 8192, "thinking_max": 100000},
    {"prefix": "claude-3.7", "provider": "anthropic", "method": "thinking", "max_output": 8192, "thinking_max": 100000},
    {"prefix": "claude-3.5", "provider": "anthropic", "method": "temperature", "max_output": 8192, "temp_max": 1.0},
    {"prefix": "claude-3", "provider": "anthropic", "method": "temperature", "max_output": 4096, "temp_max": 1.0},
    {"prefix": "claude-", "provider": "anthropic", "method": "temperature", "max_output": 4096, "temp_max": 1.0},
  ]
}

EFFORT_MAPPING = {
  "none": {"temperature_factor": 0.0, "openai_reasoning_effort": "none", "anthropic_thinking_factor": 0.0, "output_length_factor": 0.25},
  "minimal": {"temperature_factor": 0.1, "openai_reasoning_effort": "minimal", "anthropic_thinking_factor": 0.01, "output_length_factor": 0.5},
  "low": {"temperature_factor": 0.2, "openai_reasoning_effort": "low", "anthropic_thinking_factor": 0.04, "output_length_factor": 0.5},
  "medium": {"temperature_factor": 0.35, "openai_reasoning_effort": "medium", "anthropic_thinking_factor": 0.1, "output_length_factor": 0.75},
  "high": {"temperature_factor": 0.5, "openai_reasoning_effort": "high", "anthropic_thinking_factor": 0.32, "output_length_factor": 1.0},
  "xhigh": {"temperature_factor": 0.5, "openai_reasoning_effort": "xhigh", "anthropic_thinking_factor": 1.0, "output_length_factor": 1.0},
}


def get_model_config(model: str) -> dict:
  """Return model config from registry using prefix matching."""
  for entry in MODEL_REGISTRY['model_id_startswith']:
    if model.startswith(entry['prefix']):
      return entry
  known = [e['prefix'] for e in MODEL_REGISTRY['model_id_startswith']]
  raise ValueError(f"Unknown model: {model}. Known prefixes: {known}")


def build_api_params(model: str, reasoning_effort: str = 'medium', 
                     output_length: str = 'high', seed: int = None) -> tuple:
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
    params['reasoning_effort'] = effort_map[reasoning_effort]['openai_reasoning_effort']
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


def _call_openai(client, model: str, prompt: str, api_params: dict) -> dict:
  """Call OpenAI API."""
  messages = [{"role": "user", "content": prompt}]
  call_params = {'model': model, 'messages': messages}
  
  if 'temperature' in api_params:
    call_params['temperature'] = api_params['temperature']
  if 'reasoning_effort' in api_params:
    call_params['reasoning_effort'] = api_params['reasoning_effort']
  if 'seed' in api_params:
    call_params['seed'] = api_params['seed']
  
  # Use max_completion_tokens for newer models
  token_param = 'max_completion_tokens' if any(x in model for x in ['gpt-5', 'o1-', 'o3-', 'o4-']) else 'max_tokens'
  call_params[token_param] = api_params.get('max_tokens', 16384)
  
  response = client.chat.completions.create(**call_params)
  
  return {
    "text": response.choices[0].message.content,
    "usage": {
      "input_tokens": response.usage.prompt_tokens,
      "output_tokens": response.usage.completion_tokens
    },
    "model": response.model,
    "finish_reason": response.choices[0].finish_reason
  }


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
               output_length: str = 'high', api_key: str = None, timeout: int = 300):
    self.model = model
    self.timeout = timeout
    self.api_params, self.method, self.provider = build_api_params(
      model, reasoning_effort, output_length
    )
    self.client = create_client(self.provider, api_key, timeout)
  
  def call(self, prompt: str) -> dict:
    """Call the LLM with the given prompt."""
    return retry_with_backoff(
      lambda: call_llm(self.client, self.model, prompt, self.api_params, self.provider)
    )
  
  def get_info(self) -> dict:
    """Return client configuration info."""
    return {
      "model": self.model,
      "provider": self.provider,
      "method": self.method,
      "api_params": self.api_params
    }
