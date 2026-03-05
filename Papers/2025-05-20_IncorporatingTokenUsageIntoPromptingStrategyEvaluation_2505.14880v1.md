# 2025-05-20_IncorporatingTokenUsageIntoPromptingStrategyEvaluation_2505.14880v1


---

# Incorporating Token Usage into Prompting Strategy Evaluation

**Chris Sypherd¹, Sergei Petrov², Sonny George³, Vaishak Belle¹**

¹University of Edinburgh, ²Independent Researcher, ³Brandeis University  
**Correspondence:** c.n.sypherd@sms.ed.ac.uk

## Abstract

In recent years, large language models have demonstrated remarkable performance across diverse tasks. However, their task effectiveness is heavily dependent on the prompting strategy used to elicit output, which can vary widely in both performance and token usage. While task performance is often used to determine prompting strategy success, we argue that efficiency—balancing performance and token usage—can be a more practical metric for real-world utility. To enable this, we propose Big-Otok, a theoretical framework for describing the token usage growth of prompting strategies, and analyze Token Cost, an empirical measure of tokens per performance. We apply these to several common prompting strategies and find that increased token usage leads to drastically diminishing performance returns. Our results validate the Big-Otok analyses and reinforce the need for efficiency-aware evaluations.

## 1 Introduction

Large language models (LLMs) are primarily interacted with through natural language prompts. The composition of a prompt exercises significant, often unexpected, influence over the generated output. This has sparked research into "prompt engineering," the study of prompt design to extract maximum performance from LLMs (White et al., 2023). There are many ways to approach prompt engineering; in this paper, we focus on formalized **prompting strategies**, the overarching paradigms of prompt design (e.g., providing examples of question-answer pairs (Brown et al., 2020)).

As prompting strategies have developed alongside LLMs, benchmark accuracy has emerged as the primary metric for success. New prompting strategies are often tested alongside prior ones on a selection of benchmarks and LLMs, using the gain in accuracy over existing strategies as validation of the new approach. Token usage, if included, is often analyzed post-hoc, indicating that it was only a secondary consideration during development. Optimization for performance without regard for token usage leads to inefficient prompting strategies. Our purpose in this work is to demonstrate another, more holistic approach to prompting strategy evaluation and analysis by (1) proposing Big-Otok, a framework for comparing theoretical token usage between distinct prompting strategies and (2) introducing Token Cost (TC), a simple empirical metric to quantify prompting strategy efficiency.

To achieve these goals, we approach prompting strategy efficiency on two fronts: theoretical and empirical. For our theoretical analysis, we derive Big-Otok token complexities for a selection of prompting strategies, similar to time complexity analyses common in software engineering. We substantiate our Big-Otok analyses by evaluating our selection of prompting strategies against common benchmarks using multiple models. We analyze the results of those experiments in terms of TC, to compare how performance and token usage interact. Our results evidence that, while there is performance improvement to be gained from more complex, token-hungry prompting strategies, increasing token usage results in drastically diminishing performance returns.

## 2 Related Work

Although LLM efficiency has been an active area of research for years (see Wan et al. (2024)), underwhelming emphasis has been placed on the efficiency of prompting strategies. Techniques have emerged to reduce token usage, such as frameworks that dynamically manage token usage at inference time—e.g., FrugalGPT (Chen et al., 2023) and LLMLingua (Jiang et al., 2023)—and prompt compression—e.g., Mu et al. (2023). These approaches seek to enable efficient LLM usage in spite of inefficient prompting strategies, whereas this work...
---

<!-- Section 1 -->

3 Methodology

We explore the importance of token usage both theoretically and empirically. Due to the popularity of LLMs, there exists an infeasible number of possible evaluation combinations¹. To focus the scope of this paper on token usage, we restrict the number of prompting strategies, benchmarks, and models we use. We discuss our selection processes in Sections 3.1 and 3.2.

### 3.1 Theoretical Analysis

<transcription_table>
**Table 1: Big-O_tok token complexities for each prompting strategy.**

| Prompting Strategy     | Big-O_tok   | Variables                              |
|-----------------------|-------------|--------------------------------------|
| Vanilla IO            | \(O(1)\)    |                                      |
| Zeroshot CoT          | \(O(1)\)    |                                      |
| (Kojima et al., 2022) |             |                                      |
| Vanilla Fewshot       | \(O(k)\)    | \(k\): k-shot exemplars               |
| (Brown et al., 2020)  |             |                                      |
| Fewshot CoT           | \(O(k)\)    | \(k\): k-shot exemplars               |
| (Wei et al., 2022)    |             |                                      |
| CoT-SC                | \(O(pk)\)  | \(k\): k-shot exemplars; \(p\): sampled chains |
| (Wang et al., 2023b)  |             |                                      |

<transcription_json>
{"table_type": "data_table", "title": "Big-O_tok token complexities for each prompting strategy", "columns": ["Prompting Strategy", "Big-O_tok", "Variables"], "data": [{"Prompting Strategy": "Vanilla IO", "Big-O_tok": "O(1)", "Variables": ""}, {"Prompting Strategy": "Zeroshot CoT (Kojima et al., 2022)", "Big-O_tok": "O(1)", "Variables": ""}, {"Prompting Strategy": "Vanilla Fewshot (Brown et al., 2020)", "Big-O_tok": "O(k)", "Variables": "k: k-shot exemplars"}, {"Prompting Strategy": "Fewshot CoT (Wei et al., 2022)", "Big-O_tok": "O(k)", "Variables": "k: k-shot exemplars"}, {"Prompting Strategy": "CoT-SC (Wang et al., 2023b)", "Big-O_tok": "O(pk)", "Variables": "k: k-shot exemplars; p: sampled chains"}]}
</transcription_json>

We categorize prompting strategies into three broad groups: **(1) linguistic prompt engineering**, which relies on specific phrasing techniques—e.g., Plan-and-Solve (Wang et al., 2023a) or Zeroshot CoT (Kojima et al., 2022); **(2) in-context learning**, which consists of providing examples of task-response pairs before providing the task to the LLM—e.g., Vanilla Fewshot (Brown et al., 2020) or Fewshot CoT (Wei et al., 2022); and **(3) multi-hop**, which is characterized by multiple LLM calls—e.g., Least-To-Most (Zhou et al., 2023), Tree-of-Thought (Yao et al., 2023), or CoT Self-Consistency² (Wang et al., 2023b). These 3 prompting strategy categories roughly correspond to the following 3 Big-O_tok complexity classes, respectively: (1) constant—e.g., the consistent overhead of "Think step by step" (Wei et al., 2022); (2) linear—e.g., the number of fewshot exemplars; and (3) polynomial or higher—e.g., the number of multi-hop steps times the number of exemplars. These Big-O_tok complexity classes are reflected in Table 1.

To ensure our investigation represents all 3 categorizations, we select prompting strategies from each. Namely, we choose Vanilla IO (i.e., simply providing the benchmark question) as a baseline; Zeroshot CoT to represent (1); Vanilla Fewshot and Fewshot CoT for (2); and CoT-SC for (3). These strategies are widely adopted, tend to build on each other without significant changes to prompt design, and demonstrate an organic evolution of prompting strategies over several years (Chu et al., 2024).

The purpose of Big-O_tok is to provide an objective representation of the theoretical token usage of a given prompting strategy, enabling direct comparison with the Big-O_tok of other prompting strategies. Big-O_tok is based on Big-O notation (Knuth, 1976) and thus we rely on the terminology and definitions associated with it.

Big-O_tok describes the asymptotic growth of token usage as a function of variables³ in the prompting strategy (e.g., the number of fewshot examples). It is derived analogously to Big-O time complexity: by considering how token usage increases as prompting strategy variables approach infinity. The variables with the highest growth rate dominate the other terms (e.g., constants, lower-order variables,

---

² Abbreviated as CoT-SC_n, where n is the number of sampled chains.

³ We treat the initial input that the prompting strategy modifies (e.g., a benchmark question) to be constant and exclude it for simplicity. Similarly, we treat additive adjustments to the input or output (e.g., CoT's "Think step by step" (Wei et al., 2022)) as constants.

---

¹Prompting strategies: 40+ (Vatsal and Dubey, 2024; Chu et al., 2024); Benchmarks: 130+ (Gao et al., 2023); Opensource, benchmarked LLMs: 3200+, as of January, 2025 (Fourrier et al., 2024).
---

<!-- Section 4 -->
### 3.2 Empirical Analysis

We test our selection of prompting strategies against 3 common benchmarks using 3 LLMs. To perform the empirical evaluations, we leverage LM Evaluation Harness (Biderman et al., 2024; Gao et al., 2023), a framework aimed at increasing the reproducibility of LLM evaluations.

We base our selection of models on recency, popularity, and size. We do not use commercial models due to budget constraints⁴. We select Llama 3.1 8B Instruct (Dubey et al., 2024), Qwen 2.5 14B Instruct, and Qwen 2.5 32B Instruct (Qwen et al., 2025). This selection provides coverage of various sizes of smaller models (each approximately doubling the parameter count of the prior) and diversity of origin, to ensure multiple approaches to data collection, training, and alignment are represented⁵.

For benchmarks, we select BBH (Suzgun et al., 2023), GSM8K (Cobbe et al., 2021), and MMLU (Hendrycks et al., 2021). This represents a diverse group of general-purpose benchmarks based on typical accuracy ranges⁶ and response type⁷. For fewshot prompting strategies, we use 3 exemplars for BBH, 8 for GSM8K, and 4 for MMLU⁸.

### 4 Results

To substantiate our Big-O_tok analyses, we use the observed token usages from our experiments to calculate the relative token usage ratios between prompting strategies. We derive theoretical estimates of those ratios from our Big-O_tok functions by substituting in the values from our experiments for the variables in Big-O_tok (e.g., p = 5 and k = 5 for CoT-SC_5). The results of that comparison are found in Table 2. We expect noise in the observed token usage due to: inherent token usage (e.g., chat templates); the relatively low values of prompting strategy variables (e.g., k = 3 fewshot exemplars for BBH); and the unpredictability of LLM output. However, while the observed and theoretical factors are not perfect matches, our findings do correctly align with the Big-O_tok token complexity classes discussed in Section 3.1 (constant, linear, and polynomial). In other words,

\[
T_{O_{tok(1),b,m}}() < T_{O_{tok(k),b,m}}(k) < T_{O_{tok(pk),b,m}}(p, k)
\]

where \(T_{O_{tok,b,m}}(x)\) is the observed token usage for each prompting strategy in the \(O_{tok}\) complexity class, benchmark \(b\), and model \(m\) in our experiments.

To quantify token efficiency, we discuss the results from our experiments in terms of Token Cost⁹ (TC). We define TC as the number of tokens¹⁰ per percentage point of accuracy (expressed as \(\frac{t}{p}\)). The inverse of TC can be thought of as token efficiency; thus, relatively high TC is less efficient while lower TC is more efficient. We use this metric, \(\frac{t}{p}\), rather than the inverse, \(\frac{p}{t}\), because we find it to be more intuitive in the context of prompting strategies.

The results of the experiments outlined in Section 3.2 are found in Figure 1. Across all benchmarks and models, our experiments demonstrate consistent trend lines (of the form \(y = \log(\log(x))\)), reflecting the diminishing accuracy returns from increased token usage. In other words, it requires significantly more tokens to realize performance gains as token usage increases. To discuss this trend in terms of TC, we explore both *average* and *marginal* TC¹¹. Average TC is simply

---

⁴ See Appendix C.3 for cost estimates for commercial APIs.  
⁵ We choose two Qwen 2.5 models to facilitate a comparison between model size, found in Appendix D.2.  
⁶ GSM8K: 80-95%; BBH: 50-87%; MMLU: 70-92% (Fourrier et al., 2024; Dubey et al., 2024; Qwen et al., 2025).  
⁷ GSM8K: free response number; BBH: free response text; MMLU: multiple choice.  
⁸ These numbers are based on the availability of CoT examples in LM Evaluation Harness and closely reflect the number of examples suggested in CoT-SC (Wang et al., 2023b).  
⁹ See Appendix B for an expanded discussion on TC interpretation, including edge cases.  
¹⁰ Token counts are estimated by \(\frac{\text{num characters}}{4}\).  
¹¹ We use the average of ratios when discussing each to give

<transcription_table>
**Table 2: Theoretical and observed token usage ratios between prompting strategies, averaged over the 3 benchmarks. Values are formatted as *theoretical*; *observed* and derived by \(\frac{\text{num tokens}_2}{\text{num tokens}_1}\), where \(\text{num tokens}_2 > \text{num tokens}_1\).**

| Column: Higher Token Usage (Numerator) \| Row: Lower Token Usage (Denominator) | CoT-SC₅ | CoT-SC₁ | Fewshot CoT | Vanilla Fewshot | Zeroshot CoT |
|----------------------------------------------------------------------------------|---------|---------|-------------|-----------------|--------------|
| Vanilla IO                                                                       | 50; 29.3 | 25; 14.6 | 5; 3.0     | 5; 2.2         | 1; 1.3      |
| Zeroshot CoT                                                                     | 50; 23.4 | 25; 11.7 | 5; 2.4     | 5; 1.7         |              |
| Vanilla Fewshot                                                                  | 10; 13.5 | 5; 6.8  | 1; 1.4     |                 |              |
| Fewshot CoT                                                                      | 10; 9.9  | 5; 5.0  |           |                 |              |
| CoT-SC₅                                                                          | 2; 2.0   |         |           |                 |              |

<transcription_json>
{
  "table_type": "data_table",
  "title": "Theoretical and observed token usage ratios between prompting strategies",
  "description": "Values are formatted as theoretical; observed and derived by num_tokens_2 / num_tokens_1, where num_tokens_2 > num_tokens_1, averaged over the 3 benchmarks.",
  "columns": [
    "Higher Token Usage (Numerator) / Lower Token Usage (Denominator)",
    "CoT-SC5",
    "CoT-SC1",
    "Fewshot CoT",
    "Vanilla Fewshot",
    "Zeroshot CoT"
  ],
  "data": [
    {
      "Lower Token Usage (Denominator)": "Vanilla IO",
      "CoT-SC5": "50; 29.3",
      "CoT-SC1": "25; 14.6",
      "Fewshot CoT": "5; 3.0",
      "Vanilla Fewshot": "5; 2.2",
      "Zeroshot CoT": "1; 1.3"
    },
    {
      "Lower Token Usage (Denominator)": "Zeroshot CoT",
      "CoT-SC5": "50; 23.4",
      "CoT-SC1": "25; 11.7",
      "Fewshot CoT": "5; 2.4",
      "Vanilla Fewshot": "5; 1.7",
      "Zeroshot CoT": ""
    },
    {
      "Lower Token Usage (Denominator)": "Vanilla Fewshot",
      "CoT-SC5": "10; 13.5",
      "CoT-SC1": "5; 6.8",
      "Fewshot CoT": "1; 1.4",
      "Vanilla Fewshot": "",
      "Zeroshot CoT": ""
    },
    {
      "Lower Token Usage (Denominator)": "Fewshot CoT",
      "CoT-SC5": "10; 9.9",
      "CoT-SC1": "5; 5.0",
      "Fewshot CoT": "",
      "Vanilla Fewshot": "",
      "Zeroshot CoT": ""
    },
    {
      "Lower Token Usage (Denominator)": "CoT-SC5",
      "CoT-SC5": "2; 2.0",
      "CoT-SC1": "",
      "Fewshot CoT": "",
      "Vanilla Fewshot": "",
      "Zeroshot CoT": ""
    }
  ]
}
</transcription_json>

<transcription_notes>
- Table compares prompting strategies by token usage ratio: theoretical and observed values.
- Highlighted values show that observed token usage ratios generally align with theoretical estimates.
- Token usage ratios are based on average over three benchmarks.
</transcription_notes>
---

<!-- Section 1 -->
<transcription_image>
**Figure 1: Accuracy vs. token usage plots with standard error bars for various prompting strategies, models, and benchmarks. The trend lines demonstrate the rapid growth of TC for these strategies.**

```ascii
(Plot A) BBH
Accuracy (%) |
0.9 +--------------------------------------------------------------------+
    | o C_e10                                                        o C_e10|
0.8 | o C_e5                                                         o C_e5 |
    | o C_e3                                                         o C_e3 |
    |   C_e1                                                         C_e1  |
    | o C_f10                                                        o C_f10|
    | o C_f5                                                         o C_f5 |
0.7 | o C_f3                                                         o C_f3 |
    |   C_f1                                                         C_f1  |
    |                                                                *    |
0.6 |          *                                                         * |
    |                                                                    *|
0.5 |                                                                    * |
    |*                                                                   * |
0.4 |*                                                                    *|
    +--------------------------------------------------------------------+
    0          2000       4000       6000        8000       10000       12000

(Plot B) GSM8K
Accuracy (%) |
0.9 +--------------------------------------------------------------------+
    | o C_e10                                                       o C_e10 |
0.85| o C_e5                                                        o C_e5  |
    | o C_e3                                                        o C_e3  |
    |   C_e1                                                        C_e1   |
    | o C_f10                                                       o C_f10 |
0.8 | o C_f5                                                        o C_f5  |
    | o C_f3                                                        o C_f3  |
0.75|   C_f1                                                        C_f1   |
    |                                                                *     |
0.7 |          *                                                        *  |
    |                                                                     *|
0.65|                                                                     * |
    |*                                                                    * |
0.6 |*                                                                     *|
    +--------------------------------------------------------------------+
    0          2000       4000       6000        8000       10000       12000

(Plot C) MMLU
Accuracy (%) |
0.85+--------------------------------------------------------------------+
    | o C_e10                                                       o C_e10 |
0.8 | o C_e5                                                        o C_e5  |
    | o C_e3                                                        o C_e3  |
0.75|   C_e1                                                        C_e1   |
    | o C_f10                                                       o C_f10 |
0.7 | o C_f5                                                        o C_f5  |
    | o C_f3                                                        o C_f3  |
0.65|   C_f1                                                        C_f1   |
    |                                                                *     |
0.6 |          *                                                        *  |
    |                                                                     *|
0.55|                                                                     * |
    |*                                                                    * |
0.5 |*                                                                     *|
    +--------------------------------------------------------------------+
    0          2000       4000       6000        8000       10000       12000

Legend:
- Prompting Strategy:
  o Fewshot CoT
  ◇ Zeroshot CoT
  □ Vanilla IO
  + Vanilla Fewshot
  * CoT SC-5
  * CoT SC-10

- Model Colors:
  ■ Gwen 2.5 32B
  ■ Gwen 2.5 14B
  ■ Llama 3.1 18B

Axes labels:
- X-axis: Average Total Tokens (Input + Output)
- Y-axis: Accuracy (%)
```

<transcription_json>
{
  "chart_type": "scatter_plots",
  "title": "Accuracy vs. token usage plots",
  "plots": [
    {
      "name": "BBH",
      "x_axis": "Average Total Tokens (Input + Output)",
      "y_axis": "Accuracy (%)",
      "data_points": [
        {"prompting_strategy": "Fewshot CoT", "model": "Gwen 2.5 32B", "tokens": [1000, 3500, 9000], "accuracies": [0.55, 0.75, 0.85]},
        {"prompting_strategy": "Fewshot CoT", "model": "Gwen 2.5 14B", "tokens": [1200, 4000, 8500], "accuracies": [0.5, 0.7, 0.8]},
        {"prompting_strategy": "Fewshot CoT", "model": "Llama 3.1 18B", "tokens": [1100, 3700, 9000], "accuracies": [0.6, 0.8, 0.85]},
        {"prompting_strategy": "Zeroshot CoT", "model": "Gwen 2.5 32B", "tokens": [1500, 3700, 9000], "accuracies": [0.7, 0.85, 0.9]},
        {"prompting_strategy": "Vanilla IO", "model": "Gwen 2.5 32B", "tokens": [1300, 3500, 8000], "accuracies": [0.65, 0.8, 0.85]},
        {"prompting_strategy": "Vanilla Fewshot", "model": "Gwen 2.5 14B", "tokens": [1400, 3600, 8500], "accuracies": [0.68, 0.82, 0.88]},
        {"prompting_strategy": "CoT SC-5", "model": "Llama 3.1 18B", "tokens": [1100, 3600, 8500], "accuracies": [0.7, 0.85, 0.9]},
        {"prompting_strategy": "CoT SC-10", "model": "Llama 3.1 18B", "tokens": [1200, 3700, 9000], "accuracies": [0.75, 0.88, 0.92]}
      ]
    },
    {
      "name": "GSM8K",
      "x_axis": "Average Total Tokens (Input + Output)",
      "y_axis": "Accuracy (%)",
      "data_points": [
        {"prompting_strategy": "Fewshot CoT", "model": "Gwen 2.5 32B", "tokens": [1500, 4000, 7000], "accuracies": [0.75, 0.85, 0.9]},
        {"prompting_strategy": "Fewshot CoT", "model": "Gwen 2.5 14B", "tokens": [1600, 4300, 7200], "accuracies": [0.7, 0.82, 0.85]},
        {"prompting_strategy": "Fewshot CoT", "model": "Llama 3.1 18B", "tokens": [1550, 4200, 7000], "accuracies": [0.73, 0.83, 0.87]},
        {"prompting_strategy": "Zeroshot CoT", "model": "Gwen 2.5 32B", "tokens": [1700, 4600, 7500], "accuracies": [0.8, 0.88, 0.9]},
        {"prompting_strategy": "Vanilla IO", "model": "Gwen 2.5 32B", "tokens": [1600, 4300, 7200], "accuracies": [0.78, 0.85, 0.87]},
        {"prompting_strategy": "Vanilla Fewshot", "model": "Gwen 2.5 14B", "tokens": [1650, 4400, 7300], "accuracies": [0.79, 0.86, 0.89]},
        {"prompting_strategy": "CoT SC-5", "model": "Llama 3.1 18B", "tokens": [1600, 4400, 7300], "accuracies": [0.8, 0.87, 0.9]},
        {"prompting_strategy": "CoT SC-10", "model": "Llama 3.1 18B", "tokens": [1650, 4500, 7400], "accuracies": [0.82, 0.88, 0.91]}
      ]
    },
    {
      "name": "MMLU",
      "x_axis": "Average Total Tokens (Input + Output)",
      "y_axis": "Accuracy (%)",
      "data_points": [
        {"prompting_strategy": "Fewshot CoT", "model": "Gwen 2.5 32B", "tokens": [2000, 5000, 11000], "accuracies": [0.65, 0.75, 0.8]},
        {"prompting_strategy": "Fewshot CoT", "model": "Gwen 2.5 14B", "tokens": [2100, 5200, 12000], "accuracies": [0.6, 0.7, 0.75]},
        {"prompting_strategy": "Fewshot CoT", "model": "Llama 3.1 18B", "tokens": [2050, 5100, 11500], "accuracies": [0.62, 0.72, 0.78]},
        {"prompting_strategy": "Zeroshot CoT", "model": "Gwen 2.5 32B", "tokens": [2200, 5300, 12000], "accuracies": [0.7, 0.8, 0.85]},
        {"prompting_strategy": "Vanilla IO", "model": "Gwen 2.5 32B", "tokens": [2100, 5200, 11500], "accuracies": [0.68, 0.78, 0.82]},
        {"prompting_strategy": "Vanilla Fewshot", "model": "Gwen 2.5 14B", "tokens": [2150, 5250, 11800], "accuracies": [0.69, 0.79, 0.83]},
        {"prompting_strategy": "CoT SC-5", "model": "Llama 3.1 18B", "tokens": [2150, 5250, 11800], "accuracies": [0.7, 0.8, 0.84]},
        {"prompting_strategy": "CoT SC-10", "model": "Llama 3.1 18B", "tokens": [2200, 5300, 12000], "accuracies": [0.72, 0.82, 0.85]}
      ]
    }
  ],
  "legend": {
    "prompting_strategy": ["Fewshot CoT", "Zeroshot CoT", "Vanilla IO", "Vanilla Fewshot", "CoT SC-5", "CoT SC-10"],
    "models": ["Gwen 2.5 32B", "Gwen 2.5 14B", "Llama 3.1 18B"]
  }
}
</transcription_json>

<transcription_notes>
- Each plot shows accuracy (%) on the y-axis versus average total tokens (input + output) on the x-axis.
- Models represented by color-coded lines: Gwen 2.5 32B, Gwen 2.5 14B, Llama 3.1 18B.
- Prompting strategies indicated with different markers.
- Standard error bars are included.
- Trend lines indicate rapid growth of Token Cost (TC) for these strategies.
</transcription_notes>
</transcription_image>

the token usage divided by the accuracy for a given prompting strategy ( \(\frac{num\ tokens_{obs}}{accuracy_{obs}}\) ). Marginal TC is the change in token usage to realize the change in performance between two prompting strategies. In other words, for \(num\ tokens_2 >= num\ tokens_1\),

\[
\frac{num\ tokens_2 - num\ tokens_1}{accuracy_2 - accuracy_1}
\]

Both average and marginal TC can be thought of as the slope between two points (one being the origin, for average TC), which represents the expected cost, in tokens, of adding one point of accuracy.

Across all experiments, the average TC for the prompting strategy with the lowest accuracy is 5.0 \(\frac{t}{p}\), while that of the highest performing prompting strategy is 119.4 \(\frac{t}{p}\), a more than 20x increase in average TC and, inversely, 20x *decrease* in efficiency. This is reflected in the plots in Figure 1 in that even the worst performing prompting strategies still attain relatively high accuracy and more complex ones make only small gains over that for vastly more token usage. Using accuracy as the sole metric ignores the drastic decrease in efficiency that can result from increased token usage.

In Figure 1, we observe an initially steep curve, indicating that tokens are traded relatively efficiently for accuracy, followed by a plateau, where tokens are traded more inefficiently for accuracy. To compare the marginal TC along this curve, we select Vanilla IO, Fewshot CoT, and CoT-SC\(_{10}\) which tend to lie on the extremes of the trend lines. Across all experiments, the marginal TC between Vanilla IO and Fewshot CoT is 65.3 \(\frac{t}{p}\) while the marginal TC between Fewshot CoT and CoT-SC is 6701.8 \(\frac{t}{p}\), a decrease in efficiency of more than two orders of magnitude. In a high-stakes scenario where accuracy is paramount, pursuing performance gains at a rate of 6701.8 \(\frac{t}{p}\) may be an acceptable cost. For many real-world scenarios, increasing accuracy at a rate of 65.3 \(\frac{t}{p}\) might be more reasonable. TC provides an intuitive way to compare the tradeoff between token usage and performance and allows for more informed prompting strategy and variable selection.

We perform an ablation study, found in Appendix D.1, on the number of fewshot exemplars. We find that incrementally increasing the number of fewshot examples follows a similar trend of yielding diminishing returns as token usage increases.

All information for reproducing our results, as well as our verbatim results, are detailed in Appendices C.4 and C.5.

## 5 Conclusion

Token usage represents a significant, yet often underrepresented, component of prompting strategy evaluation. To facilitate the comparison of token usage between distinct prompting strategies, we present Big-O\(_{tok}\) token complexity and substantiate it empirically by comparing predicted token usages to those derived from our experiments. We analyze our experiments in terms of Token Cost and use it to demonstrate the tradeoffs between token usage and performance. Our experiments demonstrate the importance of including token usage in prompting strategy evaluation and validate Big-O\(_{tok}\) and Token Cost as viable means of doing so.
---

## Limitations

To focus the contribution of this work, we make a number of thoughtful concessions, such as the models, benchmarks, and prompting strategies we use. We explicitly justify the most relevant limitations in the main text above–such as in Sections 3.1 and 3.2–and note other minor limitations here to further demonstrate the purpose and scope of this work. Despite the limitations, we maintain that the core premise of this work–demonstrating how to incorporate token usage into prompting strategy evaluation–remains broadly applicable beyond our experiments.

**Prompting Strategies.** In Section 1, we narrow the scope of this work to a subset of the broader prompt engineering landscape: formalized prompting strategies. As detailed throughout the Appendix, we strive to control for factors extraneous to the minimalist instantiation of each prompting strategy. We do so to isolate the effects of token usage dictated by the prompting strategies and the resultant benchmark performance to demonstrate how a significant area of research has become prone to inefficiencies due to a lack of relevant metrics. Although we focus on formalized prompting strategies, Big-O_tok and TC are useful metrics for other aspects of prompt engineering as well, such as linguistic and language choices.

As noted in Sections 1 and 2, the focus of this work is on incorporating token usage into prompting strategy evaluationand analysis. We do not seek to seek to solve issues of prompting strategy efficiency but instead provide methods for quantifying it, both for researchers and practitioners. To maintain that scope, we do not explore nor propose specific methods of optimizing prompts and instead focus on introducing insightful metrics and demonstrating their utility in practice.

The results we present here represent a single thread of prompting strategy evolution; we expect the results to follow a predictable pattern (e.g., diminishing accuracy returns) because there are no drastic changes to the principles underlying our selection of prompting strategies. It is likely that fundamentally different prompting strategies, such as Least-to-Most (Zhou et al., 2023) or Algorithm of Thoughts (Sel et al., 2024), would not follow the trend lines in our plots.

**Models.** Depending on the data collection and processing methods used by LLM creators, benchmark data leakage could influence our empirical results, as demonstrated by Mirzadeh et al. (2025). LLMs that were trained on data that included BBH question-answer pairs, for example, could be influenced by prompting strategies to a lesser degree than those that were not. We use models from multiple sources in conjunction with multiple benchmarks to mitigate the potential effects of data leakage.

In this work, we exclusively consider autoregressive, text-to-text ("traditional") LLMs because most prompting strategies are optimized for them. We recognize, however, that multimodal and, more recently, reasoning LLMs have become increasingly relevant (DeepSeek-AI et al., 2025; Yin et al., 2024; Caffagni et al., 2024). We exclude them from our investigation here for a number of reasons: (1) prompt engineering specific to such models is a nascent field and distinct from prompt engineering for traditional LLMs¹² (Wu et al., 2024); (2) due to the recency of reasoning models, there are very few (especially open-source) models available; and (3) the inclusion of multimodal benchmarks and the use of reasoning models would drastically increase the compute required to undertake a similar study. Nevertheless, we maintain that the efficiency-aware metrics explored here remain relevant to such models since they function simply on tokenized inputs and outputs. We see prompting strategies designed for multimodal and, particularly, reasoning LLMs as a significant avenue for future research and are hopeful that Big-O_tok and TC will be incorporated into their development.

While we believe it a fair comparison that lends itself to real-world deployment, we recognize that running our selection of prompting strategies with relatively small LLMs on a subset of benchmarks does not fully reflect the performance of the strategy under all conditions. It is very likely, for example, that the CoT prompting strategy (Wei et al., 2022) would be leveraged better by Llama 3.1 405B than by Llama 3.1 8B, due to the former exhibiting superior reasoning capabilities (Dubey et al., 2024). The strength of an LLM may magnify the disparity between a specific prompting strategy and others.

**Benchmarks.** Similarly, while we attempt to cover a breadth of domains in our selection of benchmarks, this selection may fail to highlight

---

¹² For reasoning models, some commercial providers even advise against the use of established prompting strategies (see https://platform.openai.com/docs/guides/reasoning-best-practices).
---

the strengths of some prompting strategies over others in certain domains. Our purpose is not to rank prompting strategies but to demonstrate the tradeoff between token usage and benchmark accuracy. We recognize, however, that our selection of benchmarks may fail to cover the strength of a particular prompting strategy entirely, which may paint it in a worse light than it deserves. To mitigate this point, we focus on generalist prompting strategies and benchmarks and detail our selection processes in Sections 3.1 and 3.2.

A common issue in LLM benchmarking is reliable answer extraction. Often, regular expressions are used, which are not robust to the unpredictable output formats an LLM may generate. We rely largely on the extraction methods from LM Evaluation Harness but observe certain inaccuracies in answer extraction. This is an open problem in LLM research (Yu et al., 2025). For this project, we rely on consistency in answer extraction methods between experiments but recognize that certain correct answers may be marked incorrectly.

**Big-Otok.** A minor limitation of Big-Otok is a lack of differentiation between input and output tokens. It is inherently more expensive for an LLM to generate output tokens than to process input tokens due to its autoregressive nature, a fact that is reflected in the pricing structure of common commercial APIs¹³. We considered that differentiating between input and output tokens would have introduced excessive complexity to Big-Otok, particularly since it does not serve as a precise measure. We instead consider combined token usage (input **and** output) to provide a holistic view of token consumption.

Another limitation of Big-Otok is the decreased range of prompting strategy variable values. While variables in traditional Big-O analyses often span many orders of magnitude, variables in prompting strategies tend to be lower (typically <= 100) (Brown et al., 2020; Wang et al., 2023b). As noted in Section 4, the relatively low values for those variables could result in extraneous factors (e.g., chat templates, model idiosyncrasies, etc.) limiting their impact on overall token usage. However, we observed that, even for extremely low values (e.g., k = 3 fewshot examples for BBH), the token usages observed in each experiment aligned with the expected Big-Otok token complexity classes. Although not a precise measure, Big-Otok can still provide useful insights for expected prompting strategy token usage, even for small values.

**Ethical Impact**

LLM usage incurs real-world monetary and environmental costs (Schwartz et al., 2020; Dhar, 2020; Wu et al., 2022). This work promotes the consideration of token usage in prompting strategy development and evaluation to increase the long-term efficiency of LLM inference.

**Acknowledgments**

This work was partly funded by a Royal Society University Research Fellowship and a grant from Cisco.

**References**

Stella Biderman, Hailey Schoelkopf, Lintang Sutawika, Leo Gao, Jonathan Tow, Baber Abbasi, Alham Fikri Aji, Pawan Sasanka Ammanamanchi, Sidney Black, Jordan Clive, Anthony DiPofi, Julen Etxaniz, Benjamin Fattori, Jessica Zosa Forde, Charles Foster, Jeffrey Hsu, Mimansa Jaiswal, Wilson Y. Lee, Haonan Li, Charles Lovering, Niklas Muennighoff, Ellie Pavlick, Jason Phang, Aviya Skowron, Samson Tan, Xiangru Tang, Kevin A. Wang, Genta Indra Winata, François Yvon, and Andy Zou. 2024. Lessons from the trenches on reproducible evaluation of language models. *Preprint*, arXiv:2405.14782.

Tom Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared D Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, Sandhini Agarwal, Ariel Herbert-Voss, Gretchen Krueger, Tom Henighan, Rewon Child, Aditya Ramesh, Daniel Ziegler, Jeffrey Wu, Clemens Winter, Chris Hesse, Mark Chen, Eric Sigler, Mateusz Litwin, Scott Gray, Benjamin Chess, Jack Clark, Christopher Berner, Sam McCandlish, Alec Radford, Ilya Sutskever, and Dario Amodei. 2020. Language models are few-shot learners. In *Advances in Neural Information Processing Systems*, volume 33, pages 1877–1901. Curran Associates, Inc.

Davide Caffagni, Federico Cocchi, Luca Barsellotti, Nicholas Moratelli, Sara Sarto, Lorenzo Baraldi, Lorenzo Baraldi, Marcella Cornia, and Rita Cucchiara. 2024. The revolution of multimodal large language models: A survey. In *Findings of the Association for Computational Linguistics: ACL 2024*, pages 13590–13618, Bangkok, Thailand. Association for Computational Linguistics.

Lingjiao Chen, Matei Zaharia, and James Zou. 2023. Frugalgpt: How to use large language models while reducing cost and improving performance. *Preprint*, arXiv:2305.05176.

---

¹³E.g., https://openai.com/api/pricing/
---

<!-- Section 1 -->
<!-- Column 1 -->
Zheng Chu, Jingchang Chen, Qianglong Chen, Weijiang Yu, Tao He, Haotian Wang, Weihua Peng, Ming Liu, Bing Qin, and Ting Liu. 2024. *Navigate through enigmatic labyrinth: a survey of chain of thought reasoning: Advances, frontiers and future.* In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pages 1173–1203, Bangkok, Thailand. Association for Computational Linguistics.

Karl Cobbe, Vineet Kosaraju, Mohammad Bavarian, Jacob Hilton, Reiichiro Nakano, Christopher Hesse, and John Schulman. 2021. Training verifiers to solve math word problems. *Preprint*, arXiv:2110.14168.

DeepSeek-AI, Daya Guo, Dejian Yang, Haowei Zhang, Junxiao Song, Ruoyu Zhang, Runxin Xu, Qihao Zhu, Shirong Ma, Peiyi Wang, Xiao Bi, Xiaokang Zhang, Xingkai Yu, Yu Wu, Z. F. Wu, Zhibin Gou, Zhihong Shao, Zhuoshu Li, Ziyi Gao, Aixin Liu, Bing Xue, Bingxuan Wang, Bochao Wu, Bei Feng, Chengda Lu, Chenggang Zhao, Chengqi Deng, Chenyu Zhang, Chong Ruan, Damai Dai, Deli Chen, Dongjie Ji, Erhang Li, Fangyun Lin, Fucong Dai, Fuli Luo, Guangbo Hao, Guanting Chen, Guowei Li, H. Zhang, Han Bao, Hanwei Xu, Haocheng Wang, Honghui Ding, Huajian Xin, Huazuo Gao, Hui Qu, Hui Li, Jianzong Guo, Jiashi Li, Jiawei Wang, Jingchang Chen, Jingyang Yuan, Junjie Qiu, Junlong Li, J. L. Cai, Jiaqi Ni, Jian Liang, Jin Chen, Kai Dong, Kai Hu, Kaige Gao, Kang Guan, Kexin Huang, Kuai Yu, Lean Wang, Lecong Zhang, Liang Zhao, Litong Wang, Liyue Zhang, Lei Xu, Leyi Xia, Mingchuan Zhang, Minghua Zhang, Minghui Tang, Meng Li, Miaojun Wang, Mingming Li, Ning Tian, Panpan Huang, Peng Zhang, Qiancheng Wang, Qinyu Chen, Qiushi Du, Ruiqi Ge, Ruisong Zhang, Ruizhe Pan, Runji Wang, R. J. Chen, R. L. Jin, Ruyi Chen, Shanghao Lu, Shangyan Zhou, Shanhuang Chen, Shengfeng Ye, Shiyu Wang, Shuiping Yu, Shunfeng Zhou, Shuting Pan, S. S. Li, Shuang Zhou, Shaoqing Wu, Shengfeng Ye, Tao Yun, Tian Pei, Tianyu Sun, T. Wang, Wangding Zeng, Wanjia Zhao, Wen Liu, Wenfeng Liang, Wenjun Gao, Wenqin Yu, Wentao Zhang, W. L. Xiao, Wei An, Xiaodong Liu, Xiaohan Wang, Xiaokang Chen, Xiaotao Nie, Xin Cheng, Xin Liu, Xin Xie, Xingchao Liu, Xinyu Yang, Xinyuan Li, Xuecheng Su, Xuheng Lin, X. Q. Li, Xiangyue Jin, Xiaojin Shen, Xiaosha Chen, Xiaowen Sun, Xiaoxiang Wang, Xinnan Song, Xinyi Zhou, Xianzu Wang, Xinxia Shan, Y. K. Li, Y. Q. Wang, Y. X. Wei, Yang Zhang, Yanhong Xu, Yao Li, Yao Zhao, Yaofeng Sun, Yaohui Wang, Yi Yu, Yichao Zhang, Yifan Shi, Yiliang Xiong, Ying He, Yishi Piao, Yisong Wang, Yixuan Tan, Yiyang Ma, Yiyuan Liu, Yongqiang Guo, Yuan Ou, Yuduan Wang, Yue Gong, Yuheng Zou, Yujia He, Yunfan Xiong, Yuxiang Luo, Yuxiang You, Yuxuan Liu, Yuyang Zhou, Y. X. Zhu, Yanhong Xu, Yanping Huang, Yaohui Li, Yi Zheng, Yuchen Zhu, Yunxian Ma, Ying Tang, Yukun Zha, Yuting Yan, Z. Z. Ren, Zehui Ren, Zhangli Sha, Zhe Fu, Zhean Xu, Zhenda Xie, Zhengyan Zhang, Zhewen Hao, Zhicheng Ma, Zhigang Yan, Zhiyu Wu, Zhihui Gu, Zijia Zhu, Zijun Liu, Zilin Li, Ziwei Xie, Ziyang Song,

<!-- Column 2 -->
Zizheng Pan, Zhen Huang, Zhipeng Xu, Zhongyu Zhang, and Zhen Zhang. 2025. *Deepseek-r1: Incentivizing reasoning capability in llms via reinforcement learning.* *Preprint*, arXiv:2501.12948.

Payal Dhar. 2020. The carbon impact of artificial intelligence.

Abhimanyu Dubey, Abhinav Jauhri, Abhinav Pandey, Abhishek Kadian, Ahmad Al-Dahle, Aiesha Letman, Akhil Mathur, Alan Schelten, Amy Yang, Angela Fan, Anirudh Goyal, Anthony Hartshorn, Aobo Yang, Archi Mitra, Archie Sravankumar, Artem Korenev, Arthur Hinsvark, Arun Rao, Aston Zhang, Aurelien Rodriguez, Austen Gregerson, Ava Spataru, Baptiste Roziere, Bethany Biron, Binh Tang, Bobbie Chern, Charlotte Caucheteux, Chaya Nayak, Chloe Bi, Chris Marra, Chris McConnell, Christian Keller, Christophe Touret, Chunyang Wu, Corinne Wong, Cristian Canton Ferrer, Cyrus Nikolaidis, Damien Allonsius, Daniel Song, Danielle Pintz, Danny Livshits, David Esiobu, Dhruv Choudhary, Dhruv Mahajan, Diego Garcia-Olano, Diego Perino, Dieuwke Hupkes, Egor Lakomkin, Ehab AlBadawy, Elina Lobanova, Emily Dinan, Eric Michael Smith, Filip Radenovic, Frank Zhang, Gabriel Synnaeve, Gabrielle Lee, Georgia Lewis Anderson, Graeme Nail, Gregoire Mialon, Guan Pang, Guillem Cucurell, Hailey Nguyen, Hannah Korevaar, Hu Xu, Hugo Touvron, Iliyan Zarov, Imanol Arrieta Ibarra, Isabel Kloumann, Ishan Misra, Ivan Evtimov, Jade Copet, Jaewon Lee, Jan Geffert, Jana Vranes, Jason Park, Jay Mahadeokar, Jeet Shah, Jelmer van der Linde, Jennifer Billock, Jenny Hong, Jenya Lee, Jeremy Fu, Jianfeng Chi, Jianyu Huang, Jiawen Liu, Jie Wang, Jiecao Yu, Joanna Bitton, Joe Spisak, Jongsoo Park, Joseph Rocca, Joshua Johnstun, Joshua Saxe, Junteng Jia, Kalyan Vasuden Alwala, Kartikeya Upasani, Kate Plawiak, Ke Li, Kenneth Heafield, Kevin Stone, Khalid El-Arini, Krithika Iyer, Kshitiz Malik, Kuen-ley Chiu, Kunal Bhalla, Lauren Rantala-Yeary, Laurens van der Maaten, Lawrence Chen, Liang Tan, Liz Jenkins, Louis Martin, Lovish Madaan, Lubo Malo, Lukas Blecher, Lukas Landzaat, Luke de Oliveira, Madeline Muzzi, Mahesh Pasupuleti, Mannat Singh, Manohar Paluri, Marcin Kardas, Mathew Oldham, Mathieu Rita, Maya Pavlova, Melanie Kambadur, Mike Lewis, Min Si, Mitesh Kumar Singh, Mona Hassan, Naman Goyal, Narjes Torabi, Nikolay Bashlykov, Nikolay Bogoychev, Niladri Chatterji, Olivier Duchenne, Onur Çelebi, Patrick Alrassy, Pengchuan Zhang, Pengwei Li, Petar Vasic, Peter Weng, Prajjwal Bhargava, Pratik Dubal, Praveen Krishnan, Punit Singh Koura, Puxin Xu, Qing He, Qingxiao Dong, Ragavan Srinivasan, Raj Ganapathy, Ramon Calderer, Ricardo Silveira Cabral, Robert Stojnic, Roberta Railean, Rohit Girdhar, Rohit Patel, Romain Sauvestre, Ronnie Polidoro, Roshan Sumbaly, Ross Taylor, Ruan Silva, Rui Hou, Rui Wang, Saghar Hosseini, Sahana Chennabasappa, Sanjay Singh, Sean Bell, Seohyun Sonia Kim, Sergey Edunov, Shaoliang Nie, Sharan Narang, Sharath Raparthy, Sheng Shen, Shengye Wan, Shruti Bhosale, Shun Zhang, Simon Vandenhende, Soumya Batra, Spencer

7
---

Whitman, Sten Sootla, Stephane Collot, Suchin Gururangan, Sydney Borodinsky, Tamar Herman, Tara Fowler, Tarek Sheasha, Thomas Georgiou, Thomas Scialom, Tobias Speckbacher, Todor Mihaylov, Tong Xiao, Ujjwal Karn, Vedanuj Goswami, Vibhor Gupta, Vignesh Ramanathan, Viktor Kerkez, Vincent Gonguet, Virginie Do, Vish Vogeti, Vladan Petrovic, Weiwei Chu, Wenhan Xiong, Wenyin Fu, Whitney Meers, Xavier Martinet, Xiaodong Wang, Xiaoqing Ellen Tan, Xinfeng Xie, Xuchao Jia, Xuewei Wang, Yaelle Goldschlag, Yashesh Gaur, Yasmine Babaei, Yi Wen, Yiwen Song, Yuchen Zhang, Yue Li, Yuning Mao, Zacharie Delpierre Coudert, Zheng Yan, Zhengxing Chen, Zoe Papakipos, Aaditya Singh, Aaron Grattafiori, Abha Jain, Adam Kelsey, Adam Shajnfeld, Adithya Gangidi, Adolfo Victoria, Ahuva Goldstand, Ajay Menon, Ajay Sharma, Alex Boesenberg, Alex Vaughan, Alexei Baevski, Allie Feinstein, Amanda Kallet, Amit Sangani, Anam Yunus, Andrei Lupu, Andres Alvarado, Andrew Caples, Andrew Gu, Andrew Ho, Andrew Poulton, Andrew Ryan, Ankit Ramchandani, Annie Franco, Aparajita Saraf, Arkabandhu Chowdhury, Ashley Gabriel, Ashwin Bharambe, Assaf Eisenman, Azadeh Yazdan, Beau James, Ben Maurer, Benjamin Leonhardi, Bernie Huang, Beth Loyd, Beto De Paola, Bhargavi Paranjape, Bing Liu, Bo Wu, Boyu Ni, Braden Hancock, Bram Wasti, Brandon Spence, Brani Stojkovic, Brian Gamido, Britt Montalvo, Carl Parker, Carly Burton, Catalina Mejia, Changhan Wang, Changkyu Kim, Chao Zhou, Chester Hu, Ching-Hsiang Chu, Chris Cai, Chris Tindal, Christoph Feichtenhofer, Damon Civin, Dana Beaty, Daniel Kreymer, Daniel Li, Danny Wyatt, David Adkins, David Xu, Davide Testuggine, Delia David, Devi Parikh, Diana Liskovich, Didem Foss, Dingkang Wang, Duc Le, Dustin Holland, Edward Dowling, Eissa Jamil, Elaine Montgomery, Eleonora Presani, Emily Hahn, Emily Wood, Erik Brinkman, Esteban Arcaute, Evan Dunbar, Evan Smothers, Fei Sun, Felix Kreuk, Feng Tian, Firat Ozgenel, Francesco Caggioni, Francisco Guzmán, Frank Kanayet, Frank Seide, Gabriela Medina Florez, Gabriella Schwarz, Gada Badeer, Georgia Swee, Gil Halpern, Govind Thattai, Grant Herman, Grigory Sizov, Guangyi, Zhang, Guna Lakshminarayanan, Hamid Shojanazeri, Han Zou, Hannah Wang, Hanwen Zha, Haroun Habeeb, Harrison Rudolph, Helen Suk, Henry Aspegren, Hunter Goldman, Ibrahim Damlaj, Igor Molybog, Igor Tufanov, Irina-Elena Velliche, Itai Gat, Jake Weissman, James Geboski, James Kohli, Japhet Asher, Jean-Baptiste Gaya, Jeff Marcus, Jeff Tang, Jennifer Chan, Jenny Zhen, Jeremy Reizenstein, Jeremy Teboul, Jessica Zhong, Jian Jin, Jingyi Yang, Joe Cummings, Jon Carvill, Jon Shepard, Jonathan McPhie, Jonathan Torres, Josh Ginsburg, Junjie Wang, Kai Wu, Kam Hou U, Karan Saxena, Karthik Prasad, Kartikay Khandelwal, Katayoun Zand, Kathy Matosich, Kaushik Veeraraghavan, Kelly Michelena, Keqian Li, Kun Huang, Kunal Chawla, Kushal Lakhotia, Kyle Huang, Lailin Chen, Lakshya Garg, Lavender A, Leandro Silva, Lee Bell, Lei Zhang, Liangpeng Guo, Licheng Yu, Liron Moshkovich, Luca Wehrstedt, Madian Khabsa, Manav Avalani, Manish Bhatt, Maria Tsimpoukelli, Martynas Mankus, Matan Hasson, Matthew Lennie, Matthias Reso, Maxim Groshev, Maxim Naumov, Maya Lathi, Meghan Keneally, Michael L. Seltzer, Michal Valko, Michelle Restrepo, Mihir Patel, Mik Vyatskov, Mikayel Samvelyan, Mike Clark, Mike Macey, Mike Wang, Miquel Jubert Hermoso, Mo Metanat, Mohammad Rastegari, Munish Bansal, Nandhini Santhanam, Natascha Parks, Natasha White, Navyata Bawa, Nayan Singhal, Nick Egebo, Nicolas Usunier, Nikolay Pavlovich Laptev, Ning Dong, Ning Zhang, Norman Cheng, Oleg Chernoguz, Olivia Hart, Omkar Salpekar, Ozlem Kalinli, Parkin Kent, Parth Parekh, Paul Saab, Pavan Balaji, Pedro Rittner, Philip Bontrager, Pierre Roux, Piotr Dollar, Polina Zvyagina, Prashant Ratanchandani, Pritish Yuvraj, Qian Liang, Rachad Alao, Rachel Rodriguez, Rafi Ayub, Raghotham Murthy, Raghu Nayani, Rahul Mitra, Raymond Li, Rebekkah Hogan, Robin Battey, Rocky Wang, Rohan Maheswari, Russ Howes, Ruty Rinott, Sai Jayesh Bondu, Samyak Datta, Sara Chugh, Sara Hunt, Sargun Dhillon, Sasha Sidorov, Satadru Pan, Saurabh Verma, Seiji Yamamoto, Sharadh Ramaswamy, Shaun Lindsay, Shaun Lindsay, Sheng Feng, Shenghao Lin, Shengxin Cindy Zha, Shiva Shankar, Shuqiang Zhang, Shuqiang Zhang, Sinong Wang, Sneha Agarwal, Soji Sajuyigbe, Soumith Chintala, Stephanie Max, Stephen Chen, Steve Kehoe, Steve Satterfield, Sudarshan Govindaprasad, Sumit Gupta, Sungmin Cho, Sunny Virk, Suraj Subramanian, Sy Choudhury, Sydney Goldman, Tal Remez, Tamar Glaser, Tamara Best, Thilo Kohler, Thomas Robinson, Tianhe Li, Tianjun Zhang, Tim Matthews, Timothy Chou, Tzook Shaked, Varun Vontimitta, Victoria Ajayi, Victoria Montanez, Vijai Mohan, Vinay Satish Kumar, Vishal Mangla, Vitor Albiero, Vlad Ionescu, Vlad Poenaru, Vlad Tiberiu Mihailescu, Vladimir Ivanov, Wei Li, Wenchen Wang, Wenwen Jiang, Wes Bouaziz, Will Constable, Xiaocheng Tang, Xiaofang Wang, Xiaojian Wu, Xiaolan Wang, Xide Xia, Xilun Wu, Xinbo Gao, Yanjun Chen, Ye Hu, Ye Jia, Ye Qi, Yenda Li, Yilin Zhang, Ying Zhang, Yossi Adi, Youngjin Nam, Yu, Wang, Yuchen Hao, Yundi Qian, Yuzi He, Zach Rait, Zachary DeVito, Zef Rosnbrick, Zhaoduo Wen, Zhenyu Yang, and Zhiwei Zhao. 2024. The llama 3 herd of models. *Preprint*, arXiv:2407.21783.

Clémentine Fourrier, Nathan Habib, Alina Lozovskaya, Konrad Szafer, and Thomas Wolf. 2024. Open llm leaderboard v2. https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard.

Leo Gao, Jonathan Tow, Baber Abbasi, Stella Biderman, Sid Black, Anthony DiPofi, Charles Foster, Laurence Golding, Jeffrey Hsu, Alain Le Noac’h, Haonan Li, Kyle McDonell, Niklas Muennighoff, Chris Ociepa, Jason Phang, Laria Reynolds, Hailey Schoelkopf, Aviva Skowron, Lintang Sutawika, Eric Tang, Anish Thite, Ben Wang, Kevin Wang, and Andy Zou. 2023. A framework for few-shot language model evaluation.

Dan Hendrycks, Collin Burns, Steven Basart, Andy Zou, Mantas Mazeika, Dawn Song, and Jacob Stein-
---

<!-- Column 1 -->

hardt. 2021. Measuring massive multitask language understanding. *Proceedings of the International Conference on Learning Representations (ICLR).*

Huiqiang Jiang, Qianhui Wu, Chin-Yew Lin, Yuqing Yang, and Lili Qiu. 2023. LLMLinqua: Compressing prompts for accelerated inference of large language models. In *Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing*, pages 13358–13376, Singapore. Association for Computational Linguistics.

JoongHoon Kim, Sangmin Lee, Seung Hun Han, Saeran Park, Jiyoon Lee, Kiyoon Jeong, and Pilsung Kang. 2023. Which is better? exploring prompting strategy for LLM-based metrics. In *Proceedings of the 4th Workshop on Evaluation and Comparison of NLP Systems*, pages 164–183, Bali, Indonesia. Association for Computational Linguistics.

Donald E. Knuth. 1976. Big omicron and big omega and big theta. *SIGACT News*, 8(2):18–24.

Takeshi Kojima, Shixiang Shane Gu, Machel Reid, Yutaka Matsuo, and Yusuke Iwasawa. 2022. Large language models are zero-shot reasoners. In *Advances in Neural Information Processing Systems*.

Seyed Iman Mirzadeh, Keivan Alizadeh, Hooman Shahrokhi, Oncel Tuzel, Samy Bengio, and Mehrdad Farajtabar. 2025. GSM-symbolic: Understanding the limitations of mathematical reasoning in large language models. In *The Thirteenth International Conference on Learning Representations*.

Jesse Mu, Xiang Lisa Li, and Noah Goodman. 2023. Learning to compress prompts with gist tokens. In *Thirty-seventh Conference on Neural Information Processing Systems*.

Sania Nayab, Giulio Rossolini, Giorgio Buttazzo, Nicolamaria Manes, and Fabrizio Giacomelli. 2024. Concise thoughts: Impact of output length on llm reasoning and cost. *Preprint*, arXiv:2407.19825.

Qwen, An Yang, Baosong Yang, Beichen Zhang, Binyuan Hui, Bo Zheng, Bowen Yu, Chengyuan Li, Dayiheng Liu, Fei Huang, Haoran Wei, Huan Lin, Jian Yang, Jianhong Tu, Jianwei Zhang, Jianxin Yang, Jiaxi Yang, Jingren Zhou, Junyang Lin, Kai Dang, Keming Lu, Keqin Bao, Kexin Yang, Le Yu, Mei Li, Mingfeng Xue, Pei Zhang, Qin Zhu, Rui Men, Runji Lin, Tianhao Li, Tianyi Tang, Tingyu Xia, Xingzhang Ren, Xuancheng Ren, Yang Fan, Yang Su, Yichang Zhang, Yu Wan, Yuqiong Liu, Zeyu Cui, Zhenru Zhang, and Zihan Qiu. 2025. Qwen2.5 technical report. *Preprint*, arXiv:2412.15115.

<!-- Column 2 -->

Matthew Renze and Erhan Guven. 2024. The benefits of a concise chain of thought on problem-solving in large language models. *Preprint*, arXiv:2401.05618.

Abel Salinas and Fred Morstatter. 2024. The butterfly effect of altering prompts: How small changes and jailbreaks affect large language model performance. In *Findings of the Association for Computational Linguistics: ACL 2024*, pages 4629–4651, Bangkok, Thailand. Association for Computational Linguistics.

Roy Schwartz, Jesse Dodge, Noah A. Smith, and Oren Etzioni. 2020. Green ai. *Commun. ACM*, 63(12):54–63.

Bilgehan Sel, Ahmad Tawaha, Vanshaj Khattar, Ruoxi Jia, and Ming Jin. 2024. Algorithm of thoughts: Enhancing exploration of ideas in large language models. In *Proceedings of the 41st International Conference on Machine Learning*, volume 235 of *Proceedings of Machine Learning Research*, pages 44136–44189. PMLR.

Sonish Sivarajkumar, Mark Kelley, Alyssa Samolyk-Mazzanti, Shyam Visweswaran, and Yanshan Wang. 2024. An empirical evaluation of prompting strategies for large language models in zero-shot clinical natural language processing: Algorithm development and validation study. *JMIR Med Inform*, 12:e55318.

Aarohi Srivastava, Abhinav Rastogi, Abhishek Rao, Abu Awal Md Shoeb, Abubakar Abid, Adam Fisch, Adam R. Brown, Adam Santoro, Aditya Gupta, Adrià Garriga-Alonso, Agnieszka Kluska, Aitor Lewkowycz, Akshat Agarwal, Alethea Power, Alex Ray, Alex Warstadt, Alexander W. Kocurek, Ali Safaya, Ali Tazarv, Alice Xiang, Alicia Parrish, Allen Nie, Aman Hussain, Amanda Askell, Amanda Dsouza, Ambrose Slone, Ameet Rahane, Anantharaman S. Iyer, Anders Johan Andreassen, Andrea Madotto, Andrea Santilli, Andreas Stuhlmüller, Andrew M. Dai, Andrew La, Andrew Kyle Lampinen, Andy Zou, Angela Jiang, Angelica Chen, Anh Vuong, Animesh Gupta, Anna Gottardi, Antonio Norelli, Anu Venkatesh, Arash Gholamidavoodi, Arfa Tabassum, Arul Menezes, Arun Kirubarajan, Asher Mullokandov, Ashish Sabharwal, Austin Herrick, Avia Efrat, Aykut Erdem, Ayla Karakas, B. Ryan Roberts, Bao Sheng Loe, Barret Zoph, Bartłomiej Bojanowski, Batuhan Özyurt, Behnam Hedayatnia, Behnam Neyshabur, Benjamin Inden, Benno Stein, Berk Ekmekci, Bill Yuchen Lin, Blake Howald, Bryan Orinion, Cameron Diao, Cameron Dour, Catherine Stinson, Cedrick Argueta, Cesar Ferri, Chandan Singh, Charles Rathkopf, Chenlin Meng, Chitta Baral, Chiyu Wu, Chris Callison-Burch, Christopher Waites, Christian Voigt, Christopher D Manning, Christopher Potts, Cindy Ramirez, Clara E. Rivera, Clemencia Siro, Colin Raffel, Courtney Ashcraft, Cristina Garbacea, Damien Sileo, Dan Garrette, Dan Hendrycks, Dan Kilman, Dan Roth, C. Daniel Freeman, Daniel Khashabi, Daniel Levy, Daniel Moseguí González, Danielle Perszyk, Danny Hernandez, Danqi Chen, Daphne Ippolito, Dar Gilboa, David Dohan, David Drakard, David Jurgens, Debajyoti Datta, Deep Ganguli, Denis Emelin, Denis Kleyko, Deniz Yuret, Derek Chen, Derek Tam, DieuWke Hupkes, Diganta Misra, Dilyar Buzan, Dimitri Coelho Mollo, Diyi Yang, Dong-Ho Lee, Dylan Schrader, Ekaterina Shutova, Ekin Dogus Cubuk, Elad Segal, Eleanor Hagerman, Elizabeth Barnes, Elizabeth Donoway, Ellie Pavlick, Emanuele Rodolà, Emma Lam, Eric Chu, Eric Tang, Erkut


---

Erdem, Ernie Chang, Ethan A Chi, Ethan Dyer, Ethan Jerzak, Ethan Kim, Eunice Engefu Manyasi, Evgenii Zheltonozhskii, Fanyue Xia, Fatemeh Siar, Fernando Martínez-Plumed, Francesca Happé, François Chollet, Frieda Rong, Gaurav Mishra, Genta Indra Winata, Gerard de Melo, Germán Kruszewski, Giambattista Parascandolo, Giorgio Mariani, Gloria Xinyue Wang, Gonzalo Jaimovitch-Lopez, Gregor Betz, Guy Gur-Ari, Hana Galijasevic, Hannah Kim, Hannah Rashkin, Hannaneh Hajishirzi, Harsh Mehta, Hayden Bogar, Henry Francis Anthony Shevlin, Hinrich Schuetze, Hiromu Yakura, Hongming Zhang, Hugh Mee Wong, Ian Ng, Isaac Noble, Jaap Jumelet, Jack Geissinger, Jackson Kernion, Jacob Hilton, Jaehoon Lee, Jaime Fernández Fisac, James B Simon, James Koppel, James Zheng, James Zou, Jan Kocon, Jana Thompson, Janelle Wingfield, Jared Kaplan, Jarema Radom, Jascha Sohl-Dickstein, Jason Phang, Jason Wei, Jason Yosinski, Jekaterina Novikova, Jelle Bosscher, Jennifer Marsh, Jeremy Kim, Jeroen Taal, Jesse Engel, Jesujoba Alabi, Jiacheng Xu, Jiaming Song, Jillian Tang, Joan Waweru, John Burden, John Miller, John U. Balis, Jonathan Batchelder, Jonathan Berant, Jörg Frohberg, Jos Rozen, Jose Hernandez-Orallo, Joseph Boudeman, Joseph Guerr, Joseph Jones, Joshua B. Tenenbaum, Joshua S. Rule, Joyce Chua, Kamil Kanclerz, Karen Livescu, Karl Krauth, Karthik Gopalakrishnan, Katerina Ignatyeva, Katja Markert, Kaustubh Dhole, Kevin Gimpel, Kevin Omondi, Kory Wallace Mathewson, Kristen Chiafullo, Ksenia Shkaruta, Kumar Shridhar, Kyle McDonell, Kyle Richardson, Laria Reynolds, Leo Gao, Li Zhang, Liam Dugan, Lianhui Qin, Lidia Contreras-Ochando, Louis-Philippe Morency, Luca Moschella, Lucas Lam, Lucy Noble, Ludwig Schmidt, Luheng He, Luis Oliveros-Colón, Luke Metz, Lütfi Kerem Senel, Maarten Bosma, Maarten Sap, Maartje Ter Hoeve, Maheen Farooqi, Manaal Faruqui, Mantas Mazeika, Marco Baturan, Marco Marelli, Marco Maru, Maria Jose Ramirez-Quintana, Marie Tolkiehn, Mario Giulianelli, Martha Lewis, Martin Potthast, Matthew L Leavitt, Matthias Hagen, Mátyás Schubert, Medina Orduna Baitemirova, Melody Arnaud, Melvin McElrath, Michael Andrew Yee, Michael Cohen, Michael Gu, Michael Ivanitskiy, Michael Starritt, Michael Strube, Michał Swędrowski, Michele Bevilacqua, Michihiro Yasunaga, Mihir Kale, Mike Cain, Mimee Xu, Mirac Suzgun, Mitch Walker, Mo Tiwari, Mohit Bansal, Moin Aminnaseri, Mor Geva, Mozhdeh Gheini, Mukund Varma T, Nanyun Peng, Nathan Andrew Chi, Nayeon Lee, Neta Gur-Ari Krakover, Nicholas Cameron, Nicholas Roberts, Nick Doiron, Nicole Martinez, Nikita Nangia, Niklas Deckers, Niklas Muennighoff, Nitish Shirish Keskar, Niveditha S. Iyer, Noah Constant, Noah Fiedel, Nuan Wen, Oliver Zhang, Omar Agha, Omar Elbaghdadi, Omer Levy, Owain Evans, Pablo Antonio Moreno Casares, Parth Doshi, Pascale Fung, Paul Pu Liang, Paul Vicol, Pegah Alipoormolabashi, Peiyuan Liao, Percy Liang, Peter W Chang, Peter Eckersley, Phu Mon Htut, Pinyu Hwang, Piotr Miłkowski, Piyush Patil, Pouya Pezeshkpour, Priti Oli, Qiaozhu Mei, Qing Lyu, Qinlang Chen, Rabin Banjade, Rachel Etta Rudolph, Raefer Gabriel, Rahel Habacker, Ramon Risco, Raphaël Millière, Rhythm Garg, Richard Barnes, Rif A. Saurous, Riku Arakawa, Robbe Raymaekers, Robert Frank, Rohan Sikand, Roman Novak, Roman Sitelew, Ronan Le Bras, Rosanne Liu, Rowan Jacobs, Rui Zhang, Russ Salakhutdinov, Ryan Andrew Chi, Seungjae Ryan Lee, Ryan Stovall, Ryan Teehan, Rylan Yang, Sahib Singh, Saif M. Mohammad, Sajant Anand, Sam Dillavou, Sam Shleifer, Sam Wiseman, Samuel Gruetter, Samuel R. Bowman, Samuel Stern Schoenholz, Sanghyun Han, Sanjeev Kwatra, Sarah A. Rous, Sarik Ghazarian, Sayan Ghosh, Sean Casey, Sebastian Bischoff, Sebastian Gehrmann, Sebastian Schuster, Sepideh Sadeghi, Shadi Hamdan, Sharon Zhou, Shashank Srivastava, Sherry Shi, Shikhar Singh, Shima Asaadi, Shixiang Shane Gu, Shubh Pachchigar, Shubham Toshniwal, Shyam Upadhyay, Shyamolima Shammie Debnath, Siamak Shakeri, Simon Thormeyer, Simone Melzi, Siva Reddy, Sneha Priscilla Makini, Soo-Hwan Lee, Spencer Torene, Sriharsha Hatwar, Stanislas Dehaene, Stefan Divic, Stefano Ermon, Stella Biderman, Stephanie Lin, Stephen Prasad, Steven Piantadosi, Stuart Shieber, Summer Mishergi, Svetlana Kiritchenko, Swaroop Mishra, Tal Linzen, Tal Schuster, Tao Li, Tao Yu, Tariq Ali, Tatsunori Hashimoto, Te-Lin Wu, Théo Desbordes, Theodore Rothschild, Thomas Phan, Tianle Wang, Tiberius Nkinyili, Timo Schick, Timofei Kornev, Titus Tunduny, Tobias Gerstenberg, Trenton Chang, Trishala Neeraj, Tushar Khot, Tyler Shultz, Uri Shaham, Vedant Misra, Vera Demberg, Victoria Nyamai, Vikas Raunak, Vinay Venkatesh Ramasesh, vinay uday prabhu, Vishakh Padmakumar, Vivek Srikumar, William Fedus, William Saunders, William Zhang, Wout Vossen, Xiang Ren, Xiaoyu Tong, Xinran Zhao, Xinyi Wu, Xudong Shen, Yadollah Yaghoobzadeh, Yair Lakretz, Yangqiu Song, Yasaman Bahri, Yejin Choi, Yichi Yang, Sophie Hao, Yifu Chen, Yonatan Belinkov, Yu Hou, Yufang Hou, Yuntao Bai, Zachary Seid, Zhuoye Zhao, Zijian Wang, Zijie J. Wang, Zirui Wang, and Ziyi Wu. 2023. Beyond the imitation game: Quantifying and extrapolating the capabilities of language models. Transactions on Machine Learning Research. Featured Certification.

Mirac Suzgun, Nathan Scales, Nathanael Schärli, Sebastian Gehrmann, Yi Tay, Hyung Won Chung, Aakanksha Chowdhery, Quoc Le, Ed Chi, Denny Zhou, and Jason Wei. 2023. Challenging BIG-bench tasks and whether chain-of-thought can solve them. In Findings of the Association for Computational Linguistics: ACL 2023, pages 13003–13051, Toronto, Canada. Association for Computational Linguistics.

Shubham Vatsal and Harsh Dubey. 2024. A survey of prompt engineering methods in large language models for different nlp tasks. Preprint, arXiv:2407.12994.

Zhongwei Wan, Xin Wang, Che Liu, Samiul Alam, Yu Zheng, Jiachen Liu, Zhongnan Qu, Shen Yan, Yi Zhu, Quanlu Zhang, Mosharaf Chowdhury, and
---

Mi Zhang. 2024. Efficient large language models: A survey. *Transactions on Machine Learning Research*. Survey Certification.

Lei Wang, Wanyu Xu, Yihuai Lan, Zhiqiang Hu, Yunshi Lan, Roy Ka-Wei Lee, and Ee-Peng Lim. 2023a. Plan-and-solve prompting: Improving zero-shot chain-of-thought reasoning by large language models. In *Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pages 2609–2634, Toronto, Canada. Association for Computational Linguistics.

Xuezhi Wang, Jason Wei, Dale Schuurmans, Quoc V Le, Ed H. Chi, Sharan Narang, Aakanksha Chowdhery, and Denny Zhou. 2023b. Self-consistency improves chain of thought reasoning in language models. In *The Eleventh International Conference on Learning Representations*.

Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, brian ichter, Fei Xia, Ed H. Chi, Quoc V Le, and Denny Zhou. 2022. Chain of thought prompting elicits reasoning in large language models. In *Advances in Neural Information Processing Systems*.

Jules White, Quchen Fu, Sam Hays, Michael Sandborn, Carlos Olea, Henry Gilbert, Ashraf Elnashar, Jesse Spencer-Smith, and Douglas C. Schmidt. 2023. A prompt pattern catalog to enhance prompt engineering with chatgpt. In *Proceedings of the 30th Conference on Pattern Languages of Programs*, PLoP ’23, USA. The Hillside Group.

Carole-Jean Wu, Ramya Raghavendra, Udit Gupta, Bilge Acun, Newsha Ardalani, Kiwan Maeng, Gloria Chang, Fiona Aga, Jinshi Huang, Charles Bai, et al. 2022. Sustainable ai: Environmental implications, challenges and opportunities. *Proceedings of Machine Learning and Systems*, 4:795–813.

Junda Wu, Zhehao Zhang, Yu Xia, Xintong Li, Zhaoyang Xia, Aaron Chang, Tong Yu, Sungchul Kim, Ryan A. Rossi, Ruiyi Zhang, Subrata Mitra, Dimitris N. Metaxas, Lina Yao, Jingbo Shang, and Julian McAuley. 2024. Visual prompting in multimodal large language models: A survey. *Preprint*, arXiv:2409.15310.

Shunyu Yao, Dian Yu, Jeffrey Zhao, Izhak Shafran, Thomas L. Griffiths, Yuan Cao, and Karthik R Narasimhan. 2023. Tree of thoughts: Deliberate problem solving with large language models. In *Thirty-seventh Conference on Neural Information Processing Systems*.

Shukang Yin, Chaoyou Fu, Sirui Zhao, Ke Li, Xing Sun, Tong Xu, and Enhong Chen. 2024. A survey on multimodal large language models. *National Science Review*, 11(12):nwae403.

Qingchen Yu, Zifan Zheng, Shichao Song, Zhiyu Li, Feiyu Xiong, Bo Tang, and Ding Chen. 2025. xfinder: Large language models as automated evaluators for reliable evaluation. In *The Thirteenth International Conference on Learning Representations*.

Denny Zhou, Nathanael Schärli, Le Hou, Jason Wei, Nathan Scales, Xuezhi Wang, Dale Schuurmans, Claire Cui, Olivier Bousquet, Quoc V Le, and Ed H. Chi. 2023. Least-to-most prompting enables complex reasoning in large language models. In *The Eleventh International Conference on Learning Representations*.

---

## A Big-O\(_{tok}\) Analysis

We provide an expanded token complexity analysis for each prompting strategy examined in the main text in Table 3. We define the minimally viable IO pair (MVIO) for a given benchmark question to be the full text of the question and the minimum amount of text to convey the answer (e.g., Question: "How many days are there in a week?"; Answer: "7"). All other prompting strategies that incur additive adjustments to the input or output (e.g., the natural language thinking induced by CoT’s "Think step by step" (Wei et al., 2022)) are treated as constant overheads on top of the MVIO, which are represented by Greek letters.

Table 4 shows theoretical token usage ratios based on Big-O\(_{tok}\). The expected token usage ratios used in Table 2 are based on these, averaged across the 3 benchmarks.

We include examples of Big-O\(_{tok}\) derivations for each prompting strategy examined in the main text in Figure 2.

## B Interpreting Token Cost

Although we include a thorough example of using TC for prompting strategy analysis, we seek to provide an expanded discussion on its interpretation here. For brevity, in the main text we state that, generally, low TC can be thought of as more efficient and high TC as less efficient. In most instances, this will hold true; however, there are some plausible edge cases that deserve consideration.

### B.1 Average TC

One such edge case is exploiting extremely low token usages to achieve low average TC. For example, consider a multiple-choice benchmark with four options: (A), (B), (C), and (D). Assuming uniform distribution across the possible answers, a prompting strategy that would yield 25% accuracy (assuming the LLM could consistently produce the correct output) might be: "Output (B)." At approximately 4 combined input and output tokens, such a prompting strategy would achieve an average TC of 0.16 \(\frac{t}{p}\), a value much lower than any of our observed values in Table 6. This demonstrates the
---

| Prompting Strategy         | Big-O_tok              | Token Complexity                    | Variables                                                                 | Values Used in Original Paper      |
|----------------------------|-----------------------|-----------------------------------|---------------------------------------------------------------------------|-----------------------------------|
| MVIO                       | \(O(1)\)              | 1                                 |                                                                           |                                   |
| Vanilla IO                 | \(O(1)\)              | \(1 + \psi\)                      |                                                                           |                                   |
| Zeroshot CoT               | \(O(1)\)              | \(1 + \alpha\)                    |                                                                           |                                   |
| (Kojima et al., 2022)      |                       |                                   |                                                                           |                                   |
| Vanilla Fewshot            | \(O(k)\)              | \(1 + k\)                        | \(k\): k-shot exemplars                                                   | k=0, 1, 10-100                   |
| (Brown et al., 2020)       |                       |                                   |                                                                           |                                   |
| Fewshot CoT                | \(O(k)\)              | \(1 + \alpha + k + k\alpha\)      | \(k\): k-shot exemplars                                                   | k=8                               |
| (Wei et al., 2022)         |                       |                                   |                                                                           |                                   |
| CoT-SC                     | \(O(pk)\)             | \(p(1 + \alpha + k + k\alpha)\)   | \(k\): k-shot exemplars; \(p\): sampled chains                           | k=4-8; p=40                      |
| (Wang et al., 2023b)       |                       |                                   |                                                                           |                                   |

Table 3: The theoretical token complexities for various prompting strategies. Greek letters represent the overhead associated with an IO pair (assumed constant per prompting strategy) and Roman letters represent variables.

<!-- Section 1 -->
<!-- Column 1 -->

**The minimum text required to communicate the question and answer.**

1: Minimally viable text for **the question** + *answer*

```
∴
Token Complexity: T0 = 1
Big-O_tok: O_tok(1)
```

(a) MVIO

> "The core idea of our method is simple...: add *Let's think step by step*, or a [sic] similar text...to extract step-by-step reasoning."

\(\alpha\): the **"trigger prompt"** + the *elicited reasoning* (_treated as constant overhead_)  
1: Minimally viable IO (question + answer)

```
∴
Token Complexity: T0 = 1 + α
Big-O_tok: O_tok(1)
```

(c) Zeroshot CoT

> "Our proposed approach is to augment **each exemplar in few-shot prompting with a chain of thought for an associated answer.**"

\(k\): **Number of fewshot examples**  
\(\alpha\): Reasoning overhead  
1: Minimally viable IO

```
∴
Token Complexity: T(k) = 1 + α + k + kα
Big-O_tok: O_tok(k)
```

(e) Fewshot CoT

<!-- Column 2 -->

**The minimum text required to communicate the question and the generated output.**

1: Minimally viable text for the question  
\(\psi\): LLM-generated output

```
∴
Token Complexity: T0 = 1 + ψ
Big-O_tok: O_tok(1)
```

(b) Vanilla IO

> "[F]ew-shot works by **giving K examples of context and completion, and then one final example of context, with the model expected to provide the completion.**"

1: The **question** and the **answer** (assumed MVIO)  
\(k\): Number of fewshot examples (in the form of MVIO)

```
∴
Token Complexity: T(k) = 1 + k
Big-O_tok: O_tok(k)
```

(d) Vanilla Fewshot

> "We first **prompt the language model with chain-of-thought prompting**, then…generate a diverse set of reasoning paths."

\[
\begin{cases}
k: \text{Number of fewshot examples} \\
\alpha: \text{Reasoning overhead} \\
1: \text{Minimally viable IO} \\
p: \text{Number of generated reasoning paths}
\end{cases}
\]

```
∴
Token Complexity: T(p,k) = p(1 + α + k + kα)
Big-O_tok: O_tok(pk)
```

(f) CoT-SC

Figure 2: Sample derivations of Big-O_tok. The textual descriptions in each figure are drawn from the following sources: (c) (Kojima et al., 2022); (d) (Brown et al., 2020); (e) (Wei et al., 2022); (f) (Wang et al., 2023b). Note that for (d), the fewshot examples are equivalent to the MVIO and we make the assumption that the LLM follows that pattern.
---

| Prompting Strategy | Token Usage Growth Rate |     |     |
|--------------------|-------------------------|-----|-----|
|                    | BBH                     | GSM8K | MMLU |
| Vanilla IO         | 1                       | 1   | 1   |
| CoT Zeroshot      | 1                       | 1   | 1   |
| Vanilla Fewshot    | 3                       | 8   | 4   |
| Fewshot CoT        | 3                       | 8   | 4   |
| CoT-SC₅           | 15                      | 40  | 20  |
| CoT-SC₁₀          | 30                      | 80  | 40  |

Table 4: The token usage growth rate over MVIO per prompting strategy, derived from Table 1 using the variables used in our experiments.

need to test prompting strategies for generalizability.

## B.2 Marginal TC

For marginal TC, there are additional edge cases to consider. The formula for calculating marginal TC,

\[
\frac{num\ tokens_2 - num\ tokens_1}{accuracy_2 - accuracy_1}
\]

where \(num\ tokens_2 >= num\ tokens_1\), allows for negative values. Despite being "low," a negative marginal TC value indicates extreme inefficiency since the prompting strategy will have consumed more tokens to achieve lower accuracy.

In the unlikely event that \(num\ tokens_2 == num\ tokens_1\), marginal TC will not provide useful information. The more efficient prompting strategy would, in that case, be the one that attained higher accuracy. Similarly, if \(accuracy_2 == accuracy_1\), marginal TC cannot be calculated, but the prompting strategy that consumed fewer tokens can be considered more efficient.

# C Empirical Evaluation Details

## C.1 Detailed Results

We provide detailed results from our experiments in Table 6. Note that the results presented for each prompting strategy, model, and benchmark combination are from a single execution with the number of samples noted in Table 9.

We removed empty outputs and outputs more than four standard deviations from the mean (e.g., instances where the LLM generated a looping output) from our token usage statistics. Such erroneous outputs were surprisingly common for Llama 3.1 8B Instruct. Details of the number of outputs removed from consideration are detailed in Table 5.

## C.2 Additional Observations

While our experiments were simple, we made a number of interesting observations that may warrant further analysis in future work.

The initial motivation behind fewshot prompting strategies was to define a pattern that the LLM would then follow in its answer (Brown et al., 2020; Wei et al., 2022). For Fewshot CoT, this pattern included a reasoning chain that led to the right answer (Wei et al., 2022). Now that LLMs are more capable and often aligned with human preferences after training, their default response to a question is to explain their reasoning before providing a response. This results in high output token usage even for Vanilla IO and Zeroshot CoT. Interestingly, **the reasoning chains (averaged, per benchmark) that the LLMs produced for Zeroshot CoT were longer in every instance than the ones produced for Fewshot CoT**, in some cases more than twice as long. Nonetheless, Fewshot CoT yielded accuracy improvements for nearly every benchmark. This supports the idea that the in-context learning of correct reasoning chains does positively influence the correctness of the generated reasoning chain, even if the LLM’s default output is constrained.

That trend does not apply to Vanilla IO and Vanilla Fewshot, however. While Vanilla Fewshot outperforms Vanilla IO in almost every benchmark, the output token usage is less in most instances. This is likely caused by the pattern that is matched during Vanilla Fewshot, where the example outputs are the minimum number of tokens to convey the answer (e.g., for multiple-choice: "(A)").

We also observed how the quality of the fewshot reasoning chains provided as a part of Fewshot CoT affected performance. While Fewshot CoT yielded modest accuracy gains over Zeroshot CoT for BBH (4.6%) and GSM8K (6.3%), it actually registered a 0.9% accuracy *loss* on MMLU. This prompted an investigation into the CoT fewshot exemplars included in LM Evaluation Harness (Gao et al., 2023). The reasoning chains were significantly shorter than for the other two benchmarks. Interestingly, recent work on using concise reasoning chains, such as Constrained-CoT (Nayab et al., 2024) and Concise-CoT (Renze and Guven, 2024), has demonstrated performance improvements from shorter chains of thought. An potentially insightful future work could explore how the form and content of intentionally concise chains of thought
---

<transcription_table>
**Table 5: Percentage of Total IO Pairs Excluded**

| Model                 | Benchmark | Vanilla IO | Vanilla Fewshot | Zeroshot CoT | Fewshot CoT | CoT-SCs | CoT-SC₁₀ |
|-----------------------|-----------|------------|-----------------|--------------|-------------|---------|----------|
| Llama 3.1 8B Instruct | BBH       | 2.53       | 8.59            | 2.90         | 5.04        | 4.09    | 4.00     |
|                       | GSM8K     | 0.68       | 1.14            | 0.76         | 0.91        | 1.27    | 1.28     |
|                       | MMLU      | 1.18       | 1.76            | 1.89         | 2.35        | 1.89    | 1.93     |
| Qwen 2.5 14B Instruct | BBH       | 0.29       | 0.12            | 0.23         | 0.49        | 0.24    | 0.19     |
|                       | GSM8K     | 0.30       | 0.45            | 0.23         | 0.23        | 0.36    | 0.09     |
|                       | MMLU      | 0.07       | 0.65            | 0.20         | 0.46        | 0.20    | 0.38     |
| Qwen 2.5 32B Instruct | BBH       | 0.22       | 0.09            | 0.26         | 0.29        | 0.16    | 0.10     |
|                       | GSM8K     | 0.00       | 0.00            | 0.08         | 0.38        | 0.18    | 0.13     |
|                       | MMLU      | 0.20       | 0.46            | 0.07         | 0.07        | 0.10    | 0.11     |

<transcription_json>
{
  "table_type": "data_table",
  "title": "Percentage of Total IO Pairs Excluded",
  "columns": [
    "Model",
    "Benchmark",
    "Vanilla IO",
    "Vanilla Fewshot",
    "Zeroshot CoT",
    "Fewshot CoT",
    "CoT-SCs",
    "CoT-SC₁₀"
  ],
  "data": [
    {"Model": "Llama 3.1 8B Instruct", "Benchmark": "BBH", "Vanilla IO": 2.53, "Vanilla Fewshot": 8.59, "Zeroshot CoT": 2.90, "Fewshot CoT": 5.04, "CoT-SCs": 4.09, "CoT-SC₁₀": 4.00},
    {"Model": "Llama 3.1 8B Instruct", "Benchmark": "GSM8K", "Vanilla IO": 0.68, "Vanilla Fewshot": 1.14, "Zeroshot CoT": 0.76, "Fewshot CoT": 0.91, "CoT-SCs": 1.27, "CoT-SC₁₀": 1.28},
    {"Model": "Llama 3.1 8B Instruct", "Benchmark": "MMLU", "Vanilla IO": 1.18, "Vanilla Fewshot": 1.76, "Zeroshot CoT": 1.89, "Fewshot CoT": 2.35, "CoT-SCs": 1.89, "CoT-SC₁₀": 1.93},
    {"Model": "Qwen 2.5 14B Instruct", "Benchmark": "BBH", "Vanilla IO": 0.29, "Vanilla Fewshot": 0.12, "Zeroshot CoT": 0.23, "Fewshot CoT": 0.49, "CoT-SCs": 0.24, "CoT-SC₁₀": 0.19},
    {"Model": "Qwen 2.5 14B Instruct", "Benchmark": "GSM8K", "Vanilla IO": 0.30, "Vanilla Fewshot": 0.45, "Zeroshot CoT": 0.23, "Fewshot CoT": 0.23, "CoT-SCs": 0.36, "CoT-SC₁₀": 0.09},
    {"Model": "Qwen 2.5 14B Instruct", "Benchmark": "MMLU", "Vanilla IO": 0.07, "Vanilla Fewshot": 0.65, "Zeroshot CoT": 0.20, "Fewshot CoT": 0.46, "CoT-SCs": 0.20, "CoT-SC₁₀": 0.38},
    {"Model": "Qwen 2.5 32B Instruct", "Benchmark": "BBH", "Vanilla IO": 0.22, "Vanilla Fewshot": 0.09, "Zeroshot CoT": 0.26, "Fewshot CoT": 0.29, "CoT-SCs": 0.16, "CoT-SC₁₀": 0.10},
    {"Model": "Qwen 2.5 32B Instruct", "Benchmark": "GSM8K", "Vanilla IO": 0.00, "Vanilla Fewshot": 0.00, "Zeroshot CoT": 0.08, "Fewshot CoT": 0.38, "CoT-SCs": 0.18, "CoT-SC₁₀": 0.13},
    {"Model": "Qwen 2.5 32B Instruct", "Benchmark": "MMLU", "Vanilla IO": 0.20, "Vanilla Fewshot": 0.46, "Zeroshot CoT": 0.07, "Fewshot CoT": 0.07, "CoT-SCs": 0.10, "CoT-SC₁₀": 0.11}
  ]
}
</transcription_json>

<transcription_notes>
- The table shows the percentage of total IO pairs removed from token usage statistics.
- Pairs were removed if the output was empty or the length of the output was more than 4 standard deviations from the mean.
- Models and benchmarks are listed in rows.
- Columns display different prompting or chain-of-thought methods used.
- CoT-SCs and CoT-SC₁₀ refer to different chain-of-thought configurations.
</transcription_notes>
</transcription_table>

---

influence LLM performance to explain this discrepancy.

## C.3 Cost Estimates for Commercial Models

The cost estimates found in Table 7 are derived from the pricing pages for Anthropic¹⁴ and OpenAI¹⁵, accessed on January 31, 2025. We do not include the effects of prompt caching.

## C.4 Reproducibility

All results¹⁶, as produced by LM Evaluation Harness, (e.g., LLM inputs and outputs, hyperparameters, runtimes, model configurations, etc.) are found at the following URL: https://drive.google.com/file/d/1RsrzYUlrSuYzj43LRk33X2-Nru-7nG6y/view?usp=sharing.

All code used to run the evaluations for this paper is found at the following GitHub repository: https://github.com/Sypherd/lm-evaluation-harness/tree/reproduce-paper-results. Although we used LM Evaluation Harness, we link our fork¹⁷ as significant bug fixes had to be made to get the framework to function as expected. Despite the bugs we encountered, we encourage others to support this open-source project that promotes reproducible results for LLM projects.

¹⁴ https://anthropic.com/pricing#anthropic-api  
¹⁵ https://openai.com/api/pricing/  
¹⁶ Provided under the CC-BY-4.0 license.  
¹⁷ Under the same MIT license as LM Evaluation Harness.

## C.5 Configurations

### C.5.1 Models

We include details of model configurations in Table 8. All models were sourced from Hugging Face¹⁸. Where required, the authors complied with the necessary terms and conditions for gated models.

### C.5.2 Benchmarks

We include the benchmark configurations used for our experiments in Table 9. The underlying datasets for BBH, GSM8K, and MMLU were sourced from Hugging Face¹⁹. While the fewshot examples for BBH were drawn from the same split used for evaluation, care was taken to ensure that the fewshot examples did not overlap with the target question.

We note in the main text that we selected general-purpose LLM benchmarks for our experiments but recognize that GSM8K could be seen as targeted towards the math domain. While it is true that GSM8K is composed of questions that require basic math, the reasoning capabilities and basic world knowledge it probes are generally applicable. The focus of the benchmark is "properly interpreting a question and reasoning through the steps to solve it" (Cobbe et al., 2021), not to evaluate advanced math skills. We believe this justifies GSM8K's inclusion as a general-purpose benchmark.

We rely on the steps taken by the authors in creating BBH (Suzgun et al., 2023; Srivastava et al., 2023), GSM8K (Cobbe et al., 2021), and MMLU (Hendrycks et al., 2021) to ensure ethical dataset creation, including the mitigation of bias, offen-

¹⁸ https://huggingface.co/models  
¹⁹ https://huggingface.co/datasets  

14
---

<transcription_table>
**Table 6: Detailed results from the empirical evaluation described in Section 3.2.**

|                   | Strategy       | Avg. Tokens_in | Avg. Tokens_out | Avg. Tokens_total | Acc.* | Std. Error | Average TC |
|-------------------|----------------|----------------|-----------------|-------------------|-------|------------|------------|
| **Llama 3.1 BB Instruct** | **BBH**        |                |                 |                   |       |            |            |
|                   | Vanilla IO     | 172            | 221             | 393               | 51.1  | 0.56       | 7.70       |
|                   | Vanilla 3-shot | 420            | 226             | 646               | 35.4  | 0.54       | 18.28      |
|                   | Zeroshot CoT   | 178            | 351             | 530               | 63.2  | 0.55       | 8.38       |
|                   | 3-shot CoT     | 876            | 335             | 1212              | 70.5  | 0.51       | 17.20      |
|                   | CoT-SC₅        | 4378           | 1089            | 5468              | 72.7  | 0.50       | 75.19      |
|                   | CoT-SC₁₀       | 8758           | 2177            | 10935             | 73.1  | 0.50       | 149.58     |
|                   | **GSM8K**      |                |                 |                   |       |            |            |
|                   | Vanilla IO     | 122            | 162             | 284               | 77.3  | 1.15       | 3.68       |
|                   | Vanilla 8-shot | 639            | 147             | 787               | 79.3  | 1.12       | 9.93       |
|                   | Zeroshot CoT   | 126            | 203             | 330               | 75.5  | 1.18       | 4.37       |
|                   | 8-shot CoT     | 654            | 145             | 800               | 83.4  | 1.02       | 9.60       |
|                   | CoT-SC₅        | 3275           | 751             | 4026              | 85.7  | 0.96       | 46.96      |
|                   | CoT-SC₁₀       | 6550           | 1499            | 8050              | 89.0  | 0.86       | 90.44      |
|                   | **MMLU**       |                |                 |                   |       |            |            |
|                   | Vanilla IO     | 201            | 201             | 402               | 51.1  | 1.24       | 7.88       |
|                   | Vanilla 4-shot | 711            | 208             | 920               | 58.8  | 1.19       | 15.65      |
|                   | Zeroshot CoT   | 207            | 342             | 550               | 69.4  | 1.13       | 7.93       |
|                   | 4-shot CoT     | 1008           | 182             | 1191              | 65.7  | 1.16       | 18.13      |
|                   | CoT-SC₅        | 5037           | 955             | 5993              | 66.9  | 1.16       | 89.53      |
|                   | CoT-SC₁₀       | 10076          | 1929            | 12006             | 69.5  | 1.12       | 172.76     |
| **Qwen 2.5 14B Instruct** | **BBH**        |                |                 |                   |       |            |            |
|                   | Vanilla IO     | 134            | 197             | 332               | 63.5  | 0.51       | 5.24       |
|                   | Vanilla 3-shot | 379            | 143             | 523               | 62.0  | 0.55       | 8.44       |
|                   | Zeroshot CoT   | 140            | 254             | 395               | 79.7  | 0.42       | 4.96       |
|                   | 3-shot CoT     | 830            | 195             | 1026              | 81.2  | 0.43       | 12.64      |
|                   | CoT-SC₅        | 4155           | 1011            | 5166              | 82.8  | 0.41       | 62.37      |
|                   | CoT-SC₁₀       | 8310           | 2028            | 10339             | 83.7  | 0.40       | 123.52     |
|                   | **GSM8K**      |                |                 |                   |       |            |            |
|                   | Vanilla IO     | 101            | 180             | 281               | 81.2  | 1.08       | 3.47       |
|                   | Vanilla 8-shot | 618            | 150             | 768               | 83.5  | 1.02       | 9.21       |
|                   | Zeroshot CoT   | 104            | 194             | 299               | 81.9  | 1.06       | 3.65       |
|                   | 8-shot CoT     | 633            | 125             | 759               | 87.6  | 0.91       | 8.67       |
|                   | CoT-SC₅        | 3168           | 602             | 3770              | 88.7  | 0.87       | 42.51      |
|                   | CoT-SC₁₀       | 6337           | 1221            | 7559              | 89.7  | 0.84       | 84.28      |
|                   | **MMLU**       |                |                 |                   |       |            |            |
|                   | Vanilla IO     | 162            | 162             | 325               | 76.4  | 1.05       | 4.26       |
|                   | Vanilla 4-shot | 673            | 130             | 804               | 78.4  | 1.03       | 10.25      |
|                   | Zeroshot CoT   | 169            | 347             | 516               | 81.4  | 0.97       | 6.35       |
|                   | 4-shot CoT     | 965            | 163             | 1129              | 81.8  | 0.96       | 13.81      |
|                   | CoT-SC₅        | 4829           | 883             | 5713              | 82.5  | 0.95       | 69.26      |
|                   | CoT-SC₁₀       | 9650           | 1743            | 11394             | 82.9  | 0.94       | 137.47     |
| **Qwen 2.5 32B Instruct** | **BBH**        |                |                 |                   |       |            |            |
|                   | Vanilla IO     | 134            | 201             | 336               | 63.4  | 0.50       | 5.30       |
|                   | Vanilla 3-shot | 379            | 144             | 523               | 71.2  | 0.49       | 7.36       |
|                   | Zeroshot CoT   | 141            | 242             | 383               | 82.3  | 0.39       | 4.66       |
|                   | 3-shot CoT     | 830            | 182             | 1012              | 87.2  | 0.37       | 11.62      |
|                   | CoT-SC₅        | 4153           | 938             | 5092              | 88.5  | 0.36       | 57.56      |
|                   | CoT-SC₁₀       | 8308           | 1883            | 10191             | 88.8  | 0.35       | 114.75     |
|                   | **GSM8K**      |                |                 |                   |       |            |            |
|                   | Vanilla IO     | 101            | 197             | 298               | 83.4  | 1.02       | 3.58       |
|                   | Vanilla 8-shot | 618            | 192             | 810               | 85.2  | 0.98       | 9.51       |
|                   | Zeroshot CoT   | 104            | 199             | 304               | 84.1  | 1.01       | 3.62       |
|                   | 8-shot CoT     | 633            | 135             | 769               | 89.4  | 0.85       | 8.60       |
|                   | CoT-SC₅        | 3168           | 687             | 3856              | 89.8  | 0.83       | 42.96      |
|                   | CoT-SC₁₀       | 6337           | 1373            | 7711              | 89.8  | 0.83       | 85.90      |
|                   | **MMLU**       |                |                 |                   |       |            |            |
|                   | Vanilla IO     | 162            | 249             | 412               | 65.3  | 1.18       | 6.32       |
|                   | Vanilla 4-shot | 671            | 194             | 865               | 77.3  | 1.05       | 11.21      |
|                   | Zeroshot CoT   | 169            | 357             | 526               | 84.5  | 0.89       | 6.23       |
|                   | 4-shot CoT     | 966            | 186             | 1153              | 85.2  | 0.87       | 13.53      |
|                   | CoT-SC₅        | 4827           | 1013            | 5840              | 85.4  | 0.87       | 68.37      |
|                   | CoT-SC₁₀       | 9652           | 2030            | 11682             | 86.1  | 0.86       | 135.70     |

* Accuracy as a percentage.

<transcription_json>
{
  "table_type": "data_table",
  "title": "Detailed results from the empirical evaluation described in Section 3.2.",
  "columns": ["", "Strategy", "Avg. Tokens_in", "Avg. Tokens_out", "Avg. Tokens_total", "Acc.*", "Std. Error", "Average TC"],
  "data": [
    {"": "Llama 3.1 BB Instruct", "Strategy": "Vanilla IO", "Avg. Tokens_in": 172, "Avg. Tokens_out": 221, "Avg. Tokens_total": 393, "Acc.*": 51.1, "Std. Error": 0.56, "Average TC": 7.70},
    {"": "", "Strategy": "Vanilla 3-shot", "Avg. Tokens_in": 420, "Avg. Tokens_out": 226, "Avg. Tokens_total": 646, "Acc.*": 35.4, "Std. Error": 0.54, "Average TC": 18.28},
    {"": "", "Strategy": "Zeroshot CoT", "Avg. Tokens_in": 178, "Avg. Tokens_out": 351, "Avg. Tokens_total": 530, "Acc.*": 63.2, "Std. Error": 0.55, "Average TC": 8.38},
    {"": "", "Strategy": "3-shot CoT", "Avg. Tokens_in": 876, "Avg. Tokens_out": 335, "Avg. Tokens_total": 1212, "Acc.*": 70.5, "Std. Error": 0.51, "Average TC": 17.20},
    {"": "", "Strategy": "CoT-SC₅", "Avg. Tokens_in": 4378, "Avg. Tokens_out": 1089, "Avg. Tokens_total": 5468, "Acc.*": 72.7, "Std. Error": 0.50, "Average TC": 75.19},
    {"": "", "Strategy": "CoT-SC₁₀", "Avg. Tokens_in": 8758, "Avg. Tokens_out": 2177, "Avg. Tokens_total": 10935, "Acc.*": 73.1, "Std. Error": 0.50, "Average TC": 149.58},
    {"": "GSM8K", "Strategy": "Vanilla IO", "Avg. Tokens_in": 122, "Avg. Tokens_out": 162, "Avg. Tokens_total": 284, "Acc.*": 77.3, "Std. Error": 1.15, "Average TC": 3.68},
    {"": "", "Strategy": "Vanilla 8-shot", "Avg. Tokens_in": 639, "Avg. Tokens_out": 147, "Avg. Tokens_total": 787, "Acc.*": 79.3, "Std. Error": 1.12, "Average TC": 9.93},
    {"": "", "Strategy": "Zeroshot CoT", "Avg. Tokens_in": 126, "Avg. Tokens_out": 203, "Avg. Tokens_total": 330, "Acc.*": 75.5, "Std. Error": 1.18, "Average TC": 4.37},
    {"": "", "Strategy": "8-shot CoT", "Avg. Tokens_in": 654, "Avg. Tokens_out": 145, "Avg. Tokens_total": 800, "Acc.*": 83.4, "Std. Error": 1.02, "Average TC": 9.60},
    {"": "", "Strategy": "CoT-SC₅", "Avg. Tokens_in": 3275, "Avg. Tokens_out": 751, "Avg. Tokens_total": 4026, "Acc.*": 85.7, "Std. Error": 0.96, "Average TC": 46.96},
    {"": "", "Strategy": "CoT-SC₁₀", "Avg. Tokens_in": 6550, "Avg. Tokens_out": 1499, "Avg. Tokens_total": 8050, "Acc.*": 89.0, "Std. Error": 0.86, "Average TC": 90.44},
    {"": "MMLU", "Strategy": "Vanilla IO", "Avg. Tokens_in": 201, "Avg. Tokens_out": 201, "Avg. Tokens_total": 402, "Acc.*": 51.1, "Std. Error": 1.24, "Average TC": 7.88},
    {"": "", "Strategy": "Vanilla 4-shot", "Avg. Tokens_in": 711, "Avg. Tokens_out": 208, "Avg. Tokens_total": 920, "Acc.*": 58.8, "Std. Error": 1.19, "Average TC": 15.65},
    {"": "", "Strategy": "Zeroshot CoT", "Avg. Tokens_in": 207, "Avg. Tokens_out": 342, "Avg. Tokens_total": 550, "Acc.*": 69.4, "Std. Error": 1.13, "Average TC": 7.93},
    {"": "", "Strategy": "4-shot CoT", "Avg. Tokens_in": 1008, "Avg. Tokens_out": 182, "Avg. Tokens_total": 1191, "Acc.*": 65.7, "Std. Error": 1.16, "Average TC": 18.13},
    {"": "", "Strategy": "CoT-SC₅", "Avg. Tokens_in": 5037, "Avg. Tokens_out": 955, "Avg. Tokens_total": 5993, "Acc.*": 66.9, "Std. Error": 1.16, "Average TC": 89.53},
    {"": "", "Strategy": "CoT-SC₁₀", "Avg. Tokens_in": 10076, "Avg. Tokens_out": 1929, "Avg. Tokens_total": 12006, "Acc.*": 69.5, "Std. Error": 1.12, "Average TC": 172.76},
    {"": "Qwen 2.5 14B Instruct", "Strategy": "Vanilla IO", "Avg. Tokens_in": 134, "Avg. Tokens_out": 197, "Avg. Tokens_total": 332, "Acc.*": 63.5, "Std. Error": 0.51, "Average TC": 5.24},
    {"": "", "Strategy": "Vanilla 3-shot", "Avg. Tokens_in": 379, "Avg. Tokens_out": 143, "Avg. Tokens_total": 523, "Acc.*": 62.0, "Std. Error": 0.55, "Average TC": 8.44},
    {"": "", "Strategy": "Zeroshot CoT", "Avg. Tokens_in": 140, "Avg. Tokens_out": 254, "Avg. Tokens_total": 395, "Acc.*": 79.7, "Std. Error": 0.42, "Average TC": 4.96},
    {"": "", "Strategy": "3-shot CoT", "Avg. Tokens_in": 830, "Avg. Tokens_out": 195, "Avg. Tokens_total": 1026, "Acc.*": 81.2, "Std. Error": 0.43, "Average TC": 12.64},
    {"": "", "Strategy": "CoT-SC₅", "Avg. Tokens_in": 4155, "Avg. Tokens_out": 1011, "Avg. Tokens_total": 5166, "Acc.*": 82.8, "Std. Error": 0.41, "Average TC": 62.37},
    {"": "", "Strategy": "CoT-SC₁₀", "Avg. Tokens_in": 8310, "Avg. Tokens_out": 2028, "Avg. Tokens_total": 10339, "Acc.*": 83.7, "Std. Error": 0.40, "Average TC": 123.52},
    {"": "GSM8K", "Strategy": "Vanilla IO", "Avg. Tokens_in": 101, "Avg. Tokens_out": 180, "Avg. Tokens_total": 281, "Acc.*": 81.2, "Std. Error": 1.08, "Average TC": 3.47},
    {"": "", "Strategy": "Vanilla 8-shot", "Avg. Tokens_in": 618, "Avg. Tokens_out": 150, "Avg. Tokens_total": 768, "Acc.*": 83.5, "Std. Error": 1.02, "Average TC": 9.21},
    {"": "", "Strategy": "Zeroshot CoT", "Avg. Tokens_in": 104, "Avg. Tokens_out": 194, "Avg. Tokens_total": 299, "Acc.*": 81.9, "Std. Error": 1.06, "Average TC": 3.65},
    {"": "", "Strategy": "8-shot CoT", "Avg. Tokens_in": 633, "Avg. Tokens_out": 125, "Avg. Tokens_total": 759, "Acc.*": 87.6, "Std. Error": 0.91, "Average TC": 8.67},
    {"": "", "Strategy": "CoT-SC₅", "Avg. Tokens_in": 3168, "Avg. Tokens_out": 602, "Avg. Tokens_total": 3770, "Acc.*": 88.7, "Std. Error": 0.87, "Average TC": 42.51},
    {"": "", "Strategy": "CoT-SC₁₀", "Avg. Tokens_in": 6337, "Avg. Tokens_out": 1221, "Avg. Tokens_total": 7559, "Acc.*": 89.7, "Std. Error": 0.84, "Average TC": 84.28},
    {"": "MMLU", "Strategy": "Vanilla IO", "Avg. Tokens_in": 162, "Avg. Tokens_out": 162, "Avg. Tokens_total": 325, "Acc.*": 76.4, "Std. Error": 1.05, "Average TC": 4.26},
    {"": "", "Strategy": "Vanilla 4-shot", "Avg. Tokens_in": 673, "Avg. Tokens_out": 130, "Avg. Tokens_total": 804, "Acc.*": 78.4, "Std. Error": 1.03, "Average TC": 10.25},
    {"": "", "Strategy": "Zeroshot CoT", "Avg. Tokens_in": 169, "Avg. Tokens_out": 347, "Avg. Tokens_total": 516, "Acc.*": 81.4, "Std. Error": 0.97, "Average TC": 6.35},
    {"": "", "Strategy": "4-shot CoT", "Avg. Tokens_in": 965, "Avg. Tokens_out": 163, "Avg. Tokens_total": 1129, "Acc.*": 81.8, "Std. Error": 0.96, "Average TC": 13.81},
    {"": "", "Strategy": "CoT-SC₅", "Avg. Tokens_in": 4829, "Avg. Tokens_out": 883, "Avg. Tokens_total": 5713, "Acc.*": 82.5, "Std. Error": 0.95, "Average TC": 69.26},
    {"": "", "Strategy": "CoT-SC₁₀", "Avg. Tokens_in": 9650, "Avg. Tokens_out": 1743, "Avg. Tokens_total": 11394, "Acc.*": 82.9, "Std. Error": 0.94, "Average TC": 137.47},
    {"": "Qwen 2.5 32B Instruct", "Strategy": "Vanilla IO", "Avg. Tokens_in": 134, "Avg. Tokens_out": 201, "Avg. Tokens_total": 336, "Acc.*": 63.4, "Std. Error": 0.50, "Average TC": 5.30},
    {"": "", "Strategy": "Vanilla 3-shot", "Avg. Tokens_in": 379, "Avg. Tokens_out": 144, "Avg. Tokens_total": 523, "Acc.*": 71.2, "Std. Error": 0.49, "Average TC": 7.36},
    {"": "", "Strategy": "Zeroshot CoT", "Avg. Tokens_in": 141, "Avg. Tokens_out": 242, "Avg. Tokens_total": 383, "Acc.*": 82.3, "Std. Error": 0.39, "Average TC": 4.66},
    {"": "", "Strategy": "3-shot CoT", "Avg. Tokens_in": 830, "Avg. Tokens_out": 182, "Avg. Tokens_total": 1012, "Acc.*": 87.2, "Std. Error": 0.37, "Average TC": 11.62},
    {"": "", "Strategy": "CoT-SC₅", "Avg. Tokens_in": 4153, "Avg. Tokens_out": 938, "Avg. Tokens_total": 5092, "Acc.*": 88.5, "Std. Error": 0.36, "Average TC": 57.56},
    {"": "", "Strategy": "CoT-SC₁₀", "Avg. Tokens_in": 8308, "Avg. Tokens_out": 1883, "Avg. Tokens_total": 10191, "Acc.*": 88.8, "Std. Error": 0.35, "Average TC": 114.75},
    {"": "GSM8K", "Strategy": "Vanilla IO", "Avg. Tokens_in": 101, "Avg. Tokens_out": 197, "Avg. Tokens_total": 298, "Acc.*": 83.4, "Std. Error": 1.02, "Average TC": 3.58},
    {"": "", "Strategy": "Vanilla 8-shot", "Avg. Tokens_in": 618, "Avg. Tokens_out": 192, "Avg. Tokens_total": 810, "Acc.*": 85.2, "Std. Error": 0.98, "Average TC": 9.51},
    {"": "", "Strategy": "Zeroshot CoT", "Avg. Tokens_in": 104, "Avg. Tokens_out": 199, "Avg. Tokens_total": 304, "Acc.*": 84.1, "Std. Error": 1.01, "Average TC": 3.62},
    {"": "", "Strategy": "8-shot CoT", "Avg. Tokens_in": 633, "Avg. Tokens_out": 135, "Avg. Tokens_total": 769, "Acc.*": 89.4, "Std. Error": 0.85, "Average TC": 8.60},
    {"": "", "Strategy": "CoT-SC₅", "Avg. Tokens_in": 3168, "Avg. Tokens_out": 687, "Avg. Tokens_total": 3856, "Acc.*": 89.8, "Std. Error": 0.83, "Average TC": 42.96},
    {"": "", "Strategy": "CoT-SC₁₀", "Avg. Tokens_in": 6337, "Avg. Tokens_out": 1373, "Avg. Tokens_total": 7711, "Acc.*": 89.8, "Std. Error": 0.83, "Average TC": 85.90},
    {"": "MMLU", "Strategy": "Vanilla IO", "Avg. Tokens_in": 162, "Avg. Tokens_out": 249, "Avg. Tokens_total": 412, "Acc.*": 65.3, "Std. Error": 1.18, "Average TC": 6.32},
    {"": "", "Strategy": "Vanilla 4-shot", "Avg. Tokens_in": 671, "Avg. Tokens_out": 194, "Avg. Tokens_total": 865, "Acc.*": 77.3, "Std. Error": 1.05, "Average TC": 11.21},
    {"": "", "Strategy": "Zeroshot CoT", "Avg. Tokens_in": 169, "Avg. Tokens_out": 357, "Avg. Tokens_total": 526, "Acc.*": 84.5, "Std. Error": 0.89, "Average TC": 6.23},
    {"": "", "Strategy": "4-shot CoT", "Avg. Tokens_in": 966, "Avg. Tokens_out": 186, "Avg. Tokens_total": 1153, "Acc.*": 85.2, "Std. Error": 0.87, "Average TC": 13.53},
    {"": "", "Strategy": "CoT-SC₅", "Avg. Tokens_in": 4827, "Avg. Tokens_out": 1013, "Avg. Tokens_total": 5840, "Acc.*": 85.4, "Std. Error": 0.87, "Average TC": 68.37},
    {"": "", "Strategy": "CoT-SC₁₀", "Avg. Tokens_in": 9652, "Avg. Tokens_out": 2030, "Avg. Tokens_total": 11682, "Acc.*": 86.1, "Std. Error": 0.86, "Average TC": 135.70}
  ],
  "notes": "* Accuracy as a percentage."
}
</transcription_json>
</transcription_table>

<transcription_table>
**Table 7: Cost estimates for recreating the empirical evaluation with common commercial models.**

| Model             | Price_input* | Price_output* | Cost† (US$) BBH | Cost† (US$) GSM8K | Cost† (US$) MMLU |
|-------------------|--------------|---------------|-----------------|-------------------|------------------|
| GPT-4o            | 2.5          | 10.0          | 488.25          | 72.53             | 121.57           |
| GPT-4o-mini       | 0.15         | 0.6           | 29.29           | 4.35              | 7.29             |
| Claude 3.5 Sonnet | 3.0          | 15.0          | 662.89          | 97.81             | 163.16           |
| Claude 3.5 Haiku  | 0.8          | 4.0           | 176.77          | 26.08             | 43.51            |

* Prices are in US$ per 1M tokens.  
† Cost to run all prompting strategies on the given benchmark.

<transcription_json>
{
  "table_type": "data_table",
  "title": "Cost estimates for recreating the empirical evaluation with common commercial models.",
  "columns": ["Model", "Price_input*", "Price_output*", "Cost† (US$) BBH", "Cost† (US$) GSM8K", "Cost† (US$) MMLU"],
  "data": [
    {"Model": "GPT-4o", "Price_input*": 2.5, "Price_output*": 10.0, "Cost† (US$) BBH": 488.25, "Cost† (US$) GSM8K": 72.53, "Cost† (US$) MMLU": 121.57},
    {"Model": "GPT-4o-mini", "Price_input*": 0.15, "Price_output*": 0.6, "Cost† (US$) BBH": 29.29, "Cost† (US$) GSM8K": 4.35, "Cost† (US$) MMLU": 7.29},
    {"Model": "Claude 3.5 Sonnet", "Price_input*": 3.0, "Price_output*": 15.0, "Cost† (US$) BBH": 662.89, "Cost† (US$) GSM8K": 97.81, "Cost† (US$) MMLU": 163.16},
    {"Model": "Claude 3.5 Haiku", "Price_input*": 0.8, "Price_output*": 4.0, "Cost† (US$) BBH": 176.77, "Cost† (US$) GSM8K": 26.08, "Cost† (US$) MMLU": 43.51}
  ],
  "notes": "Prices are in US$ per 1M tokens. Cost to run all prompting strategies on the given benchmark."
}
</transcription_json>
</transcription_table>
---

| Model*                        | Max Context Length | Max Generations Tokens | Temperature               |
|------------------------------|--------------------|-----------------------|---------------------------|
| meta-llama/Llama-3.1-8B-Instruct | 128000             | 16384                 | 0.0 (0.5 for CoT-SC)      |
| Qwen/Qwen2.5-14B-Instruct    | 128000             | 8192                  | 0.0 (0.5 for CoT-SC)      |
| Qwen/Qwen2.5-32B-Instruct    | 128000             | 8192                  | 0.0 (0.5 for CoT-SC)      |

* Models were sourced from https://huggingface.co/models.

Table 8: Model configurations used for the empirical evaluation.

| Benchmark | Split      | Fewshot Split | # Samples |
|-----------|------------|---------------|-----------|
| BBH       | test       | test*         | 6511      |
| GSM8K     | test       | train         | 1319      |
| MMLU      | validation | dev           | 1531      |

* Sampled fewshot examples did not overlap with the current benchmark question.

Table 9: Benchmark configurations used for the empirical evaluation.

---

### C.5.3 Prompts

To limit the inadvertent effects of linguistic prompt engineering (see Salinas and Morstatter (2024)), we avoided making adjustments to the prompts as they were constructed by default in LM Evaluation Harness, for consistency. As such, we did not include output formatting instructions and used the default prompt template for each model. We excluded output formatting instructions for two reasons: (1) to not interfere with the LLM’s natural output for the benchmark question and (2) to allow the benefits of implicit formatting for fewshot strategies. We include an example of a raw text input and output pair for Qwen 2.5 14B on MMLU using Zeroshot CoT below:

**Input**

```
<|im_start|>system
The following are multiple choice questions (with answers) about high school psychology.

<|im_end|>
<|im_start|>user
Question: Why are psychoanalysts sometimes interested in talking with a patient about dreams?
(A) Psychoanalysts discovered that neurotransmitter abnormalities sometimes cause dream disturbances.;
(B) Since all people are striving for self-actualization, psychoanalysts look at the cognitive obstacles in dreams.;
(C) Nonproductive counterconditioning behaviors are sometimes revealed in dreams.;
(D) Some psychoanalysts believe that dream symbols represent unconscious conflicts.

Answer: Let's think step by step.
<|im_end|>
<|im_start|>assistant
```

**Output**

```
To determine the correct answer, let's analyze each option in the context of psychoanalytic theory:

(A) Psychoanalysts discovered that neurotransmitter abnormalities sometimes cause dream disturbances.
- This statement is more aligned with biological psychology rather than psychoanalysis. Psychoanalysis does not focus on neurotransmitters or biological abnormalities as the primary cause of dream disturbances.

(B) Since all people are striving for self-actualization, psychoanalysts look at the cognitive obstacles in dreams.
- This statement aligns more with humanistic psychology, particularly the work of Carl Rogers and Abraham Maslow, who emphasized self-actualization. Psychoanalysis, as developed by Freud, does not focus on self-actualization or cognitive obstacles in dreams.

(C) Nonproductive counterconditioning behaviors are sometimes revealed in
```

[Text cut off]
---

C.5.4  Compute  
Experiments were run on A100 40GB, A100 80GB, and H100 GPUs, as availability permitted. Configurations were limited to 1 or 2 GPUs per experiment. The experiments were run in tensor parallel or data parallel configurations, depending on the size of the model and the number of GPUs used. The exact configurations per experiment, as well as exact wall times, are detailed in the reproducibility materials referenced in Section C.4. The approximate number of GPU hours across all GPUs was 95.

C.6  Licensing  
We use a number of open-source artifacts in this work. We list the licenses for each in Table 10. We verify that our usage was in accordance with the projects’ licenses.

D  Additional Studies

D.1  Ablation Study on the Number of Fewshot Exemplars  
We present the results from our ablation study on the number of fewshot examples in Figure 3, with detailed results in Table 12. For this experiment, we used the Vanilla Fewshot and Fewshot CoT prompting strategies with the number of exemplars ranging from 0 to 8. As can be seen in Figure 3, the results are noisier but there is a clear trend of diminishing returns as the number of fewshot exemplars increases. To demonstrate this in a way that mitigates the noise, we examine the results piecewise, comparing the average marginal TC between 0 and 3 exemplars and 3 and 8 exemplars. Those values are found in Table 11, for concision. The marginal TC between 0 and 3 fewshot exemplars is, for both Vanilla Fewshot and Fewshot CoT, over an order of magnitude less than between 3 and 8. This indicates a significant decrease in efficiency as token usage increases, which corroborates our findings in Section 4.

D.2  Model Size  
We included two models from the Qwen 2.5 family to facilitate a discussion on the impact of model size on our observed trends. Selecting two models from the same family ensures that potentially confounding variables, such as differences in training, data collection, and alignment, are presumably kept the same. We present the results from our experiments in Figure 4²⁰.  
We observe that the trend towards diminishing accuracy returns for increased token usage is consistent between the 14B and 32B models. As expected, the 32B model generally outperforms the 14B model. However, we note some instances for prompting strategies that consume fewer tokens, such as Vanilla IO and Fewshot, where the 14B model outperforms the larger one. This suggests that larger models may be able to use additional tokens more effectively, as reflected in the consistently higher accuracy for Fewshot CoT and CoT-SC, but struggle to perform better than smaller models when fewer tokens are provided as context. This provides a promising route for future work.

E  Use of AI  
There was limited use of AI in the research and writing of this work. For writing, ChatGPT²¹ was used to rephrase several sentences (<5) and to help debug LaTeX and Kubernetes errors. GitHub Copilot²² was used to help generate some of the plots. Some grammatical suggestions from Write-

---
²⁰ These plots are identical to those from Figure 1 but with Llama 3.1 8B excluded, for ease of comparison.  
²¹ https://chatgpt.com/  
²² https://github.com/features/copilot
---

<transcription_table>
**Table 10: Licenses for the artifacts used in this work.**

| Artifact                 | License                    | Notes                                                   |
|--------------------------|----------------------------|---------------------------------------------------------|
| Llama 3.1 8B Instruct    | Llama 3.1 Community License| Copyright © Meta Platforms, Inc. All Rights Reserved.   |
| Qwen 2.5 14B Instruct    | Qwen LICENSE AGREEMENT      | Version: September 19, 2024                              |
| Qwen 2.5 32B Instruct    | Qwen LICENSE AGREEMENT      | Version: September 19, 2024                              |
| LM Evaluation Harness    | MIT License                 | Copyright (c) 2020 EleutherAI                            |
| BBH                      | MIT License                 | Copyright (c) 2022 suzgunmirac                            |
| GSM8K                    | MIT License                 | Copyright (c) 2021 OpenAI                                 |
| MMLU                     | MIT License                 | Copyright (c) 2020 Dan Hendrycks                          |

<transcription_json>
{"table_type": "data_table", "title": "Licenses for the artifacts used in this work", "columns": ["Artifact", "License", "Notes"], "data": [{"Artifact": "Llama 3.1 8B Instruct", "License": "Llama 3.1 Community License", "Notes": "Copyright © Meta Platforms, Inc. All Rights Reserved."}, {"Artifact": "Qwen 2.5 14B Instruct", "License": "Qwen LICENSE AGREEMENT", "Notes": "Version: September 19, 2024"}, {"Artifact": "Qwen 2.5 32B Instruct", "License": "Qwen LICENSE AGREEMENT", "Notes": "Version: September 19, 2024"}, {"Artifact": "LM Evaluation Harness", "License": "MIT License", "Notes": "Copyright (c) 2020 EleutherAI"}, {"Artifact": "BBH", "License": "MIT License", "Notes": "Copyright (c) 2022 suzgunmirac"}, {"Artifact": "GSM8K", "License": "MIT License", "Notes": "Copyright (c) 2021 OpenAI"}, {"Artifact": "MMLU", "License": "MIT License", "Notes": "Copyright (c) 2020 Dan Hendrycks"}]}
</transcription_json>

<transcription_notes>
- Table with three columns: Artifact, License, Notes
- Lists open source licenses and copyright information for used models and datasets
</transcription_notes>
</transcription_table>

<transcription_image>
**Figure 3: Accuracy and total token usage for the ablation study on the number of fewshot exemplars on the GSM8K benchmark. Standard error bars are included.**

```ascii
(Vanilla Fewshot)                          (Fewshot CoT)
Accuracy (%)                              Accuracy (%)
0.86 |                                  0.90 |
     |                                  0.88 |
0.84 |  1    2    3    4    5    6    7    8 |  1    2    3    4    5    6    7    8
     |  ●    ●    ●    ●    ●    ●    ●    ● |  ●    ●    ●    ●    ●    ●    ●    ●  
0.82 |  ■    ■    ■    ■    ■    ■    ■    ■ |  ■    ■    ■    ■    ■    ■    ■    ■  
     |  ◆    ◆    ◆    ◆    ◆    ◆    ◆    ◆ |  ◆    ◆    ◆    ◆    ◆    ◆    ◆    ◆  
0.80 |  *    *    *    *    *    *    *    * |  *    *    *    *    *    *    *    *  
     |---------------------------------------|------------------------------------------
       300  400  500  600  700  800            300  400  500  600  700  800
      Average Total Tokens (input + output)   Average Total Tokens (input + output)

Legend (both plots):
● Qwen 2.5 14B
■ Llama 3.1 8B
◆ Qwen 2.5 32B
* Number of Exemplars

Notes:
- Standard error bars shown on all points
- Accuracy values range roughly from 0.76 to 0.86 (Vanilla) and 0.78 to 0.89 (CoT)
- Number of exemplars increases from 1 to 8, with accuracy generally increasing
```

<transcription_json>
{
  "chart_type": "scatter_plot",
  "title": "Accuracy and total token usage for the ablation study on the number of fewshot exemplars on GSM8K",
  "data": [
    {
      "model": "Qwen 2.5 14B",
      "marker": "●",
      "accuracy_range_vanilla": [0.80, 0.85],
      "accuracy_range_cot": [0.82, 0.89],
      "tokens_range": [300, 800]
    },
    {
      "model": "Llama 3.1 8B",
      "marker": "■",
      "accuracy_range_vanilla": [0.76, 0.78],
      "accuracy_range_cot": [0.78, 0.83],
      "tokens_range": [300, 800]
    },
    {
      "model": "Qwen 2.5 32B",
      "marker": "◆",
      "accuracy_range_vanilla": [0.82, 0.86],
      "accuracy_range_cot": [0.85, 0.89],
      "tokens_range": [300, 800]
    },
    {
      "model": "Number of Exemplars",
      "marker": "*",
      "values": [1,2,3,4,5,6,7,8]
    }
  ],
  "x_axis": "Average Total Tokens (input + output)",
  "y_axis": "Accuracy (%)",
  "notes": "Standard error bars included"
}
</transcription_json>

<transcription_notes>
- Two side-by-side scatter plots comparing Vanilla Fewshot vs Fewshot CoT on GSM8K
- X-axis: Average total tokens (input + output) from 300 to 800
- Y-axis: Accuracy percentages with error bars
- Markers indicate different models: Qwen 2.5 14B (circle), Llama 3.1 8B (square), Qwen 2.5 32B (diamond), Number of Exemplars (asterisk)
- Accuracy generally higher for Fewshot CoT than Vanilla Fewshot
</transcription_notes>
</transcription_image>

<transcription_image>
**Figure 4: Accuracy and total token usage information for Qwen 2.5 14B and Qwen 2.5 32B from the empirical evaluation. The trend lines demonstrate the rapid growth of TC for these prompting strategies.**

```ascii
(A) BBH                                  (B) GSM8K                               (C) MMLU
Accuracy (%)                            Accuracy (%)                           Accuracy (%)
0.90 |                                0.92 |                               0.85 |
     |                                0.90 |                               0.80 |
0.85 |  C10  C25  C50                 0.88 |  C10  C25  C50                   0.75 |  C10  C25  C50
     |  ●    ●    ●                   0.86 |  ●    ●    ●                   0.70 |  ●    ●    ●
0.80 |  ●    ●    ●                   0.84 |  ●    ●    ●                   0.65 |  ●    ●    ●
     |  ◆    ◆    ◆                   0.82 |  ◆    ◆    ◆                   0.60 |  ◆    ◆    ◆
0.75 |  ◆    ◆    ◆                   0.80 |  ◆    ◆    ◆                   0.55 |  ◆    ◆    ◆
     |  ■    ■    ■                   0.78 |  ■    ■    ■                   0.50 |  ■    ■    ■
0.70 |  ■    ■    ■                   0.76 |  ■    ■    ■                   0.45 |  ■    ■    ■
     |--------------------------------|---------------------------------|---------------------------
      0   4000  8000 10000              0    2000  4000  6000  8000          0    4000  8000 12000
      Average Total Tokens (input + output) Average Total Tokens (input + output) Average Total Tokens (input + output)

Legend (all plots):
● Qwen 2.5 32B
■ Qwen 2.5 14B
◆ Vanilla 10
○ Vanilla Fewshot
▲ Fewshot CoT
▼ Zeroshot CoT
- Curves labeled: Cot SC-5 and Cot SC-10 (trend lines)

Notes:
- Accuracy increases with tokens and prompting strategies
- Trend lines show rapid growth of token consumption (TC)
```

<transcription_json>
{
  "chart_type": "scatter_plot_series",
  "title": "Accuracy and total token usage for Qwen 2.5 14B and Qwen 2.5 32B empirical evaluation",
  "panels": [
    {
      "label": "A",
      "dataset": "BBH",
      "x_axis": "Average Total Tokens (input + output)",
      "y_axis": "Accuracy (%)",
      "x_range": [0, 10000],
      "y_range": [0.70, 0.90],
      "data_points": [
        {"model": "Qwen 2.5 32B", "markers": ["●"], "tokens": [4000, 8000, 10000], "accuracy": [0.82, 0.85, 0.86]},
        {"model": "Qwen 2.5 14B", "markers": ["■"], "tokens": [4000, 8000, 10000], "accuracy": [0.78, 0.80, 0.82]},
        {"model": "Vanilla 10", "markers": ["◆"], "tokens": [4000, 8000, 10000], "accuracy": [0.75, 0.78, 0.79]}
      ]
    },
    {
      "label": "B",
      "dataset": "GSM8K",
      "x_axis": "Average Total Tokens (input + output)",
      "y_axis": "Accuracy (%)",
      "x_range": [0, 8000],
      "y_range": [0.76, 0.92],
      "data_points": [
        {"model": "Qwen 2.5 32B", "markers": ["●"], "tokens": [2000, 4000, 6000, 8000], "accuracy": [0.85, 0.88, 0.89, 0.90]},
        {"model": "Qwen 2.5 14B", "markers": ["■"], "tokens": [2000, 4000, 6000, 8000], "accuracy": [0.82, 0.84, 0.86, 0.87]},
        {"model": "Vanilla 10", "markers": ["◆"], "tokens": [2000, 4000, 6000, 8000], "accuracy": [0.80, 0.82, 0.83, 0.85]}
      ]
    },
    {
      "label": "C",
      "dataset": "MMLU",
      "x_axis": "Average Total Tokens (input + output)",
      "y_axis": "Accuracy (%)",
      "x_range": [0, 12000],
      "y_range": [0.45, 0.85],
      "data_points": [
        {"model": "Qwen 2.5 32B", "markers": ["●"], "tokens": [4000, 8000, 12000], "accuracy": [0.75, 0.80, 0.83]},
        {"model": "Qwen 2.5 14B", "markers": ["■"], "tokens": [4000, 8000, 12000], "accuracy": [0.60, 0.65, 0.70]},
        {"model": "Vanilla 10", "markers": ["◆"], "tokens": [4000, 8000, 12000], "accuracy": [0.55, 0.60, 0.65]}
      ]
    }
  ],
  "legend": {
    "●": "Qwen 2.5 32B",
    "■": "Qwen 2.5 14B",
    "◆": "Vanilla 10",
    "○": "Vanilla Fewshot",
    "▲": "Fewshot CoT",
    "▼": "Zeroshot CoT"
  },
  "trend_lines": ["Cot SC-5", "Cot SC-10"],
  "notes": "Trend lines demonstrate rapid growth of token consumption for these prompting strategies."
}
</transcription_json>

<transcription_notes>
- Three scatter plots (A: BBH, B: GSM8K, C: MMLU)
- X-axis: Average total tokens (input + output), ranges vary by dataset
- Y-axis: Accuracy (%), ranges approx 0.45 to 0.92 depending on dataset
- Data points labeled with different markers for Qwen 2.5 32B, Qwen 2.5 14B, Vanilla 10, Vanilla Fewshot, Fewshot CoT, Zeroshot CoT
- Curves labeled Cot SC-5 and Cot SC-10 show trend lines
- Accuracy generally increases with tokens and more advanced prompting strategies
</transcription_notes>
---

<transcription_table>
**Table 11: Average marginal TCs (Δtokens/Δaccuracy) calculated between 0 and 3 exemplars and 3 and 8 exemplars for the ablation study on the number of fewshot exemplars.**

| Fewshot Range | Marginal TC (Δp)           |               |
|---------------|----------------------------|---------------|
|               | Vanilla Fewshot            | Fewshot CoT   |
| 0-3           | 117.2                      | 30.5          |
| 3-8           | 1621.5                     | 553.8         |

<transcription_json>
{"table_type": "data_table", "title": "Average marginal TCs (Δtokens/Δaccuracy) calculated between 0 and 3 exemplars and 3 and 8 exemplars for the ablation study on the number of fewshot exemplars.", "columns": ["Fewshot Range", "Vanilla Fewshot", "Fewshot CoT"], "data": [{"Fewshot Range": "0-3", "Vanilla Fewshot": 117.2, "Fewshot CoT": 30.5}, {"Fewshot Range": "3-8", "Vanilla Fewshot": 1621.5, "Fewshot CoT": 553.8}], "unit": "marginal TC"}
</transcription_json>

<transcription_notes>
- Marginal TC calculated as Δtokens/Δaccuracy (Δp)
- Comparing Vanilla Fewshot vs Fewshot CoT for fewshot ranges 0-3 and 3-8
- Indicates efficiency of token usage with accuracy improvement for different exemplar counts
</transcription_notes>
</transcription_table>

full’s Overleaf integration23 were considered and included. All AI outputs were thoroughly reviewed by the authors prior to inclusion.

23 https://www.overleaf.com/learn/how-to/Writefull_integration
---

<transcription_table>
**Table 12: Detailed results from the ablation study on the number of fewshot exemplars. Token counts represent the total token usage (input and output).**

| Strategy        | # Exemplars | Llama 3.1 8B Instruct |                |          | Qwen 2.5 14B Instruct |                |          | Qwen 2.5 32B Instruct |                |          |
|-----------------|-------------|-----------------------|----------------|----------|-----------------------|----------------|----------|-----------------------|----------------|----------|
|                 |             | Tokens                | Acc.*          | SE†      | Tokens                | Acc.*          | SE†      | Tokens                | Acc.*          | SE†      |
| **Vanilla Fewshot** | 0           | 283.8                 | 77.6           | 1.15     | 283.0                 | 81.7           | 1.06     | 299.4                 | 83.7           | 1.02     |
|                 | 1           | 344.5                 | 77.0           | 1.16     | 321.1                 | 83.2           | 1.03     | 349.6                 | 85.5           | 0.97     |
|                 | 2           | 401.6                 | 77.1           | 1.16     | 386.6                 | 83.4           | 1.02     | 418.0                 | 85.2           | 0.98     |
|                 | 3           | 463.4                 | 78.1           | 1.14     | 447.1                 | 84.2           | 1.00     | 483.1                 | 85.1           | 0.98     |
|                 | 4           | 526.3                 | 76.6           | 1.17     | 508.8                 | 82.7           | 1.04     | 547.9                 | 84.4           | 1.00     |
|                 | 5           | 607.9                 | 78.0           | 1.14     | 574.9                 | 83.5           | 1.02     | 613.2                 | 84.8           | 0.99     |
|                 | 6           | 668.8                 | 77.6           | 1.15     | 635.1                 | 84.2           | 1.01     | 680.4                 | 85.0           | 0.98     |
|                 | 7           | 722.6                 | 76.8           | 1.16     | 700.9                 | 83.5           | 1.02     | 743.7                 | 84.7           | 0.99     |
|                 | 8           | 787.3                 | 79.2           | 1.12     | 768.9                 | 83.9           | 1.01     | 810.1                 | 84.9           | 0.99     |
| **Fewshot CoT** | 0           | 273.2                 | 78.5           | 1.13     | 281.7                 | 81.2           | 1.08     | 294.2                 | 83.2           | 1.03     |
|                 | 1           | 351.3                 | 82.2           | 1.05     | 334.1                 | 84.5           | 1.00     | 353.7                 | 84.3           | 1.00     |
|                 | 2           | 398.1                 | 82.6           | 1.04     | 370.5                 | 86.5           | 0.94     | 397.7                 | 85.7           | 0.97     |
|                 | 3           | 462.6                 | 82.5           | 1.05     | 418.9                 | 88.8           | 0.87     | 443.1                 | 87.4           | 0.91     |
|                 | 4           | 524.8                 | 82.0           | 1.06     | 479.6                 | 88.4           | 0.88     | 514.2                 | 86.8           | 0.93     |
|                 | 5           | 584.3                 | 82.3           | 1.05     | 537.4                 | 89.3           | 0.85     | 567.8                 | 87.3           | 0.92     |
|                 | 6           | 664.6                 | 81.3           | 1.07     | 615.6                 | 88.9           | 0.87     | 638.9                 | 88.1           | 0.89     |
|                 | 7           | 739.2                 | 81.4           | 1.07     | 691.0                 | 88.9           | 0.87     | 711.0                 | 88.4           | 0.88     |
|                 | 8           | 801.3                 | 82.4           | 1.05     | 751.9                 | 88.9           | 0.87     | 768.3                 | 89.2           | 0.85     |

* Accuracy as a percentage.  
† Standard error.
</transcription_table>
