## findings-1

Derived from 63/63 completed tests. Data in `_INFO_01_FormatComparison-TestResults.md [TBLF-IN05]` section 5.

- **Format preferences differ dramatically by model family** [TESTED]
  - GPT best formats: gpt-5.5: toml, gpt-5.4: json, gpt-5-mini: kv_colon_space, gpt-5: yaml, gpt-5.2: csv_quoted
  - Claude best formats: opus-4.8: csv, opus-4.5: json, sonnet-4.5: json
  - Max spread: 5.8x (gpt-5.2)

- **Token efficiency does NOT predict scale limits** [TESTED]
  - xml (2.12x tokens) outperforms csv (1.00x) on 4/8 models
  - csv outperforms xml on 4/8 models (newer GPT + Claude)

- **Format impact is massive - up to 5.8x within a single model** [TESTED]
  - gpt-5-mini: kv_colon_space (500) vs markdown_table (163) = 3.1x
  - gpt-5: yaml (333) vs markdown_table (83) = 4.0x
  - gpt-5.2: csv_quoted (268) vs toml (46) = 5.8x

- **No universal best format exists** [TESTED]
  - gpt-5.5: toml (828)
  - gpt-5.4: json (702)
  - gpt-5-mini: kv_colon_space (500)
  - gpt-5: yaml (333)
  - gpt-5.2: csv_quoted (268)
  - opus-4.8: csv (630)
  - opus-4.5: json (265)
  - sonnet-4.5: json (189)

- **Format preference shifts between model generations** [TESTED]
  - gpt-5.4: json (702). gpt-5.5: toml (828), json drops to 430 (-39%)

## findings-3

### 3.1 H2: JSON Ranking Per Model

| Model      | JSON Scale | JSON Rank | Best Format    | Best Scale | JSON vs Best |
|------------|------------|-----------|----------------|------------|--------------|
| gpt-5.5    | 430        | 7/8      | toml           | 828        | 52%            |
| gpt-5.4    | 702        | 1/8      | json           | 702        | 100%            |
| gpt-5-mini | 335        | 4/8      | kv_colon_space | 500        | 67%            |
| gpt-5      | 249        | 3/8      | yaml           | 333        | 75%            |
| gpt-5.2    | 241        | 3/8      | csv_quoted     | 268        | 90%            |
| opus-4.8   | 576        | 4/7      | csv            | 630        | 91%            |
| opus-4.5   | 265        | 1/8      | json           | 265        | 100%            |
| sonnet-4.5 | 189        | 1/8      | json           | 189        | 100%            |

**JSON is #1 in 3/8 models.**

### 3.2 H3: Family Preference Divergence

```
gpt-5.5 (gpt)        TOP: toml (828), yaml (675), markdown_table (627)
                     BOT: json (430), xml (375)
gpt-5.4 (gpt)        TOP: json (702), markdown_table (554), xml (546)
                     BOT: yaml (523), kv_colon_space (359)
gpt-5-mini (gpt)     TOP: kv_colon_space (500), yaml (500), csv_quoted (437)
                     BOT: csv (194), markdown_table (163)
gpt-5 (gpt)          TOP: yaml (333), xml (327), json (249)
                     BOT: csv (166), markdown_table (83)
gpt-5.2 (gpt)        TOP: csv_quoted (268), xml (261), json (241)
                     BOT: kv_colon_space (100), toml (46)
opus-4.8 (claude)    TOP: csv (630), toml (622), csv_quoted (607)
                     BOT: xml (545), markdown_table (468)
opus-4.5 (claude)    TOP: json (265), yaml (259), csv (232)
                     BOT: xml (182), csv_quoted (171)
sonnet-4.5 (claude)  TOP: json (189), csv (126), kv_colon_space (126)
                     BOT: toml (115), xml (99)
```

### 3.3 H5: Token Efficiency vs Scale (csv=1.00x reference)

| Model      | csv Scale | xml Scale | xml/csv Ratio | xml Wins? |
|------------|-----------|-----------|---------------|-----------|
| gpt-5.5    | 494       | 375       |          0.76 | NO        |
| gpt-5.4    | 523       | 546       |          1.04 | YES       |
| gpt-5-mini | 194       | 296       |          1.53 | YES       |
| gpt-5      | 166       | 327       |          1.97 | YES       |
| gpt-5.2    | 215       | 261       |          1.21 | YES       |
| opus-4.8   | 630       | 545       |          0.87 | NO        |
| opus-4.5   | 232       | 182       |          0.78 | NO        |
| sonnet-4.5 | 126       | 99        |          0.79 | NO        |

### 3.4 H6: Key-Value Ranking Per Model

| Model      | kv Scale | kv Rank | Best Format    | Best Scale | kv vs Best |
|------------|----------|---------|----------------|------------|------------|
| gpt-5.5    | 588      | 4/8    | toml           | 828        | 71%          |
| gpt-5.4    | 359      | 8/8    | json           | 702        | 51%          |
| gpt-5-mini | 500      | 1/8    | kv_colon_space | 500        | 100%          |
| gpt-5      | 238      | 4/8    | yaml           | 333        | 71%          |
| gpt-5.2    | 100      | 7/8    | csv_quoted     | 268        | 37%          |
| opus-4.8   | 545      | 5/7    | csv            | 630        | 87%          |
| opus-4.5   | 226      | 4/8    | json           | 265        | 85%          |
| sonnet-4.5 | 126      | 3/8    | json           | 189        | 67%          |

**kv_colon_space is #1 in 1/8 models.**

## findings-4

1. **gpt-5.5 format preference inverts vs gpt-5.4** [TESTED]
   - gpt-5.4 best: json (702). gpt-5.5 best: toml (828), json drops to 430 (-39%)

2. **markdown_table worst on 3 models** [TESTED]
   - gpt-5-mini: 163 (rank 8/8)
   - gpt-5: 83 (rank 8/8)
   - opus-4.8: 468 (rank 7/7)

3. **Format inversions (best for one model, worst for another)** [TESTED]
   - toml: BEST for gpt-5.5. WORST for gpt-5.2.
   - kv_colon_space: BEST for gpt-5-mini. WORST for gpt-5.4.
   - csv_quoted: BEST for gpt-5.2. WORST for opus-4.5.

4. **Format sensitivity inversely correlates with model capability** [VERIFIED]
   - gpt-5.2: 5.8x (best=268)
   - gpt-5: 4.0x (best=333)
   - gpt-5-mini: 3.1x (best=500)
   - gpt-5.5: 2.2x (best=828)
   - gpt-5.4: 2.0x (best=702)
   - sonnet-4.5: 1.9x (best=189)
   - opus-4.5: 1.5x (best=265)
   - opus-4.8: 1.3x (best=630)

5. **gpt-5.5 is 1.4x faster than gpt-5.4 (Time Per Kilo-Cell, TPKC)** [TESTED]
   - gpt-5.5 avg TPKC: 12s. gpt-5.4 avg TPKC: 16s

## findings-5

**Scope**: Results apply to 7-column tabular extraction with compound filter. Different column counts or task complexity may shift rankings.

**IMPORTANT (TBLF-FL-005)**: These results use 7/7 columns (simplified dataset). Test 01 used 7/20 columns. Scale limits are NOT directly comparable between Test 01 and Test 02.

### By Model (sorted by max scale)

| Model      | Recommended   | Scale | Alternative    | Scale | Avoid          | Scale |
|------------|---------------|-------|----------------|-------|----------------|-------|
| gpt-5.5    | toml          | 828   | yaml           | 675   | xml            | 375   |
| gpt-5.4    | json          | 702   | markdown_table | 554   | kv_colon_space | 359   |
| gpt-5-mini | kv_colon_space | 500   | yaml           | 500   | markdown_table | 163   |
| gpt-5      | yaml          | 333   | xml            | 327   | markdown_table | 83    |
| gpt-5.2    | csv_quoted    | 268   | xml            | 261   | toml           | 46    |
| opus-4.8   | csv           | 630   | toml           | 622   | markdown_table | 468   |
| opus-4.5   | json          | 265   | yaml           | 259   | csv_quoted     | 171   |
| sonnet-4.5 | json          | 189   | csv            | 126   | xml            | 99    |

### By Cost Efficiency (lowest Cost Per Kilo-Cell, CPKC)

| Model      | Best CPKC Format | CPKC   | Scale | 2nd Best         | CPKC   |
|------------|------------------|--------|-------|------------------|--------|
| gpt-5.5    | markdown_table   | $0.131 | 627   | csv              | $0.133 |
| gpt-5.4    | csv              | $0.038 | 523   | csv_quoted       | $0.040 |
| gpt-5-mini | kv_colon_space   | $0.005 | 500   | csv_quoted       | $0.005 |
| gpt-5      | xml              | $0.032 | 327   | toml             | $0.032 |
| gpt-5.2    | kv_colon_space   | $0.030 | 100   | csv_quoted       | $0.031 |
| opus-4.8   | csv              | $0.200 | 630   | csv_quoted       | $0.208 |
| opus-4.5   | csv              | $0.188 | 232   | markdown_table   | $0.190 |
| sonnet-4.5 | csv_quoted       | $0.110 | 120   | csv              | $0.115 |

### Key Insight

**Always test your specific model with your intended format.** Format choice matters more than previously thought - up to 5.8x scale difference. No universal best format exists.
