# Daedalus Operator Guide

This guide is for the human operator running Daedalus, supervising its agents, and recovering it when work stalls or fails.

Daedalus is an AI-assisted RSPS development studio. It has three main operating surfaces:

- CrewAI planning with `rsps-team`.
- OpenClaw coding workers with `rsps-worker` and `rsps-cron`.
- A local dashboard with queue, readiness, agent, Git, log, and automation controls.

The current local posture is autonomous. Planning can run with an API key, and coding workers can modify the configured RSPS repository when `RSPS_ALLOW_AUTONOMOUS=true` is set in `.env`. Keep that flag enabled only for repositories where unattended code changes are intended.

## Start Here

Work from the project root:

```bash
cd "/var/home/Scaar/Desktop/game project/Daedalus"
```

Install dependencies if needed:

```bash
uv sync
```

Create and edit local configuration:

```bash
cp .env.example .env
```

Set at minimum:

- `OPENROUTER_API_KEY`
- `RSPS_REPO_PATH`

For worker execution, also confirm:

- `RSPS_ALLOW_AUTONOMOUS`
- `RSPS_BUILD_COMMAND`
- `RSPS_TEST_COMMAND`
- `RSPS_OPENCLAW_BIN`
- `RSPS_DUO_MODE`
- `RSPS_DUO_USE_WORKTREES`
- `RSPS_GIT_COMMIT_AFTER_WORK`
- `RSPS_GIT_PUSH_AFTER_WORK`

Never commit `.env`, API keys, tokens, private URLs with credentials, or raw logs containing secrets.

## Operating Modes

### Planning Mode

Use planning mode when you want the agent team to inspect context, decompose work, or produce an implementation packet without directly editing the RSPS repo.

```bash
uv run rsps-team "Review current RSPS development status and propose the next 3 work orders."
```

Planning mode writes the documentation task output to `rsps_development_packet.md`. Treat the packet as a proposal. Review it before creating work orders.

### Manual Worker Mode

Use manual worker mode for one controlled coding task.

```bash
uv run rsps-worker enqueue "Small title" \
  "Exact scoped work order body with target files, acceptance criteria, and validation commands."

uv run rsps-worker status
uv run rsps-worker run-once
```

`run-once` requires `RSPS_ALLOW_AUTONOMOUS=true` and a valid `RSPS_REPO_PATH`. If autonomy is disabled, it exits before modifying the RSPS repo.

### Duo Worker Mode

Use duo mode only for two small, independent queued work orders or when the builder/reviewer split is useful.

```bash
uv run rsps-worker run-duo
```

The default agents are:

- `rsps-builder`: implementation-focused worker.
- `rsps-reviewer`: review, hardening, and follow-up fixer.

When `RSPS_DUO_USE_WORKTREES=true`, each agent works in an isolated Git worktree and branch under the configured worktree root, or under the RSPS repo parent directory by default. This reduces write conflicts.

### Scheduled Mode

Render cron without installing it:

```bash
uv run rsps-cron render
```

Inspect `cron/rsps-crewai.cron`, then install when the autonomous schedule is acceptable:

```bash
uv run rsps-cron install
```

The installer uses `crontab` when available. On systems without `crontab`, it installs `~/.config/systemd/user/daedalus-rsps-cron.timer` and enables it with `systemctl --user`. The one-minute watchdog self-fills an idle queue with `server_building_watchdog`, skips if `work_orders/running` already has active work, then checks `RSPS_ALLOW_AUTONOMOUS`; if autonomy is disabled, it logs and exits without running workers.

## Dashboard

Start the dashboard:

```bash
uv run rsps-dashboard
```

Open:

```text
http://127.0.0.1:8765
```

The dashboard reads `/api/status` every few seconds and shows:

- Daedalus project root and configured RSPS repo.
- Autonomy, duo mode, push setting, Ponytail mode, coding CLI, build command, and test command.
- Readiness for Java, Git LFS, OpenClaw, and the RSPS repo path.
- Work-order counts and recent queue items from `work_orders/inbox`, `running`, `failed`, and `done`.
- Agent role cards and model labels from `.env`.
- Git branch, cleanliness, and remote state for Daedalus and the RSPS repo.
- Recent log tails from `logs/`.

Dashboard controls:

- `Enqueue Work`: creates a Markdown work order in `work_orders/inbox`.
- `Run Duo`: spawns `rsps-worker run-duo` and appends output to `logs/dashboard-actions.log`.
- `Open Cron View`: currently starts a `rsps-cron tick` action from the dashboard.
- `Build / Test`: status-only toast in the current UI; run configured build/test commands from the shell until backend execution is implemented.
- `Push Branch`: status-only toast in the current UI; actual push is handled after successful worker runs when `RSPS_GIT_PUSH_AFTER_WORK=true`.
- Movable module windows: drag a module grip to reposition; double-click the grip to reset; click the small control area to minimize.

Dashboard actions spawn background processes. After clicking an action, inspect:

```bash
tail -n 120 logs/dashboard-actions.log
uv run rsps-worker status
```

## Work Orders

Work orders are Markdown files managed by `src/rsps_crewai_team/runtime/work_orders.py`.

Queue directories:

```text
work_orders/inbox
work_orders/running
work_orders/done
work_orders/failed
```

Lifecycle:

1. `enqueue` writes a timestamped file to `work_orders/inbox`.
2. `run-once` or `run-duo` moves the next file to `work_orders/running`.
3. A successful worker moves it to `work_orders/done`.
4. A failed worker moves it to `work_orders/failed`.

A good work order includes:

- Exact goal.
- Files or directories that may be changed.
- Files or directories that must not be changed.
- Build/test/smoke commands to run.
- Safety notes for economy, auth, trade, banking, admin commands, packets, and persistence.
- Expected final handoff.

Prefer one small work order at a time until the RSPS repo, build command, and test command are proven stable.

## Using Codex With Agents

Codex should act as the parent operator for this repo. Before non-trivial work, have Codex read:

- `AGENTS.md`
- `memory/PROJECT_MEMORY.md`
- `memory/TASK_GRAPH.md`
- Relevant docs under `docs/`

Use specialist roles from `docs/ORCHESTRATION.md` when delegating or simulating agent work:

- `repo_cartographer`
- `architecture_planner`
- `implementation_planner`
- `memory_system_designer`
- `evals_and_benchmark_designer`
- `safety_and_defensive_security_reviewer`
- `test_engineer`
- `docs_and_operator_guide_writer`

For every Codex task, state:

- Role.
- Objective.
- Allowed write scope.
- Forbidden files.
- Safety level.
- Validation command.
- Memory update expectation.

Example:

```text
You are test_engineer for Daedalus. Inspect dashboard API behavior and add only focused tests for /api/status. Do not modify dashboard UI files. Run the relevant test command and update memory only if the validation contract changes.
```

Parallel Codex agents are allowed only when write scopes do not overlap. If two agents need the same file, pause parallel work, review both proposals, merge manually, run tests, and record the decision in `memory/DECISIONS.md` if it constrains future work.

Codex must not revert user changes or other agent changes unless the operator explicitly requests it.

## Memory Files

Daedalus memory lives in `memory/` as human-readable Markdown.

Read-first file:

```text
memory/PROJECT_MEMORY.md
```

Memory map:

- `memory/PROJECT_MEMORY.md`: compact project snapshot, commands, constraints, current direction.
- `memory/DECISIONS.md`: dated decisions, rationale, alternatives, risk, rollback.
- `memory/OPEN_QUESTIONS.md`: active blockers and unresolved questions.
- `memory/FAILED_ATTEMPTS.md`: failed approaches and lessons.
- `memory/TASK_GRAPH.md`: active goals, dependencies, owners, status, risk.
- `docs/MEMORY_SYSTEM.md`: policy for maintaining memory.

Update memory when:

- Project direction changes.
- Architecture, commands, workflow, or safety policy changes.
- A task starts, finishes, blocks, or changes owner/dependency.
- Validation passes or fails in a way future agents need to know.
- A durable decision is made.
- A failed attempt produces a reusable lesson.

Do not store:

- Secrets or `.env` contents.
- Full logs or large transcripts.
- Speculative claims as facts.
- Temporary scratch notes.
- Personal data unrelated to the project.

For small docs-only edits that do not change future operating behavior, memory updates are usually not needed.

## Evals And Release Gates

Static evals are local and deterministic:

```bash
python3 evals/run_static_evals.py
```

Save a report:

```bash
python3 evals/run_static_evals.py --write-report
```

Score an agent transcript or work-order log:

```bash
python3 evals/score_agent_trace.py path/to/transcript.md
```

Save a trace report:

```bash
python3 evals/score_agent_trace.py path/to/transcript.md --write-report
```

Reports are written to `evals/results/`.

The eval suite covers:

- Planning quality.
- Task completion.
- Regression prevention.
- Code quality.
- Latency.
- Hallucination control.
- Safety fallback.
- Recovery from failed attempts.

Before treating an orchestration change as ready:

1. Run `python3 evals/run_static_evals.py`.
2. Run any feature-specific smoke test named in the work order.
3. Score the agent transcript with `python3 evals/score_agent_trace.py`.
4. Record reusable failures in `memory/FAILED_ATTEMPTS.md`.
5. Record durable process decisions in `memory/DECISIONS.md`.

## Safety Boundaries

The safety contract is `docs/SAFETY_BOUNDARIES.md`.

Allowed work includes:

- Defensive dependency review.
- Secret scanning guidance.
- Permission hardening.
- Secure configuration.
- Test coverage.
- Sandboxed local smoke tests.
- Documentation of risks and mitigations.

Disallowed work includes:

- Exploit development.
- Unauthorized scanning.
- Credential harvesting.
- Malware or persistence.
- Evasion logic.
- Bypassing safety systems.
- Leaking API keys or private tokens.

If a request is unsafe or ambiguous, route it to one of:

- Defensive checklist.
- Safe mock.
- Documentation.
- Test design.
- Human approval request.
- Smaller scoped implementation.

High-risk RSPS areas require extra review:

- Economy.
- Trade.
- Banking.
- Shops.
- Admin commands.
- Packet trust.
- Account authentication.
- Item or currency persistence.
- Database migrations.

Do not weaken safety-critical behavior in the name of Ponytail minimalism.

## Ponytail Controls

Ponytail is the minimalism layer that keeps agents from overbuilding.

Check mode:

```bash
uv run rsps-ponytail status
```

Set mode:

```bash
uv run rsps-ponytail set lite
uv run rsps-ponytail set full
uv run rsps-ponytail set ultra
uv run rsps-ponytail set off
```

Normal RSPS work should keep Ponytail enabled. Use `off` only for explicit architecture exploration or broad migration planning.

## Logs And Inspection

Common inspection commands:

```bash
uv run rsps-worker status
tail -n 120 logs/dashboard-actions.log
tail -n 120 logs/cron.log
tail -n 120 logs/daily-planning.log
git status --short
```

Worker runs write prompt and worker logs under `logs/` using timestamped names. Do not paste or commit raw logs until checked for secrets.

## Recovery Runbooks

### Worker Fails

1. Check queue state:

   ```bash
   uv run rsps-worker status
   ```

2. Inspect the newest worker log in `logs/`.
3. Inspect the failed work order in `work_orders/failed`.
4. Check RSPS repo status:

   ```bash
   git -C "$RSPS_REPO_PATH" status --short
   ```

5. Decide whether to create a smaller replacement work order or manually finish/revert in the RSPS repo.
6. Record reusable lessons in `memory/FAILED_ATTEMPTS.md`.

Do not blindly move a failed work order back to `inbox`; first narrow the scope or add missing validation details.

### Work Order Stuck In Running

1. Check whether a worker process is still active.
2. Inspect `logs/dashboard-actions.log` or the relevant worker log.
3. If no process is active and the work order is stale, manually move the file from `work_orders/running` to `work_orders/failed`.
4. Add a short note to the work order or `memory/FAILED_ATTEMPTS.md` explaining why it was failed.
5. Re-enqueue a smaller corrected work order if appropriate.

### Dashboard Action Does Nothing

1. Confirm the dashboard server is still running.
2. Open `/api/status` in the browser or query it from a local shell.
3. Check `logs/dashboard-actions.log`.
4. Confirm `.env` has `RSPS_ALLOW_AUTONOMOUS=true` for worker actions.
5. Confirm `RSPS_OPENCLAW_BIN` exists and `RSPS_REPO_PATH` points to a real directory.
6. Restart the dashboard if the server process is stale.

### Cron Does Not Run

1. Render and inspect the cron file:

   ```bash
   uv run rsps-cron render
   ```

2. Confirm it is installed in the user crontab or as `daedalus-rsps-cron.timer`.
3. Inspect `logs/cron.log`.
4. Confirm `RSPS_ALLOW_AUTONOMOUS=true` if worker execution is expected.
5. Run one manual tick:

   ```bash
   uv run rsps-cron tick
   ```

### Autonomy Accidentally Enabled

1. Set `RSPS_ALLOW_AUTONOMOUS=false` in `.env`.
2. Stop any active dashboard-spawned worker or cron process.
3. Inspect `work_orders/running` and `logs/`.
4. Inspect the RSPS repo with `git status --short`.
5. Keep or revert RSPS repo changes manually after review.
6. Record the incident in memory if it changes future operating policy.

### Git Worktree Problems

1. Inspect RSPS worktrees:

   ```bash
   git -C "$RSPS_REPO_PATH" worktree list
   ```

2. Check whether `RSPS_DUO_KEEP_WORKTREES=true` caused worktrees to remain by design.
3. Review changes before deleting any worktree.
4. Remove stale worktrees only after confirming their changes are committed, copied, or intentionally discarded.

### Model Or API Failures

1. Confirm `OPENROUTER_API_KEY` is set locally and not committed.
2. Check model IDs in `.env`; free models must be concrete IDs ending in `:free`.
3. Keep fallback lists to at most three models.
4. Lower `OPENROUTER_MAX_TOKENS` or raise `OPENROUTER_TIMEOUT_SECONDS` if free endpoints stall.
5. Retry with a smaller prompt or smaller work order.

## Normal Shutdown

Before ending an operator session:

1. Stop dashboard or worker processes you started manually.
2. Check `uv run rsps-worker status`.
3. Check Daedalus and RSPS `git status --short`.
4. Move stale work orders out of `running` only after confirming no process owns them.
5. Run relevant evals or smoke checks.
6. Update memory if direction, validation, task state, or failures changed.
7. Leave exact next actions in `memory/TASK_GRAPH.md` for future agents when the work remains active.
