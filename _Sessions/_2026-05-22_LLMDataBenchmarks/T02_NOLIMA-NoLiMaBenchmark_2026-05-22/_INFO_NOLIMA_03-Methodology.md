<DevSystem MarkdownTablesAllowed=true />

# INFO: NoLiMa Methodology

**Doc ID**: NOLIMA-IN03
**Goal**: Document NoLiMa's experimental methodology in detail for replication assessment
**Strategy**: MCPI (exhaustive)
**Domain**: SOFTWARE

## Summary

NoLiMa (No Literal Matching) is a long-context benchmark that extends Needle-in-a-Haystack (NIAH) testing by eliminating lexical overlap between questions and needles. This forces models to use latent associative reasoning (world knowledge, commonsense) rather than surface-level text matching. The benchmark measures how quickly model accuracy degrades as context length increases when literal cues are unavailable.

## Core Innovation

Standard NIAH benchmarks allow models to locate relevant information via literal text matching between the question and the embedded fact. NoLiMa removes this shortcut entirely:

- **Standard NIAH**: "What is the secret code?" -> needle contains "the secret code is 12345"
- **NoLiMa**: "Which character has been to Dresden?" -> needle contains "Yuki lives next to the Semper Opera House"

The model must know that the Semper Opera House is in Dresden to connect the question to the needle. This tests comprehension, not retrieval.

## Needle Set Design

### Construction Principles

1. **Zero literal overlap**: Question keyword (Wq) and needle keyword (Wn) share no words
2. **Associative link required**: Connection through world knowledge or commonsense
3. **Unique association**: Wn must be uniquely associated with Wq (no ambiguity)
4. **Language-neutral**: Avoid orthographic/morphological cues that hint at geographic origin
5. **Randomized characters**: Names drawn from diverse pool, excluding names already in haystacks
6. **Preface phrases**: Each needle starts with introductory text ("Actually,", "In 2013,") to isolate from preceding context

### Hop Types

- **1-hop**: Direct association (Semper Opera House -> Dresden)
- **2-hop**: Indirect association (Semper Opera House -> Dresden -> Saxony; question asks about "state of Saxony")

### Dataset Statistics

- 5 groups of needles, each with default and inverted fact-order
- 2-6 keyword pairs per group (28 total keyword pairs)
- 58 question-needle pairs total
- Both 1-hop and 2-hop variants included

### Fact Order Variations

- **Default order**: Character name precedes needle keyword ("Yuki lives next to the Semper Opera House")
- **Inverted order**: Character name follows needle keyword ("Next to the Semper Opera House lives Yuki")
- Inverted is harder due to causal attention mechanics (model cannot backtrace from Wn to character)

## Haystack Construction

### Source Material

- 10 open-licensed books, each covering at least 50K tokens
- Text concatenated from random short snippets (<250 tokens per snippet)
- Iteratively samples from random books until haystack exceeds 2K lines (60K+ tokens)
- Randomized ordering prevents memorization exploitation

### Filtering Pipeline (2 stages)

**Stage 1 - Distractor Filtering:**
- Uses Contriever embeddings to find semantically similar words to question keywords
- Computes dot-product similarity between haystack words and Wq
- Top-20 similar words per Wq manually inspected
- Sentences containing flagged words removed from haystack

**Stage 2 - Conflicting Information Filtering:**
- Semi-automatic process using instruction-tuned LLM (Llama 3.3 70B)
- Scans haystack in 250-token chunks (800-char stride, 1000-char chunk size)
- LLM identifies potential conflicting answers within each chunk
- Flagged examples manually reviewed by paper author
- Process repeats until no further removals needed
- Control test: Llama 3.3 70B achieves 99.8% on filtering verification

## Evaluation Protocol

### Context Lengths Tested

Standard evaluations: 250, 500, 1K, 2K, 4K, 8K, 16K, 32K tokens
Extended evaluations (reduced placements): 64K, 128K tokens

### Placement Strategy

- Each needle placed at 26 equally-spaced positions across the context length
- Extended evaluations (64K, 128K): 11 positions instead of 26
- 5 randomly generated haystacks per test

### Test Volume

Per context length: 58 question-needle pairs x 26 placements x 5 haystacks = **7,540 tests**

### Metrics

- **Base score**: Model accuracy at short contexts (max of average scores at 250, 500, 1K per example)
- **Effective length**: Longest context where model maintains >= 85% of base score
- **Normalized score**: Accuracy divided by base score (shows relative degradation)
- **Accuracy**: Proportion of tests where generated output contains correct character name

### Inference Settings

- Task template instructs model to answer based on provided text
- Any answer containing correct name is considered accurate
- Standard models: greedy decoding
- Reasoning models (o1, o3): default sampling decoding
- R1-based models: top-P sampling (p=0.95, temperature=0.6)
- CoT: Limited to 3 sentences or 192 generated tokens max
- Reasoning models: 1536 max tokens (reasoning + output)

## Ablation Studies

### CoT Prompting (Table 4 in paper)

- CoT improves performance at longer contexts
- Higher improvement rate for 2-hop tasks
- But: 2-hop with CoT barely reaches 1-hop without CoT scores
- CoT limited because NoLiMa questions cannot be decomposed into simpler steps
- Challenge is associative reasoning, not step decomposition

### Literal Match Effect (Table 6 in paper)

Two control conditions:
1. **Direct questions**: Explicitly mention Wn in question (vanilla NIAH). Result: near-perfect even at long contexts
2. **Multiple choice**: Include character names as options (literal match as hint). Result: significantly better than NoLiMa standard

### Distracting Literal Matches (Figure 5 in paper)

- Distractor sentence placed in haystack containing Wq but irrelevant to the answer
- Placed randomly between 20%-80% context marks, minimum 20% distance from needle
- GPT-4o effective length drops to 1K with distractors (from 8K without)
- Demonstrates models are actively misled by irrelevant literal overlaps

## NoLiMa-Hard Subset

- 10 most challenging question-needle pairs selected from original 58
- Used specifically for evaluating reasoning models
- Base scores remain near-perfect (97-100%), confirming task simplicity at short context
- All models still drop below 50% at 32K

## Replication Requirements

### Software Dependencies

- Python with packages from `requirements.txt`
- vLLM for local model serving (optional)
- LLM API access (OpenAI, Google, Anthropic, etc.)
- Tokenizer matching (tiktoken for OpenAI models)

### Data Download

```bash
# Clone repo
git clone https://github.com/adobe-research/NoLiMa.git
# Download data from HuggingFace
data/download_NoLiMa_data.sh
```

### Evaluation Pipeline

1. Install requirements (`pip install -r requirements.txt`)
2. Download data (haystacks + needlesets from HuggingFace)
3. Configure model (JSON config in `evaluation/model_configs/`)
4. Prepare run config (in `evaluation/run_config/`)
5. Run tests (`cd evaluation/ && ./run_tests.sh`)
6. Gather results (`evaluation/gather_results.ipynb`)

### Available Needle Sets

- `needle_set.json` - Main NoLiMa (58 pairs)
- `needle_set_hard.json` - NoLiMa-Hard (10 pairs)
- `needle_set_ONLYDirect.json` - Direct questions (control)
- `needle_set_MC.json` - Multiple choice format
- `needle_set_w_CoT.json` - CoT task templates
- `needle_set_w_distractor.json` - With distractor sentences

### Cost Estimation for Our Models

- 7,540 tests per context length x 8 context lengths = ~60,320 API calls for full evaluation
- At 32K average context: ~1.9B input tokens total
- Estimated cost at gpt-5-mini rates: $950-$1,900 (depending on input token pricing)
- Reduced evaluation (NoLiMa-Hard only, 4 lengths): 10 pairs x 26 placements x 5 haystacks x 4 lengths = 5,200 calls
- NoLiMa-Hard at 32K average: ~166M input tokens, estimated $80-$160

## Limitations

- Tests world-knowledge association, not structured data extraction
- Binary correct/incorrect (no partial credit)
- Only English language
- Character name matching may have edge cases with tokenization
- Adobe Research License restricts commercial use
- Haystack is natural language (books), not structured/tabular data

## Document History

**[2026-05-22 13:33]**
- Initial creation from paper sections 3, 4, appendices A-D
