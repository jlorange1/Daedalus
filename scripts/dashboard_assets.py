#!/usr/bin/env python3
"""Slice and validate dashboard pixel-art assets."""

from __future__ import annotations

import json
import struct
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Pillow is required for slicing dashboard assets") from exc


ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "rsps_crewai_team" / "dashboard_static"
ASSETS = STATIC / "assets"
SOURCES = ASSETS / "source_sheets"
MANIFESTS = ASSETS / "manifests"


SOURCE_INPUTS = {
    "ui_kit_overview": ROOT.parent / "images" / "dashboard-generated-assets" / "ChatGPT Image Jun 15, 2026, 04_14_09 PM (1).png",
    "frame_kit": ROOT.parent / "images" / "dashboard-generated-assets" / "ChatGPT Image Jun 15, 2026, 04_14_09 PM (2).png",
    "ui_icons_atlas": ROOT.parent / "images" / "dashboard-generated-assets" / "ChatGPT Image Jun 15, 2026, 04_14_09 PM (3).png",
    "board_atlas": ROOT.parent / "images" / "dashboard-generated-assets" / "ChatGPT Image Jun 15, 2026, 04_14_09 PM (4).png",
    "environment_kit": ROOT.parent / "images" / "dashboard-generated-assets" / "ChatGPT Image Jun 15, 2026, 04_14_10 PM (5).png",
    "workstation_atlas": ROOT.parent / "images" / "dashboard-generated-assets" / "ChatGPT Image Jun 15, 2026, 04_14_10 PM (6).png",
    "agent_animation_sheet": ROOT.parent / "images" / "dashboard-generated-assets" / "ChatGPT Image Jun 15, 2026, 04_14_10 PM (7).png",
    "portrait_status_sheet": ROOT.parent / "images" / "dashboard-generated-assets" / "ChatGPT Image Jun 15, 2026, 04_14_11 PM (8).png",
    "ambient_props_sheet": ROOT.parent / "images" / "dashboard-generated-assets" / "ChatGPT Image Jun 15, 2026, 04_14_11 PM (9).png",
    "timeline_widgets_sheet": ROOT.parent / "images" / "dashboard-generated-assets" / "ChatGPT Image Jun 15, 2026, 04_14_11 PM (10).png",
    "prototype_scene": ROOT.parent / "images" / "dashboard-generated-assets" / "ig_021f83eca13fe854016a3058e325c88195be7bd8e2be7e4213.png",
}


SLICES = [
    ("task_card_default", "board_atlas", "sliced/cards/task_card_default.png", (485, 480, 730, 612), "card", "Default parchment task card"),
    ("task_card_review", "board_atlas", "sliced/cards/task_card_review.png", (745, 480, 990, 612), "card", "Review-state parchment task card"),
    ("task_card_done", "board_atlas", "sliced/cards/task_card_done.png", (1000, 480, 1240, 612), "card", "Done-state parchment task card"),
    ("wood_panel_large", "frame_kit", "sliced/panels/wood_panel_large.png", (930, 42, 1215, 220), "panel", "Resizable wood panel base"),
    ("dark_panel_base", "frame_kit", "sliced/panels/dark_panel_base.png", (15, 255, 580, 385), "panel", "Dark inset panel base"),
    ("green_banner_large", "ui_kit_overview", "sliced/ui/green_banner_large.png", (868, 230, 1136, 365), "ui", "Large green cloth banner"),
    ("button_primary_default", "ui_kit_overview", "sliced/ui/button_primary_default.png", (789, 485, 965, 602), "ui", "Primary wood action button"),
    ("button_wood_default", "ui_icons_atlas", "sliced/ui/button_wood_default.png", (10, 318, 194, 374), "ui", "Blank wood command button default state"),
    ("button_wood_hover", "ui_icons_atlas", "sliced/ui/button_wood_hover.png", (10, 392, 194, 448), "ui", "Blank wood command button hover state"),
    ("button_wood_pressed", "ui_icons_atlas", "sliced/ui/button_wood_pressed.png", (10, 466, 194, 522), "ui", "Blank wood command button pressed state"),
    ("button_wood_disabled", "ui_icons_atlas", "sliced/ui/button_wood_disabled.png", (10, 542, 194, 598), "ui", "Blank wood command button disabled state"),
    ("mounted_board_column", "board_atlas", "sliced/panels/mounted_board_column.png", (12, 95, 150, 355), "panel", "Mounted board column module"),
    ("mounted_board_column_alt", "board_atlas", "sliced/panels/mounted_board_column_alt.png", (160, 95, 295, 355), "panel", "Alternate mounted board column module"),
    ("mounted_board_background", "board_atlas", "sliced/panels/mounted_board_background.png", (10, 405, 285, 520), "panel", "Mounted kanban board background"),
    ("task_card_clean_default", "board_atlas", "sliced/cards/task_card_clean_default.png", (606, 96, 752, 198), "card", "Clean small parchment task card"),
    ("task_card_clean_review", "board_atlas", "sliced/cards/task_card_clean_review.png", (604, 230, 750, 338), "card", "Clean review parchment task card"),
    ("task_card_clean_done", "board_atlas", "sliced/cards/task_card_clean_done.png", (930, 230, 1076, 338), "card", "Clean done parchment task card"),
    ("sidebar_crest", "environment_kit", "sliced/ui/sidebar_crest.png", (902, 735, 982, 820), "ui", "Guild crest for sidebar banner"),
    ("inspector_cabinet_panel", "frame_kit", "sliced/panels/inspector_cabinet_panel.png", (520, 1088, 617, 1218), "panel", "Tall inspector cabinet panel"),
    ("inspector_portrait_frame", "portrait_status_sheet", "sliced/panels/inspector_portrait_frame.png", (560, 705, 752, 862), "panel", "Portrait frame for agent inspector"),
    ("schedule_frame_full", "timeline_widgets_sheet", "sliced/widgets/schedule_frame_full.png", (265, 132, 1218, 495), "widget", "Full schedule frame and bar system"),
    ("next_events_panel", "timeline_widgets_sheet", "sliced/widgets/next_events_panel.png", (260, 505, 490, 725), "widget", "Next events widget panel"),
    ("status_bar_green", "ui_kit_overview", "sliced/status/status_bar_green.png", (995, 520, 1220, 595), "status", "Green status meter"),
    ("bubble_code", "portrait_status_sheet", "sliced/widgets/bubble_code.png", (16, 795, 92, 860), "widget", "Code speech bubble"),
    ("bubble_bug", "portrait_status_sheet", "sliced/widgets/bubble_bug.png", (100, 795, 176, 860), "widget", "Bug speech bubble"),
    ("bubble_docs", "portrait_status_sheet", "sliced/widgets/bubble_docs.png", (184, 795, 260, 860), "widget", "Docs speech bubble"),
    ("bubble_shield", "portrait_status_sheet", "sliced/widgets/bubble_shield.png", (268, 795, 344, 860), "widget", "Security speech bubble"),
    ("lantern", "ambient_props_sheet", "sliced/ambient/lantern.png", (14, 662, 92, 805), "ambient", "Hanging lantern prop"),
    ("server_lights", "ambient_props_sheet", "sliced/ambient/server_lights.png", (825, 690, 1000, 805), "ambient", "Server rack light prop"),
    ("day_cycle_panel", "timeline_widgets_sheet", "sliced/widgets/day_cycle_panel.png", (18, 36, 320, 340), "widget", "Day cycle panel base"),
    ("schedule_timeline_frame", "timeline_widgets_sheet", "sliced/widgets/schedule_timeline_frame.png", (335, 405, 1210, 610), "widget", "Schedule timeline frame"),
    ("prototype_studio_floor_full", "prototype_scene", "sliced/agents/prototype_studio_floor_full.png", (210, 396, 1112, 792), "agent_scene", "Full composed studio floor with six agent desks"),
]


ANIMATION_SLICES = [
    ("agent_typing_strip", "agent_animation_sheet", "animations/agents/agent_typing_strip.png", (648, 78, 826, 1212), 178, 189, 6, 6, True, "Six vertical role typing scenes"),
    ("agent_idle_blink_strip", "agent_animation_sheet", "animations/agents/agent_idle_blink_strip.png", (480, 78, 650, 1212), 170, 189, 6, 3, True, "Six role idle/blink references"),
    ("lamp_fire_flicker_strip", "ambient_props_sheet", "animations/ambient/lamp_fire_flicker_strip.png", (0, 0, 360, 120), 90, 120, 4, 8, True, "Ambient lantern/fire flicker references"),
    ("progress_status_modules", "timeline_widgets_sheet", "animations/status/progress_status_modules.png", (1020, 860, 1235, 1125), 215, 53, 5, 8, True, "Progress/status module strip"),
]


NINE_SLICES = [
    {
        "name": "wood_panel_large",
        "file": "/assets/sliced/panels/wood_panel_large.png",
        "type": "nine_slice",
        "left": 18,
        "right": 18,
        "top": 18,
        "bottom": 18,
        "repeat_center": True,
        "usage": "Resizable warm wood panel frame",
    },
    {
        "name": "dark_panel_base",
        "file": "/assets/sliced/panels/dark_panel_base.png",
        "type": "nine_slice",
        "left": 16,
        "right": 16,
        "top": 16,
        "bottom": 16,
        "repeat_center": True,
        "usage": "Dark stone/wood inset panel",
    },
]


def copy_sources() -> dict[str, Path]:
    SOURCES.mkdir(parents=True, exist_ok=True)
    copied = {}
    for name, source in SOURCE_INPUTS.items():
        if not source.exists():
            continue
        target = SOURCES / f"{name}.png"
        if target.resolve() != source.resolve():
            target.write_bytes(source.read_bytes())
        copied[name] = target
    return copied


def slice_image(source: Path, target: Path, box: tuple[int, int, int, int]) -> tuple[int, int]:
    target.parent.mkdir(parents=True, exist_ok=True)
    image = Image.open(source).convert("RGBA")
    crop = image.crop(box)
    crop.save(target)
    return crop.size


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not a PNG: {path}")
    return struct.unpack(">II", header[16:24])


def build() -> None:
    sources = copy_sources()
    MANIFESTS.mkdir(parents=True, exist_ok=True)

    assets = []
    for name, source_key, rel, box, kind, usage in SLICES:
        if source_key not in sources:
            continue
        target = ASSETS / rel
        width, height = slice_image(sources[source_key], target, box)
        assets.append(
            {
                "name": name,
                "file": f"/assets/{rel}",
                "type": kind,
                "usage": usage,
                "source": f"/assets/source_sheets/{source_key}.png",
                "legal_safe_name": name,
                "license_status": "generated_original_project_art",
                "recommended_size": {"width": width, "height": height},
            }
        )

    animations = []
    for name, source_key, rel, box, frame_width, frame_height, frames, fps, loop, usage in ANIMATION_SLICES:
        if source_key not in sources:
            continue
        target = ASSETS / rel
        width, height = slice_image(sources[source_key], target, box)
        animations.append(
            {
                "name": name,
                "file": f"/assets/{rel}",
                "frame_width": frame_width,
                "frame_height": frame_height,
                "frames": frames,
                "fps": fps,
                "loop": loop,
                "anchor": "bottom_center",
                "usage": usage,
                "sheet_size": {"width": width, "height": height},
            }
        )

    components = {
        "app_shell": ["wood_panel_large", "dark_panel_base"],
        "left_sidebar": ["green_banner_large", "sidebar_crest", "status_bar_green"],
        "top_sprint_header": ["green_banner_large", "button_wood_default", "button_wood_hover", "button_wood_pressed"],
        "kanban_board": ["mounted_board_background", "mounted_board_column", "task_card_clean_default", "task_card_clean_review", "task_card_clean_done"],
        "agent_grid": ["prototype_studio_floor_full", "agent_typing_strip", "agent_idle_blink_strip"],
        "agent_inspector": ["inspector_cabinet_panel", "inspector_portrait_frame", "status_bar_green"],
        "schedule_timeline": ["day_cycle_panel", "schedule_frame_full", "next_events_panel", "progress_status_modules"],
        "ambient_layer": ["lantern", "server_lights", "lamp_fire_flicker_strip"],
    }

    (MANIFESTS / "assets.json").write_text(json.dumps(assets, indent=2) + "\n")
    (MANIFESTS / "animations.json").write_text(json.dumps(animations, indent=2) + "\n")
    (MANIFESTS / "nine_slice.json").write_text(json.dumps(NINE_SLICES, indent=2) + "\n")
    (MANIFESTS / "components.json").write_text(json.dumps(components, indent=2) + "\n")


def validate() -> None:
    errors = []
    for manifest in ("assets.json", "animations.json", "nine_slice.json"):
        path = MANIFESTS / manifest
        if not path.exists():
            errors.append(f"missing manifest {path}")
            continue
        data = json.loads(path.read_text())
        for item in data:
            file_value = item.get("file")
            if not file_value:
                continue
            asset_path = STATIC / file_value.lstrip("/")
            if not asset_path.exists():
                errors.append(f"missing asset {asset_path}")
                continue
            try:
                png_size(asset_path)
            except Exception as exc:  # noqa: BLE001
                errors.append(str(exc))
    if errors:
        raise SystemExit("\n".join(errors))
    print("dashboard assets validated")


if __name__ == "__main__":
    build()
    validate()
