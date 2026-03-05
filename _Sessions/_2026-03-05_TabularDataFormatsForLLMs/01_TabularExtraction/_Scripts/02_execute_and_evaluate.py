#!/usr/bin/env python3
"""
Execute LLM extraction and evaluate in single parallel operation.
Zero waiting time - each worker completes full cycle independently.
Fixes: max_output_tokens, truncation detection, improved prompt.
"""

import argparse, asyncio, json, os, re, sys
from pathlib import Path

try:
  import openai
except ImportError:
  print("ERROR: openai package not installed. Run: pip install openai")
  sys.exit(1)


def load_config(instance_path: Path) -> dict:
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


def render_prompt(template: str, csv_data: str, filters: list, columns: list) -> str:
  """Render prompt with EXPLICIT AND logic and quoted values."""
  # Format filters with explicit numbering and quotes (POC style)
  filter_lines = []
  for i, f in enumerate(filters, 1):
    col = f["column"]
    op = f["operator"]
    val = f["value"]
    if op == "in":
      quoted = ", ".join(f'"{v}"' for v in val)
      filter_lines.append(f"{i}. {col} contains {quoted}")
    elif op == "gte":
      filter_lines.append(f"{i}. {col} is ${val:,} or higher")
    else:
      filter_lines.append(f"{i}. {col} {op} {val}")
    
  # Format output with concrete example
  col_format = " | ".join([f"{{{c}}}" for c in columns])
  example = "1. EMP-0042 | Jane Smith | Engineering | $185,000.00/year | Level 4: Top Secret | Exceeds Expectations | Project Alpha"
  output_format = f"[Num]. {col_format}\n\nExample:\n{example}"
    
  prompt = template.replace("{csv_data}", csv_data)
  prompt = prompt.replace("{filters}", "\n".join(filter_lines))
  prompt = prompt.replace("{output_format}", output_format)
    
  return prompt


def extract_employee_ids(response_text: str) -> set:
  """Extract all employee IDs from response using regex."""
  matches = re.findall(r'EMP-(\d{4})', response_text)
  return set(f"EMP-{m}" for m in matches)


def evaluate_response(response_text: str, expected_ids: set) -> dict:
  """Evaluate response against ground truth - instant regex-based."""
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


async def execute_and_evaluate_single(
  semaphore, client, model: str, prompt: str, config: dict,
  run_id: int, total_runs: int, num_rows: int, num_expected: int,
  response_file: Path, eval_file: Path, expected_ids: set
) -> dict:
  """Execute LLM call AND evaluate in single operation - zero wait."""
  async with semaphore:
    result = {
      "run_id": run_id,
      "success": False,
      "truncated": False,
      "metrics": None
    }
        
    try:
      print(f"[ {run_id} / {total_runs} ] Calling {model} to extract {num_expected} records from {num_rows} rows...")
            
      exec_config = config.get("execution", {})
      kwargs = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
      }
            
      # CRITICAL: Set max_output_tokens to avoid truncation
      # gpt-5 models use max_completion_tokens, older models use max_tokens
      max_tokens = exec_config.get("max_output_tokens", 16384)
      if "gpt-5" in model or "o1" in model or "o3" in model:
        kwargs["max_completion_tokens"] = max_tokens
      else:
        kwargs["max_tokens"] = max_tokens
            
      if exec_config.get("temperature") is not None:
        kwargs["temperature"] = exec_config["temperature"]
            
      response = await client.chat.completions.create(**kwargs)
            
      response_text = response.choices[0].message.content
      finish_reason = response.choices[0].finish_reason
      usage = response.usage
            
      # Detect truncation
      truncated = finish_reason == "length"
      if truncated:
          print(f"  WARNING: Output truncated (finish_reason=length)")
            
      # Write response immediately
      response_file.write_text(response_text, encoding="utf-8")
            
      # Evaluate immediately (no waiting)
      evaluation = evaluate_response(response_text, expected_ids)
      evaluation["run_id"] = run_id
      evaluation["response_file"] = response_file.name
      evaluation["truncated"] = truncated
      evaluation["finish_reason"] = finish_reason
      evaluation["token_count"] = usage.completion_tokens if usage else 0
      evaluation["errors"] = []
            
      # Write evaluation immediately
      with open(eval_file, "w", encoding="utf-8") as f:
        json.dump(evaluation, f, indent=2)
            
      metrics = evaluation["metrics"]
      status = "TRUNCATED" if truncated else "OK."
      tp = metrics['true_positives']
      fp = metrics['false_positives']
      fn = metrics['false_negatives']
      print(f"  [ {run_id} / {total_runs} ] {status} Extracted {tp} correct, {fp} extra, {fn} missing. Precision={metrics['precision']:.2f} Recall={metrics['recall']:.2f} F1-Score={metrics['f1']:.2f}")
            
      result["success"] = True
      result["truncated"] = truncated
      result["metrics"] = metrics
            
    except Exception as e:
      print(f"  [ {run_id} / {total_runs} ] FAIL: {e}")
      result["error"] = str(e)
        
    return result


async def run_pipeline(config: dict, instance_path: Path, prompt: str, expected_ids: set):
  """Run full parallel pipeline - execute + evaluate per worker."""
  exec_config = config["execution"]
  model = exec_config["model"]
  num_runs = exec_config["number_of_runs"]
  num_workers = exec_config.get("number_of_workers", 5)
  num_rows = config["data_generation"]["number_of_rows"]
    
  # Create output directories
  response_dir = instance_path / "02_Responses"
  eval_dir = instance_path / "03_Evaluations"
  response_dir.mkdir(parents=True, exist_ok=True)
  eval_dir.mkdir(parents=True, exist_ok=True)
    
  # Load API key
  api_key = os.environ.get("OPENAI_API_KEY")
  if not api_key:
    search_paths = [
      instance_path / ".env",
      instance_path.parent / ".env",
      Path(os.environ.get("USERPROFILE", "")) / ".openai",
    ]
    for keys_file in search_paths:
      if keys_file.exists():
        for line in keys_file.read_text().splitlines():
          line = line.strip()
          if line.startswith("OPENAI_API_KEY="):
            api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
            break
      if api_key:
        break
    
  if not api_key:
    print("ERROR: OPENAI_API_KEY not found")
    sys.exit(1)
    
  client = openai.AsyncOpenAI(api_key=api_key)
  semaphore = asyncio.Semaphore(num_workers)
    
  # Build tasks - skip already completed
  tasks = []
  for run_id in range(1, num_runs + 1):
    response_file = response_dir / f"run_{run_id:02d}.md"
    eval_file = eval_dir / f"eval_{run_id:02d}.json"
        
    if response_file.exists() and eval_file.exists():
      print(f"[ {run_id} / {num_runs} ] {model} extraction from {num_rows} rows: SKIP (already complete)")
      continue
        
    tasks.append(execute_and_evaluate_single(
      semaphore, client, model, prompt, config,
      run_id, num_runs, num_rows, len(expected_ids),
      response_file, eval_file, expected_ids
    ))
    
  if not tasks:
    print("All runs already complete.")
    return []
    
  print(f"Executing {len(tasks)} runs with {num_workers} workers (parallel execute+evaluate)...")
  results = await asyncio.gather(*tasks)
    
  success = sum(1 for r in results if r.get("success"))
  truncated = sum(1 for r in results if r.get("truncated"))
  failed = len(results) - success
    
  print(f"\nOK: {success}, TRUNCATED: {truncated}, FAIL: {failed}")
  return results


def main():
  parser = argparse.ArgumentParser(description="Execute and evaluate in parallel")
  parser.add_argument("--instance-path", required=True, help="Path to test instance")
  args = parser.parse_args()
    
  instance_path = Path(args.instance_path)
  config = load_config(instance_path)
    
  # Load template
  template_path = instance_path.parent / "_PromptsAndTemplates" / "task_prompt_template.md"
  if not template_path.exists():
    print(f"ERROR: Template not found: {template_path}")
    sys.exit(1)
  template = template_path.read_text(encoding="utf-8")
    
  # Load CSV
  csv_path = instance_path / "01_InputData" / "data.csv"
  if not csv_path.exists():
    print("ERROR: Run 01_generate_data.py first")
    sys.exit(1)
  csv_data = csv_path.read_text(encoding="utf-8")
    
  # Load ground truth
  gt_path = instance_path / "01_InputData" / "ground_truth.json"
  with open(gt_path, "r", encoding="utf-8") as f:
    ground_truth = json.load(f)
  expected_ids = set(ground_truth["expected_ids"])
    
  # Render prompt
  filters = config["extraction_task"]["filters"]
  columns = config["extraction_task"]["columns_to_extract"]
  prompt = render_prompt(template, csv_data, filters, columns)
    
  title = f"START: TABULAR EXTRACTION - {instance_path.name}"
  padding = (100 - len(title) - 2) // 2
  print("=" * padding + " " + title + " " + "=" * (100 - padding - len(title) - 2))
  print(f"Model: {config['execution']['model']}")
  print(f"Runs: {config['execution']['number_of_runs']}")
  print(f"Workers: {config['execution'].get('number_of_workers', 5)}")
  print(f"Expected records: {len(expected_ids)}")
  print(f"Max output tokens: {config['execution'].get('max_output_tokens', 16384)}")
  print()
    
  results = asyncio.run(run_pipeline(config, instance_path, prompt, expected_ids))
  
  # Final result
  success = sum(1 for r in results if r.get("success")) if results else 0
  failed = len(results) - success if results else 0
  result = "PASSED" if failed == 0 else "FAILED"
  print(f"\nRESULT: {result}")
  title = f"END: TABULAR EXTRACTION - {instance_path.name}"
  padding = (100 - len(title) - 2) // 2
  print("=" * padding + " " + title + " " + "=" * (100 - padding - len(title) - 2))


if __name__ == "__main__":
  main()
