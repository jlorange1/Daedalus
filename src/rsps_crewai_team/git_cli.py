from __future__ import annotations

import argparse
import subprocess

from dotenv import load_dotenv

from rsps_crewai_team.runtime.git_sync import ensure_git_repo, git_remote_name, has_remote, remote_url
from rsps_crewai_team.runtime.settings import PROJECT_ROOT, rsps_repo_path


def _run(cmd: list[str], *, capture: bool = False, quiet: bool = False) -> int:
    result = subprocess.run(cmd, text=True, capture_output=capture, check=False)
    if capture and not quiet and result.stdout.strip():
        print(result.stdout.strip())
    if capture and not quiet and result.stderr.strip():
        print(result.stderr.strip())
    return result.returncode


def _remote_url(repository: str) -> str:
    return f"https://github.com/{repository.removesuffix('.git')}.git"


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
            remote = git_remote_name()
            print(f"configured_remote={remote}")
            print(f"configured_remote_exists={has_remote(repo)}")
            if has_remote(repo):
                print(f"configured_remote_url={remote_url(repo).output}")
        except Exception as exc:
            print(f"git_repo=false ({exc})")
    print("gh:")
    _run(["gh", "auth", "status"])


def init_repo(_: argparse.Namespace) -> None:
    repo = rsps_repo_path()
    if _run(["git", "-C", str(repo), "rev-parse", "--is-inside-work-tree"]) != 0:
        raise SystemExit(_run(["git", "-C", str(repo), "init"]))
    print("Repository already initialized: " + str(repo))


def _configure_remote(repo, remote: str, repository: str) -> int:
    url = _remote_url(repository)
    if _run(["git", "-C", str(repo), "remote", "get-url", remote], capture=True, quiet=True) == 0:
        return _run(["git", "-C", str(repo), "remote", "set-url", remote, url], capture=True)
    return _run(["git", "-C", str(repo), "remote", "add", remote, url], capture=True)


def configure_remote(args: argparse.Namespace) -> None:
    repo = rsps_repo_path()
    ensure_git_repo(repo)
    remote = args.remote or git_remote_name()
    raise SystemExit(_configure_remote(repo, remote, args.repository))


def publish(args: argparse.Namespace) -> None:
    repo = rsps_repo_path()
    ensure_git_repo(repo)
    remote = args.remote or git_remote_name()
    visibility = "--public" if args.public else "--private"
    if _run(["gh", "repo", "view", args.repository], capture=True) != 0:
        created = _run(["gh", "repo", "create", args.repository, visibility], capture=True)
        if created != 0:
            raise SystemExit(created)
    configured = _configure_remote(repo, remote, args.repository)
    if configured != 0:
        raise SystemExit(configured)
    branch = subprocess.run(
        ["git", "-C", str(repo), "branch", "--show-current"],
        text=True,
        capture_output=True,
        check=False,
    ).stdout.strip()
    if not branch:
        raise SystemExit("Could not determine current branch.")
    raise SystemExit(_run(["git", "-C", str(repo), "push", "-u", remote, branch], capture=True))


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    parser = argparse.ArgumentParser(description="RSPS GitHub/Git helper.")
    subparsers = parser.add_subparsers(required=True)

    status_parser = subparsers.add_parser("status", help="Show RSPS git and GitHub CLI readiness.")
    status_parser.set_defaults(func=status)

    init_parser = subparsers.add_parser("init", help="Initialize git in RSPS_REPO_PATH if needed.")
    init_parser.set_defaults(func=init_repo)

    remote_parser = subparsers.add_parser("configure-remote", help="Add or update the user-owned GitHub remote.")
    remote_parser.add_argument("repository", help="GitHub repository in owner/name form.")
    remote_parser.add_argument("--remote", default=None, help="Remote name. Defaults to RSPS_GIT_REMOTE or origin.")
    remote_parser.set_defaults(func=configure_remote)

    publish_parser = subparsers.add_parser("publish", help="Create the GitHub repo if needed and push the current branch.")
    publish_parser.add_argument("repository", help="GitHub repository in owner/name form.")
    publish_parser.add_argument("--remote", default=None, help="Remote name. Defaults to RSPS_GIT_REMOTE or origin.")
    publish_parser.add_argument("--public", action="store_true", help="Create the repo as public. Default is private.")
    publish_parser.set_defaults(func=publish)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
