<DevSystem MarkdownTablesAllowed=true />

# INFO: NoLiMa Results - Anthropic, Google, Meta, and Other Models

**Doc ID**: NOLIMA-IN06
**Goal**: Document results for all non-OpenAI models on NoLiMa benchmark
**Sources**: NOLIMA-SC-GH-README (2025-07-17 update), NOLIMA-SC-ARXIV-HTML

## Summary

Non-OpenAI models on NoLiMa reveal a consistent pattern: effective context length is dramatically shorter than claimed length, typically 1K-4K regardless of model size or architecture. Claude 3.5 Sonnet achieves 4K effective length with a notably lower base score (87.6%) suggesting different architecture trade-offs. Google's Gemini models show varied results with 2.0 Flash reaching 4K but newer models (2.5 Flash w/o Thinking) only achieving 2K. Meta's Llama family peaks at 2K effective length even at 405B scale.

## Anthropic Models

| Model           | Claimed Length | Effective Length | Base Score (x0.85 Thr.) | 1K   | 2K   | 4K   | 8K   | 16K  | 32K  |
|-----------------|:-------------:|:---------------:|:-----------------------:|:----:|:----:|:----:|:----:|:----:|:----:|
| Claude 3.5 Sonnet | 200K        | 4K              | 87.6 (74.4)             | 85.4 | 84.0 | 77.6 | 61.7 | 45.7 | 29.8 |

### Observations - Anthropic

- **Only one Anthropic model tested** - significant gap in coverage
- **Lower base score** (87.6%) vs GPT-4o (99.3%) suggests Sonnet struggles with the associative reasoning task even at short context
- **But better length generalization profile**: At 4K still maintains 77.6% (above threshold)
- **Graceful degradation curve**: 87.6 -> 85.4 -> 84.0 -> 77.6 -> 61.7 -> 45.7 -> 29.8 (roughly linear decline)
- **No Claude 3.5 Opus, Claude 4, or thinking-mode Claude tested**
- **No Claude extended thinking results** - major gap for comparison with our research

### Missing Anthropic Data

- Claude 3.5 Opus (not available at paper time)
- Claude 4 / Claude 4.5 (released after paper)
- Claude with extended thinking / budget_tokens parameter
- Any Anthropic model on NoLiMa-Hard subset

## Google Models

| Model                        | Claimed Length | Effective Length | Base Score (x0.85 Thr.) | 1K   | 2K   | 4K   | 8K   | 16K  | 32K  | 64K  | 128K |
|------------------------------|:-------------:|:---------------:|:-----------------------:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|
| Gemini 2.5 Flash (w/o T)    | 1M            | 2K              | 94.4 (80.2)             | 90.1 | 86.1 | 79.4 | 68.2 | 57.9 | 48.4 | --   | --   |
| Gemini 1.5 Pro              | 2M            | 2K              | 92.6 (78.7)             | 86.4 | 82.7 | 75.4 | 63.9 | 55.5 | 48.2 | --   | --   |
| Gemini 2.0 Flash            | 1M            | 4K              | 89.4 (76.0)             | 87.7 | 87.5 | 77.9 | 64.7 | 48.2 | 41.0 | 33.0 | 16.4 |
| Gemini 1.5 Flash            | 1M            | <1K             | 84.7 (72.0)             | 68.6 | 61.6 | 51.0 | 44.4 | 35.5 | 28.6 | --   | --   |
| Gemma 3 27B                 | 128K          | <1K             | 88.6 (75.3)             | 73.3 | 65.6 | 48.1 | 32.7 | 20.2 | 9.5  | --   | --   |
| Gemma 3 12B                 | 128K          | 1K              | 87.4 (74.3)             | 74.7 | 61.8 | 39.9 | 27.4 | 16.8 | 7.3  | --   | --   |
| Gemma 3 4B                  | 128K          | <1K             | 73.6 (62.6)             | 50.3 | 35.3 | 16.4 | 7.5  | 2.3  | 0.9  | --   | --   |

### Google Reasoning Models (NoLiMa-Hard)

| Model                        | Base Score | 4K   | 8K   | 16K  | 32K  |
|------------------------------|:---------:|:----:|:----:|:----:|:----:|
| Gemini 2.5 Pro               | 99.1      | 73.9 | 63.0 | 58.6 | 58.6 |
| Gemini 2.5 Flash (w/ Thinking) | 89.5   | 48.5 | 33.6 | 21.9 | 15.7 |

### Observations - Google

- **Gemini 2.5 Pro reasoning is strong**: 58.6% at 32K on Hard (on par with GPT-o3)
- **Gemini 2.5 Pro plateaus at 16K-32K**: Same score at both lengths (58.6%), unusual pattern
- **Thinking mode transforms Flash**: But still collapses rapidly (48.5% at 4K on Hard)
- **Gemini 2.0 Flash best non-reasoning Google model**: 4K effective, extended to 128K (though only 16.4%)
- **Gemma models collapse rapidly**: 27B model reaches 9.5% at 32K, 4B is nearly zero (0.9%)
- **Size scaling limited**: Gemma 4B -> 12B -> 27B shows diminishing returns on NoLiMa

## Meta (Llama) Models

| Model              | Claimed Length | Effective Length | Base Score (x0.85 Thr.) | 1K   | 2K   | 4K   | 8K   | 16K  | 32K  |
|--------------------|:-------------:|:---------------:|:-----------------------:|:----:|:----:|:----:|:----:|:----:|:----:|
| Llama 3.3 70B      | 128K          | 2K              | 97.3 (82.7)             | 94.2 | 87.4 | 81.5 | 72.1 | 59.5 | 42.7 |
| Llama 3.1 405B     | 128K          | 2K              | 94.7 (80.5)             | 89.0 | 85.0 | 74.5 | 60.1 | 48.4 | 38.0 |
| Llama 3.1 70B      | 128K          | 2K              | 94.5 (80.3)             | 91.0 | 81.8 | 71.2 | 62.7 | 51.8 | 43.2 |
| Llama 4 Maverick   | 1M            | 2K              | 90.1 (76.6)             | 81.6 | 78.3 | 68.8 | 49.0 | 34.3 | 24.5 |
| Llama 4 Scout      | 10M           | 1K              | 81.7 (69.4)             | 72.3 | 61.8 | 50.8 | 35.5 | 26.9 | 21.6 |
| Llama 3.1 8B       | 128K          | 1K              | 76.7 (65.2)             | 65.7 | 54.4 | 44.1 | 31.9 | 22.6 | 14.2 |

### Observations - Meta

- **All Llama models cap at 2K effective length** regardless of claimed window
- **Llama 3.3 70B is best Llama**: 97.3% base, 42.7% at 32K
- **405B does NOT beat 70B at long context**: 38.0% vs 43.2% at 32K (3.1 70B even better than 405B!)
- **Llama 4 disappoints on NoLiMa**: Maverick (1M claimed) only reaches 24.5% at 32K
- **Llama 4 Scout (10M claimed!) collapses**: 21.6% at 32K despite claiming 10M context
- **Scale paradox**: 3.1 70B > 3.1 405B at 32K, and 3.3 70B > Llama 4 Maverick

## Other Models

| Model          | Claimed Length | Effective Length | Base Score (x0.85 Thr.) | 1K   | 2K   | 4K   | 8K   | 16K  | 32K  |
|----------------|:-------------:|:---------------:|:-----------------------:|:----:|:----:|:----:|:----:|:----:|:----:|
| Mistral Large 2 | 128K         | 2K              | 87.9 (74.7)             | 86.1 | 85.5 | 73.3 | 51.5 | 32.6 | 18.7 |
| Jamba 1.5 Mini  | 256K         | <1K             | 92.4 (78.6)             | 76.3 | 74.1 | 70.8 | 62.2 | 52.7 | 43.6 |
| Command R+      | 128K         | <1K             | 90.9 (77.3)             | 77.0 | 73.5 | 66.3 | 39.5 | 21.3 | 7.4  |

### Other Reasoning (NoLiMa-Hard)

| Model                          | Base Score | 4K   | 8K   | 16K  | 32K  |
|--------------------------------|:---------:|:----:|:----:|:----:|:----:|
| DeepSeek R1-Distill-Llama-70B  | 99.9      | 91.4 | 75.5 | 49.4 | 20.7 |

### Observations - Other

- **Jamba 1.5 Mini interesting**: Mamba-based architecture degrades more gracefully (43.6% at 32K) despite <1K effective length
- **Mistral Large 2 collapses fast**: 85.5% at 2K to 18.7% at 32K
- **Command R+ worst degradation**: 7.4% at 32K (near-zero performance)
- **DeepSeek R1-Distill strong**: 91.4% at 4K, competitive with GPT-o1, but collapses by 32K (20.7%)

## Cross-Model Patterns

### Effective Length Distribution (all 22 models tested)

- 16K: 1 model (GPT-4.1)
- 8K: 1 model (GPT-4o)
- 4K: 3 models (Claude 3.5 Sonnet, Gemini 2.0 Flash, GPT-4o at border)
- 2K: 9 models (most large models)
- 1K: 3 models (Llama 3.1 8B, Gemma 3 12B, Llama 4 Scout)
- <1K: 7 models (all small/lite variants)

### Architecture Observations

- **Mamba (Jamba)**: More graceful degradation curve despite low effective length
- **Larger models NOT always better**: Llama 3.1 405B < 3.1 70B at 32K
- **Newer NOT always better**: Llama 4 < Llama 3.3 on NoLiMa
- **Claimed context length is meaningless**: 10M claimed (Scout) -> 1K effective

## Document History

**[2026-05-22 13:33]**
- Initial creation from GitHub README tables (2025-07-17 update) and paper
