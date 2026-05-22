<DevSystem MarkdownTablesAllowed=true />

# INFO: TQA-Bench Deep Research Summary

**Doc ID**: TQAB-IN01
**Goal**: Exhaustive research on TQA-Bench benchmark for comparison with our tabular data format research
**Strategy**: MCPI (exhaustive)
**Domain**: SOFTWARE
**Research stats**: 25m net | 7 sources | 6 documents

## CRITICAL CORRECTION

Our initial survey (`_INFO_BenchmarkSurvey.md`) incorrectly states TQA-Bench does NOT test format. **TQA-Bench DOES test Markdown vs CSV** (Experiment 1, Section 4.1). Markdown consistently wins. This makes TQA-Bench the ONLY external benchmark we found that explicitly compares serialization formats for tabular data in LLMs.

## Key Findings

### 1. Format Comparison (Markdown vs CSV)

- **Markdown outperforms CSV** consistently across models: GPT-4o 78.7% vs 72.96% at 8K (+5.74pp)
- **Coder models show smaller gap** (CSV exposure in training data helps)
- **Effect persists at all context lengths** - not just a small-scale artifact
- **Only 2 formats tested** - no JSON, XML, YAML, HTML (our research covers 6 formats)

### 2. Scale Degradation

- GPT-4o: 78.7% (8K) → 63.4% (64K) - 19% relative decline
- Llama3.1-70B: 62.9% (8K) → 47.9% (64K) - 24% relative decline
- Qwen2.5-14B: 59.4% (8K) → 41.3% (64K) - 30% relative decline
- **Pattern**: Gradual decline, not binary cliff (unlike our results)

### 3. Task Difficulty Hierarchy

- Lookup > Aggregation > Complex Calculation (easiest to hardest)
- Correlation (COR) drops below 20% for open-source models at 64K
- Sum harder than Average (accumulation error vs estimation)

### 4. Model Hierarchy

- Closed-source (GPT-4o) > Large open-source (70B) > Medium (14B) > Small (7B)
- Chat models fail entirely (<25% = random baseline)
- Table-specialized models (TableLlama, TableGPT2) underperform general-purpose instruct models

### 5. No Reasoning Models Tested

- Paper predates reasoning model availability (November 2024)
- No o1, o3, gpt-5, Claude thinking models
- **This is the primary gap our research fills**

## Relevance Score: 9/10

TQA-Bench is highly relevant because:
- Tests format (Markdown vs CSV) - directly comparable to our Test 02
- Tests scale (8K-64K) - directly comparable to our Test 01
- Uses multi-table relational data - more complex than our single-table
- Has open code and data - fully replicable
- Missing reasoning models - we provide complementary data

## Hypotheses Generated

- **H1**: Markdown advantage for multi-table QA (TQA-Bench) may not hold for single-table extraction (our task). JSON may outperform both.
- **H2**: Reasoning models (gpt-5) would show flatter degradation curves than GPT-4o on TQA-Bench tasks.
- **H3**: Binary search on TQA-Bench tasks would reveal model-specific cliff points similar to our findings.
- **H4**: The format preference is task-dependent: Markdown for QA comprehension, JSON for extraction.
- **H5**: Coder model CSV advantage would amplify with reasoning effort (thinking models trained on more code).

## Topic Files

| # | File | Content |
|---|------|---------|
| 02 | `_INFO_TQAB_02-SOURCES.md` | 7 sources with verification status |
| 03 | `_INFO_TQAB_03-Methodology.md` | Benchmark construction, task taxonomy, code architecture |
| 04 | `_INFO_TQAB_04-FormatResults.md` | Markdown vs CSV detailed results + comparison with our findings |
| 05 | `_INFO_TQAB_05-ModelResults.md` | 22 models across 4 scales, performance patterns |
| 06 | `_INFO_TQAB_06-Replication.md` | How to run, adapt for our pipeline, cost estimates |

## Downloads

- **Paper PDF**: `../../Papers/2024-11-29_TQABench-EvaluatingLLMsForMultiTableQuestionAnsweringWithScalableContext_2411.19504v1.pdf`

Dataset files available at OneDrive links (see `_INFO_TQAB_02-SOURCES.md`):
- Task SQLite database (questions + ground truth)
- Scaled DB files (8K-64K pre-sampled instances)

Download links documented in `_DOWNLOADS_gitignore/README.md` (to be created when user downloads).

## Actionable Next Steps

1. **Correct `_INFO_BenchmarkSurvey.md`**: Update "Tests FORMAT?" from "No" to "YES (Markdown vs CSV)"
2. **Run TQA-Bench with gpt-5**: Unique contribution - first reasoning model results on this benchmark
3. **Add JSON/YAML/XML formats**: Fork their code, add our 6 formats, compare
4. **Apply binary search**: Replace fixed scale buckets with our adaptive method
5. **Cross-validate findings**: Compare GPT-4o format preference (Markdown > CSV) against our Test 02 data for same model

## Document History

**[2026-05-22 13:40]**
- Initial creation with cross-document synthesis from all topic files
