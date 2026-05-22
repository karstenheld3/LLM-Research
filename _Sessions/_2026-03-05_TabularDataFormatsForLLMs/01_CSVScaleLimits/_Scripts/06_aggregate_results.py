#!/usr/bin/env python3
"""
Aggregate all scale_limit_result.json files into a single canonical JSON
and generate ready-to-paste markdown tables for INFO_01.

Outputs:
  all_results.json  - Canonical aggregated data (single source of truth)
  all_results.md    - Markdown tables matching INFO_01 sections

Usage:
  python 06_aggregate_results.py --test-path ..
  python 06_aggregate_results.py --test-path .. --overrides overrides.json
"""

import argparse, json, math
from pathlib import Path


# -- Display names for models (JSON model ID -> human-readable) --

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
}

METHOD_DISPLAY_NAMES = {
  "reasoning_effort": "reasoning",
  "temperature": "temperature",
  "thinking": "thinking",
  "adaptive_thinking": "adaptive_thinking",
}


# ============================================================ Load ============================================================


def load_results(test_path: Path) -> list:
  """Load all scale_limit_result.json files from _TestsAndResults/."""
  results = []
  results_path = test_path / "_TestsAndResults"
  if not results_path.exists():
    return results

  for folder in sorted(results_path.iterdir()):
    if not folder.is_dir():
      continue
    result_file = folder / "scale_limit_result.json"
    if not result_file.exists():
      continue

    with open(result_file, "r", encoding="utf-8") as f:
      data = json.load(f)

    results.append(extract_record(data, folder.name))

  return results


def extract_record(data: dict, folder_name: str) -> dict:
  """Extract a normalized record from a scale_limit_result.json."""
  model_raw = data.get("model", "unknown")
  method_raw = data.get("method", "unknown")
  effort = data.get("reasoning_effort") or parse_effort_from_folder(folder_name)

  # Time per request: duration of first passing iteration at scale limit
  time_per_request = compute_time_per_request(data)

  # Truncation: check if any iteration had truncation
  any_truncation = False
  truncation_note = "No"
  for entry in data.get("search_history", []):
    if entry.get("truncated"):
      any_truncation = True
      break
  if any_truncation and data.get("primary_failure_mode") != "truncation":
    truncation_note = "Yes (early iters)"
  elif any_truncation:
    truncation_note = "Yes"

  return {
    "model": model_raw,
    "model_display": MODEL_DISPLAY_NAMES.get(model_raw, model_raw),
    "provider": data.get("provider", "unknown"),
    "method": method_raw,
    "method_display": METHOD_DISPLAY_NAMES.get(method_raw, method_raw),
    "effort": effort,
    "scale_limit": data.get("max_reliable_rows"),
    "bounds": [data.get("last_working_lower_bound"), data.get("last_failed_upper_bound")],
    "failure_mode": data.get("primary_failure_mode"),
    "context_pct": data.get("context_utilization_at_failure_pct"),
    "max_context_tokens": data.get("max_context_tokens"),
    "truncated": truncation_note,
    "cost_usd": round(data.get("total_cost_usd", 0), 2),
    "time_per_request_sec": time_per_request,
    "iterations": len(data.get("search_history", [])),
    "status": "completed",
    "folder": folder_name,
  }


def parse_effort_from_folder(folder_name: str) -> str:
  """Extract effort level from folder name pattern: model_method_effort_maxN."""
  for level in ("low", "high"):
    if f"_{level}_" in folder_name or folder_name.endswith(f"_{level}"):
      return level
  return "medium"


def compute_time_per_request(data: dict) -> float | None:
  """Time for a single LLM API call at scale limit (iteration duration / runs).

  Prefers iterations with multiple verification runs (more reliable average).
  Falls back to single-run iterations if no multi-run passes exist.
  """
  history = data.get("search_history", [])
  scale_limit = data.get("max_reliable_rows")
  if not history or not scale_limit:
    return None

  best_multi = None  # iterations with runs_total >= 3
  best_any = None    # any passing iteration

  for entry in history:
    if not entry.get("passed") or not entry.get("duration_secs"):
      continue
    runs = entry.get("runs_total", 1)
    per_request = entry["duration_secs"] / max(runs, 1)
    rows = entry.get("rows", 0)

    if best_any is None or rows > best_any["rows"]:
      best_any = {"rows": rows, "per_request": per_request}
    if runs >= 3 and (best_multi is None or rows > best_multi["rows"]):
      best_multi = {"rows": rows, "per_request": per_request}

  pick = best_multi or best_any
  return round(pick["per_request"], 1) if pick else None


def load_overrides(overrides_path: Path) -> list:
  """Load manual override records for tests without scale_limit_result.json."""
  if not overrides_path.exists():
    return []
  with open(overrides_path, "r", encoding="utf-8") as f:
    return json.load(f)


# ============================================================ JSON output =====================================================


def write_json(records: list, output_path: Path):
  """Write all_results.json."""
  report = {
    "test_count": len(records),
    "status": {
      "completed": sum(1 for r in records if r["status"] == "completed"),
      "errors": sum(1 for r in records if r["status"] == "errors"),
      "cancelled": sum(1 for r in records if r["status"] == "cancelled"),
    },
    "results": records,
  }
  with open(output_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)


# ============================================================ Markdown output =================================================


PROVIDER_DISPLAY = {"openai": "OpenAI", "anthropic": "Anthropic"}


def provider_display(provider: str) -> str:
  return PROVIDER_DISPLAY.get(provider, provider.capitalize())


def fmt_time(seconds: float | None) -> str:
  if seconds is None:
    return "-"
  if seconds < 60:
    return f"~{seconds:.0f} sec"
  return f"~{seconds / 60:.1f} min"


def fmt_cost(cost: float | None) -> str:
  if cost is None or cost == 0:
    return "$0.00"
  if cost >= 10:
    return f"~${cost:.0f}+"
  return f"${cost:.2f}"


def fmt_pct(pct: float | None) -> str:
  if pct is None:
    return "-"
  return f"{pct:.1f}%"


def fmt_limit(record: dict) -> str:
  limit = record.get("scale_limit")
  status = record.get("status", "completed")
  if limit is None:
    return "-"
  if status in ("cancelled", "errors"):
    return f"{limit}+"
  return str(limit)


def pad(text: str, width: int) -> str:
  return text.ljust(width)


def write_markdown(records: list, output_path: Path):
  """Write all_results.md with ready-to-paste tables for INFO_01."""
  sorted_desc = sorted(records, key=lambda r: r.get("scale_limit") or 0, reverse=True)
  lines = []

  # -- Section 5.1: All configurations --
  lines.append("## Section 5.1: Scale Limit Results (All Configurations)")
  lines.append("")
  lines.append("| Model             | Provider  | Method            | Effort | Scale Limit | Failure Mode  | Context % | Cost    | Time/req |")
  lines.append("|-------------------|-----------|-------------------|--------|-------------|---------------|-----------|---------|----------|")
  for r in sorted_desc:
    lines.append(
      f"| {pad(r['model_display'], 17)} "
      f"| {pad(provider_display(r['provider']), 9)} "
      f"| {pad(r['method_display'], 17)} "
      f"| {pad(r['effort'], 6)} "
      f"| {pad(fmt_limit(r), 11)} "
      f"| {pad(r.get('failure_mode') or '(' + r['status'] + ')', 13)} "
      f"| {pad(fmt_pct(r.get('context_pct')), 9)} "
      f"| {pad(fmt_cost(r.get('cost_usd')), 7)} "
      f"| {pad(fmt_time(r.get('time_per_request_sec')), 8)} |"
    )
  lines.append("")

  # -- Section 6.1: Failure mode per model --
  lines.append("## Section 6.1: Primary Failure Mode per Model")
  lines.append("")
  lines.append("| Model              | Primary Failure | Truncated              | Context Used |")
  lines.append("|--------------------|-----------------|------------------------|--------------|")
  for r in sorted_desc:
    if r["status"] not in ("completed",):
      continue
    label = r["model_display"]
    if r["effort"] != "medium":
      label += f" {r['effort']}"
    lines.append(
      f"| {pad(label, 18)} "
      f"| {pad((r.get('failure_mode') or '-').upper() if r.get('failure_mode') == 'truncation' else (r.get('failure_mode') or '-'), 15)} "
      f"| {pad(r.get('truncated', 'No'), 22)} "
      f"| {pad(fmt_pct(r.get('context_pct')), 12)} |"
    )
  lines.append("")

  # -- Section 7: Effort level data --
  lines.append("## Section 7: Effort Level Data")
  lines.append("")
  by_model = {}
  for r in records:
    key = r["model_display"]
    if key not in by_model:
      by_model[key] = []
    by_model[key].append(r)

  effort_order = {"low": 0, "medium": 1, "high": 2}
  for model_name, runs in by_model.items():
    if len(runs) < 2:
      continue
    runs_sorted = sorted(runs, key=lambda x: effort_order.get(x["effort"], 1))
    lines.append(f"### {model_name} Effort Comparison")
    lines.append("")
    lines.append("| Effort | Scale Limit | Cost    | Time/req |")
    lines.append("|--------|-------------|---------|----------|")
    for r in runs_sorted:
      lines.append(
        f"| {pad(r['effort'], 6)} "
        f"| {pad(fmt_limit(r), 11)} "
        f"| {pad(fmt_cost(r.get('cost_usd')), 7)} "
        f"| {pad(fmt_time(r.get('time_per_request_sec')), 8)} |"
      )
    lines.append("")

  # -- Section 8: Tier comparison data --
  lines.append("## Section 8: Model Tier Comparison Data")
  lines.append("")

  # Mini tier
  mini_temp = next((r for r in records if r["model_display"] == "gpt-4o-mini"), None)
  mini_reason = next((r for r in records if r["model_display"] == "gpt-5-mini" and r["effort"] == "medium"), None)
  if mini_temp and mini_reason:
    lines.append("### Mini Tier (Temperature vs Reasoning)")
    lines.append("")
    lines.append("| Model       | Method      | Scale Limit |")
    lines.append("|-------------|-------------|-------------|")
    lines.append(f"| {pad(mini_temp['model_display'], 11)} | {pad(mini_temp['method_display'], 11)} | {pad(str(mini_temp.get('scale_limit', '-')), 11)} |")
    lines.append(f"| {pad(mini_reason['model_display'], 11)} | {pad(mini_reason['method_display'], 11)} | {pad(str(mini_reason.get('scale_limit', '-')), 11)} |")
    ratio = (mini_reason.get("scale_limit") or 0) / max(mini_temp.get("scale_limit") or 1, 1)
    lines.append(f"\nRatio: {ratio:.0f}x")
    lines.append("")

  # Full tier
  full_temp = next((r for r in records if r["model_display"] == "gpt-4o"), None)
  full_reason = next((r for r in records if r["model_display"] == "gpt-5" and r["effort"] == "low"), None)
  if full_temp and full_reason:
    lines.append("### Full Tier (Temperature vs Reasoning)")
    lines.append("")
    lines.append("| Model  | Method          | Scale Limit |")
    lines.append("|--------|-----------------|-------------|")
    lines.append(f"| {pad(full_temp['model_display'], 6)} | {pad(full_temp['method_display'], 15)} | {pad(str(full_temp.get('scale_limit', '-')), 11)} |")
    lines.append(f"| {pad(full_reason['model_display'], 6)} | {pad(full_reason['method_display'] + ' (low)', 15)} | {pad(str(full_reason.get('scale_limit', '-')), 11)} |")
    ratio = (full_reason.get("scale_limit") or 0) / max(full_temp.get("scale_limit") or 1, 1)
    lines.append(f"\nRatio: {ratio:.0f}x")
    lines.append("")

  with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))


# ============================================================ Main ============================================================


def main():
  parser = argparse.ArgumentParser(description="Aggregate scale limit results into JSON + markdown")
  parser.add_argument("--test-path", type=Path, required=True, help="Path to test folder (parent of _TestsAndResults)")
  parser.add_argument("--overrides", type=Path, default=None, help="JSON file with manual override records (cancelled/error tests)")
  parser.add_argument("--output-dir", type=Path, default=None, help="Output directory (default: test-path)")
  args = parser.parse_args()

  test_path = args.test_path.resolve()
  output_dir = (args.output_dir or test_path).resolve()

  if not test_path.exists():
    print(f"ERROR: Test path not found: {test_path}")
    return

  print("=" * 35 + " START: AGGREGATE RESULTS " + "=" * 34)
  print(f"Scanning: {test_path / '_TestsAndResults'}")

  records = load_results(test_path)
  print(f"Found: {len(records)} result files")

  if args.overrides:
    overrides = load_overrides(args.overrides)
    records.extend(overrides)
    print(f"Overrides: {len(overrides)} manual records added")

  if not records:
    print("ERROR: No results found")
    return

  print(f"Total: {len(records)} test configurations")

  # Sort by scale limit descending for display
  records_sorted = sorted(records, key=lambda r: r.get("scale_limit") or 0, reverse=True)

  # Print summary
  print()
  for r in records_sorted:
    status_marker = "" if r["status"] == "completed" else f" [{r['status']}]"
    print(f"  {r['model_display']:20s} {r['effort']:7s} {fmt_limit(r):>6s} rows  {fmt_cost(r.get('cost_usd')):>8s}  {fmt_time(r.get('time_per_request_sec')):>10s}{status_marker}")
  print()

  # Write outputs
  json_path = output_dir / "all_results.json"
  md_path = output_dir / "all_results.md"

  write_json(records, json_path)
  print(f"JSON: {json_path}")

  write_markdown(records, md_path)
  print(f"Markdown: {md_path}")

  print("=" * 36 + " END: AGGREGATE RESULTS " + "=" * 35)


if __name__ == "__main__":
  main()
