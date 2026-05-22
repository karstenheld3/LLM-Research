# Topic Folder Notes

**Doc ID**: 2026-05-22_NOLIMA-NOTES

## Topic Info

- **Topic**: NoLiMa Benchmark Deep-Research
- **Topic ID**: NOLIMA
- **Created**: 2026-05-22
- **Parent Session**: `_2026-05-22_LLMDataBenchmarks`
- **Strategy**: MCPI (exhaustive)
- **Domain**: SOFTWARE

## Current Phase

**Phase**: RESEARCH (Phase 3)
**Status**: Writing research files

## Key Facts

- **Full name**: NoLiMa: Long-Context Evaluation Beyond Literal Matching
- **Authors**: Ali Modarressi, Hanieh Deilamsalehy, Franck Dernoncourt, Trung Bui, Ryan A. Rossi, Seunghyun Yoon, Hinrich Schutze (Adobe Research + LMU Munich)
- **Venue**: ICML 2025 (poster)
- **arXiv**: 2502.05167 (February 2025)
- **Code**: github.com/adobe-research/NoLiMa
- **Dataset**: huggingface.co/datasets/amodaresi/NoLiMa
- **License**: Adobe Research License (non-commercial research only)

## Important Findings

- GPT-4.1 achieves best effective length (16K) among non-reasoning models
- GPT-o3 is best reasoning model on NoLiMa-Hard (58.5% at 32K)
- 10/12 original models drop below 50% of base score at 32K
- Even reasoning models (o1, o3) cannot fully solve the task at 32K
- NoLiMa directly validates our "comprehension > retrieval" finding
- No model achieves full-length generalization without literal matches
