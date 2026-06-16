---
name: vibe-kanban-workspaces
description: "Use when adapting Vibe-Kanban-style planning and execution patterns to Daedalus work: visible work lanes, task cards, agent workspace/branch/worktree tracking, terminal/log/dev-server awareness, diff review, PR handoff, and avoiding proprietary copying."
---

# Vibe-Kanban Workspaces for Daedalus

Use this skill to organize Daedalus development work with Kanban-like visibility while preserving Codex autonomy and repo safety.

## Principles

- Treat Vibe-Kanban as an inspiration for workflow patterns, not as source material to copy. Do not reproduce proprietary UI, text, implementation details, or assets.
- Keep work visible: every active effort should have a lane, a task card, an owner or agent, a workspace, current state, and next action.
- Prefer small, reviewable tasks that can move cleanly from idea to implementation, diff review, and PR handoff.
- Make local development state explicit: branch, worktree, dev server, terminal command, logs, errors, and whether the app is ready to inspect.

## Workspace Model

For each Daedalus task, track:

- `lane`: backlog, ready, active, blocked, review, or done.
- `task`: short user-facing title plus acceptance criteria.
- `agent`: human or Codex agent responsible for the current action.
- `workspace`: repo path, branch name, and worktree path if separate.
- `runtime`: dev server command, URL, terminal/session id, and key logs.
- `review`: changed files, test status, diff summary, risks, and PR handoff notes.

When implementing UI, show this information as dense operational controls: lanes, cards, status chips, branch/worktree labels, log/dev-server indicators, and review actions. Avoid marketing-style layouts.

## Operating Flow

1. Clarify the task card: define lane, goal, scope, acceptance criteria, and known constraints.
2. Prepare the workspace: confirm repo, current branch, dirty files, and whether a new branch or worktree is needed.
3. Run or attach runtime awareness: identify dev server command, URL, terminal state, recent logs, and failure signals.
4. Implement narrowly: keep edits tied to the task card and preserve unrelated user changes.
5. Review the diff: summarize changed files, behavior changes, tests run, and any remaining risk.
6. Handoff: move the card to review/done, include branch/worktree, server URL if running, and PR-ready summary.

## Daedalus UI Guidance

- Use lanes and cards as operational surfaces, not decorative boards.
- Cards should expose actionable state: status, branch, worktree, assigned agent, latest command, log health, diff count, and review readiness.
- Provide controls for common actions: open workspace, start/stop dev server, inspect logs, view diff, run tests, and prepare PR notes.
- Surface blocked states with the exact missing input, failing command, or log excerpt needed to continue.
- Keep visual language original to Daedalus; borrow the workflow concept only.

## Review And Handoff Checklist

- Branch/worktree is named and current.
- Dirty files are understood and unrelated changes are preserved.
- Dev server and logs are checked when the change affects runtime behavior.
- Diff is reviewed for scope, regressions, and accidental churn.
- Tests or manual verification are recorded.
- PR handoff includes summary, validation, risks, and screenshots or URLs when relevant.
