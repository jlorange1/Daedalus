# Ponytail Layer

Ponytail is a minimalism guardrail for the RSPS agent workforce. It keeps the team from overbuilding by forcing every agent to prefer the smallest correct implementation before adding frameworks, abstractions, generated boilerplate, or new dependencies.

Source: https://github.com/DietrichGebert/ponytail

## How It Applies Here

- CrewAI planning receives a Ponytail policy in each task prompt.
- OpenClaw coding workers receive the same policy before every work order.
- `AGENTS.md` makes the rule visible to compatible agent tools working from this project.
- Intentional shortcuts should be marked with `ponytail:` comments and an upgrade path.

## Modes

- `off`: no Ponytail policy injection.
- `lite`: prefer simple solutions, but keep the prompt short.
- `full`: default; includes the full project policy.
- `ultra`: strongest mode; asks agents to actively delete or avoid unnecessary work.

Configure with:

```text
RSPS_PONYTAIL_ENABLED=true
PONYTAIL_DEFAULT_MODE=full
```

For RSPS work, Ponytail must never weaken security-critical behavior: packet validation, account auth, item/currency persistence, admin permissions, trade/bank safety, database migration safety, logging for abuse surfaces, or tests around these paths.
