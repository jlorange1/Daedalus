# Decisions

## 2026-06-16

- Date: 2026-06-16
- Decision: Pivot dashboard visual direction from fantasy/Stardew-inspired UI to sci-fi RSPS control panel.
- Why: User explicitly rejected the Stardew look and requested glowing sci-fi agent cores and modular control windows.
- Alternatives considered: Continue fantasy polish; rebuild as retro GBA; create fully separate app.
- Risk: Old fantasy assets may remain in repository and confuse future agents.
- Rollback plan: Revert commits `5f18309` and `7b3dc84` if the sci-fi direction is rejected.

- Date: 2026-06-16
- Decision: Initialize Markdown memory and orchestration docs before deeper implementation.
- Why: User requested Mythos-class long-horizon orchestration with persistent memory and specialist agents.
- Alternatives considered: Jump directly to implementation.
- Risk: Docs may drift if not maintained.
- Rollback plan: Remove or revise docs/memory files before orchestration code depends on them.

- Date: 2026-06-16
- Decision: Install the RSPS Java workflow as user-local toolchains instead of host rpm-ostree packages.
- Why: Fedora Atomic/Bazzite repositories did not provide `java-11-openjdk-devel`, while the configured 2009scape source explicitly requires JDK 11 and Maven.
- Alternatives considered: Layer host packages with rpm-ostree; use a toolbox/distrobox container; install a newer JDK.
- Risk: User-local tools depend on `~/.local/bin` being on PATH.
- Rollback plan: Remove `~/.local/share/daedalus-toolchains` and the symlinks/copy in `~/.local/bin`.

- Date: 2026-06-16
- Decision: Remove unlabelled mock dashboard fixture data and replace active queue fallbacks with explicit empty states.
- Why: User requested all mock data removed and the dashboard should reflect live operational state.
- Alternatives considered: Keep demo data behind a flag; leave visual backlog for aesthetics.
- Risk: Empty live queues look less populated until real work orders exist.
- Rollback plan: Reintroduce an explicit `demo_mode` API/UI flag with clearly labeled demo cards.

- Date: 2026-06-16
- Decision: Keep project skill sources in `/skills` and symlink them into `~/.codex/skills`.
- Why: The user wants the skills usable by Codex while preserving repo-versioned source files.
- Alternatives considered: Repo-local only; copy files into `~/.codex/skills`.
- Risk: Symlinks can break if the repository is moved.
- Rollback plan: Remove the symlinks from `~/.codex/skills` or replace them with copied skill folders.

- Date: 2026-06-16
- Decision: Add `[agents] max_threads = 6`, `max_depth = 1`, and `job_max_runtime_seconds = 1800` to `/var/home/Scaar/.codex/config.toml`.
- Why: The user requested parallel agent execution with bounded depth and runtime for this project.
- Alternatives considered: Document the snippet only; set a higher depth for recursive agents.
- Risk: The config is machine-local and not tracked in this repository.
- Rollback plan: Remove the `[agents]` section from `/var/home/Scaar/.codex/config.toml` or adjust the numeric limits.

## 2026-06-17

- Date: 2026-06-17
- Decision: Adapt public agency-agents/orchestrator patterns into a Daedalus-native agency catalog and workflow DAG layer.
- Why: The user requested using the GitHub Agency-agents project to enhance the system at every level. The upstream repository is MIT licensed and its most useful patterns are specialized role contracts, deliverable-focused agents, and dependency-aware orchestration.
- Alternatives considered: Vendor the full upstream role library; install the upstream orchestrator as a separate runtime; only document the repository link.
- Risk: The catalog can drift from CrewAI task execution until workflow traces are implemented.
- Rollback plan: Remove `src/rsps_crewai_team/config/agency_*.json`, `src/rsps_crewai_team/runtime/agency.py`, dashboard agency rendering, and the related tests/docs.

- Date: 2026-06-17
- Decision: Add native intelligence configs for spec contracts, prompt patterns, skill registry metadata, external inspiration attribution, and ethical profitability modeling.
- Why: The user requested adapting spec-kit, UI/UX Pro Max, LobeHub, OpenHands, Prompt Engineering Guide, DeerFlow, OpenBB, MetaGPT, and awesome-claude-skills into the dashboard, workflows, and agents.
- Alternatives considered: Install all upstream tools; vendor selected repositories; only write documentation.
- Risk: These configs are currently governance and visibility layers, not a full executable orchestrator.
- Rollback plan: Remove `src/rsps_crewai_team/config/inspiration_sources.json`, `spec_contracts.json`, `prompt_patterns.json`, `skill_catalog.json`, `profitability_model.json`, `runtime/intelligence.py`, dashboard panels, and related tests/docs.

- Date: 2026-06-17
- Decision: Add workflow-run manifests, sidecar work-order metadata, and bounded worker run manifests.
- Why: The user asked for the upgraded workflows and agents to be nearly tied together and functional, not merely visible as configs.
- Alternatives considered: Execute full DAGs immediately; embed metadata in Markdown frontmatter; leave workflows read-only.
- Risk: Workflow advancement is still first-level only until dependent-step completion/review gates are implemented.
- Rollback plan: Remove `runtime/orchestrator.py`, `runtime/run_manifests.py`, sidecar metadata changes in `runtime/work_orders.py`, dashboard workflow-run controls, and related tests.

- Date: 2026-06-17
- Decision: Implement workflow advancement and dashboard approval for review-gated code steps.
- Why: Workflow configs needed to move beyond first-level queue creation into dependency-aware execution.
- Alternatives considered: Let cron blindly queue every workflow step; require all step state changes manually; make code-writing steps auto-approved.
- Risk: Step advancement is based on work-order completion status, not yet on rich artifact review quality.
- Rollback plan: Revert `update_step_status`, `approve_step`, and worker calls to `advance_from_work_order`.

- Date: 2026-06-17
- Decision: Attach bounded artifact evidence from worker runs to workflow steps.
- Why: Review-gated approvals need visible facts such as changed files, validation result, log path, and repo/worktree path.
- Alternatives considered: Store raw logs and prompts; rely only on exit code; defer evidence capture.
- Risk: Artifact evidence is still worker-reported local metadata and does not prove semantic correctness.
- Rollback plan: Remove `changed_files`, artifact payloads, and dashboard artifact summaries.

- Date: 2026-06-17
- Decision: Auto-approve workflow code steps and remove mock/default profitability assumptions.
- Why: The user requested no gated code and no mock profitability data.
- Alternatives considered: Keep review gates; keep planning defaults; display estimated values with warnings.
- Risk: Auto-approved code steps increase autonomous-change risk; profitability will show unavailable until a real metrics source exists.
- Rollback plan: Restore review-required workflow code steps and profitability defaults if the operator wants a conservative/demo mode again.

- Date: 2026-06-17
- Decision: Reskin the dashboard as an Ancient Starforge sci-fi control room.
- Why: The user explicitly scrapped the Stardew-style direction and requested glowing neural/tesseract/liquid agents with a modular sci-fi control-panel layout.
- Alternatives considered: Keep polishing the previous pixel-fantasy style; generate a separate prototype; rebuild the dashboard with a new frontend stack.
- Risk: This is a CSS/DOM reskin over the existing dashboard rather than a full component rewrite, so deeper workflow UX can still be improved in later passes.
- Rollback plan: Revert `dashboard_static/index.html`, `app.js`, and `styles.css` to the previous sci-fi/fantasy mixed dashboard skin.
