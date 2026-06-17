from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

from rsps_crewai_team.runtime.settings import PROJECT_ROOT, WORK_ORDERS_DIR, bool_env
from rsps_crewai_team.runtime.work_orders import STATUS_DIRS, create_work_order, ensure_work_order_dirs


STATIC_DIR = Path(__file__).resolve().parent / "dashboard_static"


def _read_env_file() -> dict[str, str]:
    path = PROJECT_ROOT / ".env"
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def _run(args: list[str], cwd: Path | None = None, timeout: int = 5) -> dict[str, str | int]:
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except Exception as exc:
        return {"exit_code": 1, "output": str(exc)}
    output = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
    return {"exit_code": result.returncode, "output": output[-4000:]}


def _git_summary(repo: Path) -> dict[str, str | bool]:
    if not repo.exists():
        return {"available": False, "branch": "missing", "clean": False, "detail": str(repo)}
    branch = _run(["git", "branch", "--show-current"], repo)
    status = _run(["git", "status", "--short"], repo)
    env = _read_env_file()
    remote_name = env.get("RSPS_GIT_REMOTE", "origin") or "origin"
    remote = _run(["git", "remote", "get-url", remote_name], repo)
    return {
        "available": True,
        "branch": str(branch["output"] or "unknown"),
        "clean": not bool(status["output"]),
        "detail": str(status["output"] or "clean"),
        "remote_name": remote_name,
        "remote": str(remote["output"] or "none"),
    }


def _work_order_title(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except OSError:
        pass
    return path.stem


def _queue() -> dict[str, object]:
    ensure_work_order_dirs()
    data: dict[str, object] = {}
    for status in STATUS_DIRS:
        files = sorted((WORK_ORDERS_DIR / status).glob("*.md"))
        data[status] = {
            "count": len(files),
            "items": [
                {
                    "title": _work_order_title(path),
                    "file": path.name,
                    "updated": int(path.stat().st_mtime),
                }
                for path in files[-8:]
            ],
        }
    return data


def _recent_logs() -> list[dict[str, str]]:
    logs_dir = PROJECT_ROOT / "logs"
    if not logs_dir.exists():
        return []
    files = sorted((path for path in logs_dir.glob("*") if path.is_file()), key=lambda item: item.stat().st_mtime)
    entries: list[dict[str, str]] = []
    for path in files[-6:]:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")[-900:]
        except OSError:
            text = ""
        entries.append({"name": path.name, "tail": text.strip()})
    return entries


def _agents(queue: dict[str, object]) -> list[dict[str, object]]:
    running = int(queue["running"]["count"])  # type: ignore[index]
    inbox = int(queue["inbox"]["count"])  # type: ignore[index]
    roles = [
        ("Producer", "Command Core", "OPENROUTER_PRODUCER_MODEL"),
        ("Backend Developer", "Server Core", "OPENROUTER_BACKEND_DEVELOPER_MODEL"),
        ("Content Developer", "Content Core", "OPENROUTER_CONTENT_DEVELOPER_MODEL"),
        ("QA Tester", "QA Core", "OPENROUTER_QA_TESTER_MODEL"),
        ("Security Reviewer", "Security Core", "OPENROUTER_SECURITY_REVIEWER_MODEL"),
        ("Documentation Writer", "Docs Core", "OPENROUTER_DOCUMENTATION_WRITER_MODEL"),
    ]
    env = _read_env_file()
    running_items = list(queue["running"]["items"])  # type: ignore[index]
    inbox_items = list(queue["inbox"]["items"])  # type: ignore[index]
    live_items = running_items + inbox_items
    agents = []
    for index, (role, name, model_key) in enumerate(roles):
        active = running > 0 or (inbox > 0 and index in {0, 1, 2})
        assigned = live_items[index % len(live_items)] if active and live_items else None
        task = str(assigned["title"]) if assigned else "No live work assigned"
        agents.append(
            {
                "role": role,
                "name": name,
                "task": task,
                "model": env.get(model_key, "not configured").replace("openrouter/", ""),
                "status": "working" if active else "ready",
                "progress": min(95, 28 + (running * 24) + (index * 7)) if active else 100,
            }
        )
    return agents


def _status() -> dict[str, object]:
    load_dotenv(PROJECT_ROOT / ".env")
    env = _read_env_file()
    repo_path = Path(env.get("RSPS_REPO_PATH", "")).expanduser() if env.get("RSPS_REPO_PATH") else None
    queue = _queue()
    return {
        "project": {
            "name": "Daedalus RSPS Studio",
            "root": str(PROJECT_ROOT),
            "rsps_repo": str(repo_path) if repo_path else "not configured",
            "source": "2009scape",
        },
        "env": {
            "autonomy": bool_env("RSPS_ALLOW_AUTONOMOUS", False),
            "duo_mode": bool_env("RSPS_DUO_MODE", True),
            "push_after_work": bool_env("RSPS_GIT_PUSH_AFTER_WORK", False),
            "ponytail": env.get("PONYTAIL_DEFAULT_MODE", "full"),
            "coding_cli": env.get("RSPS_CODING_CLI", "openclaw"),
            "build_command": env.get("RSPS_BUILD_COMMAND", ""),
            "test_command": env.get("RSPS_TEST_COMMAND", ""),
        },
        "readiness": {
            "java": bool(shutil.which("java")),
            "git_lfs": _run(["git", "lfs", "version"])["exit_code"] == 0,
            "openclaw": Path(env.get("RSPS_OPENCLAW_BIN", "")).exists(),
            "rsps_repo": bool(repo_path and repo_path.exists()),
        },
        "queue": queue,
        "agents": _agents(queue),
        "git": {
            "daedalus": _git_summary(PROJECT_ROOT),
            "rsps": _git_summary(repo_path) if repo_path else {"available": False, "branch": "none", "clean": False},
        },
        "logs": _recent_logs(),
    }


def _json_response(handler: SimpleHTTPRequestHandler, status: int, payload: dict[str, object]) -> None:
    encoded = json.dumps(payload, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(encoded)))
    handler.end_headers()
    handler.wfile.write(encoded)


def _spawn_action(action: str) -> dict[str, object]:
    allowed = {
        "run-duo": ["-m", "rsps_crewai_team.worker", "run-duo"],
        "run-once": ["-m", "rsps_crewai_team.worker", "run-once"],
        "cron-tick": ["-m", "rsps_crewai_team.cron", "tick"],
        "render-cron": ["-m", "rsps_crewai_team.cron", "render"],
    }
    if action not in allowed:
        return {"ok": False, "error": "unknown action"}
    log_path = PROJECT_ROOT / "logs" / "dashboard-actions.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log_file:
        process = subprocess.Popen(
            [sys.executable, *allowed[action]],
            cwd=PROJECT_ROOT,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    return {"ok": True, "pid": process.pid, "log": str(log_path)}


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self) -> None:  # noqa: N802
        if urlparse(self.path).path == "/api/status":
            _json_response(self, 200, _status())
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            _json_response(self, 400, {"ok": False, "error": "invalid json"})
            return

        if path == "/api/enqueue":
            title = str(payload.get("title", "")).strip()
            body = str(payload.get("body", "")).strip()
            if not title or not body:
                _json_response(self, 400, {"ok": False, "error": "title and body are required"})
                return
            created = create_work_order(title, body)
            _json_response(self, 201, {"ok": True, "path": str(created)})
            return

        if path == "/api/action":
            result = _spawn_action(str(payload.get("action", "")))
            _json_response(self, 200 if result.get("ok") else 400, result)
            return

        _json_response(self, 404, {"ok": False, "error": "not found"})


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Daedalus RSPS Studio dashboard.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    load_dotenv(PROJECT_ROOT / ".env")
    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    print(f"Daedalus dashboard: http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
