<DevSystem MarkdownTablesAllowed=true />

# INFO: TQA-Bench Format Comparison Results

**Doc ID**: TQAB-IN03
**Goal**: Document serialization format evaluation results (Markdown vs CSV) and compare with our findings
**Strategy**: MCPI (exhaustive)
**Domain**: SOFTWARE

## Summary

TQA-Bench Experiment 1 compares Markdown and CSV serialization across 5 models at multiple context lengths. **Markdown consistently outperforms CSV** across most models and context sizes. GPT-4o achieves 78.7% (Markdown) vs 72.96% (CSV) at 8K - a 5.74 percentage point advantage. This finding partially validates our Test 02 results (format matters significantly), though the magnitude and direction differ from some of our format pairs.

## CRITICAL CORRECTION TO INITIAL SURVEY

Our `_INFO_BenchmarkSurvey.md` states under TQA-Bench:
> "Tests FORMAT?: No - uses fixed serialization (likely markdown or linearized tables)"

**This is WRONG.** TQA-Bench explicitly tests Markdown vs CSV in Experiment 1 (Section 4.1 of paper). The benchmark DOES test format as a variable, just not as the primary focus - they select the best format (Markdown) for subsequent experiments.

## Models Tested in Format Comparison

5 models used in Experiment 1:

- GPT-4o (closed-source, 128K context)
- GPT-4o-mini (closed-source, 128K context)
- Qwen2.5-7B-Instruct (open-source, 128K context)
- Qwen2.5-Coder-7B-Instruct (open-source, 128K context)
- Llama3.1-8B-Instruct (open-source, 128K context)

## Key Results

### Overall Accuracy (Markdown vs CSV) at 8K tokens

| Model                       | Markdown EM | CSV EM  | Difference |
|-----------------------------|-------------|---------|------------|
| GPT-4o                      | 78.7%       | 72.96%  | +5.74pp    |
| GPT-4o-mini                 | ~similar    | slightly better in specific contexts | varies |

[VERIFIED] (TQAB-SC-EMIND-TOPIC | numerical results)
[VERIFIED] (TQAB-SC-ARXIV-PAPER | Section 4.1)

Note: GPT-4o-mini was the ONLY model showing slightly better CSV accuracy in specific context lengths. All other models preferred Markdown.

### Qualitative Findings from Paper

1. **Markdown > CSV across majority of LLMs** - consistent preference
2. **Even for long-context tables, Markdown remains preferred** - advantage persists at scale
3. **Coder models perform better with CSV** than their non-coder counterparts (likely due to CSV exposure in code SFT data)
4. **But even coder models still prefer Markdown overall** - the CSV boost for coders is insufficient to overcome Markdown's general advantage
5. **Probable explanation**: Markdown tables more common in pre-training data corpus

[VERIFIED] (TQAB-SC-ARXIV-PAPER | Section 4.1 detailed discussion)

### Paper's Conclusion on Format

> "Given these results, we conclude that Markdown is the superior format for table serialization for LLMs in Multi-Table QA tasks."

All subsequent experiments use Markdown exclusively.

## Comparison with Our Format Research (Test 02)

### Agreements

- **Format significantly affects performance** - both studies confirm format is not neutral
- **Markdown performs well** - in our tests, markdown_pipe (simplified) ranks high for most models

### Differences

| Aspect              | TQA-Bench                        | Our Test 02                              |
|---------------------|----------------------------------|------------------------------------------|
| Formats tested      | 2 (Markdown, CSV)                | 6 (CSV quoted/unquoted, JSON, XML, Markdown, YAML, HTML) |
| Format difference   | ~5.7pp at 8K                     | Up to 5.8x scale difference              |
| Best format         | Markdown (always)                | Varies by model and metric               |
| CSV variant         | Unquoted (pandas default)        | Both quoted and unquoted                  |
| Task type           | Multi-table QA (MCQ)             | Single-table extraction (exact match)    |
| JSON tested?        | No (explicitly excluded as "less efficient for long tables") | Yes (often best for structured extraction) |

### Critical Differences in Methodology

1. **TQA-Bench uses pandas `to_markdown()`**: Produces pipe-delimited table with separator row. This is equivalent to our `markdown_pipe` format.
2. **TQA-Bench uses pandas `to_csv()`**: Produces standard CSV without quoting (pandas default). This is closest to our `csv_unquoted` format.
3. **They excluded JSON**: Paper states "selected for their standardization and efficiency in handling long tables, as opposed to JSON." This means they hypothesized JSON is WORSE for long tables but did not test it.
4. **No YAML, XML, or HTML tested**: Our research covers significantly more format space.

### Hypotheses Generated

- **H1**: If Markdown outperforms CSV for multi-table QA, does the same hold for single-table extraction? (Our data can answer this)
- **H2**: Would JSON outperform both Markdown and CSV for TQA-Bench tasks? (Their assumption may be wrong - our data shows JSON often wins for structured extraction)
- **H3**: Does the coder-model CSV advantage extend to our extraction tasks with reasoning models?
- **H4**: Is the format advantage model-size-dependent? (TQA-Bench only tests 7B-8B open-source models in format experiment)

## Serialization Implementation Detail

From `benchmarkUtils/database.py`:

```python
def defaultSerialization(self, markdown=False):
    tables = self.initDataFrame()
    tableList = []
    for k, v in tables.items():
        if markdown:
            tableList.append(f'## {k}\n\n{v.to_markdown(index=False)}')
        else:
            tableList.append(f'## {k}\n\n{v.to_csv(index=False)}')
    return '\n\n'.join(tableList)
```

[VERIFIED] (TQAB-SC-GH-DBPY | defaultSerialization method)

**Key observations**:
- Tables separated by `\n\n`
- Each table prefixed with `## table_name\n\n`
- No schema information provided (no CREATE TABLE or column types)
- Index excluded (`index=False`)
- Multiple tables concatenated in sequence

## Limitations of TQA-Bench Format Test

1. **Only 2 formats**: Misses JSON (often best for extraction), YAML (compact), XML (explicit structure)
2. **No format x scale interaction analysis**: Did they test format effect at EACH scale? Paper implies yes ("even for long-context tables") but detailed per-scale data for all models not fully reported
3. **Format chosen BEFORE comprehensive model testing**: Only 5 models used for format selection, then 22 models tested with Markdown only. The format preference might differ for other architectures.
4. **No reasoning models tested**: All models are pre-reasoning era (GPT-4o, not gpt-5/o1/o3)
5. **MCQ evaluation**: 25% random baseline means format differences are compressed compared to exact-match evaluation

## Document History

**[2026-05-22 13:35]**
- Initial creation with format comparison results and cross-analysis with our research
