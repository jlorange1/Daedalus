# Task Graph

## Active Goal

Build a Mythos-class inspired, safe orchestration scaffold for Daedalus using parallel specialist agents, Markdown memory, skills, evals, defensive review, and operator controls.

## Planning Notes

- This graph preserves the original Wave A-D structure while expanding each wave into small implementation units.
- Status values: `blocked`, `pending`, `ready`, `in_progress`, `review`, `done`.
- Parallel execution is allowed only when write scopes do not overlap.
- Safety review may run read-only at any time. Safety fixes must become normal graph tasks before implementation.

## Wave A: Foundation And Repository Understanding

| ID | Task | Dependencies | Owner | Status | Risk |
|---|---|---|---|---|---|
| A1 | Create AGENTS, docs, memory scaffold | none | prime | done | low |
| A2 | Phase 1 specialist repo understanding | A1 | parallel agents | done | low |
| A2.1 | Map dashboard frontend, selectors, assets, and UI fallback data | A1 | repo_cartographer | done | low |
| A2.2 | Map backend API, queue lifecycle, worker autonomy gates, and cron entry points | A1 | repo_cartographer | done | low |
| A2.3 | Map safety, legal branding, secrets, and destructive-action boundaries | A1 | safety_reviewer | done | low |
| A2.4 | Map current tests, smoke checks, eval docs, and missing validation | A1 | test_engineer | done | low |
| A3 | Prime synthesis into memory and next-wave readiness | A2.1,A2.2,A2.3,A2.4 | prime | done | low |

## Wave B: Orchestration Core And Memory

| ID | Task | Dependencies | Owner | Status | Risk |
|---|---|---|---|---|---|
| B1 | Design Markdown task graph parser/writer that preserves hand-written notes | A3 | implementation_planner | pending | medium |
| B1.1 | Add round-trip fixture tests for task graph parsing and serialization | B1 | test_engineer | pending | low |
| B1.2 | Add task fields for dependency, owner, status, risk, write scope, and validation command | B1 | implementation | pending | medium |
| B2 | Define specialist role registry for repo, architecture, implementation, memory, evals, safety, tests, docs | A3 | architecture_planner | pending | low |
| B2.1 | Map registry roles to existing CrewAI/OpenClaw agent IDs and fallback labels | B2 | implementation | pending | low |
| B2.2 | Add parallel conflict detector for overlapping write scopes | B1.2,B2 | implementation | pending | medium |
| B3 | Add memory update utility and policy for project memory, decisions, open questions, failed attempts | A3 | memory_system_designer | pending | medium |
| B3.1 | Add temp-directory tests for memory update utility | B3 | test_engineer | pending | low |
| B4 | Expose read-only task graph summary in `/api/status` | B1,B2 | implementation | pending | medium |

## Wave C: Validation And Safety Gates

| ID | Task | Dependencies | Owner | Status | Risk |
|---|---|---|---|---|---|
| C1 | Add API schema tests for `/api/status`, `/api/enqueue`, and `/api/action` | A3 | test_engineer | pending | low |
| C1.1 | Test work-order filename slug generation, title extraction, and status moves | C1 | test_engineer | pending | low |
| C2 | Add eval harness for routing, safety fallback, and memory update behavior | B1,B2,B3 | evals_designer | pending | low |
| C2.1 | Add unsafe/ambiguous automation eval cases from safety boundaries | C2 | safety_reviewer | pending | medium |
| C3 | Add dashboard smoke checks for core selectors, keyboard focus, panel visibility, and console errors | A3 | test_engineer | pending | low |
| C4 | Run validation commands and record results | C1,C2,C3 | prime | pending | low |

## Wave D: Dashboard Operator Console

| ID | Task | Dependencies | Owner | Status | Risk |
|---|---|---|---|---|---|
| D1 | Add reduced-motion CSS and clamp progress values client-side | A3 | frontend | pending | low |
| D2 | Add visible stale/offline state when `/api/status` fetch fails | A3 | frontend | pending | low |
| D3 | Implement real sidebar panel switching for Studio, Queue, Builds, GitHub, Cron, Settings | D1,D2 | frontend | pending | medium |
| D4 | Add full Queue panel using live queue lists and task graph references | D3,B4 | frontend | pending | medium |
| D5 | Add read-only Settings diagnostics for env/readiness without exposing secrets | D3 | frontend/backend | pending | medium |
| D6 | Add confirmation dialogs for `run-duo`, `run-once`, `cron-tick`, and future push/build actions | D3 | frontend | pending | medium |
| D7 | Add backend action preconditions and enforce autonomy/readiness gates before spawning | C1,D6 | backend | pending | high |
| D8 | Add redacted read-only action log tail | D7 | backend/frontend | pending | medium |

## Wave E: Skills And Repeatable Procedures

| ID | Task | Dependencies | Owner | Status | Risk |
|---|---|---|---|---|---|
| E1 | Create orchestration skill for decomposition, routing, conflict checks, synthesis | B1,B2 | docs_and_operator_guide_writer | done | low |
| E2 | Create Obsidian memory skill for project memory update policy | B3 | memory_system_designer | done | low |
| E3 | Create evals skill for running and extending smoke/eval harnesses | C2 | evals_designer | done | low |
| E4 | Create RSPS Java workflow skill after toolchain requirements are confirmed | Java decision | docs_and_operator_guide_writer | done | medium |
| E5 | Create Vibe-Kanban workspace skill | A3 | docs | done | low |
| E6 | Create n8n MCP automation contract skill | A3 | docs | done | low |

## Wave F: Real Data, Integration, And Release Readiness

| ID | Task | Dependencies | Owner | Status | Risk |
|---|---|---|---|---|---|
| F1 | Inventory every visual/demo data path in frontend and backend | A2.1,A2.2 | repo_cartographer | done | low |
| F2 | Add explicit `demo` or `fallback` flags where seeded visuals remain intentional | F1 | implementation | dropped | medium |
| F3 | Remove unlabelled visual fallback backlog and render clear empty state | F1 | frontend | done | medium |
| F3.1 | Delete unused dashboard mock JSON fixtures and mock manifest | F1 | frontend | done | low |
| F4 | Run safe docs-only end-to-end work order through enqueue, status, and memory update | B3,D7 | prime/test | pending | medium |
| F5 | Run full local validation suite | C4,D8,F3 | test_engineer | pending | low |
| F6 | Defensive safety review before release handoff | F5 | safety_reviewer | pending | medium |
| F7 | Update operator guide with exact runbook and next actions | F4,F5,F6 | docs_and_operator_guide_writer | pending | low |

## Parallelization Plan

Safe parallel groups:

| Group | Tasks | Reason |
|---|---|---|
| P1 | A2.1, A2.2, A2.3, A2.4 | Read-only repository understanding with distinct review domains |
| P2 | B2, B3, C1 initial fixture design | Distinct files once task graph writer design is known |
| P3 | D1, D2, C1.1 | Frontend reliability and backend tests touch separate surfaces |
| P4 | E1, E2, E3 | Skill docs are independent after their source systems exist |
| P5 | F5 prep, F6 read-only review, F7 draft notes | Validation, review, and docs can proceed after integration snapshot |

Serialized zones:

| Zone | Tasks | Reason |
|---|---|---|
| S1 | B1, B1.1, B1.2 | Parser/writer and graph schema must preserve content exactly |
| S2 | B2.2, D7 | Conflict detection and action spawning are safety-critical |
| S3 | D3, D4, D5, D6 | Broad frontend state and panel routing can conflict in `app.js` |
| S4 | F2, F3 | Demo/fallback semantics must be consistent across API and UI |
| S5 | F4 | End-to-end work-order run should be observed as a single integration event |

## Testable Unit Contract

Each implementation task should declare before coding:

- Write scope: exact files or directories.
- Safety level: read-only, docs-only, local state, external process, git write, or blocked.
- Validation: command, unit test, smoke check, or manual verification.
- Memory impact: whether `PROJECT_MEMORY.md`, `DECISIONS.md`, `OPEN_QUESTIONS.md`, `FAILED_ATTEMPTS.md`, or this graph must change.

## Blockers

- Build/Test dashboard actions remain disabled until command execution, timeout, and log handling are specified.
- External worker spawning must remain gated by `RSPS_ALLOW_AUTONOMOUS` and backend preconditions.

## Current Next Actions

1. Start B1 with a fixture-based task graph parser/writer.
2. Prepare C1 API schema tests and D1/D2 low-risk dashboard reliability fixes in parallel.
3. Harden dashboard mutating endpoints before enabling remote access or autonomous runs.
4. Add service-level run manifests before deeper worker automation.
