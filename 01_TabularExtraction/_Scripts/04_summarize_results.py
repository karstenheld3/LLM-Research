#!/usr/bin/env python3
"""
Summarize evaluation results across all runs.
Calculates aggregate metrics and outputs summary report.
"""

import argparse, json, statistics, sys
from pathlib import Path


def load_config(instance_path: Path) -> dict:
  """Load config with template inheritance."""
  config_path = instance_path / "test-config.json"
  template_path = instance_path.parent / "test-config-template.json"
    
  config = {}
  if template_path.exists():
    with open(template_path, "r", encoding="utf-8") as f:
      config = json.load(f)
    
  with open(config_path, "r", encoding="utf-8") as f:
    instance_config = json.load(f)
    
  def deep_merge(base, override):
    result = base.copy()
    for key, value in override.items():
      if key in result and isinstance(result[key], dict) and isinstance(value, dict):
        result[key] = deep_merge(result[key], value)
      else:
        result[key] = value
    return result
    
  return deep_merge(config, instance_config)


def calculate_stats(values: list) -> dict:
  """Calculate mean, std, min, max for a list of values."""
  if not values:
    return {"mean": 0, "std": 0, "min": 0, "max": 0}
    
  return {
    "mean": round(statistics.mean(values), 4),
    "std": round(statistics.stdev(values), 4) if len(values) > 1 else 0,
    "min": round(min(values), 4),
    "max": round(max(values), 4)
  }


def main():
  parser = argparse.ArgumentParser(description="Summarize evaluation results")
  parser.add_argument("--instance-path", required=True, help="Path to test instance folder")
  args = parser.parse_args()
    
  instance_path = Path(args.instance_path)
    
  # Load config
  config = load_config(instance_path)
    
  # Find evaluation files
  eval_dir = instance_path / "03_Evaluations"
  if not eval_dir.exists():
    print(f"ERROR: Evaluations directory not found: {eval_dir}")
    sys.exit(1)
    
  eval_files = sorted(eval_dir.glob("eval_*.json"))
  if not eval_files:
    print("ERROR: No evaluation files found")
    sys.exit(1)
    
  print(f"Found {len(eval_files)} evaluation files")
    
  # Load all evaluations
  evaluations = []
  for eval_file in eval_files:
    with open(eval_file, "r", encoding="utf-8") as f:
      evaluations.append(json.load(f))
    
  # Extract metrics
  precisions = [e["metrics"]["precision"] for e in evaluations]
  recalls = [e["metrics"]["recall"] for e in evaluations]
  f1s = [e["metrics"]["f1"] for e in evaluations]
    
  # Count perfect extractions (100% precision AND recall)
  perfect_count = sum(1 for e in evaluations 
             if e["metrics"]["precision"] == 1.0 and e["metrics"]["recall"] == 1.0)
    
  # Count passed (F1 >= 0.9)
  passed_count = sum(1 for e in evaluations if e["metrics"]["f1"] >= 0.9)
    
  # Calculate totals
  total_tp = sum(e["metrics"]["true_positives"] for e in evaluations)
  total_fp = sum(e["metrics"]["false_positives"] for e in evaluations)
  total_fn = sum(e["metrics"]["false_negatives"] for e in evaluations)
    
  # Build summary
  summary = {
    "test_instance": instance_path.name,
    "config": {
      "model": config["execution"]["model"],
      "number_of_rows": config["data_generation"]["number_of_rows"],
      "number_of_columns": config["data_generation"]["number_of_columns"],
      "number_of_runs": config["execution"]["number_of_runs"]
    },
    "aggregate_metrics": {
      "runs_total": len(evaluations),
      "runs_passed": passed_count,
      "runs_failed": len(evaluations) - passed_count,
      "precision": calculate_stats(precisions),
      "recall": calculate_stats(recalls),
      "f1": calculate_stats(f1s),
      "perfect_extraction_rate": round(perfect_count / len(evaluations), 4) if evaluations else 0
    },
    "confusion_matrix_totals": {
      "true_positives": total_tp,
      "false_positives": total_fp,
      "false_negatives": total_fn
    },
    "run_results": [
      {
        "run_id": e["run_id"],
        "precision": e["metrics"]["precision"],
        "recall": e["metrics"]["recall"],
        "f1": e["metrics"]["f1"],
        "tp": e["metrics"]["true_positives"],
        "fp": e["metrics"]["false_positives"],
        "fn": e["metrics"]["false_negatives"]
      }
      for e in evaluations
    ]
  }
    
  # Create output directory
  summary_dir = instance_path / "04_Summaries"
  summary_dir.mkdir(parents=True, exist_ok=True)
    
  # Write summary
  summary_path = summary_dir / "summary.json"
  with open(summary_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)
    
  print(f"\nWrote summary: {summary_path}")
    
  # Print report
  print("\n" + "=" * 60)
  print(f"SUMMARY: {instance_path.name}")
  print("=" * 60)
  print(f"Model: {config['execution']['model']}")
  print(f"Rows: {config['data_generation']['number_of_rows']}")
  print(f"Columns: {config['data_generation']['number_of_columns']}")
  print(f"Runs: {len(evaluations)}")
  print("-" * 60)
  print(f"Precision: {summary['aggregate_metrics']['precision']['mean']:.2f} "
      f"(std={summary['aggregate_metrics']['precision']['std']:.2f}, "
      f"min={summary['aggregate_metrics']['precision']['min']:.2f}, "
      f"max={summary['aggregate_metrics']['precision']['max']:.2f})")
  print(f"Recall:    {summary['aggregate_metrics']['recall']['mean']:.2f} "
      f"(std={summary['aggregate_metrics']['recall']['std']:.2f}, "
      f"min={summary['aggregate_metrics']['recall']['min']:.2f}, "
      f"max={summary['aggregate_metrics']['recall']['max']:.2f})")
  print(f"F1:        {summary['aggregate_metrics']['f1']['mean']:.2f} "
      f"(std={summary['aggregate_metrics']['f1']['std']:.2f}, "
      f"min={summary['aggregate_metrics']['f1']['min']:.2f}, "
      f"max={summary['aggregate_metrics']['f1']['max']:.2f})")
  print("-" * 60)
  print(f"Perfect extractions: {perfect_count}/{len(evaluations)} "
      f"({summary['aggregate_metrics']['perfect_extraction_rate']*100:.0f}%)")
  print(f"Passed (F1>=0.9): {passed_count}/{len(evaluations)}")
  print(f"Confusion totals: TP={total_tp}, FP={total_fp}, FN={total_fn}")
  print("=" * 60)
  print("OK.")


if __name__ == "__main__":
  main()
