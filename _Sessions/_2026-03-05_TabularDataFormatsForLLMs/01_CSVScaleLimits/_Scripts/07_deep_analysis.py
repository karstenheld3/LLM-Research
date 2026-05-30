#!/usr/bin/env python3
"""
Deep analysis of per-iteration data from scale limit tests.
Extracts accuracy curves, cost scaling, latency, variance, and efficiency metrics
from existing search_history without re-running tests.

Outputs:
  deep_analysis.json  - All per-iteration metrics
  deep_analysis.md    - Ready-to-paste tables for INFO_01 section 9

Usage:
  python 07_deep_analysis.py --test-path ..
  python 07_deep_analysis.py --test-path .. --update-file ../_INFO_01_CSVScaleLimits-TestResults.md
"""

import argparse, json, re, statistics
from pathlib import Path


MIN_USEFUL_ROWS = 100


# ============================================================ Config ==========================================================

MODEL_DISPLAY_NAMES = {
  "gpt-4o-mini": "gpt-4o-mini",
  "gpt-4o": "gpt-4o",
  "gpt-5-mini": "gpt-5-mini",
  "gpt-5": "gpt-5",
  "gpt-5.2": "gpt-5.2",
  "gpt-5.4": "gpt-5.4",
  "gpt-5.5": "gpt-5.5",
  "claude-haiku-4-5-20251001": "claude-haiku-4.5",
  "claude-sonnet-4-20250514": "claude-sonnet-4",
  "claude-sonnet-4-5-20250929": "claude-sonnet-4.5",
  "claude-opus-4-5-20251101": "claude-opus-4.5",
  "claude-opus-4-6": "claude-opus-4.6",
  "claude-opus-4-7": "claude-opus-4.7",
  "claude-opus-4-8": "claude-opus-4.8",
}


# ============================================================ Load ============================================================


def load_all_iterations(test_path: Path) -> list:
  """Load search_history from all scale_limit_result.json files."""
  results_path = test_path / "_TestsAndResults"
  if not results_path.exists():
    return []

  all_data = []
  for folder in sorted(results_path.iterdir()):
    if not folder.is_dir():
      continue
    result_file = folder / "scale_limit_result.json"
    if not result_file.exists():
      continue

    with open(result_file, "r", encoding="utf-8") as f:
      data = json.load(f)

    model_id = data.get("model", "")
    model_display = MODEL_DISPLAY_NAMES.get(model_id, model_id)
    effort = data.get("reasoning_effort", "medium")
    method = data.get("method", "")
    runs_at_boundary = data.get("last_working_lower_bound")

    for entry in data.get("search_history", []):
      runs_total = entry.get("runs_total", 1)
      duration = entry.get("duration_secs")
      time_per_req = duration / runs_total if duration and runs_total > 0 else None
      cost_per_req = entry.get("cost_usd", 0) / runs_total if runs_total > 0 else None

      # Per-run variance
      run_results = entry.get("run_results", [])
      precisions = [r["precision"] for r in run_results if "precision" in r]
      recalls = [r["recall"] for r in run_results if "recall" in r]
      prec_std = statistics.stdev(precisions) if len(precisions) > 1 else 0.0
      rec_std = statistics.stdev(recalls) if len(recalls) > 1 else 0.0

      all_data.append({
        "model": model_display,
        "effort": effort,
        "method": method,
        "config": f"{model_display} {effort}",
        "rows": entry.get("rows"),
        "precision": entry.get("precision"),
        "recall": entry.get("recall"),
        "f1": entry.get("f1"),
        "passed": entry.get("passed"),
        "runs_passed": entry.get("runs_passed", 0),
        "runs_total": runs_total,
        "input_tokens": entry.get("input_tokens"),
        "output_tokens": entry.get("output_tokens"),
        "cost_usd": entry.get("cost_usd"),
        "cost_per_req": cost_per_req,
        "duration_secs": duration,
        "time_per_req": time_per_req,
        "truncated": entry.get("truncated", False),
        "failure_mode": entry.get("failure_mode"),
        "precision_std": prec_std,
        "recall_std": rec_std,
        "iteration": entry.get("iteration"),
      })

  return all_data


# ============================================================ Analysis ========================================================


def analyze_accuracy_curves(data: list) -> dict:
  """Group by config, sort by rows, show precision/recall at each scale."""
  configs = {}
  for d in data:
    key = d["config"]
    if key not in configs:
      configs[key] = []
    configs[key].append(d)
  for key in configs:
    configs[key].sort(key=lambda x: x["rows"] or 0)
  return configs


def analyze_cost_scaling(data: list) -> list:
  """Cost per request at each row count."""
  return [d for d in data if d["cost_per_req"] is not None]


def analyze_latency_scaling(data: list) -> list:
  """Time per request at each row count."""
  return [d for d in data if d["time_per_req"] is not None]


def analyze_variance(data: list) -> list:
  """Entries with non-zero run-to-run variance."""
  return [d for d in data if d["precision_std"] > 0 or d["recall_std"] > 0]


def compute_efficiency_frontier(data: list) -> list:
  """Find Pareto-optimal configs: max rows/$ and rows/sec at quality=1.0."""
  # Group by config, take the scale limit (max passed rows)
  configs = {}
  for d in data:
    if not d["passed"]:
      continue
    key = d["config"]
    if key not in configs or d["rows"] > configs[key]["rows"]:
      configs[key] = d

  frontier = []
  for key, d in configs.items():
    cost = d["cost_per_req"] or 0.001
    time = d["time_per_req"] or 0.001
    frontier.append({
      "config": key,
      "max_passed_rows": d["rows"],
      "cost_per_req": cost,
      "time_per_req": time,
      "rows_per_dollar": d["rows"] / cost if cost > 0 else 0,
      "rows_per_second": d["rows"] / time if time > 0 else 0,
    })

  frontier.sort(key=lambda x: x["rows_per_dollar"], reverse=True)
  return frontier


def compute_fixed_workload_matrix(data: list) -> dict:
  """For each workload threshold, find which configs pass and their cost/time at that scale."""
  thresholds = [50, 100, 150, 200, 300, 400, 500]
  matrix = {}

  for threshold in thresholds:
    # For each config, find the iteration closest to (but >= ) threshold that passed
    # Or the iteration AT threshold if tested
    candidates = []
    by_config = {}
    for d in data:
      key = d["config"]
      if key not in by_config:
        by_config[key] = []
      by_config[key].append(d)

    for config, points in by_config.items():
      # Find max passed rows for this config
      passed_points = [p for p in points if p["passed"] and p["rows"] and p["rows"] >= threshold]
      if not passed_points:
        continue
      # Use the point closest to threshold (smallest passed rows >= threshold)
      best = min(passed_points, key=lambda x: x["rows"])
      candidates.append({
        "config": config,
        "model": best["model"],
        "effort": best["effort"],
        "tested_rows": best["rows"],
        "cost_per_req": best["cost_per_req"],
        "time_per_req": best["time_per_req"],
      })

    matrix[threshold] = candidates

  return matrix


def compute_pareto_frontier_3d(data: list) -> list:
  """Find Pareto-optimal configs on (capability, cost, latency) axes.
  A config is dominated if another has >= rows, <= cost, and <= time.
  Only includes configs with >= MIN_USEFUL_ROWS."""
  # Get best metrics per config
  by_config = {}
  for d in data:
    if not d["passed"] or not d["rows"]:
      continue
    key = d["config"]
    if key not in by_config or d["rows"] > by_config[key]["rows"]:
      by_config[key] = d

  configs = [c for c in by_config.values() if c["rows"] >= MIN_USEFUL_ROWS]
  pareto = []

  for c in configs:
    rows = c["rows"]
    cost = c["cost_per_req"] or 999
    time = c["time_per_req"] or 9999
    dominated = False
    for other in configs:
      if other["config"] == c["config"]:
        continue
      o_rows = other["rows"]
      o_cost = other["cost_per_req"] or 999
      o_time = other["time_per_req"] or 9999
      if o_rows >= rows and o_cost <= cost and o_time <= time:
        if o_rows > rows or o_cost < cost or o_time < time:
          dominated = True
          break
    if not dominated:
      pareto.append({
        "config": c["config"],
        "rows": rows,
        "cost_per_req": cost,
        "time_per_req": time,
      })

  pareto.sort(key=lambda x: x["rows"], reverse=True)
  return pareto


def compute_constraint_recommendations(data: list) -> list:
  """Generate recommendations for common production constraint scenarios.
  Only considers configs with >= MIN_USEFUL_ROWS."""
  # Get best metrics per config
  by_config = {}
  for d in data:
    if not d["passed"] or not d["rows"]:
      continue
    key = d["config"]
    if key not in by_config or d["rows"] > by_config[key]["rows"]:
      by_config[key] = d

  configs = [c for c in by_config.values() if c["rows"] >= MIN_USEFUL_ROWS]
  scenarios = []

  # Scenario 1: Budget < $0.10/req, latency < 60s, max rows?
  s1_candidates = [c for c in configs if (c["cost_per_req"] or 999) < 0.10 and (c["time_per_req"] or 9999) < 60]
  if s1_candidates:
    best = max(s1_candidates, key=lambda x: x["rows"])
    scenarios.append({"scenario": "Budget <$0.10, latency <60s", "winner": best["config"], "rows": best["rows"], "cost": best["cost_per_req"], "time": best["time_per_req"]})

  # Scenario 2: Need 200+ rows, cheapest
  s2_candidates = [c for c in configs if c["rows"] >= 200]
  if s2_candidates:
    best = min(s2_candidates, key=lambda x: x["cost_per_req"] or 999)
    scenarios.append({"scenario": "Need 200+ rows, cheapest", "winner": best["config"], "rows": best["rows"], "cost": best["cost_per_req"], "time": best["time_per_req"]})

  # Scenario 3: Need 200+ rows, fastest
  s3_candidates = [c for c in configs if c["rows"] >= 200]
  if s3_candidates:
    best = min(s3_candidates, key=lambda x: x["time_per_req"] or 9999)
    scenarios.append({"scenario": "Need 200+ rows, fastest", "winner": best["config"], "rows": best["rows"], "cost": best["cost_per_req"], "time": best["time_per_req"]})

  # Scenario 4: Need 400+ rows, any cost, fastest
  s4_candidates = [c for c in configs if c["rows"] >= 400]
  if s4_candidates:
    best = min(s4_candidates, key=lambda x: x["time_per_req"] or 9999)
    scenarios.append({"scenario": "Need 400+ rows, fastest", "winner": best["config"], "rows": best["rows"], "cost": best["cost_per_req"], "time": best["time_per_req"]})

  # Scenario 5: Latency < 2min, max rows
  s5_candidates = [c for c in configs if (c["time_per_req"] or 9999) < 120]
  if s5_candidates:
    best = max(s5_candidates, key=lambda x: x["rows"])
    scenarios.append({"scenario": "Latency <2min, max rows", "winner": best["config"], "rows": best["rows"], "cost": best["cost_per_req"], "time": best["time_per_req"]})

  # Scenario 6: Best rows/$ (most data per dollar)
  best_rpd = max(configs, key=lambda x: x["rows"] / max(x["cost_per_req"] or 0.001, 0.001))
  scenarios.append({"scenario": "Best rows/$ efficiency", "winner": best_rpd["config"], "rows": best_rpd["rows"], "cost": best_rpd["cost_per_req"], "time": best_rpd["time_per_req"]})

  return scenarios


# ============================================================ Format ==========================================================


def fmt_f(val, decimals=3):
  if val is None:
    return "-"
  return f"{val:.{decimals}f}"


def fmt_time(secs):
  if secs is None:
    return "-"
  if secs < 60:
    return f"{secs:.0f}s"
  return f"{secs / 60:.1f}m"


def fmt_cost(cost):
  if cost is None:
    return "-"
  if cost < 0.01:
    return f"${cost:.4f}"
  return f"${cost:.3f}"


def pad(text, width):
  return str(text).ljust(width)


# ============================================================ Markdown ========================================================


def generate_sections(data: list) -> dict:
  """Generate content for each AUTO section-9.x marker."""
  sections = {}

  # 9.1: Accuracy vs Scale
  curves = analyze_accuracy_curves(data)
  lines = []
  for config, points in sorted(curves.items(), key=lambda x: max((p["rows"] or 0) for p in x[1] if p["passed"]) if any(p["passed"] for p in x[1]) else 0, reverse=True):
    lines.append(f"**{config}**")
    lines.append("")
    lines.append("| Rows | Precision | Recall  | F1      | Pass | Failure Mode  |")
    lines.append("|------|-----------|---------|---------|------|---------------|")
    for p in points:
      pass_str = "YES" if p["passed"] else "NO"
      fm = p["failure_mode"] or "-"
      lines.append(
        f"| {pad(p['rows'], 4)} "
        f"| {pad(fmt_f(p['precision']), 9)} "
        f"| {pad(fmt_f(p['recall']), 7)} "
        f"| {pad(fmt_f(p['f1']), 7)} "
        f"| {pad(pass_str, 4)} "
        f"| {pad(fm, 13)} |"
      )
    lines.append("")
  sections["section-9.1"] = "\n".join(lines).rstrip()

  # 9.2: Cost Scaling
  cost_data = analyze_cost_scaling(data)
  by_config = {}
  for d in cost_data:
    key = d["config"]
    if key not in by_config:
      by_config[key] = []
    by_config[key].append(d)

  lines = []
  lines.append("| Config              | Rows | Cost/req  | In Tokens | Out Tokens | Total Cost |")
  lines.append("|---------------------|------|-----------|-----------|------------|------------|")
  for config in sorted(by_config.keys()):
    points = sorted(by_config[config], key=lambda x: x["rows"] or 0)
    for p in points:
      lines.append(
        f"| {pad(config, 19)} "
        f"| {pad(p['rows'], 4)} "
        f"| {pad(fmt_cost(p['cost_per_req']), 9)} "
        f"| {pad(p.get('input_tokens') or '-', 9)} "
        f"| {pad(p.get('output_tokens') or '-', 10)} "
        f"| {pad(fmt_cost(p['cost_usd']), 10)} |"
      )
  sections["section-9.2"] = "\n".join(lines).rstrip()

  # 9.3: Latency Scaling
  latency_data = analyze_latency_scaling(data)
  by_config = {}
  for d in latency_data:
    key = d["config"]
    if key not in by_config:
      by_config[key] = []
    by_config[key].append(d)

  lines = []
  lines.append("| Config              | Rows | Time/req | Total Duration |")
  lines.append("|---------------------|------|----------|----------------|")
  for config in sorted(by_config.keys()):
    points = sorted(by_config[config], key=lambda x: x["rows"] or 0)
    for p in points:
      lines.append(
        f"| {pad(config, 19)} "
        f"| {pad(p['rows'], 4)} "
        f"| {pad(fmt_time(p['time_per_req']), 8)} "
        f"| {pad(fmt_time(p['duration_secs']), 14)} |"
      )
  sections["section-9.3"] = "\n".join(lines).rstrip()

  # 9.4: Variance
  variance_data = analyze_variance(data)
  lines = []
  if variance_data:
    lines.append("| Config              | Rows | Precision Std | Recall Std | Runs Passed/Total |")
    lines.append("|---------------------|------|---------------|------------|-------------------|")
    for d in sorted(variance_data, key=lambda x: x["recall_std"], reverse=True):
      lines.append(
        f"| {pad(d['config'], 19)} "
        f"| {pad(d['rows'], 4)} "
        f"| {pad(fmt_f(d['precision_std'], 4), 13)} "
        f"| {pad(fmt_f(d['recall_std'], 4), 10)} "
        f"| {d['runs_passed']}/{d['runs_total']}{' ' * 13}|"
      )
  else:
    lines.append("No run-to-run variance detected (all runs within each iteration were identical).")
  sections["section-9.4"] = "\n".join(lines).rstrip()

  # 9.5: Efficiency Frontier
  frontier = compute_efficiency_frontier(data)
  lines = []
  lines.append("| Config              | Max Rows (passed) | Cost/req  | Time/req | Rows/$    | Rows/sec |")
  lines.append("|---------------------|-------------------|-----------|----------|-----------|----------|")
  for entry in frontier[:15]:
    rpd = f"{entry['rows_per_dollar']:.0f}"
    lines.append(
      f"| {pad(entry['config'], 19)} "
      f"| {pad(entry['max_passed_rows'], 17)} "
      f"| {pad(fmt_cost(entry['cost_per_req']), 9)} "
      f"| {pad(fmt_time(entry['time_per_req']), 8)} "
      f"| {pad(rpd, 9)} "
      f"| {pad(fmt_f(entry['rows_per_second'], 1), 8)} |"
    )
  sections["section-9.5"] = "\n".join(lines).rstrip()

  # 9.6: Production Decision Matrix
  lines = []

  # Part A: Fixed-workload comparison
  matrix = compute_fixed_workload_matrix(data)
  lines.append("#### Fixed-Workload Comparison")
  lines.append("")
  lines.append("Models that pass reliably at each workload size, sorted by cost:")
  lines.append("")
  for threshold, candidates in sorted(matrix.items()):
    if not candidates:
      continue
    by_cost = sorted(candidates, key=lambda x: x["cost_per_req"] or 999)
    lines.append(f"**{threshold} rows** ({len(candidates)} configs qualify)")
    lines.append("")
    lines.append("| Config              | Cost/req  | Time/req | Tested At |")
    lines.append("|---------------------|-----------|----------|-----------|")
    for c in by_cost[:8]:
      lines.append(
        f"| {pad(c['config'], 19)} "
        f"| {pad(fmt_cost(c['cost_per_req']), 9)} "
        f"| {pad(fmt_time(c['time_per_req']), 8)} "
        f"| {pad(str(c['tested_rows']) + ' rows', 9)} |"
      )
    lines.append("")

  # Part B: Pareto frontier
  pareto = compute_pareto_frontier_3d(data)
  lines.append(f"#### Pareto-Optimal Configurations (>={MIN_USEFUL_ROWS} rows, Non-Dominated)")
  lines.append("")
  lines.append(f"Configs with >={MIN_USEFUL_ROWS} rows where no other config is simultaneously better on all 3 axes:")
  lines.append("")
  lines.append("| Config              | Max Rows | Cost/req  | Time/req |")
  lines.append("|---------------------|----------|-----------|----------|")
  for p in pareto:
    lines.append(
      f"| {pad(p['config'], 19)} "
      f"| {pad(p['rows'], 8)} "
      f"| {pad(fmt_cost(p['cost_per_req']), 9)} "
      f"| {pad(fmt_time(p['time_per_req']), 8)} |"
    )
  lines.append("")

  # Part C: Constraint-based recommendations
  scenarios = compute_constraint_recommendations(data)
  lines.append("#### Constraint-Based Recommendations")
  lines.append("")
  lines.append("| Scenario                       | Winner              | Rows | Cost/req  | Time/req |")
  lines.append("|--------------------------------|---------------------|------|-----------|----------|")
  for s in scenarios:
    lines.append(
      f"| {pad(s['scenario'], 30)} "
      f"| {pad(s['winner'], 19)} "
      f"| {pad(s['rows'], 4)} "
      f"| {pad(fmt_cost(s['cost']), 9)} "
      f"| {pad(fmt_time(s['time']), 8)} |"
    )

  sections["section-9.6"] = "\n".join(lines).rstrip()

  return sections


def update_file(file_path: Path, sections: dict) -> int:
  """Replace content between AUTO markers in file."""
  content = file_path.read_text(encoding="utf-8")
  replaced = 0

  for section_id, new_content in sections.items():
    pattern = re.compile(
      rf"(<!-- AUTO:{re.escape(section_id)}:start -->\n).*?(\n<!-- AUTO:{re.escape(section_id)}:end -->)",
      re.DOTALL
    )
    new_block = f"\\1{new_content}\\2"
    result, count = pattern.subn(new_block, content)
    if count > 0:
      content = result
      replaced += count

  file_path.write_text(content, encoding="utf-8")
  return replaced


# ============================================================ Main ============================================================


def main():
  parser = argparse.ArgumentParser(description="Deep analysis of per-iteration scale limit data")
  parser.add_argument("--test-path", type=Path, required=True, help="Path to test folder (parent of _TestsAndResults)")
  parser.add_argument("--output-dir", type=Path, default=None, help="Output directory (default: test-path)")
  parser.add_argument("--update-file", type=Path, default=None, help="Update AUTO markers in target markdown file")
  args = parser.parse_args()

  test_path = args.test_path.resolve()
  output_dir = (args.output_dir or test_path).resolve()

  if not test_path.exists():
    print(f"ERROR: Test path not found: {test_path}")
    return

  print("=" * 36 + " START: DEEP ANALYSIS " + "=" * 37)
  print(f"Scanning: {test_path / '_TestsAndResults'}")

  data = load_all_iterations(test_path)
  print(f"Found: {len(data)} iteration data points")

  if not data:
    print("ERROR: No iteration data found")
    return

  configs = set(d["config"] for d in data)
  print(f"Configs: {len(configs)}")

  # Summary stats
  passed_points = [d for d in data if d["passed"]]
  failed_points = [d for d in data if not d["passed"]]
  print(f"Passed iterations: {len(passed_points)}, Failed: {len(failed_points)}")

  # Write JSON
  json_path = output_dir / "deep_analysis.json"
  with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
  print(f"JSON: {json_path}")

  # Write markdown
  sections = generate_sections(data)
  md_lines = []
  for section_id, content in sections.items():
    md_lines.append(f"## {section_id}")
    md_lines.append("")
    md_lines.append(content)
    md_lines.append("")
  md_path = output_dir / "deep_analysis.md"
  with open(md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))
  print(f"Markdown: {md_path}")

  # Update target file
  if args.update_file:
    target = args.update_file.resolve()
    if not target.exists():
      print(f"ERROR: Update target not found: {target}")
      return
    count = update_file(target, sections)
    print(f"Updated: {target} ({count} sections replaced)")

  print("=" * 37 + " END: DEEP ANALYSIS " + "=" * 38)


if __name__ == "__main__":
  main()
