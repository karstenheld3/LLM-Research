<DevSystem MarkdownTablesAllowed=true />

# INFO: NoLiMa Benchmark Deep-Research Summary

**Doc ID**: NOLIMA-IN01
**Goal**: Exhaustive research on NoLiMa benchmark methodology, model results, and relevance to our tabular data format research
**Strategy**: MCPI (exhaustive)
**Domain**: SOFTWARE
**Research stats**: 25m net | 6 sources | 22 models analyzed
**Sources accessed**: 2026-05-22

## Table of Contents

1. Research Question
2. Key Findings
3. Topic Files
4. Comparison with Our Research
5. Recommended Actions
6. Document History

## Research Question

How does the NoLiMa benchmark (Long-Context Evaluation Beyond Literal Matching) relate to our tabular data format research? What can its methodology and results teach us about why format optimization works and what its limits are?

## Key Findings

1. **NoLiMa proves attention relies on literal cues**: Models that ace standard NIAH (literal matching) collapse when literal overlap is removed. This directly explains why our format optimization works - formats create structural "literal cues" that guide attention. [VERIFIED] (NOLIMA-SC-ARXIV-HTML)

2. **GPT-4.1 achieves best non-reasoning effective length (16K)**: Significant improvement over GPT-4o (8K). Should be tested in our pipeline. [VERIFIED] (NOLIMA-SC-GH-README)

3. **Reasoning helps but doesn't solve**: GPT-o3 leads at 58.5% at 32K on NoLiMa-Hard, but still loses 41.5pp from base score. Even the strongest reasoning model cannot fully overcome attention limitations. [VERIFIED] (NOLIMA-SC-GH-README)

4. **Claimed context length is meaningless**: Llama 4 Scout claims 10M tokens but has 1K effective length on NoLiMa. All models tested have effective length at most 16K regardless of claims. [VERIFIED] (NOLIMA-SC-GH-README)

5. **Mini/small models collapse rapidly**: GPT-4o mini, GPT-4.1 Nano, Gemma 3 4B all fail below 1K effective length. Size is critical for maintaining attention at scale. [VERIFIED] (NOLIMA-SC-GH-README)

6. **5 testable hypotheses derived**: Format markers as attention cues, effort-context interaction, distractor effects, cross-model correlation with our results, NoLiMa effective length as predictor. See `_INFO_NOLIMA_07-Relevance.md`.

7. **Full dataset and code publicly available**: HuggingFace dataset + GitHub evaluation code. Adobe Research License (non-commercial). Fully replicable with our API-based setup. [VERIFIED] (NOLIMA-SC-HF-DATA)

## Topic Files

| # | File | Description | Status |
|---|------|-------------|--------|
| 01 | `_INFO_NOLIMA_01-SUMMARY.md` | This file | Complete |
| 02 | `_INFO_NOLIMA_02-SOURCES.md` | Source list (6 sources) | Complete |
| 03 | `_INFO_NOLIMA_03-Methodology.md` | Detailed methodology, evaluation protocol, replication | Complete |
| 04 | `_INFO_NOLIMA_04-ResultsOpenAI.md` | OpenAI model results (GPT-4o/4.1 family + o1/o3) | Complete |
| 05 | `_INFO_NOLIMA_05-ResultsReasoning.md` | All reasoning model results + CoT analysis | Complete |
| 06 | `_INFO_NOLIMA_06-ResultsOtherModels.md` | Anthropic, Google, Meta, Mistral, others | Complete |
| 07 | `_INFO_NOLIMA_07-Relevance.md` | Relevance to our research + 5 testable hypotheses | Complete |

## Comparison with Our Research

| Dimension              | NoLiMa                                      | Our TabularDataFormats                     |
|------------------------|---------------------------------------------|--------------------------------------------|
| Tests format?          | No (fixed natural language)                 | YES (independent variable)                 |
| Tests effort?          | Partial (reasoning models separate)         | YES (low/medium/high)                      |
| Tests scale?           | YES (250 to 128K tokens)                    | YES (binary search for limit)              |
| Input type             | Prose (book snippets)                       | Structured data (tables)                   |
| Task type              | World-knowledge association                 | Data extraction, filtering, aggregation    |
| Literal cues           | Explicitly removed                          | Inherently present (format markers)        |
| Scale finding          | Effective length 1K-16K                     | Extraction fails at <10% claimed window    |
| Reasoning finding      | Helps but doesn't solve                     | 10x improvement (effort low -> high)       |
| Mechanism              | Attention cannot find without literal cues  | Format optimization = attention optimization |

## Recommended Actions

1. **Run NoLiMa on gpt-5-mini/gpt-5** (immediate value, no existing results)
2. **Test GPT-4.1 in our pipeline** (best non-reasoning NoLiMa performer, not in our experiments)
3. **Design H1 experiment** (format degradation curves at multiple context lengths)
4. **Download and inspect NoLiMa dataset** (understand needle construction for adaptation)

## Document History

**[2026-05-22 13:33]**
- Initial creation: 7 topic files, 6 sources, 22 models documented, 5 hypotheses derived
