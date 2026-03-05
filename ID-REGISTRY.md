# ID Registry

Inventory of all IDs, acronyms, and named concepts in the DevSystem.

## Frameworks

- **AGEN** - Agentic English. Controlled vocabulary for agent-human communication
- **EDIRD** - Explore, Design, Implement, Refine, Deliver. 5-phase workflow model
- **STRUT** - Structured Thinking. Method for planning and tracking complex autonomous work
- **TRACT** - Traceability concept/goal. Ensuring development artifacts remain connected from ideation to maintenance
- **TRACTFUL** - TRACT implementation via documents. Traceable Requirements Artifacts and Coded Templates For Unified Lifecycle
- **TDID** - Tractful Document ID system (defined in TRACTFUL spec section 4)

## Core Identifiers

- **TOPIC** - 2-6 uppercase letters identifying a component (e.g., `AUTH`, `CRWL`)
- **TDID** - Tractful Document ID. Format: `[TOPIC]-[DOC][NN]`
- **FEATURE_SLUG** - Kebab-case feature identifier (e.g., `user-authentication`)

## Document Type IDs

- **IN** - INFO document (research, analysis)
- **SP** - SPEC document (specifications)
- **IP** - IMPL document (implementation plan)
- **TP** - TEST document (test plan)
- **TK** - TASKS document (partitioned work items)
- **RV** - REVIEW document (review findings)
- **LN** - LEARNINGS document (retrospective analysis)

## Spec-Level Item IDs

Used in SPEC documents. Format: `[TOPIC]-[TYPE]-[NN]`

- **FR** - Functional Requirement
- **DD** - Design Decision
- **IG** - Implementation Guarantee
- **AC** - Acceptance Criterion

## Plan-Level Item IDs

Used in IMPL/TEST documents. Format: `[TOPIC]-[DOC][NN]-[TYPE]-[NN]`

- **EC** - Edge Case
- **IS** - Implementation Step
- **TC** - Test Case
- **VC** - Verification Checklist item

## Tracking Item IDs

Used in PROBLEMS.md, FAILS.md, REVIEW.md. Format: `[TOPIC]-[TYPE]-[NNN]`

- **BG** - Bug (defect in existing code)
- **FT** - Feature (new functionality request)
- **PR** - Problem (issue discovered during session)
- **FX** - Fix (documented fix for a problem)
- **TK** - Task (general work item)
- **RV** - Review finding
- **FL** - Failure log entry
- **LN** - Learning entry

## Source IDs (INFO documents)

Format: `[TOPIC]-[DOC]-SC-[SOURCE_ID]-[SOURCE_REF]`

- **SC** - Source marker

## Agentic concepts and strategies

- **PREN** - "Proper english" - precise natural language avoiding confusion, ambiguities, term conflicts 
- **AGEN** - "Agentic english" - proper english, enriched with semantics like `@mentions`, `/workflow`, `[INSTRUCTION]`, etc.
- **HWT** - Human Work Time. Example: "max 0.5h HWT per task"
- **AWT** - Agentic Work Time. Agent time estimate. Example: "complete in < 5mins AWT"
- **MEPI** - Most Executable Point of Information (used for research and decision making)
- **MCPI** - Most Complete Point of Information (used for research)
- **SOCAS** - Signs Of Confusion And Sloppiness (10 criteria)
- **MNF** - Must Not Forget. Technique for critical item tracking during task execution
- **ASANAPAP** - As Short As Necessary, As Precise As Possible. Conciseness principle for workflows and documents
- **VCRIV** - Verify, Critique, Reconcile, Implement, Verify. Standard quality control pipeline for document review cycles. Runs `/verify` → `/critique` → `/reconcile` → `/implement` → `/verify`

## States (no brackets)

### Workflow Types
- **BUILD** - Primary output is working code
- **SOLVE** - Primary output is knowledge/decisions/documents

### Complexity (BUILD)
- **COMPLEXITY-LOW** - Single file, clear scope (patch version)
- **COMPLEXITY-MEDIUM** - Multiple files, some dependencies (minor version)
- **COMPLEXITY-HIGH** - Breaking changes, new patterns (major version)

### Problem Types (SOLVE)
- **RESEARCH** - Explore topic, gather information
- **ANALYSIS** - Deep dive into data or situation
- **EVALUATION** - Compare options, make recommendations
- **WRITING** - Create documents, books, reports
- **DECISION** - Choose between alternatives
- **HOTFIX** - Production down
- **BUGFIX** - Defect investigation
- **CHORE** - Maintenance analysis
- **MIGRATION** - Data or system migration

### Workspace Context
- **SINGLE-PROJECT** - Workspace contains one project
- **MONOREPO** - Workspace contains multiple projects
- **SINGLE-VERSION** - One active version
- **MULTI-VERSION** - Side-by-side versions
- **SESSION-BASED** - Time-limited session with specific goals
- **PROJECT-WIDE** - Work spans entire project

### Operation Modes
- **IMPL-CODEBASE** - Output to project source folders (default)
- **IMPL-ISOLATED** - Output to session folder only (POCs, prototypes)

## Labels

### Severity
- **[CRITICAL]** - Production failure risk
- **[HIGH]** - Likely failure under normal conditions
- **[MEDIUM]** - Edge case failure risk
- **[LOW]** - Minor issue

### Assumption
- **[VERIFIED]** - Confirmed correct
- **[UNVERIFIED]** - Made without evidence
- **[CONTRADICTS]** - Conflicted with reality
- **[OUTDATED]** - May no longer be valid
- **[INCOMPLETE]** - Missing critical considerations

### Status
- **[RESOLVED]** - Issue fixed
- **[WONT-FIX]** - Accepted trade-off
- **[NEEDS-DISCUSSION]** - Requires consultation

## Tracking Documents

- **NOTES** - Key decisions, topic registry, current phase
- **PROGRESS** - To Do, In Progress, Done, phase plan
- **PROBLEMS** - Issues discovered during session
- **FAILS** - Failure log (what went wrong)
- **LEARNINGS** - Retrospective analysis (via `/learn`)

## Project Topics



## Document History
