# Agency-Agents Integration

Daedalus now includes a native agency layer inspired by:

- `msitarzewski/agency-agents` (`MIT`)
- `jnMetaCode/agency-orchestrator` (`Apache-2.0`)

The integration adapts public operating patterns rather than copying the general-purpose agency wholesale. Daedalus remains an RSPS game-development studio with defensive safety gates, OpenRouter model routing, CrewAI planning, OpenClaw coding workers, GitHub sync, and local memory.

## What Was Adopted

- Specialized roles with explicit mission, deliverables, tools, permissions, handoffs, and safety limits.
- Workflow definitions that form a dependency graph.
- Parallel execution levels derived from DAG dependencies.
- Clear separation between planning, implementation, QA, security, release, operations, and documentation.
- Source attribution for the upstream public projects.

## Native Files

- `src/rsps_crewai_team/config/agency_catalog.json`: department catalog and role contracts.
- `src/rsps_crewai_team/config/agency_workflows.json`: dependency-aware studio workflows.
- `src/rsps_crewai_team/runtime/agency.py`: loader, validator, DAG-level builder, and status payload.
- `tests/test_agency_config.py`: catalog and workflow validation.

## Department Model

The catalog currently covers 14 departments:

1. Executive Production
2. Server Planning
3. Design Direction
4. Backend Engineering
5. Gameplay Content
6. Client UX
7. World & Quest Design
8. Economy & Balance
9. QA Automation
10. Security & Anti-Abuse
11. Build & Release
12. DevOps & GitHub
13. Art & Audio Direction
14. Documentation

Each department has:

- `id`
- `display_name`
- `agent_key`
- `model_env`
- `mission`
- `deliverables`
- `tools`
- `permissions`
- `handoff_to`
- `safety_limits`

## Workflow Model

Each workflow has:

- `id`
- `name`
- `description`
- `concurrency`
- `entrypoint`
- `steps`

Each step has:

- `id`
- `department`
- `depends_on`
- `output`
- `task`

The runtime builds execution levels from dependencies. Steps in the same level can run in parallel once earlier dependencies complete.

## Safety Rules

- The agency catalog does not grant write access by itself.
- RSPS source writes still require `RSPS_ALLOW_AUTONOMOUS=true`.
- Security work is defensive only.
- Release/push work must pass QA and security gates.
- Secrets must never be written to memory, docs, workflow files, or dashboard payloads.

## Future Work

- Route queued work orders to a workflow automatically based on title/body.
- Store workflow run traces under `logs/agency-runs/`.
- Add per-step status to the dashboard once execution traces exist.
- Add a CLI command to print workflow levels and department contracts.
