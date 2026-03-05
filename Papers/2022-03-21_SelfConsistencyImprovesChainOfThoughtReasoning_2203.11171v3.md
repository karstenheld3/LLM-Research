<transcription_page_header> Published as a conference paper at ICLR 2023 </transcription_page_header>

<!-- Decorative: arXiv identifier on left margin: "arXiv:2203.11171v4 [cs.CL] 7 Mar 2023" -->

<!-- Section 1 -->
# SELF-CONSISTENCY IMPROVES CHAIN OF THOUGHT REASONING IN LANGUAGE MODELS

Xuezhi Wang†‡  Jason Wei†  Dale Schuurmans†  Quoc Le†  Ed H. Chi†  
Sharan Narang†  Aakanksha Chowdhery†  Denny Zhou§

†Google Research, Brain Team  
‡xuezhiw@google.com, §dennyzhou@google.com

<!-- Section 2 -->
## ABSTRACT

Chain-of-thought prompting combined with pre-trained large language models has achieved encouraging results on complex reasoning tasks. In this paper, we propose a new decoding strategy, self-consistency, to replace the naive greedy decoding used in chain-of-thought prompting. It first samples a diverse set of reasoning paths instead of only taking the greedy one, and then selects the most consistent answer by marginalizing out the sampled reasoning paths. Self-consistency leverages the intuition that a complex reasoning problem typically admits multiple different ways of thinking leading to its unique correct answer. Our extensive empirical evaluation shows that self-consistency boosts the performance of chain-of-thought prompting with a striking margin on a range of popular arithmetic and commonsense reasoning benchmarks, including GSM8K (+17.9%), SVAMP (+11.0%), AQuA (+12.2%), StrategyQA (+6.4%) and ARC-challenge (+3.9%).

<!-- Section 3 -->
## 1 INTRODUCTION

Although language models have demonstrated remarkable success across a range of NLP tasks, their ability to demonstrate reasoning is often seen as a limitation, which cannot be overcome solely by increasing model scale (Rae et al., 2021; BIG-bench collaboration, 2021, inter alia). In an effort to address this shortcoming, Wei et al. (2022) have proposed chain-of-thought prompting, where a language model is prompted to generate a series of short sentences that mimic the reasoning process a person might employ in solving a task. For example, given the question "If there are 3 cars in the parking lot and 2 more cars arrive, how many cars are in the parking lot?", instead of directly responding with "5", a language model would be prompted to respond with the entire chain-of-thought: "There are 3 cars in the parking lot already. 2 more arrive. Now there are 3 + 2 = 5 cars. The answer is 5." It has been observed that chain-of-thought prompting significantly improves model performance across a variety of multi-step reasoning tasks (Wei et al., 2022).

In this paper, we introduce a novel decoding strategy called self-consistency to replace the greedy decoding strategy used in chain-of-thought prompting (Wei et al., 2022), that further improves language models' reasoning performance by a significant margin. Self-consistency leverages the intuition that complex reasoning tasks typically admit multiple reasoning paths that reach a correct answer (Stanovich & West, 2000). The more that deliberative thinking and analysis is required for a problem (Evans, 2010), the greater the diversity of reasoning paths that can recover the answer.

Figure 1 illustrates the self-consistency method with an example. We first prompt the language model with chain-of-thought prompting, then instead of greedily decoding the optimal reasoning path, we propose a "sample-and-marginalize" decoding procedure: we first sample from the language model's decoder to generate a diverse set of reasoning paths; each reasoning path might lead to a different final answer, so we determine the optimal answer by marginalizing out the sampled reasoning paths to find the most consistent answer in the final answer set. Such an approach is analogous to the human experience that if multiple different ways of thinking lead to the same answer, one has greater confidence that the final answer is correct. Compared to other decoding methods, self-consistency avoids the repetitiveness and local-optimality that plague greedy decoding, while mitigating the stochasticity of a single sampled generation.

<transcription_page_footer> Page 1 </transcription_page_footer>

---

<transcription_page_header> Published as a conference paper at ICLR 2023 </transcription_page_header>

<!-- Section 1 -->
# Published as a conference paper at ICLR 2023

<!-- Column 1 -->
<!-- (Graphic: Figure 1) -->

<transcription_image>
**Figure 1: The self-consistency method**

```ascii
[DIAGRAM - SELF-CONSISTENCY METHOD]

Top row (Chain-of-thought prompting):

[Prompt] [PROCESS] --> [Language model] [PROCESS] --> [Greedy decode] [PROCESS]
                                                   |
                                                   v
                                         [OUTPUT BOX - red]
                                         "This means she uses 3 + 4 = 7 eggs every day.
                                         She sells the remainder for $2 per egg, so in
                                         total she sells 7 * $2 = $14 per day.
                                         The answer is $14."
                                         [PROCESS] --> (The answer is $14.)

Divider: ----------------- Self-consistency -----------------

Self-consistency (sample a diverse set of reasoning paths):

[Prompt] [PROCESS] --> [Language model] [PROCESS]
                               |
                Sample a diverse set of reasoning paths
                               |
                               v
  ----------------------------------  ----------------------------------  ----------------------------------
  | Path 1 (blue/green)             |  | Path 2 (orange/red)           |  | Path 3 (blue/green)            |
  |                                 |  |                               |  |                                |
  | "She has 16 - 3 - 4 = 9 eggs     |  | "This means she sells the     |  | "She eats 3 for breakfast, so  |
  | left. So she makes 2 * 9 =      |  | remainder for $2 * (16 - 4 - 3) |
  | $18 per day.                    |  | = $26 per day."               |  | she has 13 - 4 = 9 eggs left.   |
  | The answer is $18." [PROCESS]   |  | The answer is $26." [PROCESS] |  | The answer is $18." [PROCESS]   |
  ----------------------------------  ----------------------------------  ----------------------------------

                \                           |                             /
                 \                          |                            /
                  \                         |                           /
                   \                        |                          /
                    \                       |                         /
                     ---> Marginalize out reasoning paths & aggregate <---
                                        |
                                        v
                                 [Final answer bubble - green]
                                 "The answer is $18."
```

<transcription_json>
{"diagram_type": "method_flow", "title": "Self-consistency method (Figure 1)", "nodes": [{"id": "prompt_top", "label": "[PROCESS]", "text": "Prompt"}, {"id": "lm_top", "label": "[PROCESS]", "text": "Language model"}, {"id": "greedy", "label": "[PROCESS]", "text": "Greedy decode -> \"This means she uses 3 + 4 = 7 eggs every day. She sells the remainder for $2 per egg, so in total she sells 7 * $2 = $14 per day. The answer is $14.\""}, {"id": "divider", "label": "(divider)", "text": "Self-consistency sampling divider"}, {"id": "prompt_sc", "label": "[PROCESS]", "text": "Prompt (CoT exemplars)"}, {"id": "lm_sc", "label": "[PROCESS]", "text": "Language model (sampled decoder)"}, {"id": "path1", "label": "[PROCESS]", "text": "Path 1: \"She has 16 - 3 - 4 = 9 eggs left. So she makes 2 * 9 = $18 per day. The answer is $18.\"", "answer": 18}, {"id": "path2", "label": "[PROCESS]", "text": "Path 2: \"This means she sells the remainder for $2 * (16 - 4 - 3) = $26 per day. The answer is $26.\"", "answer": 26}, {"id": "path3", "label": "[PROCESS]", "text": "Path 3: \"She eats 3 for breakfast, so she has 13 - 4 = 9 eggs left. The answer is $18.\"", "answer": 18}, {"id": "aggregate", "label": "[PROCESS]", "text": "Marginalize out reasoning paths and choose most consistent answer -> The answer is $18.", "final_answer": 18}], "answers_extracted": {"greedy_decode_answer": 14, "sampled_answers": [18, 26, 18], "final_aggregated_answer": 18}}
</transcription_json>

<transcription_notes>
- Type: Method diagram / flowchart illustrating chain-of-thought prompting vs. self-consistency sampling.
- Visual layout: Top row shows chain-of-thought prompt -> language model -> greedy decode (red output bubble with answer $14).
  Below a dashed divider labeled "Self-consistency" shows prompt -> language model with sampling to produce multiple colored reasoning-path bubbles (two green/blue paths yielding $18, one orange/red yielding $26), arrows marginalize to a final green bubble with "The answer is $18."
- Colors (approximate): greedy decode/output = red; correct-consistent paths = green/blue; incorrect/divergent path = orange/red; final aggregated answer = green.
- Annotations: arrows, dashed lines, and a note "Sample a diverse set of reasoning paths" and "Marginalize out reasoning paths to aggregate final answers".
- The diagram labels have been annotated with [PROCESS] per transcription rules for nodes.
- ASCII simplifies shapes and relative spacing; exact colors, rounded boxes, and arrows are not rendered in ASCII.
</transcription_notes>
</transcription_image>

Figure 1: The self-consistency method contains three steps: (1) prompt a language model using chain-of-thought (CoT) prompting; (2) replace the "greedy decode" in CoT prompting by sampling from the language model's decoder to generate a diverse set of reasoning paths; and (3) marginalize out the reasoning paths and aggregate by choosing the most consistent answer in the final answer set.

<!-- Section 2 -->
Self-consistency is far simpler than prior approaches that either train an additional verifier (Cobbe et al., 2021) or train a re-ranker given additional human annotations to improve generation quality (Thoppilan et al., 2022). Instead, self-consistency is entirely unsupervised, works off-the-shelf with pre-trained language models, requires no additional human annotation, and avoids any additional training, auxiliary models or fine-tuning. Self-consistency also differs from a typical ensemble approach where multiple models are trained and the outputs from each model are aggregated, it acts more like a "self-ensemble" that works on top of a single language model.

We evaluate self-consistency on a wide range of arithmetic and commonsense reasoning tasks over four language models with varying scales: the public UL2-20B (Tay et al., 2022) and GPT-3-175B (Brown et al., 2020), and two densely-activated decoder-only language models: LaMDA-137B (Thoppilan et al., 2022) and PaLM-540B (Chowdhery et al., 2022). On all four language models, self-consistency improves over chain-of-thought prompting by a striking margin across all tasks. In particular, when used with PaLM-540B or GPT-3, self-consistency achieves new state-of-the-art levels of performance across arithmetic reasoning tasks, including GSM8K (Cobbe et al., 2021) (+17.9% absolute accuracy gains), SVAMP (Patel et al., 2021) (+11.0%), AQUA (Ling et al., 2017) (+12.2%), and across commonsense reasoning tasks such as StrategyQA (Geva et al., 2021) (+6.4%) and ARC-challenge (Clark et al., 2018) (+3.9%). In additional experiments, we show self-consistency can robustly boost performance on NLP tasks where adding a chain-of-thought might hurt performance compared to standard prompting (Ye & Durrett, 2022). We also show self-consistency significantly outperforms sample-and-rank, beam search, ensemble-based approaches, and is robust to sampling strategies and imperfect prompts.

## 2 SELF-CONSISTENCY OVER DIVERSE REASONING PATHS

A salient aspect of humanity is that people think differently. It is natural to suppose that in tasks requiring deliberate thinking, there are likely several ways to attack the problem. We propose that such a process can be simulated in language models via sampling from the language model's decoder. For instance, as shown in Figure 1, a model can generate several plausible responses to a math question that all arrive at the same correct answer (Outputs 1 and 3). Since language models are not perfect reasoners, the model might also produce an incorrect reasoning path or make a mistake in one of the reasoning steps (e.g., in Output 2), but such solutions are less likely to arrive at the same answer. That is, we hypothesize that correct reasoning processes, even if they are diverse, tend to have greater agreement in their final answer than incorrect processes.

We leverage this intuition by proposing the following self-consistency method. First, a language model is prompted with a set of manually written chain-of-thought exemplars (Wei et al., 2022). Next,
<!-- (page cuts off mid-sentence) -->

<transcription_page_footer> Page 2 </transcription_page_footer>

---

<transcription_page_header>Published as a conference paper at ICLR 2023</transcription_page_header>

<!-- Section 1 -->
<!-- Column 1 -->
## Table 1: Accuracy comparison of different answer aggregation strategies on PaLM-540B.

<transcription_table>
**Table 1: Accuracy comparison of different answer aggregation strategies on PaLM-540B.**

| Aggregation strategy | GSM8K | MultiArith | AQuA | SVAMP | CSQA | ARC-c |
|----------------------|-------:|-----------:|-----:|------:|-----:|------:|
| Greedy decode | 56.5 | 94.7 | 35.8 | 79.0 | 79.0 | 85.2 |
| Weighted avg (unnormalized) | 56.3 ± 0.0 | 90.5 ± 0.0 | 35.8 ± 0.0 | 73.0 ± 0.0 | 74.8 ± 0.0 | 82.3 ± 0.0 |
| Weighted avg (normalized) | 22.1 ± 0.0 | 59.7 ± 0.0 | 15.7 ± 0.0 | 40.5 ± 0.0 | 52.1 ± 0.0 | 51.7 ± 0.0 |
| Weighted sum (unnormalized) | 59.9 ± 0.0 | 92.2 ± 0.0 | 38.2 ± 0.0 | 76.2 ± 0.0 | 76.2 ± 0.0 | 83.5 ± 0.0 |
| Weighted sum (normalized) | 74.1 ± 0.0 | 99.3 ± 0.0 | 48.0 ± 0.0 | 86.8 ± 0.0 | 80.7 ± 0.0 | 88.7 ± 0.0 |
| Unweighted sum (majority vote) | 74.4 ± 0.1 | 99.3 ± 0.0 | 48.3 ± 0.5 | 86.6 ± 0.1 | 80.7 ± 0.1 | 88.7 ± 0.1 |

<transcription_json>
{"table_type":"data_table","title":"Accuracy comparison of different answer aggregation strategies on PaLM-540B","columns":["Aggregation strategy","GSM8K","MultiArith","AQuA","SVAMP","CSQA","ARC-c"],"data":[{"Aggregation strategy":"Greedy decode","GSM8K":56.5,"MultiArith":94.7,"AQuA":35.8,"SVAMP":79.0,"CSQA":79.0,"ARC-c":85.2},{"Aggregation strategy":"Weighted avg (unnormalized)","GSM8K":"56.3 ± 0.0","MultiArith":"90.5 ± 0.0","AQuA":"35.8 ± 0.0","SVAMP":"73.0 ± 0.0","CSQA":"74.8 ± 0.0","ARC-c":"82.3 ± 0.0"},{"Aggregation strategy":"Weighted avg (normalized)","GSM8K":"22.1 ± 0.0","MultiArith":"59.7 ± 0.0","AQuA":"15.7 ± 0.0","SVAMP":"40.5 ± 0.0","CSQA":"52.1 ± 0.0","ARC-c":"51.7 ± 0.0"},{"Aggregation strategy":"Weighted sum (unnormalized)","GSM8K":"59.9 ± 0.0","MultiArith":"92.2 ± 0.0","AQuA":"38.2 ± 0.0","SVAMP":"76.2 ± 0.0","CSQA":"76.2 ± 0.0","ARC-c":"83.5 ± 0.0"},{"Aggregation strategy":"Weighted sum (normalized)","GSM8K":"74.1 ± 0.0","MultiArith":"99.3 ± 0.0","AQuA":"48.0 ± 0.0","SVAMP":"86.8 ± 0.0","CSQA":"80.7 ± 0.0","ARC-c":"88.7 ± 0.0"},{"Aggregation strategy":"Unweighted sum (majority vote)","GSM8K":"74.4 ± 0.1","MultiArith":"99.3 ± 0.0","AQuA":"48.3 ± 0.5","SVAMP":"86.6 ± 0.1","CSQA":"80.7 ± 0.1","ARC-c":"88.7 ± 0.1"}],"unit":"percent"}
</transcription_json>

<transcription_notes>
- Visual: A centered table with horizontal rules above and below header row and between rows. Column headers: GSM8K, MultiArith, AQuA, SVAMP, CSQA, ARC-c. Values include means and ± standard error (displayed as ± 0.0 or ± 0.1).
- Caption under table: "Table 1: Accuracy comparison of different answer aggregation strategies on PaLM-540B."
- Fonts: serif, small. Table occupies full page width near top.
</transcription_notes>
</transcription_table>

<!-- Section 2 -->
## Main text

we sample a set of candidate outputs from the language model's decoder, generating a diverse set of candidate reasoning paths. Self-consistency is compatible with most existing sampling algorithms, including temperature sampling (Ackley et al., 1985; Ficler & Goldberg, 2017), top-k sampling (Fan et al., 2018; Holtzman et al., 2018; Radford et al., 2019), and nucleus sampling (Holtzman et al., 2020). Finally, we aggregate the answers by marginalizing out the sampled reasoning paths and choosing the answer that is the most consistent among the generated answers.

In more detail, assume the generated answers a_i are from a fixed answer set, a_i ∈ A, where i = 1, ..., m indexes the m candidate outputs sampled from the decoder. Given a prompt and a question, self-consistency introduces an additional latent variable r_i, which is a sequence of tokens representing the reasoning path in the i-th output; then couples the generation of (r_i, a_i) where r_i → a_i, i.e., generating a reasoning path r_i is optional and only used to reach the final answer a_i. As an example, consider Output 3 from Figure 1: the first few sentences "She eats 3 for breakfast ... So she has 9 eggs * $2 = $18." constitutes r_i, while the answer 18 from the last sentence, "The answer is $18", is parsed as a_i. After sampling multiple (r_i, a_i) from the model's decoder, self-consistency applies a marginalization over r_i by taking a majority vote over a_i, i.e., arg max_a Σ_{i=1}^m 1(a_i = a), or as we defined as the most "consistent" answer among the final answer set.

In Table 1, we show the test accuracy over a set of reasoning tasks by using different answer aggregation strategies. In addition to majority vote, one can also weight each (r_i, a_i) by P(r_i, a_i | prompt, question) when aggregating the answers. Note to compute P(r_i, a_i | prompt, question), we can either take the unnormalized probability of the model generating (r_i, a_i) given (prompt, question), or we can normalize the conditional probability by the output length (Brown et al., 2020), i.e.,

P(r_i, a_i | prompt, question) = exp^{1/K} Σ_{k=1}^K log P(t_k | prompt, question, t_1, ..., t_{k-1}), (1)

where log P(t_k | prompt, question, t_1, ..., t_{k-1}) is the log probability of generating the k-th token t_k in (r_i, a_i) conditioned on the previous tokens, and K is the total number of tokens in (r_i, a_i). In Table 1, we show that taking the "unweighted sum", i.e., taking a majority vote directly over a_i, yields a very similar accuracy as aggregating using the "normalized weighted sum". We took a closer look at the model's output probabilities and found this is because for each (r_i, a_i), the normalized conditional probabilities P(r_i, a_i | prompt, question) are quite close to each other, i.e., the language model regards those generations as "similarly likely". Additionally, when aggregating the answers, the results in Table 1 show that the "normalized" weighted sum (i.e., Equation 1) yields a much higher accuracy compared to its unnormalized counterpart. For completeness, in Table 1 we also report the results by taking a "weighted average", i.e., each a_i gets a score of its weighted sum divided by Σ_{i=1}^m 1(a_i = a), which results in a much worse performance.

Self-consistency explores an interesting space between open-ended text generation and optimal text generation with a fixed answer. Reasoning tasks typically have fixed answers, which is why researchers have generally considered greedy decoding approaches (Radford et al., 2019; Wei et al., 2022; Chowdhery et al., 2022). However, we have found that even when the desired answer is fixed, introducing diversity in the reasoning processes can be highly beneficial; therefore we leverage

<!-- Section 3 -->
### Footnotes

1 The parser is task dependent. For arithmetic reasoning, we parse the first numerical part as the final answer after the model generates "The answer is ". For commonsense reasoning, we parse the full string answer as the final answer after the model generates "The answer is ". Most generated outputs have a consistent format of "{Reasoning paths}. The answer is X." if we prompt the language model in this format.

2 This also means that the language model is not well calibrated and thus cannot distinguish well between correct solutions and wrong solutions, which also explains why additional re-rankers were trained to better judge the quality of the solutions in previous work (Cobbe et al., 2021; Thoppilan et al., 2022).

<transcription_page_footer>3</transcription_page_footer>

---

<transcription_page_header>Published as a conference paper at ICLR 2023</transcription_page_header>

<!-- Section 1 -->

## 3 EXPERIMENTS

We conducted a series of experiments to compare the proposed self-consistency method with existing approaches on a range of reasoning benchmarks. We find that self-consistency robustly improves reasoning accuracy for every language model considered, spanning a wide range of model scales.

### 3.1 EXPERIMENT SETUP

Tasks and datasets. We evaluate self-consistency on the following reasoning benchmarks.3

- Arithmetic reasoning. For these tasks, we used the Math Word Problem Repository (Koncel-Kedziorski et al., 2016), including AddSub (Hosseini et al., 2014), MultiArith (Roy & Roth, 2015), and ASDiv (Miao et al., 2020). We also included AQUA-RAT (Ling et al., 2017), a recently published benchmark of grade-school-math problems (GSM8K; Cobbe et al., 2021), and a challenge dataset over math word problems (SVAMP; Patel et al., 2021).

- Commonsense reasoning. For these tasks, we used CommonsenseQA (Talmor et al., 2019), StrategyQA (Geva et al., 2021), and the AI2 Reasoning Challenge (ARC) (Clark et al., 2018).

- Symbolic Reasoning. We evaluate two symbolic reasoning tasks: last letter concatenation (e.g., the input is "Elon Musk" and the output should be "nk"), and Coinflip (e.g., a coin is heads-up, after a few flips is the coin still heads-up?) from Wei et al. (2022).

Language models and prompts. We evaluate self-consistency over four transformer-based language models with varying scales:

- UL2 (Tay et al., 2022) is an encoder-decoder model trained on a mixture of denoisers with 20-billion parameters. UL2 is completely open-sourced4 and has similar or better performance than GPT-3 on zero-shot SuperGLUE, with only 20B parameters and thus is more compute-friendly;

- GPT-3 (Brown et al., 2020) with 175-billion parameters. We use two public engines code-davinci-001 and code-davinci-002 from the Codex series (Chen et al., 2021) to aid reproducibility;5

- LaMDA-137B (Thoppilan et al., 2022) is a dense left-to-right, decoder-only language model with 137-billion parameters, pre-trained on a mixture of web documents, dialog data and Wikipedia;

- PaLM-540B (Chowdhery et al., 2022) is a dense left-to-right, decoder-only language model with 540-billion parameters, pre-trained on a high quality corpus of 780 billion tokens with filtered webpages, books, Wikipedia, news articles, source code, and social media conversations.

We perform all experiments in the few-shot setting, without training or fine-tuning the language models. For a fair comparison we use the same prompts as in Wei et al. (2022): for all arithmetic reasoning tasks we use the same set of 8 manually written exemplars; for each commonsense reasoning task, 4-7 exemplars are randomly chosen from the training set with manually composed chain-of-thought prompts.6 Full details on the prompts used are given in Appendix A.3.

Sampling scheme. To sample diverse reasoning paths, we followed similar settings to those suggested in Radford et al. (2019); Holtzman et al. (2020) for open-text generation. In particular, for UL2-20B and LaMDA-137B we applied temperature sampling with T = 0.5 and truncated at the top-k (k = 40) tokens with the highest probability; for PaLM-540B we applied T = 0.7, k = 40, and for GPT-3 we use T = 0.7 without top-k truncation. We provide an ablation study in Section 3.5 to show that self-consistency is generally robust to sampling strategies and parameters.

<!-- Decorative: horizontal rule at top of page -->

3 By default we use the test split for all datasets if the labels are available for evaluation. For CommonsenseQA we use the dev split; for StrategyQA we use the question-only set from BIG-bench collaboration (2021): https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/strategyqa.

4 Model checkpoints at https://github.com/google-research/google-research/tree/master/ul2.

5 Public API available at https://openai.com/api/.

6 Self-consistency is robust to different sets of prompts and we provide a study in Appendix A.1.2.

<transcription_notes>
- Page layout: single-column typeset academic page (ICLR style) with serif font.
- Header: centered text "Published as a conference paper at ICLR 2023" with a thin horizontal rule beneath.
- Footer: centered page number "4".
- Visual cues: section numbers in small caps; in-text citations and footnote superscripts present.
- No figures or tables on this page.
</transcription_notes>

<transcription_page_footer>Page 4</transcription_page_footer>

---

<transcription_page_header> Published as a conference paper at ICLR 2023 </transcription_page_header>

<!-- Decorative: [horizontal rule under header] -->

## 3.2 MAIN RESULTS

We report the results of self-consistency averaged over 10 runs, where we sampled 40 outputs independently from the decoder in each run. The baseline we compare to is chain-of-thought prompting with greedy decoding (Wei et al., 2022), referred to as CoT-prompting, which has been previously used for decoding in large language models (Chowdhery et al., 2022).

### Arithmetic Reasoning

The results are shown in Table 2.7 Self-consistency improves the arithmetic reasoning performance over all four language models significantly over chain-of-thought prompting. More surprisingly, the gains become more significant when the language model's scale increases, e.g., we see +3%-6% absolute accuracy improvement over UL2-20B but +9%-23% for LaMDA-137B and GPT-3. For larger models that already achieve high accuracy on most tasks (e.g., GPT-3 and PaLM-540B), self-consistency still contributes significant additional gains with +12%-18% absolute accuracy on tasks like AQuA and GSM8K, and +7%-11% on SVAMP and ASDiv. With self-consistency, we achieve new state-of-the-art results on almost all tasks: despite the fact that self-consistency is unsupervised and task-agnostic, these results compare favorably to existing approaches that require task-specific training, or fine-tuning with thousands of examples (e.g., on GSM8K).

<transcription_table>
**Table 2: Arithmetic reasoning accuracy by self-consistency compared to chain-of-thought prompting**

| Method | AddSub | MultiArith | ASDiv | AQuA | SVAMP | GSM8K |
|--------|--------:|-----------:|------:|-----:|------:|------:|
| Previous SoTA | 94.9^a | 60.5^a | 75.3^b | 37.9^c | 57.4^d | 35^e / 55^g |
| UL2-20B — CoT-prompting | 18.2 | 10.7 | 16.9 | 23.6 | 12.6 | 4.1 |
| UL2-20B — Self-consistency | 24.8 (+6.6) | 15.0 (+4.3) | 21.5 (+4.6) | 26.9 (+3.3) | 19.4 (+6.8) | 7.3 (+3.2) |
| LaMDA-137B — CoT-prompting | 52.9 | 51.8 | 49.0 | 17.7 | 38.9 | 17.1 |
| LaMDA-137B — Self-consistency | 63.5 (+10.6) | 75.7 (+23.9) | 58.2 (+9.2) | 26.8 (+9.1) | 53.3 (+14.4) | 27.7 (+10.6) |
| PaLM-540B — CoT-prompting | 91.9 | 94.7 | 74.0 | 35.8 | 79.0 | 56.5 |
| PaLM-540B — Self-consistency | 93.7 (+1.8) | 99.3 (+4.6) | 81.9 (+7.9) | 45.3 (+12.5) | 86.6 (+7.6) | 74.4 (+17.9) |
| GPT-3 (code-davinci-001) — CoT-prompting | 57.2 | 59.5 | 52.7 | 18.9 | 39.8 | 14.6 |
| GPT-3 (code-davinci-001) — Self-consistency | 67.8 (+10.6) | 82.7 (+23.2) | 61.9 (+9.2) | 25.6 (+6.7) | 54.5 (+14.7) | 23.4 (+8.8) |
| GPT-3 (code-davinci-002) — CoT-prompting | 89.4 | 96.2 | 80.1 | 39.8 | 75.8 | 60.1 |
| GPT-3 (code-davinci-002) — Self-consistency | 91.6 (+2.2) | 100.0 (+3.8) | 87.8 (+7.6) | 52.0 (+12.2) | 86.8 (+11.0) | 78.0 (+17.9) |

<transcription_json>
{"table_type":"data_table","title":"Table 2: Arithmetic reasoning accuracy by self-consistency compared to chain-of-thought prompting","columns":["Method","AddSub","MultiArith","ASDiv","AQuA","SVAMP","GSM8K"],"data":[{"Method":"Previous SoTA","AddSub":"94.9^a","MultiArith":"60.5^a","ASDiv":"75.3^b","AQuA":"37.9^c","SVAMP":"57.4^d","GSM8K":"35^e / 55^g"},{"Method":"UL2-20B — CoT-prompting","AddSub":18.2,"MultiArith":10.7,"ASDiv":16.9,"AQuA":23.6,"SVAMP":12.6,"GSM8K":4.1},{"Method":"UL2-20B — Self-consistency","AddSub":24.8,"AddSub_delta":"+6.6","MultiArith":15.0,"MultiArith_delta":"+4.3","ASDiv":21.5,"ASDiv_delta":"+4.6","AQuA":26.9,"AQuA_delta":"+3.3","SVAMP":19.4,"SVAMP_delta":"+6.8","GSM8K":7.3,"GSM8K_delta":"+3.2"},{"Method":"LaMDA-137B — CoT-prompting","AddSub":52.9,"MultiArith":51.8,"ASDiv":49.0,"AQuA":17.7,"SVAMP":38.9,"GSM8K":17.1},{"Method":"LaMDA-137B — Self-consistency","AddSub":63.5,"AddSub_delta":"+10.6","MultiArith":75.7,"MultiArith_delta":"+23.9","ASDiv":58.2,"ASDiv_delta":"+9.2","AQuA":26.8,"AQuA_delta":"+9.1","SVAMP":53.3,"SVAMP_delta":"+14.4","GSM8K":27.7,"GSM8K_delta":"+10.6"},{"Method":"PaLM-540B — CoT-prompting","AddSub":91.9,"MultiArith":94.7,"ASDiv":74.0,"AQuA":35.8,"SVAMP":79.0,"GSM8K":56.5},{"Method":"PaLM-540B — Self-consistency","AddSub":93.7,"AddSub_delta":"+1.8","MultiArith":99.3,"MultiArith_delta":"+4.6","ASDiv":81.9,"ASDiv_delta":"+7.9","AQuA":45.3,"AQuA_delta":"+12.5","SVAMP":86.6,"SVAMP_delta":"+7.6","GSM8K":74.4,"GSM8K_delta":"+17.9"},{"Method":"GPT-3 (code-davinci-001) — CoT-prompting","AddSub":57.2,"MultiArith":59.5,"ASDiv":52.7,"AQuA":18.9,"SVAMP":39.8,"GSM8K":14.6},{"Method":"GPT-3 (code-davinci-001) — Self-consistency","AddSub":67.8,"AddSub_delta":"+10.6","MultiArith":82.7,"MultiArith_delta":"+23.2","ASDiv":61.9,"ASDiv_delta":"+9.2","AQuA":25.6,"AQuA_delta":"+6.7","SVAMP":54.5,"SVAMP_delta":"+14.7","GSM8K":23.4,"GSM8K_delta":"+8.8"},{"Method":"GPT-3 (code-davinci-002) — CoT-prompting","AddSub":89.4,"MultiArith":96.2,"ASDiv":80.1,"AQuA":39.8,"SVAMP":75.8,"GSM8K":60.1},{"Method":"GPT-3 (code-davinci-002) — Self-consistency","AddSub":91.6,"AddSub_delta":"+2.2","MultiArith":100.0,"MultiArith_delta":"+3.8","ASDiv":87.8,"ASDiv_delta":"+7.6","AQuA":52.0,"AQuA_delta":"+12.2","SVAMP":86.8,"SVAMP_delta":"+11.0","GSM8K":78.0,"GSM8K_delta":"+17.9"}],"unit":"accuracy (%)"}
</transcription_json>

<transcription_notes>
- Table spans full width; columns left-to-right: Method, AddSub, MultiArith, ASDiv, AQuA, SVAMP, GSM8K.
- "Previous SoTA" row contains superscript citations: ^a, ^b, ^c, ^d, ^e, ^g referring to sources listed in caption.
- Self-consistency rows show absolute value followed by the absolute improvement in parentheses, e.g., "24.8 (+6.6)".
- Best performances (per task) are bolded in original PDF (bolding not preserved here).
- Fonts: numeric values use same monospaced font as surrounding table.
</transcription_notes>
</transcription_table>

Table 2: Arithmetic reasoning accuracy by self-consistency compared to chain-of-thought prompting (Wei et al., 2022). The previous SoTA baselines are obtained from: a: Relevance and LCA operation classifier (Roy & Roth, 2015), b: Lan et al. (2021), c: Amini et al. (2019), d: Pi et al. (2022), e: GPT-3 175B finetuned with 7.5k examples (Cobbe et al., 2021), g: GPT-3 175B finetuned plus an additional 175B verifier (Cobbe et al., 2021). The best performance for each task is shown in bold.

<transcription_table>
**Table 3: Commonsense and symbolic reasoning accuracy by self-consistency compared to chain-of-thought prompting**

| Method | CSQA | StrategyQA | ARC-e | ARC-c | Letter (4) | Coinflip (4) |
|--------|-----:|-----------:|------:|------:|-----------:|--------------:|
| Previous SoTA | 91.2^a | 73.9^b | 86.4^c | 75.0^c | N/A | N/A |
| UL2-20B — CoT-prompting | 51.4 | 53.3 | 61.6 | 42.9 | 0.0 | 50.4 |
| UL2-20B — Self-consistency | 55.7 (+4.3) | 54.9 (+1.6) | 69.8 (+8.2) | 49.5 (+6.8) | 0.0 (+0.0) | 50.5 (+0.1) |
| LaMDA-137B — CoT-prompting | 57.9 | 65.4 | 75.3 | 55.1 | 8.2 | 72.4 |
| LaMDA-137B — Self-consistency | 63.1 (+5.2) | 67.8 (+2.4) | 79.3 (+4.0) | 59.8 (+4.7) | 8.2 (+0.0) | 73.5 (+1.1) |
| PaLM-540B — CoT-prompting | 79.0 | 75.3 | 95.3 | 85.2 | 65.8 | 88.2 |
| PaLM-540B — Self-consistency | 80.7 (+1.7) | 81.6 (+6.3) | 96.4 (+1.1) | 88.7 (+3.5) | 70.8 (+5.0) | 91.2 (+3.0) |
| GPT-3 (code-davinci-001) — CoT-prompting | 46.6 | 56.7 | 63.1 | 43.1 | 7.8 | 71.4 |
| GPT-3 (code-davinci-001) — Self-consistency | 54.9 (+8.3) | 61.7 (+5.0) | 72.1 (+9.0) | 53.7 (+10.6) | 10.0 (+2.2) | 75.9 (+4.5) |
| GPT-3 (code-davinci-002) — CoT-prompting | 79.0 | 73.4 | 94.0 | 83.6 | 70.4 | 99.0 |
| GPT-3 (code-davinci-002) — Self-consistency | 81.5 (+2.5) | 79.8 (+6.4) | 96.0 (+2.0) | 87.5 (+3.9) | 73.4 (+3.0) | 99.5 (+0.5) |

<transcription_json>
{"table_type":"data_table","title":"Table 3: Commonsense and symbolic reasoning accuracy by self-consistency compared to chain-of-thought prompting","columns":["Method","CSQA","StrategyQA","ARC-e","ARC-c","Letter (4)","Coinflip (4)"],"data":[{"Method":"Previous SoTA","CSQA":"91.2^a","StrategyQA":"73.9^b","ARC-e":"86.4^c","ARC-c":"75.0^c","Letter (4)":"N/A","Coinflip (4)":"N/A"},{"Method":"UL2-20B — CoT-prompting","CSQA":51.4,"StrategyQA":53.3,"ARC-e":61.6,"ARC-c":42.9,"Letter (4)":0.0,"Coinflip (4)":50.4},{"Method":"UL2-20B — Self-consistency","CSQA":55.7,"CSQA_delta":"+4.3","StrategyQA":54.9,"StrategyQA_delta":"+1.6","ARC-e":69.8,"ARC-e_delta":"+8.2","ARC-c":49.5,"ARC-c_delta":"+6.8","Letter (4)":0.0,"Letter (4)_delta":"+0.0","Coinflip (4)":50.5,"Coinflip (4)_delta":"+0.1"},{"Method":"LaMDA-137B — CoT-prompting","CSQA":57.9,"StrategyQA":65.4,"ARC-e":75.3,"ARC-c":55.1,"Letter (4)":8.2,"Coinflip (4)":72.4},{"Method":"LaMDA-137B — Self-consistency","CSQA":63.1,"CSQA_delta":"+5.2","StrategyQA":67.8,"StrategyQA_delta":"+2.4","ARC-e":79.3,"ARC-e_delta":"+4.0","ARC-c":59.8,"ARC-c_delta":"+4.7","Letter (4)":8.2,"Letter (4)_delta":"+0.0","Coinflip (4)":73.5,"Coinflip (4)_delta":"+1.1"},{"Method":"PaLM-540B — CoT-prompting","CSQA":79.0,"StrategyQA":75.3,"ARC-e":95.3,"ARC-c":85.2,"Letter (4)":65.8,"Coinflip (4)":88.2},{"Method":"PaLM-540B — Self-consistency","CSQA":80.7,"CSQA_delta":"+1.7","StrategyQA":81.6,"StrategyQA_delta":"+6.3","ARC-e":96.4,"ARC-e_delta":"+1.1","ARC-c":88.7,"ARC-c_delta":"+3.5","Letter (4)":70.8,"Letter (4)_delta":"+5.0","Coinflip (4)":91.2,"Coinflip (4)_delta":"+3.0"},{"Method":"GPT-3 (code-davinci-001) — CoT-prompting","CSQA":46.6,"StrategyQA":56.7,"ARC-e":63.1,"ARC-c":43.1,"Letter (4)":7.8,"Coinflip (4)":71.4},{"Method":"GPT-3 (code-davinci-001) — Self-consistency","CSQA":54.9,"CSQA_delta":"+8.3","StrategyQA":61.7,"StrategyQA_delta":"+5.0","ARC-e":72.1,"ARC-e_delta":"+9.0","ARC-c":53.7,"ARC-c_delta":"+10.6","Letter (4)":10.0,"Letter (4)_delta":"+2.2","Coinflip (4)":75.9,"Coinflip (4)_delta":"+4.5"},{"Method":"GPT-3 (code-davinci-002) — CoT-prompting","CSQA":79.0,"StrategyQA":73.4,"ARC-e":94.0,"ARC-c":83.6,"Letter (4)":70.4,"Coinflip (4)":99.0},{"Method":"GPT-3 (code-davinci-002) — Self-consistency","CSQA":81.5,"CSQA_delta":"+2.5","StrategyQA":79.8,"StrategyQA_delta":"+6.4","ARC-e":96.0,"ARC-e_delta":"+2.0","ARC-c":87.5,"ARC-c_delta":"+3.9","Letter (4)":73.4,"Letter (4)_delta":"+3.0","Coinflip (4)":99.5,"Coinflip (4)_delta":"+0.5"}],"unit":"accuracy (%)"}
</transcription_json>

<transcription_notes>
- Table 3 columns (left-to-right): Method, CSQA, StrategyQA, ARC-e, ARC-c, Letter (4), Coinflip (4).
- "Previous SoTA" row contains superscript citations referencing sources listed in the paper caption/notes.
- Self-consistency rows show improvement deltas in parentheses, e.g., "55.7 (+4.3)".
- Some tasks (Letter (4) / Coinflip (4)) include "N/A" for previous SoTA.
</transcription_notes>
</transcription_table>

Table 3: Commonsense and symbolic reasoning accuracy by self-consistency compared to chain-of-thought prompting (Wei et al., 2022). The previous SoTA baselines are obtained from: a: DeBERTaV3-large + KEAR (Xu et al., 2021b), b: Chowdhery et al. (2022), c: UnifiedQA-FT (Khashabi et al., 2020). The best performance for each task is shown in bold.

7 The standard deviation of self-consistency is ≤ 0.5 for all tasks and is thus omitted in the table. Please refer to Figure 2, Figure 7 and 8 for the standard deviations under varying numbers of sampled paths.

<!-- Decorative: [page number centered] -->
<transcription_page_footer> Page 5 </transcription_page_footer>

---

<transcription_page_header> Published as a conference paper at ICLR 2023 | Section </transcription_page_header>

<!-- Section 1 -->
## Commonsense and Symbolic Reasoning

Table 3 shows the results on commonsense and symbolic reasoning tasks. Similarly, self-consistency yields large gains across all four language models, and obtained SoTA results on 5 out of 6 tasks. For symbolic reasoning, we test the out-of-distribution (OOD) setting where the input prompt contains examples of 2-letters or 2-flips but we test examples of 4-letters and 4-flips (this setting is more challenging as PaLM-540B or GPT-3 can already achieve perfect in-distribution accuracy). In this challenging OOD setting, the gain of self-consistency is still quite significant compared to CoT-prompting with sufficient model sizes.

To show the effect of the number of sampled reasoning paths, we plot the accuracy (mean and standard deviation over 10 runs) with respect to varying numbers of sampled paths (1, 5, 10, 20, 40) in Figure 2. The results show that sampling a higher number (e.g., 40) of reasoning paths leads to a consistently better performance, further emphasizing the importance of introducing diversity in the reasoning paths. In Table 4, we show self-consistency yields a richer set of reasoning paths compared to greedy decoding with a few example questions from two tasks.

<transcription_image>
**Figure 2: Self-consistency (blue) significantly improves accuracy over CoT-prompting with greedy decoding (orange) across arithmetic and commonsense reasoning tasks, over LaMDA-137B. Sampling a higher number of diverse reasoning paths consistently improves reasoning accuracy.**

```ascii
[LINE PLOTS - Accuracy vs #Sampled Reasoning Paths]
X-axis: #Sampled Reasoning Paths (1,5,10,20,40)
Y-axis: Accuracy (%)

MultiArith:
  Greedy Decode (orange): 55.0, 55.0, 55.0, 55.0, 55.0
  Self Consistency (blue): 67.0, 70.0, 72.0, 73.5, 74.5

SVAMP:
  Greedy Decode (orange): 42.0, 42.0, 42.0, 42.0, 42.0
  Self Consistency (blue): 47.0, 52.0, 54.0, 55.5, 56.5

Commonsense QA:
  Greedy Decode (orange): 56.0, 56.0, 56.0, 56.0, 56.0
  Self Consistency (blue): 58.0, 60.0, 61.0, 61.5, 62.0

ARC (Challenge):
  Greedy Decode (orange): 53.0, 53.0, 53.0, 53.0, 53.0
  Self Consistency (blue): 54.0, 56.0, 57.0, 57.5, 58.5

Legend:
  Orange = Greedy Decode (Single-path)
  Blue   = Self Consistency (Multi-path)
```

<transcription_json>
{"chart_type":"line_plots","title":"Accuracy vs #Sampled Reasoning Paths (Figure 2)","x_values":[1,5,10,20,40],"series":[{"name":"MultiArith - Greedy Decode (orange)","values":[55.0,55.0,55.0,55.0,55.0],"unit":"%","uncertainty":"[unclear: approx]"},{"name":"MultiArith - Self Consistency (blue)","values":[67.0,70.0,72.0,73.5,74.5],"unit":"%","uncertainty":"[unclear: approx]"},{"name":"SVAMP - Greedy Decode (orange)","values":[42.0,42.0,42.0,42.0,42.0],"unit":"%","uncertainty":"[unclear: approx]"},{"name":"SVAMP - Self Consistency (blue)","values":[47.0,52.0,54.0,55.5,56.5],"unit":"%","uncertainty":"[unclear: approx]"},{"name":"Commonsense QA - Greedy Decode (orange)","values":[56.0,56.0,56.0,56.0,56.0],"unit":"%","uncertainty":"[unclear: approx]"},{"name":"Commonsense QA - Self Consistency (blue)","values":[58.0,60.0,61.0,61.5,62.0],"unit":"%","uncertainty":"[unclear: approx]"},{"name":"ARC (Challenge) - Greedy Decode (orange)","values":[53.0,53.0,53.0,53.0,53.0],"unit":"%","uncertainty":"[unclear: approx]"},{"name":"ARC (Challenge) - Self Consistency (blue)","values":[54.0,56.0,57.0,57.5,58.5],"unit":"%","uncertainty":"[unclear: approx]"}],"notes":"Values estimated from plotted curves; exact numbers in original figure may differ. All numbers marked [unclear: approx] where not explicitly printed."}
</transcription_json>

<transcription_notes>
- Type: 4 small line plots arranged left-to-right: MultiArith, SVAMP, Commonsense QA, ARC (Challenge).
- Colors: blue = Self Consistency (multi-path), orange = Greedy Decode (single-path).
- X-axis ticks visible at roughly: 0,5,10,15,20,25,30,35,40 (we report only the sampled x-values 1,5,10,20,40 used in caption).
- Y-axis labeled "Accuracy (%)". Exact numeric points are estimated from figure; original plot shows mean and standard deviation over 10 runs (error bars visible).
- Legend below plots: orange square labeled "Greedy Decode (Single-path)"; blue line labeled "Self Consistency (Multi-path)".
</transcription_notes>
</transcription_image>

<!-- Section 2 -->
<transcription_table>
**Table 4: Examples where self-consistency helps repair the errors over greedy decode, on PaLM-540B. Two sampled reasoning paths that are consistent with the ground truth are shown.**

| GSM8K | StrategyQA |
|-------|------------|
| **Question**: Henry made two stops during his 60-mile bike trip. He first stopped after 20 miles. His second stop was 15 miles before the end of the trip. How many miles did he travel between his first and second stops? | **Question**: Yes or no: Is Albany, Georgia the most populous US Albany? |
| **Greedy Decode**: He traveled 60 miles in total. He stopped after 20 miles, so he traveled 60 - 20 = 40 miles between the first and second stops. The answer is 40. | **Greedy Decode**: Albany, Georgia is the most populous US Albany. Thus, the answer is Yes. |
| **Sampled Path 1**: Henry travelled a total of 60 miles. His first stop was 20 miles in, and his second stop was 15 miles before the end. So between his first and second stops he travelled 60 - 20 - 15 = 25 miles. The answer is 25. | **Sampled Path 1**: The most populous US Albany is Albany, New York. Thus, the answer is No. |
| **Sampled Path 2**: He made two stops during a 60-mile trip. The first was 20 miles into the trip. The second was 15 miles before the end. The second stop was at 60 - 15 = 45 miles, so the distance between stops is 45 - 20 = 25 miles. The answer is 25. | **Sampled Path 2**: Albany, Georgia has a population of about 88,000. Albany, New York has a population of about 95,000. Thus, Albany, Georgia is not the most populous US Albany. So the answer is No. |

<transcription_json>
{"table_type":"example_table","title":"Table 4: Examples where self-consistency helps repair the errors over greedy decode, on PaLM-540B.","columns":["GSM8K","StrategyQA"],"data":[{"Question":"Henry made two stops during his 60-mile bike trip. He first stopped after 20 miles. His second stop was 15 miles before the end of the trip. How many miles did he travel between his first and second stops?","Greedy Decode":"He traveled 60 miles in total. He stopped after 20 miles, so he traveled 60 - 20 = 40 miles between the first and second stops. The answer is 40.","Sampled Path 1":"Henry travelled a total of 60 miles. His first stop was 20 miles in, and his second stop was 15 miles before the end. So between his first and second stops he travelled 60 - 20 - 15 = 25 miles. The answer is 25.","Sampled Path 2":"He made two stops during a 60-mile trip. The first was 20 miles into the trip. The second was 15 miles before the end. The second stop was at 60 - 15 = 45 miles, so the distance between stops is 45 - 20 = 25 miles. The answer is 25."},{"Question":"Yes or no: Is Albany, Georgia the most populous US Albany?","Greedy Decode":"Albany, Georgia is the most populous US Albany. Thus, the answer is Yes.","Sampled Path 1":"The most populous US Albany is Albany, New York. Thus, the answer is No.","Sampled Path 2":"Albany, Georgia has a population of about 88,000. Albany, New York has a population of about 95,000. Thus, Albany, Georgia is not the most populous US Albany. So the answer is No."}],"notes":"Two sampled reasoning paths (Sampled Path 1 and Path 2) are shown for each task. Greedy decode demonstrates a common incorrect output for GSM8K."
</transcription_json>

<transcription_notes>
- Layout: two-column table comparing outputs for GSM8K (arithmetic) and StrategyQA (commonsense yes/no).
- Colors in original: alternate row shading and vertical separators; preserve textual content only.
- Source: examples illustrating how self-consistency can correct greedy-decoding errors.
</transcription_notes>
</transcription_table>

<!-- Section 3 -->
### 3.3 SELF-CONSISTENCY HELPS WHEN CHAIN-OF-THOUGHT HURTS PERFORMANCE

Ye & Durrett (2022) show that sometimes chain-of-thought prompting could hurt performance compared to standard prompting in few-shot in-context learning. Here we perform a study using self-consistency to see if it can help fill in the gap, over a set of common NLP tasks, including (1) Closed-Book Question Answering: BoolQ (Clark et al., 2019), HotpotQA (Yang et al., 2018), and (2) Natural Language Inference: e-SNLI (Camburu et al., 2018), ANLI (Nie et al., 2020) and RTE (Dagan et al., 2005; Bar-Haim et al., 2006; Giampiccolo et al., 2007; Bentivogli et al., 2009).

The results over PaLM-540B are shown in Table 5. For some tasks (e.g., ANLI-R1, e-SNLI, RTE), adding chain-of-thought does hurt performance compared to standard prompting (Brown et al., 2020), but self-consistency is able to robustly boost the performance and outperform standard prompting, making it a reliable way to add rationales in few-shot in-context learning for common NLP tasks.

<transcription_table>
**Table 5: Compare Standard/CoT prompting with self-consistency on common NLP tasks.**

| Method | ANLI R1 / R2 / R3 | e-SNLI | RTE | BoolQ | HotpotQA (EM / F1) |
|--------|-------------------:|-------:|----:|------:|-------------------:|
| Standard-prompting (no-rationale) | 69.1 / 55.8 / 55.8 | 85.8 | 84.8 | 71.3 | 27.1 / 36.8 |
| CoT-prompting (Wei et al., 2022)  | 68.8 / 58.9 / 60.6 | 81.0 | 79.1 | 74.2 | 28.9 / 39.8 |
| Self-consistency                  | 78.5 / 64.5 / 63.4 | 88.4 | 86.3 | 78.4 | 33.8 / 44.6 |

<transcription_json>
{"table_type":"metrics_table","title":"Table 5: Compare Standard/CoT prompting with self-consistency on common NLP tasks.","columns":["Method","ANLI R1 / R2 / R3","e-SNLI","RTE","BoolQ","HotpotQA (EM / F1)"],"data":[{"Method":"Standard-prompting (no-rationale)","ANLI R1 / R2 / R3":"69.1 / 55.8 / 55.8","e-SNLI":85.8,"RTE":84.8,"BoolQ":71.3,"HotpotQA EM / F1":"27.1 / 36.8"},{"Method":"CoT-prompting (Wei et al., 2022)","ANLI R1 / R2 / R3":"68.8 / 58.9 / 60.6","e-SNLI":81.0,"RTE":79.1,"BoolQ":74.2,"HotpotQA EM / F1":"28.9 / 39.8"},{"Method":"Self-consistency","ANLI R1 / R2 / R3":"78.5 / 64.5 / 63.4","e-SNLI":88.4,"RTE":86.3,"BoolQ":78.4,"HotpotQA EM / F1":"33.8 / 44.6"}],"unit_notes":"ANLI entries are three numbers for R1/R2/R3. HotpotQA reported as EM / F1."}
</transcription_json>

<transcription_notes>
- Table shows comparative results (percentages) on multiple NLP tasks for PaLM-540B.
- Bold/italic styling in original omitted; numeric values preserved as shown.
- Source: experiments comparing Standard prompting, Chain-of-thought prompting, and Self-consistency.
</transcription_notes>
</transcription_table>

<!-- Decorative: [horizontal rules, page header/footer separators] -->

<transcription_page_footer> Page 6 | ICLR 2023 </transcription_page_footer>

---

<transcription_page_header>Published as a conference paper at ICLR 2023</transcription_page_header>

## 3.4 COMPARE TO OTHER EXISTING APPROACHES

We conduct a set of additional studies and show that self-consistency significantly outperforms existing methods including sample-and-rank, beam search, and ensemble-based approaches.

### Comparison to Sample-and-Rank

One commonly used approach to improve generation quality is sample-and-rank, where multiple sequences are sampled from the decoder and then ranked according to each sequence's log probability (Adiwardana et al., 2020). We compare self-consistency with sample-and-rank on GPT-3 code-davinci-001, by sampling the same number of sequences from the decoder as self-consistency and taking the final answer from the top-ranked sequence. The results are shown in Figure 3. While sample-and-rank does improve the accuracy with additionally sampled sequences and ranking, the gain is much smaller compared to self-consistency.

<transcription_image>
**Figure 3: Self-consistency significantly outperforms sample-and-rank with the same # of samples.**

```ascii
[LINE CHARTS - Accuracy (%) vs #Sampled Reasoning Paths]

GSM8K
Accuracy (%)
24 ┤                      ★
22 ┤                    ★  |
20 ┤                 ★  ▪  |
18 ┤             ★   ▪  ▪  |
16 ┤         ★   ▪   ▪  ○ |
14 ┤    ○   ▪   ▪   ○  ○  |
12 ┼────────────────────────
     0  5 10 15 20 25 30 35 40
Legend:
★ Self Consistency (Multi-path)
▪ Sample & Rank (Multi-path)
○ Greedy Decode (Single-path)


MultiArith
Accuracy (%)
80 ┤                        ★
75 ┤                     ★  ▪
70 ┤                  ★   ▪ ▪
65 ┤               ★   ▪  ▪
60 ┤          ▪    ▪   ○  ○
55 ┤     ○   ▪   ○   ○
50 ┼────────────────────────
     0  5 10 15 20 25 30 35 40


ARC (Challenge)
Accuracy (%)
55 ┤                     ★
50 ┤                 ★  ▪
45 ┤             ★   ▪ ▪
40 ┤         ▪   ▪  ○  ○
35 ┤     ○   ▪   ○   ○
30 ┼────────────────────────
     0  5 10 15 20 25 30 35 40
```

<transcription_json>
{"chart_type": "multi_line", "title": "Figure 3: Accuracy vs #Sampled Reasoning Paths", "x_axis": {"label": "#Sampled Reasoning Paths", "ticks": [0,5,10,15,20,25,30,35,40]}, "series": [{"name": "Self Consistency (Multi-path)", "marker": "star", "GSM8K": [{"x":0,"y":"[unclear: ~14]"}, {"x":5,"y":"[unclear: ~17]"}, {"x":10,"y":"[unclear: ~19.5]"}, {"x":15,"y":"[unclear: ~20.5]"}, {"x":20,"y":"[unclear: ~21.5]"}, {"x":25,"y":"[unclear: ~22]"}, {"x":30,"y":"[unclear: ~23]"}, {"x":35,"y":"[unclear: ~23.5]"}, {"x":40,"y":"[unclear: ~24]"}], "MultiArith": [{"x":0,"y":"[unclear: ~60]"}, {"x":5,"y":"[unclear: ~68]"}, {"x":10,"y":"[unclear: ~72]"}, {"x":15,"y":"[unclear: ~74]"}, {"x":20,"y":"[unclear: ~75]"}, {"x":25,"y":"[unclear: ~76]"}, {"x":30,"y":"[unclear: ~77.5]"}, {"x":35,"y":"[unclear: ~78.5]"}, {"x":40,"y":"[unclear: ~79.5]"}], "ARC-Challenge": [{"x":0,"y":"[unclear: ~34]"}, {"x":5,"y":"[unclear: ~44]"}, {"x":10,"y":"[unclear: ~48]"}, {"x":15,"y":"[unclear: ~50]"}, {"x":20,"y":"[unclear: ~51]"}, {"x":25,"y":"[unclear: ~52]"}, {"x":30,"y":"[unclear: ~53]"}, {"x":35,"y":"[unclear: ~54]"}, {"x":40,"y":"[unclear: ~55]"}]}, {"name": "Sample & Rank (Multi-path)", "marker": "square", "GSM8K": [{"x":0,"y":"[unclear: ~15]"}, {"x":5,"y":"[unclear: ~16]"}, {"x":10,"y":"[unclear: ~17]"}, {"x":15,"y":"[unclear: ~17.5]"}, {"x":20,"y":"[unclear: ~17.5]"}, {"x":25,"y":"[unclear: ~18]"}, {"x":30,"y":"[unclear: ~18.5]"}, {"x":35,"y":"[unclear: ~18.8]"}, {"x":40,"y":"[unclear: ~19.0]"}], "MultiArith": [{"x":0,"y":"[unclear: ~58]"}, {"x":5,"y":"[unclear: ~62]"}, {"x":10,"y":"[unclear: ~64]"}, {"x":15,"y":"[unclear: ~65]"}, {"x":20,"y":"[unclear: ~66]"}, {"x":25,"y":"[unclear: ~66.5]"}, {"x":30,"y":"[unclear: ~67]"}, {"x":35,"y":"[unclear: ~67.5]"}, {"x":40,"y":"[unclear: ~68]"}], "ARC-Challenge": [{"x":0,"y":"[unclear: ~37]"}, {"x":5,"y":"[unclear: ~42]"}, {"x":10,"y":"[unclear: ~44]"}, {"x":15,"y":"[unclear: ~45]"}, {"x":20,"y":"[unclear: ~46]"}, {"x":25,"y":"[unclear: ~46.5]"}, {"x":30,"y":"[unclear: ~47]"}, {"x":35,"y":"[unclear: ~47.5]"}, {"x":40,"y":"[unclear: ~48]"}]}, {"name": "Greedy Decode (Single-path)", "marker": "circle", "GSM8K": [{"x":0,"y":14}, {"x":5,"y":"[unclear: ~14]"}, {"x":10,"y":"[unclear: ~14]"}, {"x":15,"y":"[unclear: ~14.5]"}, {"x":20,"y":"[unclear: ~14]"}, {"x":25,"y":"[unclear: ~14]"}, {"x":30,"y":"[unclear: ~14]"}, {"x":35,"y":"[unclear: ~14]"}, {"x":40,"y":"[unclear: ~14]"}], "MultiArith": [{"x":0,"y":55}, {"x":5,"y":"[unclear: ~55]"}, {"x":10,"y":"[unclear: ~55]"}, {"x":15,"y":"[unclear: ~55]"}, {"x":20,"y":"[unclear: ~55]"}, {"x":25,"y":"[unclear: ~55]"}, {"x":30,"y":"[unclear: ~55]"}, {"x":35,"y":"[unclear: ~55]"}, {"x":40,"y":"[unclear: ~55]"}], "ARC-Challenge": [{"x":0,"y":"[unclear: ~36]"}, {"x":5,"y":"[unclear: ~36]"}, {"x":10,"y":"[unclear: ~36]"}, {"x":15,"y":"[unclear: ~36]"}, {"x":20,"y":"[unclear: ~36]"}, {"x":25,"y":"[unclear: ~36]"}, {"x":30,"y":"[unclear: ~36]"}, {"x":35,"y":"[unclear: ~36]"}, {"x":40,"y":"[unclear: ~36]"}]}], "notes": "Values marked with [unclear: ~value] indicate visually estimated points where exact numeric labels are not fully legible in the image."}
</transcription_json>

<transcription_notes>
- Figure contains three small line plots side-by-side: GSM8K (left), MultiArith (center), ARC (Challenge) (right).
- Colors/markers: blue star = Self Consistency (Multi-path); green square = Sample & Rank (Multi-path); orange circle = Greedy Decode (Single-path).
- X-axis ticks visible at 0, 5, 10, 15, 20, 25, 30, 35, 40 (# Sampled Reasoning Paths).
- Y-axis ranges (approx): GSM8K: 12–24 (%); MultiArith: 50–80 (%); ARC (Challenge): 30–55 (%).
- ASCII approximates relative curve shapes and ordering; specific numeric y-values are visually estimated and flagged as [unclear: ~value] where exact digits are not fully legible.
</transcription_notes>
</transcription_image>

### Comparison to Beam Search

In Table 6, we compare self-consistency with beam search decoding on the UL2-20B model. For a fair comparison we report the accuracy under the same number of beams and reasoning paths. On both tasks self-consistency outperforms beam search significantly. Note self-consistency can also adopt beam search to decode each reasoning path (results are shown as "Self-consistency using beam search"), but its performance is worse compared to self-consistency with sampling. The reason is that beam search yields a lower diversity in the outputs (Li & Jurafsky, 2016), while in self-consistency the diversity of the reasoning paths is the key to a better performance.

<transcription_table>
**Table 6: Compare self-consistency with beam search decoding on the UL2-20B model.**

Beam size / Self-consistency paths | 1 | 5 | 10 | 20 | 40
---|---:|---:|---:|---:|---:
AQuA — Beam search decoding (top beam) | 23.6 | 19.3 | 16.1 | 15.0 | 10.2
AQuA — Self-consistency using beam search | 23.6 | 19.8 ± 0.3 | 21.2 ± 0.7 | 24.6 ± 0.4 | 24.2 ± 0.5
AQuA — Self-consistency using sampling | 19.7 ± 2.5 | 24.9 ± 2.6 | 25.3 ± 1.8 | 26.7 ± 1.0 | 26.9 ± 0.5

Beam size / Self-consistency paths | 1 | 5 | 10 | 20 | 40
---|---:|---:|---:|---:|---:
MultiArith — Beam search decoding (top beam) | 10.7 | 12.0 | 11.3 | 11.0 | 10.5
MultiArith — Self-consistency using beam search | 10.7 | 11.8 ± 0.0 | 11.4 ± 0.1 | 12.3 ± 0.1 | 10.8 ± 0.1
MultiArith — Self-consistency using sampling | 9.5 ± 1.2 | 11.3 ± 1.2 | 12.3 ± 0.8 | 13.7 ± 0.9 | 14.7 ± 0.3

<transcription_json>
{"table_type": "comparison_table", "title": "Compare self-consistency with beam search decoding on the UL2-20B model", "columns": ["Beam size / Self-consistency paths", "1", "5", "10", "20", "40"], "data": [{"task":"AQuA - Beam search decoding (top beam)","1":23.6,"5":19.3,"10":16.1,"20":15.0,"40":10.2},{"task":"AQuA - Self-consistency using beam search","1":23.6,"5":"19.8 ± 0.3","10":"21.2 ± 0.7","20":"24.6 ± 0.4","40":"24.2 ± 0.5"},{"task":"AQuA - Self-consistency using sampling","1":"19.7 ± 2.5","5":"24.9 ± 2.6","10":"25.3 ± 1.8","20":"26.7 ± 1.0","40":"26.9 ± 0.5"},{"task":"MultiArith - Beam search decoding (top beam)","1":10.7,"5":12.0,"10":11.3,"20":11.0,"40":10.5},{"task":"MultiArith - Self-consistency using beam search","1":10.7,"5":"11.8 ± 0.0","10":"11.4 ± 0.1","20":"12.3 ± 0.1","40":"10.8 ± 0.1"},{"task":"MultiArith - Self-consistency using sampling","1":"9.5 ± 1.2","5":"11.3 ± 1.2","10":"12.3 ± 0.8","20":"13.7 ± 0.9","40":"14.7 ± 0.3"}], "unit": "accuracy (%)", "model": "UL2-20B"}
</transcription_json>

<transcription_notes>
- Table 6 contains two subtables (AQuA and MultiArith) comparing beam search (top beam), self-consistency using beam search, and self-consistency using sampling across beam sizes / sampled-path counts {1,5,10,20,40}.
- Values include reported mean ± standard deviation where shown in the image.
- Source/model: UL2-20B.
</transcription_notes>
</transcription_table>

### Comparison to Ensemble-based Approaches

We further compare self-consistency to ensemble-based methods for few-shot learning. In particular, we consider ensembling by: (1) prompt order permutation: we randomly permute the exemplars in the prompt 40 times to mitigate model's sensitivity to prompt order (Zhao et al., 2021; Lu et al., 2021); and (2) multiple sets of prompts (Gao et al., 2021): we manually write 3 different sets of prompts. We took majority vote of the answers from greedy decoding in both approaches as an ensemble. Table 7 shows that compared to self-consistency, existing ensemble-based approaches achieve a much smaller gain.8 In addition, note that self-consistency is different from a typical model-ensemble approach, where multiple models are trained and their outputs are aggregated. Self-consistency acts more like a "self-ensemble" on top of a single language model. We additionally show the results of ensembling multiple models in Appendix A.1.3 where the model-ensembles perform much worse compared to self-consistency.

<transcription_table>
**Table 7: Self-consistency outperforms prompt-order and multi-prompt ensembles on LaMDA-137B.**

| Method (Wei et al., 2022 / ensembles / self-consistency) | GSM8K | MultiArith | SVAMP | ARC-e | ARC-c |
|---|---:|---:|---:|---:|---:|
| CoT (Wei et al., 2022) | 17.1 | 51.8 | 38.9 | 75.3 | 55.1 |
| Ensemble (3 sets of prompts) | 18.6 ± 0.5 | 57.1 ± 0.7 | 42.1 ± 0.6 | 76.6 ± 0.1 | 57.0 ± 0.2 |
| Ensemble (40 prompt permutations) | 19.2 ± 0.1 | 60.9 ± 0.2 | 42.7 ± 0.1 | 76.9 ± 0.1 | 57.0 ± 0.1 |
| Self-Consistency (40 sampled paths) | 27.7 ± 0.2 | 75.7 ± 0.3 | 53.3 ± 0.2 | 79.3 ± 0.3 | 59.8 ± 0.2 |

<transcription_json>
{"table_type":"data_table","title":"Self-consistency outperforms prompt-order and multi-prompt ensembles on LaMDA-137B","columns":["Method","GSM8K","MultiArith","SVAMP","ARC-e","ARC-c"], "data":[{"Method":"CoT (Wei et al., 2022)","GSM8K":17.1,"MultiArith":51.8,"SVAMP":38.9,"ARC-e":75.3,"ARC-c":55.1},{"Method":"Ensemble (3 sets of prompts)","GSM8K":"18.6 ± 0.5","MultiArith":"57.1 ± 0.7","SVAMP":"42.1 ± 0.6","ARC-e":"76.6 ± 0.1","ARC-c":"57.0 ± 0.2"},{"Method":"Ensemble (40 prompt permutations)","GSM8K":"19.2 ± 0.1","MultiArith":"60.9 ± 0.2","SVAMP":"42.7 ± 0.1","ARC-e":"76.9 ± 0.1","ARC-c":"57.0 ± 0.1"},{"Method":"Self-Consistency (40 sampled paths)","GSM8K":"27.7 ± 0.2","MultiArith":"75.7 ± 0.3","SVAMP":"53.3 ± 0.2","ARC-e":"79.3 ± 0.3","ARC-c":"59.8 ± 0.2"}], "unit":"accuracy (%)", "model":"LaMDA-137B"}
</transcription_json>

<transcription_notes>
- Table shows comparisons across datasets GSM8K, MultiArith, SVAMP, ARC-e, ARC-c for different ensembling methods and self-consistency.
- Self-Consistency (40 sampled paths) shows substantially higher accuracies across the board.
- Values include mean ± standard deviation where present.
- Footnote 8 (printed on the page): "8 Self-consistency is compatible with both ensemble approaches and we show the results in Appendix A.1.4."
</transcription_notes>
</transcription_table>

8 Self-consistency is compatible with both ensemble approaches and we show the results in Appendix A.1.4.

<transcription_page_footer>Page 7</transcription_page_footer>

---

<transcription_page_header> Published as a conference paper at ICLR 2023 </transcription_page_header>

## 3.5 ADDITIONAL STUDIES

<!-- Section 1 -->
<!-- Column 1 -->
We conducted a number of additional experiments to analyze different aspects of the self-consistency method, including its robustness to sampling strategies and parameters, and how it works with imperfect prompts and non-natural-language reasoning paths.

### Self-Consistency is Robust to Sampling Strategies and Scaling
We show self-consistency is robust to sampling strategies and parameters, by varying T in temperature sampling (Ackley et al., 1985; Ficler & Goldberg, 2017), k in top-k sampling (Fan et al., 2018; Holtzman et al., 2018; Radford et al., 2019), and p in nucleus sampling (Holtzman et al., 2020), over PaLM-540B in Figure 4 (left). Figure 4 (right) shows that self-consistency robustly improves performance across all scales for the LaMDA-137B model series. The gain is relatively lower for smaller models due to certain abilities (e.g., arithmetic) only emerge when the model reaches a sufficient scale (Brown et al., 2020).

<transcription_image>
**Figure 4: GSM8K accuracy. (Left) Self-consistency is robust to various sampling strategies and parameters. (Right) Self-consistency improves performance across language model scales.**

```ascii
[LEFT - GSM8K Accuracy vs #Sampled Reasoning Paths]
Y-axis: Accuracy (%) from 44 to 76 (ticks: 44, 46, 48, ..., 76)
X-axis: #Sampled Reasoning Paths (0, 5, 10, 15, 20, 25, 30, 35, 40)

Legend:
- T=0.7, k=40        : ● (purple)
- T=0.5, k=40        : ■ (green)
- T=0.3, k=40        : ▲ (red)
- T=0.7, k=20        : ◆ (orange)
- T=0.7, no top k    : ○ (grey)
- p=0.95             : ⊙ (olive)
- p=0.9              : ✕ (brown)
- Greedy Decode      : ––––– (flat, lowest)

Representative curve shapes (approximate):
#Paths  0    5    10   15   20   25   30   35   40
T=0.7,40 48 -> 66 -> 70 -> 71 -> 72 -> 72 -> 72 -> 72 -> 72
T=0.5,40 46 -> 64 -> 68 -> 69 -> 70 -> 71 -> 71 -> 71 -> 71
T=0.3,40 44 -> 60 -> 66 -> 67 -> 68 -> 68 -> 68 -> 68 -> 68
Greedy   44 -> 48 -> 50 -> 51 -> 51 -> 51 -> 51 -> 51 -> 51

[RIGHT - Model Scale vs Accuracy (%)]
Y-axis: Accuracy (%) 0 to 25 (ticks approx 0,5,10,15,20,25)
X-axis: Model size (#param in billions) log scale: 1, 2, 5, 10, 20, 50, 100, 200

Legend:
- Self Consistency : ● (blue)
- Greedy Decode    : ■ (orange)

Representative points (approximate):
Model size (B) : Greedy (%) -> Self-Consistency (%)
1  : 2 -> 3
2  : 3 -> 4
5  : 4 -> 6
10 : 5 -> 8
20 : 8 -> 12
50 : 10 -> 15
100: 12 -> 18
200: 15 -> 25
```

<transcription_json>
{
  "chart_type": "multi_plot",
  "title": "Figure 4: GSM8K accuracy (Left: sampling strategies; Right: model scale)",
  "left_plot": {
    "plot_type": "line_chart",
    "x_label": "#Sampled Reasoning Paths",
    "x_values": [0,5,10,15,20,25,30,35,40],
    "y_label": "Accuracy (%)",
    "y_ticks": [44,46,48,50,52,54,56,58,60,62,64,66,68,70,72,74,76],
    "series": [
      {"label": "T=0.7, k=40", "color": "purple", "values": [48, 66, 70, 71, 72, 72, 72, 72, 72]},
      {"label": "T=0.5, k=40", "color": "green",  "values": [46, 64, 68, 69, 70, 71, 71, 71, 71]},
      {"label": "T=0.3, k=40", "color": "red",    "values": [44, 60, 66, 67, 68, 68, 68, 68, 68]},
      {"label": "T=0.7, k=20", "color": "orange", "values": ["[unclear: ~50]", "[unclear: ~62]", "[unclear: ~66]", "[unclear: ~68]", "[unclear: ~69]", "[unclear: ~70]", "[unclear: ~70]", "[unclear: ~70]", "[unclear: ~70]"]},
      {"label": "T=0.7, no top k", "color": "grey", "values": ["[unclear]"]},
      {"label": "p=0.95", "color": "olive", "values": ["[unclear]"]},
      {"label": "p=0.9", "color": "brown", "values": ["[unclear]"]},
      {"label": "Greedy Decode", "color": "black", "values": [44, 48, 50, 51, 51, 51, 51, 51, 51]}
    ],
    "notes": "Some series values are visually estimated; see transcription_notes for uncertainties."
  },
  "right_plot": {
    "plot_type": "line_chart",
    "x_label": "Model size (#param in billions)",
    "x_values": [1,2,5,10,20,50,100,200],
    "y_label": "Accuracy (%)",
    "series": [
      {"label": "Greedy Decode", "color": "orange", "values": [2,3,4,5,8,10,12,15]},
      {"label": "Self Consistency", "color": "blue", "values": [3,4,6,8,12,15,18,25]}
    ],
    "notes": "Right-plot values are approximate estimates from the figure; exact numeric values not printed on figure."
  }
}
</transcription_json>

<transcription_notes>
- Left plot type: line chart showing accuracy on GSM8K vs number of sampled reasoning paths.
- Left plot legend entries (as shown in figure): T=0.7,k=40; T=0.5,k=40; T=0.3,k=40; T=0.7,k=20; T=0.7, no top k; p=0.95; p=0.9; Greedy Decode.
- Colors (visual): multiple (purple, green, red, orange, grey, olive, brown, black).
- Right plot: shows improvement of Self-Consistency over Greedy Decode across model sizes (LaMDA-137B series).
- Many numeric values in the plots are visually estimated; where uncertain values are present they are marked with \"[unclear: ...]\" in the JSON.
- Decorative elements (axes/grid styling) omitted.
</transcription_notes>
</transcription_image>

<!-- Column 2 -->
### Self-Consistency Improves Robustness to Imperfect Prompts
For few-shot learning with manually constructed prompts, human annotators sometimes make minor mistakes when creating the prompts. We further study if self-consistency can help improve a language model's robustness to imperfect prompts.9 We show the results in Table 8: while imperfect prompts decrease accuracy with greedy decoding (17.1 → 14.9), self-consistency can fill in the gaps and robustly improve the results.

Additionally, we found that the consistency (in terms of % of decodes agreeing with the final aggregated answer) is highly correlated with accuracy (Figure 5, over GSM8K). This suggests that one can use self-consistency to provide an uncertainty estimate of the model in its generated solutions. In other words, one can use low consistency as an indicator that the model has low confidence; i.e., self-consistency confers some ability for the model to "know when it doesn't know".

<transcription_table>
**Table 8: Self-consistency works under imperfect prompts, equation prompts and zero-shot chain-of-thought for GSM8K.**

| Prompt / Setting                                      | Accuracy (%) |
|------------------------------------------------------|-------------:|
| LaMDA-137B                                           |              |
| Prompt with correct chain-of-thought                 | 17.1         |
| Prompt with imperfect chain-of-thought               | 14.9         |
| + Self-consistency (40 paths)                        | 23.4         |
| Prompt with equations                                | 5.0          |
| + Self-consistency (40 paths)                        | 6.5          |
| PaLM-540B                                            |              |
| Zero-shot CoT (Kojima et al., 2022)                  | 43.0         |
| + Self-consistency (40 paths)                        | 69.2         |

<transcription_json>
{
  "table_type": "data_table",
  "title": "Table 8: Self-consistency works under imperfect prompts, equation prompts and zero-shot chain-of-thought for GSM8K.",
  "columns": ["Prompt / Setting", "Accuracy (%)"],
  "data": [
    {"Prompt / Setting": "LaMDA-137B", "Accuracy (%)": null},
    {"Prompt / Setting": "Prompt with correct chain-of-thought", "Accuracy (%)": 17.1},
    {"Prompt / Setting": "Prompt with imperfect chain-of-thought", "Accuracy (%)": 14.9},
    {"Prompt / Setting": "+ Self-consistency (40 paths)", "Accuracy (%)": 23.4},
    {"Prompt / Setting": "Prompt with equations", "Accuracy (%)": 5.0},
    {"Prompt / Setting": "+ Self-consistency (40 paths)", "Accuracy (%)": 6.5},
    {"Prompt / Setting": "PaLM-540B", "Accuracy (%)": null},
    {"Prompt / Setting": "Zero-shot CoT (Kojima et al., 2022)", "Accuracy (%)": 43.0},
    {"Prompt / Setting": "+ Self-consistency (40 paths)", "Accuracy (%)": 69.2}
  ],
  "unit": "percent",
  "notes": "Table rows and numeric values transcribed exactly as shown in the figure."
}
</transcription_json>

<transcription_notes>
- Table 8 is located in the lower-left region of the page. Numeric values are visually clear and transcribed verbatim.
- The table groups results by model (LaMDA-137B and PaLM-540B) and shows effect of imperfect prompts, equation prompts, and zero-shot CoT with and without self-consistency (40 sampled paths).
- Visual styling: single-column cells with light separators; no color coding present in the table itself.
</transcription_notes>
</transcription_table>

<!-- Column 2 continued -->
### Self-Consistency Works for Non-Natural-Language Reasoning Paths and Zero-shot CoT
We also tested the generality of the self-consistency concept to alternative forms of intermediate reasoning like equations (e.g., from "There are 3 cars in the parking lot already. 2 more arrive. Now there are 3 + 2 = 5 cars." to "3 + 2 = 5"). The results are shown in Table 8 ("Prompt with equations"): self-consistency still improves accuracy by generating intermediate equations; however, compared to generating natural language reasoning paths, the gain is smaller since the equations are much shorter and less opportunity remains for generating diversity in the decoding process. In addition, we tested self-consistency with zero-shot chain-of-thought (Kojima et al., 2022) and show that self-consistency works for zero-shot CoT as well and improves the results significantly (+26.2%) in Table 8.

<transcription_image>
**Figure 5: The consistency is correlated with model's accuracy.**

```ascii
[SCATTER - Accuracy (%) vs Consistency (%)]
X-axis: Consistency (%) 0 .. 100
Y-axis: Accuracy (%) 0 .. 100

Many scatter points trending upward (positive correlation).
Representative visual cluster:
Consistency: 0-20%  -> Accuracy: 0-20%
Consistency: 20-40% -> Accuracy: 20-50%
Consistency: 40-60% -> Accuracy: 50-70%
Consistency: 60-80% -> Accuracy: 70-85%
Consistency: 80-100%-> Accuracy: 85-100%

Trend: roughly monotonic increase; higher consistency aligns with higher accuracy.
```

<transcription_json>
{
  "chart_type": "scatter_plot",
  "title": "Figure 5: Consistency vs Accuracy (GSM8K)",
  "x_label": "Consistency (%)",
  "y_label": "Accuracy (%)",
  "points": [
    {"consistency": "[unclear: several points in 0-20]", "accuracy": "[unclear: 0-20]"},
    {"consistency": "[unclear: several points in 20-40]", "accuracy": "[unclear: 20-50]"},
    {"consistency": "[unclear: several points in 40-60]", "accuracy": "[unclear: 50-70]"},
    {"consistency": "[unclear: several points in 60-80]", "accuracy": "[unclear: 70-85]"},
    {"consistency": "[unclear: several points in 80-100]", "accuracy": "[unclear: 85-100]"}
  ],
  "notes": "Exact (x,y) values are not printed on the figure; the JSON encodes approximate clusters and the clear positive correlation. Individual point coordinates are visually estimated and marked with [unclear]."
}
</transcription_json>

<transcription_notes>
- Scatter plot shows a clear positive correlation between the % of decodes agreeing with the final aggregated answer ("Consistency") and model Accuracy on GSM8K.
- Exact numerical coordinates of the individual points are not printed on the figure; only the visual trend/clusters are shown. Values in the JSON are therefore approximate and marked with [unclear] where precise numbers cannot be read.
</transcription_notes>
</transcription_image>

---

9 We use the same prompts as before, but swap all the numbers in the reasoning paths with random numbers except the final answer, e.g., from "There are 3 cars in the parking lot already. 2 more arrive. Now there are 3 + 2 = 5 cars." to "There are 7 cars in the parking lot already. 6 more arrive. Now there are 7 + 6 = 5 cars.".

<transcription_page_footer> Page 8 </transcription_page_footer>

---

<transcription_page_header> Published as a conference paper at ICLR 2023 </transcription_page_header>

<!-- Section 1 -->
## 4 RELATED WORK

### Reasoning in language models.
Language models are known to struggle in Type 2 tasks, such as arithmetic, logical and commonsense reasoning (Evans, 2010). Previous work has primarily focused on specialized approaches for improving reasoning (Andor et al., 2019; Ran et al., 2019; Geva et al., 2020; Piekos et al., 2021). Compared to prior work, self-consistency is applicable to a wide range of reasoning tasks without any additional supervision or fine-tuning, while still substantially improving the performance of the chain-of-thought prompting approach proposed in Wei et al. (2022).

### Sampling and re-ranking in language models.
Multiple decoding strategies for language models have been proposed in the literature, e.g., temperature sampling (Ackley et al., 1985; Fiedler & Goldberg, 2017), top-k sampling (Fan et al., 2018; Holtzman et al., 2018; Radford et al., 2019), nucleus sampling (Holtzman et al., 2020), minimum Bayes risk decoding (Eikema & Aziz, 2020; Shi et al., 2022), and typical decoding (Meister et al., 2022). Other work has sought to explicitly promote diversity in the decoding process (Batra et al., 2012; Li et al., 2016; Vijayakumar et al., 2018).

Re-ranking is another common approach to improve generation quality in language models (Adiwardana et al., 2020; Shen et al., 2021). Thoppilan et al. (2022) collect additional human annotations to train a re-ranker for response filtering. Cobbe et al. (2021) train a "verifier" to re-rank generated solutions, which substantially improves the solve rate on math tasks compared to just fine-tuning the language model. Elazar et al. (2021) improve the consistency of factual knowledge extraction by extending pre-training with an additional consistency loss. All these methods require either training an additional re-ranker or collecting additional human annotation, while self-consistency requires no additional training, fine-tuning, nor extra data collection.

### Extract reasoning paths.
Some previous work has considered task-specific approaches for identifying reasoning paths, such as constructing semantic graphs (Xu et al., 2021a), learning an RNN to retrieve reasoning paths over the Wikipedia graph (Asai et al., 2020), fine-tuning with human annotated reasoning paths on math problems (Cobbe et al., 2021), or training an extractor with heuristic-based pseudo reasoning paths (Chen et al., 2019). More recently, the importance of diversity in the reasoning processes has been noticed, but only leveraged via task-specific training, either through an additional QA model over extracted reasoning paths (Chen et al., 2019), or by the introduction of latent variables in a commonsense knowledge graph (Yu et al., 2022). Compared to these approaches, self-consistency is far simpler and requires no additional training. The approach we propose simply couples the generation of reasoning paths and a final answer by sampling from the decoder, using aggregation to recover the most consistent answer without additional modules.

### Consistency in language models.
Some prior work has shown that language models can suffer from inconsistency in conversation (Adiwardana et al., 2020), explanation generation (Camburu et al., 2020), and factual knowledge extraction (Elazar et al., 2021). Welleck et al. (2020) use "consistency" to refer to generating an infinite-length sequence in recurrent language models. Nye et al. (2021) improve the logical consistency of samples from a System 1 model by adding a System 2-inspired logical reasoning module. In this paper we focus on a slightly different notion of "consistency", i.e., utilizing answer consistency among diverse reasoning paths to improve accuracy.

<!-- Section 2 -->
## 5 CONCLUSION AND DISCUSSION

We introduced a simple yet effective method called self-consistency, and observed that it significantly improves accuracy in a range of arithmetic and commonsense reasoning tasks, across four large language models with varying scales. Beyond accuracy gains, self-consistency is also useful for collecting rationales when performing reasoning tasks with language models, and for providing uncertainty estimates and improved calibration of language model outputs.

One limitation of self-consistency is that it incurs more computation cost. In practice people can try a small number of paths (e.g., 5 or 10) as a starting point to realize most of the gains while not incurring too much cost, as in most cases the performance saturates quickly (Figure 2). As part of future work, one could use self-consistency to generate better supervised data to fine-tune the model, such that the model can give more accurate predictions in a single inference run after fine-tuning. In addition, we observed that language models can sometimes generate incorrect or nonsensical reasoning paths (e.g., the StrategyQA example in Table 4, the two population numbers are not exactly correct), and further work is needed to better ground models' rationale generations.

<transcription_page_footer> Page 9 </transcription_page_footer>

---

<transcription_page_header> Published as a conference paper at ICLR 2023 </transcription_page_header>

<!-- Section 1 -->
## REPRODUCIBILITY STATEMENT

In experiments, we included four different language models with varying scales. Two of them are public models: UL2 is a completely open-sourced model with model checkpoints available at https://github.com/google-research/google-research/tree/master/ul2; GPT-3 is also a public model with public API available at https://openai.com/api/. For GPT-3, we have included two public engines ("code-davinci-001" and "code-davinci-002") to further aid reproducibility, as Codex is currently free so anyone can reproduce the results. In addition, as our results make use of LaMDA-137B and PaLM-540B that are not publicly available, we provide the exact input prompts for all tasks in Appendix A.3 (and note that we do not perform any finetuning and only apply prompting to off-the-shelf language models).

<!-- Section 2 -->
## ETHICS STATEMENT

As we stated in the discussion, language models can sometimes generate nonsensical or non-factual reasoning paths, so one should use language models' outputs with extra caution. We deal with reasoning tasks mostly and the generated rationales are only used for inspecting how a model reaches its answer. One could potentially use the generated rationales to further check why the model makes certain mistakes or whether the model contains any biases when performing a certain task. For language model in real-world use, further work is needed to better ground models' predictions and improve model's factuality and safety, to ensure the models do not cause harms to users.

<!-- Section 3 -->
## REFERENCES

David H. Ackley, Geoffrey E. Hinton, and Terrence J. Sejnowski. A learning algorithm for boltzmann machines. Cognitive Science, 9(1):147–169, 1985. ISSN 0364-0213. URL https://www.sciencedirect.com/science/article/pii/S0364021385800124.

Daniel Adiwardana, Minh-Thang Luong, David R. So, Jamie Hall, Noah Fiedel, Romal Thoppilan, Zi Yang, Apoorv Kulshreshtha, Gaurav Nemade, Yifeng Lu, and Quoc V. Le. Towards a human-like open-domain chatbot, 2020.

Aida Amini, Saadia Gabriel, Shanchuan Lin, Rik Koncel-Kedziorski, Yejin Choi, and Hannaneh Hajishirzi. MathQA: Towards interpretable math word problem solving with operation-based formalisms. In Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long and Short Papers), pp. 2357–2367. Association for Computational Linguistics, June 2019. URL https://aclanthology.org/N19-1245.

Daniel Andor, Luheng He, Kenton Lee, and Emily Pitler. Giving BERT a calculator: Finding operations and arguments with reading comprehension. In Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP), 2019. URL https://aclanthology.org/D19-1609.

Akari Asai, Kazuma Hashimoto, Hannaneh Hajishirzi, Richard Socher, and Caiming Xiong. Learning to retrieve reasoning paths over wikipedia graph for question answering. In International Conference on Learning Representations, 2020. URL https://openreview.net/forum?id=SJgVKh-rYDH.

Roy Bar-Haim, Ido Dagan, Bill Dolan, Lisa Ferro, Danilo Giampiccolo, Bernardo Magnini, and Idan Szpektor. The second pascal recognising textual entailment challenge. In Proceedings of the second PASCAL challenges workshop on recognising textual entailment, 2006.

Dhruv Batra, Payman Yadollahpour, Abner Guzman-Rivera, and Gregory Shakhnarovich. Diverse m-best solutions in markov random fields. In Proceedings of the 12th European Conference on Computer Vision - Volume Part V, ECCV'12, pp. 1–16, Berlin, Heidelberg, 2012. Springer-Verlag. ISBN 9783642337147. URL https://doi.org/10.1007/978-3-642-33715-4_1.

<transcription_page_footer> Page 10 </transcription_page_footer>

<!-- Decorative: horizontal rule under header -->

---

<transcription_page_header>Published as a conference paper at ICLR 2023</transcription_page_header>

<!-- Decorative: horizontal rule under header -->

<!-- Section 1 -->

Luisa Bentivogli, Peter Clark, Ido Dagan, and Danilo Giampiccolo. The fifth pascal recognizing textual entailment challenge. In TAC, 2009.

BIG-bench collaboration. Beyond the imitation game: Measuring and extrapolating the capabilities of language models. In preparation, 2021. URL https://github.com/google/BIG-bench/.

Tom Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared D Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, Sandhini Agarwal, Ariel Herbert-Voss, Gretchen Krueger, Tom Henighan, Rewon Child, Aditya Ramesh, Daniel Ziegler, Jeffrey Wu, Clemens Winter, Chris Hesse, Mark Chen, Eric Sigler, Mateusz Litwin, Scott Gray, Benjamin Chess, Jack Clark, Christopher Berner, Sam McCandlish, Alec Radford, Ilya Sutskever, and Dario Amodei. Language models are few-shot learners. In Advances in Neural Information Processing Systems, 2020. URL https://proceedings.neurips.cc/paper/2020/file/1457c0d6bfcb4967418bf8ac142f64a-Paper.pdf.

Oana-Maria Camburu, Tim Rocktäschel, Thomas Lukasiewicz, and Phil Blunsom. e-snli: Natural language inference with natural language explanations. In S. Bengio, H. Wallach, H. Larochelle, K. Grauman, N. Cesa-Bianchi, and R. Garnett (eds.), Advances in Neural Information Processing Systems 31, pp. 9539–9549, Curran Associates, Inc., 2018. URL http://papers.nips.cc/paper/8163-e-snli-natural-language-inference-with-natural-language-explanations.pdf.

Oana-Maria Camburu, Brendan Shillingford, Pasquale Minervini, Thomas Lukasiewicz, and Phil Blunsom. Make up your mind! adversarial generation of inconsistent natural language explanations. In Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics, pp. 4157–4165, Online, July 2020. Association for Computational Linguistics. doi: 10.18653/v1/2020.acl-main.382. URL https://aclanthology.org/2020.acl-main.382.

Jifan Chen, Shih-Ting Lin, and Greg Durrett. Multi-hop question answering via reasoning chains. CoRR, abs/1910.02610, 2019. URL http://arxiv.org/abs/1910.02610.

Mark Chen, Jerry Tworek, Heewoo Jun, Qiming Yuan, Henrique Ponde de Oliveira Pinto, Jared Kaplan, Harri Edwards, Yuri Burda, Nicholas Joseph, Greg Brockman, et al. Evaluating large language models trained on code. arXiv preprint arXiv:2107.03374, 2021.

Aakanksha Chowdhery, Sharan Narang, Jacob Devlin, Maarten Bosma, Gaurav Mishra, Adam Roberts, Paul Barham, Hyung Won Chung, Charles Sutton, Sebastian Gehrmann, Parker Schul [unclear], Kensen Shi [unclear], Sasha Tyvashchenko [unclear], Joshua Maynez, Abhishek Rao, Parker Barnes, Yi Tay, Noam Shazeer, Vinodkumar Prabhakaran, Emily Reif, Nan Du, Ben Hutchinson, Reiner Pope, James Bradbury, Jacob Austin, Michael Isard, Guy Gur-Ari, Pengcheng Yin, Toju Duke [unclear], Anselm Levskaya, Sanjay Ghemawat, Sunipa Dev, Henryk Michalewski, Xavier Garcia, Vedant Misra, Kevin Robinson, Liam Fedus, Denny Zhou, Daphne Ippolito, David Luan, Hyeontaek Lim, Barret Zoph, Alexander Spiridonov, Ryan Sepassi, David Dohan, Shivani Agrawal, Mark Omernick, Andrew M. Dai, Thanumalayan Sankaranarayana Pillai, Marie Pellat, Aitor Lewkowycz, Erica Moreira, Rewon Child, Oleksandr Polozov, Katherine Lee, Zongwei Zhou, Xuezhi Wang, Brennan Saeta, Mark Diaz, Orhan Firat, Michele Catasta, Jason Wei, Kathy Meier-Hellstern, Douglas Eck, Jeff Dean, Slav Petrov, and Noah Fiedel. Palm: Scaling language modeling with pathways, 2022. URL https://arxiv.org/abs/2204.02311.

Christopher Clark, Kenton Lee, Ming-Wei Chang, Tom Kwiatkowski, Michael Collins, and Kristina Toutanova. BoolQ: Exploring the surprising difficulty of natural yes/no questions. In NAACL, 2019.

Peter Clark, Isaac Cowhey, Oren Etzioni, Tushar Khot, Ashish Sabharwal, Carissa Schoenick, and Oyvind Tafjord. Think you have solved question answering? try arc, the ai2 reasoning challenge. ArXiv, abs/1803.05457, 2018.

Karl Cobbe, Vineet Kosaraju, Mohammad Bavarian, Mark Chen, Heewoo Jun, Lukasz Kaiser, Matthias Plappert, Jerry Tworek, Jacob Hilton, Reiichiro Nakano [unclear], Christopher Hesse, and John Schulman. Training verifiers to solve math word problems, 2021.

<transcription_page_footer>Page 11</transcription_page_footer>

---

<transcription_page_header>Published as a conference paper at ICLR 2023</transcription_page_header>

<!-- Section 1 -->

Ido Dagan, Oren Glickman, and Bernardo Magnini. The pascal recognising textual entailment challenge. In Machine Learning Challenges Workshop, pp. 177–190. Springer, 2005.

Bryan Eikema and Wilker Aziz. Is MAP decoding all you need? the inadequacy of the mode in neural machine translation. In Proceedings of the 28th International Conference on Computational Linguistics, pp. 4506–4520, Barcelona, Spain (Online), December 2020. International Committee on Computational Linguistics. URL https://aclanthology.org/2020.coling-main.398.

Yanai Elazar, Nora Kassner, Shauli Ravfogel, Abhilasha Ravichander, Eduard Hovy, Hinrich Schütze, and Yoav Goldberg. Measuring and improving consistency in pretrained language models. Transactions of the Association for Computational Linguistics, 9:1012–1031, 2021. doi: 10.1162/tacl_a_00410. URL https://aclanthology.org/2021.tacl-1.60.

Jonathan St BT Evans. Intuition and reasoning: A dual-process perspective. Psychological Inquiry, 21(4):313–326, 2010.

Angela Fan, Mike Lewis, and Yann Dauphin. Hierarchical neural story generation. In Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pp. 889–898, Melbourne, Australia, July 2018. Association for Computational Linguistics. doi: 10.18653/v1/P18-1082. URL https://aclanthology.org/P18-1082.

Jessica Ficler and Yoav Goldberg. Controlling linguistic style aspects in neural language generation. In Proceedings of the Workshop on Stylistic Variation, pp. 94–104, Copenhagen, Denmark, September 2017. Association for Computational Linguistics. doi: 10.18653/v1/W17-4912. URL https://aclanthology.org/W17-4912.

Tianyu Gao, Adam Fisch, and Danqi Chen. Making pre-trained language models better few-shot learners. In Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics and the 11th International Joint Conference on Natural Language Processing (Volume 1: Long Papers), pp. 3816–3830, Online, August 2021. Association for Computational Linguistics. doi: 10.18653/v1/2021.acl-long.295. URL https://aclanthology.org/2021.acl-long.295.

Mor Geva, Ankit Gupta, and Jonathan Berant. Injecting numerical reasoning skills into language models. In Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics, 2020. doi: 10.18653/v1/2020.acl-main.89. URL https://aclanthology.org/2020.acl-main.89.

Mor Geva, Daniel Khashabi, Elad Segal, Tushar Khot, Dan Roth, and Jonathan Berant. Did aristotle use a laptop? A question answering benchmark with implicit reasoning strategies. Transactions of the Association for Computational Linguistics, 2021. URL https://aclanthology.org/2021.tacl-1.21.

Danilo Giampiccolo, Bernardo Magnini, Ido Dagan, and Bill Dolan. The third pascal recognizing textual entailment challenge. In Proceedings of the ACL-PASCAL workshop on textual entailment and paraphrasing, pp. 1–9. Association for Computational Linguistics, 2007.

Ari Holtzman, Jan Buys, Maxwell Forbes, Antoine Bosselut, David Golub, and Yejin Choi. Learning to write with cooperative discriminators. In Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pp. 1638–1649, Melbourne, Australia, July 2018. Association for Computational Linguistics. doi: 10.18653/v1/P18-1152. URL https://aclanthology.org/P18-1152.

Ari Holtzman, Jan Buys, Li Du, Maxwell Forbes, and Yejin Choi. The curious case of neural text degeneration. In International Conference on Learning Representations, 2020. URL https://openreview.net/forum?id=rygGQyrFvH.

Mohammad Javad Hosseini, Hannaneh Hajishirzi, Oren Etzioni, and Nate Kushman. Learning to solve arithmetic word problems with verb categorization. In Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2014. doi: 10.3115/v1/D14-1058. URL https://aclanthology.org/D14-1058.

<transcription_page_footer>12</transcription_page_footer>

---

<transcription_page_header> Published as a conference paper at ICLR 2023 </transcription_page_header>

<!-- Section 1 -->

Daniel Khashabi, Sewon Min, Tushar Khot, Ashish Sabharwal, Oyvind Tafjord, Peter Clark, and Hannaneh Hajishirzi. UNIFIEDQA: Crossing format boundaries with a single QA system. In Findings of the Association for Computational Linguistics: EMNLP 2020, pp. 1896–1907, Online, November 2020. Association for Computational Linguistics. doi: 10.18653/v1/2020.findings-emnlp.171. URL https://aclanthology.org/2020.findings-emnlp.171.

Takeshi Kojima, Shixiang Shane Gu, Machel Reid, Yutaka Matsuo, and Yusuke Iwasawa. Large language models are zero-shot reasoners. In Alice H. Oh, Alekh Agarwal, Danielle Belgrave, and Kyunghyun Cho (eds.), Advances in Neural Information Processing Systems, 2022. URL https://openreview.net/forum?id=e2TBb5yOyFf.

Rik Koncel-Kedziorski, Subhro Roy, Aida Amini, Nate Kushman, and Hannaneh Hajishirzi. MAWPS: A math word problem repository. In Proceedings of the 2016 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, 2016. doi: 10.18653/v1/N16-1136. URL https://aclanthology.org/N16-1136.

Yihuai Lan, Lei Wang, Qiyuan Zhang, Yunshi Lan, Bing Tian Dai, Yan Wang, Dongxiang Zhang, and Ee-Peng Lim. MWPToolkit: An open-source framework for deep learning-based math word problem solvers. arXiv preprint arXiv:2109.00799, 2021. URL https://arxiv.org/abs/2109.00799.

Jiwei Li and Dan Jurafsky. Mutual information and diverse decoding improve neural machine translation, 2016. URL https://arxiv.org/abs/1601.00372.

Jiwei Li, Will Monroe, and Dan Jurafsky. A simple, fast diverse decoding algorithm for neural generation. CoRR, abs/1611.08562, 2016. URL http://arxiv.org/abs/1611.08562.

Wang Ling, Dani Yogatama, Chris Dyer, and Phil Blunsom. Program induction by rationale generation: Learning to solve and explain algebraic word problems. In Proceedings of the 55th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), 2017. doi: 10.18653/v1/P17-1015. URL [unclear].

Yao Lu, Max Bartolo, Alastair Moore, Sebastian Riedel, and Pontus Stenetorp. Fantastically ordered prompts and where to find them: Overcoming few-shot prompt order sensitivity. ArXiv, abs/2104.08786, 2021.

Clara Meister, Tiago Pimentel, Gian Wiher [unclear], and Ryan Cotterell. Typical decoding for natural language generation. arXiv preprint arXiv:2202.00666, 2022.

Shen Yun Miao, Chao Chun Liang, and Keh Yih Su. A diverse corpus for evaluating and developing English math word problem solvers. In Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics, 2020. URL https://aclanthology.org/2020.acl-main.92.

Yixin Nie, Adina Williams, Emily Dinan, Mohit Bansal, Jason Weston, and Douwe Kiela. Adversarial NLI: A new benchmark for natural language understanding. In Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics, 2020.

Maxwell Nye, Michael Henry Tessler, Joshua B. Tenenbaum, and Brenden M. Lake. Improving coherence and consistency in neural sequence models with dual-system, neuro-symbolic reasoning. In A. Beygelzimer, Y. Dauphin, P. Liang, and J. Wortman Vaughan (eds.), Advances in Neural Information Processing Systems, 2021. URL [unclear].

Arkil Patel, Satwik Bhattamishra, and Navin Goyal. Are NLP models really able to solve simple math word problems? In Proceedings of the 2021 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, pp. 2080–2094, Online, June 2021. Association for Computational Linguistics. doi: 10.18653/v1/2021.naacl-main.168. URL https://aclanthology.org/2021.naacl-main.168.

Xinyu Pi, Qian Liu, Bei Chen, Morteza Ziyadi, Zeqi Lin, Yan Gao, Qiang Fu, Jian-Guang Lou, and Weizhu Chen. Reasoning like program executors, 2022.

<transcription_page_footer> Page 13 </transcription_page_footer>

---

<transcription_page_header> Published as a conference paper at ICLR 2023 </transcription_page_header>

<!-- Section 1 -->
Piotr Piękos, Mateusz Malinowski, and Henryk Michalewski. Measuring and improving BERT’s mathematical abilities by predicting the order of reasoning. In Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics and the 11th International Joint Conference on Natural Language Processing (Volume 2: Short Papers), 2021. doi: 10.18653/v1/2021.acl-short.49. URL https://aclanthology.org/2021.acl-short.49.

Alec Radford, Jeff Wu, Rewon Child, David Luan, Dario Amodei, and Ilya Sutskever. Language models are unsupervised multitask learners. 2019.

Jack W Rae, Sebastian Borgeaud, Trevor Cai, Katie Millican, Jordan Hoffmann, Francis Song, John Aslanides, Sarah Henderson, Roman Ring, Susannah Young, et al. Scaling language models: Methods, analysis & insights from training gopher. arXiv preprint arXiv:2112.11446, 2021.

Qiu Ran, Yankai Lin, Peng Li, Jie Zhou, and Zhiyuan Liu. NumNet: Machine reading comprehension with numerical reasoning. In Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP), 2019. doi: 10.18653/v1/D19-1251. URL https://aclanthology.org/D19-1251.

Subhro Roy and Dan Roth. Solving general arithmetic word problems. In Proceedings of the 2015 Conference on Empirical Methods in Natural Language Processing, 2015. doi: 10.18653/v1/D15-1202. URL https://aclanthology.org/D15-1202.

Jianhao Shen, Yichun Yin, Lin Li, Lifeng Shang, Xin Jiang, Ming Zhang, and Qun Liu. Generate & rank: A multi-task framework for math word problems. In Findings of the Association for Computational Linguistics: EMNLP 2021, pp. 2269–2279, Punta Cana, Dominican Republic, November 2021. Association for Computational Linguistics. URL https://aclanthology.org/2021.findings-emnlp.195.

Freda Shi, Daniel Fried, Marjan Ghazvininejad, Luke Zettlemoyer, and Sida I. Wang. Natural language to code translation with execution. In Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing, pp. 3533–3546, Abu Dhabi, United Arab Emirates, December 2022. Association for Computational Linguistics. URL https://aclanthology.org/2022.emnlp-main.231.

Keith E Stanovich and Richard F West. Individual differences in reasoning: Implications for the rationality debate? Behavioral and brain sciences, 23(5):645–665, 2000. URL https://pubmed.ncbi.nlm.nih.gov/11301544/.

Alon Talmor, Jonathan Herzig, Nicholas Lourie, and Jonathan Berant. CommonsenseQA: A question answering challenge targeting commonsense knowledge. In Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long and Short Papers), 2019. URL https://aclanthology.org/N19-1421.

Yi Tay, Mostafa Dehghani, Vinh Q. Tran, Xavier Garcia, Jason Wei, Xuezhi Wang, Hyung Won Chung, Dara Bahri, Tal Schuster, Steven Zheng, Denny Zhou, Neil Houlsby, and Donald Metzler. Unifying language learning paradigms, 2022. URL https://arxiv.org/abs/2205.05131.

Romal Thoppilan, Daniel De Freitas, Jamie Hall, Noam Shazeer, Apoorv Kulshreshtha, Heng-Tze Cheng, Alicia Jin, Taylor Bos, Leslie Baker, Yu Du, et al. Lamda: Language models for dialog applications. arXiv preprint arXiv:2201.08239, 2022. URL https://arxiv.org/abs/2201.08239.

Ashwin Vijayakumar, Michael Cogswell, Ramprasaath Selvaraju, Qing Sun, Stefan Lee, David Crandall, and Dhruv Batra. Diverse beam search for improved description of complex scenes. Proceedings of the AAAI Conference on Artificial Intelligence, 32, Apr. 2018. URL https://ojs.aaai.org/index.php/AAAI/article/view/12340.

Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Maarten Bosma appears twice in image? [unclear], Brian Ichter, Fei Xia, Ed Chi, Quoc Le, and Denny Zhou. Chain of thought prompting elicits reasoning in large language models. Conference on Neural Information Processing Systems (NeurIPS), 2022. URL https://arxiv.org/pdf/2201.11903.

<!-- Decorative: none visible besides page number -->

<transcription_notes>
- Layout: single-column references page, serif font, fully justified paragraphs.
- Top header: centered small text "Published as a conference paper at ICLR 2023".
- Footer: centered page number "14".
- No figures or tables on this page.
- Minor uncertainties flagged inline:
  - Author name "Piękos" as transcribed; diacritic visible but verify original spelling if needed.
  - Final reference line shows a possible duplication "Maarten Bosma" in the author list in the scanned image; marked with [unclear].
</transcription_notes>

<transcription_page_footer> Page 14 </transcription_page_footer>

---

<transcription_page_header> Published as a conference paper at ICLR 2023 </transcription_page_header>

<!-- Section 1 -->

Sean Welleck, Ilia Kulikov, Jaedeok Kim, Richard Yuanzhe Pang, and Kyunghyun Cho. Consistency of a recurrent language model with respect to incomplete decoding. In Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP), pp. 5553–5568, Online, November 2020. Association for Computational Linguistics. doi: 10.18653/v1/2020. emnlp-main.448. URL https://aclanthology.org/2020.emnlp-main.448.

Weiwen Xu, Yang Deng, Huihui Zhang, Deng Cai, and Wai Lam. Exploiting reasoning chains for multi-hop science question answering. In Findings of the Association for Computational Linguistics: EMNLP 2021, pp. 1143–1156, Punta Cana, Dominican Republic, November 2021a. Association for Computational Linguistics. URL https://aclanthology.org/2021.findings-emnlp.99.

Yichong Xu, Chenguang Zhu, Shuohang Wang, Siqi Sun, Hao Cheng, Xiaodong Liu, Jianfeng Gao, Pengcheng He, Michael Zeng, and Xuedong Huang. Human parity on commonsenseqa: Augmenting self-attention with external attention, 2021b. URL https://arxiv.org/abs/2112.03254.

Zhilin Yang, Peng Qi, Saizheng Zhang, Yoshua Bengio, William Cohen, Ruslan Salakhutdinov, and Christopher D. Manning. HotpotQA: A dataset for diverse, explainable multi-hop question answering. In Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing, pp. 2369–2380, Brussels, Belgium, October-November 2018. Association for Computational Linguistics. doi: 10.18653/v1/D18-1259. URL https://aclanthology.org/D18-1259.

Xi Ye and Greg Durrett. The unreliability of explanations in few-shot prompting for textual reasoning. In Alice H. Oh, Alekh Agarwal, Danielle Belgrave, and Kyunghyun Cho (eds.), Advances in Neural Information Processing Systems, 2022. URL https://openreview.net/forum?id=Bct2f8Fd8S.

Wenhao Yu, Chenguang Zhu, Lianhui Qin, Zhihan Zhang, Tong Zhao, and Meng Jiang. Diversifying content generation for commonsense reasoning with mixture of knowledge graph experts. In Findings of Annual Meeting of the Association for Computational Linguistics (ACL), 2022.

Zihao Zhao, Eric Wallace, Shi Feng, Dan Klein, and Sameer Singh. Calibrate before use: Improving few-shot performance of language models. In Marina Meila and Tong Zhang (eds.), Proceedings of the 38th International Conference on Machine Learning, volume 139 of Proceedings of Machine Learning Research. PMLR, 2021. URL https://proceedings.mlr.press/v139/zhao21c.html.

<transcription_page_footer> 15 </transcription_page_footer>

---

<transcription_page_header> Published as a conference paper at ICLR 2023 </transcription_page_header>

# A  APPENDIX

<!-- Section 1 -->
## A.1  ADDITIONAL EXPERIMENT RESULTS

### A.1.1  ROBUSTNESS TO SAMPLING STRATEGIES AND PARAMETERS

In Figure 6 we ablate the results with respect to different sampling strategies and parameters by varying T in temperature sampling and k in Top-k sampling, on LaMDA-137B. We show that self-consistency is robust to various sampling strategies and parameters.

<transcription_image>
**Figure 6: GSM8K accuracy over LaMDA-137B**

```ascii
[LINE CHART - GSM8K accuracy over LaMDA-137B]
y-axis: Accuracy (%) from ~18 to ~28
x-axis: #Sampled Reasoning Paths : 4 8 12 16 20 24 28 32 36 40

Legend:
- T=0.7, k=40        : ──●── (blue)
- T=0.5, k=40        : ──■── (orange)
- T=0.3, k=40        : ──▲── (green)
- T=0.5, k=20        : ──◆── (red)
- T=0.5, no top k    : ──✳── (purple)
- Greedy Decode      : ──○── (brown)

ASCII trend (approximate visual trends; exact point values are unclear):
4:   Greedy Decode ~18, T=0.3 ~19, others ~20
8:   Greedy ~20, others rising 21-24
12:  Greedy ~21, others 23-26
16:  Greedy ~22, others 24-27
20-40: Greedy flattens ~22-24, self-consistency variants rise up to ~27-28
```

<transcription_json>
{"chart_type": "line_chart", "title": "GSM8K accuracy over LaMDA-137B", "x_ticks": [4,8,12,16,20,24,28,32,36,40], "y_range_percent": {"min":"~18","max":"~28"}, "series":[{"name":"T=0.7, k=40","color":"blue","values":["[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]"]},{"name":"T=0.5, k=40","color":"orange","values":["[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]"]},{"name":"T=0.3, k=40","color":"green","values":["[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]"]},{"name":"T=0.5, k=20","color":"red","values":["[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]"]},{"name":"T=0.5, no top k","color":"purple","values":["[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]"]},{"name":"Greedy Decode","color":"brown","values":["[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]","[unclear]"]}], "unit":"percent", "notes":"Exact numeric point values on each series are not legible in the image; trends approximated in ASCII."
}
</transcription_json>

<transcription_notes>
- Type: Single line chart (multiple series)
- X-axis: #Sampled Reasoning Paths with ticks at 4, 8, 12, 16, 20, 24, 28, 32, 36, 40
- Y-axis: Accuracy (%) roughly from 18% to 28%
- Legend (left-to-right in plot): T=0.7, k=40 (blue); T=0.5, k=40 (orange); T=0.3, k=40 (green); T=0.5, k=20 (red); T=0.5, no top k (purple); Greedy Decode (brown)
- Visual: self-consistency variants increase accuracy with more sampled paths, greedy decode remains substantially lower and flattens earlier
- Exact numeric values for each plotted point are not readable in the image and are marked as [unclear] in JSON.
</transcription_notes>
</transcription_image>

Figure 6: GSM8K accuracy over LaMDA-137B. Self-consistency works under various sampling strategies and sampling parameters.

In Figure 7 and Figure 8, we show the results of self-consistency compared with greedy decoding a single path over LaMDA-137B and PaLM-540B, respectively. Self-consistency improves over greedy decode by a quite significant margin on both models, on top of high accuracy already achieved by scaling up model sizes.

<transcription_image>
**Figure 7: Self-consistency (blue) significantly improves accuracy across various arithmetic and commonsense reasoning tasks, over LaMDA-137B.**

```ascii
[SMALL-MULTIPLES - 2 rows x 4 columns of mini line charts: Accuracy (%) vs #Sampled Reasoning Paths]
Row 1 titles: MultiArith | ASDiv | SVAMP | GSM8K
Row 2 titles: Commonsense QA | Strategy QA | ARC (Easy) | ARC (Challenge)

Each small chart legend:
- Greedy Decode (Single-path) : ──○── (orange)
- Self Consistency (Multi-path): ──●── (blue)

Axes: x ticks: 0 5 10 15 20 25 30 35 40 (varies slightly by plot)
y-axis ranges differ per plot (e.g., MultiArith ~55-75, ASDiv ~44-58, SVAMP ~42-54, GSM8K ~16-28, Commonsense QA ~54-64, Strategy QA ~62-68, ARC (Easy) ~68-78, ARC (Challenge) ~48-60)

Approximate trends:
- In all plots blue (self-consistency) rises with number of sampled paths and stays above orange (greedy)
- Orange (greedy) is flat / slightly increasing but much lower
```

<transcription_json>
{"chart_type":"small_multiple_line_charts","title":"Self-consistency vs Greedy Decode across tasks (LaMDA-137B)","layout":{"rows":2,"cols":4},"charts":[{"title":"MultiArith","x_ticks":[0,5,10,15,20,25,30,35,40],"y_range_percent":[55,75],"series":[{"name":"Greedy Decode (Single-path)","color":"orange","values":["[unclear]"]},{"name":"Self Consistency (Multi-path)","color":"blue","values":["[unclear]"]}]},{"title":"ASDiv","x_ticks":[0,5,10,15,20,25,30,35,40],"y_range_percent":[44,58],"series":[{"name":"Greedy Decode (Single-path)","color":"orange","values":["[unclear]"]},{"name":"Self Consistency (Multi-path)","color":"blue","values":["[unclear]"]}]},{"title":"SVAMP","x_ticks":[0,5,10,15,20,25,30,35,40],"y_range_percent":[42,54],"series":[{"name":"Greedy Decode (Single-path)","color":"orange","values":["[unclear]"]},{"name":"Self Consistency (Multi-path)","color":"blue","values":["[unclear]"]}]},{"title":"GSM8K","x_ticks":[0,5,10,15,20,25,30,35,40],"y_range_percent":[16,28],"series":[{"name":"Greedy Decode (Single-path)","color":"orange","values":["[unclear]"]},{"name":"Self Consistency (Multi-path)","color":"blue","values":["[unclear]"]}]},{"title":"Commonsense QA","x_ticks":[0,5,10,15,20,25,30,35,40],"y_range_percent":[54,64],"series":[{"name":"Greedy Decode (Single-path)","color":"orange","values":["[unclear]"]},{"name":"Self Consistency (Multi-path)","color":"blue","values":["[unclear]"]}]},{"title":"Strategy QA","x_ticks":[0,5,10,15,20,25,30,35,40],"y_range_percent":[62,68],"series":[{"name":"Greedy Decode (Single-path)","color":"orange","values":["[unclear]"]},{"name":"Self Consistency (Multi-path)","color":"blue","values":["[unclear]"]}]},{"title":"ARC (Easy)","x_ticks":[0,5,10,15,20,25,30,35,40],"y_range_percent":[68,78],"series":[{"name":"Greedy Decode (Single-path)","color":"orange","values":["[unclear]"]},{"name":"Self Consistency (Multi-path)","color":"blue","values":["[unclear]"]}]},{"title":"ARC (Challenge)","x_ticks":[0,5,10,15,20,25,30,35,40],"y_range_percent":[48,60],"series":[{"name":"Greedy Decode (Single-path)","color":"orange","values":["[unclear]"]},{"name":"Self Consistency (Multi-path)","color":"blue","values":["[unclear]"]}]}],"unit":"percent","notes":"Exact numeric values for the plotted points are not legible in the image; trends and axis ranges are extracted from visible ticks and labels and marked as [unclear] where exact numbers cannot be read."}
</transcription_json>

<transcription_notes>
- Type: Small-multiples of line charts (8 panels arranged 2x4)
- Panels (left-to-right, top row): MultiArith, ASDiv, SVAMP, GSM8K
- Panels (left-to-right, bottom row): Commonsense QA, Strategy QA, ARC (Easy), ARC (Challenge)
- Legend consistent across panels: Greedy Decode (Single-path) in orange; Self Consistency (Multi-path) in blue
- X-axis: #Sampled Reasoning Paths (ticks shown at regular intervals, often 0,5,10,...,40)
- Y-axis ranges vary per panel; approximate ranges inferred from axis tick labels printed on each small plot
- Visual observation: self-consistency (blue) significantly outperforms greedy (orange) across all tasks, improving with more sampled paths
- Numerical values of each plotted point are not readable; represented as [unclear] in JSON.
</transcription_notes>
</transcription_image>

Figure 7: Self-consistency (blue) significantly improves accuracy across various arithmetic and commonsense reasoning tasks, over LaMDA-137B. Sampling a higher number of diverse reasoning paths consistently improves reasoning accuracy.

We further show additional sampled reasoning paths from the LaMDA-137B model in Table 12, and sampled reasoning paths from the PaLM-540B model in Table 13. We see that the diversity in the additionally sampled reasoning paths indeed helps the model arrive at a more correct final answer after aggregation.

<!-- Section 2 -->
### A.1.2  ROBUSTNESS TO DIFFERENT SETS OF PROMPTS

In Table 9, we further show that self-consistency is quite robust to different sets of input prompts. We manually wrote 3 different sets of chain-of-thought as prompts to the model. Across all sets of prompts, self-consistency yields consistent gains over the original CoT approach.

### A.1.3  COMPARED TO MODEL ENSEMBLES

Additionally, we provide results of directly ensembling the outputs from multiple language models. The results are shown in Table 10, by greedily decoding sequences from 3 language models and

<transcription_page_footer> 16 </transcription_page_footer>

<!-- Decorative: none visible beyond header/footer line -->

---

<transcription_page_header> Published as a conference paper at ICLR 2023 </transcription_page_header>

<!-- Section 1 -->
# Figure 8 and surrounding discussion

<transcription_image>
**Figure 8: Self-consistency (blue) significantly improves accuracy across various arithmetic and commonsense reasoning tasks, over PaLM-540B. Sampling a higher number of diverse reasoning paths consistently helps reasoning accuracy.**

```ascii
[GRID OF SMALL LINE CHARTS - Accuracy (%) vs #Sampled Reasoning Chains]

AddSub
Accuracy (%)
94 ──────────────────────────────●────────
92 ──────●───────────────────────┼────────
90 ──────┼───────────────────────┼────────
88 ──●───┼───────────────────────┼────────
     0   5  10   15  20  25  30  35  40
  Blue = Self Consistency (Multi-path)
  Orange = Greedy Decode (Single-path)

ASDiv
Accuracy (%)
82 ────────────────────────────●───────
80 ─────●──────────────────────┼───────
78 ─────┼──────────────────────┼───────
76 ──●───┼──────────────────────┼───────
     0   5  10   15  20  25  30  35  40

AQuA
Accuracy (%)
48 ─────────────────────●───────
44 ─────●───────────────┼───────
40 ─────┼───────────────┼───────
36 ──●───┼───────────────┼───────
     0   5  10   15  20  25  30  35  40

MultiArith
Accuracy (%)
98 ──────────────────────●──────
96 ─────●────────────────┼──────
94 ─────┼────────────────┼──────
92 ──●───┼────────────────┼──────
     0   5  10   15  20  25  30  35  40

SVAMP
Accuracy (%)
87 ─────────────────────●───────
83 ─────●───────────────┼───────
79 ─────┼───────────────┼───────
75 ──●───┼───────────────┼───────
     0   5  10   15  20  25  30  35  40

GSM8K
Accuracy (%)
75 ──────────────────────●──────
70 ─────●───────────────┼───────
65 ─────┼───────────────┼───────
60 ──●───┼───────────────┼───────
     0   5  10   15  20  25  30  35  40

Commonsense QA
Accuracy (%)
82 ──────────────────────●──────
80 ─────●───────────────┼───────
78 ─────┼───────────────┼───────
76 ──●───┼───────────────┼───────
     0   5  10   15  20  25  30  35  40

Strategy QA
Accuracy (%)
96 ──────────────────────●──────
92 ─────●───────────────┼───────
88 ─────┼───────────────┼───────
84 ──●───┼───────────────┼───────
     0   5  10   15  20  25  30  35  40

ARC (Easy)
Accuracy (%)
96 ──────────────────────●──────
94 ─────●───────────────┼───────
92 ─────┼───────────────┼───────
90 ──●───┼───────────────┼───────
     0   5  10   15  20  25  30  35  40

ARC (Challenge)
Accuracy (%)
88 ──────────────────────●──────
84 ─────●───────────────┼───────
80 ─────┼───────────────┼───────
76 ──●───┼───────────────┼───────
     0   5  10   15  20  25  30  35  40

Legend:
● Blue = Self Consistency (Multi-path)
● Orange = Greedy Decode (Single-path)
```

<transcription_json>
{
  "chart_type": "multiple_line_charts_grid",
  "title": "Self-consistency vs Greedy Decode across tasks (Figure 8)",
  "common_x_label": "#Sampled Reasoning Chains",
  "common_y_label": "Accuracy (%)",
  "charts": [
    {
      "title": "AddSub",
      "series": [
        {"name": "Greedy Decode (Single-path)", "points": [{"x":0,"y":92},{"x":5,"y":92},{"x":10,"y":92},{"x":20,"y":92},{"x":40,"y":92}]},
        {"name": "Self Consistency (Multi-path)", "points": [{"x":0,"y":"~88 [unclear]"},{"x":5,"y":"~92 [unclear]"},{"x":10,"y":"~93 [unclear]"},{"x":20,"y":"~94 [unclear]"},{"x":40,"y":"~94 [unclear]"}]}
      ]
    },
    {
      "title": "ASDiv",
      "series": [
        {"name": "Greedy Decode (Single-path)", "points": [{"x":0,"y":74},{"x":5,"y":74},{"x":10,"y":74},{"x":20,"y":74},{"x":40,"y":74}]},
        {"name": "Self Consistency (Multi-path)", "points": [{"x":0,"y":"~76 [unclear]"},{"x":5,"y":"~78 [unclear]"},{"x":10,"y":"~79 [unclear]"},{"x":20,"y":"~81 [unclear]"},{"x":40,"y":"~82 [unclear]"}]}
      ]
    },
    {
      "title": "AQuA",
      "series": [
        {"name": "Greedy Decode (Single-path)", "points": [{"x":0,"y":36},{"x":5,"y":36},{"x":10,"y":36},{"x":20,"y":36},{"x":40,"y":36}]},
        {"name": "Self Consistency (Multi-path)", "points": [{"x":0,"y":"~34 [unclear]"},{"x":5,"y":"~38 [unclear]"},{"x":10,"y":"~42 [unclear]"},{"x":20,"y":"~45 [unclear]"},{"x":40,"y":"~48 [unclear]"}]}
      ]
    },
    {
      "title": "MultiArith",
      "series": [
        {"name": "Greedy Decode (Single-path)", "points": [{"x":0,"y":94},{"x":5,"y":94},{"x":10,"y":94},{"x":20,"y":94},{"x":40,"y":94}]},
        {"name": "Self Consistency (Multi-path)", "points": [{"x":0,"y":"~92 [unclear]"},{"x":5,"y":"~96 [unclear]"},{"x":10,"y":"~97 [unclear]"},{"x":20,"y":"~98 [unclear]"},{"x":40,"y":"~98 [unclear]"}]}
      ]
    },
    {
      "title": "SVAMP",
      "series": [
        {"name": "Greedy Decode (Single-path)", "points": [{"x":0,"y":78},{"x":5,"y":78},{"x":10,"y":78},{"x":20,"y":78},{"x":40,"y":78}]},
        {"name": "Self Consistency (Multi-path)", "points": [{"x":0,"y":"~71 [unclear]"},{"x":5,"y":"~78 [unclear]"},{"x":10,"y":"~82 [unclear]"},{"x":20,"y":"~85 [unclear]"},{"x":40,"y":"~87 [unclear]"}]}
      ]
    },
    {
      "title": "GSM8K",
      "series": [
        {"name": "Greedy Decode (Single-path)", "points": [{"x":0,"y":56.5},{"x":5,"y":56.5},{"x":10,"y":56.5},{"x":20,"y":56.5},{"x":40,"y":56.5}]},
        {"name": "Self Consistency (Multi-path)", "points": [{"x":0,"y":"~60 [unclear]"},{"x":5,"y":"~66 [unclear]"},{"x":10,"y":"~69 [unclear]"},{"x":20,"y":"~72 [unclear]"},{"x":40,"y":74.4}]}
      ]
    },
    {
      "title": "Commonsense QA",
      "series": [
        {"name": "Greedy Decode (Single-path)", "points": [{"x":0,"y":76},{"x":5,"y":76},{"x":10,"y":76},{"x":20,"y":76},{"x":40,"y":76}]},
        {"name": "Self Consistency (Multi-path)", "points": [{"x":0,"y":"~78 [unclear]"},{"x":5,"y":"~80 [unclear]"},{"x":10,"y":"~80.5 [unclear]"},{"x":20,"y":"~81 [unclear]"},{"x":40,"y":"~81.5 [unclear]"}]}
      ]
    },
    {
      "title": "Strategy QA",
      "series": [
        {"name": "Greedy Decode (Single-path)", "points": [{"x":0,"y":76},{"x":5,"y":76},{"x":10,"y":76},{"x":20,"y":76},{"x":40,"y":76}]},
        {"name": "Self Consistency (Multi-path)", "points": [{"x":0,"y":"~84 [unclear]"},{"x":5,"y":"~90 [unclear]"},{"x":10,"y":"~92 [unclear]"},{"x":20,"y":"~94 [unclear]"},{"x":40,"y":"~95.5 [unclear]"}]}
      ]
    },
    {
      "title": "ARC (Easy)",
      "series": [
        {"name": "Greedy Decode (Single-path)", "points": [{"x":0,"y":96},{"x":5,"y":96},{"x":10,"y":96},{"x":20,"y":96},{"x":40,"y":96}]},
        {"name": "Self Consistency (Multi-path)", "points": [{"x":0,"y":"~96 [unclear]"},{"x":5,"y":"~96 [unclear]"},{"x":10,"y":"~96 [unclear]"},{"x":20,"y":"~96 [unclear]"},{"x":40,"y":"~96 [unclear]"}]}
      ]
    },
    {
      "title": "ARC (Challenge)",
      "series": [
        {"name": "Greedy Decode (Single-path)", "points": [{"x":0,"y":82},{"x":5,"y":82},{"x":10,"y":82},{"x":20,"y":82},{"x":40,"y":82}]},
        {"name": "Self Consistency (Multi-path)", "points": [{"x":0,"y":"~78 [unclear]"},{"x":5,"y":"~84 [unclear]"},{"x":10,"y":"~86 [unclear]"},{"x":20,"y":"~87 [unclear]"},{"x":40,"y":"~88 [unclear]"}]}
      ]
    }
  ],
  "legend": ["Greedy Decode (Single-path) - orange", "Self Consistency (Multi-path) - blue"],
  "notes": "x-axis ticks at 0,5,10,15,20,25,30,35,40. Many plotted values are approximate due to small figure size; values marked with [unclear] indicate estimation."
}
</transcription_json>

<transcription_notes>
- Type: Grid of 10 small line charts (3 columns × 4 rows layout; some pages show 10 charts).
- Colors: blue = Self Consistency (multi-path); orange = Greedy Decode (single-path).
- X-axis: "#Sampled Reasoning Chains" with ticks 0, 5, 10, 15, 20, 25, 30, 35, 40.
- Y-axis: "Accuracy (%)" for each chart (range varies per chart; charts show small error bars).
- Many exact point values are not fully legible at page resolution; values in JSON are best-effort estimates. Where uncertain, values include [unclear].
- The GSM8K chart aligns with table values reported elsewhere on the page (Single model PaLM-540B greedy: 56.5; self-consistency: 74.4).
</transcription_notes>
</transcription_image>

<!-- Section 2 -->
## Table 9: GSM8K accuracy over PaLM-540B

<transcription_table>
**Table 9: GSM8K accuracy over PaLM-540B. The results show robustness of self-consistency with respect to different prompts in the input.**

|  | Prompt set 1 (used in the main text) | Prompt set 2 | Prompt set 3 |
|---|---:|---:|---:|
| CoT (Wei et al., 2022) | 56.5 | 54.6 | 54.0 |
| Self-consistency | 74.4 (+17.9) | 72.1 (+17.5) | 70.4 (+[unclear]) |

<transcription_json>
{
  "table_type": "data_table",
  "title": "GSM8K accuracy over PaLM-540B (Table 9)",
  "columns": ["Metric", "Prompt set 1 (used in the main text)", "Prompt set 2", "Prompt set 3"],
  "data": [
    {"Metric": "CoT (Wei et al., 2022)", "Prompt set 1 (used in the main text)": 56.5, "Prompt set 2": 54.6, "Prompt set 3": 54.0},
    {"Metric": "Self-consistency", "Prompt set 1 (used in the main text)": "74.4 (+17.9)", "Prompt set 2": "72.1 (+17.5)", "Prompt set 3": "70.4 (+[unclear])"}
  ],
  "notes": "Parenthesized values are relative improvements over CoT. The last parenthesized improvement for Prompt set 3 is partly unclear in the image."
}
</transcription_json>

<transcription_notes>
- Source: Figure/table on the page; shows CoT baseline and Self-consistency performance for GSM8K across three prompt sets.
- The improvement parentheses reflect the delta between Self-consistency and CoT for each prompt set.
- The last improvement value (Prompt set 3, +??) is not fully legible; marked as [unclear] in table and JSON.
</transcription_notes>
</transcription_table>

<!-- Section 3 -->
## Paragraph (excerpt)

taking the majority vote (averaged over 10 runs). Note this is a typical ensemble approach (averaging over the predictions over multiple models) and it achieves a performance significantly worse than self-consistency (self-consistency over PaLM-540B gets an accuracy of 74.4%), as lower-capacity models drag down the performance of higher-capacity models. In addition, this approach is limited in two ways: 1) It requires multiple models for an ensemble which might not always be available, while self-consistency only requires one single model to "self-ensemble"; 2) If one of the models is much weaker, it can actually hurt the final performance.

<!-- Section 4 -->
## Table 10: Comparison of GSM8K accuracy over multiple-model ensembles

<transcription_table>
**Table 10: Comparison of GSM8K accuracy over multiple-model ensembles.**

| Method | GSM8K accuracy |
|---|---:|
| Single model: PaLM-540B, greedy / self-consistency | 56.5 / 74.4 |
| Ensemble of models: LaMDA-137B + PaLM-540B | 36.9 ± 0.5 |
| Ensemble of models: PaLM-540B + GPT-3 (code-davinci-001, 175B) | 36.6 ± 0.4 |
| Ensemble of models: LaMDA-137B + GPT-3 (code-davinci-001, 175B) | 16.0 ± 0.8 |
| Ensemble of models: LaMDA-137B + PaLM-540B + GPT-3 (code-davinci-001, 175B) | 33.3 ± 0.7 |

<transcription_json>
{
  "table_type": "data_table",
  "title": "Comparison of GSM8K accuracy over multiple-model ensembles (Table 10)",
  "columns": ["Method", "GSM8K accuracy"],
  "data": [
    {"Method": "Single model: PaLM-540B, greedy / self-consistency", "GSM8K accuracy": "56.5 / 74.4"},
    {"Method": "LaMDA-137B + PaLM-540B", "GSM8K accuracy": "36.9 ± 0.5"},
    {"Method": "PaLM-540B + GPT-3 (code-davinci-001, 175B)", "GSM8K accuracy": "36.6 ± 0.4"},
    {"Method": "LaMDA-137B + GPT-3 (code-davinci-001, 175B)", "GSM8K accuracy": "16.0 ± 0.8"},
    {"Method": "LaMDA-137B + PaLM-540B + GPT-3 (code-davinci-001, 175B)", "GSM8K accuracy": "33.3 ± 0.7"}
  ],
  "notes": "Reported accuracies are averaged/ensemble results; ± indicates standard error reported in the table image."
}
</transcription_json>

<transcription_notes>
- The first row contrasts single-model greedy decode vs self-consistency (PaLM-540B).
- Ensemble rows show various combinations of LaMDA-137B, PaLM-540B, and GPT-3 (code-davinci-001, 175B) with their reported GSM8K accuracies and reported ± uncertainties.
- Values copied as they appear on the page; smaller numeric uncertainties visible (±0.5, ±0.4, ±0.8, ±0.7).
</transcription_notes>
</transcription_table>

<!-- Section 5 -->
### A.1.4 COMBINING SELF-CONSISTENCY WITH OTHER ENSEMBLING STRATEGIES

Self-consistency is completely compatible with other ensemble strategies, although the gains achieved by self-consistency are significantly higher than other ensemble strategies (and can "override" the performance gains achieved by other ensemble strategies). We further performed experiments and include the results in Table 11 (for a fair comparison, we use 40 sets of prompts, or 40 prompt permutations to compare with self-consistency with 40 paths, all experiments are based on PaLM-540B).

<transcription_page_footer> Page 17 | (document) </transcription_page_footer>

---

<transcription_page_header>Published as a conference paper at ICLR 2023</transcription_page_header>

<!-- Decorative: [horizontal rule at top of page] -->

<transcription_table>
**Table 11: Combining self-consistency with other ensembling strategies.**

| Method                                                                  | GSM8K accuracy |
|-------------------------------------------------------------------------|----------------|
| Different sets of prompts (x40)                                         | 58.9           |
| Prompt-permutation (x40)                                                | 59.6           |
| Self-consistency (x40)                                                  | 74.4           |
| Self-consistency + different sets of prompts (x40)                      | 75.4           |
| Self-consistency + prompt-permutation (x40)                             | 73.8           |

<transcription_json>
{"table_type":"data_table","title":"Combining self-consistency with other ensembling strategies","columns":["Method","GSM8K accuracy"],"data":[{"Method":"Different sets of prompts (x40)","GSM8K accuracy":58.9},{"Method":"Prompt-permutation (x40)","GSM8K accuracy":59.6},{"Method":"Self-consistency (x40)","GSM8K accuracy":74.4},{"Method":"Self-consistency + different sets of prompts (x40)","GSM8K accuracy":75.4},{"Method":"Self-consistency + prompt-permutation (x40)","GSM8K accuracy":73.8}]}
</transcription_json>

<transcription_notes>
- Table centered at top of page, spans column width.
- Simple two-column table: left = method description, right = numeric accuracy on GSM8K.
- No colors; thin horizontal rules separate header and rows in printed layout.
</transcription_notes>
</transcription_table>

## A.2 DETAILS ON RESOURCES AND INFERENCE

<!-- Section 1 -->
<!-- Column 1 -->
For all four language models we perform prompting-based inference only. For UL2 we use TPU v3 (2x2 configuration, 4 chips, 8 cores). For GPT-3 models the experiments are done through the public API.10 For LaMDA-137B we use TPU v3 (8x8 configuration, 64 chips, 128 cores). For PaLM-540B we use TPU v4 (4x4x12 configuration, 192 chips, 384 cores). Most inference jobs take 1 to 4 hours (over about 1,000 examples) for each task on UL2 and LaMDA-137B, and about 2 to 12 hours on PaLM-540B. Some tasks (e.g., commonsense reasoning) take longer but do not exceed 2 days for each task.
<!-- Column 2 -->
For GPT-3 models, we use 128 max tokens for all methods, without frequency penalty or presence penalty. For all models, we take the generated outputs until the start of the next "Q:" to parse the final answers, consistent with our prompting format.

<!-- Section 2 -->
<transcription_table>
**Table 12: Additional examples where self-consistency helps repair the errors over greedy decode on LaMDA-137B. Two sampled reasoning paths that are consistent with the ground truth are shown.**

| Question | Greedy Decode | Sampled Path 1 | Sampled Path 2 |
|---------|---------------|----------------|----------------|
| [MultiArith] Sam had 10 socks. If he threw away 3 old ones that didn't fit and bought 36 new ones, how many socks would he have? | Sam had 10 socks. He threw away 3 old ones that didn't fit. He bought 36 new ones. That means he has 10 - 3 = 7 socks. The answer is 41. [unclear: final numeric reading?] | Sam had 10 socks. He threw away 3 old ones that didn't fit. So now he has 7 left. Then he bought 36 new ones. So now he has 7 + 36 = 43 socks. The answer is 43. | He had 10 socks. He threw away 3 old ones that didn't fit. He bought 36 new ones. So in total he has 10 - 3 + 36 = 43 socks. The answer is 43. |
| [SVAMP] In a school there are 697 girls and the rest are boys. If there are 228 more girls than boys. How many boys are there in that school? | There are 697 girls and the rest are boys. That means there are 697 + 228 = 925 girls. The number of boys is 925 - 697 = 228. The answer is 228. | The number of boys is the difference between 697 and 228. This is 697 - 228 = 469. The answer is 469. | In the beginning there are 697 girls and the rest are boys. So, the number of boys must be 697 - 228 = 469 boys. The answer is 469. |
| [AQUA] There are 10 oranges in a basket. Find the no. of ways in which 2 oranges are chosen from the basket? (a) 45 (b) 90 (c) 120 (d) 150 (e) 180 | There are 10 oranges in a basket. So there are 10 ways to choose 2 oranges from the basket. [unclear: numeric step missing] So the number of ways are 10C2. So the answer is (a). | There are 10 oranges in a basket. We need to choose 2 oranges from the basket. So the number of ways are 10C2. So the answer is (a). | There are 10 oranges in the basket. If you choose 2 oranges, you have 10C2 = 45 ways of choosing 2 oranges. So the answer is (a). |
| [CommonsenseQA] The man laid on the soft moss and looked up at the trees, where was the man? (a) niagra falls (b) forest (c) waterfall (d) ground (e) tree | The answer must be something that is soft and mossy. Of the above choices, only ground is soft and mossy. So the answer is (d). | The answer must be somewhere where moss is found. Of the above choices, only forests are known for having moss. So the answer is (b). | The answer must be a place where the man is laying down and looking up at trees. Of the above choices, only forest is a place where people lay down and look at trees. So the answer is (b). |
| [ARC] Which of these will most likely harm a habitat? (a) planting trees. (b) water pollution. (c) rainfall. (d) sunlight. | Planting trees will not harm a habitat. So the answer is (a). | The answer is (b), water pollution, because it will most likely harm the habitat. The other answers are not likely to harm the habitat. | The answer is (b), water pollution. Trees are good for a habitat, rainfall is necessary for a habitat, and sunlight is necessary for a habitat. So the answer is (b). |
| [ARC-challenge] Which process in the carbon cycle takes the longest to complete? (a) emission of waste. (b) respiration in animals. (c) photosynthesis in plants. (d) formation of fossil fuels. | The process of photosynthesis in plants takes the longest to complete. So the answer is (c). | The formation of fossil fuels takes the longest time to complete. So the answer is (d). | The process that takes the longest time to complete is the formation of fossil fuels, which happens over millions of years. So the answer is (d). |

<transcription_json>
{"table_type":"data_table","title":"Additional examples where self-consistency helps repair the errors over greedy decode on LaMDA-137B","columns":["Question","Greedy Decode","Sampled Path 1","Sampled Path 2"],"data":[{"Question":"[MultiArith] Sam had 10 socks. If he threw away 3 old ones that didn't fit and bought 36 new ones, how many socks would he have?","Greedy Decode":"Sam had 10 socks. He threw away 3 old ones that didn't fit. He bought 36 new ones. That means he has 10 - 3 = 7 socks. The answer is 41. [unclear: final numeric reading?]","Sampled Path 1":"Sam had 10 socks. He threw away 3 old ones that didn't fit. So now he has 7 left. Then he bought 36 new ones. So now he has 7 + 36 = 43 socks. The answer is 43.","Sampled Path 2":"He had 10 socks. He threw away 3 old ones that didn't fit. He bought 36 new ones. So in total he has 10 - 3 + 36 = 43 socks. The answer is 43."},{"Question":"[SVAMP] In a school there are 697 girls and the rest are boys. If there are 228 more girls than boys. How many boys are there in that school?","Greedy Decode":"There are 697 girls and the rest are boys. That means there are 697 + 228 = 925 girls. The number of boys is 925 - 697 = 228. The answer is 228.","Sampled Path 1":"The number of boys is the difference between 697 and 228. This is 697 - 228 = 469. The answer is 469.","Sampled Path 2":"In the beginning there are 697 girls and the rest are boys. So, the number of boys must be 697 - 228 = 469 boys. The answer is 469."},{"Question":"[AQUA] There are 10 oranges in a basket. Find the no. of ways in which 2 oranges are chosen from the basket? (a) 45 (b) 90 (c) 120 (d) 150 (e) 180","Greedy Decode":"There are 10 oranges in a basket. So there are 10 ways to choose 2 oranges from the basket. [unclear: numeric step missing] So the number of ways are 10C2. So the answer is (a).","Sampled Path 1":"There are 10 oranges in a basket. We need to choose 2 oranges from the basket. So the number of ways are 10C2. So the answer is (a).","Sampled Path 2":"There are 10 oranges in the basket. If you choose 2 oranges, you have 10C2 = 45 ways of choosing 2 oranges. So the answer is (a)."},{"Question":"[CommonsenseQA] The man laid on the soft moss and looked up at the trees, where was the man? (a) niagra falls (b) forest (c) waterfall (d) ground (e) tree","Greedy Decode":"The answer must be something that is soft and mossy. Of the above choices, only ground is soft and mossy. So the answer is (d).","Sampled Path 1":"The answer must be somewhere where moss is found. Of the above choices, only forests are known for having moss. So the answer is (b).","Sampled Path 2":"The answer must be a place where the man is laying down and looking up at trees. Of the above choices, only forest is a place where people lay down and look at trees. So the answer is (b)."},{"Question":"[ARC] Which of these will most likely harm a habitat? (a) planting trees. (b) water pollution. (c) rainfall. (d) sunlight.","Greedy Decode":"Planting trees will not harm a habitat. So the answer is (a).","Sampled Path 1":"The answer is (b), water pollution, because it will most likely harm the habitat. The other answers are not likely to harm the habitat.","Sampled Path 2":"The answer is (b), water pollution. Trees are good for a habitat, rainfall is necessary for a habitat, and sunlight is necessary for a habitat. So the answer is (b)."},{"Question":"[ARC-challenge] Which process in the carbon cycle takes the longest to complete? (a) emission of waste. (b) respiration in animals. (c) photosynthesis in plants. (d) formation of fossil fuels.","Greedy Decode":"The process of photosynthesis in plants takes the longest to complete. So the answer is (c).","Sampled Path 1":"The formation of fossil fuels takes the longest time to complete. So the answer is (d).","Sampled Path 2":"The process that takes the longest time to complete is the formation of fossil fuels, which happens over millions of years. So the answer is (d)."}]}
</transcription_json>

<transcription_notes>
- Table 12 spans full page width and contains long text cells; printed layout uses small font and multiple horizontal rules separating example rows.
- Leftmost column lists dataset name in square brackets then the question. Other columns show model outputs (Greedy Decode, two sampled reasoning paths).
- Several numeric readings in the Greedy Decode column were ambiguous in the scan (marked with [unclear]).
</transcription_notes>
</transcription_table>

10 https://beta.openai.com/docs/api-reference/making-requests

<!-- Decorative: [horizontal rule above footer] -->

<transcription_page_footer>Page 18</transcription_page_footer>

---

<transcription_page_header>Published as a conference paper at ICLR 2023</transcription_page_header>

<!-- Section 1 -->
<transcription_table>
**Table 13: Additional examples where self-consistency helps repair the errors over greedy decode on PaLM-540B. Two sampled reasoning paths that are consistent with the ground truth are shown.**

| Question | Greedy Decode | Sampled Path 1 | Sampled Path 2 |
|---------|---------------|----------------|----------------|
| [GSM8K] Kyle bought last year's best-selling book for $19.50. This is with a 25% discount from the original price. What was the original price of the book? | The book was sold for $19.50. This is 25% less than the original price. This means the original price was 100%. 25% of 100% is 25%. Therefore the original price was 100% - 25% = 75%. The original price was 75% of $19.50. 75% of $19.50 is 75% * $19.50 = $14.625. The answer is $14.625. | The original price of the book is $19.50. Since it was discounted by 25%, the original price was 19.50 / 0.75 = 26. The answer is 26. | Kyle bought a book that is sold for $19.50. With a 25% discount, the original price must be higher. If we call the original price x, then the discounted price is 0.75x. Since this is $19.50, we can write 0.75x = 19.50. Solving this, we find that the original price is x = 19.50 / 0.75 = $26. The answer is $26. |
| [AQUA] The capacity of a tank of dimensions (8 m x 6 m x 2.5 m) is (a) 120 litres (b) 1,200 litres (c) 12,000 litres (d) 120,000 litres (e) None of these | The volume of the tank is 8 m * 6 m * 2.5 m = 120 m^3. So the capacity of the tank is 120 m^3. So the answer is (c). | The volume of the tank is 8m * 6m * 2.5m = 120m^3. This is equal to 120000 litres. So the answer is (d). | The volume of the tank is 8 m * 6 m * 2.5 m = 120 m^3. One cubic meter contains 1000 liters, so the tank contains 120 m^3 * 1000 liters/m^3 = 120,000 liters. So the answer is (d). |
| [StrategyQA] Yes or no: Can the Great Depression be treated with Prozac? | The Great Depression was an economic depression. Prozac is a drug used to treat depression. Thus, the Great Depression could be treated with Prozac. So the answer is yes. | Prozac is an anti-depressant medication. The Great Depression is not a disease. Thus, Prozac cannot treat the Great Depression. So the answer is no. | The Great Depression is a time period. Prozac is used to treat depression (the mental illness). Thus, the Great Depression can not be treated with Prozac. So the answer is no. |
| [ARC-easy] Which source of energy is nonrenewable? (a) coal (b) sunlight (c) water (d) wood | Coal, sunlight, and water are all renewable sources of energy. Wood is a nonrenewable source of energy. So the answer is (d). | A nonrenewable source of energy is one in which the source is not replenished in a short amount of time. Thus, the only option that is nonrenewable is coal. So the answer is (a). | Coal is a fossil fuel and is formed from dead organisms from the past. Coal cannot be produced in a short period of time, so it is considered a nonrenewable source of energy. So the answer is (a). |
| [ARC-challenge] Students studied the revolution of Earth around the Sun. During which month will Florida have the most sunlight energy available? (a) March (b) June (c) September (d) December. | The Earth is closest to the Sun in December, hence Florida will have the most sunlight energy available in December. So the answer is (d). | Earth is closest to the Sun on June 21, the summer solstice. So the answer is (b). | Florida is closer to the sun during June, so it will have the most sunlight energy during that month. So the answer is (b). |

<transcription_json>
{
  "table_type": "examples_table",
  "title": "Additional examples where self-consistency helps repair the errors over greedy decode on PaLM-540B",
  "columns": ["Question", "Greedy Decode", "Sampled Path 1", "Sampled Path 2"],
  "data": [
    {
      "Question": "[GSM8K] Kyle bought last year's best-selling book for $19.50. This is with a 25% discount from the original price. What was the original price of the book?",
      "Greedy Decode": "The book was sold for $19.50. This is 25% less than the original price. This means the original price was 100%. 25% of 100% is 25%. Therefore the original price was 100% - 25% = 75%. The original price was 75% of $19.50. 75% of $19.50 is 75% * $19.50 = $14.625. The answer is $14.625.",
      "Sampled Path 1": "The original price of the book is $19.50. Since it was discounted by 25%, the original price was 19.50 / 0.75 = 26. The answer is 26.",
      "Sampled Path 2": "Kyle bought a book that is sold for $19.50. With a 25% discount, the original price must be higher. If we call the original price x, then the discounted price is 0.75x. Since this is $19.50, we can write 0.75x = 19.50. Solving this, we find that the original price is x = 19.50 / 0.75 = $26. The answer is $26."
    },
    {
      "Question": "[AQUA] The capacity of a tank of dimensions (8 m x 6 m x 2.5 m) is (a) 120 litres (b) 1,200 litres (c) 12,000 litres (d) 120,000 litres (e) None of these",
      "Greedy Decode": "The volume of the tank is 8 m * 6 m * 2.5 m = 120 m^3. So the capacity of the tank is 120 m^3. So the answer is (c).",
      "Sampled Path 1": "The volume of the tank is 8m * 6m * 2.5m = 120m^3. This is equal to 120000 litres. So the answer is (d).",
      "Sampled Path 2": "The volume of the tank is 8 m * 6 m * 2.5 m = 120 m^3. One cubic meter contains 1000 liters, so the tank contains 120 m^3 * 1000 liters/m^3 = 120,000 liters. So the answer is (d)."
    },
    {
      "Question": "[StrategyQA] Yes or no: Can the Great Depression be treated with Prozac?",
      "Greedy Decode": "The Great Depression was an economic depression. Prozac is a drug used to treat depression. Thus, the Great Depression could be treated with Prozac. So the answer is yes.",
      "Sampled Path 1": "Prozac is an anti-depressant medication. The Great Depression is not a disease. Thus, Prozac cannot treat the Great Depression. So the answer is no.",
      "Sampled Path 2": "The Great Depression is a time period. Prozac is used to treat depression (the mental illness). Thus, the Great Depression can not be treated with Prozac. So the answer is no."
    },
    {
      "Question": "[ARC-easy] Which source of energy is nonrenewable? (a) coal (b) sunlight (c) water (d) wood",
      "Greedy Decode": "Coal, sunlight, and water are all renewable sources of energy. Wood is a nonrenewable source of energy. So the answer is (d).",
      "Sampled Path 1": "A nonrenewable source of energy is one in which the source is not replenished in a short amount of time. Thus, the only option that is nonrenewable is coal. So the answer is (a).",
      "Sampled Path 2": "Coal is a fossil fuel and is formed from dead organisms from the past. Coal cannot be produced in a short period of time, so it is considered a nonrenewable source of energy. So the answer is (a)."
    },
    {
      "Question": "[ARC-challenge] Students studied the revolution of Earth around the Sun. During which month will Florida have the most sunlight energy available? (a) March (b) June (c) September (d) December.",
      "Greedy Decode": "The Earth is closest to the Sun in December, hence Florida will have the most sunlight energy available in December. So the answer is (d).",
      "Sampled Path 1": "Earth is closest to the Sun on June 21, the summer solstice. So the answer is (b).",
      "Sampled Path 2": "Florida is closer to the sun during June, so it will have the most sunlight energy during that month. So the answer is (b)."
    }
  ]
}
</transcription_json>

<transcription_notes>
- Table type: 4-column comparison table (Question | Greedy Decode | Sampled Path 1 | Sampled Path 2).
- Visual: single bordered table occupying the page width, black text on white background. Some cells contain multi-line explanation text. No color coding visible.
- The AQUA question options were read as (a) 120 litres (b) 1,200 litres (c) 12,000 litres (d) 120,000 litres (e) None of these; the correct conversion uses 1 m^3 = 1000 litres.
</transcription_notes>
</transcription_table>

<!-- Section 2 -->
Table 13: Additional examples where self-consistency helps repair the errors over greedy decode on PaLM-540B. Two sampled reasoning paths that are consistent with the ground truth are shown.

<!-- Section 3 -->
A.3 FULL SETS OF PROMPTS

We list the full details of the prompts used for two newly-introduced datasets, AQUA-RAT (Ling et al., 2017) and AI2 Reasoning Challenge (ARC) (Clark et al., 2018), where we manually composed the example chain-of-thought in this paper, in Table 14 and Table 15, respectively.

<!-- Section 4 -->
<transcription_table>
**Table 14: Few-shot exemplars for AQUA-RAT.**

| Q / A Pair |
|------------|
| Q: John found that the average of 15 numbers is 40. If 10 is added to each number then the mean of the numbers is? Answer Choices: (a) 50 (b) 45 (c) 65 (d) 78 (e) 64 |
| A: If 10 is added to each number, then the mean of the numbers also increases by 10. So the new mean would be 50. The answer is (a). |
| Q: If a / b = 3/4 and 8a + 5b = 22, then find the value of a. Answer Choices: (a) 1/2 (b) 3/2 (c) 5/2 (d) 4/2 (e) 7/2 |
| A: If a / b = 3/4, then b = 4a / 3. So 8a + 5(4a/3) = 22. This simplifies to 8a + 20a/3 = 22, which means 44a/3 = 22. So a is equal to 3/2. The answer is (b). |
| Q: A person is traveling at 20 km/hr and reached his destiny in 2.5 hr then find the distance? Answer Choices: (a) 53 km (b) 55 km (c) 52 km (d) 60 km (e) 50 km |
| A: The distance that the person traveled would have been 20 km/hr * 2.5 hrs = 50 km. The answer is (e). |
| Q: How many keystrokes are needed to type the numbers from 1 to 500? Answer Choices: (a) 1156 (b) 1392 (c) 1480 (d) 1562 (e) 1788 |
| A: There are 9 one-digit numbers from 1 to 9. There are 90 two-digit numbers from 10 to 99. There are 401 three-digit numbers from 100 to 500. 9 + 90(2) + 401(3) = 1392. The answer is (b). |

<transcription_json>
{
  "table_type": "few_shot_exemplars",
  "title": "Few-shot exemplars for AQUA-RAT",
  "rows": [
    {
      "Q": "John found that the average of 15 numbers is 40. If 10 is added to each number then the mean of the numbers is? Answer Choices: (a) 50 (b) 45 (c) 65 (d) 78 (e) 64",
      "A": "If 10 is added to each number, then the mean of the numbers also increases by 10. So the new mean would be 50. The answer is (a)."
    },
    {
      "Q": "If a / b = 3/4 and 8a + 5b = 22, then find the value of a. Answer Choices: (a) 1/2 (b) 3/2 (c) 5/2 (d) 4/2 (e) 7/2",
      "A": "If a / b = 3/4, then b = 4a / 3. So 8a + 5(4a/3) = 22. This simplifies to 8a + 20a/3 = 22, which means 44a/3 = 22. So a is equal to 3/2. The answer is (b)."
    },
    {
      "Q": "A person is traveling at 20 km/hr and reached his destiny in 2.5 hr then find the distance? Answer Choices: (a) 53 km (b) 55 km (c) 52 km (d) 60 km (e) 50 km",
      "A": "The distance that the person traveled would have been 20 km/hr * 2.5 hrs = 50 km. The answer is (e)."
    },
    {
      "Q": "How many keystrokes are needed to type the numbers from 1 to 500? Answer Choices: (a) 1156 (b) 1392 (c) 1480 (d) 1562 (e) 1788",
      "A": "There are 9 one-digit numbers from 1 to 9. There are 90 two-digit numbers from 10 to 99. There are 401 three-digit numbers from 100 to 500. 9 + 90(2) + 401(3) = 1392. The answer is (b)."
    }
  ]
}
</transcription_json>

<transcription_notes>
- Table 14 contains four QA exemplars shown as few-shot examples for AQUA-RAT. Each row contains one Q or A line; the presentation on the page is a compact list under the table caption.
- Visual: plain black text, single-column list beneath the heading "Table 14: Few-shot exemplars for AQUA-RAT."
</transcription_notes>
</transcription_table>

<transcription_page_footer>19</transcription_page_footer>

---

<transcription_page_header> Published as a conference paper at ICLR 2023 </transcription_page_header>

<!-- Section 1 -->
## Table 15: Few-shot exemplars for ARC easy/challenge.

Q: George wants to warm his hands quickly by rubbing them. Which skin surface will produce the most heat? (a) dry palms. (b) wet palms. (c) palms covered with oil. (d) palms covered with lotion.

A: Dry surfaces will more likely cause more friction via rubbing than other smoother surfaces, hence dry palms will produce the most heat. The answer is (a).

Q: Which factor will most likely cause a person to develop a fever? (a) a leg muscle relaxing after exercise. (b) a bacterial population in the bloodstream. (c) several viral particles on the skin. (d) carbohydrates being digested in the stomach.

A: Option (b), bacterial population is the most likely cause for a person developing fever. The answer is (b).

Q: Which change in the state of water particles causes the particles to become arranged in a fixed position? (a) boiling. (b) melting. (c) freezing. (d) evaporating.

A: When water is freezed, the particles are arranged in a fixed position; the particles are still moving for all other options. The answer is (c).

Q: When a switch is used in an electrical circuit, the switch can (a) cause the charge to build. (b) increase and decrease the voltage. (c) cause the current to change direction. (d) stop and start the flow of current.

A: The function of a switch is to start and stop the flow of a current. The answer is (d).

<!-- Section 2 -->
## Table 16: Few-shot exemplars for HotpotQA (closed-book setting).

Q: Which magazine was started first Arthur's Magazine or First for Women?

A: Arthur's Magazine started in 1844. First for Women started in 1989. So Arthur's Magazine was started first. The answer is Arthur's Magazine.

Q: The Oberoi family is part of a hotel company that has a head office in what city?

A: The Oberoi family is part of the hotel company called The Oberoi Group. The Oberoi Group has its head office in Delhi. The answer is Delhi.

Q: What nationality was James Henry Miller's wife?

A: James Henry Miller's wife is June Miller. June Miller is an American. The answer is American.

Q: The Dutch-Belgian television series that "House of Anubis" was based on first aired in what year?

A: "House of Anubis" is based on the Dutch-Belgian television series Het Huis Anubis. Het Huis Anubis is first aired in September 2006. The answer is 2006.

<!-- Section 3 -->
As additional information, we also list the exact set of prompts used for all arithmetic reasoning tasks in Table 17, since there are multiple sets of prompts introduced in Wei et al. (2022). The prompts for CommonsenseQA and StrategyQA are the same as used in Wei et al. (2022).

We provide the exact prompts used for common NLP tasks in the following tables as well, including NLI (Table 18, Table 19, Table 20) and Closed-Book Question-Answering tasks (Table 16, Table 21).

<transcription_page_footer> Page 20 </transcription_page_footer>

---

<transcription_page_header>Published as a conference paper at ICLR 2023</transcription_page_header>

<!-- Section 1 -->
<!-- Column 1 -->
## Table 17: Few-shot exemplars for all arithmetic reasoning tasks, from Wei et al. (2022).

Q: There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today?

A: We start with 15 trees. Later we have 21 trees. The difference must be the number of trees they planted. So, they must have planted 21 - 15 = 6 trees. The answer is 6.

Q: If there are 3 cars in the parking lot and 2 more cars arrive, how many cars are in the parking lot?

A: There are 3 cars in the parking lot already. 2 more arrive. Now there are 3 + 2 = 5 cars. The answer is 5.

Q: Leah had 32 chocolates and her sister had 42. If they ate 35, how many pieces do they have left in total?

A: Leah had 32 chocolates and Leah’s sister had 42. That means there were originally 32 + 42 = 74 chocolates. 35 have been eaten. So in total they still have 74 - 35 = 39 chocolates. The answer is 39.

Q: Jason had 20 lollipops. He gave Denny some lollipops. Now Jason has 12 lollipops. How many lollipops did Jason give to Denny?

A: Jason had 20 lollipops. Since he only has 12 now, he must have given the rest to Denny. The number of lollipops he has given to Denny must have been 20 - 12 = 8 lollipops. The answer is 8.

Q: Shawn has five toys. For Christmas, he got two toys each from his mom and dad. How many toys does he have now?

A: He has 5 toys. He got 2 from mom, so after that he has 5 + 2 = 7 toys. Then he got 2 more from dad, so in total he has 7 + 2 = 9 toys. The answer is 9.

Q: There were nine computers in the server room. Five more computers were installed each day, from monday to thursday. How many computers are now in the server room?

A: There are 4 days from monday to thursday. 5 computers were added each day. That means in total 4 * 5 = 20 computers were added. There were 9 computers in the beginning, so now there are 9 + 20 = 29 computers. The answer is 29.

Q: Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On wednesday, he lost 2 more. How many golf balls did he have at the end of wednesday?

A: Michael initially had 58 balls. He lost 23 on Tuesday, so after that he has 58 - 23 = 35 balls. On Wednesday he lost 2 more so now he has 35 - 2 = 33 balls. The answer is 33.

Q: Olivia has $23. She bought five bagels for $3 each. How much money does she have left?

A: She bought 5 bagels for $3 each. This means she spent 5 * $3 = $15 on the bagels. She had $23 in beginning, so now she has $23 - $15 = $8. The answer is 8.

<transcription_page_footer>21</transcription_page_footer>

---

<transcription_page_header>Published as a conference paper at ICLR 2023</transcription_page_header>

# Table 18: Few-shot exemplars for ANLI.

<!-- Section 1 -->
**Premise:**
"Conceptually cream skimming has two basic dimensions - product and geography."
Based on this premise, can we conclude the hypothesis "Product and geography are what make cream skimming work." is true?
OPTIONS:
- yes
- no
- it is not possible to tell

A: Based on "cream skimming has two basic dimensions" we can't infer that these two dimensions are what make cream skimming work. The answer is it is not possible to tell.

<!-- Section 2 -->
**Premise:**
"One of our member will carry out your instructions minutely."
Based on this premise, can we conclude the hypothesis "A member of my team will execute your orders with immense precision." is true?
OPTIONS:
- yes
- no
- it is not possible to tell

A: "one of" means the same as "a member of", "carry out" means the same as "execute", and "minutely" means the same as "immense precision". The answer is yes.

<!-- Section 3 -->
**Premise:**
"Fun for adults and children."
Based on this premise, can we conclude the hypothesis "Fun for only children." is true?
OPTIONS:
- yes
- no
- it is not possible to tell

A: "adults and children" contradicts "only children". The answer is no.

<!-- Section 4 -->
**Premise:**
"He turned and smiled at Vrenna."
Based on this premise, can we conclude the hypothesis "He smiled at Vrenna who was walking slowly behind him with her mother." is true?
OPTIONS:
- yes
- no
- it is not possible to tell

A: the premise does not say anything about "Vrenna was walking". The answer is it is not possible to tell.

<!-- Section 5 -->
**Premise:**
"well you see that on television also"
Based on this premise, can we conclude the hypothesis "You can see that on television, as well." is true?
OPTIONS:
- yes
- no
- it is not possible to tell

A: "also" and "as well" mean the same thing. The answer is yes.

<!-- Section 6 -->
**Premise:**
"Vrenna and I both fought him and he nearly took us."
Based on this premise, can we conclude the hypothesis "Neither Vrenna nor myself have ever fought him." is true?
OPTIONS:
- yes
- no
- it is not possible to tell

A: "Vrenna and I both" contradicts "neither Vrenna nor myself". The answer is no.

<transcription_page_footer>Page 22</transcription_page_footer>

---

<transcription_page_header>Published as a conference paper at ICLR 2023</transcription_page_header>

# Table 19: Few-shot exemplars for e-SNLI (the rationales are crowd-sourced annotations from the original dataset).

<!-- Section 1 -->

Premise:
"A person on a horse jumps over a broken down airplane."
Based on this premise, can we conclude the hypothesis "A person is training his horse for a competition." is true?
OPTIONS:
- yes
- no
- it is not possible to tell
A: The person is not necessarily training his horse. The answer is it is not possible to tell.

Premise:
"A person on a horse jumps over a broken down airplane."
Based on this premise, can we conclude the hypothesis "A person is at a diner, ordering an omelette." is true?
OPTIONS:
- yes
- no
- it is not possible to tell
A: One jumping horse cannot be in a diner ordering food. The answer is no.

Premise:
"A person on a horse jumps over a broken down airplane."
Based on this premise, can we conclude the hypothesis "A person is outdoors, on a horse." is true?
OPTIONS:
- yes
- no
- it is not possible to tell
A: A broken down airplane is outdoors. The answer is yes.

Premise:
"Children smiling and waving at camera."
Based on this premise, can we conclude the hypothesis "They are smiling at their parents." is true?
OPTIONS:
- yes
- no
- it is not possible to tell
A: Just because they are smiling and waving at a camera does not imply their parents or anyone [unclear] behind it. The answer is it is not possible to tell.

Premise:
"Children smiling and waving at camera."
Based on this premise, can we conclude the hypothesis "The kids are frowning." is true?
OPTIONS:
- yes
- no
- it is not possible to tell
A: One cannot be smiling and frowning at the same time. The answer is no.

Premise:
"Children smiling and waving at camera."
Based on this premise, can we conclude the hypothesis "There are children present." is true?
OPTIONS:
- yes
- no
- it is not possible to tell
A: The children must be present to see them smiling and waving. The answer is yes.

<transcription_page_footer>23</transcription_page_footer>

---

<transcription_page_header> Published as a conference paper at ICLR 2023 </transcription_page_header>

<!-- Section 1 -->
## Table 20: Few-shot exemplars for RTE.

Premise:
: "No Weapons of Mass Destruction Found in Iraq Yet."
: Based on this premise, can we conclude the hypothesis "Weapons of Mass Destruction Found in Iraq." is true?
A:
: "No Weapons of Mass Destruction Found" contradicts "Weapons of Mass Destruction Found". The answer is no.

Premise:
: "A place of sorrow, after Pope John Paul II died, became a place of celebration, as Roman Catholic faithful gathered in downtown Chicago to mark the installation of new Pope Benedict XVI."
: Based on this premise, can we conclude the hypothesis "Pope Benedict XVI is the new leader of the Roman Catholic Church." is true?
A:
: "installation of new Pope Benedict XVI." means "Pope Benedict XVI is the new leader". The answer is yes.

Premise:
: "A man is due in court later charged with the murder 26 years ago of a teenager whose case was the first to be featured on BBC One's Crimewatch. Colette Aram, 16, was walking to her boyfriend's house in Keyworth, Nottinghamshire, on 30 October 1983 when she disappeared. Her body was later found in a field close to her home. Paul Stewart Hutchinson, 50, has been charged with murder and is due before Nottingham magistrates later."
: Based on this premise, can we conclude the hypothesis "Paul Stewart Hutchinson is accused of having stabbed a girl." is true?
A:
: The premise does not say Paul Stewart Hutchinson "stabbed" this girl. The answer is no.

Premise:
: "Herceptin was already approved to treat the sickest breast cancer patients, and the company said, Monday, it will discuss with federal regulators the possibility of prescribing the drug for more breast cancer patients."
: Based on this premise, can we conclude the hypothesis "Herceptin can be used to treat breast cancer." is true?
A:
: "Herceptin was approved to treat breast cancer" implies that "Herceptin can be used to treat breast cancer". The answer is yes.

<!-- Section 2 -->
## Table 21: Few-shot exemplars for BoolQ (closed-book setting).

Q: does system of a down have 2 singers?
A:
: System of a Down currently consists of Serj Tankian, Daron Malakian, Shavo Odadjian and John Dolmayan. Serj and Daron do vocals, so the band does have two singers. The answer is yes.

Q: do iran and afghanistan speak the same language?
A:
: Iran and Afghanistan both speak the Indo-European language Persian. The answer is yes.

Q: is a cello and a bass the same thing?
A:
: The cello is played sitting down with the instrument between the knees, whereas the double bass is played standing or sitting on a stool. The answer is no.

Q: can you use oyster card at epsom station?
A:
: Epsom railway station serves the town of Epsom in Surrey and is not in the London Oyster card zone. The answer is no.

<transcription_page_footer> 24 </transcription_page_footer>

---


