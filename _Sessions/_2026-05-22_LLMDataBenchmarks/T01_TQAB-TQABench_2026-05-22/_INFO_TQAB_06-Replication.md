# INFO: TQA-Bench Replication Guide

**Doc ID**: TQAB-IN05
**Goal**: Document how to replicate and adapt TQA-Bench for our research pipeline
**Strategy**: MCPI (exhaustive)
**Domain**: SOFTWARE

## Summary

TQA-Bench is fully open-source (GPL-3.0) with public datasets and straightforward API integration. Replication requires downloading task/database files from OneDrive, installing Python dependencies, and running model-specific scripts. The code supports both Markdown and CSV serialization via a boolean flag. Adaptation for our pipeline is feasible - we can inject additional formats, add reasoning models, and extend the scale range.

## Prerequisites

- Python 3.x
- OpenAI API key (for GPT-4o/mini evaluation)
- SQLite3 (included in Python stdlib)
- pandas (for DataFrame serialization)
- torch (for BenchmarkDataset class, but not needed for API-based evaluation)
- tqdm (progress bars)

## Dataset Download

### Task File

- **URL**: https://hkustconnect-my.sharepoint.com/:u:/g/personal/zqiuao_connect_ust_hk/EWAnhWoIhJpIgkkge1ZoBoYB7eF1AgJbcfV4nDfpFLua4A?e=727pOz
- **Place in**: `symDataset/tasks/TableQA/`
- **Content**: `dataset.sqlite` containing questions for 10 databases

### Scaled Database Files

- **URL**: https://hkustconnect-my.sharepoint.com/:u:/g/personal/zqiuao_connect_ust_hk/ESGMS0lh1l9MirS9SvS7_E0BSpBXpml7OsCdc0oLx70b_A?e=AgHy9i
- **Place in**: `symDataset/scaledDB/` (unzip)
- **Content**: Pre-sampled databases at 8K, 16K, 32K, 64K scales (10 instances each)

### Data Structure After Download

```
symDataset/
├── tasks/TableQA/
│   └── dataset.sqlite       # Questions (140 templates x 10 instances x 4 scales)
├── scaledDB/
│   ├── 8k/
│   │   ├── airline/
│   │   │   ├── airline_0.sqlite  # Instance 0
│   │   │   ├── airline_1.sqlite  # Instance 1
│   │   │   └── ...              # Through instance 9
│   │   ├── california_schools/
│   │   └── ...                  # 10 databases total
│   ├── 16k/
│   ├── 32k/
│   └── 64k/
└── results/TableQA/            # Output directory (created by scripts)
```

## Running Evaluation

### Minimal Example (GPT-4o)

```python
# From repository root
import sys
sys.path.append(".")
from symbolic import dataDict
from symDataloader.utils import TaskCore
from benchmarkUtils.LLM import gptCall
from benchmarkLoader import singlePrompt

def qaPrompt(dbStr, question, choices):
    totalQuestion = f"{dbStr}\n\n{question}\n\n{choices}"
    return singlePrompt.format(question=totalQuestion)

def gpt4oCall(dbStr, question, choices):
    prompt = qaPrompt(dbStr, question, choices)
    return gptCall("gpt-4o", prompt, "tmp", "symDataset/results/TableQA/log")

# Initialize
tc = TaskCore(
    dbRoot="symDataset/scaledDB",
    taskPath="symDataset/tasks/TableQA/dataset.sqlite",
    resultPath="symDataset/results/TableQA/4o.sqlite"
)

# Run for single database, single scale
tc.testAll(
    model="gpt-4o",
    dbn="airline",           # database name
    scale="8k",              # 8k, 16k, 32k, 64k
    markdown=True,           # True=Markdown, False=CSV
    dbLimit=5,               # number of database instances (max 10)
    sampleLimit=1,           # samples per instance (max 10)
    questionLimit=14,        # questions per sample (max 14)
    callFunc=gpt4oCall,
    timeSleep=0              # seconds between API calls
)
```

[VERIFIED] (TQAB-SC-GH-GPT4O | gpt4o.py)

### Key Parameters

- `dbLimit=5`: Use 5 of 10 database instances (sufficient per paper's sensitivity analysis)
- `sampleLimit=1`: 1 sample per instance (1 is sufficient per paper)
- `questionLimit=14`: All 14 question types (7 subcategories x 2 templates)
- `markdown=True/False`: Toggle serialization format
- `timeSleep`: Rate limiting (30s for 16K, 60s for 32K recommended)

### Cost Estimate

Per model, per format, all scales:
- 10 databases x 5 instances x 1 sample x 14 questions x 4 scales = 2,800 API calls
- At 8K-64K tokens per call: ~70M-280M input tokens total
- GPT-4o cost: roughly $100-400 depending on scale distribution

## Adaptation Opportunities for Our Research

### 1. Add More Serialization Formats

Modify `benchmarkUtils/database.py`:

```python
def defaultSerialization(self, format_type='markdown'):
    tables = self.initDataFrame()
    tableList = []
    for k, v in tables.items():
        if format_type == 'markdown':
            tableList.append(f'## {k}\n\n{v.to_markdown(index=False)}')
        elif format_type == 'csv':
            tableList.append(f'## {k}\n\n{v.to_csv(index=False)}')
        elif format_type == 'json':
            tableList.append(f'## {k}\n\n{v.to_json(orient="records", indent=2)}')
        elif format_type == 'xml':
            tableList.append(f'## {k}\n\n{v.to_xml(index=False)}')
        # ... add YAML, HTML, etc.
    return '\n\n'.join(tableList)
```

### 2. Add Reasoning Models

Create new dataloader script (e.g., `symDataloader/gpt5.py`):
- Replace `gptCall("gpt-4o", ...)` with `gptCall("gpt-5", ...)`
- Add reasoning effort parameter if supported by wrapper
- May need to handle extended thinking tokens in cost calculation

### 3. Extend Scale Range

The 128K source data exists but is not included in the standard download. Contact authors or regenerate using the sampling code. Could also test 128K and 200K with Llama/Claude.

### 4. Binary Search Adaptation

Instead of fixed buckets, use their row-sampling mechanism with our binary search:
1. Start at known-good row count
2. Double until accuracy drops below threshold
3. Binary search for exact breaking point
4. Report maximum rows per model/format/question-type

## Limitations for Replication

- **OneDrive hosting**: Dataset links may expire. No DOI or permanent archive.
- **No requirements.txt**: Dependencies must be inferred from imports
- **Chinese comments**: Code comments primarily in Chinese (database.py)
- **No explicit version pinning**: pandas `to_markdown()` output may differ across versions
- **GPL-3.0 license**: Copyleft - any derivative must also be GPL-3.0

## Document History

**[2026-05-22 13:38]**
- Initial creation with replication instructions from code analysis
