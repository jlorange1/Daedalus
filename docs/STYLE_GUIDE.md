# Daedalus GUI Style Guide

## Product Direction

Daedalus is a retro fantasy software-studio control room: part operational dashboard, part game-room command center. The first screen must remain the usable dashboard, not a landing page. Prioritize dense status, queue visibility, and safe worker controls over decoration.

## Layout Contract

- Desktop target: fixed operational canvas with `body { min-width: 1180px; }` and `.shell` capped around `1487px` wide by `1024px` tall.
- Primary grid: left sidebar, central board/studio/schedule column, right inspector.
- Mobile fallback: below `1180px`, stack sections vertically and keep all controls reachable.
- Do not nest cards inside cards. Use framed panels for major dashboard regions and individual cards only for repeated work orders.

## Visual Language

- Theme: warm pixel-art workshop using wood, stone, parchment, brass, dark paneling, and green readiness accents.
- Core colors currently in CSS:
  - Ink: `#24180e`
  - Shadow: `#130d08`
  - Panel: `#1c1710`
  - Line/brass: `#7b542c`, production border `#9b672b`
  - Parchment: `#d5b982`, paper `#ead5a0`
  - Success green: `#5fad3f`, bright meter `#9ee36d`
  - Warning gold: `#d49a35`
  - Blue lane/accent: `#2f74a2`
  - Danger red: `#a54a2f`
- Use textured PNGs already in `src/rsps_crewai_team/dashboard_static/assets/`: `wood-floor.png`, `stone-wall.png`, `dark-panel.png`, `sample-card.png`, and `prototype-studio-floor-full.png`.
- Image assets should render pixelated with `image-rendering: pixelated` where scaled.

## Typography

- Current stack: `"Trebuchet MS", Verdana, sans-serif`.
- Headings: uppercase, compact, gold, small enough for panels. Avoid hero-scale type inside dashboard regions.
- Work-card text must remain scannable at small sizes. Use short titles and clip overflow with ellipsis where content is dynamic.
- Letter spacing may be positive for uppercase labels, never negative.

## Controls

- Main commands are icon-first block buttons using asset icons: enqueue, build/test, push branch, run duo.
- State indicators:
  - Good: green chip/dot/meter.
  - Warning/tools needed: gold or warn chip.
  - Disabled/autonomy off: dark switch plus explicit `ON`/`OFF` text.
- Dialogs use dark panels with parchment inputs. Keep enqueue form fields: `title`, `body`.
- Toasts are short status messages at bottom-right with `role="status"` and `aria-live="polite"`.

## Asset Rules

- Prefer existing bitmap assets over CSS-only decoration.
- Do not introduce generic stock art. Assets must show the actual studio, workstation, role portrait, icon, or UI state.
- New role assets must match current filenames/patterns:
  - `role-portrait-{producer|backend|content|qa|security|docs}.png`
  - `icon-{home|queue|builds|github|cron|settings|build|plus|robot|push}.png`
  - optional station assets should map to the same six role keys.
