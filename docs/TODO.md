# GUI TODO

## Immediate

- Add reduced-motion CSS for `bob` and any future loops.
- Clamp agent progress meters to `0..100`.
- Add an offline/stale state when `/api/status` fails.
- Make agent desks keyboard-focusable and selectable with Enter/Space.
- Add confirmation before spawning `run-duo` or `cron-tick`.

## API

- Add tests for:
  - `/api/status` shape with configured and missing RSPS repo.
  - `/api/enqueue` validation for empty title/body.
  - `/api/action` allowlist behavior.
  - work-order filename slug generation.
- Add response field for server time if the day/clock becomes backend-owned.
- Add explicit `demo` flag only if seeded visual cards are intentionally reintroduced later.

## Frontend

- Implement real sidebar panel switching from existing `data-panel` attributes.
- Add full Queue view with all visible work orders and file/status metadata.
- Add Builds view for configured build/test commands, last run status, and log tail.
- Add GitHub view for Daedalus and RSPS remotes, branch, dirty state, and push policy.
- Add Cron view for rendered schedule, next tick, and last tick log.
- Add Settings view for read-only environment and readiness diagnostics.

## Visual

- Consolidate duplicated/stale CSS passes after screenshot QA.
- Confirm final agent DOM: either composed `.station-scene` art or simplified `.agent-hitbox`, then remove unused selectors.
- Keep `prototype-studio-floor-full.png` as the floor source until modular prop placement is production-ready.
- Add visible selected-agent state that works on both pointer and keyboard focus.

## Safety

- Never run worker actions unless `RSPS_ALLOW_AUTONOMOUS=true`.
- Do not add frontend controls that write `.env` or push git branches without a separate confirmation design.
- Redact secrets from logs before any log tail becomes visible in the UI.
- Keep Build/Test disabled or toast-only until command execution and timeout behavior are implemented.
