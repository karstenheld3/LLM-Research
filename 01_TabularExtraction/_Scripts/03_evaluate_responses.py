#!/usr/bin/env python3
"""
Evaluate LLM responses against ground truth using deterministic ID matching.
No LLM judge - uses regex to extract employee IDs and compare against expected.
"""

import argparse, json, re, sys
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


def extract_employee_ids(response_text: str) -> set:
  """Extract all employee IDs from response using regex."""
  # Match EMP-XXXX pattern (4 digits)
  matches = re.findall(r'EMP-(\d{4})', response_text)
  # Return unique IDs with full format
  return set(f"EMP-{m}" for m in matches)


def evaluate_response(response_text: str, expected_ids: set) -> dict:
  """Evaluate a single response against ground truth."""
  extracted_ids = extract_employee_ids(response_text)
    
  tp = len(extracted_ids & expected_ids)
  fp = len(extracted_ids - expected_ids)
  fn = len(expected_ids - extracted_ids)
    
  precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
  recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
  f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
  return {
    "extracted_ids": sorted(list(extracted_ids)),
    "metrics": {
      "true_positives": tp,
      "false_positives": fp,
      "false_negatives": fn,
      "precision": round(precision, 4),
      "recall": round(recall, 4),
      "f1": round(f1, 4)
    },
    "missing_ids": sorted(list(expected_ids - extracted_ids)),
    "extra_ids": sorted(list(extracted_ids - expected_ids))
  }


def main():
  parser = argparse.ArgumentParser(description="Evaluate LLM responses")
  parser.add_argument("--instance-path", required=True, help="Path to test instance folder")
  args = parser.parse_args()
    
  instance_path = Path(args.instance_path)
    
  # Load ground truth
  gt_path = instance_path / "01_InputData" / "ground_truth.json"
  if not gt_path.exists():
    print(f"ERROR: Ground truth not found: {gt_path}")
    sys.exit(1)
    
  with open(gt_path, "r", encoding="utf-8") as f:
    ground_truth = json.load(f)
    
  expected_ids = set(ground_truth["expected_ids"])
  print(f"Expected {len(expected_ids)} records")
    
  # Find response files
  responses_dir = instance_path / "02_Responses"
  if not responses_dir.exists():
    print(f"ERROR: Responses directory not found: {responses_dir}")
    sys.exit(1)
    
  response_files = sorted(responses_dir.glob("run_*.md"))
  if not response_files:
    print("ERROR: No response files found")
    sys.exit(1)
    
  print(f"Found {len(response_files)} response files")
    
  # Create output directory
  eval_dir = instance_path / "03_Evaluations"
  eval_dir.mkdir(parents=True, exist_ok=True)
    
  # Evaluate each response
  results = []
  for resp_file in response_files:
    run_id = int(resp_file.stem.split("_")[1])
    eval_file = eval_dir / f"eval_{run_id:02d}.json"
        
    # Skip if already evaluated
    if eval_file.exists():
      print(f"  Run {run_id}: SKIP (exists)")
      with open(eval_file, "r", encoding="utf-8") as f:
        results.append(json.load(f))
      continue
        
    # Read and evaluate response
    response_text = resp_file.read_text(encoding="utf-8")
    evaluation = evaluate_response(response_text, expected_ids)
        
    # Add metadata
    evaluation["run_id"] = run_id
    evaluation["response_file"] = resp_file.name
    evaluation["token_count"] = len(response_text) // 4  # Rough estimate
    evaluation["errors"] = []
        
    # Write evaluation
    with open(eval_file, "w", encoding="utf-8") as f:
      json.dump(evaluation, f, indent=2)
        
    metrics = evaluation["metrics"]
    print(f"  Run {run_id}: P={metrics['precision']:.2f} R={metrics['recall']:.2f} F1={metrics['f1']:.2f}")
    results.append(evaluation)
    
  # Summary
  print(f"\nEvaluated {len(results)} responses")
  if results:
    avg_precision = sum(r["metrics"]["precision"] for r in results) / len(results)
    avg_recall = sum(r["metrics"]["recall"] for r in results) / len(results)
    avg_f1 = sum(r["metrics"]["f1"] for r in results) / len(results)
    print(f"Average: P={avg_precision:.2f} R={avg_recall:.2f} F1={avg_f1:.2f}")
    
  print("OK.")


if __name__ == "__main__":
  main()
