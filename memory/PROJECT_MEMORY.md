# Project Memory

Read this file first. It is the compact project snapshot and index for Daedalus persistent memory. The memory-system contract lives in `docs/MEMORY_SYSTEM.md`.

## Repository Purpose

Daedalus is an autonomous coding and operations scaffold for an AI-assisted RSPS game-development studio. It coordinates specialist agents, local dashboard controls, worker orchestration concepts, memory/docs, and planned skills for repeatable Codex workflows.

## Current Product Direction

- Build a safe autonomous game-development studio with departments, specialist agents, review loops, evals, and operator controls.
- The GUI direction is a sci-fi RSPS control panel, not Stardew/fantasy.
- The dashboard should use modular movable windows inspired by desktop agent systems.
- Agent visuals should lean toward glowing sci-fi cores such as neural networks, tesseracts, and liquid metal orbs.
- Mock data should be removed once API/UI impact is understood.

## Current Architecture

- Python package: `src/rsps_crewai_team`
- Dashboard static frontend: `src/rsps_crewai_team/dashboard_static`
- Dashboard API/server: `src/rsps_crewai_team/dashboard.py`
- Documentation: `docs/`
- Persistent memory: `memory/`
- Eval harnesses: `evals/`
- Project skills: `skills/`

## Memory Map

- `docs/MEMORY_SYSTEM.md`: memory contract, storage policy, and update rules.
- `memory/PROJECT_MEMORY.md`: this read-first project snapshot.
- `memory/DECISIONS.md`: durable choices and rationale.
- `memory/OPEN_QUESTIONS.md`: unresolved questions and blockers.
- `memory/FAILED_ATTEMPTS.md`: rejected or failed approaches and lessons.
- `memory/TASK_GRAPH.md`: active goal, task waves, dependencies, and blockers.

## Known Commands

- Validate dashboard assets: `python3 scripts/dashboard_assets.py`
- Validate dashboard JSON: `python3 -c "import json, pathlib; root=pathlib.Path('src/rsps_crewai_team/dashboard_static'); [json.loads(p.read_text()) for p in root.glob('**/*.json')]; print('json ok')"`
- Run static evals: `python3 evals/run_static_evals.py`
- Run smoke tests: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests`
- Run dashboard server: existing local dashboard has been served at `http://127.0.0.1:8765`.
- Java toolchain: `java`, `javac`, `mvn`, and `git-lfs` are installed under `~/.local/bin` using user-local toolchains.

## Constraints

- Do not expose API keys or secrets.
- Keep shipped UI legally original.
- Safety boundaries live in `/docs/SAFETY_BOUNDARIES.md`.
- User wants parallel agents for major work.
- User wants sci-fi control-panel UI, not Stardew/fantasy.
- Memory must be human-readable, versionable, and Obsidian-compatible Markdown.
- Do not store `.env` contents, credentials, long logs, or generated transcripts in memory.

## User Preferences

- Wants an autonomous game-development studio with departments.
- Wants modular movable windows inspired by desktop agent systems.
- Wants glowing sci-fi agent cores such as neural networks, tesseracts, and liquid metal orbs.
- Wants Obsidian-compatible Markdown memory.
- Wants skills split into folders with `SKILL.md`.
- Wants mock data removed.

## Validated Facts

- Dashboard browser smoke checks have rendered 6 agents and 4 module grips.
- Asset and JSON validation commands pass as of the last dashboard cleanup.
- Existing persistent memory files were present before the memory-system design: `DECISIONS.md`, `OPEN_QUESTIONS.md`, `FAILED_ATTEMPTS.md`, and `TASK_GRAPH.md`.
- Phase 1 specialist agents completed and wrote `docs/REPO_MAP.md`, `docs/TARGET_ARCHITECTURE.md`, `docs/IMPLEMENTATION_PLAN.md`, `docs/MEMORY_SYSTEM.md`, `docs/EVALS.md`, `docs/DEFENSIVE_SECURITY_REVIEW.md`, `docs/TEST_PLAN.md`, and `docs/OPERATOR_GUIDE.md`.
- Temurin JDK 11.0.31, Apache Maven 3.9.9, and Git LFS 3.6.1 are installed user-locally and verified on PATH.
- `git lfs pull` completed in the configured 2009scape repository.
- Unused dashboard mock JSON fixtures and `mock-data-manifest.json` were removed; live queue lanes now render explicit empty states when no work exists.
- Project skills are source-controlled under `/skills` and symlinked into `~/.codex/skills` for local Codex discovery.
- Autonomous RSPS worker routing uses OpenClaw through `openrouter/free`; the special OpenRouter free-router alias must be passed to OpenClaw as `free`.
- The first useful RSPS source commit created by this workflow is local commit `b3ea455` in `/var/home/Scaar/Desktop/game project/2009scape`, fixing desert quest NPC constants after `timeout 240 ./mvnw -q -DskipTests compile` passed.
- Duo agents must be treated as supervised until another run proves the worktree guard prevents absolute-path edits to the main checkout.

## Unfinished Tasks

- Add orchestration service utilities for task graph, memory, role registry, and run manifests.
- Harden dashboard action endpoints and prompt-injection boundaries.
- Run full validation and push the Phase 0/1 foundation.
- Decide where the 2009scape-derived server fork should be pushed; the current `origin` is upstream GitLab, not a user-owned GitHub remote.

## Update Policy

- Read this file before non-trivial project work.
- Update this file when project direction, architecture, commands, constraints, preferences, validated facts, or active work changes.
- Put detailed decision records in `memory/DECISIONS.md`.
- Put unresolved planning or implementation questions in `memory/OPEN_QUESTIONS.md`.
- Put failed/rejected approaches in `memory/FAILED_ATTEMPTS.md`.
- Put task dependencies, owners, statuses, and blockers in `memory/TASK_GRAPH.md`.
- Keep memory concise, dated where useful, and free of secrets.
