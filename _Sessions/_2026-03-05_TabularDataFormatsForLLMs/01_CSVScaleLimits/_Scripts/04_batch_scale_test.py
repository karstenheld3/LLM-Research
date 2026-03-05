#!/usr/bin/env python3
"""
Batch scale test runner.
Runs 03_find_scale_limit.py for multiple model/effort configurations.
"""

import argparse, json, subprocess, sys, time
from pathlib import Path


def run_scale_test(test_path: Path, model: str, reasoning_effort: str, initial_rows: int, tolerance: int) -> dict:
  """Run scale test for a single configuration."""
  cmd = [
    sys.executable,
    str(test_path / "_Scripts" / "03_find_scale_limit.py"),
    "--test-path", str(test_path),
    "--model", model,
    "--initial-rows", str(initial_rows),
    "--tolerance", str(tolerance)
  ]
  
  start_time = time.time()
  result = subprocess.run(cmd, capture_output=True, text=True)
  duration = time.time() - start_time
  
  if result.returncode != 0:
    return {
      "model": model,
      "reasoning_effort": reasoning_effort,
      "status": "error",
      "error": result.stderr[:500] if result.stderr else "Unknown error",
      "duration_secs": round(duration, 1)
    }
  
  # Find and load result file
  model_safe = model.replace("/", "_").replace(":", "_")
  result_folders = list(test_path.glob(f"{model_safe}_*"))
  
  if not result_folders:
    return {
      "model": model,
      "reasoning_effort": reasoning_effort,
      "status": "error",
      "error": "Result folder not found",
      "duration_secs": round(duration, 1)
    }
  
  # Get most recent folder
  result_folder = sorted(result_folders, key=lambda x: x.stat().st_mtime)[-1]
  result_file = result_folder / "scale_limit_result.json"
  
  if not result_file.exists():
    return {
      "model": model,
      "reasoning_effort": reasoning_effort,
      "status": "error",
      "error": "scale_limit_result.json not found",
      "duration_secs": round(duration, 1)
    }
  
  with open(result_file, "r", encoding="utf-8") as f:
    scale_result = json.load(f)
  
  return {
    "model": model,
    "reasoning_effort": reasoning_effort,
    "status": "success",
    "scale_limit": scale_result.get("max_reliable_rows"),
    "failure_mode": scale_result.get("primary_failure_mode"),
    "context_utilization_pct": scale_result.get("context_utilization_at_failure_pct"),
    "cost_usd": scale_result.get("total_cost_usd"),
    "iterations": scale_result.get("total_iterations"),
    "duration_secs": round(duration, 1),
    "result_folder": str(result_folder.name)
  }


def run_batch(test_path: Path, config: dict, dry_run: bool = False):
  """Run batch of scale tests."""
  test_matrix = config.get("test_matrix", [])
  initial_rows = config.get("initial_rows", 100)
  tolerance = config.get("tolerance", 10)
  
  print("=" * 35 + " START: BATCH SCALE TEST " + "=" * 35)
  print(f"Test path: {test_path}")
  print(f"Configurations: {len(test_matrix)}")
  print(f"Initial rows: {initial_rows}, Tolerance: {tolerance}")
  print()
  
  if dry_run:
    print("DRY RUN - Would test:")
    for i, cfg in enumerate(test_matrix, 1):
      print(f"  {i}. {cfg['model']} (effort={cfg.get('reasoning_effort', 'medium')})")
    return
  
  results = []
  total_start = time.time()
  
  for i, cfg in enumerate(test_matrix, 1):
    model = cfg["model"]
    effort = cfg.get("reasoning_effort", "medium")
    
    print(f"[ {i} / {len(test_matrix)} ] Testing: {model} (effort={effort})")
    
    # Update config template with effort before running
    template_path = test_path / "test-config-template.json"
    with open(template_path, "r", encoding="utf-8") as f:
      template = json.load(f)
    
    template["execution"]["reasoning_effort"] = effort
    
    with open(template_path, "w", encoding="utf-8") as f:
      json.dump(template, f, indent=2)
    
    result = run_scale_test(test_path, model, effort, initial_rows, tolerance)
    results.append(result)
    
    if result["status"] == "success":
      print(f"  Scale limit: {result['scale_limit']} rows, Mode: {result['failure_mode']}, Cost: ${result['cost_usd']:.4f}")
    else:
      print(f"  ERROR: {result.get('error', 'Unknown')}")
    print()
  
  total_duration = time.time() - total_start
  total_cost = sum(r.get("cost_usd", 0) or 0 for r in results if r["status"] == "success")
  
  # Generate batch summary
  batch_summary = {
    "test_date": time.strftime("%Y-%m-%d %H:%M"),
    "configurations_tested": len(test_matrix),
    "successful": sum(1 for r in results if r["status"] == "success"),
    "failed": sum(1 for r in results if r["status"] == "error"),
    "results": results,
    "total_cost_usd": round(total_cost, 6),
    "elapsed_time_seconds": round(total_duration, 1)
  }
  
  # Save summary
  summary_file = test_path / "batch_summary.json"
  with open(summary_file, "w", encoding="utf-8") as f:
    json.dump(batch_summary, f, indent=2)
  
  # Print summary
  print("=" * 35 + " BATCH SUMMARY " + "=" * 40)
  print(f"Tested: {batch_summary['configurations_tested']}, Success: {batch_summary['successful']}, Failed: {batch_summary['failed']}")
  print(f"Total cost: ${total_cost:.4f} USD")
  print(f"Total time: {total_duration:.1f} secs")
  print()
  
  print("Results:")
  for r in results:
    if r["status"] == "success":
      print(f"  {r['model']} (effort={r['reasoning_effort']}): {r['scale_limit']} rows, {r['failure_mode']}")
    else:
      print(f"  {r['model']} (effort={r['reasoning_effort']}): ERROR - {r.get('error', 'Unknown')[:50]}")
  
  print()
  print(f"Summary saved to: {summary_file}")
  print("=" * 36 + " END: BATCH SCALE TEST " + "=" * 36)
  
  return batch_summary


def main():
  parser = argparse.ArgumentParser(description="Batch scale test runner")
  parser.add_argument("--test-path", type=Path, required=True, help="Path to test folder")
  parser.add_argument("--config", type=str, default="batch-config.json", help="Batch config file")
  parser.add_argument("--dry-run", action="store_true", help="Show what would be tested")
  args = parser.parse_args()
  
  test_path = args.test_path.resolve()
  
  if not test_path.exists():
    print(f"ERROR: Test path not found: {test_path}")
    sys.exit(1)
  
  config_path = test_path / args.config
  if not config_path.exists():
    print(f"ERROR: Config file not found: {config_path}")
    sys.exit(1)
  
  with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)
  
  run_batch(test_path, config, args.dry_run)


if __name__ == "__main__":
  main()
