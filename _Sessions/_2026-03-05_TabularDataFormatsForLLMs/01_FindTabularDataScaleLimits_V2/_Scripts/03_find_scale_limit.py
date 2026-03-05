#!/usr/bin/env python3
"""
Find maximum reliable scale for LLM tabular extraction.
V2: Uses llm_client for model-agnostic parameter handling (OpenAI + Anthropic).
Uses binary search to find the highest row count where Precision=1.00 AND Recall=1.00.
"""

import argparse, json, shutil, subprocess, sys, time
from pathlib import Path

from llm_client import get_model_config


def run_script(script_path: Path, instance_path: Path) -> bool:
  """Run a script and return success status."""
  cmd = [sys.executable, str(script_path), "--instance-path", str(instance_path)]
  result = subprocess.run(cmd, capture_output=True, text=True)
  return result.returncode == 0


def run_test_at_scale(test_path: Path, model_output_path: Path, num_rows: int, model: str, iteration: int) -> dict:
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
  
  # Write instance config
  with open(instance_path / "test-config.json", "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2)
  
  scripts_path = test_path / "_Scripts"
  
  # Run generate data
  if not run_script(scripts_path / "01_generate_data.py", instance_path):
    return {"error": "Data generation failed", "passed": False}
  
  # Run execute and evaluate
  cmd = [sys.executable, str(scripts_path / "02_execute_and_evaluate.py"), "--instance-path", str(instance_path)]
  result = subprocess.run(cmd, capture_output=True, text=True)
  
  if result.returncode != 0:
    return {"error": f"Execution failed: {result.stderr}", "passed": False}
  
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
  
  # Keep folder for inspection (no cleanup)
  
  return {
    "rows": num_rows,
    "precision": precision,
    "recall": recall,
    "f1": f1,
    "passed": passed,
    "true_positives": metrics["true_positives"],
    "false_positives": metrics["false_positives"],
    "false_negatives": metrics["false_negatives"]
  }


def find_scale_limit(test_path: Path, initial_rows: int, tolerance: int, model: str):
  """Binary search to find maximum reliable scale."""
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
  reasoning = exec_config.get("reasoning_effort", "medium")
  
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
  
  last_working_lower_bound = None
  last_failed_upper_bound = None
  current_rows = initial_rows
  
  while True:
    iteration += 1
    iter_start = time.time()
    print(f"[ {iteration} ] Testing with {current_rows} rows: Can '{model}' extract all matching records correctly?")
    
    result = run_test_at_scale(test_path, model_output_path, current_rows, model, iteration)
    iter_duration = time.time() - iter_start
    result["iteration"] = iteration
    result["duration_secs"] = iter_duration
    search_history.append(result)
    
    if "error" in result:
      print(f"  ERROR: {result['error']} ({iter_duration:.1f} secs)")
      last_failed_upper_bound = current_rows
      if last_working_lower_bound is None:
        current_rows = current_rows // 2
      else:
        current_rows = last_working_lower_bound + (last_failed_upper_bound - last_working_lower_bound) // 2
      continue
    
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
    
    if current_rows < 10:
      print("\n  WARNING: Row count too low, stopping")
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
  
  # Prepare result
  final_result = {
    "model": model,
    "max_reliable_rows": last_working_lower_bound,
    "last_working_lower_bound": last_working_lower_bound,
    "last_failed_upper_bound": last_failed_upper_bound,
    "search_history": search_history,
    "total_iterations": iteration,
    "elapsed_time_seconds": round(elapsed_time, 1),
    "timing_stats": timing_stats
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
  print(f"  The model starts making errors somewhere between {last_working_lower_bound} and {last_failed_upper_bound} rows.")
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
  
  find_scale_limit(test_path, args.initial_rows, args.tolerance, model)


if __name__ == "__main__":
  main()
