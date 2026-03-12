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

def test_model(index: int, total: int, model: str, reasoning_effort: str = "low", output_length: str = "low", verbosity: str = None):
    """Test a single model with specific settings and return result."""
    verb_str = f" verbosity='{verbosity}'" if verbosity else ""
    prefix = f"[ {index:2} / {total:2} ]"
    try:
        # Get model config to check method
        config = get_model_config(model)
        method = config.get("method", "unknown")
        provider = config.get("provider", "unknown")
        
        # Build params to verify
        params, _, _ = build_api_params(model, reasoning_effort, output_length, verbosity)
        max_tokens = params.get("max_tokens", 0)
        has_verbosity = 'verbosity' in params
        
        verb_info = f" verbosity='{params.get('verbosity')}'" if has_verbosity else ""
        print(f"{prefix} Testing model='{model}' effort='{reasoning_effort}' output='{output_length}'{verb_str}...")
        print(f"{prefix}   Creating client ({provider}/{method}, max_tokens={max_tokens}{verb_info})...")
        client = LLMClient(model, reasoning_effort=reasoning_effort, output_length=output_length, verbosity=verbosity, timeout=120)
        
        print(f"{prefix}   Calling API...")
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
        status = "OK" if correct else "FAIL"
        
        if correct:
            print(f"{prefix}   OK. {in_tok} tokens in, {out_tok} out. finish='{finish}'")
        else:
            print(f"{prefix}   FAIL: Incorrect extraction. Found: 0001={has_0001}, 0002={has_0002}, 0003={has_0003}")
        
        return {
            "model": model, "status": status, "method": method, "error": None,
            "reasoning_effort": reasoning_effort, "output_length": output_length,
            "verbosity": verbosity, "max_tokens": max_tokens, "index": index
        }
        
    except Exception as e:
        print(f"{prefix}   ERROR: {e}")
        return {
            "model": model, "status": "ERROR", "method": "?", "error": str(e),
            "reasoning_effort": reasoning_effort, "output_length": output_length,
            "verbosity": verbosity, "max_tokens": 0, "index": index
        }


def main():
    # Test configurations: (model, reasoning_effort, output_length)
    test_configs = []
    
    # Check which API keys are available
    has_openai = os.environ.get("OPENAI_API_KEY") is not None
    has_anthropic = os.environ.get("ANTHROPIC_API_KEY") is not None
    
    # LOG-SC-02: 100-char START header
    header = "START: LLM CLIENT TEST"
    pad = (100 - len(header) - 2) // 2
    print(f"{'=' * pad} {header} {'=' * pad}")
    print(f"Testing LLM client with multiple model types and parameter combinations.")
    print()
    print(f"OpenAI API key: {'YES' if has_openai else 'NO'}")
    print(f"Anthropic API key: {'YES' if has_anthropic else 'NO'}")
    print()
    
    if has_openai:
        # OpenAI temperature method - test output_length variations
        test_configs.append(("gpt-4o-mini", "low", "low", None))
        test_configs.append(("gpt-4o-mini", "medium", "high", None))
        # OpenAI reasoning_effort method - test effort variations
        test_configs.append(("gpt-5-mini", "low", "low", None))
        test_configs.append(("gpt-5-mini", "medium", "medium", None))
        # gpt-5.4 - new model with verbosity support
        test_configs.append(("gpt-5.4", "none", "low", None))
        test_configs.append(("gpt-5.4", "low", "low", None))
        test_configs.append(("gpt-5.4", "none", "low", "low"))    # verbosity test
        test_configs.append(("gpt-5.4", "none", "low", "medium")) # verbosity test
    
    if has_anthropic:
        # Anthropic haiku 4.5 (newer, available)
        test_configs.append(("claude-haiku-4-5-20251001", "low", "low", None))
        test_configs.append(("claude-haiku-4-5-20251001", "medium", "high", None))
        # Anthropic thinking method - test thinking budget variations
        test_configs.append(("claude-sonnet-4-20250514", "low", "low", None))
        test_configs.append(("claude-sonnet-4-20250514", "high", "high", None))
    
    if not test_configs:
        print("ERROR: No API keys found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        sys.exit(1)
    
    total = len(test_configs)
    print(f"Running {total} test configurations...")
    print()
    
    # Run tests in parallel (max 4 to avoid rate limits)
    results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(test_model, i, total, m, e, o, v): (i, m, e, o, v) for i, (m, e, o, v) in enumerate(test_configs, 1)}
        for future in as_completed(futures):
            results.append(future.result())
    
    # LOG-SC-07: Summary with counts
    print()
    print("===== TEST COMPLETE =====")
    ok_count = sum(1 for r in results if r["status"] == "OK")
    fail_count = sum(1 for r in results if r["status"] == "FAIL")
    error_count = sum(1 for r in results if r["status"] == "ERROR")
    
    # Sort by index for consistent output
    results.sort(key=lambda r: r.get("index", 0))
    
    for r in results:
        effort = r.get("reasoning_effort", "?")
        output = r.get("output_length", "?")
        verbosity = r.get("verbosity")
        max_tok = r.get("max_tokens", 0)
        verb_str = f" verbosity='{verbosity}'" if verbosity else ""
        status = r["status"]
        if status == "OK":
            print(f"  OK. model='{r['model']}' method='{r['method']}' effort='{effort}' output='{output}'{verb_str}")
        else:
            print(f"  {status}: model='{r['model']}' method='{r['method']}' effort='{effort}' output='{output}'{verb_str}")
            if r["error"]:
                print(f"    -> {r['error'][:80]}")
    
    print()
    print(f"OK: {ok_count}, FAIL: {fail_count}, ERROR: {error_count}")
    
    # LOG-SC-07: Final RESULT line
    if fail_count == 0 and error_count == 0:
        print("RESULT: PASSED")
    else:
        print("RESULT: FAILED")
    
    # LOG-SC-02: 100-char END footer
    footer = "END: LLM CLIENT TEST"
    pad = (100 - len(footer) - 2) // 2
    print(f"{'=' * pad} {footer} {'=' * pad}")
    
    if error_count > 0 or fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
