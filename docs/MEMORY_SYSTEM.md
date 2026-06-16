# Memory System

Daedalus uses plain Markdown files as its persistent project memory. The system is designed for humans first: every file should be readable in a terminal, reviewable in Git, and linkable in Obsidian without a database or hidden state.

## Goals

- Preserve project direction, decisions, constraints, and operational state across agent sessions.
- Keep memory small enough that future agents can read it before acting.
- Make updates auditable through normal Git diffs.
- Separate stable facts from volatile task state.
- Avoid storing secrets, credentials, private tokens, or long generated logs.

## Location

Memory lives in `/memory`. Durable policy and usage instructions live in `/docs`.

| Path | Purpose | Update cadence |
|---|---|---|
| `memory/PROJECT_MEMORY.md` | Fast project snapshot and memory index. Read this first. | Every meaningful project-direction, architecture, preference, command, or status change |
| `memory/DECISIONS.md` | Decision records with date, rationale, alternatives, risk, and rollback. | Whenever a choice constrains future work |
| `memory/OPEN_QUESTIONS.md` | Questions that block or shape upcoming work. | Add when discovered; remove or resolve when answered |
| `memory/FAILED_ATTEMPTS.md` | Failed experiments and lessons learned. | Whenever an approach wastes time, breaks UX, or is explicitly rejected |
| `memory/TASK_GRAPH.md` | Active goals, waves, dependencies, blockers, and status. | Before and after multi-step work |
| `docs/MEMORY_SYSTEM.md` | Contract for what memory stores and how to maintain it. | Only when the memory system itself changes |

Related source-of-truth docs stay in `/docs` and should not be duplicated in full inside memory:

- `docs/SAFETY_BOUNDARIES.md` for autonomous behavior limits.
- `docs/STYLE_GUIDE.md` for GUI direction.
- `docs/ORCHESTRATION.md` for agent loop and conflict handling.
- `docs/INTELLIGENCE_ARCHITECTURE.md` for target capabilities.
- `docs/EVALS.md` for validation strategy.

## Obsidian Compatibility

- Use normal Markdown headings, lists, tables, and fenced code blocks.
- Use wiki links for cross-memory references when useful, such as `[[DECISIONS]]`.
- Keep filenames stable and uppercase with underscores for easy search.
- Avoid frontmatter unless the project later standardizes metadata.
- Prefer short dated entries over long narrative transcripts.

## What To Store

Store information that future agents or maintainers need to avoid rediscovery:

- Project purpose and current product direction.
- Architecture map and important file locations.
- User preferences that affect design, workflow, or safety.
- Durable constraints, especially legal, safety, branding, and secret-handling limits.
- Known commands that have been validated or are expected to work.
- Validated facts from tests, smoke checks, reviews, and browser verification.
- Decisions and their rationale.
- Open questions and blockers.
- Failed attempts and the lesson from each.
- Active task graph and dependency state.

## What Not To Store

Do not store:

- API keys, credentials, secrets, private URLs with tokens, or `.env` contents.
- Full logs, stack traces, dependency dumps, or generated transcripts.
- Speculative claims presented as facts.
- Large code snippets already available in tracked source files.
- Temporary scratch notes that will not matter after the current task.
- Personal data unrelated to the project.

If a long artifact matters, store a short summary and point to the file or command that reproduces it.

## Update Policy

Every agent working on Daedalus should read `memory/PROJECT_MEMORY.md` before non-trivial work. For multi-step or risky work, also read the relevant focused memory files.

Update memory when any of these happen:

- The user changes direction or states a durable preference.
- Architecture, commands, or workflow change.
- A decision is made that future agents should honor.
- A task starts, finishes, blocks, or changes owner/dependency.
- A validation command passes or fails in a way future work should know.
- An approach is rejected, fails materially, or should not be repeated.
- An open question is answered or a new blocker appears.

Do not update memory for tiny edits that do not affect future behavior.

## File Responsibilities

### `PROJECT_MEMORY.md`

This is the read-first snapshot. Keep it concise and current. It should summarize:

- Repository purpose.
- Current direction.
- Architecture map.
- Memory map.
- Known commands.
- Constraints.
- User preferences.
- Validated facts.
- Active unfinished tasks.

It may link to detailed memory files, but it should not duplicate full decision logs or task tables.

### `DECISIONS.md`

Use one dated record per decision. Include:

- Date.
- Decision.
- Why.
- Alternatives considered.
- Risk.
- Rollback plan, if possible.

### `OPEN_QUESTIONS.md`

Use short bullets. Include only questions that matter for planning, implementation, or validation.

When resolved, either remove the question or mark it with the answer and date if the history matters.

### `FAILED_ATTEMPTS.md`

Use dated entries with:

- Attempt.
- Failure.
- Lesson.

Focus on practical lessons, not blame.

### `TASK_GRAPH.md`

Track active goals as tables with IDs, dependencies, owner, status, and risk. Status values should be simple:

- `pending`
- `in_progress`
- `blocked`
- `done`
- `dropped`

Keep blockers explicit and dated when possible.

## Conflict And Merge Rules

- Parallel agents must use disjoint write scopes.
- If two agents need the same memory file, the parent agent merges manually.
- Prefer appending dated entries to rewriting history.
- Rewrite `PROJECT_MEMORY.md` when the snapshot becomes stale or noisy.
- Never delete useful prior memory unless it is moved to a more appropriate memory file or is clearly obsolete.

## Review Checklist

Before final handoff on meaningful work:

1. Read the relevant memory files.
2. Update `PROJECT_MEMORY.md` if the project snapshot changed.
3. Add a decision record if a durable choice was made.
4. Update `TASK_GRAPH.md` if task state changed.
5. Record failed attempts or rejected approaches.
6. Verify no secrets or oversized logs were added.
7. Keep the diff limited to files required by the task.
