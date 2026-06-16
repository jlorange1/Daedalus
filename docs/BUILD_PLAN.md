# GUI Build Plan

## Goal

Turn the current Daedalus dashboard into a reliable implementation-ready RSPS studio GUI while preserving the existing static frontend and Python API shape.

## Constraints

- Keep the first screen as the operational dashboard.
- Do not require a JS framework unless the app outgrows the current static controller.
- Worker execution must continue to respect `RSPS_ALLOW_AUTONOMOUS`.
- Do not expose secrets from `.env`, worker prompts, or logs.
- Keep changes reviewable: frontend, backend API, assets, and docs should land in small batches.

## Phase 1: Stabilize Current Dashboard

- Add missing DOM/CSS alignment tests for rendered agent desks, queue lanes, inspector, dialog, and toast.
- Add a reduced-motion CSS block for existing infinite animations.
- Clamp progress meter values client-side before applying `--value`.
- Handle `/api/status` fetch failure with a visible stale/offline state instead of only a toast.
- Replace visual fallback backlog with a clearly marked demo mode or server-provided seed state.

Acceptance:

- `uv run rsps-dashboard` opens without console errors.
- Empty queues, missing RSPS repo, dirty git state, and unavailable Java/Git LFS all render clearly.

## Phase 2: Implement Real Panel Navigation

- Use existing `data-panel` values to switch sections: Studio, Queue, Builds, GitHub, Cron, Settings.
- Keep Studio as default.
- Preserve sidebar status card across panels.
- Queue panel should expose full queue lists, not only four cards per lane.
- Settings panel should show read-only env state first; writes require a separate safety decision.

Acceptance:

- Every sidebar button changes visible content and active state.
- Browser refresh returns to a deterministic default or hash-selected panel.

## Phase 3: Safe Action Workflows

- Add confirmation dialogs for `run-duo`, `run-once`, `cron-tick`, and future push actions.
- Show action preconditions before spawn: autonomy flag, RSPS repo path, Java, Git LFS, OpenClaw.
- Stream or poll `dashboard-actions.log` into a read-only action log panel.
- Keep Build/Test as a gated action until command execution, timeout, and log handling are specified.

Acceptance:

- Dangerous actions cannot be triggered accidentally.
- Failed actions show API error, precondition failure, or log path without hiding the board.

## Phase 4: Data And Accessibility Hardening

- Add server-side schema tests for `/api/status`, `/api/enqueue`, and `/api/action`.
- Ensure all dynamic HTML continues through `escapeHtml`.
- Add keyboard focus states for nav, commands, work cards, agent desks, dialog controls.
- Add accessible names for icon-first buttons and clickable agent desks.

Acceptance:

- Keyboard-only use can enqueue, inspect agents, pause/resume time, and trigger confirmed actions.
- Automated tests cover basic API validation and XSS escaping on queue titles/body-derived display.

## Phase 5: Visual Polish

- Consolidate stale CSS passes once the final composition is confirmed.
- Keep the production selectors documented in `COMPONENT_MAP.md`.
- Verify desktop `1440x1024`, minimum desktop `1180x800`, and stacked mobile widths.
- Run screenshot checks for text overflow, panel overlap, nonblank assets, and modal layout.

Acceptance:

- No incoherent overlap at target viewports.
- Pixel assets are crisp and aligned.
- Workstation selected/working states are visible without blocking text.

## Verification Commands

```bash
uv run rsps-dashboard
```

```bash
uv run rsps-worker status
```

When tests are added:

```bash
uv run pytest
```

