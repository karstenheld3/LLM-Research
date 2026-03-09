#!/usr/bin/env python3
"""
Execute LLM extraction and evaluate in single parallel operation.
V2: Uses llm_client for model-agnostic API handling (OpenAI + Anthropic).
Zero waiting time - each worker completes full cycle independently.
"""

import argparse, asyncio, json, os, re, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor


def load_env_file():
  """Load API keys from .env file."""
  env_paths = [
    Path(__file__).parent.parent / ".env",
    Path(__file__).parent.parent.parent / ".env",
    Path.home() / ".env",
  ]
  for env_path in env_paths:
    if env_path.exists():
      with open(env_path, "r") as f:
        for line in f:
          line = line.strip()
          if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip().strip('"\'')
      return True
  return False

load_env_file()

from llm_client import LLMClient, build_api_params, get_model_config


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


def render_prompt(template: str, data: str, filters: list, columns: list) -> str:
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
    
  prompt = template.replace("{csv_data}", data)
  prompt = prompt.replace("{data}", data)
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


def execute_and_evaluate_single(
  llm_client: LLMClient, model: str, prompt: str,
  run_id: int, total_runs: int, num_rows: int, num_expected: int,
  response_file: Path, eval_file: Path, expected_ids: set
) -> dict:
  """Execute LLM call AND evaluate in single operation - zero wait."""
  result = {
    "run_id": run_id,
    "success": False,
    "truncated": False,
    "metrics": None,
    "duration_secs": 0
  }
  start_time = time.time()
      
  try:
    print(f"[ {run_id} / {total_runs} ] Sending {num_rows} CSV rows to '{model}' ({llm_client.provider}), expecting {num_expected} matching records...")
    
    # Use configured max_tokens from LLMClient (output_length='high' = factor 1.0)
    response = llm_client.call(prompt)
          
    response_text = response["text"]
    finish_reason = response.get("finish_reason", "")
    usage = response.get("usage", {})
          
    # Detect truncation
    truncated = finish_reason == "length" or finish_reason == "max_tokens"
    if truncated:
      print(f"  WARNING: Output truncated (finish_reason={finish_reason})")
          
    # Write response immediately
    response_file.write_text(response_text, encoding="utf-8")
          
    # Evaluate immediately (no waiting)
    evaluation = evaluate_response(response_text, expected_ids)
    evaluation["run_id"] = run_id
    evaluation["response_file"] = response_file.name
    evaluation["truncated"] = truncated
    evaluation["finish_reason"] = finish_reason
    evaluation["input_tokens"] = usage.get("input_tokens", 0)
    evaluation["output_tokens"] = usage.get("output_tokens", 0)
    evaluation["errors"] = []
          
    # Write evaluation immediately
    with open(eval_file, "w", encoding="utf-8") as f:
      json.dump(evaluation, f, indent=2)
          
    metrics = evaluation["metrics"]
    duration = time.time() - start_time
    status = "TRUNCATED:" if truncated else "OK."
    tp = metrics['true_positives']
    fp = metrics['false_positives']
    fn = metrics['false_negatives']
    print(f"  [ {run_id} / {total_runs} ] {status} {tp} correct, {fp} extra, {fn} missing. Precision={metrics['precision']:.2f} Recall={metrics['recall']:.2f} F1-Score={metrics['f1']:.2f} ({duration:.1f} secs)")
          
    result["success"] = True
    result["truncated"] = truncated
    result["metrics"] = metrics
    result["duration_secs"] = duration
          
  except Exception as e:
    duration = time.time() - start_time
    print(f"  [ {run_id} / {total_runs} ] FAIL: {e} ({duration:.1f} secs)")
    result["error"] = str(e)
    result["duration_secs"] = duration
      
  return result


def run_pipeline(config: dict, instance_path: Path, prompt: str, expected_ids: set):
  """Run parallel pipeline using ThreadPoolExecutor - works with sync LLMClient."""
  exec_config = config["execution"]
  model = exec_config["model"]
  num_runs = exec_config["number_of_runs"]
  num_workers = exec_config.get("number_of_workers", 5)
  num_rows = config["data_generation"]["number_of_rows"]
  reasoning_effort = exec_config.get("reasoning_effort", "medium")
    
  # Create output directories
  response_dir = instance_path / "02_Responses"
  eval_dir = instance_path / "03_Evaluations"
  response_dir.mkdir(parents=True, exist_ok=True)
  eval_dir.mkdir(parents=True, exist_ok=True)
  
  # Create LLM client with model-aware parameter handling
  try:
    llm_client = LLMClient(model, reasoning_effort=reasoning_effort, output_length='high')
    print(f"LLM Client: {llm_client.provider} / {llm_client.method}")
  except Exception as e:
    print(f"ERROR: Failed to create LLM client: {e}")
    sys.exit(1)
  
  # output_length='high' uses factor=1.0 from model-parameter-mapping.json
  # This gives max output tokens for the model, avoiding truncation
  num_expected = len(expected_ids)
  configured_max = llm_client.api_params.get("max_tokens", 16384)
  print(f"Max output tokens: {configured_max} (expecting {num_expected} records)")
  
  # Context window pre-flight check
  context_check = llm_client.check_context(prompt, configured_max)
  if not context_check["fits"]:
    print(f"ERROR: {context_check['warning']}")
    print(f"  Input: ~{context_check['input_tokens']} tokens, Output: {context_check['output_tokens']} tokens")
    print(f"  Total: {context_check['total_tokens']} / {context_check['max_context']} max")
    sys.exit(1)
  elif context_check["warning"]:
    print(f"WARNING: {context_check['warning']}")
    
  # Build task list - skip already completed
  pending_runs = []
  for run_id in range(1, num_runs + 1):
    response_file = response_dir / f"run_{run_id:02d}.md"
    eval_file = eval_dir / f"eval_{run_id:02d}.json"
        
    if response_file.exists() and eval_file.exists():
      print(f"[ {run_id} / {num_runs} ] {model} extraction from {num_rows} rows: SKIP (already complete)")
      continue
    
    pending_runs.append((run_id, response_file, eval_file))
    
  if not pending_runs:
    print("All runs already complete.")
    return []
    
  print(f"Executing {len(pending_runs)} runs with {num_workers} parallel workers...")
  
  results = []
  with ThreadPoolExecutor(max_workers=num_workers) as executor:
    futures = []
    for run_id, response_file, eval_file in pending_runs:
      future = executor.submit(
        execute_and_evaluate_single,
        llm_client, model, prompt,
        run_id, num_runs, num_rows, num_expected,
        response_file, eval_file, expected_ids
      )
      futures.append(future)
    
    for future in futures:
      try:
        results.append(future.result())
      except Exception as e:
        print(f"ERROR: {e}")
    
  success = sum(1 for r in results if r.get("success"))
  truncated = sum(1 for r in results if r.get("truncated"))
  failed = len(results) - success
  
  # Calculate timing statistics
  durations = [r.get("duration_secs", 0) for r in results if r.get("duration_secs")]
  if durations:
    avg_time = sum(durations) / len(durations)
    min_time = min(durations)
    max_time = max(durations)
    print(f"\nDuration: min={min_time:.1f} secs, max={max_time:.1f} secs, avg={avg_time:.1f} secs")
    
  print(f"OK: {success}, TRUNCATED: {truncated}, FAIL: {failed}")
  return results


def main():
  parser = argparse.ArgumentParser(description="Execute and evaluate in parallel")
  parser.add_argument("--instance-path", required=True, help="Path to test instance")
  args = parser.parse_args()
    
  instance_path = Path(args.instance_path)
  config = load_config(instance_path)
    
  # Load template - search in instance parent, or test root
  template_paths = [
    instance_path.parent / "_PromptsAndTemplates" / "task_prompt_template.md",
    instance_path.parent.parent / "_PromptsAndTemplates" / "task_prompt_template.md",
    instance_path.parent.parent.parent / "_PromptsAndTemplates" / "task_prompt_template.md",
  ]
  template_path = None
  for tp in template_paths:
    if tp.exists():
      template_path = tp
      break
  
  if not template_path:
    print(f"ERROR: Template not found in: {[str(p) for p in template_paths]}")
    sys.exit(1)
  template = template_path.read_text(encoding="utf-8")
    
  # Load data (CSV or kv_colon format)
  csv_path = instance_path / "01_InputData" / "data.csv"
  txt_path = instance_path / "01_InputData" / "data.txt"
  if csv_path.exists():
    data = csv_path.read_text(encoding="utf-8")
  elif txt_path.exists():
    data = txt_path.read_text(encoding="utf-8")
  else:
    print("ERROR: Run 01_generate_data.py first (no data.csv or data.txt found)")
    sys.exit(1)
    
  # Load ground truth
  gt_path = instance_path / "01_InputData" / "ground_truth.json"
  with open(gt_path, "r", encoding="utf-8") as f:
    ground_truth = json.load(f)
  expected_ids = set(ground_truth["expected_ids"])
    
  # Render prompt
  filters = config["extraction_task"]["filters"]
  columns = config["extraction_task"]["columns_to_extract"]
  prompt = render_prompt(template, data, filters, columns)
    
  title = f"START: TABULAR EXTRACTION - {instance_path.name}"
  padding = (100 - len(title) - 2) // 2
  print("=" * padding + " " + title + " " + "=" * (100 - padding - len(title) - 2))
  print(f"Model: {config['execution']['model']}")
  print(f"Runs: {config['execution']['number_of_runs']}")
  print(f"Workers: {config['execution'].get('number_of_workers', 5)}")
  print(f"Expected records: {len(expected_ids)}")
  print(f"Max output tokens: {config['execution'].get('max_output_tokens', 16384)}")
  print()
    
  results = run_pipeline(config, instance_path, prompt, expected_ids)
  
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
