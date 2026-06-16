# Daedalus GUI Style Guide

## Product Direction

Daedalus is a sci-fi RSPS operations control room for an autonomous AI game-development studio. The first screen must remain the usable dashboard, not a landing page. Prioritize dense status, queue visibility, agent department awareness, and safe worker controls over decoration.

## Layout Contract

- Desktop target: fixed operational canvas with `body { min-width: 1180px; }` and `.shell` capped around `1487px` wide by `1024px` tall.
- Primary grid: left sidebar, central work queue / agent mesh / automation timeline column, right telemetry inspector.
- Major modules use `.module-window` and receive draggable `.window-grip` handles from `wireModuleWindows()`. Dragging is local-only and double-clicking a grip resets the module position.
- Mobile fallback: below `1180px`, stack sections vertically and keep all controls reachable.
- Do not nest cards inside cards. Use framed panels for major dashboard regions and individual cards only for repeated work orders.

## Visual Language

- Theme: dark sci-fi command surface using glassy navy panels, cyan grid lines, neon green readiness accents, violet secondary glow, and compact operational labels.
- Core colors currently in CSS:
  - Ink: `#dcefff`
  - Shadow: `#02060b`
  - Panel: `#06111f`
  - Cyan line/glow: `#2bc6ff`, `#48d9ff`
  - Success green: `#5dffb0`
  - Violet secondary glow: `#9d7cff`
  - Warning amber: `#ffd36a`
  - Danger red: `#ff5e7a`
- Do not reintroduce Stardew-like, medieval fantasy, parchment, wood, brass, cozy lantern, or farmhouse styling in the shipped control UI.
- Existing source-sheet assets may remain in the repository for provenance, but the active dashboard surface should read as sci-fi control software.

## Typography

- Current stack: `"Segoe UI", "Trebuchet MS", Verdana, sans-serif`.
- Headings: uppercase, compact, cyan or green, small enough for panels. Avoid hero-scale type inside dashboard regions.
- Work-card text must remain scannable at small sizes. Use short titles and clip overflow with ellipsis where content is dynamic.
- Letter spacing may be positive for uppercase labels, never negative.

## Controls

- Main commands are icon-first block buttons using asset icons: enqueue, build/test, push branch, run duo.
- State indicators:
  - Good: green chip/dot/meter.
  - Warning/tools needed: gold or warn chip.
  - Disabled/autonomy off: dark switch plus explicit `ON`/`OFF` text.
- Dialogs use dark sci-fi panels and high-contrast inputs. Keep enqueue form fields: `title`, `body`.
- Toasts are short status messages at bottom-right with `role="status"` and `aria-live="polite"`.

## Asset Rules

- Agent departments are represented as unique sci-fi cores, not character sprites:
  - Command: neural mesh
  - Server: tesseract field
  - Content: liquid metal orb
  - QA: reactor core
  - Security: shield lattice
  - Docs: archival prism
- New agent visuals should stay in this family: luminous, abstract, operational, and readable at small sizes.
- Icons may reuse existing files where they fit the control-panel style, but avoid fantasy props or role portraits in the active UI.
