# TQA-Bench Dataset Downloads

Download these files manually (OneDrive links, require browser):

## Task File (Questions + Ground Truth)

- **URL**: https://hkustconnect-my.sharepoint.com/:u:/g/personal/zqiuao_connect_ust_hk/EWAnhWoIhJpIgkkge1ZoBoYB7eF1AgJbcfV4nDfpFLua4A?e=727pOz
- **Save as**: `dataset.sqlite`
- **Content**: 10 database question tables, each with (scale, dbIdx, sampleIdx, questionIdx, qtype, question, rightIdx, A, B, C, D)

## Scaled Database Files (Pre-sampled Instances)

- **URL**: https://hkustconnect-my.sharepoint.com/:u:/g/personal/zqiuao_connect_ust_hk/ESGMS0lh1l9MirS9SvS7_E0BSpBXpml7OsCdc0oLx70b_A?e=AgHy9i
- **Save as**: Unzip into this folder
- **Content**: SQLite databases at 4 scales (8k, 16k, 32k, 64k), 10 databases, 10 instances each

## GitHub Repository

```
git clone https://github.com/Relaxed-System-Lab/TQA-Bench.git
```

## After Download

Expected structure:
```
_DOWNLOADS_gitignore/
├── README.md (this file)
├── dataset.sqlite
├── scaledDB/
│   ├── 8k/
│   ├── 16k/
│   ├── 32k/
│   └── 64k/
└── TQA-Bench/  (git clone)
```
