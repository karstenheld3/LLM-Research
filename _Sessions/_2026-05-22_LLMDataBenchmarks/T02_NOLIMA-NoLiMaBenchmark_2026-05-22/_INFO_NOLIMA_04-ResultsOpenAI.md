<DevSystem MarkdownTablesAllowed=true />

# INFO: NoLiMa Results - OpenAI Models

**Doc ID**: NOLIMA-IN04
**Goal**: Document all OpenAI model results on NoLiMa benchmark
**Sources**: NOLIMA-SC-GH-README (2025-07-17 update), NOLIMA-SC-ARXIV-HTML

## Summary

OpenAI models span the widest performance range on NoLiMa. GPT-4.1 achieves the best effective length (16K) among all non-reasoning models tested. GPT-4o follows at 8K. The smaller models (4o mini, 4.1 Mini, 4.1 Nano) all fail to maintain performance beyond 1K tokens. The GPT-4.1 series (released 2025) shows significant improvement over GPT-4o in length generalization despite lower base scores for smaller variants.

## Main NoLiMa Results (Non-Reasoning)

| Model         | Claimed Length | Effective Length | Base Score (x0.85 Thr.) | 1K   | 2K   | 4K   | 8K   | 16K  | 32K  | 64K  | 128K |
|---------------|:-------------:|:---------------:|:-----------------------:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|
| GPT-4.1       | 1M            | 16K             | 97.0 (82.5)             | 95.6 | 95.2 | 91.7 | 87.5 | 84.9 | 79.8 | 69.7 | 64.7 |
| GPT-4o        | 128K          | 8K              | 99.3 (84.4)             | 98.1 | 98.0 | 95.7 | 89.2 | 81.6 | 69.7 | 62.4 | 56.0 |
| GPT-4o mini   | 128K          | <1K             | 84.9 (72.2)             | 67.7 | 58.2 | 44.1 | 32.6 | 20.6 | 13.7 | --   | --   |
| GPT-4.1 Mini  | 1M            | <1K             | 80.9 (68.8)             | 66.7 | 62.8 | 58.7 | 51.9 | 46.2 | 38.8 | --   | --   |
| GPT-4.1 Nano  | 1M            | <1K             | 80.7 (68.6)             | 60.8 | 48.2 | 36.7 | 28.8 | 19.5 | 9.4  | --   | --   |

## Key Observations - Non-Reasoning

- **GPT-4.1 is the NoLiMa champion**: 16K effective length, maintains 79.8% at 32K (vs GPT-4o's 69.7%)
- **GPT-4o has highest base score** (99.3%) but degrades faster after 8K than GPT-4.1
- **GPT-4.1 vs GPT-4o trade-off**: GPT-4.1 trades 2.3% base score for 2x effective length
- **Size matters enormously**: GPT-4o -> GPT-4o mini drops from 8K to <1K effective length
- **GPT-4.1 Mini degrades gracefully**: Despite <1K effective length, still shows 38.8% at 32K (vs 4o mini's 13.7%)
- **GPT-4.1 Nano collapses fast**: Nearly unusable beyond 4K (36.7% -> 9.4% at 32K)

## NoLiMa-Hard Results (Non-Reasoning Baselines)

| Model    | Base Score | 4K   | 8K   | 16K  | 32K  |
|----------|:---------:|:----:|:----:|:----:|:----:|
| GPT-4.1  | 96.0      | 69.8 | 58.4 | 54.5 | 45.4 |
| GPT-4o   | 99.9      | 90.7 | 75.6 | 61.1 | 38.5 |

## NoLiMa-Hard Results (Reasoning Models)

| Model       | Base Score | 4K   | 8K   | 16K  | 32K  |
|-------------|:---------:|:----:|:----:|:----:|:----:|
| GPT-o3      | 100.0     | 94.4 | 86.2 | 74.9 | 58.5 |
| GPT-o1      | 99.9      | 92.0 | 78.0 | 60.1 | 31.1 |
| GPT-o3 Mini | 98.8      | 52.8 | 36.9 | 25.5 | 18.9 |
| GPT-o4 Mini | 99.6      | 57.4 | 30.8 | 20.2 | 11.7 |

## Key Observations - Reasoning Models

- **GPT-o3 is best overall** on NoLiMa-Hard: 58.5% at 32K, never drops below 50% threshold
- **GPT-o1 degrades significantly**: From 92.0% at 4K to 31.1% at 32K (below 50% mark)
- **Mini reasoning models fail badly**: o3 Mini and o4 Mini both collapse below 50% by 8K
- **Reasoning helps but doesn't solve**: Even o3 loses 41.5 percentage points from base to 32K
- **o4 Mini worse than o3 Mini at longer contexts**: 11.7% vs 18.9% at 32K despite higher base score
- **Perfect base scores** (99.6-100.0) confirm task is trivial at short context; degradation is purely length-driven

## Performance Ranking (OpenAI, at 32K)

1. GPT-o3: 58.5% (NoLiMa-Hard)
2. GPT-4.1: 79.8% (main NoLiMa) / 45.4% (Hard)
3. GPT-4o: 69.7% (main) / 38.5% (Hard)
4. GPT-o1: 31.1% (Hard)
5. GPT-4.1 Mini: 38.8% (main)
6. GPT-o3 Mini: 18.9% (Hard)
7. GPT-4o mini: 13.7% (main)
8. GPT-o4 Mini: 11.7% (Hard)
9. GPT-4.1 Nano: 9.4% (main)

## Relevance to Our Research

- **GPT-4.1 should be tested in our pipeline**: Best non-reasoning length generalization, not tested in our experiments yet
- **Reasoning model hierarchy**: o3 >> o1 >> o3-mini ~ o4-mini for long-context comprehension
- **Our gpt-5-mini findings**: We showed 10x improvement with high effort; NoLiMa shows reasoning helps but doesn't fully solve length degradation
- **Implication**: Format optimization (our research) may be complementary to reasoning - reducing effective context length needed could bypass the attention limitation NoLiMa exposes

## Document History

**[2026-05-22 13:33]**
- Initial creation from GitHub README tables (2025-07-17 update) and paper Table 3/5
