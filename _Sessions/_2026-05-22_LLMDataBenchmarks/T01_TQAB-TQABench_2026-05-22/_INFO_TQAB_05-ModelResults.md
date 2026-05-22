<DevSystem MarkdownTablesAllowed=true />

# INFO: TQA-Bench Model Results by Scale

**Doc ID**: TQAB-IN04
**Goal**: Document comprehensive LLM evaluation results across context scales and model categories
**Strategy**: MCPI (exhaustive)
**Domain**: SOFTWARE

## Summary

22 LLMs evaluated on TQA-Bench using Markdown serialization. GPT-4o leads at all scales (78.7% at 8K, 63.4% at 64K). Performance universally degrades with context length. Chat models score below 25% (MCQ random baseline). Instruct models scale with parameters. Table-specialized models (TableLlama, TableGPT2) underperform expectations. No reasoning models (o1, o3, gpt-5) were tested.

## Top-Performing Models (Exact Match %)

### Scale Degradation - Best Models

| Model               | 8K    | 16K   | 32K   | 64K   | Drop (8K→64K) |
|---------------------|-------|-------|-------|-------|----------------|
| GPT-4o              | 78.7% | ~72%  | ~68%  | 63.4% | -15.3pp (19%)  |
| Llama3.1-70B        | 62.9% | ~57%  | ~52%  | 47.9% | -15.0pp (24%)  |
| Qwen2.5-14B         | 59.4% | ~53%  | ~47%  | 41.3% | -18.1pp (30%)  |
| GPT-4o-mini         | ~65%  | ~60%  | ~55%  | ~50%  | ~15pp          |

[VERIFIED] (TQAB-SC-EMIND-TOPIC | numerical results)

Note: Values marked with `~` are interpolated from paper figures. Exact values from Table 6 in paper (not fully extractable from HTML).

## Model Categories and Performance Patterns

### Closed-Source Models (Instruct)

- **GPT-4o**: Best overall. 78.7% at 8K, degrades to 63.4% at 64K. Supports 128K context.
- **GPT-4o-mini**: Strong second. Slightly below GPT-4o. Only model with marginal CSV advantage in specific contexts.

### Open-Source Instruct Models

Performance correlates with parameter count:

| Model                       | Params | 8K EM  | Context Limit |
|-----------------------------|--------|--------|---------------|
| Qwen2.5-72B-Instruct       | 72B    | ~65%   | 128K          |
| Llama3.1-70B-Instruct      | 70B    | 62.9%  | 128K          |
| Gemma2-27B-Instruct        | 27B    | ~50%   | 8K only       |
| Qwen2.5-14B-Instruct       | 14B    | 59.4%  | 128K          |
| Mistral-Nemo-Instruct      | 12.2B  | ~40%   | 128K          |
| Gemma2-9B-Instruct         | 9B     | ~45%   | 8K only       |
| Qwen2.5-7B-Instruct        | 7B     | ~45%   | 128K          |
| Qwen2.5-Coder-7B-Instruct  | 7B     | ~47%   | 128K          |
| Llama3.1-8B-Instruct       | 8B     | ~42%   | 128K          |
| Mistral-7B-Instruct        | 7B     | ~35%   | 32K           |
| Qwen2.5-3B-Instruct        | 3B     | ~35%   | 128K          |
| Gemma2-2B-Instruct         | 2B     | ~30%   | 8K only       |

[VERIFIED] (TQAB-SC-ARXIV-PAPER | Section 4.2)

### Chat Models (Poor Performance)

All below 25% overall accuracy (at or below MCQ random baseline):

- Baichuan2-7B-Chat, Baichuan2-13B-Chat
- Vicuna-7B-V1.5-16K, Vicuna-13B-V1.5-16K
- GLM-4-9B-Chat (slightly better, can follow instructions)

**Failure mode**: Produce "I don't know", "None of the above", or multi-answer responses. Cannot follow MCQ format.

**Interesting pattern**: Larger chat models perform WORSE (Baichuan2-13B < Baichuan2-7B). Larger models produce verbose analyses or "None of the above" while smaller ones occasionally produce parseable multi-choice answers.

[VERIFIED] (TQAB-SC-ARXIV-PAPER | Section 4.2 Chat LLM Performance)

### Table-Specialized Models (Disappointing)

- **TableLlama** (7B, 8K context): Failed to follow answer format entirely. Specialized fine-tuning narrowed focus.
- **TableGPT2** (7B, 128K context): Average performance only. Trained mostly on Chinese corpora. Can follow format better than TableLlama.

[VERIFIED] (TQAB-SC-ARXIV-PAPER | Section 4.2 Domain-Specific Table LLMs)

### MoE Models

- **DeepSeek-V2-Lite-Chat** (15.7B, 32K): Below 25% accuracy. Chat model limitations. Also hit 16K tokenizer warning despite 32K advertised support.

## Performance by Task Subcategory

Performance decay varies by task complexity (as context length increases):

### Lookup Tasks (Slowest Decay)

- **EL (Entity Lookup)**: Relatively manageable even at long context. Only requires retrieving single/few items.
- **TS (Top Selection)**: More complex but still decays slowly.

### Aggregation Tasks (Moderate Decay)

- **CNT (Count)**: Moderate performance drop
- **AVG (Average)**: Better than SUM (estimating average is more intuitive)
- **SUM (Sum)**: Pronounced drop (summing many elements accurately is demanding)

### Complex Calculation (Fastest Decay)

- **CS (Composite Subtraction)**: Relatively preserved (some instances only require simple retrieval + subtraction)
- **COR (Correlation)**: Significant drop. Requires both complex numerical computation AND logical reasoning.

**Key insight**: COR drops below 20% EM for open-source models at large context lengths.

[VERIFIED] (TQAB-SC-ARXIV-PAPER | Section 4.2 Influence of Context Length)

## Comparison with Our Scale Degradation Findings

### TQA-Bench vs Our Test 01 (CSV Scale Limits)

| Metric                    | TQA-Bench GPT-4o          | Our gpt-5 (high effort)    |
|---------------------------|----------------------------|-----------------------------|
| Task type                 | Multi-table QA (MCQ)       | Single-table extraction     |
| Degradation pattern       | Linear decline 8K→64K      | Binary cliff (works/fails)  |
| Scale at 100% accuracy    | N/A (never 100%)           | ~500 rows (CSV)            |
| Performance at max scale  | 63.4% at 64K               | 0% beyond breaking point   |
| Format                    | Markdown only              | 6 formats tested           |

### Key Differences in Degradation Pattern

1. **TQA-Bench shows gradual decline**: 78.7% → 63.4% over 8x scale increase. No cliff.
2. **Our tests show binary cliff**: Near-100% accuracy up to a threshold, then rapid failure.
3. **Explanation**: MCQ format provides 25% random floor + partial credit from simpler subtasks. Our exact-match extraction has no partial credit - either correct or not.

### Implications

- The 15pp degradation (8K→64K) in TQA-Bench likely masks much larger degradation for specific subtasks (COR shows this)
- For reasoning-intensive tasks (COR), the degradation pattern may be closer to our binary cliff
- **Missing**: No reasoning model (o1, o3, gpt-5) results. Would these show different degradation curves?

## Models NOT Tested (Gap for Our Research)

The following model families are absent from TQA-Bench results:

- **OpenAI reasoning models**: o1, o1-mini, o3, o3-mini, gpt-5, gpt-5-mini
- **Anthropic models**: Claude 3.5 Sonnet, Claude 3 Opus, Claude 3.5 Haiku (any version)
- **Anthropic thinking models**: Claude with extended thinking
- **Google**: Gemini 1.5 Pro/Flash

This is the most significant gap - TQA-Bench was published November 2024, before reasoning models became widely available. Our research fills this gap with gpt-5 family and Claude thinking model data.

## Document History

**[2026-05-22 13:37]**
- Initial creation with model results extracted from paper and EmergentMind summary
