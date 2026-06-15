from __future__ import annotations

import os
import subprocess
from pathlib import Path

from crewai.tools import tool


MAX_LISTING_LINES = 250


def _repo_path() -> Path | None:
    raw_path = os.getenv("RSPS_REPO_PATH", "").strip()
    if not raw_path:
        return None
    path = Path(raw_path).expanduser().resolve()
    if not path.exists() or not path.is_dir():
        return None
    return path


@tool("Summarize RSPS repository")
def summarize_rsps_repo() -> str:
    """Summarize the configured RSPS repository layout and likely build system."""
    repo = _repo_path()
    if repo is None:
        return "RSPS_REPO_PATH is not configured or does not point to a directory."

    markers = [
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
        "settings.gradle",
        "settings.gradle.kts",
        "gradlew",
        "src",
        "data",
        "cache",
        "config",
    ]
    found = [marker for marker in markers if (repo / marker).exists()]
    lines = [f"Repository: {repo}", f"Detected markers: {', '.join(found) or 'none'}", ""]

    count = 0
    for path in sorted(repo.rglob("*")):
        if count >= MAX_LISTING_LINES:
            lines.append(f"...truncated after {MAX_LISTING_LINES} entries")
            break
        if any(part in {".git", "build", "target", ".gradle", "node_modules"} for part in path.parts):
            continue
        rel = path.relative_to(repo)
        suffix = "/" if path.is_dir() else ""
        lines.append(f"- {rel}{suffix}")
        count += 1
    return "\n".join(lines)


@tool("Run configured RSPS build command")
def run_rsps_build() -> str:
    """Run RSPS_BUILD_COMMAND in RSPS_REPO_PATH and return a bounded output summary."""
    return _run_configured_command("RSPS_BUILD_COMMAND")


@tool("Run configured RSPS test command")
def run_rsps_tests() -> str:
    """Run RSPS_TEST_COMMAND in RSPS_REPO_PATH and return a bounded output summary."""
    return _run_configured_command("RSPS_TEST_COMMAND")


def _run_configured_command(env_name: str) -> str:
    repo = _repo_path()
    if repo is None:
        return "RSPS_REPO_PATH is not configured or does not point to a directory."

    command = os.getenv(env_name, "").strip()
    if not command:
        return f"{env_name} is not configured."

    try:
        result = subprocess.run(
            command,
            cwd=repo,
            shell=True,
            text=True,
            capture_output=True,
            timeout=180,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return f"{env_name} timed out after 180 seconds: {command}"

    output = "\n".join(
        part
        for part in [
            f"Command: {command}",
            f"Exit code: {result.returncode}",
            "STDOUT:",
            result.stdout[-6000:],
            "STDERR:",
            result.stderr[-6000:],
        ]
        if part is not None
    )
    return output
