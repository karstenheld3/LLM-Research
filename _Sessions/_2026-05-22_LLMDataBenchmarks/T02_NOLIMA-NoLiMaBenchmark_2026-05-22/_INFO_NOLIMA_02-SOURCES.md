<DevSystem MarkdownTablesAllowed=true />

# INFO: NoLiMa Sources

**Doc ID**: NOLIMA-IN02
**Goal**: Collected sources for NoLiMa benchmark deep-research
**Preflight accuracy**: N/A (expanding known benchmark from survey)

## Source List

- **NOLIMA-SC-ARXIV-PAPER**
  - Title: "NoLiMa: Long-Context Evaluation Beyond Literal Matching"
  - URL: https://arxiv.org/abs/2502.05167
  - Type: Academic paper (Tier 1)
  - Accessed: 2026-05-22
  - Label: [VERIFIED]

- **NOLIMA-SC-ARXIV-HTML**
  - Title: NoLiMa paper full HTML version
  - URL: https://arxiv.org/html/2502.05167v1
  - Type: Full paper with all sections, tables, appendices (Tier 1)
  - Accessed: 2026-05-22
  - Label: [VERIFIED]

- **NOLIMA-SC-GH-REPO**
  - Title: adobe-research/NoLiMa GitHub repository
  - URL: https://github.com/adobe-research/NoLiMa
  - Type: Official code repository with evaluation scripts and results (Tier 1)
  - Accessed: 2026-05-22
  - Label: [VERIFIED]
  - Note: Updated 2025-07-17 with GPT-o3 and GPT-o4 Mini results

- **NOLIMA-SC-GH-README**
  - Title: NoLiMa README.md (raw) with full results tables
  - URL: https://raw.githubusercontent.com/adobe-research/NoLiMa/main/README.md
  - Type: Results tables with all model scores (Tier 1)
  - Accessed: 2026-05-22
  - Label: [VERIFIED]

- **NOLIMA-SC-HF-DATA**
  - Title: amodaresi/NoLiMa HuggingFace Dataset
  - URL: https://huggingface.co/datasets/amodaresi/NoLiMa
  - Type: Dataset repository with needlesets and haystacks (Tier 1)
  - Accessed: 2026-05-22
  - Label: [VERIFIED]

- **NOLIMA-SC-ADOBE-PUB**
  - Title: Adobe Research publication page
  - URL: https://research.adobe.com/publication/nolima-long-context-evaluation-beyond-literal-matching/
  - Type: Official publication page (Tier 2)
  - Accessed: 2026-05-22
  - Label: [VERIFIED]

## Related / Easily Confused

- **BABILong** (Kuratov et al., NeurIPS 2024) - Tests reasoning degradation with scale using bAbI tasks; NoLiMa specifically removes literal matching
- **RULER** (Hsieh et al., 2024) - Synthetic long-context benchmark; NoLiMa shows RULER scores do NOT predict NoLiMa performance
- **HELMET** (Yen et al., ICLR 2025) - Holistic long-context evaluation; broader task diversity but no literal-match control

## Document History

**[2026-05-22 13:33]**
- Initial source collection (6 sources, all Tier 1-2)
