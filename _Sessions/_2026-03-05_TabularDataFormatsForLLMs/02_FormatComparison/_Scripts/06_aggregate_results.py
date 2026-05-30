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
  python 06_aggregate_results.py --test-path .. --update-file ../_INFO_01_FormatComparison-TestResults.md
"""

import argparse, json, re
from pathlib import Path


# -- Display names for models --

MODEL_DISPLAY_NAMES = {
  "gpt-5-mini": "gpt-5-mini",
  "gpt-5": "gpt-5",
  "gpt-5.2": "gpt-5.2",
  "gpt-5.4": "gpt-5.4",
  "gpt-5.5": "gpt-5.5",
  "claude-sonnet-4-5-20250929": "sonnet-4.5",
  "claude-opus-4-5-20251101": "opus-4.5",
  "claude-opus-4-8": "opus-4.8",
}

# Model sort order (for consistent table output)
MODEL_SORT_ORDER = [
  "gpt-5.5", "gpt-5.4", "gpt-5-mini", "gpt-5", "gpt-5.2", "opus-4.8", "opus-4.5", "sonnet-4.5"
]

FORMAT_SORT_ORDER = [
  "csv_quoted", "csv", "kv_colon_space", "markdown_table", "json", "xml", "yaml", "toml"
]

COLUMNS_COUNT = 7  # For per-kilo-cell metrics


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
  effort = data.get("reasoning_effort") or parse_effort_from_folder(folder_name)
  output_format = data.get("output_format") or parse_format_from_folder(folder_name)

  # Time per request at scale limit
  time_per_request = compute_time_per_request(data)
  scale_limit = data.get("max_reliable_rows")

  # Cost per request at scale limit (cost of highest passing iteration / runs)
  cost_per_request = compute_cost_per_request(data)

  # Input/output tokens at scale limit (from highest passing iteration)
  input_tokens, output_tokens = compute_tokens_at_scale(data)

  # Per-kilo-cell metrics
  tpkc = None
  cpkc = None
  if scale_limit and scale_limit > 0:
    cells = scale_limit * COLUMNS_COUNT
    if time_per_request is not None:
      tpkc = round(time_per_request / cells * 1000, 0)
    if cost_per_request is not None:
      cpkc = round(cost_per_request / cells * 1000, 3)

  return {
    "model": model_raw,
    "model_display": MODEL_DISPLAY_NAMES.get(model_raw, model_raw),
    "provider": data.get("provider", "unknown"),
    "effort": effort,
    "format": output_format,
    "scale_limit": scale_limit,
    "bounds": [data.get("last_working_lower_bound"), data.get("last_failed_upper_bound")],
    "failure_mode": data.get("primary_failure_mode"),
    "context_pct": data.get("context_utilization_at_failure_pct"),
    "max_context_tokens": data.get("max_context_tokens"),
    "cost_per_request": cost_per_request,
    "time_per_request_sec": time_per_request,
    "input_tokens_k": round(input_tokens / 1000, 0) if input_tokens else None,
    "output_tokens_k": round(output_tokens / 1000, 0) if output_tokens else None,
    "tpkc": tpkc,
    "cpkc": cpkc,
    "total_cost_usd": round(data.get("total_cost_usd", 0), 2),
    "iterations": len(data.get("search_history", [])),
    "status": "completed",
    "folder": folder_name,
  }


def parse_effort_from_folder(folder_name: str) -> str:
  """Extract effort level from folder name."""
  for level in ("low", "high"):
    if f"_{level}_" in folder_name or folder_name.endswith(f"_{level}"):
      return level
  return "medium"


def parse_format_from_folder(folder_name: str) -> str:
  """Extract format from folder name pattern: model_method_effort_format_maxN."""
  for fmt in FORMAT_SORT_ORDER:
    if f"_{fmt}_" in folder_name:
      return fmt
  return "unknown"


def compute_time_per_request(data: dict) -> float | None:
  """Time for a single LLM API call at scale limit (iteration duration / runs)."""
  history = data.get("search_history", [])
  scale_limit = data.get("max_reliable_rows")
  if not history or not scale_limit:
    return None

  best_multi = None
  best_any = None

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


def compute_cost_per_request(data: dict) -> float | None:
  """Cost for a single LLM API call at scale limit."""
  history = data.get("search_history", [])
  if not history:
    return None

  # Find highest passing iteration (closest to scale limit)
  best = None
  for entry in history:
    if not entry.get("passed"):
      continue
    runs = entry.get("runs_total", 1)
    cost = entry.get("cost_usd", 0)
    per_request = cost / max(runs, 1)
    rows = entry.get("rows", 0)
    if best is None or rows > best["rows"]:
      best = {"rows": rows, "per_request": per_request}

  return round(best["per_request"], 4) if best else None


def compute_tokens_at_scale(data: dict) -> tuple:
  """Get input/output tokens from the highest passing iteration."""
  history = data.get("search_history", [])
  if not history:
    return None, None

  best = None
  for entry in history:
    if not entry.get("passed"):
      continue
    rows = entry.get("rows", 0)
    if best is None or rows > best.get("rows", 0):
      best = entry

  if best:
    return best.get("input_tokens"), best.get("output_tokens")
  return None, None


def load_overrides(overrides_path: Path) -> list:
  """Load manual override records."""
  if not overrides_path.exists():
    return []
  with open(overrides_path, "r", encoding="utf-8") as f:
    return json.load(f)


# ============================================================ Derived data ====================================================


def compute_vs_best(records: list) -> None:
  """Add vs_best_pct field: percentage relative to best format per model."""
  by_model = {}
  for r in records:
    key = r["model_display"]
    if key not in by_model:
      by_model[key] = []
    by_model[key].append(r)

  for model, model_records in by_model.items():
    best = max((r.get("scale_limit") or 0) for r in model_records)
    for r in model_records:
      if best > 0 and r.get("scale_limit"):
        r["vs_best_pct"] = round(r["scale_limit"] / best * 100)
      else:
        r["vs_best_pct"] = None


# ============================================================ JSON output =====================================================


def write_json(records: list, output_path: Path):
  """Write all_results.json."""
  report = {
    "test_count": len(records),
    "columns": COLUMNS_COUNT,
    "status": {
      "completed": sum(1 for r in records if r["status"] == "completed"),
    },
    "results": records,
  }
  with open(output_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)


# ============================================================ Markdown output =================================================


def pad(text: str, width: int) -> str:
  return text.ljust(width)


def fmt_time(seconds: float | None) -> str:
  if seconds is None:
    return "-"
  if seconds < 60:
    return f"~{seconds:.0f} sec"
  return f"~{seconds / 60:.1f} min"


def fmt_cost(cost: float | None) -> str:
  if cost is None or cost == 0:
    return "-"
  return f"${cost:.2f}"


def fmt_tpkc(tpkc: float | None) -> str:
  if tpkc is None:
    return "-"
  return f"{tpkc:.0f}s"


def fmt_cpkc(cpkc: float | None) -> str:
  if cpkc is None:
    return "-"
  return f"${cpkc:.3f}"


def fmt_tokens(tokens_k: float | None) -> str:
  if tokens_k is None:
    return "-"
  return str(int(tokens_k))


def model_sort_key(record: dict) -> tuple:
  model = record["model_display"]
  idx = MODEL_SORT_ORDER.index(model) if model in MODEL_SORT_ORDER else 99
  return (idx, -(record.get("scale_limit") or 0))


def write_markdown(records: list, output_path: Path):
  """Write all_results.md with ready-to-paste tables for INFO_01."""
  sorted_records = sorted(records, key=model_sort_key)
  lines = []

  # -- Section 5.1: All results --
  lines.append("## Section 5.1: All Tests (sorted by model then scale limit)")
  lines.append("")
  lines.append("| Model      | Effort | Format         | Scale   | vs Best | In (K) | Out (K) | Time     | TPKC | Cost  | CPKC   |")
  lines.append("|------------|--------|----------------|---------|---------|--------|---------|----------|------|-------|--------|")

  prev_model = None
  for r in sorted_records:
    if prev_model and r["model_display"] != prev_model:
      lines.append("|            |        |                |         |         |        |         |          |      |       |        |")
    prev_model = r["model_display"]
    lines.append(
      f"| {pad(r['model_display'], 10)} "
      f"| {pad(r['effort'], 6)} "
      f"| {pad(r['format'], 14)} "
      f"| **{r.get('scale_limit', '-')}**{' ' * max(0, 4 - len(str(r.get('scale_limit', '-'))))} "
      f"| {pad(str(r.get('vs_best_pct', '-')) + '%' if r.get('vs_best_pct') else '-', 7)} "
      f"| {pad(fmt_tokens(r.get('input_tokens_k')), 6)} "
      f"| {pad(fmt_tokens(r.get('output_tokens_k')), 7)} "
      f"| {pad(fmt_time(r.get('time_per_request_sec')), 8)} "
      f"| {pad(fmt_tpkc(r.get('tpkc')), 4)} "
      f"| {pad(fmt_cost(r.get('cost_per_request')), 5)} "
      f"| {pad(fmt_cpkc(r.get('cpkc')), 6)} |"
    )
  lines.append("")
  lines.append(f"**Total: {len(records)} tests** ({len(set(r['model_display'] for r in records))} models x {len(set(r['format'] for r in records))} formats)")
  lines.append("")

  # -- Section 5.2: Best format per model --
  lines.append("## Section 5.2: Best Format Per Model (Summary)")
  lines.append("")
  lines.append("| Model        | Best Format | Scale | Worst Format   | Scale | Ratio |")
  lines.append("|--------------|-------------|-------|----------------|-------|-------|")

  by_model = {}
  for r in records:
    key = r["model_display"]
    if key not in by_model:
      by_model[key] = []
    by_model[key].append(r)

  for model in MODEL_SORT_ORDER:
    if model not in by_model:
      continue
    model_records = sorted(by_model[model], key=lambda x: x.get("scale_limit") or 0, reverse=True)
    best = model_records[0]
    worst = model_records[-1]
    ratio = f"{(best.get('scale_limit') or 1) / max(worst.get('scale_limit') or 1, 1):.1f}x"
    lines.append(
      f"| {pad(model, 12)} "
      f"| {pad(best['format'], 11)} "
      f"| {str(best.get('scale_limit', '-')):5s} "
      f"| {pad(worst['format'], 14)} "
      f"| {str(worst.get('scale_limit', '-')):5s} "
      f"| {ratio:5s} |"
    )
  lines.append("")

  # -- Section 5.3: Format rankings per model --
  lines.append("## Section 5.3: Format Rankings Per Model")
  lines.append("")
  lines.append("```")
  for model in MODEL_SORT_ORDER:
    if model not in by_model:
      continue
    model_records = sorted(by_model[model], key=lambda x: x.get("scale_limit") or 0, reverse=True)
    parts = [f"{r['format']} ({r.get('scale_limit', '?')})" for r in model_records]
    lines.append(f"{model + ':':14s} {' > '.join(parts)}")
  lines.append("```")
  lines.append("")

  # -- Section 5.4: Token efficiency vs scale --
  lines.append("## Section 5.4: Token Efficiency vs Scale (csv=1.00x reference)")
  lines.append("")
  lines.append("```")
  for model in MODEL_SORT_ORDER:
    if model not in by_model:
      continue
    csv_rec = next((r for r in by_model[model] if r["format"] == "csv"), None)
    xml_rec = next((r for r in by_model[model] if r["format"] == "xml"), None)
    if csv_rec and xml_rec:
      csv_scale = csv_rec.get("scale_limit") or 0
      xml_scale = xml_rec.get("scale_limit") or 0
      if csv_scale > xml_scale:
        ratio = f"csv {csv_scale / max(xml_scale, 1):.1f}x better"
      else:
        ratio = f"xml {xml_scale / max(csv_scale, 1):.1f}x better despite 2x tokens"
      lines.append(f"{model + ':':14s} csv ({csv_scale}) vs xml ({xml_scale}) - {ratio}")
  lines.append("```")
  lines.append("")

  # -- Section 5.5: Cost efficiency --
  lines.append("## Section 5.5: Cost Efficiency (CPKC - Cost Per Kilo Cells)")
  lines.append("")
  lines.append("| Model        | Best CPKC Format | CPKC   | Scale |")
  lines.append("|--------------|------------------|--------|-------|")
  for model in MODEL_SORT_ORDER:
    if model not in by_model:
      continue
    model_records = [r for r in by_model[model] if r.get("cpkc") is not None]
    if model_records:
      best = min(model_records, key=lambda x: x["cpkc"])
      lines.append(
        f"| {pad(model, 12)} "
        f"| {pad(best['format'], 16)} "
        f"| {fmt_cpkc(best['cpkc']):6s} "
        f"| {str(best.get('scale_limit', '-')):5s} |"
      )
  lines.append("")

  with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))


# ============================================================ Marker-based update =============================================


def generate_sections(records: list) -> dict:
  """Generate content for each AUTO marker section."""
  sorted_records = sorted(records, key=model_sort_key)
  sections = {}

  # section-5.1: main results table
  lines = []
  lines.append("| Model      | Effort | Format         | Scale   | vs Best | In (K) | Out (K) | Time     | TPKC | Cost  | CPKC   |")
  lines.append("|------------|--------|----------------|---------|---------|--------|---------|----------|------|-------|--------|")
  prev_model = None
  for r in sorted_records:
    if prev_model and r["model_display"] != prev_model:
      lines.append("|            |        |                |         |         |        |         |          |      |       |        |")
    prev_model = r["model_display"]
    lines.append(
      f"| {pad(r['model_display'], 10)} "
      f"| {pad(r['effort'], 6)} "
      f"| {pad(r['format'], 14)} "
      f"| **{r.get('scale_limit', '-')}**{' ' * max(0, 4 - len(str(r.get('scale_limit', '-'))))} "
      f"| {pad(str(r.get('vs_best_pct', '-')) + '%' if r.get('vs_best_pct') else '-', 7)} "
      f"| {pad(fmt_tokens(r.get('input_tokens_k')), 6)} "
      f"| {pad(fmt_tokens(r.get('output_tokens_k')), 7)} "
      f"| {pad(fmt_time(r.get('time_per_request_sec')), 8)} "
      f"| {pad(fmt_tpkc(r.get('tpkc')), 4)} "
      f"| {pad(fmt_cost(r.get('cost_per_request')), 5)} "
      f"| {pad(fmt_cpkc(r.get('cpkc')), 6)} |"
    )
  lines.append("")
  lines.append(f"**Total: {len(records)} tests** ({len(set(r['model_display'] for r in records))} models x {len(set(r['format'] for r in records))} formats)")
  sections["section-5.1"] = "\n".join(lines)

  # section-5.2: best format per model
  by_model = {}
  for r in records:
    key = r["model_display"]
    if key not in by_model:
      by_model[key] = []
    by_model[key].append(r)

  lines = []
  lines.append("| Model        | Best Format | Scale | Worst Format   | Scale | Ratio |")
  lines.append("|--------------|-------------|-------|----------------|-------|-------|")
  for model in MODEL_SORT_ORDER:
    if model not in by_model:
      continue
    model_records = sorted(by_model[model], key=lambda x: x.get("scale_limit") or 0, reverse=True)
    best = model_records[0]
    worst = model_records[-1]
    ratio = f"{(best.get('scale_limit') or 1) / max(worst.get('scale_limit') or 1, 1):.1f}x"
    lines.append(
      f"| {pad(model, 12)} "
      f"| {pad(best['format'], 11)} "
      f"| {str(best.get('scale_limit', '-')):5s} "
      f"| {pad(worst['format'], 14)} "
      f"| {str(worst.get('scale_limit', '-')):5s} "
      f"| {ratio:5s} |"
    )
  sections["section-5.2"] = "\n".join(lines)

  # section-5.3: format rankings
  lines = []
  lines.append("```")
  for model in MODEL_SORT_ORDER:
    if model not in by_model:
      continue
    model_records = sorted(by_model[model], key=lambda x: x.get("scale_limit") or 0, reverse=True)
    parts = [f"{r['format']} ({r.get('scale_limit', '?')})" for r in model_records]
    lines.append(f"{model + ':':14s} {' > '.join(parts)}")
  lines.append("```")
  sections["section-5.3"] = "\n".join(lines)

  # section-5.4: token efficiency vs scale
  lines = []
  lines.append("```")
  for model in MODEL_SORT_ORDER:
    if model not in by_model:
      continue
    csv_rec = next((r for r in by_model[model] if r["format"] == "csv"), None)
    xml_rec = next((r for r in by_model[model] if r["format"] == "xml"), None)
    if csv_rec and xml_rec:
      csv_scale = csv_rec.get("scale_limit") or 0
      xml_scale = xml_rec.get("scale_limit") or 0
      if csv_scale > xml_scale:
        ratio = f"csv {csv_scale / max(xml_scale, 1):.1f}x better"
      else:
        ratio = f"xml {xml_scale / max(csv_scale, 1):.1f}x better despite 2x tokens"
      lines.append(f"{model + ':':14s} csv ({csv_scale}) vs xml ({xml_scale}) - {ratio}")
  lines.append("```")
  sections["section-5.4"] = "\n".join(lines)

  # section-5.5: cost efficiency
  lines = []
  lines.append("| Model        | Best CPKC Format | CPKC   | Scale |")
  lines.append("|--------------|------------------|--------|-------|")
  for model in MODEL_SORT_ORDER:
    if model not in by_model:
      continue
    model_records = [r for r in by_model[model] if r.get("cpkc") is not None]
    if model_records:
      best = min(model_records, key=lambda x: x["cpkc"])
      lines.append(
        f"| {pad(model, 12)} "
        f"| {pad(best['format'], 16)} "
        f"| {fmt_cpkc(best['cpkc']):6s} "
        f"| {str(best.get('scale_limit', '-')):5s} |"
      )
  sections["section-5.5"] = "\n".join(lines)

  return sections


def update_file(file_path: Path, sections: dict) -> int:
  """Replace content between AUTO markers in file. Returns count of sections replaced."""
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
  parser = argparse.ArgumentParser(description="Aggregate format comparison results into JSON + markdown")
  parser.add_argument("--test-path", type=Path, required=True, help="Path to test folder (parent of _TestsAndResults)")
  parser.add_argument("--overrides", type=Path, default=None, help="JSON file with manual override records")
  parser.add_argument("--output-dir", type=Path, default=None, help="Output directory (default: test-path)")
  parser.add_argument("--update-file", type=Path, default=None, help="Update AUTO markers in target markdown file")
  args = parser.parse_args()

  test_path = args.test_path.resolve()
  output_dir = (args.output_dir or test_path).resolve()

  if not test_path.exists():
    print(f"ERROR: Test path not found: {test_path}")
    return

  print("=" * 30 + " START: AGGREGATE FORMAT COMPARISON " + "=" * 29)
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

  # Compute derived metrics
  compute_vs_best(records)

  print(f"Total: {len(records)} test configurations")
  print(f"Models: {len(set(r['model_display'] for r in records))}")
  print(f"Formats: {len(set(r['format'] for r in records))}")

  # Print summary
  print()
  sorted_records = sorted(records, key=model_sort_key)
  prev_model = None
  for r in sorted_records:
    if prev_model and r["model_display"] != prev_model:
      print()
    prev_model = r["model_display"]
    print(f"  {r['model_display']:12s} {r['format']:16s} {str(r.get('scale_limit', '-')):>5s} rows  {fmt_cpkc(r.get('cpkc')):>7s}/Kcell  {fmt_time(r.get('time_per_request_sec')):>10s}")
  print()

  # Write outputs
  json_path = output_dir / "all_results.json"
  md_path = output_dir / "all_results.md"

  write_json(records, json_path)
  print(f"JSON: {json_path}")

  write_markdown(records, md_path)
  print(f"Markdown: {md_path}")

  # Update target file if requested
  if args.update_file:
    target = args.update_file.resolve()
    if not target.exists():
      print(f"ERROR: Update target not found: {target}")
      return
    sections = generate_sections(records)
    count = update_file(target, sections)
    print(f"Updated: {target} ({count} sections replaced)")

  print("=" * 31 + " END: AGGREGATE FORMAT COMPARISON " + "=" * 30)


if __name__ == "__main__":
  main()
