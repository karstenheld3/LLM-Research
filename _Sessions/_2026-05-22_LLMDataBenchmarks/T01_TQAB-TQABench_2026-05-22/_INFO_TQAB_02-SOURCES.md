<DevSystem MarkdownTablesAllowed=true />

# INFO: TQA-Bench Sources

**Doc ID**: TQAB-IN01-SRC
**Goal**: Collected sources for TQA-Bench deep research
**Preflight accuracy**: 6/8 assumptions verified (format testing was WRONG in initial survey - TQA-Bench DOES test format)

## Primary Sources (Tier 1)

- `TQAB-SC-ARXIV-PAPER` - arXiv:2411.19504 (full paper HTML) | Accessed: 2026-05-22
  - https://arxiv.org/html/2411.19504v1
- `TQAB-SC-GH-REPO` - GitHub repository (code, README, implementation) | Accessed: 2026-05-22
  - https://github.com/Relaxed-System-Lab/TQA-Bench
- `TQAB-SC-GH-GPT4O` - gpt4o.py model evaluation script | Accessed: 2026-05-22
  - https://raw.githubusercontent.com/Relaxed-System-Lab/TQA-Bench/main/symDataloader/gpt4o.py
- `TQAB-SC-GH-DBPY` - database.py serialization code | Accessed: 2026-05-22
  - https://raw.githubusercontent.com/Relaxed-System-Lab/TQA-Bench/main/benchmarkUtils/database.py
- `TQAB-SC-GH-UTILS` - symDataloader/utils.py TaskCore class | Accessed: 2026-05-22
  - https://raw.githubusercontent.com/Relaxed-System-Lab/TQA-Bench/main/symDataloader/utils.py
- `TQAB-SC-GH-PROMPT` - singleChoicePrompt.txt evaluation prompt | Accessed: 2026-05-22
  - https://raw.githubusercontent.com/Relaxed-System-Lab/TQA-Bench/main/benchmarkLoader/prompts/singleChoicePrompt.txt

## Secondary Sources (Tier 2-3)

- `TQAB-SC-EMIND-TOPIC` - EmergentMind topic summary with numerical results | Accessed: 2026-05-22
  - https://www.emergentmind.com/topics/tqa-bench

## Dataset Downloads

- **Task file**: https://hkustconnect-my.sharepoint.com/:u:/g/personal/zqiuao_connect_ust_hk/EWAnhWoIhJpIgkkge1ZoBoYB7eF1AgJbcfV4nDfpFLua4A?e=727pOz
  - Place in: `symDataset/tasks/TableQA/`
- **Scaled database**: https://hkustconnect-my.sharepoint.com/:u:/g/personal/zqiuao_connect_ust_hk/ESGMS0lh1l9MirS9SvS7_E0BSpBXpml7OsCdc0oLx70b_A?e=AgHy9i
  - Place in: `symDataset/scaledDB/` (unzip)

## Source Verification

| Source ID              | Tier | Access | Status     |
|------------------------|------|--------|------------|
| TQAB-SC-ARXIV-PAPER   | 1    | FREE   | [VERIFIED] |
| TQAB-SC-GH-REPO       | 1    | FREE   | [VERIFIED] |
| TQAB-SC-GH-GPT4O      | 1    | FREE   | [VERIFIED] |
| TQAB-SC-GH-DBPY       | 1    | FREE   | [VERIFIED] |
| TQAB-SC-GH-UTILS      | 1    | FREE   | [VERIFIED] |
| TQAB-SC-GH-PROMPT     | 1    | FREE   | [VERIFIED] |
| TQAB-SC-EMIND-TOPIC   | 3    | FREE   | [VERIFIED] |

## Document History

**[2026-05-22 13:33]**
- Initial source collection from paper, GitHub, and EmergentMind
