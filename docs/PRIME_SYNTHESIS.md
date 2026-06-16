# Prime Synthesis

Generated: 2026-06-16

Post-synthesis implementation update: Wave A was completed, project skills were created and installed by symlink, a user-local Java 11/Maven/Git LFS toolchain was installed, the Codex agent config was updated, and unlabelled dashboard mock data was removed in favor of live empty states.

## What The Repo Is

Daedalus is a local-first AI game-development studio scaffold for RSPS-oriented work. It combines:

- CrewAI planning through `rsps-team`.
- Filesystem work orders through `rsps-worker`.
- OpenClaw/custom coding-worker execution.
- Cron automation through `rsps-cron`.
- Git/worktree helpers.
- A static sci-fi dashboard served by `rsps-dashboard`.
- Markdown memory and evaluation scaffolding.

The repository is primarily Python with a plain HTML/CSS/JavaScript dashboard. It uses `uv`, Hatchling, CrewAI, OpenRouter, `python-dotenv`, Pillow for the asset script, and no JavaScript build system.

## Phase 1 Agent Outputs

| Agent | Output | Key Finding |
|---|---|---|
| `repo_cartographer` | `docs/REPO_MAP.md` | Main entry points are the `rsps-*` console scripts; high-risk files are worker execution, shell build/test commands, dashboard actions, and Git sync. |
| `architecture_planner` | `docs/TARGET_ARCHITECTURE.md` | Keep the local filesystem/Markdown model but introduce domain, service, adapter, and interface boundaries incrementally. |
| `implementation_planner` | `docs/IMPLEMENTATION_PLAN.md`, `memory/TASK_GRAPH.md` | Next work should proceed in staged slices: baseline, task graph/memory core, role registry, work-order hardening, dashboard reliability, safe actions, evals, skills, mock removal. |
| `memory_system_designer` | `docs/MEMORY_SYSTEM.md`, `memory/PROJECT_MEMORY.md` | Markdown memory should be human-readable, Git-reviewable, Obsidian-compatible, and updated only for durable facts. |
| `evals_and_benchmark_designer` | `docs/EVALS.md`, `evals/README.md`, `evals/run_static_evals.py`, `evals/score_agent_trace.py` | Evals should measure orchestration quality and safety with deterministic local checks plus trace scoring. |
| `safety_and_defensive_security_reviewer` | `docs/DEFENSIVE_SECURITY_REVIEW.md` | No confirmed critical issues; high risks are unauthenticated dashboard actions, shell build/test execution, prompt injection in work orders, and status/log disclosure. |
| `test_engineer` | `docs/TEST_PLAN.md`, `tests/test_work_orders_smoke.py` | Minimal unittest smoke tests now cover work-order lifecycle; missing coverage is documented. |
| `docs_and_operator_guide_writer` | `docs/OPERATOR_GUIDE.md` | Operator guide now covers setup, dashboard, work orders, Codex agents, safety, evals, and recovery. |

## External Patterns To Integrate

### Vibe-Kanban Pattern

The public Vibe-Kanban repo describes a workflow centered on kanban planning, agent workspaces, branches, terminals, dev servers, diff review, app preview, agent switching, and PR handoff. Daedalus should adopt the pattern, not the implementation:

- Make work visible as cards, owners, branches, validation, and status.
- Treat each agent run as a workspace with a branch/worktree, logs, and reviewable output.
- Put diff review and validation results in the operator loop before merge/push.

### n8n-MCP Pattern

The n8n MCP concept is useful as an integration pattern:

- Model external automations as explicit tool/node contracts.
- Keep generated workflows reviewable before execution.
- Prefer small validated nodes over opaque broad automation.

Daedalus should expose future automations through explicit action manifests, preconditions, safety gates, and evals.

### Skill Architecture Pattern

Reusable agent procedures should live in `skills/<skill-name>/SKILL.md`. Skills should be concise, procedural, and triggered only when relevant. Project-native skills should cover orchestration, Obsidian memory, evals, Vibe-Kanban-style workspaces, n8n-MCP-style automation, and RSPS Java workflow.

### Obsidian Memory Pattern

The `/memory` directory is the project vault. Files should use stable Markdown names, short sections, normal links, and Obsidian-compatible wiki links when helpful. Memory should be versioned and reviewed like source.

## What Is Broken Or Missing

1. There is no central orchestration service yet; CLI, cron, dashboard, and workers still call implementation modules directly.
2. Work orders are Markdown files, but lifecycle metadata, run manifests, validation records, and retry state are not yet structured.
3. Dashboard mutating endpoints have no auth token or CSRF/origin protection.
4. Build/test commands use shell strings from environment configuration.
5. Work-order bodies are sent to coding agents as raw prompt content without a strong untrusted-data boundary.
6. `/api/status` can expose log tails, paths, commands, Git metadata, and other diagnostics too broadly.
7. Dashboard mutating endpoints still need auth/origin hardening.
8. Work-order run manifests and structured retry state are not yet implemented.
9. Service-level task graph/memory utilities still need code implementation.
10. Dashboard/API smoke coverage needs to expand beyond the initial work-order smoke tests.

## Highest-Leverage Improvements

1. Add safe service boundaries around work orders, actions, readiness, memory, and dashboard status.
2. Create project skills so future Codex runs load only the needed procedure.
3. Add run manifests and structured task graph data.
4. Preserve live data and explicit empty states; only add demo data later behind an operator-visible demo mode.
5. Harden dashboard actions with token/origin gates and precondition checks.
6. Add evals into the default validation path.
7. Install/confirm Java after reading the RSPS source requirements.

## Final Architecture Direction

Keep the repo local-first and Markdown/filesystem-backed for now. Evolve toward:

- `domain`: pure task graph, work order, run, policy, memory models.
- `services`: planning, work order, execution, dashboard, memory, readiness, eval, safety.
- `adapters`: CrewAI, coding CLI, Git, filesystem, Markdown, shell, clock.
- `interfaces`: CLI, dashboard API, cron, future MCP/n8n nodes.

This should be incremental. Do not do a sweeping directory rewrite before tests cover the current behavior.

## Implementation Sequence

1. Finish Wave A foundation: docs, memory, repo map, synthesis, test plan, eval plan.
2. Project skills under `/skills` are complete and symlinked into `~/.codex/skills`.
3. Codex agent thread settings are applied in `~/.codex/config.toml`.
4. Java 11, Maven, and Git LFS are installed user-locally for the RSPS source.
5. Frontend mock data was replaced with explicit empty states.
6. Add service-level task graph/memory utilities.
7. Add run manifests and safer work-order prompt boundaries.
8. Harden dashboard mutating endpoints.
9. Add dashboard/API smoke tests and eval result reports.

## Risks

- Autonomous worker paths can modify or commit code when enabled.
- Dashboard actions are currently local-only by default but still unauthenticated.
- Empty queue lanes are intentional when no live work orders exist.
- User-local Java/Maven/Git LFS avoids OS layering changes but depends on `~/.local/bin` staying on `PATH`.
- Skills are loaded through symlinks in `~/.codex/skills`; if the repo moves, refresh those symlinks.

## First Execution Wave

Proceed with these disjoint tasks:

1. Implement service-level task graph and memory update utilities.
2. Add structured run manifests for work-order executions.
3. Harden dashboard mutating endpoints with local auth/origin checks.
4. Expand dashboard/API smoke tests.
5. Run static evals, unittest smoke tests, asset validation, and JSON validation after each wave.

## Safety Notes

All orchestration improvements must stay defensive and operator-controlled. Do not add bypasses for autonomy gates. Do not expose secrets. Do not build offensive security capability. Unsafe or ambiguous work routes to documentation, tests, defensive review, or human approval.
