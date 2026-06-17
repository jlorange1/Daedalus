from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from rsps_crewai_team.runtime.settings import bool_env, rsps_repo_path


@dataclass(frozen=True)
class GitResult:
    exit_code: int
    output: str


def _run_git(args: list[str], cwd: Path) -> GitResult:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    return GitResult(result.returncode, (result.stdout + result.stderr).strip())


def slugify_branch(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._/-]+", "-", text.strip().lower()).strip("-/")
    return slug[:80] or "work-order"


def ensure_git_repo(path: Path | None = None) -> None:
    repo = path or rsps_repo_path()
    result = _run_git(["rev-parse", "--is-inside-work-tree"], repo)
    if result.exit_code != 0:
        raise RuntimeError(f"RSPS_REPO_PATH is not a git repository: {repo}")


def has_remote(path: Path | None = None) -> bool:
    repo = path or rsps_repo_path()
    result = _run_git(["remote", "get-url", git_remote_name()], repo)
    return result.exit_code == 0 and bool(result.output)


def git_remote_name() -> str:
    return os.getenv("RSPS_GIT_REMOTE", "origin").strip() or "origin"


def remote_url(path: Path | None = None, remote: str | None = None) -> GitResult:
    repo = path or rsps_repo_path()
    return _run_git(["remote", "get-url", remote or git_remote_name()], repo)


def _is_protected_upstream(url: str) -> bool:
    normalized = url.lower().removesuffix(".git")
    return "gitlab.com/2009scape/2009scape" in normalized


def has_changes(path: Path | None = None) -> bool:
    repo = path or rsps_repo_path()
    result = _run_git(["status", "--porcelain"], repo)
    return bool(result.output)


def commit_all(message: str, path: Path | None = None) -> GitResult:
    repo = path or rsps_repo_path()
    _run_git(["add", "-A"], repo)
    return _run_git(["commit", "-m", message], repo)


def push_current_branch(path: Path | None = None) -> GitResult:
    repo = path or rsps_repo_path()
    branch = _run_git(["branch", "--show-current"], repo).output.strip()
    if not branch:
        return GitResult(1, "Could not determine current branch.")
    remote = git_remote_name()
    url = remote_url(repo, remote)
    if url.exit_code != 0:
        return GitResult(1, f"Remote {remote!r} is not configured.")
    if _is_protected_upstream(url.output):
        return GitResult(
            1,
            f"Refusing to push autonomous work to protected upstream remote {remote!r}: {url.output}",
        )
    return _run_git(["push", "-u", remote, branch], repo)


def sync_changes(message: str, path: Path | None = None) -> GitResult:
    repo = path or rsps_repo_path()
    ensure_git_repo(repo)
    if not has_changes(repo):
        return GitResult(0, "No changes to commit.")
    commit = commit_all(message, repo)
    if commit.exit_code != 0:
        return commit
    if bool_env("RSPS_GIT_PUSH_AFTER_WORK", False):
        if not has_remote(repo):
            return GitResult(1, f"Committed locally, but remote {git_remote_name()!r} is not configured.")
        return push_current_branch(repo)
    return GitResult(0, "Committed locally. Push disabled by RSPS_GIT_PUSH_AFTER_WORK=false.")


def create_agent_worktree(agent_id: str, label: str) -> Path:
    repo = rsps_repo_path()
    ensure_git_repo(repo)
    raw_root = os.getenv("RSPS_AGENT_WORKTREE_ROOT", "").strip()
    root = Path(raw_root or str(repo.parent / ".rsps-agent-worktrees")).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    branch = f"agent/{slugify_branch(agent_id)}/{slugify_branch(label)}"
    worktree = (root / slugify_branch(f"{agent_id}-{label}")).resolve()
    if worktree.exists():
        raise RuntimeError(f"Agent worktree already exists, refusing to delete it: {worktree}")
    result = _run_git(["worktree", "add", "-B", branch, str(worktree), "HEAD"], repo)
    if result.exit_code != 0:
        raise RuntimeError(result.output)
    return worktree


def remove_agent_worktree(path: Path) -> GitResult:
    repo = rsps_repo_path()
    return _run_git(["worktree", "remove", "--force", str(path)], repo)
