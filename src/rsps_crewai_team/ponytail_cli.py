from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from rsps_crewai_team.runtime.ponytail import ponytail_mode, ponytail_policy
from rsps_crewai_team.runtime.settings import PROJECT_ROOT


def status(_: argparse.Namespace) -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    print(f"mode={ponytail_mode()}")
    print(ponytail_policy())


def set_mode(args: argparse.Namespace) -> None:
    env_path = PROJECT_ROOT / ".env"
    lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    updated = False
    for index, line in enumerate(lines):
        if line.startswith("PONYTAIL_DEFAULT_MODE="):
            lines[index] = f"PONYTAIL_DEFAULT_MODE={args.mode}"
            updated = True
            break
    if not updated:
        lines.append(f"PONYTAIL_DEFAULT_MODE={args.mode}")
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"PONYTAIL_DEFAULT_MODE={args.mode}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect or change Ponytail mode.")
    subparsers = parser.add_subparsers(required=True)

    status_parser = subparsers.add_parser("status", help="Show active Ponytail policy.")
    status_parser.set_defaults(func=status)

    set_parser = subparsers.add_parser("set", help="Set Ponytail mode in .env.")
    set_parser.add_argument("mode", choices=["off", "lite", "full", "ultra"])
    set_parser.set_defaults(func=set_mode)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
