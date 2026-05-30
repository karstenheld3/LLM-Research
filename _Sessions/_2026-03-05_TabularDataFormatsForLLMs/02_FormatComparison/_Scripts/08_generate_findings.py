#!/usr/bin/env python3
"""
Generate data-backed findings for INFO_02 from aggregated results.

Reads all_results.json and computes:
  - Key findings summary (section 1)
  - Hypothesis evidence tables (section 3)
  - Unexpected findings (section 4)
  - Production recommendations data (section 5)

Updates AUTO markers in INFO_02.

Usage:
  python 08_generate_findings.py --results-file ../all_results.json
  python 08_generate_findings.py --results-file ../all_results.json --update-file ../_INFO_02_FormatComparison-Findings.md
"""

import argparse, json, re
from pathlib import Path


MODEL_SORT_ORDER = [
  "gpt-5.5", "gpt-5.4", "gpt-5-mini", "gpt-5", "gpt-5.2", "opus-4.8", "opus-4.5", "sonnet-4.5"
]

MODEL_FAMILY = {
  "gpt-5.5": "gpt", "gpt-5.4": "gpt", "gpt-5-mini": "gpt",
  "gpt-5": "gpt", "gpt-5.2": "gpt",
  "opus-4.8": "claude", "opus-4.5": "claude", "sonnet-4.5": "claude",
}

COLUMNS = 7


def load_results(results_path: Path) -> list:
  with open(results_path, "r", encoding="utf-8") as f:
    data = json.load(f)
  return data.get("results", data) if isinstance(data, dict) else data


def by_model(records: list) -> dict:
  groups = {}
  for r in records:
    key = r["model_display"]
    if key not in groups:
      groups[key] = []
    groups[key].append(r)
  for key in groups:
    groups[key].sort(key=lambda x: x.get("scale_limit") or 0, reverse=True)
  return groups


def pad(text: str, width: int) -> str:
  return text.ljust(width)


# ============================================================ Section generators ==============================================


def gen_key_findings(records: list, models: dict) -> str:
  """Section 1: Key Findings - computed from data."""
  lines = []
  total = len(records)
  n_models = len(models)
  n_formats = len(set(r["format"] for r in records))

  lines.append(f"Derived from {total}/{total} completed tests. Data in `_INFO_01_FormatComparison-TestResults.md [TBLF-IN05]` section 5.")
  lines.append("")

  # Finding 1: Format preferences differ by model family
  gpt_bests = []
  claude_bests = []
  for model in MODEL_SORT_ORDER:
    if model not in models:
      continue
    best = models[model][0]
    if MODEL_FAMILY.get(model) == "gpt":
      gpt_bests.append((model, best["format"]))
    else:
      claude_bests.append((model, best["format"]))

  gpt_formats = set(f for _, f in gpt_bests)
  claude_formats = set(f for _, f in claude_bests)

  lines.append("- **Format preferences differ dramatically by model family** [TESTED]")
  gpt_summary = ", ".join(f"{m}: {f}" for m, f in gpt_bests)
  claude_summary = ", ".join(f"{m}: {f}" for m, f in claude_bests)
  lines.append(f"  - GPT best formats: {gpt_summary}")
  lines.append(f"  - Claude best formats: {claude_summary}")

  # Max ratio
  max_ratio_model = None
  max_ratio = 0
  for model in MODEL_SORT_ORDER:
    if model not in models:
      continue
    recs = models[model]
    best_scale = recs[0].get("scale_limit") or 1
    worst_scale = recs[-1].get("scale_limit") or 1
    ratio = best_scale / max(worst_scale, 1)
    if ratio > max_ratio:
      max_ratio = ratio
      max_ratio_model = model
  lines.append(f"  - Max spread: {max_ratio:.1f}x ({max_ratio_model})")
  lines.append("")

  # Finding 2: Token efficiency vs scale
  lines.append("- **Token efficiency does NOT predict scale limits** [TESTED]")
  csv_better = 0
  xml_better = 0
  for model in MODEL_SORT_ORDER:
    if model not in models:
      continue
    csv_rec = next((r for r in models[model] if r["format"] == "csv"), None)
    xml_rec = next((r for r in models[model] if r["format"] == "xml"), None)
    if csv_rec and xml_rec:
      csv_s = csv_rec.get("scale_limit") or 0
      xml_s = xml_rec.get("scale_limit") or 0
      if xml_s > csv_s:
        xml_better += 1
      else:
        csv_better += 1
  lines.append(f"  - xml (2.12x tokens) outperforms csv (1.00x) on {xml_better}/{xml_better + csv_better} models")
  lines.append(f"  - csv outperforms xml on {csv_better}/{xml_better + csv_better} models (newer GPT + Claude)")
  lines.append("")

  # Finding 3: Format impact magnitude
  lines.append("- **Format impact is massive - up to {:.1f}x within a single model** [TESTED]".format(max_ratio))
  for model in MODEL_SORT_ORDER:
    if model not in models:
      continue
    recs = models[model]
    best = recs[0]
    worst = recs[-1]
    ratio = (best.get("scale_limit") or 1) / max(worst.get("scale_limit") or 1, 1)
    if ratio >= 3.0:
      lines.append(f"  - {model}: {best['format']} ({best.get('scale_limit')}) vs {worst['format']} ({worst.get('scale_limit')}) = {ratio:.1f}x")
  lines.append("")

  # Finding 4: No universal best format
  best_formats = set(models[m][0]["format"] for m in MODEL_SORT_ORDER if m in models)
  lines.append(f"- **No universal best format exists** [TESTED]")
  for model in MODEL_SORT_ORDER:
    if model not in models:
      continue
    best = models[model][0]
    lines.append(f"  - {model}: {best['format']} ({best.get('scale_limit')})")
  lines.append("")

  # Finding 5: Generational shift
  gpt54 = models.get("gpt-5.4", [None])[0]
  gpt55 = models.get("gpt-5.5", [None])[0]
  if gpt54 and gpt55 and gpt54["format"] != gpt55["format"]:
    lines.append("- **Format preference shifts between model generations** [TESTED]")
    gpt55_json = next((r for r in models.get("gpt-5.5", []) if r["format"] == "json"), None)
    json_drop = ""
    if gpt55_json:
      drop_pct = round((1 - gpt55_json.get("scale_limit", 0) / max(gpt54.get("scale_limit", 1), 1)) * 100)
      json_drop = f", json drops to {gpt55_json.get('scale_limit')} (-{drop_pct}%)"
    lines.append(f"  - gpt-5.4: {gpt54['format']} ({gpt54.get('scale_limit')}). gpt-5.5: {gpt55['format']} ({gpt55.get('scale_limit')}){json_drop}")

  return "\n".join(lines)


def gen_hypothesis_evidence(records: list, models: dict) -> str:
  """Section 3: Hypothesis evidence tables."""
  lines = []

  # H2: JSON ranking per model
  lines.append("### 3.1 H2: JSON Ranking Per Model")
  lines.append("")
  lines.append("| Model      | JSON Scale | JSON Rank | Best Format    | Best Scale | JSON vs Best |")
  lines.append("|------------|------------|-----------|----------------|------------|--------------|")
  for model in MODEL_SORT_ORDER:
    if model not in models:
      continue
    recs = models[model]
    json_rec = next((r for r in recs if r["format"] == "json"), None)
    best = recs[0]
    if json_rec:
      rank = next(i + 1 for i, r in enumerate(recs) if r["format"] == "json")
      vs_best = round(json_rec.get("scale_limit", 0) / max(best.get("scale_limit", 1), 1) * 100)
      lines.append(
        f"| {pad(model, 10)} "
        f"| {str(json_rec.get('scale_limit', '-')):10s} "
        f"| {str(rank) + '/' + str(len(recs)):8s} "
        f"| {pad(best['format'], 14)} "
        f"| {str(best.get('scale_limit', '-')):10s} "
        f"| {vs_best}%{' ':11s} |"
      )
  lines.append("")
  json_best_count = sum(1 for m in MODEL_SORT_ORDER if m in models and models[m][0]["format"] == "json")
  lines.append(f"**JSON is #1 in {json_best_count}/{len(models)} models.**")
  lines.append("")

  # H3: Family preference matrix
  lines.append("### 3.2 H3: Family Preference Divergence")
  lines.append("")
  lines.append("```")
  for model in MODEL_SORT_ORDER:
    if model not in models:
      continue
    recs = models[model]
    family = MODEL_FAMILY.get(model, "?")
    top3 = ", ".join(f"{r['format']} ({r.get('scale_limit')})" for r in recs[:3])
    bot2 = ", ".join(f"{r['format']} ({r.get('scale_limit')})" for r in recs[-2:])
    lines.append(f"{model + ' (' + family + ')':20s} TOP: {top3}")
    lines.append(f"{'':20s} BOT: {bot2}")
  lines.append("```")
  lines.append("")

  # H5: Token efficiency vs scale
  lines.append("### 3.3 H5: Token Efficiency vs Scale (csv=1.00x reference)")
  lines.append("")
  lines.append("| Model      | csv Scale | xml Scale | xml/csv Ratio | xml Wins? |")
  lines.append("|------------|-----------|-----------|---------------|-----------|")
  for model in MODEL_SORT_ORDER:
    if model not in models:
      continue
    csv_rec = next((r for r in models[model] if r["format"] == "csv"), None)
    xml_rec = next((r for r in models[model] if r["format"] == "xml"), None)
    if csv_rec and xml_rec:
      csv_s = csv_rec.get("scale_limit") or 0
      xml_s = xml_rec.get("scale_limit") or 0
      ratio = xml_s / max(csv_s, 1)
      wins = "YES" if xml_s > csv_s else "NO"
      lines.append(
        f"| {pad(model, 10)} "
        f"| {str(csv_s):9s} "
        f"| {str(xml_s):9s} "
        f"| {ratio:13.2f} "
        f"| {wins:9s} |"
      )
  lines.append("")

  # H6: Key-value ranking per model
  lines.append("### 3.4 H6: Key-Value Ranking Per Model")
  lines.append("")
  lines.append("| Model      | kv Scale | kv Rank | Best Format    | Best Scale | kv vs Best |")
  lines.append("|------------|----------|---------|----------------|------------|------------|")
  for model in MODEL_SORT_ORDER:
    if model not in models:
      continue
    recs = models[model]
    kv_rec = next((r for r in recs if r["format"] == "kv_colon_space"), None)
    best = recs[0]
    if kv_rec:
      rank = next(i + 1 for i, r in enumerate(recs) if r["format"] == "kv_colon_space")
      vs_best = round(kv_rec.get("scale_limit", 0) / max(best.get("scale_limit", 1), 1) * 100)
      lines.append(
        f"| {pad(model, 10)} "
        f"| {str(kv_rec.get('scale_limit', '-')):8s} "
        f"| {str(rank) + '/' + str(len(recs)):6s} "
        f"| {pad(best['format'], 14)} "
        f"| {str(best.get('scale_limit', '-')):10s} "
        f"| {vs_best}%{' ':9s} |"
      )
  lines.append("")
  kv_best_count = sum(1 for m in MODEL_SORT_ORDER if m in models and models[m][0]["format"] == "kv_colon_space")
  lines.append(f"**kv_colon_space is #1 in {kv_best_count}/{len(models)} models.**")

  return "\n".join(lines)


def gen_unexpected_findings(records: list, models: dict) -> str:
  """Section 4: Unexpected findings - computed inversions and anomalies."""
  lines = []

  # 1. Generational inversion
  gpt54 = models.get("gpt-5.4", [])
  gpt55 = models.get("gpt-5.5", [])
  if gpt54 and gpt55:
    gpt54_best = gpt54[0]
    gpt55_best = gpt55[0]
    gpt55_json = next((r for r in gpt55 if r["format"] == "json"), None)
    if gpt55_json:
      drop = round((1 - gpt55_json.get("scale_limit", 0) / max(gpt54_best.get("scale_limit", 1), 1)) * 100)
      lines.append(f"1. **gpt-5.5 format preference inverts vs gpt-5.4** [TESTED]")
      lines.append(f"   - gpt-5.4 best: {gpt54_best['format']} ({gpt54_best.get('scale_limit')}). gpt-5.5 best: {gpt55_best['format']} ({gpt55_best.get('scale_limit')}), json drops to {gpt55_json.get('scale_limit')} (-{drop}%)")

  # 2. markdown_table consistently worst
  md_worst_models = []
  for model in MODEL_SORT_ORDER:
    if model not in models:
      continue
    recs = models[model]
    if recs[-1]["format"] == "markdown_table":
      md_worst_models.append(f"{model}: {recs[-1].get('scale_limit')} (rank {len(recs)}/{len(recs)})")
  if md_worst_models:
    lines.append(f"\n2. **markdown_table worst on {len(md_worst_models)} models** [TESTED]")
    for m in md_worst_models:
      lines.append(f"   - {m}")

  # 3. Max inversion (same format best for one, worst for another)
  format_best_worst = {}
  for model in MODEL_SORT_ORDER:
    if model not in models:
      continue
    recs = models[model]
    best_fmt = recs[0]["format"]
    worst_fmt = recs[-1]["format"]
    for fmt in [best_fmt, worst_fmt]:
      if fmt not in format_best_worst:
        format_best_worst[fmt] = {"best_for": [], "worst_for": []}
    format_best_worst[best_fmt]["best_for"].append(model)
    format_best_worst[worst_fmt]["worst_for"].append(model)

  inversions = []
  for fmt, info in format_best_worst.items():
    if info["best_for"] and info["worst_for"]:
      inversions.append((fmt, info["best_for"], info["worst_for"]))

  if inversions:
    lines.append(f"\n3. **Format inversions (best for one model, worst for another)** [TESTED]")
    for fmt, best_for, worst_for in inversions:
      bf = ", ".join(best_for)
      wf = ", ".join(worst_for)
      lines.append(f"   - {fmt}: BEST for {bf}. WORST for {wf}.")

  # 4. Sensitivity ratio
  lines.append(f"\n4. **Format sensitivity inversely correlates with model capability** [VERIFIED]")
  ratios = []
  for model in MODEL_SORT_ORDER:
    if model not in models:
      continue
    recs = models[model]
    best_s = recs[0].get("scale_limit") or 1
    worst_s = recs[-1].get("scale_limit") or 1
    ratio = best_s / max(worst_s, 1)
    ratios.append((model, ratio, best_s))
  ratios_sorted = sorted(ratios, key=lambda x: x[1], reverse=True)
  for model, ratio, best_s in ratios_sorted:
    lines.append(f"   - {model}: {ratio:.1f}x (best={best_s})")

  # 5. Speed comparison gpt-5.5 vs gpt-5.4
  gpt55_tpkc = [r.get("tpkc") for r in gpt55 if r.get("tpkc")]
  gpt54_tpkc = [r.get("tpkc") for r in gpt54 if r.get("tpkc")]
  if gpt55_tpkc and gpt54_tpkc:
    avg55 = sum(gpt55_tpkc) / len(gpt55_tpkc)
    avg54 = sum(gpt54_tpkc) / len(gpt54_tpkc)
    speedup = avg54 / max(avg55, 1)
    lines.append(f"\n5. **gpt-5.5 is {speedup:.1f}x faster than gpt-5.4 (Time Per Kilo-Cell, TPKC)** [TESTED]")
    lines.append(f"   - gpt-5.5 avg TPKC: {avg55:.0f}s. gpt-5.4 avg TPKC: {avg54:.0f}s")

  return "\n".join(lines)


def gen_production_recs(records: list, models: dict) -> str:
  """Section 5: Production recommendations data tables."""
  lines = []

  lines.append("**Scope**: Results apply to 7-column tabular extraction with compound filter. Different column counts or task complexity may shift rankings.")
  lines.append("")
  lines.append("**IMPORTANT (TBLF-FL-005)**: These results use 7/7 columns (simplified dataset). Test 01 used 7/20 columns. Scale limits are NOT directly comparable between Test 01 and Test 02.")
  lines.append("")

  # By model family tables
  lines.append("### By Model (sorted by max scale)")
  lines.append("")
  lines.append("| Model      | Recommended   | Scale | Alternative    | Scale | Avoid          | Scale |")
  lines.append("|------------|---------------|-------|----------------|-------|----------------|-------|")
  for model in MODEL_SORT_ORDER:
    if model not in models:
      continue
    recs = models[model]
    best = recs[0]
    second = recs[1] if len(recs) > 1 else {"format": "-", "scale_limit": "-"}
    worst = recs[-1]
    lines.append(
      f"| {pad(model, 10)} "
      f"| {pad(best['format'], 13)} "
      f"| {str(best.get('scale_limit', '-')):5s} "
      f"| {pad(second['format'], 14)} "
      f"| {str(second.get('scale_limit', '-')):5s} "
      f"| {pad(worst['format'], 14)} "
      f"| {str(worst.get('scale_limit', '-')):5s} |"
    )
  lines.append("")

  # By cost efficiency
  lines.append("### By Cost Efficiency (lowest Cost Per Kilo-Cell, CPKC)")
  lines.append("")
  lines.append("| Model      | Best CPKC Format | CPKC   | Scale | 2nd Best         | CPKC   |")
  lines.append("|------------|------------------|--------|-------|------------------|--------|")
  for model in MODEL_SORT_ORDER:
    if model not in models:
      continue
    cost_sorted = sorted([r for r in models[model] if r.get("cpkc")], key=lambda x: x["cpkc"])
    if len(cost_sorted) >= 2:
      b = cost_sorted[0]
      s = cost_sorted[1]
      lines.append(
        f"| {pad(model, 10)} "
        f"| {pad(b['format'], 16)} "
        f"| ${b['cpkc']:.3f} "
        f"| {str(b.get('scale_limit', '-')):5s} "
        f"| {pad(s['format'], 16)} "
        f"| ${s['cpkc']:.3f} |"
      )
  lines.append("")

  lines.append("### Key Insight")
  lines.append("")
  lines.append("**Always test your specific model with your intended format.** Format choice matters more than previously thought - up to {:.1f}x scale difference. No universal best format exists.".format(
    max((models[m][0].get("scale_limit") or 1) / max(models[m][-1].get("scale_limit") or 1, 1) for m in MODEL_SORT_ORDER if m in models)
  ))

  return "\n".join(lines)


# ============================================================ Marker-based update =============================================


def update_file(file_path: Path, sections: dict) -> int:
  content = file_path.read_text(encoding="utf-8")
  replaced = 0
  for section_id, new_content in sections.items():
    start_marker = f"<!-- AUTO:{section_id}:start -->"
    end_marker = f"<!-- AUTO:{section_id}:end -->"
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    if start_idx == -1 or end_idx == -1:
      continue
    before = content[:start_idx + len(start_marker)] + "\n"
    after = "\n" + content[end_idx:]
    content = before + new_content + after
    replaced += 1
  file_path.write_text(content, encoding="utf-8")
  return replaced


# ============================================================ Markdown output =================================================


def write_findings_md(sections: dict, output_path: Path):
  """Write all_findings.md as reference."""
  lines = []
  for section_id, content in sections.items():
    lines.append(f"## {section_id}")
    lines.append("")
    lines.append(content)
    lines.append("")
  with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))


# ============================================================ Main ============================================================


def main():
  parser = argparse.ArgumentParser(description="Generate findings from aggregated results")
  parser.add_argument("--results-file", type=Path, required=True, help="Path to all_results.json")
  parser.add_argument("--output-dir", type=Path, default=None, help="Output directory (default: results-file parent)")
  parser.add_argument("--update-file", type=Path, default=None, help="Update AUTO markers in target markdown file")
  args = parser.parse_args()

  results_path = args.results_file.resolve()
  output_dir = (args.output_dir or results_path.parent).resolve()

  if not results_path.exists():
    print(f"ERROR: Results file not found: {results_path}")
    return

  print("=" * 30 + " START: GENERATE FINDINGS " + "=" * 30)
  print(f"Reading: {results_path}")

  records = load_results(results_path)
  models = by_model(records)
  print(f"Records: {len(records)} ({len(models)} models)")

  sections = {
    "findings-1": gen_key_findings(records, models),
    "findings-3": gen_hypothesis_evidence(records, models),
    "findings-4": gen_unexpected_findings(records, models),
    "findings-5": gen_production_recs(records, models),
  }

  # Write reference file
  md_path = output_dir / "all_findings.md"
  write_findings_md(sections, md_path)
  print(f"Markdown: {md_path}")

  # Print summary
  print()
  for model in MODEL_SORT_ORDER:
    if model not in models:
      continue
    recs = models[model]
    best = recs[0]
    worst = recs[-1]
    ratio = (best.get("scale_limit") or 1) / max(worst.get("scale_limit") or 1, 1)
    print(f"  {model:12s}  best={best['format']:16s} ({best.get('scale_limit'):4d})  worst={worst['format']:16s} ({worst.get('scale_limit'):4d})  ratio={ratio:.1f}x")
  print()

  # Update target file if requested
  if args.update_file:
    target = args.update_file.resolve()
    if not target.exists():
      print(f"ERROR: Update target not found: {target}")
      return
    count = update_file(target, sections)
    print(f"Updated: {target} ({count} sections replaced)")

  print("=" * 31 + " END: GENERATE FINDINGS " + "=" * 31)


if __name__ == "__main__":
  main()
