from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from rsps_crewai_team.runtime.settings import PROJECT_ROOT

CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"
INSPIRATION_SOURCES_PATH = CONFIG_DIR / "inspiration_sources.json"
SPEC_CONTRACTS_PATH = CONFIG_DIR / "spec_contracts.json"
PROMPT_PATTERNS_PATH = CONFIG_DIR / "prompt_patterns.json"
SKILL_CATALOG_PATH = CONFIG_DIR / "skill_catalog.json"
PROFITABILITY_MODEL_PATH = CONFIG_DIR / "profitability_model.json"
AGENCY_WORKFLOWS_PATH = CONFIG_DIR / "agency_workflows.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_inspiration_sources() -> dict[str, Any]:
    return _load_json(INSPIRATION_SOURCES_PATH)


def load_spec_contracts() -> dict[str, Any]:
    return _load_json(SPEC_CONTRACTS_PATH)


def load_prompt_patterns() -> dict[str, Any]:
    return _load_json(PROMPT_PATTERNS_PATH)


def load_skill_catalog() -> dict[str, Any]:
    return _load_json(SKILL_CATALOG_PATH)


def load_profitability_model() -> dict[str, Any]:
    return _load_json(PROFITABILITY_MODEL_PATH)


def profitability_metrics_path(model: dict[str, Any] | None = None) -> Path:
    data = model if model is not None else load_profitability_model()
    engine = data.get("engine", {})
    env_name = str(engine.get("metrics_path_env", "RSPS_PROFITABILITY_METRICS_PATH"))
    configured = os.getenv(env_name, "").strip()
    raw = configured or str(engine.get("default_metrics_path", "data/profitability_metrics.json"))
    path = Path(raw).expanduser()
    return path if path.is_absolute() else PROJECT_ROOT / path


def load_profitability_metrics(model: dict[str, Any] | None = None) -> tuple[dict[str, float] | None, str, str | None]:
    path = profitability_metrics_path(model)
    if not path.exists():
        return None, str(path), "metrics file is missing"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, str(path), f"metrics file is invalid JSON: line {exc.lineno}"
    source = raw.get("metrics", raw) if isinstance(raw, dict) else {}
    if not isinstance(source, dict):
        return None, str(path), "metrics file must contain an object or a metrics object"
    metrics: dict[str, float] = {}
    for key, value in source.items():
        try:
            metrics[str(key)] = float(value)
        except (TypeError, ValueError):
            return None, str(path), f"metric {key} is not numeric"
    return metrics, str(path), None


def profitability_scenarios(model: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    data = model if model is not None else load_profitability_model()
    metrics, _, error = load_profitability_metrics(data)
    if error or metrics is None:
        return []
    required = ["monthly_active_players", "payer_conversion", "arppu", "hosting_cost", "tooling_cost", "asset_budget"]
    missing = [item for item in required if item not in metrics]
    if missing:
        return []

    fixed_cost = metrics["hosting_cost"] + metrics["tooling_cost"] + metrics["asset_budget"]
    rows: list[dict[str, Any]] = []
    for scenario in data.get("scenarios", []):
        players = metrics["monthly_active_players"] * float(scenario.get("active_players_multiplier", 1))
        conversion = metrics["payer_conversion"] * float(scenario.get("conversion_multiplier", 1)) / 100
        arppu = metrics["arppu"] * float(scenario.get("arppu_multiplier", 1))
        costs = fixed_cost * float(scenario.get("cost_multiplier", 1))
        paying_users = players * conversion
        revenue = paying_users * arppu
        net = revenue - costs
        rows.append(
            {
                "id": scenario["id"],
                "players": round(players),
                "paying_users": round(paying_users, 1),
                "revenue": round(revenue, 2),
                "costs": round(costs, 2),
                "net": round(net, 2),
                "margin_percent": round((net / revenue * 100), 1) if revenue else 0,
            }
        )
    return rows


def validate_intelligence_configs(root: Path | None = None) -> dict[str, Any]:
    repo_root = root or CONFIG_DIR.parents[2]
    sources = load_inspiration_sources()
    specs = load_spec_contracts()
    prompts = load_prompt_patterns()
    skills = load_skill_catalog()
    profit = load_profitability_model()
    workflows = _load_json(AGENCY_WORKFLOWS_PATH)

    source_ids = [str(item["id"]) for item in sources.get("sources", [])]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("inspiration source IDs must be unique")
    if len(source_ids) < 9:
        raise ValueError("expected at least 9 inspiration sources")

    lifecycle = specs.get("lifecycle", [])
    if "draft" not in lifecycle or "validated" not in lifecycle:
        raise ValueError("spec lifecycle must include draft and validated")
    for artifact in specs.get("artifact_types", []):
        if not artifact.get("required_fields"):
            raise ValueError(f"artifact {artifact.get('id')} has no required_fields")
    workflow_ids = {str(item["id"]) for item in workflows.get("workflows", [])}
    unknown_workflows = sorted(set(specs.get("workflow_links", [])) - workflow_ids)
    if unknown_workflows:
        raise ValueError("spec contracts reference unknown workflows: " + ", ".join(unknown_workflows))

    prompt_ids = [str(item["id"]) for item in prompts.get("patterns", [])]
    if len(prompt_ids) != len(set(prompt_ids)):
        raise ValueError("prompt pattern IDs must be unique")
    for pattern in prompts.get("patterns", []):
        if not pattern.get("required_context") or not pattern.get("forbidden_content"):
            raise ValueError(f"prompt pattern {pattern.get('id')} is missing guardrails")

    cataloged = []
    for skill in skills.get("skills", []):
        path = repo_root / str(skill["path"])
        cataloged.append(path)
        if not path.exists():
            raise ValueError(f"skill path missing: {skill['path']}")
        if skill.get("status") not in {"active", "draft", "deprecated"}:
            raise ValueError(f"skill {skill.get('name')} has invalid status")

    scenario_defs = profit.get("scenarios", [])
    if len(scenario_defs) < 3:
        raise ValueError("profitability model requires at least 3 scenario definitions")
    required_metrics = [metric for metric in profit.get("metrics", []) if metric.get("required")]
    if not required_metrics:
        raise ValueError("profitability model requires live metric definitions")
    if any(stream.get("risk") not in {"low", "medium", "high"} for stream in profit.get("revenue_streams", [])):
        raise ValueError("profitability revenue streams must have low/medium/high risk")

    return {
        "source_count": len(source_ids),
        "artifact_type_count": len(specs.get("artifact_types", [])),
        "prompt_pattern_count": len(prompt_ids),
        "skill_count": len(cataloged),
        "profitability_scenarios": profitability_scenarios(profit),
    }


def intelligence_status() -> dict[str, Any]:
    sources = load_inspiration_sources()
    specs = load_spec_contracts()
    prompts = load_prompt_patterns()
    skills = load_skill_catalog()
    profit = load_profitability_model()
    validation = validate_intelligence_configs()
    metrics, metrics_path, metrics_error = load_profitability_metrics(profit)
    required_metrics = [str(metric["id"]) for metric in profit.get("metrics", []) if metric.get("required")]
    missing_metrics = sorted(set(required_metrics) - set(metrics or {}))
    scenarios = validation["profitability_scenarios"] if not missing_metrics else []
    return {
        "source_count": validation["source_count"],
        "sources": sources.get("sources", []),
        "specs": {
            "principles": specs.get("principles", []),
            "artifact_type_count": validation["artifact_type_count"],
            "lifecycle": specs.get("lifecycle", []),
            "approval_gates": specs.get("approval_gates", []),
        },
        "prompts": {
            "pattern_count": validation["prompt_pattern_count"],
            "patterns": prompts.get("patterns", []),
        },
        "skills": {
            "skill_count": validation["skill_count"],
            "skills": skills.get("skills", []),
        },
        "profitability": {
            "engine": profit.get("engine", {}),
            "status": "live" if scenarios else "unavailable",
            "metrics_path": metrics_path,
            "missing_reason": metrics_error or ("missing required metrics: " + ", ".join(missing_metrics) if missing_metrics else ""),
            "ethics_policy": profit.get("ethics_policy", []),
            "revenue_streams": profit.get("revenue_streams", []),
            "scenarios": scenarios,
            "release_gates": profit.get("release_gates", []),
        },
    }
