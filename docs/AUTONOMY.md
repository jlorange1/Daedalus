# Daedalus Autonomy

Daedalus can run without Codex after it is launched, but it is still a local automation system.

## What Runs Without Codex

- The dashboard runs as a local Python HTTP server.
- `rsps-cron tick` can run one-minute autonomous watchdog cycles from cron or the user systemd timer.
- OpenClaw workers can call OpenRouter and edit the configured RSPS repository when `RSPS_ALLOW_AUTONOMOUS=true`.
- Successful worker runs can commit and push to the configured `RSPS_GIT_REMOTE`.

## What Must Be Running

- This PC must be awake and online.
- `.env` must contain the OpenRouter API key.
- OpenClaw must be installed and configured.
- The RSPS source must be clean and reachable.
- A launcher, terminal process, cron job, or future systemd user service must be active.

## Current Safety Defaults

- Workers use isolated git worktrees.
- Worker child processes receive the assigned worktree as `RSPS_REPO_PATH`.
- `RSPS_REQUIRE_WORKER_CHANGES=true` prevents no-op model replies from being marked successful.
- Pushes use `RSPS_GIT_REMOTE=github`.
- Pushes to upstream `gitlab.com/2009scape/2009scape` are refused.

## One-Click Launcher

Use the desktop launcher:

```text
/var/home/Scaar/Desktop/Daedalus Studio.desktop
```

It starts the dashboard at:

```text
http://127.0.0.1:8765
```

The launcher starts the dashboard UI. It does not install cron by itself.

## One-Minute Autonomous Watchdog

Install the user cron only after you are comfortable with supervised `run-duo` behavior:

```bash
cd "/var/home/Scaar/Desktop/game project/Daedalus"
PYTHONPATH=src python3 -m rsps_crewai_team.cron install
```

The watchdog checks every minute. It starts work only when `RSPS_ALLOW_AUTONOMOUS=true` and no work order is currently in `work_orders/running`.
