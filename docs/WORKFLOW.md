# RSPS Workforce Workflow

## Roles

- Producer: scope, milestones, acceptance criteria.
- Lead RSPS Designer: mechanics, balancing, economy, progression.
- Backend Developer: server systems, persistence, packets, commands.
- Content Developer: NPCs, drops, shops, dialogue, spawns, quests.
- Client Developer: interfaces, cache/client concerns, UX notes.
- QA Tester: build/test plan, regression cases, gameplay edge cases.
- Security Reviewer: dupes, privilege checks, packet trust, economy abuse.
- Documentation Writer: implementation summary, changelog, operator notes.

## Guardrails

- Do not merge agent output without human review.
- Treat all economy, trade, banking, shop, and admin-command changes as high risk.
- Require a test-server run before production deployment.
- Keep content changes reproducible through configs or migrations.
- Avoid direct cache edits unless the toolchain and rollback path are known.
- Keep `RSPS_ALLOW_AUTONOMOUS=false` until a real RSPS repo, build command, and test command are configured.
- Prefer one queued work order at a time. Autonomous cron should execute small, reviewable tasks, not broad rewrites.
- Use `RSPS_WORKER_DRY_RUN=true` for the first pass on any new codebase.
- Keep Ponytail mode enabled for normal work so agents prefer stdlib, engine-native behavior, config/data changes, and the smallest correct code.
- Disable Ponytail only when explicitly doing architecture exploration or broad migration planning.

## Execution Modes

- Planning mode: `uv run rsps-team "...request..."`.
- Manual worker mode: `uv run rsps-worker enqueue ...` then `uv run rsps-worker run-once`.
- Scheduled mode: `uv run rsps-cron render`, inspect `cron/rsps-crewai.cron`, then `uv run rsps-cron install`.
- Ponytail mode: `uv run rsps-ponytail status` or `uv run rsps-ponytail set ultra`.

## Suggested Requests

```text
Create a new mid-game boss for level 90 players with three mechanics, drops, and anti-farm controls.
```

```text
Review this RSPS repo for common dupes and privilege bypasses. Prioritize trade, shops, commands, and packets.
```

```text
Plan a Mining skill rework with XP rates, progression, content files, tests, and deployment notes.
```
