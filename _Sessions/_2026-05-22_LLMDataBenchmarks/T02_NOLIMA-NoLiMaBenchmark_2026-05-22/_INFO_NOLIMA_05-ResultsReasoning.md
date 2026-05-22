<DevSystem MarkdownTablesAllowed=true />

# INFO: NoLiMa Results - Reasoning Models

**Doc ID**: NOLIMA-IN05
**Goal**: Document all reasoning model results on NoLiMa and NoLiMa-Hard, including CoT analysis
**Sources**: NOLIMA-SC-GH-README, NOLIMA-SC-ARXIV-HTML (sections 4.4.3, 4.4.4)

## Summary

Reasoning models (GPT-o1, o3, o3-mini, o4-mini, DeepSeek R1, Gemini 2.5 Pro/Flash) are evaluated on NoLiMa-Hard (10 hardest pairs). While they outperform standard CoT prompting, no reasoning model achieves full-length generalization. GPT-o3 leads at 58.5% at 32K. The critical finding: reasoning helps with associative linking but cannot overcome the fundamental attention limitation at scale - the model must still locate the relevant needle before it can reason about it.

## NoLiMa-Hard Results (All Reasoning Models)

| Model                             | Base Score | 4K   | 8K   | 16K  | 32K  | Below 50% at |
|-----------------------------------|:---------:|:----:|:----:|:----:|:----:|:------------:|
| GPT-o3                            | 100.0     | 94.4 | 86.2 | 74.9 | 58.5 | >32K         |
| Gemini 2.5 Pro                    | 99.1      | 73.9 | 63.0 | 58.6 | 58.6 | >32K         |
| GPT-o1                            | 99.9      | 92.0 | 78.0 | 60.1 | 31.1 | 32K          |
| DeepSeek R1-Distill-Llama-70B     | 99.9      | 91.4 | 75.5 | 49.4 | 20.7 | 16K          |
| GPT-o3 Mini                       | 98.8      | 52.8 | 36.9 | 25.5 | 18.9 | 4K           |
| Gemini 2.5 Flash (w/ Thinking)    | 89.5      | 48.5 | 33.6 | 21.9 | 15.7 | 4K           |
| GPT-o4 Mini                       | 99.6      | 57.4 | 30.8 | 20.2 | 11.7 | 8K           |

## Baseline Comparison (Non-Reasoning on NoLiMa-Hard)

| Model                             | Base Score | 4K   | 8K   | 16K  | 32K  |
|-----------------------------------|:---------:|:----:|:----:|:----:|:----:|
| GPT-4.1                           | 96.0      | 69.8 | 58.4 | 54.5 | 45.4 |
| GPT-4o                            | 99.9      | 90.7 | 75.6 | 61.1 | 38.5 |
| Gemini 2.5 Flash (w/o Thinking)   | 87.5      | 47.2 | 23.5 | 13.4 | 9.8  |
| Llama 3.3 70B (w/o CoT)          | 98.3      | 55.5 | 37.2 | 16.7 | 8.9  |
| Llama 3.3 70B (w/ CoT)           | 97.1      | 73.0 | 51.2 | 31.8 | 10.1 |

## CoT Prompting Analysis (from paper Table 4)

CoT prompting on standard (non-reasoning) models was tested on Llama 3.3 70B:
- CoT improves NoLiMa-Hard from 55.5% to 73.0% at 4K (+17.5pp)
- Improvement persists at 8K: 37.2% -> 51.2% (+14.0pp)
- Diminishing returns at 16K: 16.7% -> 31.8% (+15.1pp)
- Negligible at 32K: 8.9% -> 10.1% (+1.2pp)

**Why CoT has limited impact on NoLiMa:**
- NoLiMa questions are inherently simple (single clue, not decomposable)
- The bottleneck is FINDING the needle, not REASONING about it
- CoT cannot help the attention mechanism locate relevant information
- Once found, the associative reasoning is trivial (confirmed by near-perfect base scores)

## Reasoning Model Tiers

**Tier 1 - Sustained performance (>50% at 32K):**
- GPT-o3 (58.5%)
- Gemini 2.5 Pro (58.6%)

**Tier 2 - Moderate degradation (<50% only at 32K):**
- GPT-o1 (31.1% at 32K but 60.1% at 16K)
- DeepSeek R1-Distill-Llama-70B (similar profile to o1)

**Tier 3 - Rapid collapse (<50% by 8K):**
- GPT-o3 Mini (36.9% at 8K)
- GPT-o4 Mini (30.8% at 8K)
- Gemini 2.5 Flash w/ Thinking (33.6% at 8K)

## Critical Insight: Reasoning Cannot Fix Attention

The paper demonstrates that reasoning-based approaches (CoT prompting, o1/o3 models) improve performance but fundamentally cannot solve the NoLiMa challenge because:

1. **Two-stage process**: Model must (a) LOCATE the needle via attention, then (b) REASON about the association
2. **Reasoning only helps stage (b)**: Extended thinking improves associative reasoning but doesn't help attention locate information without literal cues
3. **Attention is the bottleneck**: At longer contexts, attention weights spread thinner, making it harder to attend to semantically (but not lexically) related tokens
4. **Evidence**: Even GPT-o3 (100% base score, strongest reasoning) still loses 41.5pp at 32K

## Inference Settings for Reasoning Models

- **GPT-o1, GPT-o3**: Default sampling decoding (OpenAI API defaults)
- **GPT-o3 Mini, GPT-o4 Mini**: Default sampling decoding
- **DeepSeek R1-Distill-Llama-70B**: top-P sampling (p=0.95, temperature=0.6)
- **Gemini 2.5 Pro/Flash**: Default with thinking_budget parameter in model config
- **Max generation**: 1536 tokens (reasoning + output) for all reasoning models

## Relevance to Our Research

- **Validates effort-scaling limits**: Our Test 01 showed 10x improvement with high reasoning effort, but NoLiMa shows reasoning cannot fully overcome context length degradation
- **Format as complementary strategy**: If better format reduces effective context length needed, it bypasses the attention limitation entirely
- **Hypothesis**: Structured data formats that cluster related information may reduce the "effective search space" for attention, improving comprehension without reasoning overhead
- **Missing data**: No gpt-5 or gpt-5-mini results exist for NoLiMa yet - opportunity for our pipeline to contribute

## Document History

**[2026-05-22 13:33]**
- Initial creation from GitHub README (2025-07-17 update) and paper sections 4.4.3-4.4.4
