<DevSystem MarkdownTablesAllowed=true />

# INFO: Format Comparison - Test Results

**Doc ID**: TBLF-IN05
**Goal**: Collect all test result data from format comparison experiments (56 tests across 7 models and 8 formats)
**Timeline**: Created 2026-05-22 (data collected 2026-03-09 to 2026-05-22)

**Depends on:**
- `_SPEC_FormatComparison.md [TBLF-SP02]` for test framework specification
- `_TEST_FormatComparison.md [TBLF-TP02]` for execution procedures

## 1. Research Problem

**Question**: Does input format affect LLM extraction scale limits for tabular data?

**Prior evidence** (TK-001 benchmark, `_INFO_LLM_MARKDOWN_PREFERENCES.md [LLMO-IN01]`):
- Key-value formats (`:`, `: `) ranked #1-#2 at 300 records
- CSV ranked #3, JSON #7, XML #10
- Format type appeared to matter more than token efficiency
- Tested on gpt-5-mini only

## 2. Methodology

- **Algorithm**: Binary search for maximum reliable rows (same as Test 01)
- **Start point**: CSV baseline from Test 01 (faster convergence)
- **Success criteria**: Precision=1.00 AND Recall=1.00 across 3 runs per iteration
- **Evaluation**: Deterministic ID matching (regex: `EMP-\d{4}`)

### 2.1 Test Configuration

- **Columns**: 7 (id, name, department, salary, clearance, rating, projects)
- **Column selection**: 7 from 7 available (NOT 7 from 20 as in Test 01)
- **Filter**: department="Engineering" AND salary>75000
- **Seed**: 42
- **Adversarial content**: Yes (~20% records contain delimiter characters)

**IMPORTANT (TBLF-FL-005)**: This test uses a simplified dataset (7/7 columns) that differs from Test 01 (7/20 columns selected). Scale limit results are NOT directly comparable between Test 01 and Test 02.

### 2.2 Format Token Efficiency

| Format         | Size (300 rows) | Relative |
|----------------|-----------------|----------|
| csv            | 148 KB          | 1.00x    |
| csv_quoted     | 156 KB          | 1.06x    |
| markdown_table | 197 KB          | 1.33x    |
| kv_colon_space | 217 KB          | 1.47x    |
| toml           | 235 KB          | 1.59x    |
| yaml           | 249 KB          | 1.68x    |
| json           | 269 KB          | 1.82x    |
| xml            | 314 KB          | 2.12x    |

## 3. Variables

**Independent variables:**
- Input format (8): csv_quoted, csv, kv_colon_space, markdown_table, json, xml, yaml, toml
- Model (7): gpt-5.5, gpt-5.4, gpt-5-mini, gpt-5, gpt-5.2, claude-opus-4.5, claude-sonnet-4.5

**Controlled variables:**
- Column count: 7
- Filter complexity: 2 conditions (IN list + threshold)
- Adversarial content: ~20%
- Seed: 42
- Verification runs: 3 per iteration
- Reasoning effort: medium (except gpt-5: low)

**Dependent variables:**
- Scale limit (max reliable rows)
- Per-request cost at scale limit
- Per-request time at scale limit
- Failure mode (comprehension or truncation)
- Input/output token counts

## 4. Metrics

- **Scale** - Maximum reliable rows at 100% accuracy (3/3 runs passed)
- **vs Best** - Percentage relative to best format for this model (100% = top performer)
- **In (K)** - Input tokens in thousands at scale limit
- **Out (K)** - Output tokens in thousands at scale limit
- **Time** - Average time per request at scale limit
- **TPKC** - Time Per Kilo Cells (seconds) = time / (rows x 7 columns) x 1000
- **Cost** - Cost per request at scale limit
- **CPKC** - Cost Per Kilo Cells = cost / (rows x 7 columns) x 1000

**Why per-kilo-cell metrics?** Raw time and cost are measured at different scale limits (row counts). TPKC and CPKC normalize to a common unit (1000 cells), making formats directly comparable regardless of scale limit.

## 5. Results

### 5.1 All Tests (56 tests, sorted by model then scale limit)

| Model      | Effort | Format         | Scale   | vs Best | In (K) | Out (K) | Time     | TPKC | Cost  | CPKC   |
|------------|--------|----------------|---------|---------|--------|---------|----------|------|-------|--------|
| gpt-5.5    | medium | toml           | **828** | 100%    | -      | -       | ~1.2 min | 12s  | $0.76 | $0.131 |
| gpt-5.5    | medium | yaml           | **675** | 82%     | -      | -       | ~1.0 min | 13s  | $0.67 | $0.142 |
| gpt-5.5    | medium | markdown_table | **627** | 76%     | -      | -       | ~0.7 min | 10s  | $0.58 | $0.132 |
| gpt-5.5    | medium | kv_colon_space | **588** | 71%     | -      | -       | ~0.8 min | 12s  | $0.52 | $0.126 |
| gpt-5.5    | medium | csv            | **494** | 60%     | -      | -       | ~0.6 min | 12s  | $0.43 | $0.124 |
| gpt-5.5    | medium | csv_quoted     | **491** | 59%     | -      | -       | ~0.6 min | 12s  | $0.43 | $0.125 |
| gpt-5.5    | medium | json           | **430** | 52%     | -      | -       | ~0.7 min | 14s  | $0.44 | $0.146 |
| gpt-5.5    | medium | xml            | **375** | 45%     | -      | -       | ~0.7 min | 16s  | $0.40 | $0.152 |
|            |        |                |         |         |        |         |          |      |       |        |
| gpt-5.4    | medium | json           | **702** | 100%    | -      | -       | ~2.9 min | 35s  | $0.93 | $0.189 |
| gpt-5.4    | medium | markdown_table | **554** | 79%     | -      | -       | ~3.0 min | 46s  | $0.54 | $0.139 |
| gpt-5.4    | medium | xml            | **546** | 78%     | -      | -       | ~3.0 min | 47s  | $0.63 | $0.165 |
| gpt-5.4    | medium | csv            | **523** | 75%     | -      | -       | ~2.5 min | 41s  | $0.53 | $0.145 |
| gpt-5.4    | medium | csv_quoted     | **523** | 75%     | -      | -       | ~2.5 min | 41s  | $0.53 | $0.145 |
| gpt-5.4    | medium | toml           | **523** | 75%     | -      | -       | ~2.9 min | 47s  | $0.53 | $0.145 |
| gpt-5.4    | medium | yaml           | **523** | 75%     | -      | -       | ~2.5 min | 41s  | $0.53 | $0.145 |
| gpt-5.4    | medium | kv_colon_space | **359** | 51%     | -      | -       | ~2.2 min | 52s  | $0.33 | $0.131 |
|            |        |                |         |         |        |         |          |      |       |        |
| gpt-5-mini | medium | kv_colon_space | **500** | 100%    | 98     | 42      | ~9.3 min | 159s | $0.07 | $0.020 |
| gpt-5-mini | medium | yaml           | **500** | 100%    | 110    | 44      | ~4.4 min | 76s  | $0.06 | $0.017 |
| gpt-5-mini | medium | csv_quoted     | **437** | 87%     | 62     | 39      | ~4.7 min | 92s  | $0.05 | $0.016 |
| gpt-5-mini | medium | json           | **335** | 67%     | 86     | 35      | ~5.1 min | 131s | $0.05 | $0.021 |
| gpt-5-mini | medium | xml            | **296** | 59%     | 87     | 42      | ~4.0 min | 116s | $0.05 | $0.024 |
| gpt-5-mini | medium | toml           | **296** | 59%     | 63     | 29      | ~3.7 min | 107s | $0.05 | $0.024 |
| gpt-5-mini | medium | csv            | **194** | 39%     | 28     | 27      | ~3.6 min | 159s | $0.04 | $0.029 |
| gpt-5-mini | medium | markdown_table | **163** | 33%     | 24     | 22      | ~2.2 min | 116s | $0.04 | $0.035 |
|            |        |                |         |         |        |         |          |      |       |        |
| gpt-5      | low    | yaml           | **333** | 100%    | 73     | 38      | ~2.6 min | 67s  | $0.21 | $0.090 |
| gpt-5      | low    | xml            | **327** | 98%     | 96     | 32      | ~3.2 min | 84s  | $0.21 | $0.092 |
| gpt-5      | low    | json           | **249** | 75%     | 64     | 32      | ~3.0 min | 103s | $0.19 | $0.109 |
| gpt-5      | low    | kv_colon_space | **238** | 71%     | 47     | 29      | ~3.9 min | 141s | $0.18 | $0.108 |
| gpt-5      | low    | csv_quoted     | **227** | 68%     | 33     | 23      | ~2.7 min | 102s | $0.16 | $0.101 |
| gpt-5      | low    | toml           | **216** | 65%     | 46     | 23      | ~2.4 min | 95s  | $0.17 | $0.112 |
| gpt-5      | low    | csv            | **166** | 50%     | 24     | 21      | ~2.3 min | 119s | $0.13 | $0.112 |
| gpt-5      | low    | markdown_table | **83**  | 25%     | 13     | 13      | ~2.4 min | 248s | $0.10 | $0.172 |
|            |        |                |         |         |        |         |          |      |       |        |
| gpt-5.2    | medium | csv_quoted     | **268** | 100%    | 39     | 20      | ~1.4 min | 45s  | $0.19 | $0.101 |
| gpt-5.2    | medium | xml            | **261** | 97%     | 77     | 24      | ~1.5 min | 49s  | $0.23 | $0.126 |
| gpt-5.2    | medium | json           | **241** | 90%     | 62     | 20      | ~1.2 min | 43s  | $0.20 | $0.119 |
| gpt-5.2    | medium | csv            | **215** | 80%     | 30     | 19      | ~1.3 min | 52s  | $0.17 | $0.113 |
| gpt-5.2    | medium | markdown_table | **154** | 57%     | 22     | 18      | ~1.1 min | 61s  | $0.15 | $0.139 |
| gpt-5.2    | medium | yaml           | **134** | 50%     | 30     | 10      | ~0.6 min | 38s  | $0.11 | $0.117 |
| gpt-5.2    | medium | kv_colon_space | **100** | 37%     | 20     | 6       | ~0.5 min | 43s  | $0.08 | $0.114 |
| gpt-5.2    | medium | toml           | **46**  | 17%     | 11     | 3       | ~0.4 min | 75s  | $0.06 | $0.186 |
|            |        |                |         |         |        |         |          |      |       |        |
| opus-4.5   | medium | json           | **265** | 100%    | 81     | 30      | ~1.8 min | 58s  | $1.23 | $0.663 |
| opus-4.5   | medium | yaml           | **259** | 98%     | 69     | 29      | ~1.7 min | 56s  | $1.03 | $0.568 |
| opus-4.5   | medium | csv            | **232** | 88%     | 38     | 29      | ~1.6 min | 59s  | $0.92 | $0.566 |
| opus-4.5   | medium | kv_colon_space | **226** | 85%     | 51     | 30      | ~1.7 min | 65s  | $0.98 | $0.619 |
| opus-4.5   | medium | markdown_table | **221** | 83%     | 38     | 28      | ~1.8 min | 70s  | $0.93 | $0.601 |
| opus-4.5   | medium | xml            | **182** | 69%     | 63     | 29      | ~1.8 min | 85s  | $0.82 | $0.644 |
| opus-4.5   | medium | toml           | **182** | 69%     | 47     | 27      | ~1.7 min | 80s  | $0.97 | $0.761 |
| opus-4.5   | medium | csv_quoted     | **171** | 65%     | 29     | 27      | ~1.3 min | 65s  | $0.82 | $0.685 |
|            |        |                |         |         |        |         |          |      |       |        |
| sonnet-4.5 | medium | json           | **189** | 100%    | 58     | 22      | ~1.6 min | 73s  | $0.54 | $0.408 |
| sonnet-4.5 | medium | csv            | **126** | 67%     | 21     | 16      | ~1.1 min | 75s  | $0.30 | $0.340 |
| sonnet-4.5 | medium | kv_colon_space | **126** | 67%     | 29     | 19      | ~1.2 min | 82s  | $0.37 | $0.419 |
| sonnet-4.5 | medium | markdown_table | **126** | 67%     | 22     | 16      | ~1.2 min | 82s  | $0.32 | $0.363 |
| sonnet-4.5 | medium | csv_quoted     | **120** | 63%     | 21     | 14      | ~1.0 min | 71s  | $0.29 | $0.345 |
| sonnet-4.5 | medium | yaml           | **120** | 63%     | 33     | 15      | ~1.1 min | 79s  | $0.32 | $0.381 |
| sonnet-4.5 | medium | toml           | **115** | 61%     | 30     | 14      | ~1.0 min | 75s  | $0.31 | $0.385 |
| sonnet-4.5 | medium | xml            | **99**  | 52%     | 35     | 12      | ~1.0 min | 87s  | $0.33 | $0.476 |

**Total: 56 tests** (7 models x 8 formats)

### 5.2 Best Format Per Model (Summary)

| Model        | Best Format | Scale | Worst Format   | Scale | Ratio |
|--------------|-------------|-------|----------------|-------|-------|
| gpt-5.5      | toml        | 828   | xml            | 375   | 2.2x  |
| gpt-5.4      | json        | 702   | kv_colon_space | 359   | 2.0x  |
| gpt-5-mini   | yaml/kv     | 500   | markdown_table | 163   | 3.1x  |
| gpt-5        | yaml        | 333   | markdown_table | 83    | 4.0x  |
| gpt-5.2      | csv_quoted  | 268   | toml           | 46    | 5.8x  |
| opus-4.5     | json        | 265   | csv_quoted     | 171   | 1.5x  |
| sonnet-4.5   | json        | 189   | xml            | 99    | 1.9x  |

### 5.3 Format Rankings Per Model

```
gpt-5.5:       toml (828) > yaml (675) > markdown (627) > kv (588) > csv (494) > csv_q (491) > json (430) > xml (375)
gpt-5.4:       json (702) > markdown (554) > xml (546) > csv=csv_q=toml=yaml (523) > kv (359)
gpt-5-mini:    kv=yaml (500) > csv_q (437) > json (335) > xml=toml (296) > csv (194) > markdown (163)
gpt-5:         yaml (333) > xml (327) > json (249) > kv (238) > csv_q (227) > toml (216) > csv (166) > markdown (83)
gpt-5.2:       csv_q (268) > xml (261) > json (241) > csv (215) > markdown (154) > yaml (134) > kv (100) > toml (46)
opus-4.5:      json (265) > yaml (259) > csv (232) > kv (226) > markdown (221) > xml=toml (182) > csv_q (171)
sonnet-4.5:    json (189) > csv=kv=markdown (126) > csv_q=yaml (120) > toml (115) > xml (99)
```

### 5.4 Token Efficiency vs Scale (csv=1.00x reference)

```
gpt-5.5:       csv (494) > xml (375) - csv 1.3x better (reversal from older GPT)
gpt-5.4:       csv (523) < xml (546) - xml 1.04x better
gpt-5-mini:    csv (194) < xml (296) - xml 1.5x better despite 2x tokens
gpt-5:         csv (166) < xml (327) - xml 2.0x better
gpt-5.2:       csv (215) < xml (261) - xml 1.2x better
opus-4.5:      csv (232) > xml (182) - csv 1.3x better
sonnet-4.5:    csv (126) > xml (99) - csv 1.3x better
```

### 5.5 Cost Efficiency (CPKC - Cost Per Kilo Cells)

| Model        | Best CPKC Format | CPKC   | Scale |
|--------------|------------------|--------|-------|
| gpt-5-mini   | csv_quoted       | $0.016 | 437   |
| gpt-5-mini   | yaml             | $0.017 | 500   |
| gpt-5        | yaml             | $0.090 | 333   |
| gpt-5.2      | csv_quoted       | $0.101 | 268   |
| gpt-5.5      | csv              | $0.124 | 494   |
| gpt-5.4      | kv_colon_space   | $0.131 | 359   |
| sonnet-4.5   | csv              | $0.340 | 126   |
| opus-4.5     | csv              | $0.566 | 232   |

## 6. Data Sources

- Test results stored in `_TestsAndResults/` subfolders as `scale_limit_result.json`
- Format-specific config templates: `test-config-template-{format}.json`
- Test execution scripts: `_Scripts/03_find_scale_limit.py`

## 7. Document History

**[2026-05-22 18:50]**
- Initial document created from restructuring of `_INFO_FormatComparison.md` and `_TEST_FormatComparison.md`
- Contains: all 56 test results, format rankings, token efficiency analysis, cost efficiency
- Follows 4-document methodology per `_INFO_LLM_TEST_METHODOLOGY.md [TBLF-IN04]`
