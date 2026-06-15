# RSPS CrewAI Team

CrewAI workforce scaffold for RuneScape private server development. It is designed to coordinate specialized agents for planning, implementation guidance, code review, content design, QA, and security analysis.

## Setup

```bash
cd /var/home/Scaar/rsps-crewai-team
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
6. `rsps-worker` can apply one approved work order directly to the configured RSPS repo.
7. `rsps-cron` can run scheduled autonomous cycles when explicitly enabled.

By default this scaffold is conservative: direct file modification is disabled until `RSPS_ALLOW_AUTONOMOUS=true` is set.

## Environment

- `OPENROUTER_API_KEY`: required.
- `OPENROUTER_MODEL`: primary model. The included template uses `openrouter/qwen/qwen3-coder:free`.
- `OPENROUTER_FALLBACK_MODELS`: optional OpenRouter fallback model list. OpenRouter currently allows at most 3 IDs in one fallback request.
- `OPENROUTER_TIMEOUT_SECONDS`: optional model timeout for slow free endpoints.
- `OPENROUTER_MAX_TOKENS`: optional per-agent response cap for free endpoints.
- `OPENROUTER_<AGENT>_MODEL`: optional per-agent primary model. The scaffold already assigns unique free models for `PRODUCER`, `LEAD_DESIGNER`, `BACKEND_DEVELOPER`, `CONTENT_DEVELOPER`, `CLIENT_DEVELOPER`, `QA_TESTER`, `SECURITY_REVIEWER`, and `DOCUMENTATION_WRITER`.
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
| Lead designer | `openrouter/qwen/qwen3-next-80b-a3b-instruct:free` |
| Backend developer | `openrouter/qwen/qwen3-coder:free` |
| Content developer | `openrouter/nousresearch/hermes-3-llama-3.1-405b:free` |
| Client developer | `openrouter/poolside/laguna-m.1:free` |
| QA tester | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` |
| Security reviewer | `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free` |
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

Install it as your user crontab:

```bash
uv run rsps-cron install
```

The cron tick runs the OpenClaw duo every 30 minutes when `RSPS_DUO_MODE=true`, but only when `RSPS_ALLOW_AUTONOMOUS=true`.

## Files

- `src/rsps_crewai_team/config/agents.yaml`: agent roles.
- `src/rsps_crewai_team/config/tasks.yaml`: workflow tasks.
- `src/rsps_crewai_team/crew.py`: CrewAI wiring.
- `src/rsps_crewai_team/tools/repo_tools.py`: repo scan/build/test tools.
- `docs/WORKFLOW.md`: operating model and recommended guardrails.
- `docs/PONYTAIL.md`: Ponytail minimalism layer.
- `docs/RSPS_SOURCE.md`: selected RSPS source recommendation and setup notes.
