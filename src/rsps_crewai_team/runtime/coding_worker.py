from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path

from rsps_crewai_team.runtime.settings import LOGS_DIR, require_autonomy_enabled, rsps_repo_path


@dataclass(frozen=True)
class WorkerResult:
    command: list[str]
    exit_code: int
    log_path: Path


def _shared_env() -> dict[str, str]:
    env = os.environ.copy()
    key = os.getenv("OPENROUTER_API_KEY", "")
    if key:
        env["OPENROUTER_API_KEY"] = key
        env["OPENAI_API_KEY"] = key
    env["OPENROUTER_BASE_URL"] = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    return env


def _openclaw_model_override(model: str) -> str:
    normalized = model.strip()
    if normalized.lower() == "openrouter/free":
        return "free"
    if normalized.lower().startswith("openrouter/openrouter/"):
        return normalized[len("openrouter/") :]
    return normalized


def _openclaw_command(message_file: Path, agent_id: str) -> list[str]:
    message = message_file.read_text(encoding="utf-8")
    model_env = f"RSPS_OPENCLAW_{agent_id.upper().replace('-', '_')}_MODEL"
    model = _openclaw_model_override(
        os.getenv(model_env, os.getenv("RSPS_CODING_MODEL", "openrouter/qwen/qwen3-coder:free"))
    )
    command = [
        os.getenv("RSPS_OPENCLAW_BIN", "/var/home/Scaar/.local/bin/openclaw"),
        "agent",
        "--local",
        "--agent",
        agent_id,
        "--session-key",
        f"agent:{agent_id}:{message_file.stem}",
        "--model",
        model,
        "--message",
        message,
        "--timeout",
        os.getenv("RSPS_OPENCLAW_TIMEOUT_SECONDS", os.getenv("RSPS_WORKER_TIMEOUT_SECONDS", "900")),
        "--json",
    ]
    return command


def _custom_command(message_file: Path) -> list[str]:
    template = os.getenv("OPENCLAW_CLI_CMD") or os.getenv("RSPS_CODING_CLI_CMD")
    if not template:
        raise RuntimeError("RSPS_CODING_CLI=custom requires OPENCLAW_CLI_CMD or RSPS_CODING_CLI_CMD.")
    repo = rsps_repo_path()
    replacements = {
        "message_file": str(message_file),
        "repo": str(repo),
        "model": os.getenv("RSPS_CODING_MODEL", "openrouter/qwen/qwen3-coder:free"),
        "base_url": os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    }
    return shlex.split(template.format(**replacements))


def build_worker_command(message_file: Path, agent_id: str = "rsps-builder") -> list[str]:
    cli = os.getenv("RSPS_CODING_CLI", "openclaw").strip().lower()
    if cli == "openclaw":
        return _openclaw_command(message_file, agent_id)
    if cli == "custom":
        return _custom_command(message_file)
    raise RuntimeError(f"Unsupported RSPS_CODING_CLI: {cli}")


def run_coding_worker(message: str, label: str, agent_id: str = "rsps-builder", cwd: Path | None = None) -> WorkerResult:
    require_autonomy_enabled()
    repo = cwd or rsps_repo_path()
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    message_file = LOGS_DIR / f"{label}.prompt.md"
    log_path = LOGS_DIR / f"{label}.worker.log"
    message_file.write_text(message, encoding="utf-8")
    command = build_worker_command(message_file, agent_id)
    with log_path.open("w", encoding="utf-8") as log:
        log.write("$ " + " ".join(shlex.quote(part) for part in command) + "\n\n")
        result = subprocess.run(
            command,
            cwd=repo,
            env=_shared_env(),
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            timeout=int(os.getenv("RSPS_WORKER_TIMEOUT_SECONDS", "900")),
        )
    return WorkerResult(command=command, exit_code=result.returncode, log_path=log_path)
