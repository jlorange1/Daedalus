# Daedalus Studio

Autonomous sci-fi software-studio dashboard and CrewAI/OpenClaw workforce scaffold for open-source 2009-era MMORPG server development. It coordinates specialized agents for planning, server direction, implementation guidance, code review, content design, QA, security, release, DevOps, art/audio direction, and documentation.

The studio also includes a Daedalus-native Agency layer inspired by the public `agency-agents` and `agency-orchestrator` projects. See [docs/AGENCY_AGENTS_INTEGRATION.md](docs/AGENCY_AGENTS_INTEGRATION.md) for the role catalog, workflow DAG model, safety gates, and future extension points.

Additional integration patterns from spec-kit, UI/UX Pro Max, LobeHub, OpenHands, Prompt Engineering Guide, DeerFlow, OpenBB, MetaGPT, and awesome-claude-skills are captured as validated Daedalus-native configs. See [docs/INTELLIGENCE_UPGRADES.md](docs/INTELLIGENCE_UPGRADES.md).

Workflow runs can now be started from the dashboard Agency Layer. A run creates a manifest under `logs/agency-runs/`, queues first-level work orders with sidecar metadata, and records bounded worker evidence under `logs/runs/` when workers execute.

Cron is self-filling: each tick creates a new `profitability_review` workflow when there are no active workflow runs and no queued/running work orders. Code-writing workflow steps are auto-approved; autonomous repository writes still require `RSPS_ALLOW_AUTONOMOUS=true`.

Profitability does not use mock defaults. Put live metrics at `RSPS_PROFITABILITY_METRICS_PATH` or `data/profitability_metrics.json`; otherwise the dashboard reports profitability as unavailable.

## One-Click Launcher

Use the desktop launcher:

```text
/var/home/Scaar/Desktop/Daedalus Studio.desktop
```

It starts the local dashboard server and opens:

```text
http://127.0.0.1:8765
```

The launcher does not require Codex. It starts the local dashboard process on this PC.

## Setup

```bash
cd /var/home/Scaar/Desktop/game project/Daedalus
cp .env.example .env
# edit .env with OPENROUTER_API_KEY and RSPS_REPO_PATH
uv sync
uv run rsps-team "Design and implement a starter goblin boss with drops, mechanics, and QA checks"
```

If `uv sync` cannot download dependencies because network access is blocked, run it later from a network-enabled shell.

## Intended Workflow

1. Producer turns your request into a scoped milestone.
2. Designer defines RSPS mechanics, progression, economy, and content constraints.
3. Backend/content/client specialists produce implementation guidance and file targets.
4. QA and security agents review build/test risks, dupes, permission checks, and exploit paths.
5. Documentation agent outputs implementation notes and a review checklist.
6. `rsps-worker` can apply queued work orders directly to the configured RSPS repo when autonomy is enabled.
7. `rsps-cron` can run scheduled autonomous cycles and self-fill the queue when the system is idle.

Codex is not required for scheduled autonomous runs after the local launcher/cron process is running. The PC must stay awake and online, `.env` must contain the OpenRouter key, OpenClaw must be configured, and `RSPS_ALLOW_AUTONOMOUS=true` must remain enabled.

The included `.env.example` is configured for autonomous local operation. Keep `RSPS_ALLOW_AUTONOMOUS=true` only on a machine and repository where you want Daedalus to write code without an extra approval step.

## Environment

- `OPENROUTER_API_KEY`: required.
- `OPENROUTER_MODEL`: primary model. The included template uses `openrouter/qwen/qwen3-coder:free`.
- `OPENROUTER_FALLBACK_MODELS`: optional OpenRouter fallback model list. OpenRouter currently allows at most 3 IDs in one fallback request.
- `OPENROUTER_TIMEOUT_SECONDS`: optional model timeout for slow free endpoints.
- `OPENROUTER_MAX_TOKENS`: optional per-agent response cap for free endpoints.
- `OPENROUTER_<AGENT>_MODEL`: optional per-agent primary model. The scaffold already assigns unique free models for `PRODUCER`, `SERVER_PLANNER`, `LEAD_DESIGNER`, `BACKEND_DEVELOPER`, `CONTENT_DEVELOPER`, `CLIENT_DEVELOPER`, `WORLD_DESIGNER`, `ECONOMY_DESIGNER`, `QA_TESTER`, `SECURITY_REVIEWER`, `BUILD_RELEASE_ENGINEER`, `DEVOPS_ENGINEER`, `ART_AUDIO_DIRECTOR`, and `DOCUMENTATION_WRITER`.
- `OPENROUTER_<AGENT>_FALLBACK_MODELS`: optional per-agent fallback list, capped to 3 IDs.
- `OPENROUTER_<AGENT>_TEMPERATURE`: optional per-agent creativity/strictness setting.
- `RSPS_REPO_PATH`: absolute path to your RSPS repository.
- `RSPS_BUILD_COMMAND`: optional command to run in the RSPS repo.
- `RSPS_TEST_COMMAND`: optional command to run in the RSPS repo.
- `RSPS_CODING_CLI`: coding worker backend. This setup uses `openclaw`.
- `RSPS_CODING_MODEL`: OpenRouter model used by the coding worker.
- `RSPS_ALLOW_AUTONOMOUS`: must be `true` before `rsps-worker` or `rsps-cron` can modify the RSPS repo.
- `RSPS_DUO_MODE`: when `true`, cron runs both OpenClaw workers in parallel.
- `RSPS_DUO_USE_WORKTREES`: when `true`, each OpenClaw agent works in its own Git worktree and branch.
- `RSPS_OPENCLAW_BUILDER_AGENT`: implementation agent id, default `rsps-builder`.
- `RSPS_OPENCLAW_REVIEWER_AGENT`: review/fix agent id, default `rsps-reviewer`.
- `RSPS_GIT_COMMIT_AFTER_WORK`: when `true`, successful work orders are committed.
- `RSPS_GIT_PUSH_AFTER_WORK`: when `true`, successful work-order branches are pushed to `origin`.
- `RSPS_PONYTAIL_ENABLED`: enables the Ponytail minimalism layer.
- `PONYTAIL_DEFAULT_MODE`: `lite`, `full`, `ultra`, or `off`.

## Agent Model Assignments

All agents use the same `OPENROUTER_API_KEY`. Each role has a distinct primary free model plus a small fallback pool:

| Agent | Primary model |
|-------|---------------|
| Producer | `openrouter/openai/gpt-oss-120b:free` |
| Server planner | `openrouter/openai/gpt-oss-120b:free` |
| Lead designer | `openrouter/qwen/qwen3-next-80b-a3b-instruct:free` |
| Backend developer | `openrouter/qwen/qwen3-coder:free` |
| Content developer | `openrouter/nousresearch/hermes-3-llama-3.1-405b:free` |
| Client developer | `openrouter/poolside/laguna-m.1:free` |
| World designer | `openrouter/nousresearch/hermes-3-llama-3.1-405b:free` |
| Economy designer | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` |
| QA tester | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` |
| Security reviewer | `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free` |
| Build/release engineer | `openrouter/openai/gpt-oss-20b:free` |
| DevOps engineer | `openrouter/qwen/qwen3-coder:free` |
| Art/audio director | `openrouter/google/gemma-4-31b-it:free` |
| Documentation writer | `openrouter/google/gemma-4-31b-it:free` |

## Free Model Routing

`openrouter/free` is not a concrete model ID. Free models use concrete IDs ending in `:free`, such as:

```text
qwen/qwen3-coder:free
openai/gpt-oss-120b:free
qwen/qwen3-next-80b-a3b-instruct:free
```

The scaffold passes OpenRouter's `models` fallback list through `extra_body` so CrewAI's OpenAI-compatible client forwards it correctly.

## Ponytail Layer

Ponytail keeps the RSPS agent workforce from overbuilding. It is injected into CrewAI planning and OpenClaw coding prompts, and the project root includes `AGENTS.md` for compatible tools.

Check the active policy:

```bash
uv run rsps-ponytail status
```

Change intensity:

```bash
uv run rsps-ponytail set lite
uv run rsps-ponytail set full
uv run rsps-ponytail set ultra
uv run rsps-ponytail set off
```

See [PONYTAIL.md](docs/PONYTAIL.md) for the local policy.

## OpenClaw Coding Duo

Point the scaffold at an RSPS source tree:

```bash
RSPS_REPO_PATH=/absolute/path/to/your/rsps
RSPS_ALLOW_AUTONOMOUS=true
```

Queue a work order:

```bash
uv run rsps-worker enqueue "Bootstrap RSPS skeleton" \
  "Create the initial Java RSPS server skeleton, Gradle build, README, and CI placeholders."
```

Run exactly one queued work order:

```bash
uv run rsps-worker run-once
```

Run two queued work orders in parallel with the OpenClaw coding duo:

```bash
uv run rsps-worker run-duo
```

Check queue state:

```bash
uv run rsps-worker status
```

The active worker is OpenClaw using the same `OPENROUTER_API_KEY`.

Configured OpenClaw agents:

- `rsps-builder`: implementation-focused coding worker.
- `rsps-reviewer`: review, hardening, and follow-up fixer.

When `RSPS_DUO_USE_WORKTREES=true`, each agent gets an isolated Git worktree and branch:

```text
agent/rsps-builder/<work-order>
agent/rsps-reviewer/<work-order>
```

This avoids two agents editing the same working tree at the same time.

## GitHub Sync

GitHub CLI is installed at:

```text
/var/home/Scaar/.local/bin/gh
```

Authenticate once:

```bash
gh auth login
```

For an existing RSPS repo, set its remote:

```bash
git -C "$RSPS_REPO_PATH" remote add origin git@github.com:OWNER/REPO.git
```

Or create a GitHub repo from the RSPS folder:

```bash
cd "$RSPS_REPO_PATH"
gh repo create OWNER/REPO --private --source=. --remote=origin --push
```

Then enable pushing after successful work orders:

```text
RSPS_GIT_PUSH_AFTER_WORK=true
```

## Autonomous Cron

Render a cron file without installing it:

```bash
uv run rsps-cron render
```

This writes:

```text
cron/rsps-crewai.cron
```

Install it as the local scheduler:

```bash
uv run rsps-cron install
```

If `crontab` is installed, this writes the user crontab. If `crontab` is unavailable, it installs and enables the user systemd timer `daedalus-rsps-cron.timer`. The tick self-fills an idle queue with a `profitability_review` workflow, then runs the OpenClaw duo every 30 minutes when `RSPS_DUO_MODE=true` and `RSPS_ALLOW_AUTONOMOUS=true`.

## Studio Dashboard

Run the retro Sprint Workshop dashboard:

```bash
uv run rsps-dashboard
```

Open:

```text
http://127.0.0.1:8765
```

## Dashboard Asset Pipeline

Dashboard pixel-art assets are managed by `scripts/dashboard_assets.py`. The script copies generated source sheets into `src/rsps_crewai_team/dashboard_static/assets/source_sheets/`, slices UI-ready PNGs into `assets/sliced/` and `assets/animations/`, then writes JSON manifests under `assets/manifests/`.

Run the pipeline after replacing or adding source sheets:

```bash
uv run python scripts/dashboard_assets.py
```

Keep source sheet names, slice names, and manifest entries legal-safe and project-owned. Do not use official RuneScape/Jagex logos, sprites, screenshots, or trade dress as dashboard assets. See [ASSET_INVENTORY.md](docs/ASSET_INVENTORY.md) for the current source sheets, outputs, animation strips, state gaps, and naming rules.

The dashboard shows queue state, agent roles, readiness checks, Git status, cron schedule, and OpenClaw duo controls. Enqueue is safe to use immediately. Worker execution requires `RSPS_ALLOW_AUTONOMOUS=true`; the included local setup enables that for unattended development.

## Files

- `src/rsps_crewai_team/config/agents.yaml`: agent roles.
- `src/rsps_crewai_team/config/tasks.yaml`: workflow tasks.
- `src/rsps_crewai_team/crew.py`: CrewAI wiring.
- `src/rsps_crewai_team/tools/repo_tools.py`: repo scan/build/test tools.
- `docs/WORKFLOW.md`: operating model and recommended guardrails.
- `docs/PONYTAIL.md`: Ponytail minimalism layer.
- `docs/RSPS_SOURCE.md`: selected RSPS source recommendation and setup notes.
- `design-qa.md`: visual QA notes for the Studio Dashboard.
