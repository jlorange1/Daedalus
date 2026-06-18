# Defensive Security Review

Reviewed repository: `/var/home/Scaar/Desktop/game project/Daedalus`

Scope: unsafe patterns, secrets handling, dangerous permissions, dependency risks, insecure defaults, shell execution, prompt injection surfaces, and unsafe agent behaviors. This is a defensive review only.

## Critical Issues

No critical issues were confirmed in the reviewed code. The repo has high-impact autonomous execution paths, but they are gated by `RSPS_ALLOW_AUTONOMOUS` and default to disabled in `.env.example`.

## High Issues

### H-1: Dashboard action endpoints are unauthenticated and can start autonomous workers

Evidence:
- `src/rsps_crewai_team/dashboard.py:217-239` accepts POST requests to `/api/enqueue` and `/api/action` without authentication, CSRF protection, origin checks, or a local-only request validation token.
- `src/rsps_crewai_team/dashboard.py:185-204` spawns worker and cron subprocesses for allowlisted actions.
- `src/rsps_crewai_team/dashboard.py:244-250` defaults to `127.0.0.1`, which is safer, but the CLI permits any `--host` value.

Risk:
- If the dashboard is bound to `0.0.0.0`, reverse-proxied, or accessed through browser-based local network abuse, an untrusted party could enqueue agent work or trigger worker cycles.
- Impact increases when `RSPS_ALLOW_AUTONOMOUS=true`, because triggered workers can modify the configured RSPS repository and may commit changes.

Mitigations:
- Require an operator token for every mutating endpoint and compare it with a constant-time check against a value from `.env`.
- Reject mutating requests unless `Host` is loopback and an explicit `DASHBOARD_ALLOW_REMOTE=true` is set.
- Add CSRF protection for browser-originated POSTs, or make the dashboard API require a non-cookie bearer token.
- Keep `--host 127.0.0.1` as the default and document that remote binding requires a separate authenticated reverse proxy.

### H-2: Build/test tool uses `shell=True` on environment-configured commands

Evidence:
- `src/rsps_crewai_team/tools/repo_tools.py:71-89` runs `RSPS_BUILD_COMMAND` and `RSPS_TEST_COMMAND` with `subprocess.run(..., shell=True)`.
- Tool calling is disabled by default, but can be enabled through `RSPS_ENABLE_CREW_TOOLS`.

Risk:
- The command source is `.env`, so this is not directly user-controlled by default. However, once tool calling is enabled, agents can cause these commands to run and the shell gives full access to command chaining, redirection, expansion, and environment access.
- Build logs are returned to the model and can include sensitive paths, tokens printed by build systems, or private dependency URLs.

Mitigations:
- Replace free-form shell commands with an allowlisted command profile, for example `gradle-build`, `gradle-test`, `maven-build`, and `maven-test`, each mapped to fixed argv lists.
- If custom commands must remain, require `RSPS_ALLOW_SHELL_COMMANDS=true`, document the risk, and default it to false.
- Run build/test commands with a reduced environment that excludes API keys.
- Redact likely secrets from stdout/stderr before returning output to agents or dashboard logs.

### H-3: Work orders are raw prompt content sent to coding agents without prompt-injection boundaries

Evidence:
- `src/rsps_crewai_team/worker.py:31-40` and `src/rsps_crewai_team/worker.py:52-63` embed `order.body` directly into the agent prompt.
- `src/rsps_crewai_team/dashboard.py:226-233` allows arbitrary dashboard users to create work orders.
- `src/rsps_crewai_team/runtime/coding_worker.py:29-46` forwards the full prompt as an agent message.

Risk:
- A malicious or careless work order can instruct the coding agent to ignore project rules, expose secrets, alter unrelated files, weaken tests, or perform unsafe Git operations.
- The risk is amplified by autonomous mode and by `RSPS_GIT_COMMIT_AFTER_WORK=true`, which is shown as the default in `.env.example`.

Mitigations:
- Wrap work-order text in a clearly delimited untrusted-data block and add an explicit system/developer instruction that work-order text cannot override safety, scope, secret-handling, or repository rules.
- Add a preflight classifier for work orders that flags requests involving secrets, credentials, destructive operations, offensive security, broad filesystem access, or unrelated repositories.
- Require human confirmation for high-risk work orders before moving them from `inbox` to `running`.
- Give each worker a manifest of allowed write paths and reject or quarantine runs that modify files outside scope.

### H-4: Logs and status API may disclose sensitive operational data

Evidence:
- `src/rsps_crewai_team/dashboard.py:96-108` returns tails of recent log files through `/api/status`.
- `src/rsps_crewai_team/dashboard.py:151-158` returns configured build/test command strings.
- `src/rsps_crewai_team/dashboard.py:168-172` returns Git branch, status detail, remote URL, and local project paths.
- `src/rsps_crewai_team/runtime/coding_worker.py:81-82` logs the full worker command, including the full `--message` prompt text.

Risk:
- Logs can contain prompts, private paths, remote URLs, branch names, tool output, or accidental secrets printed by external tools.
- If the dashboard is exposed beyond localhost, `/api/status` becomes an information disclosure endpoint.

Mitigations:
- Redact secret-like strings, private tokens in URLs, and `.env`-style assignments before saving or returning logs.
- Do not log full prompts in command lines. Log the prompt file path plus a hash or short summary instead.
- Remove Git remote URLs, local absolute paths, and build/test command bodies from unauthenticated status responses.
- Split `/api/status` into safe public status and authenticated diagnostic status.

## Medium Issues

### M-1: Custom coding CLI template permits arbitrary executable selection

Evidence:
- `src/rsps_crewai_team/runtime/coding_worker.py:50-61` formats `OPENCLAW_CLI_CMD` or `RSPS_CODING_CLI_CMD` and executes the resulting argv list.

Risk:
- This avoids `shell=True`, which is good, but still allows `.env` to define any executable and arguments. If `.env` is edited accidentally or by an untrusted helper, autonomous runs can execute unintended local programs with API keys in the environment.

Mitigations:
- Keep `RSPS_CODING_CLI=openclaw` as the default.
- Require an explicit `RSPS_ALLOW_CUSTOM_CLI=true` gate before accepting custom CLI templates.
- Validate the executable path against an allowlist and reject world-writable executable paths.
- Pass a minimal environment to custom commands.

### M-2: Autonomous Git sync commits all changes without path scoping

Evidence:
- `src/rsps_crewai_team/runtime/git_sync.py:54-57` runs `git add -A` and commits everything in the repository.
- `src/rsps_crewai_team/runtime/git_sync.py:68-80` can push after successful work if `RSPS_GIT_PUSH_AFTER_WORK=true`.

Risk:
- Agent-created, user-created, generated, or unrelated local changes can be swept into an autonomous commit.
- If push is enabled, unintended files may leave the workstation.

Mitigations:
- Replace `git add -A` with a scoped allowlist derived from the work order or agent role.
- Before committing, produce a diff summary and require human approval unless a narrow safe path policy passes.
- Add secret scanning before every autonomous commit.
- Keep `RSPS_GIT_PUSH_AFTER_WORK=false` by default and require manual review for remote pushes.

### M-3: Worktree deletion is forceful and root is environment-configurable

Evidence:
- `src/rsps_crewai_team/runtime/git_sync.py:83-91` derives `RSPS_AGENT_WORKTREE_ROOT` from the environment and deletes an existing matching worktree path with `shutil.rmtree`.
- `src/rsps_crewai_team/runtime/git_sync.py:98-100` removes worktrees with `git worktree remove --force`.

Risk:
- Branch and worktree names are slugified, reducing path traversal risk, but an unsafe `RSPS_AGENT_WORKTREE_ROOT` can still point to an important directory tree.
- Force removal can hide useful forensic state after a failed agent run.

Mitigations:
- Require `RSPS_AGENT_WORKTREE_ROOT` to resolve under a dedicated parent such as `<repo parent>/.rsps-agent-worktrees`.
- Refuse to remove paths that are not recognized Git worktrees created by Daedalus.
- Keep failed worktrees by default, or archive their metadata before cleanup.

### M-4: Broad third-party agent dependency graph increases supply-chain exposure

Evidence:
- `pyproject.toml` depends on `crewai[litellm,tools]>=1.14.0` and `python-dotenv>=1.0.1`.
- `uv.lock` includes a large transitive graph with agent, web, parsing, model, vector DB, and networking packages.

Risk:
- The direct dependency range allows future CrewAI releases without an upper bound.
- Agent/tool ecosystems move quickly and may add new transitive behavior, telemetry, or tool execution surfaces.

Mitigations:
- Pin direct dependencies to reviewed versions and update through planned dependency review.
- Run `uv pip audit` or an equivalent vulnerability scanner in CI and before enabling autonomy.
- Consider removing the `tools` extra unless CrewAI tools are actively needed.
- Document which networked packages are expected to make outbound calls.

### M-5: Repository summarization can leak filenames and structure to external models

Evidence:
- `src/rsps_crewai_team/tools/repo_tools.py:23-56` walks up to 250 entries in `RSPS_REPO_PATH` and sends the listing into model context.
- `src/rsps_crewai_team/main.py:25-35` passes repository context to the CrewAI workflow.

Risk:
- File names, paths, internal naming, private module structure, or accidental secret filenames can be sent to third-party model providers.

Mitigations:
- Add denylisted directories and filename patterns such as `.env`, `secrets`, `credentials`, `keys`, `backups`, and private deployment configs.
- Provide a `RSPS_REPO_CONTEXT_SAFE_MODE=true` default that summarizes only build markers and high-level directories.
- Require explicit operator approval before sending repository context to remote LLMs.

## Low Issues

### L-1: `.env` exists locally but is correctly ignored and private

Evidence:
- `.gitignore` includes `.env`.
- Local file permissions observed for `.env` were `rw-------`.

Risk:
- Current local handling is reasonable. The residual risk is accidental leakage through logs, prompts, screenshots, or agent output rather than Git tracking.

Mitigations:
- Keep `.env` mode `0600`.
- Add a pre-commit secret scan and a log redaction helper.
- Avoid adding `.env` contents to memory, docs, dashboard responses, or worker prompts.

### L-2: Cron template uses absolute user paths and a broad user PATH

Evidence:
- `src/rsps_crewai_team/cron.py` and `cron/rsps-crewai.cron` set a fixed PATH and run scheduled tasks from the user account.

Risk:
- Absolute paths reduce ambiguity, but the cron environment is still capable of starting autonomous work every minute if `.env` enables it.

Mitigations:
- Keep cron installation manual.
- Add a startup log line that records whether autonomy is enabled without exposing secrets.
- Consider a lock file to prevent overlapping cron runs.

### L-3: Dashboard static file serving has no cache or security headers

Evidence:
- `src/rsps_crewai_team/dashboard.py:207-215` uses `SimpleHTTPRequestHandler` for static files.

Risk:
- For localhost-only development this is low risk, but if exposed remotely it lacks common hardening headers.

Mitigations:
- Add `X-Content-Type-Options: nosniff`, a restrictive `Content-Security-Policy`, and `Referrer-Policy: no-referrer`.
- Keep remote exposure behind a hardened reverse proxy if needed.

## Positive Findings

- No `eval()` or Python `exec()` usage was found in the reviewed source.
- Most subprocess calls use argv lists rather than shell strings.
- Dashboard worker actions are allowlisted rather than directly executing arbitrary request payloads.
- Autonomous execution is gated by `RSPS_ALLOW_AUTONOMOUS`.
- `.env` is ignored by Git and locally permissioned as private.
- Existing docs include safety boundaries and secret-handling guidance.

## Recommended Next Steps

1. Add authentication and CSRF/origin protection to dashboard mutating endpoints.
2. Remove or hard-gate `shell=True` build/test execution.
3. Add prompt-injection boundaries and work-order preflight review before autonomous execution.
4. Redact prompts, logs, Git remotes, paths, and command outputs before exposing them through `/api/status`.
5. Scope autonomous Git commits and add secret scanning before commit or push.
