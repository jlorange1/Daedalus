# Dashboard Asset Inventory

This inventory documents the dashboard asset pipeline without changing app, CSS, HTML, or asset files. Current dashboard assets live under `src/rsps_crewai_team/dashboard_static/assets/` and are generated from project-owned source sheets by `scripts/dashboard_assets.py`.

## Pipeline

Run:

```bash
uv run python scripts/dashboard_assets.py
```

The script:

1. Copies configured generated PNGs from `../images/dashboard-generated-assets/` into `assets/source_sheets/` using stable project-safe names.
2. Crops static UI slices into `assets/sliced/`.
3. Crops animation strips into `assets/animations/`.
4. Writes manifests into `assets/manifests/`.
5. Validates that manifest-referenced PNG files exist and have valid PNG headers.

## Source Sheets

| Source sheet | Role |
|---|---|
| `source_sheets/ui_kit_overview.png` | Banners, buttons, and status meter source art. |
| `source_sheets/frame_kit.png` | Resizable panel and dark inset frame source art. |
| `source_sheets/ui_icons_atlas.png` | Icon atlas source retained for dashboard icon expansion. |
| `source_sheets/board_atlas.png` | Task card state source art. |
| `source_sheets/environment_kit.png` | Environment tile and prop source retained for scene expansion. |
| `source_sheets/workstation_atlas.png` | Workstation source retained for role/station expansion. |
| `source_sheets/agent_animation_sheet.png` | Agent idle and typing animation source art. |
| `source_sheets/portrait_status_sheet.png` | Role/status portrait and speech bubble source art. |
| `source_sheets/ambient_props_sheet.png` | Ambient props and lantern/fire animation source art. |
| `source_sheets/timeline_widgets_sheet.png` | Schedule, day cycle, progress, and status widget source art. |
| `source_sheets/prototype_scene.png` | Full studio floor composition source art. |

## Sliced Outputs

| Output | Source | Usage |
|---|---|---|
| `sliced/cards/task_card_default.png` | `board_atlas` | Default task card. |
| `sliced/cards/task_card_review.png` | `board_atlas` | Review-state task card. |
| `sliced/cards/task_card_done.png` | `board_atlas` | Done-state task card. |
| `sliced/panels/wood_panel_large.png` | `frame_kit` | Resizable warm wood panel frame. |
| `sliced/panels/dark_panel_base.png` | `frame_kit` | Dark inset panel base. |
| `sliced/ui/green_banner_large.png` | `ui_kit_overview` | Large green banner. |
| `sliced/ui/button_primary_default.png` | `ui_kit_overview` | Primary wood action button. |
| `sliced/status/status_bar_green.png` | `ui_kit_overview` | Green status meter. |
| `sliced/widgets/bubble_code.png` | `portrait_status_sheet` | Code status bubble. |
| `sliced/widgets/bubble_bug.png` | `portrait_status_sheet` | Bug/QA status bubble. |
| `sliced/widgets/bubble_docs.png` | `portrait_status_sheet` | Docs status bubble. |
| `sliced/widgets/bubble_shield.png` | `portrait_status_sheet` | Security status bubble. |
| `sliced/ambient/lantern.png` | `ambient_props_sheet` | Hanging lantern prop. |
| `sliced/ambient/server_lights.png` | `ambient_props_sheet` | Server light prop. |
| `sliced/widgets/day_cycle_panel.png` | `timeline_widgets_sheet` | Day cycle widget panel. |
| `sliced/widgets/schedule_timeline_frame.png` | `timeline_widgets_sheet` | Schedule timeline frame. |
| `sliced/agents/prototype_studio_floor_full.png` | `prototype_scene` | Full studio floor with six agent desks. |

## Manifests

| Manifest | Contents |
|---|---|
| `manifests/assets.json` | Static sliced assets with `name`, `file`, `type`, `usage`, `source`, `legal_safe_name`, `license_status`, and `recommended_size`. |
| `manifests/animations.json` | Animation strips with frame dimensions, frame count, FPS, loop flag, anchor, usage, and sheet size. |
| `manifests/nine_slice.json` | Resizable panel definitions for `wood_panel_large` and `dark_panel_base`. |
| `manifests/components.json` | Component-to-asset groupings for app shell, sidebar, header, kanban, agent grid, inspector, schedule timeline, and ambient layer. |

Note: the old dashboard mock-data manifest was removed on 2026-06-16. Runtime state now comes from `/api/status`; empty lanes use styled empty states instead of seeded fixture cards.

## Animation Strips

| Strip | Frames | FPS | Frame size | Usage |
|---|---:|---:|---|---|
| `animations/agents/agent_typing_strip.png` | 6 | 6 | `178x189` | Six vertical role typing scenes. |
| `animations/agents/agent_idle_blink_strip.png` | 6 | 3 | `170x189` | Six role idle/blink references. |
| `animations/ambient/lamp_fire_flicker_strip.png` | 4 | 8 | `90x120` | Ambient lantern/fire flicker. |
| `animations/status/progress_status_modules.png` | 5 | 8 | `215x53` | Progress/status modules. |

## Empty, Loading, And Error Needs

The current pipeline covers the main dashboard, cards, status bubbles, panels, ambient props, and agent scene. Dedicated state assets still need to be added before the dashboard can avoid text-only fallbacks:

- Empty queue or empty kanban board illustration.
- Loading spinner or clockwork/progress loop that matches the pixel-art style.
- Error or blocked-state panel treatment for failed API/status loads.
- Offline/autonomy-disabled state icon for worker controls.
- Missing avatar/station placeholder for unknown agent roles.
- Skeleton versions of task cards and inspector rows for initial load.

Add these as generated original source art first, then slice them through `scripts/dashboard_assets.py` so manifests remain the source of truth.

## Legal-Safe Naming

- Use descriptive project-owned names such as `task_card_default`, `agent_typing_strip`, `schedule_timeline_frame`, or `offline_worker_icon`.
- Keep `legal_safe_name` equal to the manifest asset `name` unless there is a documented reason to alias it.
- Mark generated original project art as `generated_original_project_art` in manifest metadata.
- Do not use official RuneScape/Jagex names, logos, sprites, screenshots, UI captures, item names as asset identifiers, or copied trade dress.
- Prefer functional terms: `RSPS`, `studio`, `agent`, `worker`, `build`, `queue`, `security`, `docs`, `backend`, `content`, and `qa`.
- Keep source sheets or generation notes so future revisions can prove project ownership and reproduce the style.
