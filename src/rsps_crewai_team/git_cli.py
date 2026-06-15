from __future__ import annotations

import argparse
import subprocess

from dotenv import load_dotenv

from rsps_crewai_team.runtime.git_sync import ensure_git_repo, has_remote
from rsps_crewai_team.runtime.settings import PROJECT_ROOT, rsps_repo_path


def _run(cmd: list[str]) -> int:
    result = subprocess.run(cmd, text=True, check=False)
    return result.returncode


def status(_: argparse.Namespace) -> None:
    repo = None
    try:
        repo = rsps_repo_path()
    except Exception as exc:
        print(f"rsps_repo=not configured ({exc})")
    if repo is not None:
        print(f"rsps_repo={repo}")
        try:
            ensure_git_repo(repo)
            print("git_repo=true")
            print(f"origin_remote={has_remote(repo)}")
        except Exception as exc:
            print(f"git_repo=false ({exc})")
    print("gh:")
    _run(["gh", "auth", "status"])


def init_repo(_: argparse.Namespace) -> None:
    repo = rsps_repo_path()
    if _run(["git", "-C", str(repo), "rev-parse", "--is-inside-work-tree"]) != 0:
        raise SystemExit(_run(["git", "-C", str(repo), "init"]))
    print("Repository already initialized: " + str(repo))


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    parser = argparse.ArgumentParser(description="RSPS GitHub/Git helper.")
    subparsers = parser.add_subparsers(required=True)

    status_parser = subparsers.add_parser("status", help="Show RSPS git and GitHub CLI readiness.")
    status_parser.set_defaults(func=status)

    init_parser = subparsers.add_parser("init", help="Initialize git in RSPS_REPO_PATH if needed.")
    init_parser.set_defaults(func=init_repo)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
