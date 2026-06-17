# Intelligence Upgrade Integrations

Daedalus adapts public project patterns into native, validated configuration. These are not vendored dependencies and do not grant execution authority by themselves.

## Sources Adapted

- `github/spec-kit`: spec-driven lifecycle and required implementation artifacts.
- `nextlevelbuilder/ui-ux-pro-max-skill`: UI quality gates and professional interaction polish.
- `lobehub/lobehub`: reference-only agent operations dashboard patterns.
- `OpenHands/OpenHands`: reference-only guarded coding session and workspace lifecycle patterns.
- `dair-ai/Prompt-Engineering-Guide`: prompt pattern and critique-loop concepts.
- `bytedance/deer-flow`: long-horizon memory, skill, subagent, and message-gateway concepts.
- `OpenBB-finance/OpenBB`: reference-only analyst workflow patterns for the profitability engine.
- `FoundationAgents/MetaGPT`: software-company role decomposition and SOP handoffs.
- `ComposioHQ/awesome-claude-skills`: reference-only curated skill registry pattern.

## Native Files

- `src/rsps_crewai_team/config/inspiration_sources.json`
- `src/rsps_crewai_team/config/spec_contracts.json`
- `src/rsps_crewai_team/config/prompt_patterns.json`
- `src/rsps_crewai_team/config/skill_catalog.json`
- `src/rsps_crewai_team/config/profitability_model.json`
- `src/rsps_crewai_team/runtime/intelligence.py`
- `tests/test_intelligence_configs.py`

## Dashboard Additions

The dashboard now shows:

- Profit Engine: downside/base/upside net scenarios with ethical monetization guardrails.
- Spec & Skill Systems: source count, spec artifacts, prompt patterns, local skills, and approval gates.
- Agency Layer: workflow count, department count, and parallel DAG levels.

## Profitability Policy

The OpenBB-inspired layer is an internal planning model, not financial advice. It is designed to make server operations sustainable without pay-to-win mechanics.

Allowed direction:

- Cosmetics
- Non-pay-to-win memberships
- Transparent community events
- Account services that do not distort progression

Blocked direction:

- Gambling loops
- Deceptive scarcity
- Minors-targeted pressure
- Pay-to-win power, progression, or economy advantages

## Next Engineering Step

The first durable orchestrator run-state model is now present:

1. Workflow starts create `logs/agency-runs/<run-id>/manifest.json`.
2. First ready steps are queued as work orders with sidecar metadata.
3. Work-order sidecars connect `workflow_id`, `run_id`, `step_id`, department, code-write status, and approval status.
4. Worker runs create bounded JSON evidence under `logs/runs/`.
5. The dashboard shows workflow runs and recent worker manifests.
6. Completed or failed work orders advance their workflow step.
7. Completed dependencies unblock downstream steps.
8. Code-writing steps pause at `awaiting_review` until approved from the dashboard.

The next durable upgrade is richer artifact review: attach summaries, changed files, and validation evidence to each workflow step before approval.
