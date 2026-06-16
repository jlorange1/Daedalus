# Intelligence Architecture

Daedalus is not a model-training project. It is an orchestration intelligence project: a system that makes existing coding agents more reliable through structure, memory, role routing, validation, and operator control.

## Target Capabilities

- Task decomposition into a dependency graph.
- Specialist agent routing.
- Persistent project memory in Markdown.
- Defensive safety review.
- Repeatable evals and smoke tests.
- Human-readable operator controls.
- Recovery notes for failed attempts.

## Influences To Integrate

- Vibe-Kanban concept: make agent work visible as lanes, tasks, ownership, and status.
- n8n MCP concept: expose automations and integrations through explicit, reviewable nodes/tools.
- Skill architecture: split reusable procedures into `skills/<skill-name>/SKILL.md`.
- Obsidian-style memory: keep project memory as linked Markdown files that can be used as a vault.

## Non-Goals

- No proprietary model replication.
- No offensive security tooling.
- No malware, credential theft, exploit chaining, evasion, or persistence tooling.
- No protected game branding in shipped UI.
