<DevSystem MarkdownTablesAllowed=true />

# INFO: LLM Data Processing Benchmark Landscape

**Doc ID**: DATBMRS-IN01
**Goal**: Identify all external benchmarks measuring data handling capability of reasoning models (OpenAI/Anthropic), to derive testable hypotheses for our own research

## Filtering Criteria

Included benchmarks must satisfy ALL of:
1. Tests reasoning models (gpt-5 family, Claude thinking models) - NOT temperature-only models
2. Measures data processing, analysis, extraction, or tabular comprehension
3. Methodology is documented and replicatable
4. Considers at least one of: data format, reasoning effort, context scale, structured data

Excluded:
- Saturated benchmarks (MMLU 90%+, HellaSwag 95%+)
- Pure coding benchmarks (SWE-bench) unless data processing component
- Pure browsing/search (BrowseComp)
- Safety/alignment evaluations
- Benchmarks testing only non-reasoning models (gpt-4o family, base LLMs)

## Benchmark Landscape Overview

### Category A: Tabular Data Comprehension

**A1. TQA-Bench** (Multi-Table Question Answering)
- **Source**: Qiu et al. 2024 (arXiv:2411.19504)
- **What it tests**: LLM ability to answer questions requiring reasoning across multiple related tables (joins, aggregation, symbolic reasoning)
- **Scale testing**: Explicitly varies context size (number of tables, rows)
- **Relevance to us**: Directly measures tabular comprehension at scale - same construct as our tests
- **Models tested**: GPT-4o, Claude, Gemini (likely updated for reasoning models)
- **Deep-research priority**: HIGH

**A2. TAT-QA / TAT-DQA** (Tabular And Textual QA)
- **Source**: Zhu et al. 2021/2022, TAT-LLM (2024, ICLR 2025)
- **What it tests**: Hybrid reasoning over tables + text in financial documents
- **Reasoning requirement**: Discrete reasoning (arithmetic, comparison, counting) over structured data
- **Relevance to us**: Tests data extraction + reasoning from structured formats
- **Deep-research priority**: MEDIUM (finance-specific, may not generalize)

**A3. SciTaRC** (Scientific Tabular Reasoning and Comprehension)
- **Source**: arXiv:2603.08910 (2026)
- **What it tests**: QA on scientific tabular data requiring multi-step reasoning
- **Relevance to us**: Scientific domain with complex table structures
- **Deep-research priority**: LOW (very new, may not have reasoning model results)

### Category B: Long Context + Data Retrieval

**B1. BABILong** (Long Context Reasoning)
- **Source**: Kuratov et al. 2024 (NeurIPS 2024, arXiv:2406.10149)
- **What it tests**: Reasoning capability degradation as context length increases (up to 10M tokens)
- **Key insight**: Tasks require reasoning IN context, not just retrieval
- **Relevance to us**: Our finding that "attention, not tokens" is the bottleneck at <10% context utilization directly parallels this benchmark's design
- **Models tested**: GPT-4, Claude, Gemini, Llama, Mistral
- **Deep-research priority**: HIGH

**B2. NoLiMa** (Long Context Beyond Literal Matching)
- **Source**: arXiv:2502.05167 (2025)
- **What it tests**: Comprehension (not just retrieval) in long contexts. Goes beyond Needle in a Haystack by requiring semantic understanding
- **Relevance to us**: Our models fail at comprehension, not retrieval - this benchmark isolates exactly that distinction
- **Deep-research priority**: HIGH

**B3. Michelangelo** (Latent Structure Queries)
- **Source**: Vodrahalli et al. 2024 (arXiv:2409.12640)
- **What it tests**: Long context evaluation via "latent structure queries" - requires understanding implicit patterns in data
- **Relevance to us**: Referenced in Anthropic Claude Opus 4.6 system card
- **Deep-research priority**: MEDIUM

**B4. LIFBench** (Instruction Following in Long Context)
- **Source**: ECNU/iQIYI 2024 (arXiv:2411.07037)
- **Already in our research**: Referenced in `_INFO_FormatComparison.md [TBLF-IN02]`
- **Key finding**: Format capability most stable across context lengths; Recognition degrades most
- **Deep-research priority**: LOW (already analyzed)

### Category C: Reasoning Effort / Thinking Budget Impact

**C1. OpenAI Reasoning Effort Evaluations**
- **Source**: OpenAI system cards (GPT-5, GPT-5.2, GPT-5.5)
- **What it tests**: Same benchmarks run at different reasoning effort levels (low/medium/high/xhigh)
- **Benchmarks used**: GPQA Diamond, AIME 2025, SimpleQA, SWE-bench at varied effort
- **Relevance to us**: We tested effort impact on data extraction (10x for gpt-5-mini). OpenAI tests it on reasoning tasks - are the scaling curves similar?
- **Key data point**: GPT-5.5 evals "run with reasoning effort set to xhigh" (from introduction page)
- **Deep-research priority**: HIGH

**C2. Lineage-bench** (Logical Reasoning at Varied Effort)
- **Source**: Community benchmark (OpenAI community forum, 2025)
- **What it tests**: Logical reasoning on lineage relationship graphs, explicitly tested at different reasoning effort levels
- **Key finding**: GPT-5.2 performs "much worse than GPT-5.1" at medium/high, only matches at xhigh
- **Relevance to us**: Same phenomenon as our gpt-5.2 result (215 rows vs gpt-5-mini's 500) - regression in newer models
- **Deep-research priority**: MEDIUM

**C3. Anthropic Extended Thinking Research**
- **Source**: Anthropic 2025 ("Visible Extended Thinking" paper)
- **What it tests**: How thinking budget (token count allocated to reasoning) affects accuracy
- **Key finding**: "Math accuracy improves predictably with thinking budget"
- **Relevance to us**: We found 10x improvement from low to high effort on gpt-5-mini. Anthropic studied this systematically
- **Deep-research priority**: HIGH

### Category D: Agentic Data Processing

**D1. MCP Atlas** (Scale AI)
- **Source**: Scale AI SEAL Leaderboard (2025-2026, updated April 2026)
- **What it tests**: Model ability to perform data analysis tasks using tool calls (MCP protocol). Evaluates data processing in agentic context
- **Scoring**: Judge-based evaluation, 100 max tool calls per task
- **Relevance to us**: Tests data ANALYSIS capability (not just extraction). Used by OpenAI for GPT-5.5 benchmarking
- **Models tested**: 18+ models including GPT-5.5, Claude
- **Deep-research priority**: HIGH

**D2. Tau2-bench** (Tool-Agent-User Interaction)
- **Source**: Sierra Research 2024/2025 (arXiv:2406.12045), updated 2025
- **What it tests**: Agent interaction with databases across domains (airline, retail, banking)
- **Relevance to us**: Tests structured data operations in realistic scenarios. Referenced in OpenAI GPT-5.5 results
- **Domains**: Airline reservation, retail, banking - all structured data tasks
- **Deep-research priority**: MEDIUM (more agentic than pure data comprehension)

### Category E: Provider-Specific Methodology

**E1. OpenAI Model Card Benchmark Suite**
- **Source**: OpenAI system cards (GPT-5, GPT-5.2, GPT-5.5)
- **Standard benchmarks used**: GPQA Diamond, AIME 2025, SimpleQA, Humanity's Last Exam, FrontierMath
- **Data-relevant subset**: SimpleQA (factual accuracy), MCP Atlas (data analysis)
- **Methodology**: Tests at specific effort levels, reports "research environment" conditions
- **Deep-research priority**: HIGH (understanding their methodology informs our design)

**E2. Anthropic Model Card Benchmark Suite**
- **Source**: Anthropic system cards (Opus 4.5, Opus 4.6, Opus 4.7/Mythos)
- **Standard benchmarks used**: GPQA Diamond, HLE, Michelangelo, safety evals
- **Data-relevant subset**: Michelangelo (long context structure), domain-specific evals
- **Methodology**: Tests with extended thinking enabled, adaptive thinking modes
- **Deep-research priority**: HIGH (understanding their methodology informs our design)

## Proposed Deep-Research Topics

Based on landscape analysis, these topics should each be researched independently:

| # | Topic | Priority | Addresses |
|---|-------|----------|-----------|
| 1 | TQA-Bench methodology and results for reasoning models | HIGH | DATBMRS-PR-0001, PR-0003 |
| 2 | BABILong: context length vs reasoning degradation | HIGH | DATBMRS-PR-0001 |
| 3 | NoLiMa: comprehension vs retrieval in long context | HIGH | DATBMRS-PR-0001 |
| 4 | OpenAI reasoning effort scaling (system card methodology) | HIGH | DATBMRS-PR-0002, PR-0004 |
| 5 | Anthropic extended thinking research and scaling laws | HIGH | DATBMRS-PR-0002, PR-0004 |
| 6 | MCP Atlas: agentic data analysis benchmark methodology | HIGH | DATBMRS-PR-0001, PR-0002 |
| 7 | Lineage-bench and effort-level regression in newer models | MEDIUM | DATBMRS-PR-0004 |
| 8 | Tau2-bench: structured data operations in agent scenarios | MEDIUM | DATBMRS-PR-0001 |

**Excluded from deep-research** (already in our research or not meeting criteria):
- LIFBench (already analyzed in TBLF-IN02)
- Sclar et al. 2024, Microsoft/MIT 2024, Microsoft CFPO 2025 (already in TBLF-IN02)
- SciTaRC (too new, no reasoning model results)
- TAT-QA (finance-specific, less generalizable)

## Correlation with Our Results

| Our Finding | Potentially Correlated Benchmark |
|-------------|----------------------------------|
| Attention bottleneck at <10% context | BABILong, NoLiMa |
| 10x improvement from effort low->high | OpenAI effort evals, Anthropic thinking research, Lineage-bench |
| 5.8x format sensitivity | TQA-Bench (if format-aware), MCP Atlas |
| Comprehension > truncation as failure mode | NoLiMa (tests comprehension explicitly) |
| gpt-5.2 regression vs gpt-5-mini | Lineage-bench (confirmed same pattern) |
| Claude mid-range despite thinking budget | Anthropic extended thinking scaling |

## Next Steps

1. User confirms deep-research topic list and priority order
2. Execute `/deep-research` for each topic (starting with HIGH priority)
3. After all topics researched, synthesize into testable hypotheses (DATBMRS-PR-0005)
4. Map hypotheses to our existing test pipeline capabilities

## Document History

**[2026-05-22 12:45]**
- Initial landscape analysis from web research
- Identified 12 benchmarks across 5 categories
- Proposed 8 deep-research topics
