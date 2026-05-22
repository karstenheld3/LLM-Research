<DevSystem MarkdownTablesAllowed=true />

# INFO: LLM Data Processing Benchmark Survey

**Doc ID**: DATBMRS-IN02
**Goal**: Survey 12 benchmarks on methodology, replicability, and relevance to our tabular data format research
**Strategy**: MCPI (exhaustive)
**Domain**: SOFTWARE
**Timeline**: Created 2026-05-22, 1 update, range 2026-05-22
**Sources accessed**: 2026-05-22 (all URLs)

## Table of Contents

1. Summary
2. Our Research Context
3. Benchmark Classification
4. Benchmarks 1-12 (individual assessments across dimensions A-G)
5. Comparison Matrix
6. Replicability Ranking
7. Gap Analysis
8. Variable Coverage Matrix
9. Recommended Deep-Dives
10. Corroborating Observations
11. Document History

## Summary

Key findings from surveying 12 benchmarks across 5 tiers:

- **Only TQA-Bench tests format (Markdown vs CSV)** - but limited to 2 formats; our 8-format comparison is unique
- **No benchmark uses binary search for scale limits** - all use fixed difficulty levels
- **Only OpenAI/Anthropic system cards test reasoning effort explicitly** - no independent benchmark parameterizes effort
- **TQA-Bench is most directly comparable** to our tests (multi-table QA with scalable context, public dataset, open code)
- **NoLiMa directly validates** our "comprehension > retrieval" finding - models fail at semantic association even in short contexts
- **Anthropic's extended thinking shows logarithmic scaling** of accuracy with thinking tokens - matches our 10x improvement pattern
- **Most benchmarks lack reasoning model results** - tested GPT-4o era models, not gpt-5 family

## Our Research Context

This survey evaluates external benchmarks against our empirical research on LLM data processing capability. Our methodology:

- **Task**: Filtered extraction from tabular data (compound filter, exact-match evaluation)
- **Scale discovery**: Binary search for maximum reliable row count (3/3 runs at 100% accuracy)
- **Formats tested**: 8 (csv_quoted, csv_unquoted, json, xml, yaml, markdown_table, key_value, toml)
- **Reasoning effort**: low / medium / high on same model
- **Models**: OpenAI gpt-5 family (mini, 5, 5.2, 5.4, 5.5) and Anthropic Claude (haiku, sonnet, opus)

Key findings from our tests:

- Reasoning models outperform temperature models by 65-89x on data extraction
- Effort level produces up to 10x scale improvement (gpt-5-mini low=65 vs high=675+ rows)
- Format choice causes up to 5.8x scale difference (best vs worst format per model)
- Primary failure mode is comprehension (not truncation) at <10% context utilization
- Model family determines format preference (GPT prefers yaml/toml, Claude prefers json)
- Format preferences shift across model generations (gpt-5.4: json best; gpt-5.5: toml best)

## Benchmark Classification

**Comparability criterion**: Does the benchmark test a model's ability to process, comprehend, or extract from structured data in response to a prompt? Includes direct comprehension, code-mediated analysis, and long-context reasoning over data.

**Tiers:**

- **Tier 1a** - Direct Data Comprehension (benchmarks 1-2: TQA-Bench, TableBench). FULL depth on all dimensions A-G. Most comparable to our work.
- **Tier 1b** - Code-Mediated Data Analysis (benchmarks 3-4: DACO, InfiAgent-DABench). Full depth on A-D, lighter on E-G. Different construct but informs methodology.
- **Tier 2** - Long Context + Reasoning Degradation (benchmarks 5-7: BABILong, NoLiMa, HELMET). Full depth on B, C, F. Explains our "attention bottleneck" finding.
- **Tier 3** - Reasoning Effort / Thinking Budget Scaling (benchmarks 8-9: OpenAI Cards, Anthropic Extended Thinking). Full B, C, D, F. Directly relevant to our effort-scaling results.
- **Tier 4** - Agentic Data Processing (benchmarks 10-12: MCP Atlas, Tau-bench, DAComp). Dimensions B, F only. Different paradigm (tools/agents) but establishes ceiling.

## Benchmark 1: TQA-Bench

### A. Identity
- **Full name**: TQA-Bench: Evaluating LLMs for Multi-Table Question Answering with Scalable Context and Symbolic Extension
- **Authors**: Qiu et al. (Relaxed System Lab)
- **Date/Venue**: November 2024, arXiv:2411.19504
- **URLs**: Paper: arxiv.org/abs/2411.19504 | Code: github.com/Relaxed-System-Lab/TQA-Bench

### B. Goal and Scope
- **Capability**: Multi-table relational QA requiring reasoning across joined tables
- **Research question**: How do LLMs perform on complex multi-table QA as context scales?
- **Task types**: QA, aggregation, joins, symbolic reasoning across relational tables
- **Tests FORMAT?**: YES - compares Markdown vs CSV (Experiment 1, Section 4.1). Markdown wins consistently. See T01_TQAB-TQABench_2026-05-22/ for details.
- **Tests EFFORT?**: No
- **Tests SCALE?**: YES - explicitly varies context from 8K to 64K tokens

### C. Methodology
- **Task design**: Answer questions requiring reasoning across multiple related database tables
- **Input format**: Serialized relational tables (Markdown or CSV via pandas)
- **Multiple formats?**: YES - Markdown vs CSV tested (Experiment 1), then Markdown used for all subsequent experiments
- **Metrics**: Accuracy (exact match with symbolic extensions)
- **Samples**: Multiple database instances from real-world datasets (finance, healthcare, e-commerce)
- **Ground truth**: Deterministic SQL queries over source databases
- **Statistical rigor**: [PARTIAL] - systematic across context sizes
- **Binary search?**: No - fixed context size buckets (8K, 16K, 32K, 64K)

### D. Models Tested
- **OpenAI**: GPT-4o [NO-REASONING-DATA for gpt-5 family]
- **Anthropic**: Claude (version unspecified in abstract) [NO-REASONING-DATA for thinking models]
- **Reasoning vs non-reasoning**: Not distinguished
- **Effort levels**: Not tested

### E. Replicability Assessment
- **Dataset public?**: YES (github.com/Relaxed-System-Lab/TQA-Bench)
- **Code open-source?**: YES (same repo)
- **Our setup compatible?**: YES - API-based evaluation, Python
- **Estimated cost**: [UNKNOWN] - depends on number of samples per context size
- **Estimated time**: Hours (multiple API calls at 64K context)
- **Dependencies**: Python, LLM APIs
- **Known issues**: Symbolic extensions may need careful adaptation
- **Reproductions**: [UNKNOWN]

### F. Relevance to Our Research
- **Validates/contradicts**: Could validate our scale degradation findings if run with gpt-5 family
- **New variables?**: Multi-table joins (we test single-table extraction)
- **Pipeline adaptation?**: YES - could run their tasks through our API client
- **Gap filled**: Tests reasoning ACROSS tables, we test extraction FROM tables

### G. Limitations and Criticism
- **Weaknesses**: Only tests up to 64K tokens; our models handle 128K+ context windows
- **Saturation**: [UNKNOWN] - likely not saturated given task complexity
- **Contamination risk**: Low (uses sampling mechanism for unique instances)
- **Community criticism**: [UNKNOWN]

## Benchmark 2: TableBench

### A. Identity
- **Full name**: TableBench: A Comprehensive and Complex Benchmark for Table Question Answering
- **Authors**: Wu, Wang, Li, Yang, Duan et al.
- **Date/Venue**: August 2024 (arXiv:2408.09174), accepted AAAI 2025
- **URLs**: Paper: arxiv.org/abs/2408.09174 | Code: github.com/TableBench/TableBench | Site: tablebench.github.io

### B. Goal and Scope
- **Capability**: Comprehensive table QA across fact-checking, numerical reasoning, data analysis, visualization
- **Research question**: How large is the gap between LLMs and humans on complex table QA in real-world industrial scenarios?
- **Task types**: Fact verification, numerical reasoning, data analysis, chart generation (4 categories, 18 subcategories)
- **Tests FORMAT?**: No - tables presented in fixed format
- **Tests EFFORT?**: No
- **Tests SCALE?**: No - fixed table sizes (min 8 rows, 5 columns)

### C. Methodology
- **Task design**: Answer questions about tables requiring multi-step reasoning, generate charts from data
- **Input format**: Tables (fixed serialization) - sourced from WTQ, SQA, TabFact, FinQA, AIT-QA
- **Multiple formats?**: No
- **Metrics**: ROUGE-L for text answers, pass@1 for code/chart generation. Also GPT-4 judge and human evaluation for consistency
- **Samples**: 886 human-annotated samples across 18 fields, 20 topics
- **Ground truth**: Human-annotated with self-consistency mechanism (3 LLM agents + voting + manual review)
- **Statistical rigor**: Human annotation cost $12,000. Cross-validated with GPT-4 judge. Pearson Correlation Coefficient (PCC) consistency analysis
- **Binary search?**: No - fixed difficulty per category

### D. Models Tested
- **OpenAI**: GPT-3.5-Turbo, GPT-4-Turbo, GPT-4o [NO-REASONING-DATA for gpt-5]
- **Anthropic**: Not mentioned in original paper
- **Reasoning vs non-reasoning**: Not distinguished (pre-reasoning-model era)
- **Effort levels**: Not tested

### E. Replicability Assessment
- **Dataset public?**: YES (github.com/TableBench/TableBench)
- **Code open-source?**: YES (evaluation code + TableInstruct training data)
- **Our setup compatible?**: YES - API-based
- **Estimated cost**: Low-Medium (~886 samples, moderate context per sample)
- **Estimated time**: 2-4 hours with API
- **Dependencies**: Python, transformers (for open models), LLM APIs
- **Known issues**: ROUGE-L may not capture semantic equivalence well
- **Reproductions**: [UNKNOWN]

### F. Relevance to Our Research
- **Validates/contradicts**: Could show if our format findings extend to complex reasoning tasks (not just extraction)
- **New variables?**: Task complexity gradient (fact-checking is easy, chart generation is hard)
- **Pipeline adaptation?**: PARTIAL - we'd need to add their evaluation metrics
- **Gap filled**: Tests reasoning depth we don't measure (multi-step analytical reasoning)

### G. Limitations and Criticism
- **Weaknesses**: Small sample size (886); tables are relatively small; GPT-4 era models only
- **Saturation**: NOT saturated - even GPT-4 significantly below human performance
- **Contamination risk**: Moderate - sources from public datasets (WTQ, FinQA) which may be in training data
- **Community criticism**: Limited to tabular context; does not test format variation

## Benchmark 3: DACO

### A. Identity
- **Full name**: DACO: Towards Application-Driven and Comprehensive Data Analysis via Code Generation
- **Authors**: Xueqing Wu, Rui Zheng, Jingzhen Sha, Te-Lin Wu et al. (UCLA, Kai-Wei Chang group)
- **Date/Venue**: NeurIPS 2024, Datasets and Benchmarks Track
- **URLs**: Paper: proceedings.neurips.cc/paper/2024/... | Code: github.com/shirley-wu/daco | Site: shirley-wu.github.io/daco

### B. Goal and Scope
- **Capability**: End-to-end data analysis via CODE GENERATION (different construct from direct extraction)
- **Research question**: Can LLMs generate code to perform comprehensive data analysis on real-world databases?
- **Task types**: Code generation for data exploration, statistical analysis, visualization
- **Tests FORMAT?**: No
- **Tests EFFORT?**: No
- **Tests SCALE?**: [PARTIAL] - varies database complexity

### C. Methodology
- **Task design**: Given a database + analytical query, generate Python code that produces the correct analysis
- **Input format**: Database schema + natural language query (tables are accessed via code, not presented directly)
- **Multiple formats?**: No (code-mediated access)
- **Metrics**: Pair-wise comparison (LLM judge), automated execution correctness
- **Samples**: 440 databases, ~2K query-answer pairs (train/valid/test split), concentrated high-quality test set with human annotations
- **Ground truth**: Human-refined annotations + automated answer checking
- **Statistical rigor**: Multiple reasoning methods compared (zero-shot, prompt-based, fine-tuned)
- **Binary search?**: No

### D. Models Tested
- **OpenAI**: ChatGPT, GPT-4 [NO-REASONING-DATA]
- **Anthropic**: [UNKNOWN]
- **Reasoning vs non-reasoning**: Code generation improves performance significantly
- **Effort levels**: Not tested

### E. Replicability Assessment
- **Dataset public?**: YES (github.com/shirley-wu/daco)
- **Code open-source?**: YES
- **Our setup compatible?**: PARTIAL - requires code execution sandbox
- **Cost**: [UNKNOWN]
- **Dependencies**: Python, pandas, matplotlib, code execution environment
- **Reproductions**: [UNKNOWN]

### F. Relevance to Our Research
- **Validates/contradicts**: Different construct - tests code-generation ability not direct comprehension
- **New variables?**: Code as reasoning tool (our models extract directly)
- **Pipeline adaptation?**: Low - fundamentally different approach
- **Gap filled**: Shows that code-mediated analysis can bypass comprehension limitations

### G. Limitations
- **Weaknesses**: Code generation is a different capability than data comprehension
- **Saturation**: [UNKNOWN]
- **Contamination risk**: Moderate (databases from public sources)

## Benchmark 4: InfiAgent-DABench

### A. Identity
- **Full name**: InfiAgent-DABench: Evaluating Agents on Data Analysis Tasks
- **Authors**: Xueyu Hu, Ziyu Zhao, Shuang Wei et al.
- **Date/Venue**: January 2024 (arXiv:2401.05507)
- **URLs**: Paper: arxiv.org/abs/2401.05507 | Code: github.com/InfiAgent/InfiAgent | Site: infiagent.github.io

### B. Goal and Scope
- **Capability**: LLM AGENT performance on end-to-end data analysis with CSV files
- **Research question**: How well can LLM agents solve real-world data analysis tasks by interacting with an execution environment?
- **Task types**: Data analysis requiring code generation, execution, and iterative refinement
- **Tests FORMAT?**: No (CSV input only)
- **Tests EFFORT?**: No
- **Tests SCALE?**: [PARTIAL] - varies task complexity

### C. Methodology
- **Task design**: Agent receives CSV file + analytical question, must write and execute code to answer
- **Input format**: CSV files (311 unique files)
- **Multiple formats?**: No - CSV only
- **Metrics**: Accuracy of final answer (after code execution)
- **Samples**: DAEval: 257 tasks (closed-source test) + open split
- **Ground truth**: Human-verified answers
- **Statistical rigor**: 34 LLMs benchmarked
- **Binary search?**: No

### D. Models Tested
- **OpenAI**: GPT-3.5, GPT-4, GPT-4 Turbo [NO-REASONING-DATA]
- **Anthropic**: [UNKNOWN]
- **Reasoning vs non-reasoning**: Not distinguished
- **Effort levels**: Not tested

### E. Replicability Assessment
- **Dataset public?**: PARTIAL (open split available, closed-source test set exists)
- **Code open-source?**: YES (github.com/InfiAgent/InfiAgent)
- **Our setup compatible?**: PARTIAL - requires code execution sandbox (Docker)
- **Dependencies**: Python, Docker, pandas, multiple packages
- **Reproductions**: [UNKNOWN]

### F. Relevance to Our Research
- **Validates/contradicts**: Different construct (agent + code execution vs direct extraction)
- **New variables?**: Iterative refinement capability
- **Pipeline adaptation?**: Low
- **Gap filled**: Shows limitations of direct extraction (agents can overcome via code)

### G. Limitations
- **Weaknesses**: Agent framework conflates model ability with harness design
- **Saturation**: [UNKNOWN]
- **Contamination risk**: Low (original CSV files)

## Benchmark 5: BABILong

### A. Identity
- **Full name**: BABILong: Testing the Limits of LLMs with Long Context Reasoning-in-a-Haystack
- **Authors**: Yury Kuratov, Aydar Bulatov, Petr Anokhin, Ivan Rodkin et al.
- **Date/Venue**: NeurIPS 2024, Datasets and Benchmarks Track (arXiv:2406.10149)
- **URLs**: Paper: arxiv.org/abs/2406.10149 | Code: github.com/booydar/babilong

### B. Goal and Scope
- **Capability**: Reasoning capability DEGRADATION as context length increases
- **Research question**: Do LLMs actually reason in long contexts, or do they only retrieve?
- **Task types**: 20 bAbI tasks (fact chaining, counting, spatial reasoning, path finding) embedded in long irrelevant text
- **Tests FORMAT?**: No
- **Tests EFFORT?**: No
- **Tests SCALE?**: YES - systematically scales from 0 to 10M tokens

### C. Methodology
- **Task design**: bAbI reasoning tasks (facts like "Mary went to office") embedded in book text filler
- **Input format**: Natural language facts embedded in natural language text
- **Multiple formats?**: No (text only)
- **Metrics**: Accuracy per task type per context length
- **Samples**: Multiple bAbI tasks x multiple context lengths
- **Ground truth**: Deterministic (bAbI tasks have exact answers)
- **Statistical rigor**: Systematic length variation, multiple task types
- **Binary search?**: No - fixed context length levels

### D. Models Tested
- **OpenAI**: GPT-3.5, GPT-4 [NO-REASONING-DATA for gpt-5]
- **Anthropic**: Claude (version not specified)
- **Other**: Gemini, Llama, Mistral
- **Reasoning vs non-reasoning**: Not distinguished in original paper
- **Effort levels**: Not tested

### E. Replicability Assessment
- **Dataset public?**: YES (github.com/booydar/babilong)
- **Code open-source?**: YES
- **Our setup compatible?**: YES - API-based, Python
- **Cost**: Moderate-High (10M token contexts are expensive)
- **Time**: Hours to days depending on context sizes tested
- **Dependencies**: Python, LLM APIs
- **Reproductions**: [UNKNOWN]

### F. Relevance to Our Research
- **Validates/contradicts**: Validates our "attention bottleneck" finding - reasoning degrades before context window fills
- **New variables?**: Task complexity gradient (QA1 simple vs QA5 complex)
- **Pipeline adaptation?**: YES - could embed our extraction tasks in longer contexts
- **Gap filled**: Shows how reasoning degrades with scale (we show WHERE it breaks)

### G. Limitations
- **Weaknesses**: bAbI tasks are synthetic and simple; may not represent real data comprehension
- **Saturation**: Some models near-perfect on simple tasks (QA1) but fail on complex (QA5)
- **Contamination risk**: Low (bAbI embedded in book text creates novel combinations)

## Benchmark 6: NoLiMa

### A. Identity
- **Full name**: NoLiMa: Long-Context Evaluation Beyond Literal Matching
- **Authors**: Ali Modarressi, Hanieh Deilamsalehy, Franck Dernoncourt, Trung Bui, Ryan A. Rossi, Seunghyun Yoon, Hinrich Schutze
- **Date/Venue**: February 2025 (arXiv:2502.05167), ICML 2025 poster
- **URLs**: Paper: arxiv.org/abs/2502.05167

### B. Goal and Scope
- **Capability**: Long-context COMPREHENSION (not retrieval) - tests semantic association without literal matching
- **Research question**: When literal cues are removed, how well do models comprehend information in long contexts?
- **Task types**: Associative reasoning requiring world knowledge (1-hop and 2-hop)
- **Tests FORMAT?**: No
- **Tests EFFORT?**: PARTIAL - tested GPT-o1 and o3-mini (reasoning models) separately
- **Tests SCALE?**: YES - varies context length systematically

### C. Methodology
- **Task design**: Find "needle" in "haystack" where question and needle have ZERO literal overlap. Requires world-knowledge association (e.g., "Dresden" -> "Semper Opera House")
- **Input format**: Natural language (book snippets as haystack)
- **Multiple formats?**: No
- **Metrics**: Accuracy, effective length (context at which accuracy drops to 85% of base)
- **Samples**: 58 question-needle pairs x 26 placements x 5 haystacks = 7,540 tests per context length
- **Ground truth**: Deterministic (correct character name)
- **Statistical rigor**: HIGH - 7,540 tests per context length, systematic placement variation
- **Binary search?**: No - fixed context lengths (1K, 2K, 4K, 8K, 16K, 32K, 64K)

### D. Models Tested
- **OpenAI**: GPT-4o, GPT-4o Mini, GPT-o1, GPT-o3 Mini (REASONING MODELS TESTED)
- **Anthropic**: Claude 3.5 Sonnet
- **Other**: Gemini 1.5 Pro/Flash, Llama 3.x family, Mistral, Command R+, Jamba
- **Reasoning vs non-reasoning**: YES - separately evaluates o1 and o3-mini
- **Effort levels**: Not explicitly varied

### E. Replicability Assessment
- **Dataset public?**: [UNKNOWN] - paper describes methodology but no GitHub link found
- **Code open-source?**: [UNKNOWN]
- **Our setup compatible?**: YES if dataset available
- **Cost**: Moderate (7,540 tests per context length, but questions are short)
- **Time**: Hours per model per context length
- **Dependencies**: Python, LLM APIs
- **Reproductions**: [UNKNOWN]

### F. Relevance to Our Research
- **Validates/contradicts**: DIRECTLY VALIDATES our finding that models fail at comprehension, not retrieval. Models achieve <50% at 32K even with 128K context windows.
- **New variables?**: Hop count (1-hop vs 2-hop reasoning), template inversion (causal attention effects)
- **Pipeline adaptation?**: Could design similar "no literal match" variants of our extraction tasks
- **Gap filled**: Isolates comprehension from retrieval - explains WHY our models fail at <10% context utilization

### G. Limitations
- **Weaknesses**: Tests world-knowledge association, not structured data extraction specifically
- **Saturation**: NOT saturated - even GPT-4o degrades significantly beyond 8K
- **Contamination risk**: Low (randomized character names, book-snippet haystacks)
- **Key finding**: 10 of 12 models have effective length <= 2K tokens despite claiming 128K+

## Benchmark 7: HELMET

### A. Identity
- **Full name**: HELMET: How to Evaluate Long-context Models Effectively and Thoroughly
- **Authors**: Howard Yen, Tianyu Gao et al. (Princeton)
- **Date/Venue**: October 2024 (arXiv:2410.02694), ICLR 2025
- **URLs**: Paper: arxiv.org/abs/2410.02694

### B. Goal and Scope
- **Capability**: Holistic evaluation of long-context models across diverse real-world tasks
- **Research question**: Do synthetic benchmarks (RULER, Needle in a Haystack) predict real-world long-context performance?
- **Task types**: QA, summarization, Retrieval-Augmented Generation (RAG), many-shot In-Context Learning (ICL), code completion, re-ranking
- **Tests FORMAT?**: No
- **Tests EFFORT?**: No
- **Tests SCALE?**: YES - varies context length

### C. Methodology
- **Task design**: Multiple real-world tasks evaluated at different context lengths
- **Input format**: Various (documents, code, conversation histories)
- **Multiple formats?**: PARTIAL - different task types use different input types, but not as controlled variable
- **Metrics**: Task-specific (accuracy, F1, ROUGE depending on task)
- **Samples**: [PARTIAL] - multiple tasks with substantial test sets
- **Ground truth**: Task-specific
- **Statistical rigor**: Correlation analysis with synthetic benchmarks
- **Binary search?**: No

### D. Models Tested
- **OpenAI**: [PARTIAL]
- **Anthropic**: [PARTIAL]
- **Key finding**: RULER and NIAH scores do NOT correlate with HELMET scores
- **Effort levels**: Not tested

### E. Replicability Assessment
- **Dataset public?**: [UNKNOWN]
- **Code open-source?**: [UNKNOWN]
- **Our setup compatible?**: Likely YES
- **Reproductions**: Referenced by Stanford HELM project

### F. Relevance to Our Research
- **Validates/contradicts**: Validates that synthetic retrieval tests (NIAH) don't predict real performance - explains why models with large context windows still fail our tests
- **New variables?**: Task diversity as evaluation dimension
- **Pipeline adaptation?**: Limited (different task types than ours)
- **Gap filled**: Meta-evidence that simple context benchmarks mislead

### G. Limitations
- **Weaknesses**: [PARTIAL] information available
- **Saturation**: [UNKNOWN]
- **Contamination risk**: [UNKNOWN]

## Benchmark 8: OpenAI Effort-Scaling Data

### A. Identity
- **Full name**: Not a benchmark - scattered data from OpenAI System Cards
- **Authors**: OpenAI
- **Date/Venue**: GPT-5 (Jan 2025), GPT-5.2 (2025), GPT-5.5 (2026) system cards
- **URLs**: arxiv.org/html/2601.03267v1 (GPT-5), openai.com/index/ pages

### B. Goal and Scope
- **Capability**: Impact of reasoning effort setting on benchmark performance
- **Research question**: How does compute allocation (effort level) affect model accuracy?
- **Task types**: GPQA Diamond (science QA), AIME (math), SimpleQA (factual), SWE-bench (coding)
- **Tests FORMAT?**: No
- **Tests EFFORT?**: YES - explicitly reports low/medium/high/xhigh
- **Tests SCALE?**: No

### C. Methodology
- **Task design**: Standard benchmarks run at different effort levels
- **Input format**: Varies by benchmark (text questions)
- **Metrics**: Accuracy, pass rate
- **Samples**: Standard benchmark sizes (GPQA=198, AIME=30, SimpleQA=~4K)
- **Ground truth**: Standard benchmark ground truth
- **Statistical rigor**: [PARTIAL] - single-run or averaged (unclear from system cards)
- **Binary search?**: No

### D. Models Tested
- **OpenAI**: gpt-5, gpt-5.2, gpt-5.5 at multiple effort levels (PRIMARY SOURCE)
- **Anthropic**: Not applicable
- **Reasoning models**: YES - this IS about reasoning models
- **Effort levels**: YES - low, medium, high, xhigh explicitly varied

### E. Replicability Assessment
- **Dataset public?**: YES (GPQA, AIME are public)
- **Code**: Underlying benchmarks are public but OpenAI's exact evaluation setup is internal
- **Our setup compatible?**: PARTIAL - we can run GPQA/AIME ourselves at different effort levels
- **Cost**: Moderate (GPQA=198 questions x effort levels x runs)
- **Reproductions**: Community attempts exist (lineage-bench community post)

### F. Relevance to Our Research
- **Validates/contradicts**: Their effort-scaling curves should parallel ours. If GPQA shows 10x improvement low->high like our data extraction, the effect is general. If curves differ, data extraction is uniquely sensitive to effort.
- **New variables?**: xhigh effort level (we tested low/medium/high only)
- **Pipeline adaptation?**: YES - run GPQA/AIME at our effort levels for direct comparison
- **Gap filled**: Provides effort-scaling reference curves for non-data-extraction tasks

### G. Limitations
- **Weaknesses**: Cherry-picked presentation in marketing materials; exact methodology unclear
- **Saturation**: GPQA Diamond approaching saturation for top models
- **Contamination risk**: AIME 2025 low risk; GPQA moderate risk

## Benchmark 9: Anthropic Extended Thinking Research

### A. Identity
- **Full name**: "Claude's extended thinking" (Research blog post / technical report)
- **Authors**: Anthropic Research
- **Date/Venue**: February 2025 (alongside Claude 3.7 Sonnet launch)
- **URLs**: anthropic.com/research/visible-extended-thinking

### B. Goal and Scope
- **Capability**: Thinking budget scaling - how accuracy improves with allowed thinking tokens
- **Research question**: What is the scaling law for serial test-time compute (thinking tokens) vs accuracy?
- **Task types**: Math (AIME), science (GPQA Diamond)
- **Tests FORMAT?**: No
- **Tests EFFORT?**: YES - explicitly varies thinking budget (token count)
- **Tests SCALE?**: No (input scale not varied, only thinking budget)

### C. Methodology
- **Task design**: Standard benchmarks (AIME, GPQA) with varying max thinking token budget
- **Key finding**: "Accuracy on math questions improves LOGARITHMICALLY with thinking tokens"
- **Parallel scaling**: 256 independent samples + learned scoring model achieved GPQA 84.8% (physics: 96.5%)
- **Metrics**: Accuracy at each thinking budget level
- **Statistical rigor**: [PARTIAL] - plot shown but raw data not published

### D. Models Tested
- **OpenAI**: Not applicable
- **Anthropic**: Claude 3.7 Sonnet (with extended thinking)
- **Reasoning models**: YES - specifically about thinking/reasoning capability
- **Effort levels**: YES - thinking budget explicitly varied (up to 64K tokens)

### E. Replicability Assessment
- **Dataset public?**: YES (GPQA, AIME are public)
- **Code**: No - internal research methodology
- **Our setup compatible?**: PARTIAL - we can vary budget_tokens in Anthropic API
- **Cost**: High (256 parallel samples at high token counts)
- **Reproductions**: [UNKNOWN]

### F. Relevance to Our Research
- **Validates/contradicts**: LOGARITHMIC scaling matches our observation that effort improvement has diminishing returns (gpt-5-mini: low=65, medium=~500, high=675 - concave curve)
- **New variables?**: Explicit token budget control (we use effort levels which map to unknown budgets)
- **Pipeline adaptation?**: YES - test our tasks with explicit budget_tokens parameter
- **Gap filled**: Provides theoretical framework (log scaling) for our empirical effort results

### G. Limitations
- **Weaknesses**: Blog-level publication, not peer-reviewed paper. Limited to math/science tasks. Only Claude 3.7 Sonnet tested.
- **Saturation**: Not applicable (scaling continues with compute)
- **Contamination risk**: Standard benchmarks
- **Key concern**: Methodology details sparse - we cannot determine exact experimental setup

## Benchmark 10: MCP Atlas

### A. Identity
- **Full name**: MCP-Atlas: A Large-Scale Benchmark for Tool-Use Competency with Model Context Protocol
- **Authors**: Scale AI Research
- **Date/Venue**: April 2026 (initial), updated May 2026. arXiv:2602.00933
- **URLs**: Paper: arxiv.org/html/2602.00933 | Leaderboard: labs.scale.com/leaderboard/mcp_atlas | Blog: scale.com/blog/open-sourcing-mcp-atlas

### B. Goal and Scope
- **Capability**: Agentic data analysis via MCP tool calls
- **Research question**: How well can models perform data analysis tasks using tool calls in realistic scenarios?
- **Task types**: Data analysis requiring planning, tool selection, execution
- **Tests FORMAT?**: No (data accessed via tools)
- **Tests EFFORT?**: No
- **Tests SCALE?**: [PARTIAL] - task complexity varies

### C. Methodology
- **Task design**: Agent receives analytical question, must use MCP tools (database queries, file operations) to answer
- **Metrics**: Judge-based evaluation (LLM judge scores responses)
- **Max interactions**: 100 tool calls per task
- **Statistical rigor**: Averaged over multiple runs, 95% CI reported for some models
- **Binary search?**: No

### D. Models Tested
- **OpenAI**: GPT-5.5 (0.769), GPT-5.2, o4-mini
- **Anthropic**: Claude Opus 4.7 (0.763), Claude Sonnet 4.5
- **Other**: Gemini 3.5 Flash (0.836 - top score)
- **Reasoning models**: YES - current frontier models tested
- **Effort levels**: [UNKNOWN]

### E. Replicability Assessment
- **Dataset public?**: YES (open-sourced per May 2026 blog post)
- **Code open-source?**: YES (evaluation harness + MCP servers released)
- **Our setup compatible?**: PARTIAL - requires MCP server setup
- **Cost**: High (100 tool calls per task, judge evaluation)
- **Dependencies**: MCP protocol, Python, tool servers
- **Reproductions**: Active leaderboard with community submissions

### F. Relevance to Our Research
- **Validates/contradicts**: Shows model data analysis capability with tools - ceiling for what's possible when extraction limitations are bypassed
- **New variables?**: Planning and tool selection strategy
- **Pipeline adaptation?**: Low (fundamentally different paradigm - agentic vs single-prompt)
- **Gap filled**: Shows "solved" version of data analysis (with tools) vs our "raw" version (direct extraction)

### G. Limitations
- **Weaknesses**: Judge-based scoring introduces variance; tool server availability affects reproducibility
- **Saturation**: Not saturated (top score 0.836)
- **Contamination risk**: Low (live tool servers, dynamic data)

## Benchmark 11: Tau-bench / Tau2-bench

### A. Identity
- **Full name**: tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains (original); tau2-bench: Evaluating Conversational Agents in a Dual-Control Environment (updated)
- **Authors**: Shunyu Yao, Noah Shinn, Pedram Razavi, Karthik Narasimhan (Sierra Research / Princeton)
- **Date/Venue**: June 2024 (arXiv:2406.12045 original), June 2025 (arXiv:2506.07982 tau2)
- **URLs**: Code: github.com/sierra-research/tau-bench, github.com/sierra-research/tau2-bench

### B. Goal and Scope
- **Capability**: Agent interaction with databases in real-world domains
- **Research question**: Can agents follow domain-specific rules while interacting with users and tools?
- **Task types**: Database operations (lookup, modify, cancel) in airline and retail domains
- **Tests FORMAT?**: No
- **Tests EFFORT?**: No
- **Tests SCALE?**: No

### C. Methodology
- **Task design**: Simulated user conversation + database interaction. Agent must follow domain rules (cancellation policies, refund rules)
- **Input format**: Conversational (user messages + tool responses)
- **Metrics**: Task completion accuracy (binary pass/fail)
- **Domains**: Airline reservation, retail (original); expanded in tau2
- **Statistical rigor**: Multiple tasks per domain
- **Binary search?**: No

### D. Models Tested
- **OpenAI**: Referenced in GPT-5.5 system card
- **Anthropic**: [PARTIAL]
- **Reasoning models**: [PARTIAL] - recent models tested
- **Effort levels**: Not tested

### E. Replicability Assessment
- **Dataset public?**: YES (GitHub)
- **Code open-source?**: YES
- **Our setup compatible?**: PARTIAL - requires agent framework
- **Dependencies**: Python, agent harness, simulated user

### F. Relevance to Our Research
- **Validates/contradicts**: Different paradigm (conversational agent vs single extraction)
- **New variables?**: Rule compliance, multi-turn interaction
- **Pipeline adaptation?**: Low
- **Gap filled**: Shows structured data OPERATIONS (not just reading) in realistic scenarios

### G. Limitations
- **Weaknesses**: Agentic framework makes it hard to isolate model capability from harness
- **Saturation**: [UNKNOWN]
- **Contamination risk**: Low (domain-specific rules are novel)

## Benchmark 12: DAComp

### A. Identity
- **Full name**: DAComp: Benchmarking Data Agents across the Full Data Intelligence Lifecycle
- **Authors**: Fangyu Lei, Jinxiang Meng et al. (ByteDance Seed)
- **Date/Venue**: December 2025 (arXiv:2512.04324)
- **URLs**: Paper: arxiv.org/abs/2512.04324 | Code: github.com/ByteDance-Seed/DAComp | Site: da-comp.github.io

### B. Goal and Scope
- **Capability**: Full data intelligence lifecycle (engineering + analysis)
- **Research question**: Can agents handle the complete pipeline from raw data to analytical insights?
- **Task types**: Data engineering (Extract-Transform-Load, cleaning, transformation) + data analysis (queries, visualization)
- **Tests FORMAT?**: [PARTIAL] - different source formats exist but not varied as independent variable
- **Tests EFFORT?**: No
- **Tests SCALE?**: [PARTIAL] - task complexity varies

### C. Methodology
- **Task design**: End-to-end data pipelines: raw data -> clean tables -> analysis
- **Input format**: Various (raw data in multiple formats as input to engineering tasks)
- **Includes Chinese (DAComp-zh)** for multilingual evaluation
- **Metrics**: Task-specific accuracy
- **Statistical rigor**: [PARTIAL]
- **Binary search?**: No

### D. Models Tested
- **OpenAI**: [PARTIAL]
- **Anthropic**: [PARTIAL]
- **Reasoning models**: [UNKNOWN]
- **Effort levels**: Not tested

### E. Replicability Assessment
- **Dataset public?**: YES (GitHub + HuggingFace)
- **Code open-source?**: YES
- **Our setup compatible?**: PARTIAL - requires execution environment
- **Dependencies**: Python, data processing libraries

### F. Relevance to Our Research
- **Validates/contradicts**: Tests data TRANSFORMATION (ETL) which we don't test
- **New variables?**: Data quality, multi-step pipelines
- **Pipeline adaptation?**: Low (different paradigm)
- **Gap filled**: The "full lifecycle" perspective we don't cover

### G. Limitations and Criticism
- **Weaknesses**: Very new (Dec 2025), limited model evaluations published
- **Contamination risk**: Low (novel task construction)

## Comparison Matrix

| Benchmark | Format? | Scale? | Effort? | Dataset? | Code? | Reasoning? | Saturated? |
|-----------|---------|--------|---------|----------|-------|------------|------------|
| TQA-Bench | Y       | Y      | N       | Y        | Y     | N          | N          |
| TableBench | N      | N      | N       | Y        | Y     | N          | N          |
| DACO      | N       | N      | N       | Y        | Y     | N          | N          |
| InfiAgent | N       | N      | N       | Partial  | Y     | N          | N          |
| BABILong  | N       | Y      | N       | Y        | Y     | N          | N          |
| NoLiMa    | N       | Y      | Partial | Unknown  | Unknown | Y        | N          |
| HELMET    | N       | Y      | N       | Unknown  | Unknown | N        | Unknown    |
| OpenAI Cards | N   | N      | Y       | Y (underlying) | N | Y       | Partial    |
| Anthropic  | N      | N      | Y       | Y (underlying) | N | Y       | N          |
| MCP Atlas | N       | Partial | N      | Y        | Y     | Y          | N          |
| Tau-bench | N       | N      | N       | Y        | Y     | Partial    | Unknown    |
| DAComp    | Partial | Partial | N      | Y        | Y     | Unknown    | N          |

**Critical observation**: Only TQA-Bench tests format (Markdown vs CSV, Experiment 1) but as a preliminary step, not the primary research question. No benchmark tests format across 3+ serializations as an independent variable.

## Replicability Ranking

1. **TQA-Bench** - Public dataset + code, API-compatible, directly relevant task type
2. **BABILong** - Public dataset + code, simple evaluation, scales systematically
3. **TableBench** - Public dataset + code, 886 well-annotated samples, API-compatible
4. **OpenAI effort-scaling** - Run GPQA/AIME ourselves at different effort levels (replicating their methodology, not their exact setup)
5. **MCP Atlas** - Open-sourced (May 2026), but requires MCP server infrastructure
6. **DACO** - Public dataset + code, but requires code execution sandbox
7. **InfiAgent-DABench** - Public code but closed test set, requires Docker
8. **Anthropic thinking scaling** - Can approximate by varying budget_tokens in API
9. **Tau-bench** - Public code but requires agent framework setup
10. **DAComp** - Public but requires complex execution environment
11. **NoLiMa** - Methodology clear but dataset/code availability unclear
12. **HELMET** - Limited availability information

## Gap Analysis

Our research tests variables that NO surveyed benchmark covers:

- **Binary search for scale limits**: No benchmark finds the MAXIMUM scale a model handles. All use fixed difficulty levels. Our binary search methodology is unique.
- **Format as independent variable**: Only TQA-Bench compares 2 formats (Markdown vs CSV) as a preliminary experiment. No benchmark tests 3+ formats as a controlled variable on the same task. Our 8-format comparison is unprecedented.
- **Effort impact on data extraction**: OpenAI/Anthropic test effort on math/science tasks. Nobody tests effort impact on structured data extraction specifically.
- **Comprehension vs truncation failure classification**: No benchmark classifies WHY models fail. We distinguish comprehension errors from truncation.
- **Same task, same data, different format**: No benchmark presents identical data in multiple serializations to isolate format effect.

## Variable Coverage Matrix

| Variable | Benchmarks that test it |
|----------|------------------------|
| Input format variation | TQA-Bench (2 formats only: Markdown vs CSV) |
| Input scale / context length | TQA-Bench (8K-64K), BABILong (0-10M), NoLiMa (1K-64K), HELMET |
| Reasoning effort / thinking budget | OpenAI Cards, Anthropic thinking, NoLiMa (partial - tested o1/o3) |
| Task complexity | TableBench (4 categories), BABILong (QA1-QA5), DACO |
| Model family comparison | All benchmarks (but rarely same task/format/effort) |
| Cost efficiency | NONE explicitly measure tokens-per-correct-answer |

## Recommended Deep-Dives

Priority order for follow-up research:

1. **TQA-Bench** - Run with gpt-5 family + Claude thinking models. Add format variation (re-serialize their tables as JSON, XML, YAML). Directly extends our methodology. HIGH relevance, data available, novel hypothesis: "Does format sensitivity persist on multi-table join tasks?"

2. **NoLiMa** - Study methodology in detail. Design analogous "no literal match" variant for our data extraction tasks. Tests whether our models fail because of literal-matching shortcuts or genuine comprehension. HIGH relevance, novel hypothesis: "Do models extract data via pattern matching or semantic understanding?"

3. **OpenAI effort curves** - Replicate GPQA Diamond at low/medium/high/xhigh with our models. Compare scaling curves to our data extraction curves. HIGH relevance, immediately executable, novel hypothesis: "Is effort-scaling steeper for data extraction than for reasoning tasks?"

4. **Anthropic budget_tokens** - Run our extraction tasks with explicit budget_tokens (1K, 4K, 16K, 64K). Test if logarithmic scaling holds for data tasks. MEDIUM relevance, novel hypothesis: "Does data extraction follow the same log-scaling law as math?"

5. **BABILong** - Subset evaluation: embed our extraction task in varying context lengths. Compare degradation curve to their bAbI results. MEDIUM relevance, tests whether our "attention bottleneck" matches their finding.

## Corroborating Observations

Not benchmarks - insufficient methodology for independent deep-research:

- **Lineage-bench** (community.openai.com forum post, 2025): User reported GPT-5.2 performs "much worse than GPT-5.1" at medium/high reasoning effort, only matching at xhigh. Aligns with our gpt-5.2 result (215 rows vs gpt-5-mini's 500). No published methodology, code, or dataset - cannot be replicated.

## Document History

**[2026-05-22 14:27]**
- Added: "Our Research Context" section with methodology and key findings
- Added: "Benchmark Classification" section with tier structure and comparability criterion
- Added: "Corroborating Observations" section (Lineage-bench note)
- Fixed: TQA-Bench Format column in Comparison Matrix (N -> Y)
- Fixed: Format count 6 -> 8 in Summary
- Fixed: Gap Analysis and Variable Coverage Matrix to reflect TQA-Bench format test
- Changed: Critical observation refined (TQA-Bench tests 2 formats, not zero)

**[2026-05-22 13:10]**
- Initial survey of 12 benchmarks across 7 dimensions
- Comparison matrix, replicability ranking, gap analysis, recommendations
