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

def test_model(model: str):
    """Test a single model and return result."""
    try:
        # Get model config to check method
        config = get_model_config(model)
        method = config.get("method", "unknown")
        provider = config.get("provider", "unknown")
        
        # Build params to verify
        params, _, _ = build_api_params(model, "medium", "medium")
        
        print(f"[{model}] Creating client ({provider}/{method})...")
        client = LLMClient(model, reasoning_effort="low", output_length="low", timeout=60)
        
        print(f"[{model}] Calling API...")
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
        
        print(f"[{model}] {status} | finish={finish} | in={in_tok} out={out_tok}")
        if not correct:
            print(f"  Found: 0001={has_0001}, 0002={has_0002}, 0003={has_0003}")
        
        return {"model": model, "status": status, "method": method, "error": None}
        
    except Exception as e:
        print(f"[{model}] ERROR: {e}")
        return {"model": model, "status": "ERROR", "method": "?", "error": str(e)}


def main():
    # Models to test - one of each method type
    models_to_test = []
    
    # Check which API keys are available
    has_openai = os.environ.get("OPENAI_API_KEY") is not None
    has_anthropic = os.environ.get("ANTHROPIC_API_KEY") is not None
    
    print("=" * 60)
    print("LLM Client Test - Multiple Model Types")
    print("=" * 60)
    print(f"OpenAI API key: {'YES' if has_openai else 'NO'}")
    print(f"Anthropic API key: {'YES' if has_anthropic else 'NO'}")
    print()
    
    if has_openai:
        models_to_test.extend([
            "gpt-4o-mini",       # temperature method (cheap, fast)
            "gpt-5-mini",        # reasoning_effort method
        ])
    
    if has_anthropic:
        models_to_test.extend([
            "claude-3-5-haiku-20241022",  # temperature method (cheap)
        ])
    
    if not models_to_test:
        print("ERROR: No API keys found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        sys.exit(1)
    
    print(f"Testing {len(models_to_test)} models: {models_to_test}")
    print()
    
    # Run tests in parallel
    results = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(test_model, m): m for m in models_to_test}
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
        print(f"  {r['model']}: {r['status']} ({r['method']})")
        if r["error"]:
            print(f"    Error: {r['error'][:80]}")
    
    print()
    print(f"PASS: {passed}, FAIL: {failed}, ERROR: {errors}")
    
    if errors > 0 or failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
