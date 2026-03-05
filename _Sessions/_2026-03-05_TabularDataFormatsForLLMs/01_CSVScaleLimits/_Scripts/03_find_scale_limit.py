#!/usr/bin/env python3
"""
Find maximum reliable scale for LLM tabular extraction.
V2: Uses llm_client for model-agnostic parameter handling (OpenAI + Anthropic).
Uses binary search to find the highest row count where Precision=1.00 AND Recall=1.00.
"""

import argparse, json, shutil, subprocess, sys, time
from pathlib import Path

from llm_client import get_model_config, calculate_cost


def run_script(script_path: Path, instance_path: Path) -> tuple:
  """Run a script and return (success, stderr)."""
  # Use absolute paths to avoid cwd confusion
  cmd = [sys.executable, str(script_path.resolve()), "--instance-path", str(instance_path.resolve())]
  result = subprocess.run(cmd, capture_output=True, text=True)
  return result.returncode == 0, result.stderr + result.stdout


def run_test_at_scale(test_path: Path, model_output_path: Path, num_rows: int, model: str, iteration: int, reasoning_effort: str = None) -> dict:
  """Run a single test at given row count and return metrics."""
  instance_name = f"iter{iteration:02d}_{num_rows:04d}rows"
  instance_path = model_output_path / instance_name
  
  # Clean up any existing folder for this iteration
  if instance_path.exists():
    shutil.rmtree(instance_path)
  
  # Create instance folder structure
  instance_path.mkdir(parents=True)
  (instance_path / "01_InputData").mkdir()
  (instance_path / "02_Responses").mkdir()
  (instance_path / "03_Evaluations").mkdir()
  
  # Load template config and override rows
  template_path = test_path / "test-config-template.json"
  with open(template_path, "r", encoding="utf-8") as f:
    config = json.load(f)
  
  config["data_generation"]["number_of_rows"] = num_rows
  config["execution"]["model"] = model
  config["execution"]["number_of_runs"] = 1  # Single run sufficient for scale finding
  config["execution"]["number_of_workers"] = 1
  if reasoning_effort:
    config["execution"]["reasoning_effort"] = reasoning_effort
  
  # Write instance config
  with open(instance_path / "test-config.json", "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2)
  
  scripts_path = test_path / "_Scripts"
  
  # Run generate data
  success, output = run_script(scripts_path / "01_generate_data.py", instance_path)
  if not success:
    return {"error": f"Data generation failed: {output[:200]}", "passed": False}
  
  # Run execute and evaluate
  success, output = run_script(scripts_path / "02_execute_and_evaluate.py", instance_path)
  if not success:
    return {"error": f"Execution failed: {output[:200]}", "passed": False}
  
  # Read evaluation result
  eval_file = instance_path / "03_Evaluations" / "eval_01.json"
  if not eval_file.exists():
    return {"error": "Evaluation file not found", "passed": False}
  
  with open(eval_file, "r", encoding="utf-8") as f:
    evaluation = json.load(f)
  
  metrics = evaluation["metrics"]
  precision = metrics["precision"]
  recall = metrics["recall"]
  f1 = metrics["f1"]
  passed = (precision == 1.0 and recall == 1.0)
  
  # Extract token and finish_reason data for hypothesis testing
  input_tokens = evaluation.get("input_tokens", 0)
  output_tokens = evaluation.get("output_tokens", 0)
  finish_reason = evaluation.get("finish_reason", "")
  truncated = evaluation.get("truncated", False)
  
  # Calculate cost
  usage = {"input_tokens": input_tokens, "output_tokens": output_tokens}
  cost_data = calculate_cost(usage, model)
  
  # Determine failure mode
  failure_mode = None
  if not passed:
    failure_mode = "truncation" if truncated else "comprehension"
  
  return {
    "rows": num_rows,
    "precision": precision,
    "recall": recall,
    "f1": f1,
    "passed": passed,
    "true_positives": metrics["true_positives"],
    "false_positives": metrics["false_positives"],
    "false_negatives": metrics["false_negatives"],
    "input_tokens": input_tokens,
    "output_tokens": output_tokens,
    "finish_reason": finish_reason,
    "truncated": truncated,
    "failure_mode": failure_mode,
    "cost_usd": cost_data.get("total_cost", 0)
  }


def find_scale_limit(test_path: Path, initial_rows: int, tolerance: int, model: str,
                     verify_runs: int = 1, skip_baseline: bool = False,
                     reasoning_effort: str = None):
  """Binary search to find maximum reliable scale.
  
  Args:
    verify_runs: Number of runs to verify final boundary (default: 1)
    skip_baseline: Skip baseline validation at small scale
    reasoning_effort: Override reasoning effort level (low/medium/high)
  """
  # Get model config for provider info
  try:
    model_config = get_model_config(model)
    provider = model_config.get("provider", "unknown")
    method = model_config.get("method", "unknown")
  except ValueError as e:
    print(f"ERROR: {e}")
    sys.exit(1)
  
  # Load template config for folder naming
  template_path = test_path / "test-config-template.json"
  with open(template_path, "r", encoding="utf-8") as f:
    template_config = json.load(f)
  
  exec_config = template_config.get("execution", {})
  max_tokens = exec_config.get("max_output_tokens", 16384)
  # Use CLI reasoning_effort if provided, otherwise from config
  reasoning = reasoning_effort if reasoning_effort else exec_config.get("reasoning_effort", "medium")
  
  # Create model output folder with key params
  model_safe_name = model.replace("/", "_").replace(":", "_")
  folder_name = f"{model_safe_name}_{method}_{reasoning}_max{max_tokens}"
  model_output_path = test_path / folder_name
  if model_output_path.exists():
    shutil.rmtree(model_output_path)
  model_output_path.mkdir(parents=True)
  
  print("=" * 36 + " START: SCALE LIMIT FINDER " + "=" * 37)
  print(f"Goal: Find the maximum number of CSV rows where '{model}' achieves 100% accuracy.")
  print(f"Method: Binary search starting at {initial_rows} rows, stopping when bounds are within {tolerance} rows.")
  print(f"Model: '{model}' ({provider} / {method})")
  print(f"Output folder: '{model_output_path}'")
  print()
  
  start_time = time.time()
  search_history = []
  iteration = 0
  consecutive_errors = 0
  
  last_working_lower_bound = None
  last_failed_upper_bound = None
  current_rows = initial_rows
  
  while True:
    iteration += 1
    iter_start = time.time()
    print(f"[ {iteration} ] Testing with {current_rows} rows: Can '{model}' extract all matching records correctly?")
    
    result = run_test_at_scale(test_path, model_output_path, current_rows, model, iteration, reasoning)
    iter_duration = time.time() - iter_start
    result["iteration"] = iteration
    result["duration_secs"] = iter_duration
    search_history.append(result)
    
    if "error" in result:
      print(f"  ERROR: {result['error']} ({iter_duration:.1f} secs)")
      consecutive_errors += 1
      
      # Prevent infinite loop on persistent errors
      if consecutive_errors >= 3:
        print(f"\n  ERROR: {consecutive_errors} consecutive errors. Stopping. Check API keys and model.")
        break
      
      last_failed_upper_bound = current_rows
      if last_working_lower_bound is None:
        current_rows = max(10, current_rows // 2)
      else:
        current_rows = last_working_lower_bound + (last_failed_upper_bound - last_working_lower_bound) // 2
      continue
    
    # Reset consecutive errors on success
    consecutive_errors = 0
    
    precision = result["precision"]
    recall = result["recall"]
    passed = result["passed"]
    tp = result['true_positives']
    fp = result['false_positives']
    fn = result['false_negatives']
    
    if passed:
      print(f"  OK. {tp} correct, {fp} extra, {fn} missing. Precision={precision:.2f} Recall={recall:.2f} ({iter_duration:.1f} secs)")
    else:
      print(f"  FAIL: {tp} correct, {fp} extra, {fn} missing. Precision={precision:.2f} Recall={recall:.2f} ({iter_duration:.1f} secs)")
    
    if passed:
      last_working_lower_bound = current_rows
      if last_failed_upper_bound is None:
        # No upper bound yet, keep going higher
        current_rows = int(current_rows * 1.5)
        print(f"  Scaling up to {current_rows} rows...")
      else:
        # Binary search
        current_rows = last_working_lower_bound + (last_failed_upper_bound - last_working_lower_bound) // 2
        print(f"  Binary search: next test at {current_rows} rows...")
    else:
      last_failed_upper_bound = current_rows
      if last_working_lower_bound is None:
        # No lower bound yet, keep going lower
        current_rows = current_rows // 2
        print(f"  Scaling down to {current_rows} rows...")
      else:
        # Binary search
        current_rows = last_working_lower_bound + (last_failed_upper_bound - last_working_lower_bound) // 2
        print(f"  Binary search: next test at {current_rows} rows...")
    
    # Check stopping condition
    if last_working_lower_bound is not None and last_failed_upper_bound is not None:
      gap = last_failed_upper_bound - last_working_lower_bound
      if gap <= tolerance:
        print(f"\n  Converged: gap={gap} <= tolerance={tolerance}")
        break
    
    # Safety: prevent infinite loops
    if iteration > 20:
      print("\n  WARNING: Maximum iterations reached")
      break
  
  elapsed_time = time.time() - start_time
  
  # Calculate timing statistics
  durations = [r.get("duration_secs", 0) for r in search_history if r.get("duration_secs")]
  timing_stats = {}
  if durations:
    timing_stats = {
      "min_secs": round(min(durations), 1),
      "max_secs": round(max(durations), 1),
      "avg_secs": round(sum(durations) / len(durations), 1)
    }
  
  # Calculate total cost across all iterations
  total_cost = sum(r.get("cost_usd", 0) for r in search_history)
  
  # Verify boundary with multiple runs if requested
  verify_results = []
  if verify_runs > 1 and last_working_lower_bound:
    print()
    print(f"VERIFY: Running {verify_runs} verification runs at {last_working_lower_bound} rows...")
    verify_passes = 0
    for v in range(verify_runs):
      iteration += 1
      print(f"  [ Verify {v+1}/{verify_runs} ] Testing {last_working_lower_bound} rows...")
      result = run_test_at_scale(test_path, model_output_path, last_working_lower_bound, model, iteration, reasoning)
      verify_results.append(result)
      if result.get("passed"):
        verify_passes += 1
        print(f"    PASS")
      else:
        print(f"    FAIL: {result.get('error', 'Unknown')[:50]}")
      total_cost += result.get("cost_usd", 0)
    
    verify_rate = verify_passes / verify_runs
    print(f"  Verification complete: {verify_passes}/{verify_runs} runs passed ({verify_rate*100:.0f}%) for '{model}' at {last_working_lower_bound} rows")
    
    # Adjust max_reliable_rows if verification fails majority
    if verify_rate < 0.5:
      print(f"  WARNING: '{model}' boundary {last_working_lower_bound} rows failed verification ({verify_rate*100:.0f}% pass rate). Results may be unreliable.")
  
  # Calculate context utilization at failure point
  max_context = model_config.get("max_context", 128000)
  failure_entry = next((r for r in search_history if not r.get("passed") and r.get("input_tokens")), None)
  context_utilization_at_failure = None
  if failure_entry and failure_entry.get("input_tokens"):
    context_utilization_at_failure = round(failure_entry["input_tokens"] / max_context * 100, 1)
  
  # Determine primary failure mode
  failure_modes = [r.get("failure_mode") for r in search_history if r.get("failure_mode")]
  primary_failure_mode = max(set(failure_modes), key=failure_modes.count) if failure_modes else None
  
  # Prepare result
  final_result = {
    "model": model,
    "provider": provider,
    "method": method,
    "max_reliable_rows": last_working_lower_bound,
    "last_working_lower_bound": last_working_lower_bound,
    "last_failed_upper_bound": last_failed_upper_bound,
    "primary_failure_mode": primary_failure_mode,
    "context_utilization_at_failure_pct": context_utilization_at_failure,
    "max_context_tokens": max_context,
    "total_cost_usd": round(total_cost, 6),
    "search_history": search_history,
    "total_iterations": iteration,
    "elapsed_time_seconds": round(elapsed_time, 1),
    "timing_stats": timing_stats,
    "verify_runs": verify_runs,
    "verify_results": verify_results if verify_results else None
  }
  
  # Save result in model output folder
  result_file = model_output_path / "scale_limit_result.json"
  with open(result_file, "w", encoding="utf-8") as f:
    json.dump(final_result, f, indent=2)
  
  # Format elapsed time
  if elapsed_time >= 60:
    mins = int(elapsed_time // 60)
    secs = int(elapsed_time % 60)
    elapsed_str = f"{mins} min {secs} secs"
  else:
    elapsed_str = f"{elapsed_time:.1f} secs"
  
  print()
  print(f"RESULT: '{model}' achieves 100% accuracy up to {last_working_lower_bound} rows.")
  print(f"  Scale boundary: {last_working_lower_bound} - {last_failed_upper_bound} rows")
  if primary_failure_mode:
    print(f"  Primary failure mode: {primary_failure_mode}")
  if context_utilization_at_failure:
    print(f"  Context utilization at failure: {context_utilization_at_failure}%")
  print(f"  Total cost: ${total_cost:.6f} USD")
  print(f"  {iteration} iterations completed in {elapsed_str}.")
  if timing_stats:
    print(f"  Duration per iteration: min={timing_stats['min_secs']} secs, max={timing_stats['max_secs']} secs, avg={timing_stats['avg_secs']} secs")
  print(f"  Results saved to '{result_file}'")
  print("=" * 37 + " END: SCALE LIMIT FINDER " + "=" * 38)
  
  return final_result


def main():
  parser = argparse.ArgumentParser(description="Find maximum reliable scale for LLM extraction")
  parser.add_argument("--test-path", type=Path, required=True, help="Path to test folder")
  parser.add_argument("--initial-rows", type=int, default=500, help="Starting row count")
  parser.add_argument("--tolerance", type=int, default=10, help="Stop when bounds within this gap")
  parser.add_argument("--model", type=str, default=None, help="Model to test (default: from config)")
  parser.add_argument("--verify-runs", type=int, default=1, help="Number of runs to verify final boundary (default: 1)")
  parser.add_argument("--skip-baseline", action="store_true", help="Skip baseline validation at small scale")
  parser.add_argument("--reasoning-effort", type=str, default=None, choices=["low", "medium", "high"], help="Reasoning effort level (default: from config)")
  args = parser.parse_args()
  
  test_path = args.test_path.resolve()
  
  if not test_path.exists():
    print(f"ERROR: Test path not found: {test_path}")
    sys.exit(1)
  
  template_path = test_path / "test-config-template.json"
  if not template_path.exists():
    print(f"ERROR: Template config not found: {template_path}")
    sys.exit(1)
  
  # Get model from config if not specified
  model = args.model
  if model is None:
    with open(template_path, "r", encoding="utf-8") as f:
      config = json.load(f)
    model = config["execution"]["model"]
  
  find_scale_limit(
    test_path, args.initial_rows, args.tolerance, model,
    verify_runs=args.verify_runs, skip_baseline=args.skip_baseline,
    reasoning_effort=args.reasoning_effort
  )


if __name__ == "__main__":
  main()
