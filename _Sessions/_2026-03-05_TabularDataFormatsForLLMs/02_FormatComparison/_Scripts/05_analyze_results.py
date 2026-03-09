#!/usr/bin/env python3
"""
Analyze scale limit results and test hypotheses.
Generates comparison reports from scale_limit_result.json files.
"""

import argparse, json, statistics, time
from pathlib import Path


def load_results(test_path: Path) -> list:
  """Load all scale_limit_result.json files from test path."""
  results = []
  
  for folder in test_path.iterdir():
    if not folder.is_dir():
      continue
    
    result_file = folder / "scale_limit_result.json"
    if result_file.exists():
      with open(result_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        data["folder"] = folder.name
        results.append(data)
  
  return results


def test_h1_effort_impact(results: list) -> dict:
  """H1: Low reasoning effort degrades performance at scale."""
  # Group by model, compare effort levels
  by_model = {}
  for r in results:
    model = r.get("model", "unknown")
    if model not in by_model:
      by_model[model] = []
    by_model[model].append(r)
  
  findings = []
  for model, runs in by_model.items():
    if len(runs) < 2:
      continue
    
    # Sort by scale limit
    runs_sorted = sorted(runs, key=lambda x: x.get("max_reliable_rows") or 0)
    low_run = runs_sorted[0]
    high_run = runs_sorted[-1]
    
    low_scale = low_run.get("max_reliable_rows") or 0
    high_scale = high_run.get("max_reliable_rows") or 0
    
    if low_scale > 0 and high_scale > low_scale:
      improvement = ((high_scale - low_scale) / low_scale) * 100
      findings.append({
        "model": model,
        "low_scale": low_scale,
        "high_scale": high_scale,
        "improvement_pct": round(improvement, 1)
      })
  
  if not findings:
    return {"verdict": "INCONCLUSIVE", "reason": "Insufficient data for comparison", "findings": []}
  
  avg_improvement = statistics.mean([f["improvement_pct"] for f in findings])
  verdict = "SUPPORTED" if avg_improvement > 10 else "NOT SUPPORTED"
  
  return {
    "verdict": verdict,
    "reason": f"Average improvement: {avg_improvement:.1f}%",
    "findings": findings
  }


def test_h2_truncation_primary(results: list) -> dict:
  """H2: Truncation is primary failure mode, not comprehension errors."""
  failure_modes = [r.get("primary_failure_mode") for r in results if r.get("primary_failure_mode")]
  
  if not failure_modes:
    return {"verdict": "INCONCLUSIVE", "reason": "No failure mode data", "findings": []}
  
  truncation_count = sum(1 for m in failure_modes if m == "truncation")
  comprehension_count = sum(1 for m in failure_modes if m == "comprehension")
  total = len(failure_modes)
  
  truncation_pct = (truncation_count / total) * 100 if total > 0 else 0
  
  verdict = "SUPPORTED" if truncation_pct > 50 else "NOT SUPPORTED"
  
  return {
    "verdict": verdict,
    "reason": f"Truncation: {truncation_count}/{total} ({truncation_pct:.1f}%), Comprehension: {comprehension_count}/{total}",
    "findings": {
      "truncation": truncation_count,
      "comprehension": comprehension_count,
      "total": total,
      "truncation_pct": round(truncation_pct, 1)
    }
  }


def test_h3_token_correlation(results: list) -> dict:
  """H3: Scale limit correlates with token count, not absolute row count."""
  # Check if tokens per row is consistent
  tokens_per_row = []
  
  for r in results:
    history = r.get("search_history", [])
    for h in history:
      rows = h.get("rows", 0)
      tokens = h.get("input_tokens", 0)
      if rows > 0 and tokens > 0:
        tokens_per_row.append(tokens / rows)
  
  if len(tokens_per_row) < 3:
    return {"verdict": "INCONCLUSIVE", "reason": "Insufficient token data", "findings": []}
  
  mean_tpr = statistics.mean(tokens_per_row)
  std_tpr = statistics.stdev(tokens_per_row) if len(tokens_per_row) > 1 else 0
  cv = (std_tpr / mean_tpr) * 100 if mean_tpr > 0 else 0
  
  # Low coefficient of variation = consistent tokens per row
  verdict = "SUPPORTED" if cv < 20 else "NOT SUPPORTED"
  
  return {
    "verdict": verdict,
    "reason": f"Tokens/row: {mean_tpr:.1f} (CV={cv:.1f}%)",
    "findings": {
      "mean_tokens_per_row": round(mean_tpr, 1),
      "std_tokens_per_row": round(std_tpr, 1),
      "coefficient_of_variation": round(cv, 1),
      "samples": len(tokens_per_row)
    }
  }


def test_h4_context_utilization(results: list) -> dict:
  """H4: Failure occurs at ~80% context window utilization."""
  utilizations = [r.get("context_utilization_at_failure_pct") for r in results 
                  if r.get("context_utilization_at_failure_pct") is not None]
  
  if not utilizations:
    return {"verdict": "INCONCLUSIVE", "reason": "No context utilization data", "findings": []}
  
  mean_util = statistics.mean(utilizations)
  std_util = statistics.stdev(utilizations) if len(utilizations) > 1 else 0
  min_util = min(utilizations)
  max_util = max(utilizations)
  
  # Check if mean is around 80% (70-90%)
  verdict = "SUPPORTED" if 70 <= mean_util <= 90 else "PARTIALLY SUPPORTED" if 60 <= mean_util <= 95 else "NOT SUPPORTED"
  
  return {
    "verdict": verdict,
    "reason": f"Mean: {mean_util:.1f}%, Range: {min_util:.1f}% - {max_util:.1f}%",
    "findings": {
      "mean_pct": round(mean_util, 1),
      "std_pct": round(std_util, 1),
      "min_pct": round(min_util, 1),
      "max_pct": round(max_util, 1),
      "samples": len(utilizations)
    }
  }


def test_h6_reasoning_vs_temperature(results: list) -> dict:
  """H6: Reasoning models outperform temperature models at scale."""
  reasoning_scales = []
  temperature_scales = []
  
  for r in results:
    method = r.get("method", "")
    scale = r.get("max_reliable_rows")
    if scale is None:
      continue
    
    if "reasoning" in method or "thinking" in method:
      reasoning_scales.append(scale)
    elif "temperature" in method:
      temperature_scales.append(scale)
  
  if not reasoning_scales or not temperature_scales:
    return {"verdict": "INCONCLUSIVE", "reason": "Need both reasoning and temperature model data", "findings": []}
  
  avg_reasoning = statistics.mean(reasoning_scales)
  avg_temperature = statistics.mean(temperature_scales)
  
  improvement = ((avg_reasoning - avg_temperature) / avg_temperature) * 100 if avg_temperature > 0 else 0
  verdict = "SUPPORTED" if improvement > 10 else "NOT SUPPORTED"
  
  return {
    "verdict": verdict,
    "reason": f"Reasoning: {avg_reasoning:.0f} rows, Temperature: {avg_temperature:.0f} rows ({improvement:+.1f}%)",
    "findings": {
      "avg_reasoning_scale": round(avg_reasoning, 0),
      "avg_temperature_scale": round(avg_temperature, 0),
      "improvement_pct": round(improvement, 1)
    }
  }


def generate_markdown_report(results: list, hypotheses: dict, output_path: Path):
  """Generate markdown analysis report."""
  lines = [
    "# Scale Limit Analysis Report",
    "",
    f"Generated: {time.strftime('%Y-%m-%d %H:%M')}",
    "",
    "## Summary",
    "",
    "| Model | Method | Effort | Scale Limit | Failure Mode | Context % | Cost |",
    "|-------|--------|--------|-------------|--------------|-----------|------|"
  ]
  
  for r in sorted(results, key=lambda x: x.get("model", "")):
    model = r.get("model", "?")
    method = r.get("method", "?")
    scale = r.get("max_reliable_rows", "?")
    mode = r.get("primary_failure_mode", "?")
    ctx = r.get("context_utilization_at_failure_pct")
    ctx_str = f"{ctx:.1f}%" if ctx else "?"
    cost = r.get("total_cost_usd")
    cost_str = f"${cost:.4f}" if cost else "?"
    
    # Extract effort from folder name
    folder = r.get("folder", "")
    effort = "medium"
    if "_low_" in folder:
      effort = "low"
    elif "_high_" in folder:
      effort = "high"
    
    lines.append(f"| {model} | {method} | {effort} | {scale} | {mode} | {ctx_str} | {cost_str} |")
  
  lines.extend(["", "## Hypothesis Testing", ""])
  
  for h_id, h_data in hypotheses.items():
    lines.extend([
      f"### {h_id}",
      f"**Result**: {h_data['verdict']}",
      f"- {h_data['reason']}",
      ""
    ])
  
  lines.extend([
    "## Data Files",
    ""
  ])
  
  for r in results:
    lines.append(f"- `{r.get('folder', '?')}/scale_limit_result.json`")
  
  with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
  
  return output_path


def generate_json_report(results: list, hypotheses: dict, output_path: Path):
  """Generate JSON analysis report."""
  report = {
    "generated": time.strftime("%Y-%m-%d %H:%M"),
    "results_count": len(results),
    "results": results,
    "hypotheses": hypotheses
  }
  
  with open(output_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
  
  return output_path


def main():
  parser = argparse.ArgumentParser(description="Analyze scale limit results")
  parser.add_argument("--test-path", type=Path, required=True, help="Path to test folder")
  parser.add_argument("--output", type=str, default="analysis_report.md", help="Output file name")
  parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
  args = parser.parse_args()
  
  test_path = args.test_path.resolve()
  
  if not test_path.exists():
    print(f"ERROR: Test path not found: {test_path}")
    return
  
  print("=" * 35 + " START: RESULTS ANALYSIS " + "=" * 35)
  print(f"Scanning: {test_path}")
  
  # Load results
  results = load_results(test_path)
  print(f"Found: {len(results)} result files")
  
  if not results:
    print("ERROR: No scale_limit_result.json files found")
    return
  
  # Test hypotheses
  hypotheses = {
    "H1: Low effort degrades performance": test_h1_effort_impact(results),
    "H2: Truncation is primary failure mode": test_h2_truncation_primary(results),
    "H3: Scale correlates with token count": test_h3_token_correlation(results),
    "H4: Failure at ~80% context utilization": test_h4_context_utilization(results),
    "H6: Reasoning models outperform temperature": test_h6_reasoning_vs_temperature(results)
  }
  
  # Print summary
  print()
  print("Hypothesis Results:")
  for h_id, h_data in hypotheses.items():
    print(f"  {h_id}: {h_data['verdict']}")
  print()
  
  # Generate report
  output_path = test_path / args.output
  
  if args.format == "md":
    generate_markdown_report(results, hypotheses, output_path)
  else:
    output_path = test_path / args.output.replace(".md", ".json")
    generate_json_report(results, hypotheses, output_path)
  
  print(f"Report saved: {output_path}")
  print("=" * 36 + " END: RESULTS ANALYSIS " + "=" * 37)


if __name__ == "__main__":
  main()
