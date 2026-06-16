# Implementation Plan

## Purpose

Convert Daedalus from a dashboard-plus-worker scaffold into a reliable orchestration system for AI-assisted RSPS development. The implementation should proceed in small, testable slices that preserve operator control, Markdown memory, safety boundaries, and safe parallel work.

## Guardrails

- Keep the dashboard operational as the first screen.
- Keep autonomous execution gated by `RSPS_ALLOW_AUTONOMOUS`.
- Do not expose `.env`, API keys, worker prompts, or unredacted logs.
- Do not add offensive security, unauthorized scanning, exploit, malware, evasion, or credential-harvesting capability.
- Prefer Markdown-backed state until a stronger persistence layer is justified.
- Keep parallel agents on disjoint write scopes. If two tasks need the same file, serialize or merge manually.
- Every implementation slice must have a direct smoke check, unit test, or documented manual verification.

## Stage 0: Baseline And Freeze Points

Goal: establish the known-good behavior before orchestration changes begin.

| Unit | Scope | Owner | Parallel Safe | Verification |
|---|---|---|---|---|
| 0.1 | Record current commands, env assumptions, and smoke checks in docs/memory | docs | yes | `uv run rsps-worker status` |
| 0.2 | Add or confirm dashboard asset/static JSON validation commands | test | yes | `python3 scripts/dashboard_assets.py` and JSON parse command from memory |
| 0.3 | Capture `/api/status` sample for configured and missing RSPS repo states | test | yes | Start `uv run rsps-dashboard`, request `/api/status` |

Exit criteria:

- Current dashboard, queue, worker status, and asset checks are reproducible.
- Any missing external tools are documented as readiness failures, not treated as app crashes.

## Stage 1: Task Graph And Memory Core

Goal: make the architecture loop concrete: operator goal -> task graph -> status updates -> memory update.

| Unit | Scope | Owner | Parallel Safe | Verification |
|---|---|---|---|---|
| 1.1 | Define a Markdown task graph parser/writer for active goal, waves, task rows, blockers | implementation | no | Unit tests with round-trip fixture |
| 1.2 | Add task metadata fields: dependencies, owner role, status, risk, write scope, validation | implementation | no | Parser rejects malformed rows and preserves unknown text |
| 1.3 | Add memory update policy helpers for project memory, decisions, failed attempts, open questions | memory | yes after 1.1 | Unit tests use temporary memory directory |
| 1.4 | Expose read-only task graph summary through dashboard status | implementation | yes after 1.1 | `/api/status` includes task graph summary without secrets |

Exit criteria:

- `memory/TASK_GRAPH.md` can be read, updated, and preserved without losing hand-written notes.
- Dashboard can show planning state without running worker actions.

## Stage 2: Specialist Role Registry

Goal: route work by explicit role, risk, dependency, and write scope.

| Unit | Scope | Owner | Parallel Safe | Verification |
|---|---|---|---|---|
| 2.1 | Define role registry for repo cartography, architecture, implementation, memory, evals, safety, tests, docs | architecture | yes | Static registry test checks required roles |
| 2.2 | Map role registry to existing CrewAI/OpenClaw agent names where available | implementation | yes after 2.1 | Unit test validates configured IDs and fallback labels |
| 2.3 | Add routing decision object: task ID, role, write scope, approval needs, validation command | implementation | no | Unit tests for safe/unsafe routing examples |
| 2.4 | Add conflict detector for overlapping write scopes before parallel dispatch | implementation | no | Tests cover same-file, same-directory, docs-only, and read-only cases |

Exit criteria:

- Daedalus can explain why a task is routed to a role.
- Parallel work is blocked when write scopes overlap.

## Stage 3: Work Order Lifecycle Hardening

Goal: make queue transitions and worker runs auditable and recoverable.

| Unit | Scope | Owner | Parallel Safe | Verification |
|---|---|---|---|---|
| 3.1 | Add tests for work-order creation, slug generation, title extraction, and status moves | test | yes | `uv run pytest` |
| 3.2 | Add lifecycle metadata to work orders: task graph ID, owner role, validation command, created/updated time | implementation | no | Existing work orders still load |
| 3.3 | Record worker result summary beside done/failed orders without leaking prompts or secrets | implementation | no | Failed mock run produces redacted summary |
| 3.4 | Add recovery notes path for repeated failures | memory | yes after 3.3 | Failed task references `memory/FAILED_ATTEMPTS.md` guidance |

Exit criteria:

- A work order can be traced from task graph row to queue file to worker result.
- Failed work has enough information to retry safely.

## Stage 4: Dashboard Reliability And Panels

Goal: finish the static dashboard as an operator console for orchestration state.

| Unit | Scope | Owner | Parallel Safe | Verification |
|---|---|---|---|---|
| 4.1 | Add reduced-motion CSS and clamp progress values client-side | frontend | yes | Browser smoke check, no console errors |
| 4.2 | Add offline/stale state for `/api/status` failures | frontend | yes | Simulated failed fetch shows visible stale state |
| 4.3 | Implement real panel switching for Studio, Queue, Builds, GitHub, Cron, Settings | frontend | no | Every sidebar button changes visible panel and active state |
| 4.4 | Expand Queue panel to full queue lists and task graph references | frontend | yes after 4.3 | Empty and populated lanes render clearly |
| 4.5 | Add read-only Settings diagnostics for env/readiness | frontend/backend | yes after 4.3 | No `.env` values or secrets exposed |

Exit criteria:

- Operators can inspect queue, readiness, logs, and task state without shell access.
- Missing RSPS repo, missing Java, missing Git LFS, dirty git state, and empty queue states are explicit.

## Stage 5: Safe Action Workflows

Goal: make all state-changing dashboard actions deliberate, visible, and bounded.

| Unit | Scope | Owner | Parallel Safe | Verification |
|---|---|---|---|---|
| 5.1 | Add confirmation dialog for `run-duo`, `run-once`, `cron-tick`, and future push/build actions | frontend | yes | Keyboard and pointer confirmation paths work |
| 5.2 | Add backend precondition response for autonomy, RSPS repo, Java, Git LFS, and OpenClaw | backend | yes | API tests cover pass/fail preconditions |
| 5.3 | Gate `/api/action` on preconditions before spawn | backend | no | `RSPS_ALLOW_AUTONOMOUS=false` cannot spawn workers |
| 5.4 | Add read-only action log tail with redaction | backend/frontend | yes after 5.2 | Secret-like values are not returned in log payloads |
| 5.5 | Keep Build/Test commands disabled until timeout and log handling are specified | safety | yes | UI shows gated state, not executable command |

Exit criteria:

- Dangerous or expensive actions require confirmation and clear precondition success.
- Failed actions display an error, failed precondition, or log location.

## Stage 6: Evals And Smoke Harness

Goal: create repeatable checks for orchestration quality, dashboard stability, and safety.

| Unit | Scope | Owner | Parallel Safe | Verification |
|---|---|---|---|---|
| 6.1 | Add API schema tests for `/api/status`, `/api/enqueue`, and `/api/action` | test | yes | `uv run pytest` |
| 6.2 | Add task graph fixture tests for dependency ordering and conflict detection | test | yes after Stage 2 | `uv run pytest` |
| 6.3 | Add dashboard smoke test for core selectors and keyboard focus | test/frontend | no | Playwright or equivalent browser smoke check |
| 6.4 | Add safety eval cases for unsafe task requests and ambiguous automation | safety/evals | yes | Eval harness routes to safe fallback |
| 6.5 | Add memory eval: completed work updates task graph and relevant memory files | evals | yes | Eval fixture validates expected Markdown changes |

Exit criteria:

- A local validation run can catch broken API shape, unsafe routing, missing selectors, and memory regressions.

## Stage 7: Skill Packs And Operator Procedures

Goal: turn repeated procedures into reusable project skills.

| Unit | Scope | Owner | Parallel Safe | Verification |
|---|---|---|---|---|
| 7.1 | Create orchestration skill for decomposition, routing, conflict checks, and synthesis | docs/skills | yes | Skill references task graph format |
| 7.2 | Create Obsidian memory skill for project memory update policy | docs/skills | yes | Skill links memory files and examples |
| 7.3 | Create evals skill for running and extending smoke/eval harnesses | docs/skills | yes | Skill references exact commands |
| 7.4 | Create RSPS Java workflow skill after toolchain requirements are confirmed | docs/skills | blocked by Java decision | Skill includes build/test commands and prerequisites |

Exit criteria:

- New agents can follow repository-native procedures without rediscovering conventions.

## Stage 8: Real Data And Mock Removal

Goal: replace visual/demo state with explicit live, empty, or demo modes.

| Unit | Scope | Owner | Parallel Safe | Verification |
|---|---|---|---|---|
| 8.1 | Inventory every fallback/demo data path in frontend and backend | repo_cartographer | yes | Checklist links selectors/functions |
| 8.2 | Add explicit `demo` or `fallback` flags where seeded visuals remain intentional | backend/frontend | no | API and UI label demo state clearly |
| 8.3 | Remove unlabelled visual fallback backlog | frontend | yes after 8.2 | Empty queue renders professional empty state |
| 8.4 | Update docs and screenshots after mock removal | docs | yes after 8.3 | Component map and build plan match behavior |

Exit criteria:

- Operators can distinguish live data, empty state, demo state, and unavailable data.

## Stage 9: Integration And Release Readiness

Goal: prove the full loop works end to end.

| Unit | Scope | Owner | Parallel Safe | Verification |
|---|---|---|---|---|
| 9.1 | Run a safe docs-only work order through enqueue, worker gate, status, and memory update | prime/test | no | Queue transition and memory update observed |
| 9.2 | Run full local validation suite | test | no | Asset checks, JSON parse, pytest, dashboard smoke |
| 9.3 | Perform defensive safety review | safety | yes after 9.2 | Findings resolved or logged |
| 9.4 | Update operator guide with exact runbook | docs | yes after 9.1 | Runbook follows current commands |

Exit criteria:

- Daedalus can decompose, route, display, validate, and record a bounded task without unsafe side effects.

## Safe Parallelization Map

Parallel-safe work streams:

- Documentation and skills can proceed beside backend tests when they touch distinct files.
- Frontend panel implementation can proceed beside backend API schema tests only after the API contract is stable.
- Evals can proceed beside memory helpers when fixtures use temporary directories.
- Safety review can proceed read-only at any time, then fixes should be scheduled as normal task graph items.

Serialize these areas:

- `memory/TASK_GRAPH.md` parser/writer changes and task graph content edits.
- `/api/action` spawning, precondition, and log-redaction changes.
- Frontend panel routing and broad `app.js` state changes.
- Any worker lifecycle change that moves queue files or starts external agents.

## Minimum Verification Set

Use this set before merging a staged slice when applicable:

```bash
python3 scripts/dashboard_assets.py
```

```bash
python3 -c "import json, pathlib; root=pathlib.Path('src/rsps_crewai_team/dashboard_static'); [json.loads(p.read_text()) for p in root.glob('**/*.json')]; print('json ok')"
```

```bash
uv run rsps-worker status
```

```bash
uv run pytest
```

```bash
uv run rsps-dashboard
```
