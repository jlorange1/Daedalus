---
name: obsidian-project-memory
description: Maintain Obsidian-compatible Markdown project memory for the Daedalus repo. Use when Codex needs to read, create, or update repo-local memory notes covering project state, decisions, failed attempts, task graph, implementation context, and handoff notes without storing secrets.
---

# Obsidian Project Memory

Use this skill to keep durable, repo-local Markdown memory accurate and useful for future Codex sessions. Treat the memory as shared engineering context, not a private scratchpad.

## Read First

Before changing memory, inspect the repo and read any existing memory files that match the task, especially:

- `README.md`, contributor docs, and current task instructions.
- `memory/`, `docs/`, `notes/`, `.codex/`, or existing Obsidian vault folders if present.
- Existing files named like `decisions.md`, `failed-attempts.md`, `task-graph.md`, `project-memory.md`, or `handoff.md`.

Prefer existing structure and filenames. Create new Markdown files only when no suitable file exists and the user request requires memory to be recorded.

## Update Policy

- Write Obsidian-compatible Markdown: plain headings, lists, links, and wiki links only when the repo already uses them.
- Update memory after meaningful discoveries, implemented changes, architecture choices, blocked investigations, or task graph changes.
- Keep entries concise, dated when useful, and tied to concrete files, commands, or decisions.
- Preserve historical notes unless they are plainly wrong; mark superseded information instead of deleting useful context.
- Separate facts from inference. Use labels such as `Known`, `Decision`, `Open`, `Blocked`, and `Superseded` where helpful.
- Do not store chain-of-thought, credentials, private tokens, personal data, API keys, or secret configuration values.

## What To Capture

### Decisions

Record durable choices with:

- Decision summary.
- Rationale and tradeoffs.
- Files or systems affected.
- Date and status.
- Reversal criteria if known.

### Failed Attempts

Record attempts that future agents might otherwise repeat:

- Goal of the attempt.
- Commands, files, or approach used.
- Failure mode or observed result.
- Why it failed or what remains unknown.
- Safer next direction.

### Task Graph

Maintain current work as a small dependency graph:

- `Done`: completed tasks with evidence.
- `Active`: current task and owner if known.
- `Blocked`: blocker, dependency, and unblock condition.
- `Next`: ordered follow-ups.

Keep the graph practical; do not turn it into a full issue tracker unless the repo already does that.

## Editing Rules

- Modify only memory files relevant to the current task.
- Avoid broad rewrites, formatting churn, and unrelated cleanup.
- Link to repo files with relative Markdown links where useful.
- If memory conflicts with source code or tests, trust the source and update the note to reflect the conflict.
- If asked only to inspect or report, do not update memory unless the user explicitly asks.

## Handoff

At the end of memory updates, ensure the next agent can answer:

- What is true now?
- What changed?
- What was decided?
- What failed and should not be retried unchanged?
- What should happen next?
