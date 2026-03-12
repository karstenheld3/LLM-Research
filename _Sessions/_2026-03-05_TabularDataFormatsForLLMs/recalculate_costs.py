#!/usr/bin/env python3
"""
Recalculate all costs in scale_limit_result.json files based on updated model-pricing.json.

Usage:
  python recalculate_costs.py [--dry-run]

Options:
  --dry-run    Show what would be changed without modifying files
"""

import argparse
import json
import re
from pathlib import Path


def load_pricing(pricing_path: Path) -> dict:
    """Load model pricing from JSON file."""
    with open(pricing_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["pricing"]


def normalize_model_name(model: str) -> str:
    """Normalize model name to match pricing keys.
    
    Examples:
      claude-opus-4-5-20251101 -> claude-opus-4-5
      claude-sonnet-4-5-20250929 -> claude-sonnet-4-5
      claude-haiku-4-5-20251001 -> claude-haiku-4-5
      gpt-5-mini -> gpt-5-mini
      gpt-5 -> gpt-5
      gpt-5.2 -> gpt-5.2
    """
    # Remove date suffix from Claude models (e.g., -20251101)
    model = re.sub(r"-\d{8}$", "", model)
    return model


def get_pricing_for_model(model: str, provider: str, pricing: dict) -> tuple:
    """Get input and output pricing per 1M tokens for a model."""
    normalized = normalize_model_name(model)
    
    if provider not in pricing:
        raise ValueError(f"Unknown provider: {provider}")
    
    provider_pricing = pricing[provider]
    
    # Try exact match first
    if normalized in provider_pricing:
        p = provider_pricing[normalized]
        return p["input_per_1m"], p["output_per_1m"]
    
    # Try without version suffix (e.g., gpt-5.2 -> gpt-5)
    base_model = re.sub(r"\.\d+$", "", normalized)
    if base_model in provider_pricing:
        p = provider_pricing[base_model]
        return p["input_per_1m"], p["output_per_1m"]
    
    raise ValueError(f"No pricing found for model: {model} (normalized: {normalized}, provider: {provider})")


def calculate_cost(input_tokens: int, output_tokens: int, input_per_1m: float, output_per_1m: float) -> float:
    """Calculate cost from token counts and pricing."""
    input_cost = input_tokens * input_per_1m / 1_000_000
    output_cost = output_tokens * output_per_1m / 1_000_000
    return round(input_cost + output_cost, 6)


def process_result_file(result_path: Path, pricing: dict, dry_run: bool = False) -> dict:
    """Process a single scale_limit_result.json file and recalculate costs."""
    with open(result_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    model = data.get("model", "")
    provider = data.get("provider", "")
    
    if not model or not provider:
        return {"path": str(result_path), "status": "skipped", "reason": "missing model or provider"}
    
    try:
        input_per_1m, output_per_1m = get_pricing_for_model(model, provider, pricing)
    except ValueError as e:
        return {"path": str(result_path), "status": "error", "reason": str(e)}
    
    changes = []
    new_total_cost = 0.0
    
    # Recalculate costs in search_history
    if "search_history" in data:
        for i, entry in enumerate(data["search_history"]):
            input_tokens = entry.get("input_tokens", 0)
            output_tokens = entry.get("output_tokens", 0)
            old_cost = entry.get("cost_usd", 0)
            new_cost = calculate_cost(input_tokens, output_tokens, input_per_1m, output_per_1m)
            
            if abs(old_cost - new_cost) > 0.000001:
                changes.append({
                    "iteration": entry.get("iteration", i + 1),
                    "old_cost": old_cost,
                    "new_cost": new_cost,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens
                })
                entry["cost_usd"] = new_cost
            
            new_total_cost += new_cost
    
    # Recalculate verify_results costs if present
    if "verify_results" in data and data["verify_results"]:
        for i, entry in enumerate(data["verify_results"]):
            input_tokens = entry.get("input_tokens", 0)
            output_tokens = entry.get("output_tokens", 0)
            old_cost = entry.get("cost_usd", 0)
            new_cost = calculate_cost(input_tokens, output_tokens, input_per_1m, output_per_1m)
            
            if abs(old_cost - new_cost) > 0.000001:
                changes.append({
                    "verify_run": i + 1,
                    "old_cost": old_cost,
                    "new_cost": new_cost,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens
                })
                entry["cost_usd"] = new_cost
            
            new_total_cost += new_cost
    
    # Update total cost
    old_total = data.get("total_cost_usd", 0)
    new_total_cost = round(new_total_cost, 6)
    
    total_changed = abs(old_total - new_total_cost) > 0.000001
    if total_changed:
        data["total_cost_usd"] = new_total_cost
    
    result = {
        "path": str(result_path),
        "model": model,
        "provider": provider,
        "pricing": {"input_per_1m": input_per_1m, "output_per_1m": output_per_1m},
        "old_total_cost": old_total,
        "new_total_cost": new_total_cost,
        "changes_count": len(changes),
        "status": "changed" if changes or total_changed else "unchanged"
    }
    
    if changes:
        result["changes"] = changes
    
    # Write updated file
    if not dry_run and (changes or total_changed):
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Recalculate costs in scale_limit_result.json files")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without modifying files")
    args = parser.parse_args()
    
    base_path = Path(__file__).parent
    
    # Load pricing from both test folders (should be identical)
    pricing_paths = [
        base_path / "01_CSVScaleLimits" / "_Scripts" / "model-pricing.json",
        base_path / "02_FormatComparison" / "_Scripts" / "model-pricing.json"
    ]
    
    pricing = None
    for p in pricing_paths:
        if p.exists():
            pricing = load_pricing(p)
            print(f"Loaded pricing from: {p}")
            break
    
    if not pricing:
        print("ERROR: No model-pricing.json found")
        return 1
    
    # Find all scale_limit_result.json files
    result_files = list(base_path.rglob("scale_limit_result.json"))
    print(f"\nFound {len(result_files)} result files")
    
    if args.dry_run:
        print("\n=== DRY RUN MODE (no files will be modified) ===\n")
    
    # Process each file
    summary = {"changed": 0, "unchanged": 0, "skipped": 0, "error": 0}
    all_results = []
    
    for result_path in sorted(result_files):
        result = process_result_file(result_path, pricing, dry_run=args.dry_run)
        all_results.append(result)
        summary[result["status"]] += 1
        
        # Print progress
        status_icon = {"changed": "~", "unchanged": ".", "skipped": "?", "error": "!"}[result["status"]]
        rel_path = result_path.relative_to(base_path)
        
        if result["status"] == "changed":
            print(f"{status_icon} {rel_path}")
            print(f"    Model: {result['model']} ({result['provider']})")
            print(f"    Total: ${result['old_total_cost']:.6f} -> ${result['new_total_cost']:.6f}")
            if "changes" in result:
                for c in result["changes"][:3]:  # Show first 3 changes
                    iter_key = "iteration" if "iteration" in c else "verify_run"
                    print(f"    {iter_key} {c[iter_key]}: ${c['old_cost']:.6f} -> ${c['new_cost']:.6f}")
                if len(result["changes"]) > 3:
                    print(f"    ... and {len(result['changes']) - 3} more changes")
        elif result["status"] == "error":
            print(f"{status_icon} {rel_path}: {result['reason']}")
    
    # Print summary
    print(f"\n=== Summary ===")
    print(f"Changed:   {summary['changed']}")
    print(f"Unchanged: {summary['unchanged']}")
    print(f"Skipped:   {summary['skipped']}")
    print(f"Errors:    {summary['error']}")
    
    if args.dry_run and summary["changed"] > 0:
        print(f"\nRun without --dry-run to apply {summary['changed']} changes")
    
    return 0


if __name__ == "__main__":
    exit(main())
