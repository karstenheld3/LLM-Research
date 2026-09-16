<DevSystem MarkdownTablesAllowed=true />

# INFO: Format Comparison - Test Results

**Doc ID**: TBLF-IN05
**Goal**: Collect all test result data from format comparison experiments (63 tests across 8 models and 8 formats)
**Timeline**: Created 2026-05-22 (data collected 2026-03-09 to 2026-05-30)

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
- **Filter**: clearance IN [Level 3, Level 4, Level 5] AND salary >= 150000
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
- Model (8): gpt-5.5, gpt-5.4, gpt-5-mini, gpt-5, gpt-5.2, claude-opus-4.8, claude-opus-4.5, claude-sonnet-4.5

**Controlled variables:**
- Column count: 7
- Filter complexity: 2 conditions (IN list + threshold)
- Adversarial content: ~20%
- Seed: 42
- Verification runs: 3 per iteration
- Reasoning effort: medium (except gpt-5: low, opus-4.8: high)

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

### 5.1 All Tests (63 tests, sorted by model then scale limit)

**Note**: opus-4.8 yaml test stopped at 1107 rows (passed at 738) due to endless reasoning tokens consuming budget without producing output. Same Anthropic adaptive thinking issue as opus-4.7 high in Test 01. 7/8 formats shown.

<!-- AUTO:section-5.1:start -->
| Model      | Effort | Format         | Scale   | vs Best | In (K) | Out (K) | Time     | TPKC | Cost  | CPKC   |
|------------|--------|----------------|---------|---------|--------|---------|----------|------|-------|--------|
| gpt-5.5    | medium | toml           | **828**  | 100%    | 173    | 52      | ~1.0 min | 11s  | $0.81 | $0.139 |
| gpt-5.5    | medium | yaml           | **675**  | 82%     | 147    | 45      | ~59 sec  | 12s  | $0.69 | $0.147 |
| gpt-5.5    | medium | markdown_table | **627**  | 76%     | 88     | 43      | ~42 sec  | 10s  | $0.58 | $0.131 |
| gpt-5.5    | medium | kv_colon_space | **588**  | 71%     | 115    | 38      | ~36 sec  | 9s   | $0.57 | $0.138 |
| gpt-5.5    | medium | csv            | **494**  | 60%     | 68     | 35      | ~42 sec  | 12s  | $0.46 | $0.133 |
| gpt-5.5    | medium | csv_quoted     | **491**  | 59%     | 70     | 35      | ~42 sec  | 12s  | $0.46 | $0.135 |
| gpt-5.5    | medium | json           | **430**  | 52%     | 110    | 29      | ~42 sec  | 14s  | $0.47 | $0.157 |
| gpt-5.5    | medium | xml            | **375**  | 45%     | 110    | 26      | ~30 sec  | 12s  | $0.45 | $0.170 |
|            |        |                |         |         |        |         |          |      |       |        |
| gpt-5.4    | medium | json           | **702**  | 100%    | 179    | 65      | ~1.4 min | 17s  | $0.24 | $0.048 |
| gpt-5.4    | medium | markdown_table | **554**  | 79%     | 78     | 56      | ~1.1 min | 17s  | $0.17 | $0.044 |
| gpt-5.4    | medium | xml            | **546**  | 78%     | 159    | 55      | ~1.2 min | 18s  | $0.20 | $0.053 |
| gpt-5.4    | medium | csv            | **523**  | 75%     | 72     | 43      | ~49 sec  | 13s  | $0.14 | $0.038 |
| gpt-5.4    | medium | csv_quoted     | **523**  | 75%     | 74     | 46      | ~56 sec  | 15s  | $0.15 | $0.040 |
| gpt-5.4    | medium | toml           | **523**  | 75%     | 110    | 44      | ~58 sec  | 16s  | $0.16 | $0.043 |
| gpt-5.4    | medium | yaml           | **523**  | 75%     | 115    | 43      | ~51 sec  | 14s  | $0.16 | $0.042 |
| gpt-5.4    | medium | kv_colon_space | **359**  | 51%     | 71     | 34      | ~39 sec  | 16s  | $0.11 | $0.045 |
|            |        |                |         |         |        |         |          |      |       |        |
| gpt-5-mini | medium | kv_colon_space | **500**  | 100%    | 98     | 42      | ~1.1 min | 20s  | $0.02 | $0.005 |
| gpt-5-mini | medium | yaml           | **500**  | 100%    | 110    | 44      | ~1.5 min | 25s  | $0.02 | $0.006 |
| gpt-5-mini | medium | csv_quoted     | **437**  | 87%     | 62     | 39      | ~1.1 min | 22s  | $0.02 | $0.005 |
| gpt-5-mini | medium | json           | **335**  | 67%     | 86     | 35      | ~1.1 min | 27s  | $0.02 | $0.006 |
| gpt-5-mini | medium | toml           | **296**  | 59%     | 63     | 29      | ~52 sec  | 25s  | $0.01 | $0.006 |
| gpt-5-mini | medium | xml            | **296**  | 59%     | 87     | 42      | ~1.1 min | 31s  | $0.02 | $0.008 |
| gpt-5-mini | medium | csv            | **194**  | 39%     | 28     | 27      | ~55 sec  | 40s  | $0.01 | $0.007 |
| gpt-5-mini | medium | markdown_table | **163**  | 33%     | 24     | 22      | ~39 sec  | 34s  | $0.01 | $0.007 |
|            |        |                |         |         |        |         |          |      |       |        |
| gpt-5      | low    | yaml           | **333**  | 100%    | 73     | 38      | ~1.0 min | 26s  | $0.08 | $0.033 |
| gpt-5      | low    | xml            | **327**  | 98%     | 96     | 32      | ~50 sec  | 22s  | $0.07 | $0.032 |
| gpt-5      | low    | json           | **249**  | 75%     | 64     | 32      | ~46 sec  | 27s  | $0.07 | $0.039 |
| gpt-5      | low    | kv_colon_space | **238**  | 71%     | 47     | 29      | ~38 sec  | 23s  | $0.06 | $0.035 |
| gpt-5      | low    | csv_quoted     | **227**  | 68%     | 33     | 23      | ~2.7 min | 102s | $0.16 | $0.101 |
| gpt-5      | low    | toml           | **216**  | 65%     | 46     | 23      | ~37 sec  | 25s  | $0.05 | $0.032 |
| gpt-5      | low    | csv            | **166**  | 50%     | 24     | 21      | ~48 sec  | 41s  | $0.04 | $0.034 |
| gpt-5      | low    | markdown_table | **83**   | 25%     | 13     | 13      | ~36 sec  | 62s  | $0.02 | $0.043 |
|            |        |                |         |         |        |         |          |      |       |        |
| gpt-5.2    | medium | csv_quoted     | **268**  | 100%    | 39     | 20      | ~22 sec  | 12s  | $0.06 | $0.031 |
| gpt-5.2    | medium | xml            | **261**  | 97%     | 77     | 24      | ~31 sec  | 17s  | $0.08 | $0.042 |
| gpt-5.2    | medium | json           | **241**  | 90%     | 62     | 20      | ~26 sec  | 15s  | $0.06 | $0.038 |
| gpt-5.2    | medium | csv            | **215**  | 80%     | 30     | 19      | ~23 sec  | 15s  | $0.05 | $0.035 |
| gpt-5.2    | medium | markdown_table | **154**  | 57%     | 22     | 18      | ~22 sec  | 20s  | $0.05 | $0.046 |
| gpt-5.2    | medium | yaml           | **134**  | 50%     | 30     | 10      | ~12 sec  | 13s  | $0.03 | $0.035 |
| gpt-5.2    | medium | kv_colon_space | **100**  | 37%     | 20     | 6       | ~7 sec   | 10s  | $0.02 | $0.030 |
| gpt-5.2    | medium | toml           | **46**   | 17%     | 11     | 3       | ~4 sec   | 14s  | $0.01 | $0.034 |
|            |        |                |         |         |        |         |          |      |       |        |
| opus-4.8   | high   | csv            | **630**  | 100%    | 156    | 75      | ~1.1 min | 15s  | $0.88 | $0.200 |
| opus-4.8   | high   | toml           | **622**  | 99%     | 223    | 76      | ~1.1 min | 16s  | $1.00 | $0.230 |
| opus-4.8   | high   | csv_quoted     | **607**  | 96%     | 151    | 76      | ~1.1 min | 16s  | $0.88 | $0.208 |
| opus-4.8   | high   | json           | **576**  | 91%     | 231    | 86      | ~1.7 min | 25s  | $1.10 | $0.274 |
| opus-4.8   | high   | kv_colon_space | **545**  | 87%     | 184    | 66      | ~1.0 min | 16s  | $0.85 | $0.224 |
| opus-4.8   | high   | xml            | **545**  | 87%     | 245    | 69      | ~1.1 min | 17s  | $0.98 | $0.258 |
| opus-4.8   | high   | markdown_table | **468**  | 74%     | 118    | 59      | ~54 sec  | 16s  | $0.69 | $0.210 |
|            |        |                |         |         |        |         |          |      |       |        |
| opus-4.5   | medium | json           | **265**  | 100%    | 81     | 30      | ~34 sec  | 18s  | $0.38 | $0.206 |
| opus-4.5   | medium | yaml           | **259**  | 98%     | 69     | 29      | ~37 sec  | 20s  | $0.36 | $0.199 |
| opus-4.5   | medium | csv            | **232**  | 88%     | 38     | 29      | ~32 sec  | 20s  | $0.30 | $0.188 |
| opus-4.5   | medium | kv_colon_space | **226**  | 85%     | 51     | 30      | ~32 sec  | 20s  | $0.33 | $0.210 |
| opus-4.5   | medium | markdown_table | **221**  | 83%     | 38     | 28      | ~32 sec  | 21s  | $0.29 | $0.190 |
| opus-4.5   | medium | toml           | **182**  | 69%     | 47     | 27      | ~34 sec  | 27s  | $0.30 | $0.235 |
| opus-4.5   | medium | xml            | **182**  | 69%     | 63     | 29      | ~32 sec  | 25s  | $0.35 | $0.275 |
| opus-4.5   | medium | csv_quoted     | **171**  | 65%     | 29     | 27      | ~30 sec  | 25s  | $0.27 | $0.229 |
|            |        |                |         |         |        |         |          |      |       |        |
| sonnet-4.5 | medium | json           | **189**  | 100%    | 58     | 22      | ~30 sec  | 23s  | $0.17 | $0.126 |
| sonnet-4.5 | medium | csv            | **126**  | 67%     | 21     | 16      | ~21 sec  | 24s  | $0.10 | $0.115 |
| sonnet-4.5 | medium | kv_colon_space | **126**  | 67%     | 29     | 19      | ~24 sec  | 27s  | $0.13 | $0.143 |
| sonnet-4.5 | medium | markdown_table | **126**  | 67%     | 22     | 16      | ~20 sec  | 23s  | $0.10 | $0.116 |
| sonnet-4.5 | medium | csv_quoted     | **120**  | 63%     | 21     | 14      | ~18 sec  | 22s  | $0.09 | $0.110 |
| sonnet-4.5 | medium | yaml           | **120**  | 63%     | 33     | 15      | ~19 sec  | 22s  | $0.11 | $0.128 |
| sonnet-4.5 | medium | toml           | **115**  | 61%     | 30     | 14      | ~18 sec  | 22s  | $0.10 | $0.124 |
| sonnet-4.5 | medium | xml            | **99**   | 52%     | 35     | 12      | ~19 sec  | 28s  | $0.10 | $0.139 |

**Total: 63 tests** (8 models x 8 formats)
<!-- AUTO:section-5.1:end -->

### 5.2 Best Format Per Model (Summary)

<!-- AUTO:section-5.2:start -->
| Model        | Best Format | Scale | Worst Format   | Scale | Ratio |
|--------------|-------------|-------|----------------|-------|-------|
| gpt-5.5      | toml        | 828   | xml            | 375   | 2.2x  |
| gpt-5.4      | json        | 702   | kv_colon_space | 359   | 2.0x  |
| gpt-5-mini   | kv_colon_space | 500   | markdown_table | 163   | 3.1x  |
| gpt-5        | yaml        | 333   | markdown_table | 83    | 4.0x  |
| gpt-5.2      | csv_quoted  | 268   | toml           | 46    | 5.8x  |
| opus-4.8     | csv         | 630   | markdown_table | 468   | 1.3x  |
| opus-4.5     | json        | 265   | csv_quoted     | 171   | 1.5x  |
| sonnet-4.5   | json        | 189   | xml            | 99    | 1.9x  |
<!-- AUTO:section-5.2:end -->

### 5.3 Format Rankings Per Model

<!-- AUTO:section-5.3:start -->
```
gpt-5.5:       toml (828) > yaml (675) > markdown_table (627) > kv_colon_space (588) > csv (494) > csv_quoted (491) > json (430) > xml (375)
gpt-5.4:       json (702) > markdown_table (554) > xml (546) > csv (523) > csv_quoted (523) > toml (523) > yaml (523) > kv_colon_space (359)
gpt-5-mini:    kv_colon_space (500) > yaml (500) > csv_quoted (437) > json (335) > toml (296) > xml (296) > csv (194) > markdown_table (163)
gpt-5:         yaml (333) > xml (327) > json (249) > kv_colon_space (238) > csv_quoted (227) > toml (216) > csv (166) > markdown_table (83)
gpt-5.2:       csv_quoted (268) > xml (261) > json (241) > csv (215) > markdown_table (154) > yaml (134) > kv_colon_space (100) > toml (46)
opus-4.8:      csv (630) > toml (622) > csv_quoted (607) > json (576) > kv_colon_space (545) > xml (545) > markdown_table (468)
opus-4.5:      json (265) > yaml (259) > csv (232) > kv_colon_space (226) > markdown_table (221) > toml (182) > xml (182) > csv_quoted (171)
sonnet-4.5:    json (189) > csv (126) > kv_colon_space (126) > markdown_table (126) > csv_quoted (120) > yaml (120) > toml (115) > xml (99)
```
<!-- AUTO:section-5.3:end -->

### 5.4 Token Efficiency vs Scale (csv=1.00x reference)

<!-- AUTO:section-5.4:start -->
```
gpt-5.5:       csv (494) vs xml (375) - csv 1.3x better
gpt-5.4:       csv (523) vs xml (546) - xml 1.0x better despite 2x tokens
gpt-5-mini:    csv (194) vs xml (296) - xml 1.5x better despite 2x tokens
gpt-5:         csv (166) vs xml (327) - xml 2.0x better despite 2x tokens
gpt-5.2:       csv (215) vs xml (261) - xml 1.2x better despite 2x tokens
opus-4.8:      csv (630) vs xml (545) - csv 1.2x better
opus-4.5:      csv (232) vs xml (182) - csv 1.3x better
sonnet-4.5:    csv (126) vs xml (99) - csv 1.3x better
```
<!-- AUTO:section-5.4:end -->

### 5.5 Cost Efficiency (CPKC - Cost Per Kilo Cells)

<!-- AUTO:section-5.5:start -->
| Model        | Best CPKC Format | CPKC   | Scale |
|--------------|------------------|--------|-------|
| gpt-5.5      | markdown_table   | $0.131 | 627   |
| gpt-5.4      | csv              | $0.038 | 523   |
| gpt-5-mini   | csv_quoted       | $0.005 | 437   |
| gpt-5        | toml             | $0.032 | 216   |
| gpt-5.2      | kv_colon_space   | $0.030 | 100   |
| opus-4.8     | csv              | $0.200 | 630   |
| opus-4.5     | csv              | $0.188 | 232   |
| sonnet-4.5   | csv_quoted       | $0.110 | 120   |
<!-- AUTO:section-5.5:end -->

## 6. Data Sources and Pipeline

- **Result files**: `_TestsAndResults/{config_folder}/scale_limit_result.json` (62 files)
- **Overrides**: `_Scripts/overrides.json` (1 record: gpt-5 csv_quoted, test folder missing)
- **Config templates**: `test-config-template-{format}.json` (8 formats)
- **Aggregation**: `_Scripts/06_aggregate_results.py` reads all results + overrides, generates `all_results.json` and `all_results.md`, updates AUTO markers in this file
- **Pipeline runner**: `_Scripts/run_pipeline.ps1 -SkipTest` to re-aggregate and update

**AUTO markers**: Sections 5.1-5.5 are managed by `06_aggregate_results.py`. Manual edits between `<!-- AUTO:section-X.X:start/end -->` markers will be overwritten on next pipeline run.

## 7. Document History

**[2026-05-30 20:00]**
- Added: claude-opus-4-8 (high effort) results: 7/8 formats (yaml incomplete)
- Changed: Test count 56 → 63, model count 7 → 8
- Changed: Pipeline scripts updated with opus-4.8 display name and sort order

**[2026-05-22 19:15]**
- Added: AUTO markers on sections 5.1-5.5
- Added: Pipeline scripts (`06_aggregate_results.py`, `run_pipeline.ps1`, `overrides.json`)
- Changed: CPKC values now use per-request cost (was total test cost)
- Changed: Token counts (In/Out K) now populated from actual result data for all models
- Fixed: gpt-5 csv_quoted (scale=227) added via overrides.json (test folder missing)

**[2026-05-22 18:50]**
- Initial document created from restructuring of `_INFO_FormatComparison.md` and `_TEST_FormatComparison.md`
- Contains: all 56 test results, format rankings, token efficiency analysis, cost efficiency
- Follows 4-document methodology per `_INFO_LLM_TEST_METHODOLOGY.md [TBLF-IN04]`
