#!/usr/bin/env python3
"""Quick test of llm_client with multiple model types."""

import sys
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add script dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load .env from common locations
def load_env_file():
    """Load API keys from .env file."""
    env_paths = [
        Path(__file__).parent.parent / ".env",  # V2 folder
        Path(__file__).parent.parent.parent / ".env",  # Session folder
        Path.home() / ".env",
    ]
    for env_path in env_paths:
        if env_path.exists():
            print(f"Loading keys from: {env_path}")
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip().strip('"\'')
            return True
    return False

load_env_file()

from llm_client import LLMClient, get_model_config, build_api_params

# Simple test prompt - minimal tokens
TEST_PROMPT = """Extract employee IDs from this CSV:

"id","name","salary"
"EMP-0001","Alice Smith","$150,000"
"EMP-0002","Bob Jones","$85,000"
"EMP-0003","Carol White","$175,000"

Filter: salary >= $100,000
Output format: List matching IDs, one per line."""

def test_model(model: str, reasoning_effort: str = "low", output_length: str = "low"):
    """Test a single model with specific settings and return result."""
    test_id = f"{model}|effort={reasoning_effort}|output={output_length}"
    try:
        # Get model config to check method
        config = get_model_config(model)
        method = config.get("method", "unknown")
        provider = config.get("provider", "unknown")
        
        # Build params to verify
        params, _, _ = build_api_params(model, reasoning_effort, output_length)
        max_tokens = params.get("max_tokens", 0)
        
        print(f"[{test_id}] Creating client ({provider}/{method}, max_tokens={max_tokens})...")
        client = LLMClient(model, reasoning_effort=reasoning_effort, output_length=output_length, timeout=120)
        
        print(f"[{test_id}] Calling API...")
        response = client.call(TEST_PROMPT)
        
        text = response.get("text", "")[:200]
        finish = response.get("finish_reason", "?")
        usage = response.get("usage", {})
        in_tok = usage.get("input_tokens", 0)
        out_tok = usage.get("output_tokens", 0)
        
        # Check if correct IDs found
        has_0001 = "EMP-0001" in response["text"]
        has_0003 = "EMP-0003" in response["text"]
        has_0002 = "EMP-0002" in response["text"]  # Should NOT have this
        
        correct = has_0001 and has_0003 and not has_0002
        status = "PASS" if correct else "FAIL"
        
        print(f"[{test_id}] {status} | finish={finish} | in={in_tok} out={out_tok}")
        if not correct:
            print(f"  Found: 0001={has_0001}, 0002={has_0002}, 0003={has_0003}")
        
        return {
            "model": model, "status": status, "method": method, "error": None,
            "reasoning_effort": reasoning_effort, "output_length": output_length,
            "max_tokens": max_tokens
        }
        
    except Exception as e:
        print(f"[{test_id}] ERROR: {e}")
        return {
            "model": model, "status": "ERROR", "method": "?", "error": str(e),
            "reasoning_effort": reasoning_effort, "output_length": output_length,
            "max_tokens": 0
        }


def main():
    # Test configurations: (model, reasoning_effort, output_length)
    test_configs = []
    
    # Check which API keys are available
    has_openai = os.environ.get("OPENAI_API_KEY") is not None
    has_anthropic = os.environ.get("ANTHROPIC_API_KEY") is not None
    
    print("=" * 60)
    print("LLM Client Test - Multiple Model Types & Settings")
    print("=" * 60)
    print(f"OpenAI API key: {'YES' if has_openai else 'NO'}")
    print(f"Anthropic API key: {'YES' if has_anthropic else 'NO'}")
    print()
    
    if has_openai:
        # OpenAI temperature method - test output_length variations
        test_configs.append(("gpt-4o-mini", "low", "low"))
        test_configs.append(("gpt-4o-mini", "medium", "high"))
        # OpenAI reasoning_effort method - test effort variations
        test_configs.append(("gpt-5-mini", "low", "low"))
        test_configs.append(("gpt-5-mini", "medium", "medium"))
    
    if has_anthropic:
        # Anthropic haiku 4.5 (newer, available)
        test_configs.append(("claude-haiku-4-5-20251001", "low", "low"))
        test_configs.append(("claude-haiku-4-5-20251001", "medium", "high"))
        # Anthropic thinking method - test thinking budget variations
        test_configs.append(("claude-sonnet-4-20250514", "low", "low"))
        test_configs.append(("claude-sonnet-4-20250514", "high", "high"))
    
    if not test_configs:
        print("ERROR: No API keys found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        sys.exit(1)
    
    print(f"Running {len(test_configs)} test configurations:")
    for model, effort, output in test_configs:
        print(f"  - {model} (effort={effort}, output={output})")
    print()
    
    # Run tests in parallel (max 4 to avoid rate limits)
    results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(test_model, m, e, o): (m, e, o) for m, e, o in test_configs}
        for future in as_completed(futures):
            results.append(future.result())
    
    # Summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    errors = sum(1 for r in results if r["status"] == "ERROR")
    
    for r in results:
        effort = r.get("reasoning_effort", "?")
        output = r.get("output_length", "?")
        max_tok = r.get("max_tokens", 0)
        print(f"  {r['model']}: {r['status']} ({r['method']}) effort={effort} output={output} max_tokens={max_tok}")
        if r["error"]:
            print(f"    Error: {r['error'][:80]}")
    
    print()
    print(f"PASS: {passed}, FAIL: {failed}, ERROR: {errors}")
    
    if errors > 0 or failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
