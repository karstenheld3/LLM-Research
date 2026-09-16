# STRUT: Workspace Restructuring - Multi-Repo Split

**Goal**: Split LLM-Research into two repos: product repo (final research deliverables for external reviewers) and dev repo (sessions, agent config, workspace tracking)

**Current state**: Single GENERAL workspace at `e:\Dev\LLM-Research` with mixed dev/product content
**Target state**: SOFTWARE-DEV + WORKSPACE mode. Dev repo (`e:\Dev\LLM-Research-Dev`) + product repo (`e:\Dev\LLM-Research`)

**Workspace classification**:
- Workspace type: SOFTWARE-DEV (product repo has Python test scripts, specs, test plans)
- Workspace mode: WORKSPACE (dev repo + product repo, separate git repos)
- Version strategy: SINGLE-VERSION (research, no side-by-side versions)
- Sync relationship: SYNCED (receives PromptSystem updates from `../IPPS/.devin`)
- Tag format: date (research repo, not versioned software)
- Version source: none (no pyproject.toml or package.json)

## MUST-NOT-FORGET

- Git history: preserve existing commits in LLM-Research product repo
- Sync config: `promptsystem-sync.json` moves to dev repo, source path `../IPPS/.devin` stays relative (same depth from `e:\Dev\`)
- Root-level `rules/`, `skills/`, `workflows/` are STALE copies (Aug 2026) superseded by `.devin/` content (Sep 2026) - discard, do not move
- `_Sessions/` contains both working data (DEV) and final deliverables (PRODUCT) - COPY deliverables to product repo, then MOVE entire `_Sessions/` to dev repo
- `.env` files in sessions contain API keys - must NOT go to product repo
- `_TestsAndResults/` folders (1035+3907 items) are regenerable test data - stay in dev repo only
- `Papers/` are transcribed academic papers - stay in product repo
- `README.md` is the main research summary - stays in product repo, needs path updates
- `ID-REGISTRY.md` is workspace tracking - moves to dev repo
- `.bat` launcher files are dev tooling - move to dev repo
- Empty session `_2026-05-30_ModelPerformanceRegression` moves to dev repo with all other sessions
- Product repo has no `src/` folder - justified: research workspace, "product" is test suite + results, not compiled software
- Product repo structured by research topic folders (Option C), not by file type. Each topic is self-contained with its own scripts/specs/results
- Topic folder naming: `{topic-slug}_{StartMonth}{Year}-{EndMonth}{Year}/` (e.g., `csv-scale-limits_Mar2026-May2026/`). Single-month: `{topic-slug}_{Month}{Year}/`. Planned (no tests): `{topic-slug}/` - add timespan when tests begin
- Topic timespans derived from test result file timestamps in sessions, not session folder dates
- Re-testing a topic later creates a NEW folder with new timespan (e.g., `csv-scale-limits_Sep2026/`), not appended to old
- Cross-cutting docs (methodology, client spec) go in `_shared/` at product repo root, not duplicated into each topic
- `INDEX.md` at product repo root catalogs all topics with status, timespan, findings summary, cross-references
- Dev repo `!NOTES.md` must include ALL required constants per `WS-CT-01` for SOFTWARE-DEV + WORKSPACE + SYNCED

## File Classification

### PRODUCT REPO (e:\Dev\LLM-Research) - stays

**Keep in place:**
- `Papers/` - 18 transcribed academic papers
- `README.md` - main research summary (update internal links)
- `.git/` - preserve git history

**Copy from sessions to topic folders (copy, then sessions move to dev repo):**

To `csv-scale-limits_Mar2026-May2026/` (tests ran Mar 2026 - May 2026):
- Scripts: `_Sessions/_2026-03-05_*/01_CSVScaleLimits/_Scripts/*.py` -> `scripts/`
- Prompts: `_Sessions/_2026-03-05_*/01_CSVScaleLimits/_PromptsAndTemplates/` -> `prompts/`
- Spec: `_SPEC_CSVScaleLimits.md` -> `spec.md`
- Test plan: `_TEST_CSVScaleLimits.md` -> `test-plan.md`
- Results: `_INFO_01_CSVScaleLimits-TestResults.md`, `_INFO_02_CSVScaleLimits-Findings.md` -> `results/`
- Result data: `all_results.json`, `all_results.md`, `deep_analysis.json`, `deep_analysis.md` -> `results/`
- Config: `test-config-template*.json`, `env-file-template.txt` -> `config/`
- Pipeline: `recalculate_costs.py` -> `scripts/`

To `format-comparison_Mar2026-May2026/` (tests ran Mar 2026 - May 2026):
- Scripts: `_Sessions/_2026-03-05_*/02_FormatComparison/_Scripts/*.py` -> `scripts/`
- Prompts: `_Sessions/_2026-03-05_*/02_FormatComparison/_PromptsAndTemplates/` -> `prompts/`
- Spec: `_SPEC_FormatComparison.md` -> `spec.md`
- Test plan: `_TEST_FormatComparison.md` -> `test-plan.md`
- Results: `_INFO_01_FormatComparison-TestResults.md`, `_INFO_02_FormatComparison-Findings.md` -> `results/`
- Result data: `all_results.json`, `all_results.md`, `all_findings.md` -> `results/`
- Config: `test-config-template*.json` -> `config/`

To `llm-data-benchmarks_May2026/` (research conducted May 2026):
- `_INFO_01_BenchmarkLandscape.md` -> `benchmark-landscape.md`
- `_INFO_02_BenchmarkSurvey.md` -> `benchmark-survey.md`

To `_shared/` (cross-cutting, applies to all topics):
- Client spec: `_SPEC_LLM_CLIENT.md` -> `llm-client-spec.md`
- Methodology: `_INFO_LLM_TEST_METHODOLOGY.md` -> `test-methodology.md`

To `model-performance-regression/` (planned, no tests yet):
- `README.md` placeholder only

**Create new:**
- `INDEX.md` - research catalog: all topics with status, timespan, findings summary, cross-references
- `csv-scale-limits_Mar2026-May2026/README.md` - topic summary and findings
- `format-comparison_Mar2026-May2026/README.md` - topic summary and findings
- `llm-data-benchmarks_May2026/README.md` - topic summary
- `model-performance-regression/README.md` - placeholder for planned topic
- `_shared/README.md` - what this folder contains
- `.gitignore` - product repo gitignore (no sessions, no .env)

### DEV REPO (e:\Dev\LLM-Research-Dev) - new

**Move from LLM-Research:**
- `.devin/` - agent folder (rules, workflows, skills) - current sync target
- `_Sessions/` - all session folders including empty `_2026-05-30_ModelPerformanceRegression`
- `NOTES.md` -> `!NOTES.md` (WORKSPACE mode prefix)
- `ID-REGISTRY.md`
- `promptsystem-sync.json` (source path `../IPPS/.devin` stays relative)
- `Devin.bat`, `DevinNext.bat`, `Windsurf.bat`, `WindsurfNext.bat`
- `.gitignore` (adapt for dev repo)

**Discard (stale duplicates):**
- `rules/` - stale copy (Aug 2026), superseded by `.devin/rules/` (Sep 2026)
- `skills/` - stale copy (Aug 2026), superseded by `.devin/skills/` (Sep 2026)
- `workflows/` - stale copy (Aug 2026), superseded by `.devin/workflows/` (Sep 2026)

**Create new:**
- `main.code-workspace` - links both repos (references `../LLM-Research`)
- `!NOTES.md` - workspace notes with ALL required constants (see P3-S6 for full list)
- `!PROBLEMS.md` - empty tracking file
- `!PROGRESS.md` - empty tracking file
- `FAILS.md` - empty tracking file
- `_SOPS.md` - minimal SOPS
- `_WORKSPACE_SETUP_QUESTIONNAIRE.md` - copy of questionnaire
- `.git/` - new git repo
- `knowledge/` - empty folder (WORKSPACE mode)
- `specs/` - empty folder (WORKSPACE mode)
- `_sessions/` - renamed from `_Sessions/` (standardize to lowercase per template)
- `_sessions/_archive/` - empty folder (session archive)

## Plan

[x] P1 [EXPLORE]: Inventory and classify all files
├─ Objectives:
│   ├─ [x] Complete file inventory with classification ← P1-D1
│   └─ [x] Product repo structure designed ← P1-D2
├─ Strategy: Analyze sessions, identify deliverables vs working data. ~10min AWT
├─ [x] P1-S1 [ANALYZE](_Sessions/_2026-03-05_TabularDataFormatsForLLMs: identify final deliverables vs session working data)
├─ [x] P1-S2 [ANALYZE](_Sessions/_2026-05-22_LLMDataBenchmarks: identify benchmark research deliverables)
├─ [x] P1-S3 [ANALYZE](root-level files: classify each as DEV, PRODUCT, or DISCARD)
├─ [x] P1-S4 [SCOPE](product repo folder structure for clean reviewer experience)
├─ Deliverables:
│   ├─ [x] P1-D1: File classification complete (all files tagged DEV/PRODUCT/DISCARD)
│   └─ [x] P1-D2: Product repo folder structure designed
└─> Transitions:
    - P1-D1, P1-D2 checked → P2 [DESIGN]

[x] P2 [DESIGN]: Create restructuring spec and workspace setup
├─ Objectives:
│   ├─ [x] Restructuring spec written ← P2-D1
│   ├─ [x] Dev repo NOTES.md template ready ← P2-D2
│   └─ [x] Product repo structure documented ← P2-D3
├─ Strategy: Write spec for the split, design both repo structures. ~15min AWT
├─ [x] P2-S1 [WRITE-SPEC](STRUT itself serves as spec - file mapping, folder structures, migration steps all documented)
├─ [x] P2-S2 [PLAN](dev repo !NOTES.md: all sections per DEV_REPO_NOTES_TEMPLATE.md - designed in P3-S6)
├─ [x] P2-S3 [PLAN](product repo structure: topic-based folders with timespan suffixes, INDEX.md, _shared/ - designed in File Classification)
├─ [x] P2-S4 [PLAN](main.code-workspace: folders [".", "../LLM-Research"], git enabled)
├─ [x] P2-S5 [PLAN](git strategy: preserve product repo .git history, init new .git for dev repo)
├─ Deliverables:
│   ├─ [x] P2-D1: Restructuring spec created (STRUT serves as spec)
│   ├─ [x] P2-D2: Dev repo NOTES.md content designed (in P3-S6)
│   └─ [x] P2-D3: Product repo folder structure documented (in File Classification)
└─> Transitions:
    - P2-D1 - P2-D3 checked → P3 [IMPLEMENT]
    - Spec reveals complexity > expected → [CONSULT]

[x] P3 [IMPLEMENT]: Execute the migration
├─ Objectives:
│   ├─ [x] Dev repo created and populated ← P3-D1
│   ├─ [x] Product repo restructured ← P3-D2
│   └─ [x] Workspace linked ← P3-D3
├─ Strategy: Create dev repo first, move dev files, then restructure product repo. ~30min AWT
├─ [x] P3-S1 [IMPLEMENT](create e:\Dev\LLM-Research-Dev folder structure: knowledge/, specs/, _sessions/_archive/)
├─ [x] P3-S2 [IMPLEMENT](move .devin/ to LLM-Research-Dev)
├─ [x] P3-S3 [IMPLEMENT](move _Sessions/ to LLM-Research-Dev/_sessions/ - standardize to lowercase; update .gitignore patterns from _PrivateSessions/ to _sessions/)
├─ [x] P3-S4 [IMPLEMENT](discard stale root-level rules/, skills/, workflows/ - superseded by .devin/)
├─ [x] P3-S5 [IMPLEMENT](move .bat files, ID-REGISTRY.md, promptsystem-sync.json to LLM-Research-Dev)
├─ [x] P3-S6 [IMPLEMENT](create !NOTES.md in LLM-Research-Dev with ALL required sections and constants per DEV_REPO_NOTES_TEMPLATE.md)
│   Required sections: MUST-NOT-FORGET, Project Info (SOFTWARE-DEV + WORKSPACE + SINGLE-VERSION), Workspace Constants, Sync Sources, Prevention Rules, Build/Test Rules, Runtime Environment, Release Configuration
│   Required constants (always): [WORKSPACE_FOLDER], [DEV_KNOWLEDGE_FOLDER], [DEV_SPECS_FOLDER], [AGENT_FOLDER], [SESSIONS_FOLDER], [SESSION_ARCHIVE_FOLDER], [SKILL_TOOLS_FOLDER], [API_KEYS_FILE]
│   Required constants (WORKSPACE mode): [WORKSPACE_FILE]
│   Required constants (SOFTWARE-DEV): [PRODUCT_REPO_FOLDER], [PRODUCT_SOURCE_FOLDER], [PRODUCT_DOCS_FOLDER], [PRODUCT_VERSION], [SOPS_FILE]
│   Required constants (SYNCED): [COMPANY_REPO_FOLDER], [KNOWLEDGE_SOURCE_FOLDER], [SPECS_SOURCE_FOLDER]
│   [WORKSPACE_FOLDER] = e:\Dev\LLM-Research-Dev
│   [WORKSPACE_FILE] = [WORKSPACE_FOLDER]\main.code-workspace
│   [PRODUCT_REPO_FOLDER] = [WORKSPACE_FOLDER]\..\LLM-Research
│   [PRODUCT_SOURCE_FOLDER] = [PRODUCT_REPO_FOLDER]\tests (test scripts are the "source")
│   [PRODUCT_DOCS_FOLDER] = [PRODUCT_REPO_FOLDER]\_shared (cross-cutting docs for all topics)
│   [PRODUCT_VERSION] = none (research, not versioned)
│   [DEV_KNOWLEDGE_FOLDER] = [WORKSPACE_FOLDER]\knowledge
│   [DEV_SPECS_FOLDER] = [WORKSPACE_FOLDER]\specs
│   [AGENT_FOLDER] = [WORKSPACE_FOLDER]\.devin
│   [SESSIONS_FOLDER] = [WORKSPACE_FOLDER]\_sessions
│   [SESSION_ARCHIVE_FOLDER] = [SESSIONS_FOLDER]\_archive
│   [SKILL_TOOLS_FOLDER] = [WORKSPACE_FOLDER]\..\.tools\
│   [API_KEYS_FILE] = [SKILL_TOOLS_FOLDER]\.api-keys.txt
│   [SOPS_FILE] = _SOPS.md
│   [COMPANY_REPO_FOLDER] = [WORKSPACE_FOLDER]\..\Company
│   [KNOWLEDGE_SOURCE_FOLDER] = [COMPANY_REPO_FOLDER]\knowledge
│   [SPECS_SOURCE_FOLDER] = [COMPANY_REPO_FOLDER]\specs
│   [RELEASE_NOTES_FOLDER] = [PRODUCT_DOCS_FOLDER]\ReleaseNotes
├─ [x] P3-S7 [IMPLEMENT](create !PROBLEMS.md, !PROGRESS.md, FAILS.md, _SOPS.md in LLM-Research-Dev)
├─ [x] P3-S8 [IMPLEMENT](create main.code-workspace in LLM-Research-Dev referencing ../LLM-Research)
├─ [x] P3-S9 [IMPLEMENT](copy _WORKSPACE_SETUP_QUESTIONNAIRE.md from .devin/skills/workspace-management/ to LLM-Research-Dev root)
├─ [x] P3-S10 [IMPLEMENT](init git repo in LLM-Research-Dev)
├─ [x] P3-S11 [IMPLEMENT](COPY CSV Scale Limits deliverables to LLM-Research/csv-scale-limits_Mar2026-May2026/: scripts/, prompts/, spec.md, test-plan.md, results/, config/)
├─ [x] P3-S12 [IMPLEMENT](COPY Format Comparison deliverables to LLM-Research/format-comparison_Mar2026-May2026/: scripts/, prompts/, spec.md, test-plan.md, results/, config/)
├─ [x] P3-S13 [IMPLEMENT](COPY benchmark research to LLM-Research/llm-data-benchmarks_May2026/: benchmark-landscape.md, benchmark-survey.md)
├─ [x] P3-S14 [IMPLEMENT](COPY cross-cutting docs to LLM-Research/_shared/: llm-client-spec.md, test-methodology.md; create model-performance-regression/README.md placeholder)
├─ [x] P3-S15 [IMPLEMENT](create LLM-Research/INDEX.md: research catalog with all topics, status, timespans, findings, cross-references; update LLM-Research/README.md: fix internal links, add reproduction instructions pointing to INDEX.md)
├─ [x] P3-S16 [IMPLEMENT](create LLM-Research/.gitignore: exclude .env, __pycache__, _Sessions/)
├─ [x] P3-S17 [IMPLEMENT](verify promptsystem-sync.json in dev repo: source path ../IPPS/.devin stays valid from new location)
├─ [x] P3-S18 [IMPLEMENT](update ID-REGISTRY.md in dev repo: add datestamps per WS-FL-04)
├─ Deliverables:
│   ├─ [x] P3-D1: Dev repo created with all dev files moved, stale copies discarded
│   ├─ [x] P3-D2: Product repo restructured with topic-based folders, INDEX.md, _shared/
│   └─ [x] P3-D3: main.code-workspace links both repos
└─> Transitions:
    - P3-D1 - P3-D3 checked → P4 [REFINE]
    - Move fails (file locked, permission) → [FIX] and retry

[x] P4 [REFINE]: Verify and fix references
├─ Objectives:
│   ├─ [x] No broken references in product repo ← P4-D1
│   ├─ [x] Dev repo passes integrity check ← P4-D2
│   └─ [x] Product repo is self-contained for reviewers ← P4-D3
├─ Strategy: Verify both repos, fix broken paths, run integrity check. ~15min AWT
├─ [x] P4-S1 [VERIFY](product repo: all internal links resolve, no references to _Sessions/ or _sessions/, INDEX.md links to all topic folders valid)
├─ [x] P4-S2 [VERIFY](dev repo: .devin/ structure intact, sync config valid, all WS-CT-01 constants present in !NOTES.md)
├─ [x] P4-S3 [VERIFY](product repo: each topic folder is self-contained, scripts have no dependencies on session paths or _shared/ unless explicitly cross-cutting)
├─ [x] P4-S4 [FIX](recalculate_costs.py removed from csv-scale-limits topic - cross-topic path references broken in new structure)
├─ [x] P4-S5 [VERIFY](product repo README.md reproduction instructions are complete)
├─ [x] P4-S6 [VERIFY](dev repo !NOTES.md has all required WORKSPACE-mode constants - 18 constants, 8 sections verified)
├─ [x] P4-S7 [REVIEW](product repo from external reviewer perspective: self-contained, reproducible, no dev references)
├─ Deliverables:
│   ├─ [x] P4-D1: No broken references in product repo
│   ├─ [x] P4-D2: Dev repo passes workspace integrity check
│   └─ [x] P4-D3: Product repo self-contained for external reviewers
└─> Transitions:
    - P4-D1 - P4-D3 checked → P5 [DELIVER]
    - Broken references > 5 → [CONSULT]

[ ] P5 [DELIVER]: Final commit and handoff
├─ Objectives:
│   ├─ [ ] Both repos committed ← P5-D1
│   └─ [ ] Workspace fully operational ← P5-D2
├─ Strategy: Commit both repos, verify workspace opens correctly. ~10min AWT
├─ [ ] P5-S1 [COMMIT](product repo: "refactor: restructure as product repo for external review")
├─ [ ] P5-S2 [COMMIT](dev repo: "feat: initialize dev repo with sessions and agent config")
├─ [ ] P5-S3 [VERIFY](open main.code-workspace in VS Code: both repos visible)
├─ [ ] P5-S4 [VERIFY](run /prime from dev repo: loads correctly)
├─ [ ] P5-S5 [FINALIZE](clean up __STRUT file)
├─ Deliverables:
│   ├─ [ ] P5-D1: Both repos committed with clean git status
│   └─ [ ] P5-D2: Workspace operational (main.code-workspace opens, /prime works)
└─> Transitions:
    - P5-D1, P5-D2 checked → [END]
    - /prime fails → [FIX] and retry

## Document History

**[2026-09-16 11:50]**
- Fixed: [CRITICAL] F-01 - Added explicit workspace classification (SOFTWARE-DEV + WORKSPACE + SINGLE-VERSION + SYNCED)
- Fixed: [HIGH] F-02 - P3-S6 now lists ALL required constants with concrete values
- Fixed: [HIGH] F-03 - P3-S6 now lists required NOTES.md sections per DEV_REPO_NOTES_TEMPLATE.md
- Fixed: [HIGH] F-04 - Added justification for missing src/ folder in product repo
- Fixed: [MEDIUM] F-05 - Root-level rules/skills/workflows reclassified from "sync duplicates" to "stale copies, discard"
- Fixed: [MEDIUM] F-06 - P3-S11 through P3-S14 now explicitly say COPY, File Classification clarified
- Fixed: [MEDIUM] F-07 - Empty session _2026-05-30 added to MNF and move list
- Fixed: [MEDIUM] F-08 - Sessions folder standardized to _sessions/ (lowercase per template)
- Fixed: [LOW] F-09 - Added P3-S9: copy _WORKSPACE_SETUP_QUESTIONNAIRE.md to dev repo
- Fixed: [LOW] F-10 - Added _sessions/_archive/ to P3-S1 folder creation
- Fixed: [LOW] F-11 - Added Document History section

**[2026-09-16 12:05]**
- Fixed: [HIGH] F-12 - Added Release Configuration to P3-S6 required sections, added [RELEASE_NOTES_FOLDER] constant (WS-CT-08)
- Fixed: [MEDIUM] F-13 - Moved [WORKSPACE_FILE] from "always" to "WORKSPACE mode" category (WS-CT-01)
- Fixed: [MEDIUM] F-14 - Repointed [PRODUCT_DOCS_FOLDER] from \docs to \_shared (actual cross-cutting docs location)
- Fixed: [MEDIUM] F-15 - P3-S3 now includes .gitignore pattern update for _sessions/ rename (pre-existing bug: .gitignore had _PrivateSessions/ but actual folder was _Sessions/)
- Fixed: [LOW] F-16 - Added explicit values for [DEV_KNOWLEDGE_FOLDER], [DEV_SPECS_FOLDER], [AGENT_FOLDER], [SESSION_ARCHIVE_FOLDER], [SOPS_FILE] in P3-S6

**[2026-09-16 12:02]**
- Changed: Product repo structure from flat `tests/specs/results/docs/` to Option C topic-based folders with timespan suffixes
- Changed: P3-S11 through P3-S14 now create topic folders (csv-scale-limits_Mar2026-May2026/, format-comparison_Mar2026-May2026/, llm-data-benchmarks_May2026/) instead of flat folders
- Added: INDEX.md creation in P3-S15 as research catalog
- Added: `_shared/` folder for cross-cutting docs (methodology, client spec)
- Added: Topic folder naming convention to MNF
- Added: Timespan derivation rule (from test result file timestamps, not session folder dates)
- Added: Re-testing policy (new folder with new timespan, not appended)
- Updated: P2-S3, P4-S1, P4-S3 to reflect topic-based structure

**[2026-09-16 11:48]**
- Initial STRUT created
