---
name: daedalus-orchestration
description: Use for safe long-horizon orchestration on the Daedalus game project, including decomposing work, routing tasks to agents, checking conflicts, synthesizing results, updating memory, applying safety gates, and validating outcomes.
---

# Daedalus Orchestration

Use this skill when coordinating multi-step Daedalus work that may span files, agents, sessions, or project memory. Keep orchestration explicit, reversible, and grounded in current repo state.

## Operating Loop

1. Restate the objective, constraints, target files, and definition of done.
2. Inspect current state before assigning work: git status, relevant docs, task logs, memory, and touched files.
3. Decompose into small tasks with owners, inputs, expected outputs, validation, and merge order.
4. Route work to the narrowest capable agent or local workflow; avoid overlapping writes unless the merge path is clear.
5. Run conflict checks before and after each task batch.
6. Synthesize outputs into one coherent implementation, preserving user changes and project conventions.
7. Validate with the lightest reliable checks first, then broader tests for shared behavior or risky changes.
8. Update project memory only with durable decisions, completed work, known risks, and next actions.

## Task Decomposition

- Break long work into independently reviewable steps: research, design, implementation, asset work, testing, documentation, and cleanup.
- For each task, define scope boundaries and files likely to be touched.
- Sequence tasks so shared interfaces, schemas, save data, or asset contracts are settled before dependent work.
- Keep speculative ideas out of implementation tasks unless the user asked for exploration.

## Agent Routing

- Use specialist agents for bounded research, asset audits, test investigation, or independent review.
- Give agents only the context needed for their task plus exact output requirements.
- Ask agents for evidence: file paths, line references, commands run, and unresolved risks.
- Treat agent output as input, not truth; verify before merging conclusions or code.

## Conflict Checks

- Check `git status` before editing and before final synthesis.
- Identify files with concurrent or user-made changes; read them before editing.
- Do not overwrite unrelated work. If two tasks touch the same file, serialize them and merge intentionally.
- Re-run focused searches after edits for duplicate logic, stale names, broken references, and TODOs created during the work.

## Synthesis

- Prefer existing Daedalus patterns over new abstractions.
- Combine agent outputs into a single consistent direction; resolve contradictions with repo evidence.
- Keep changes scoped to the objective. Defer unrelated refactors and nice-to-have cleanup.
- Record assumptions and residual risks plainly when evidence is incomplete.

## Memory Updates

- Update memory only after validation or when a durable decision is made.
- Store: decision, rationale, affected systems, validation performed, remaining risks, and next checkpoint.
- Do not store secrets, transient logs, unverified guesses, or raw agent chatter.

## Safety Gates

- Before edits: confirm scope, dirty worktree, affected files, and rollback strategy.
- Before destructive actions: require explicit user approval.
- Before asset or save-format changes: check downstream references and compatibility.
- Before final reply: confirm requested files only, validation status, and any unhandled risks.

## Validation

- Match validation depth to risk: syntax checks for isolated docs, focused tests for local logic, integration or play checks for gameplay-facing changes.
- Prefer deterministic commands already used by the project.
- If validation cannot run, state the blocker and the best manual check.
- Final summaries must include changed paths, what changed, and validation performed.
