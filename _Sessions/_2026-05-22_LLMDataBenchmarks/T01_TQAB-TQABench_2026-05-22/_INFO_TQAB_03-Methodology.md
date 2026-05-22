<DevSystem MarkdownTablesAllowed=true />

# INFO: TQA-Bench Methodology

**Doc ID**: TQAB-IN02
**Goal**: Document TQA-Bench benchmark construction, task taxonomy, and evaluation protocol
**Strategy**: MCPI (exhaustive)
**Domain**: SOFTWARE

## Summary

TQA-Bench is a multi-table QA benchmark evaluating LLMs on relational database reasoning at scale (8K-64K tokens). It uses 10 real-world databases from WorldBank, DataGov, and BIRD, generates questions via symbolic template extension (140 templates producing 1400+ instances), and evaluates using multiple-choice format with exact match scoring. The benchmark uniquely combines scalable context length, multi-table foreign key relationships, and symbolic extensions to prevent memorization.

## Benchmark Construction Pipeline

4 phases:

1. **Multi-Table Data Collection** - 10 databases from 3 sources (WorldBank, DataGov, BIRD)
2. **Sampling to Variate Context-Length** - Topological sort + row sampling preserving referential integrity
3. **Evaluation Task Categories** - 3 categories, 7 subcategories
4. **Question Generation with Symbolic Extension** - Template-based MCQ generation with Python answer verification

## Data Sources

- **WorldBank** (1 database): Large-scale real-world tabular data with foreign key relationships, tables with 100K+ rows
- **DataGov** (2 databases): Water Quality Data, Food Facility Inspections - large tables with numerous rows/columns
- **BIRD** (7 databases): Text2SQL benchmark databases with complex foreign key relationships. Filtered to 7 from 20 valid (of total set) requiring referential integrity and acyclic FK graphs

[VERIFIED] (TQAB-SC-ARXIV-PAPER | Section 2.1)

## Context Length Scaling Method

**Method**: Binary search over row sampling parameter `k` to approximate target token count.

**Process**:
1. Determine topological order of tables based on foreign key relationships (DAG requirement)
2. For tables without incoming references: ordered sampling of `k` rows directly
3. For referenced tables: sampling guided by topological order, respecting FK constraints
4. Serialize to Markdown format, calculate token count
5. Binary search adjusts `k` until target context length reached

**Scale levels**: 8K, 16K, 32K, 64K tokens (sampled from 128K source)
**Instances per scale**: 10 different database instances per original database, 10 sample instances each (indexed 0-9)

[VERIFIED] (TQAB-SC-ARXIV-PAPER | Section 2.2)

**Critical observation**: This is effectively a binary search for scale, but applied to DATA SIZE (row count) rather than to MODEL CAPABILITY. Our binary search finds the maximum rows a model can handle correctly; TQA-Bench pre-defines fixed scale buckets and measures accuracy at each.

## Task Taxonomy

### Category 1: Lookup

- **EL (Entity Lookup)**: Retrieve a specific value based on given conditions. Cross-table reference resolution required.
- **TS (Top Selection)**: Identify top-N entities by a criterion across joined tables. Multi-step: resolve FK, aggregate, select max.

### Category 2: Aggregation

- **CNT (Count)**: Total rows satisfying a condition across tables
- **SUM (Sum)**: Compute sum of numerical attribute across filtered rows
- **AVG (Average)**: Calculate mean of numerical column for matching rows

### Category 3: Complex Calculation

- **CS (Composite Subtraction)**: Difference between two values (direct or derived through intermediate calculations)
- **COR (Correlation)**: Statistical correlation coefficient between two filtered columns

[VERIFIED] (TQAB-SC-ARXIV-PAPER | Section 2.3)

## Question Generation (Symbolic Extension)

Inspired by GSM-Symbolic framework:

- **Templates**: 2 per subcategory per database = 140 total template questions
- **Variables**: Placeholder variables instead of fixed values, instantiated dynamically
- **Answer generation**: Python code computes correct answer deterministically
- **MCQ format**: 4 choices (A/B/C/D)
- **Error choice generation**:
  - Entity tasks: random cells from same column
  - Numerical tasks: correct answer multiplied by 0.25, 2.0, 3.0
- **Scale**: 10 database instances x 10 question batches per template = hundreds of unique instances per scale

[VERIFIED] (TQAB-SC-ARXIV-PAPER | Section 2.4)

## Evaluation Protocol

### Prompt Template

```text
Please carefully analyze and answer the following single choice question step by step.

{serialized_tables}

{question}

{choices}

This question has only one correct answer. Please break down the question, evaluate each option, and explain why it is correct or incorrect. Conclude with your final choice on a new line formatted as `Answer: A/B/C/D`.
```

[VERIFIED] (TQAB-SC-GH-PROMPT | singleChoicePrompt.txt)

### Answer Extraction

Regex pattern: `r"answer:\s*([A-F]+)"` (case-insensitive, takes last match)

[VERIFIED] (TQAB-SC-GH-UTILS | extractAnswer function)

### Metric

**Exact Match (EM)**: `|CorrectAnswers| / |TotalQuestions|`

No partial credit. MCQ format chosen over BLEU/ROUGE/F1 for direct reasoning assessment.

## Serialization Formats Tested

Two formats compared in Experiment 1:

### Markdown Format

```markdown
## table_name

| col1 | col2 | col3 |
|------|------|------|
| val1 | val2 | val3 |
```

Generated by: `pandas.DataFrame.to_markdown(index=False)` with `## {table_name}` header

### CSV Format

```csv
## table_name

col1,col2,col3
val1,val2,val3
```

Generated by: `pandas.DataFrame.to_csv(index=False)` with `## {table_name}` header

[VERIFIED] (TQAB-SC-GH-DBPY | defaultSerialization method)

**Critical finding**: Both formats use the SAME `## table_name` header. The only difference is the table body serialization (pipe-delimited markdown table vs comma-separated CSV).

## Code Architecture

```
TQA-Bench/
├── benchmarkLoader/         # Data loading, prompt templates
│   └── prompts/             # singleChoicePrompt.txt, multiChoicePrompt.txt
├── benchmarkUtils/          # DB class (serialization), LLM API wrappers
│   ├── database.py          # Serialization (markdown/csv), sampling, FK handling
│   └── LLM.py              # gptCall and other API wrappers
├── symDataloader/           # Model-specific evaluation scripts
│   ├── gpt4o.py            # GPT-4o evaluation
│   └── utils.py            # TaskCore class (result storage, answer extraction)
├── symAnalysis/             # Result analysis scripts
│   ├── format_evaluation.py # Markdown vs CSV comparison
│   ├── overall.py          # Overall results
│   └── sensitive.py        # Sensitivity analysis
├── symbolic/                # Symbolic extension templates
├── symWorkflow/             # Workflow orchestration
└── dataset/task/            # Task definitions
```

[VERIFIED] (TQAB-SC-GH-REPO | repository structure)

## Result Storage

SQLite database with schema:

```sql
CREATE TABLE {database_name} (
    model TEXT,
    scale TEXT,
    markdown INTEGER,     -- 0=CSV, 1=Markdown
    dbidx INTEGER,        -- 0-9
    sampleidx INTEGER,    -- 0-9
    questionidx INTEGER,  -- 0-13
    gt TEXT,              -- ground truth answer
    pred TEXT,            -- model prediction
    correct INTEGER,      -- 0 or 1
    error TEXT,
    message TEXT,
    PRIMARY KEY (model, scale, markdown, dbidx, sampleidx, questionidx)
);
```

[VERIFIED] (TQAB-SC-GH-UTILS | TaskCore class)

## Relevance to Our Research

### Direct Comparisons

| Dimension          | TQA-Bench                    | Our Research (TBLF)           |
|--------------------|------------------------------|-------------------------------|
| Format test        | Markdown vs CSV              | 6 formats (CSV, JSON, XML, Markdown, YAML, HTML) |
| Scale method       | Fixed buckets (8K-64K)       | Binary search for exact limit |
| Task type          | Multi-table QA (MCQ)         | Single-table extraction       |
| Ground truth       | Python-computed MCQ answers   | Exact field extraction match  |
| Effort variable    | Not tested                   | Low/Medium/High reasoning     |
| Models             | GPT-4o/mini, open-source     | gpt-5, gpt-5-mini, Claude    |
| Context range      | 8K-64K tokens                | Up to 128K+ tokens           |

### Key Methodological Differences

1. **Our binary search vs their fixed buckets**: We find the EXACT breaking point; they measure accuracy AT predetermined sizes
2. **Our single-table extraction vs their multi-table QA**: Different cognitive tasks - ours tests pure data extraction, theirs tests relational reasoning
3. **Their format test only compares 2 formats**: Markdown and CSV. We test 6 formats including JSON, XML, YAML, HTML
4. **Their MCQ vs our exact extraction**: MCQ has 25% random baseline; our extraction has 0% random baseline

## Document History

**[2026-05-22 13:33]**
- Initial creation from paper HTML, GitHub code, and EmergentMind summary
