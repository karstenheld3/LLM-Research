## Section 5.1: Scale Limit Results (All Configurations)

| Model             | Provider  | Method            | Effort | Scale Limit | Failure Mode  | Context % | Cost    | Time/req |
|-------------------|-----------|-------------------|--------|-------------|---------------|-----------|---------|----------|
| claude-opus-4.7   | Anthropic | adaptive_thinking | high   | 843+        | (cancelled)   | -         | ~$30+   | ~3.3 min |
| gpt-5-mini        | OpenAI    | reasoning         | high   | 675+        | (errors)      | -         | $0.00   | -        |
| claude-opus-4.6   | Anthropic | adaptive_thinking | high   | 667         | comprehension | 55.4%     | ~$18+   | ~1.5 min |
| gpt-5-mini        | OpenAI    | reasoning         | medium | 500         | comprehension | 7.1%      | $0.40   | ~1.2 min |
| claude-opus-4.8   | Anthropic | adaptive_thinking | high   | 492         | comprehension | 12.4%     | ~$20+   | ~59 sec  |
| gpt-5.4           | OpenAI    | reasoning         | medium | 492         | comprehension | 6.8%      | $2.49   | ~51 sec  |
| gpt-5             | OpenAI    | reasoning         | high   | 492         | truncation    | 8.0%      | $2.73   | ~4.9 min |
| gpt-5             | OpenAI    | reasoning         | medium | 450         | comprehension | 6.4%      | $2.97   | ~1.5 min |
| gpt-5.5           | OpenAI    | reasoning         | medium | 437         | comprehension | 6.8%      | $8.15   | ~32 sec  |
| gpt-5             | OpenAI    | reasoning         | low    | 356         | comprehension | 2.1%      | $0.43   | ~2.2 min |
| gpt-5.2           | OpenAI    | reasoning         | medium | 215         | comprehension | 1.4%      | $0.29   | ~55 sec  |
| claude-sonnet-4   | Anthropic | thinking          | medium | 187         | truncation    | 25.1%     | $3.41   | ~40 sec  |
| claude-opus-4.5   | Anthropic | thinking          | medium | 177         | truncation    | 25.1%     | $5.36   | ~32 sec  |
| claude-sonnet-4.5 | Anthropic | thinking          | medium | 168         | comprehension | 8.4%      | $0.89   | ~1.1 min |
| gpt-5-mini        | OpenAI    | reasoning         | low    | 65          | comprehension | 4.3%      | $0.07   | ~16 sec  |
| claude-opus-4.7   | Anthropic | adaptive_thinking | medium | 12          | comprehension | 5.1%      | $1.96   | ~2 sec   |
| claude-haiku-4.5  | Anthropic | temperature       | medium | 9           | comprehension | 8.3%      | $0.09   | ~2 sec   |
| claude-opus-4.6   | Anthropic | adaptive_thinking | medium | 6           | comprehension | 16.9%     | $1.12   | ~2 sec   |
| gpt-4o-mini       | OpenAI    | temperature       | medium | 6           | comprehension | 2.1%      | $0.00   | ~5 sec   |
| gpt-4o            | OpenAI    | temperature       | medium | 4           | comprehension | 11.3%     | $0.10   | ~3 sec   |

## Section 6.1: Primary Failure Mode per Model

| Model              | Primary Failure | Truncated              | Context Used |
|--------------------|-----------------|------------------------|--------------|
| claude-opus-4.6 high | comprehension   | No                     | 55.4%        |
| gpt-5-mini         | comprehension   | No                     | 7.1%         |
| claude-opus-4.8 high | comprehension   | No                     | 12.4%        |
| gpt-5.4            | comprehension   | No                     | 6.8%         |
| gpt-5 high         | TRUNCATION      | Yes                    | 8.0%         |
| gpt-5              | comprehension   | No                     | 6.4%         |
| gpt-5.5            | comprehension   | No                     | 6.8%         |
| gpt-5 low          | comprehension   | No                     | 2.1%         |
| gpt-5.2            | comprehension   | No                     | 1.4%         |
| claude-sonnet-4    | TRUNCATION      | Yes                    | 25.1%        |
| claude-opus-4.5    | TRUNCATION      | Yes                    | 25.1%        |
| claude-sonnet-4.5  | comprehension   | No                     | 8.4%         |
| gpt-5-mini low     | comprehension   | No                     | 4.3%         |
| claude-opus-4.7    | comprehension   | No                     | 5.1%         |
| claude-haiku-4.5   | comprehension   | Yes (early iters)      | 8.3%         |
| claude-opus-4.6    | comprehension   | No                     | 16.9%        |
| gpt-4o-mini        | comprehension   | No                     | 2.1%         |
| gpt-4o             | comprehension   | No                     | 11.3%        |

## Section 7: Effort Level Data

### claude-opus-4.6 Effort Comparison

| Effort | Scale Limit | Cost    | Time/req |
|--------|-------------|---------|----------|
| medium | 6           | $1.12   | ~2 sec   |
| high   | 667         | ~$18+   | ~1.5 min |

### claude-opus-4.7 Effort Comparison

| Effort | Scale Limit | Cost    | Time/req |
|--------|-------------|---------|----------|
| medium | 12          | $1.96   | ~2 sec   |
| high   | 843+        | ~$30+   | ~3.3 min |

### gpt-5-mini Effort Comparison

| Effort | Scale Limit | Cost    | Time/req |
|--------|-------------|---------|----------|
| low    | 65          | $0.07   | ~16 sec  |
| medium | 500         | $0.40   | ~1.2 min |
| high   | 675+        | $0.00   | -        |

### gpt-5 Effort Comparison

| Effort | Scale Limit | Cost    | Time/req |
|--------|-------------|---------|----------|
| low    | 356         | $0.43   | ~2.2 min |
| medium | 450         | $2.97   | ~1.5 min |
| high   | 492         | $2.73   | ~4.9 min |

## Section 8: Model Tier Comparison Data

### Mini Tier (Temperature vs Reasoning)

| Model       | Method      | Scale Limit |
|-------------|-------------|-------------|
| gpt-4o-mini | temperature | 6           |
| gpt-5-mini  | reasoning   | 500         |

Ratio: 83x

### Full Tier (Temperature vs Reasoning)

| Model  | Method          | Scale Limit |
|--------|-----------------|-------------|
| gpt-4o | temperature     | 4           |
| gpt-5  | reasoning (low) | 356         |

Ratio: 89x
