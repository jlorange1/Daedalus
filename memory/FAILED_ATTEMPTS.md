# Failed Attempts

## 2026-06-16

- Attempt: Iterative fantasy/Stardew dashboard polish.
- Failure: User rejected the direction and reported broken graphics.
- Lesson: Do not keep layering old asset styles when the requested direction changes. Prefer a clean active skin and hard-disable obsolete assets.

- Attempt: Browser verification inside the default sandbox.
- Failure: Headless Chromium may fail with sandbox host shutdown errors.
- Lesson: Use the approved escalated Playwright command path for dashboard screenshot verification when sandboxed launch fails.

## 2026-06-16 / 2026-06-17

- Attempt: First `rsps-worker run-duo` autonomous server run.
- Failure: Agent worktree paths were returned relative to the Daedalus process, so subprocess `cwd` resolution failed before coding started.
- Lesson: Resolve worktree roots and worktree paths to absolute paths before returning them to worker subprocesses.

- Attempt: Retried `rsps-worker run-duo` with persistent OpenClaw agent sessions and fixed free model IDs.
- Failure: Builder hit OpenRouter rate limits on `qwen/qwen3-coder:free`; reviewer reused or entered an unhelpful session state and completed without changes.
- Lesson: Use a unique OpenClaw `--session-key` per work order and route coding agents through `openrouter/free` unless a specific free model is proven available.

- Attempt: Retried `rsps-worker run-duo` with `RSPS_CODING_MODEL=openrouter/free`.
- Failure: OpenClaw rejected the model override as `openrouter/openrouter/free`; its CLI accepts the special OpenRouter free-router alias as `free`, while concrete OpenRouter models keep the `openrouter/` prefix.
- Lesson: Normalize only the `openrouter/free` alias to `free` before passing `--model` to OpenClaw, and allow-list `openrouter/free` in the local OpenClaw config.
