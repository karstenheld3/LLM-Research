#!/usr/bin/env python3
"""
Generate test data for tabular extraction benchmark.
Creates CSV with adversarial characters and ground truth for evaluation.
"""

import argparse, csv, json, random, re, sys
from pathlib import Path

# Data pools with adversarial characters (colons, pipes, commas, ampersands)
FIRST_NAMES = [
  "Sarah", "James", "Maria", "Chen", "Alexandra", "Marcus", "Yuki", "Robert",
  "Jennifer", "Lisa", "Michael", "Emma", "David", "Sophia", "Daniel", "Olivia",
  "William", "Isabella", "Alexander", "Mia", "Benjamin", "Charlotte", "Ethan",
  "Amelia", "Jacob", "Harper", "Lucas", "Evelyn", "Mason", "Abigail"
]

LAST_NAMES = [
  "Mitchell-Reynolds", "O'Connor", "Gonzalez-Smith", "Wei-Lin", "Petrova-Williams",
  "Johnson Jr.", "Tanaka-Morrison", "Stevens", "Garcia", "Park", "Anderson",
  "Taylor-Brown", "Martinez", "Lee-Chang", "Wilson III", "Moore", "Jackson",
  "White-Peters", "Harris", "Thompson", "Clark-Davis", "Lewis", "Robinson",
  "Walker", "Young-Kim", "Allen", "King", "Wright-Scott", "Lopez", "Hill"
]

DEPARTMENTS = [
  "Research & Development", "Sales: Enterprise", "Human Resources | Talent",
  "Engineering, Platform", "Legal: Compliance", "Marketing, Brand",
  "Finance: Treasury", "Customer Success | Support", "Operations, Logistics",
  "Product: Core", "IT, Infrastructure", "Security | Risk"
]

TITLES = [
  "Principal Scientist: AI", "Senior Account Exec, West", "VP | People Ops",
  "Staff Engineer: Backend", "Associate Counsel, IP", "Marketing Lead: Digital",
  "Director, FP&A", "Success Manager | Enterprise", "Ops Lead: Supply Chain",
  "Product Manager, Core", "IT Admin: Network", "Security Analyst | SOC"
]

LOCATIONS = [
  "Building A, Floor 3 | Desk 101", "Remote: San Francisco, CA",
  "Building B | Floor 5, Room 502", "Hybrid: NYC, 3 days/week",
  "Building C, Floor 2 | Lab Area", "Remote: Austin, TX",
  "HQ: Main Building, Exec Floor", "Hybrid: Seattle, 2 days/week"
]

CLEARANCE_LEVELS = [
  "Level 1: Basic", "Level 2: Confidential", "Level 3: Secret",
  "Level 4: Top Secret", "Level 5: Executive"
]

PERFORMANCE_RATINGS = [
  "Exceptional: Top 5%", "Exceeds Expectations: Top 20%",
  "Meets Expectations", "Developing: Needs Improvement",
  "Exceeds Expectations: Promotion Ready"
]

PROJECTS = [
  "Project Aurora: Lead | Nexus: Contributor",
  "Q4 Push: Owner, Enterprise | SMB Expansion",
  "Culture 2025: Sponsor | DEI: Executive Lead",
  "Platform v3: Tech Lead | Migration: Owner",
  "Compliance 2025: Lead | Audit: Support",
  "Brand Refresh: Lead | Campaign: Q1, Q2"
]

# All possible columns
ALL_COLUMNS = [
  "id", "name", "department", "title", "salary", "clearance", "rating",
  "projects", "location", "start_date", "email", "phone", "manager_id",
  "team", "level", "bonus_pct", "reviews", "certifications", "equipment", "pto"
]


def generate_employee_id(idx: int) -> str:
  return f"EMP-{idx:04d}"


def generate_salary() -> int:
  return random.choice([65000, 72000, 85000, 95000, 110000, 125000, 145000, 
              165000, 185000, 215000, 245000, 275000, 325000, 385000])


def generate_start_date() -> str:
  year = random.randint(2015, 2024)
  month = random.randint(1, 12)
  day = random.randint(1, 28)
  return f"{year}-{month:02d}-{day:02d}"


def generate_email(first: str, last: str) -> str:
  first_clean = first.lower().replace(" ", "")
  last_clean = last.lower().replace("'", "").replace("-", ".").replace(" ", "")
  domain = random.choice(["company.com", "corp.io", "enterprise.net"])
  return f"{first_clean}.{last_clean}@{domain}"


def generate_phone() -> str:
  area = random.choice([415, 510, 650, 408, 212, 312, 617, 303, 206, 512])
  ext = random.randint(100, 999)
  return f"+1-{area}-555-{random.randint(1000,9999)} | ext: {ext}"


def generate_record(idx: int, columns: list) -> dict:
  first = random.choice(FIRST_NAMES)
  last = random.choice(LAST_NAMES)
  salary = generate_salary()
    
  all_data = {
    "id": generate_employee_id(idx),
    "name": f"{first} {last}",
    "department": random.choice(DEPARTMENTS),
    "title": random.choice(TITLES),
    "salary": f"${salary:,}.00/year",
    "clearance": random.choice(CLEARANCE_LEVELS),
    "rating": random.choice(PERFORMANCE_RATINGS),
    "projects": random.choice(PROJECTS),
    "location": random.choice(LOCATIONS),
    "start_date": generate_start_date(),
    "email": generate_email(first, last),
    "phone": generate_phone(),
    "manager_id": f"EMP-{random.randint(1, 50):04d}",
    "team": random.choice(["Platform", "Enterprise", "Core", "Infra"]),
    "level": f"L{random.randint(3, 10)}",
    "bonus_pct": f"{random.choice([5, 8, 10, 12, 15, 20])}%",
    "reviews": str(random.randint(1, 5)),
    "certifications": random.choice(["AWS, Azure", "None", "PMP, CSM", "CISSP"]),
    "equipment": random.choice(["MacBook Pro M3", "Dell XPS 15", "ThinkPad X1"]),
    "pto": f"{random.choice([15, 18, 20, 25])} days"
  }
    
  return {col: all_data[col] for col in columns}


def apply_filters(records: list, filters: list) -> list:
  """Apply filters to records and return matching ones."""
  matching = []
  for record in records:
    match = True
    for f in filters:
      col = f["column"]
      op = f["operator"]
      val = f["value"]
            
      record_val = record.get(col, "")
            
      if op == "in":
        # Check if any value in list is contained in record value
        if not any(v in record_val for v in val):
          match = False
          break
      elif op == "gte":
        # Extract numeric value from salary string
        if col == "salary":
          num_match = re.search(r'\$?([\d,]+)', record_val)
          if num_match:
            record_num = int(num_match.group(1).replace(",", ""))
            if record_num < val:
              match = False
              break
          else:
            match = False
            break
        
    if match:
      matching.append(record)
    
  return matching


def estimate_tokens(text: str) -> int:
  """Rough token estimate: ~4 chars per token for English text."""
  return len(text) // 4


def format_as_csv(records: list, columns: list) -> str:
  """Format records as quoted CSV."""
  import io
  output = io.StringIO()
  writer = csv.DictWriter(output, fieldnames=columns, quoting=csv.QUOTE_ALL)
  writer.writeheader()
  writer.writerows(records)
  return output.getvalue()


def format_as_csv_raw(records: list, columns: list) -> str:
  """Format records as unquoted CSV (csv_raw format)."""
  import io
  output = io.StringIO()
  writer = csv.DictWriter(output, fieldnames=columns, quoting=csv.QUOTE_MINIMAL)
  writer.writeheader()
  writer.writerows(records)
  return output.getvalue()


def format_as_kv_colon_space(records: list, columns: list) -> str:
  """Format records as key: value pairs with space (kv_colon_space format)."""
  lines = []
  for i, record in enumerate(records, 1):
    lines.append(f"### Record {i}")
    for col in columns:
      label = col.replace("_", " ").title().replace(" ", "")
      lines.append(f"{label}: {record[col]}")
    lines.append("")
  return "\n".join(lines)


def format_as_markdown_table(records: list, columns: list) -> str:
  """Format records as Markdown table."""
  lines = []
  # Header row
  lines.append("| " + " | ".join(columns) + " |")
  # Separator row
  lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
  # Data rows
  for record in records:
    row = "| " + " | ".join(str(record[col]) for col in columns) + " |"
    lines.append(row)
  return "\n".join(lines)


def format_as_json(records: list, columns: list) -> str:
  """Format records as JSON array."""
  return json.dumps(records, indent=2, ensure_ascii=False)


def format_as_xml(records: list, columns: list) -> str:
  """Format records as XML."""
  lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<records>']
  for record in records:
    lines.append('  <record>')
    for col in columns:
      # Escape XML special characters
      value = str(record[col]).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
      lines.append(f'    <{col}>{value}</{col}>')
    lines.append('  </record>')
  lines.append('</records>')
  return "\n".join(lines)


def format_as_yaml(records: list, columns: list) -> str:
  """Format records as YAML list."""
  lines = []
  for record in records:
    first = True
    for col in columns:
      prefix = "- " if first else "  "
      first = False
      lines.append(f'{prefix}{col}: "{record[col]}"')
  return "\n".join(lines)


def format_as_toml(records: list, columns: list) -> str:
  """Format records as TOML array of tables."""
  lines = []
  for record in records:
    lines.append('[[records]]')
    for col in columns:
      # Escape TOML strings
      value = str(record[col]).replace('\\', '\\\\').replace('"', '\\"')
      lines.append(f'{col} = "{value}"')
    lines.append('')
  return "\n".join(lines)


def main():
  parser = argparse.ArgumentParser(description="Generate test data for extraction benchmark")
  parser.add_argument("--instance-path", required=True, help="Path to test instance folder")
  args = parser.parse_args()
    
  instance_path = Path(args.instance_path)
  config_path = instance_path / "test-config.json"
    
  if not config_path.exists():
    print(f"ERROR: Config not found: {config_path}")
    sys.exit(1)
    
  # Load config (with template inheritance)
  template_path = instance_path.parent / "test-config-template.json"
  config = {}
  if template_path.exists():
    with open(template_path, "r", encoding="utf-8") as f:
      config = json.load(f)
    
  with open(config_path, "r", encoding="utf-8") as f:
    instance_config = json.load(f)
    
  # Deep merge instance over template
  def deep_merge(base, override):
    result = base.copy()
    for key, value in override.items():
      if key in result and isinstance(result[key], dict) and isinstance(value, dict):
        result[key] = deep_merge(result[key], value)
      else:
        result[key] = value
    return result
    
  config = deep_merge(config, instance_config)
    
  # Extract parameters
  num_rows = config["data_generation"]["number_of_rows"]
  num_cols = config["data_generation"]["number_of_columns"]
  seed = config["data_generation"].get("seed", 42)
  columns = config["extraction_task"]["columns_to_extract"]
  filters = config["extraction_task"]["filters"]
    
  # Ensure we have the right number of columns
  if len(columns) < num_cols:
    # Add more columns from ALL_COLUMNS
    available = [c for c in ALL_COLUMNS if c not in columns]
    columns = columns + available[:num_cols - len(columns)]
  columns = columns[:num_cols]
    
  # Set seed for reproducibility
  random.seed(seed)
    
  # Generate records
  print(f"Generating {num_rows} records with {len(columns)} columns...")
  records = [generate_record(i + 1, columns) for i in range(num_rows)]
    
  # Apply filters to get expected results
  matching = apply_filters(records, filters)
  expected_ids = [r["id"] for r in matching]
    
  print(f"Filters matched {len(matching)} records")
    
  # Create output directory
  output_dir = instance_path / "01_InputData"
  output_dir.mkdir(parents=True, exist_ok=True)
    
  # Get output format from config (default: csv)
  output_format = config["data_generation"].get("output_format", "csv")
  
  # Format mapping: format_name -> (formatter_function, file_extension)
  FORMAT_MAP = {
    "csv": (format_as_csv_raw, "csv"),     # Regular CSV (QUOTE_MINIMAL)
    "csv_quoted": (format_as_csv, "csv"),  # Quoted CSV (Test 01 baseline, QUOTE_ALL)
    "kv_colon_space": (format_as_kv_colon_space, "txt"),
    "markdown_table": (format_as_markdown_table, "md"),
    "json": (format_as_json, "json"),
    "xml": (format_as_xml, "xml"),
    "yaml": (format_as_yaml, "yaml"),
    "toml": (format_as_toml, "toml"),
  }
  
  if output_format not in FORMAT_MAP:
    print(f"ERROR: Unknown output format '{output_format}'. Supported: {list(FORMAT_MAP.keys())}")
    sys.exit(1)
  
  formatter, ext = FORMAT_MAP[output_format]
  data_content = formatter(records, columns)
  data_path = output_dir / f"data.{ext}"
  
  with open(data_path, "w", encoding="utf-8") as f:
    f.write(data_content)
    
  print(f"Wrote {output_format}: {data_path}")
    
  # Estimate token count for prompt
  token_estimate = estimate_tokens(data_content) + 500  # Add prompt overhead
    
  # Write ground truth
  ground_truth = {
    "filters_applied": filters,
    "columns_requested": columns,
    "expected_records": matching,
    "expected_count": len(matching),
    "expected_ids": expected_ids,
    "token_estimate": token_estimate
  }
    
  gt_path = output_dir / "ground_truth.json"
  with open(gt_path, "w", encoding="utf-8") as f:
    json.dump(ground_truth, f, indent=2, ensure_ascii=False)
    
  print(f"Wrote ground truth: {gt_path}")
  print(f"Token estimate: ~{token_estimate}")
  print("OK.")


if __name__ == "__main__":
  main()
