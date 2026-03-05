#!/usr/bin/env python3
"""
Execute LLM extraction task with parallel workers.
Renders prompt template and calls LLM API for each run.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

try:
  import openai
except ImportError:
  print("ERROR: openai package not installed. Run: pip install openai")
  sys.exit(1)


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


def render_prompt(template: str, csv_data: str, filters: list, columns: list) -> str:
  """Render prompt template with data."""
  # Format filters as human-readable text
  filter_text = []
  for f in filters:
    col = f["column"]
    op = f["operator"]
    val = f["value"]
    if op == "in":
      filter_text.append(f"- {col} contains one of: {', '.join(val)}")
    elif op == "gte":
      filter_text.append(f"- {col} is ${val:,} or higher")
    else:
      filter_text.append(f"- {col} {op} {val}")
    
  # Format output format
  output_format = f"[Num]. {' | '.join(['{' + c + '}' for c in columns])}\n\nExample:\n1. EMP-0001 | Alice Smith | Engineering | $185,000.00/year | Level 4: Top Secret | Exceeds Expectations | Project Aurora"
    
  prompt = template.replace("{csv_data}", csv_data)
  prompt = prompt.replace("{filters}", "\n".join(filter_text))
  prompt = prompt.replace("{output_format}", output_format)
    
  return prompt


async def call_llm(client, model: str, prompt: str, config: dict) -> str:
  """Call LLM API and return response."""
  exec_config = config.get("execution", {})
    
  kwargs = {
    "model": model,
    "messages": [{"role": "user", "content": prompt}],
  }
    
  # Add optional parameters
  if exec_config.get("temperature") is not None:
    kwargs["temperature"] = exec_config["temperature"]
  if exec_config.get("max_output_tokens"):
    kwargs["max_tokens"] = exec_config["max_output_tokens"]
    
  response = await client.chat.completions.create(**kwargs)
  return response.choices[0].message.content


async def execute_single_run(semaphore, client, model: str, prompt: str, 
               config: dict, run_id: int, output_file: Path) -> dict:
  """Execute a single LLM run with semaphore for concurrency control."""
  async with semaphore:
    try:
      print(f"  Run {run_id}: Starting...")
      response = await call_llm(client, model, prompt, config)
            
      output_file.write_text(response, encoding="utf-8")
      print(f"  Run {run_id}: OK.")
      return {"run_id": run_id, "success": True}
    except Exception as e:
      print(f"  Run {run_id}: FAIL - {e}")
      return {"run_id": run_id, "success": False, "error": str(e)}


async def execute_runs(config: dict, instance_path: Path, prompt: str):
  """Execute all runs with parallel workers."""
  exec_config = config["execution"]
  model = exec_config["model"]
  num_runs = exec_config["number_of_runs"]
  num_workers = exec_config.get("number_of_workers", 5)
  max_tokens = exec_config.get("max_context_tokens", 128000)
    
  # Check token estimate
  gt_path = instance_path / "01_InputData" / "ground_truth.json"
  if gt_path.exists():
    with open(gt_path, "r", encoding="utf-8") as f:
      gt = json.load(f)
    token_est = gt.get("token_estimate", 0)
    if token_est > max_tokens * 0.9:
      print(f"WARNING: Token estimate ({token_est}) approaches limit ({max_tokens})")
    
  # Create output directory
  output_dir = instance_path / "02_Responses"
  output_dir.mkdir(parents=True, exist_ok=True)
    
  # Initialize OpenAI client
  api_key = os.environ.get("OPENAI_API_KEY")
  if not api_key:
    # Try loading from various locations
    search_paths = [
      instance_path / ".env",
      instance_path.parent / ".env",
      Path(os.environ.get("USERPROFILE", "")) / ".openai",
      Path(os.environ.get("USERPROFILE", "")) / ".env",
      Path(os.environ.get("USERPROFILE", "")) / ".tools" / ".api-keys.txt",
    ]
    for keys_file in search_paths:
      if keys_file.exists():
        for line in keys_file.read_text().splitlines():
          line = line.strip()
          if line.startswith("OPENAI_API_KEY="):
            api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
            print(f"Loaded API key from: {keys_file}")
            break
      if api_key:
        break
    
  if not api_key:
    env_file = instance_path.parent / ".env"
    print(f"ERROR: OPENAI_API_KEY not found.")
    print(f"Please create {env_file} with content:")
    print("OPENAI_API_KEY=sk-...")
    sys.exit(1)
    
  client = openai.AsyncOpenAI(api_key=api_key)
    
  # Create semaphore for worker limit
  semaphore = asyncio.Semaphore(num_workers)
    
  # Build tasks for runs that don't exist yet
  tasks = []
  for run_id in range(1, num_runs + 1):
    output_file = output_dir / f"run_{run_id:02d}.md"
    if output_file.exists():
      print(f"  Run {run_id}: SKIP (exists)")
      continue
    tasks.append(execute_single_run(semaphore, client, model, prompt, 
                    config, run_id, output_file))
    
  if not tasks:
    print("All runs already exist.")
    return
    
  print(f"Executing {len(tasks)} runs with {num_workers} workers...")
  results = await asyncio.gather(*tasks)
    
  success = sum(1 for r in results if r.get("success"))
  failed = len(results) - success
  print(f"Completed: {success} OK, {failed} FAIL")


def main():
  parser = argparse.ArgumentParser(description="Execute LLM extraction task")
  parser.add_argument("--instance-path", required=True, help="Path to test instance folder")
  args = parser.parse_args()
    
  instance_path = Path(args.instance_path)
    
  # Load config
  config = load_config(instance_path)
    
  # Load prompt template
  template_path = instance_path.parent / "_PromptsAndTemplates" / "task_prompt_template.md"
  if not template_path.exists():
    print(f"ERROR: Template not found: {template_path}")
    sys.exit(1)
    
  template = template_path.read_text(encoding="utf-8")
    
  # Load CSV data
  csv_path = instance_path / "01_InputData" / "data.csv"
  if not csv_path.exists():
    print(f"ERROR: CSV not found: {csv_path}. Run 01_generate_data.py first.")
    sys.exit(1)
    
  csv_data = csv_path.read_text(encoding="utf-8")
    
  # Render prompt
  filters = config["extraction_task"]["filters"]
  columns = config["extraction_task"]["columns_to_extract"]
  prompt = render_prompt(template, csv_data, filters, columns)
    
  print(f"Model: {config['execution']['model']}")
  print(f"Runs: {config['execution']['number_of_runs']}")
  print(f"Workers: {config['execution'].get('number_of_workers', 5)}")
    
  # Execute
  asyncio.run(execute_runs(config, instance_path, prompt))
  print("OK.")


if __name__ == "__main__":
  main()
