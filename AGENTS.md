# Daedalus Agent Contract

Daedalus is an autonomous AI game-development studio scaffold for RSPS-oriented work. Agents in this repository must behave like a disciplined engineering organization: plan first, work in bounded scopes, validate before handoff, and update memory when project direction changes.

## Operating Rules

- Prefer small, reviewable changes over broad rewrites.
- Do not revert user changes or other agent changes without explicit instruction.
- Keep agent roles narrow. A planning agent plans, a test agent tests, a documentation agent documents, and an implementation agent edits only its assigned files.
- Update `/memory/PROJECT_MEMORY.md`, `/memory/DECISIONS.md`, and `/memory/TASK_GRAPH.md` after meaningful changes.
- Record failed experiments in `/memory/FAILED_ATTEMPTS.md`.
- Use `/docs/SAFETY_BOUNDARIES.md` as the safety contract for all autonomous behavior.
- Avoid protected branding in shipped UI or generated assets.
- Never expose API keys, credentials, or secrets in docs, logs, screenshots, commits, or UI.

## Required Review Loop

Before finalizing work:

1. Compare the change against the active task graph.
2. Run relevant tests or smoke checks.
3. Review for unsafe shell execution, secret exposure, destructive file operations, and prompt-injection surfaces.
4. Update memory and docs if behavior or project direction changed.
5. Leave exact next actions.

## Parallel Work

Parallel agents must use disjoint write scopes. If two agents need the same file, the parent agent merges manually after reviewing both outputs.
