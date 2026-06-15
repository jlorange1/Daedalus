from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from rsps_crewai_team.crew import RspsCrew
from rsps_crewai_team.runtime.ponytail import ponytail_policy
from rsps_crewai_team.tools.repo_tools import summarize_rsps_repo


def run() -> None:
    parser = argparse.ArgumentParser(description="Run the RSPS CrewAI workforce.")
    parser.add_argument("request", nargs="+", help="RSPS development request for the agent team.")
    args = parser.parse_args()

    env_file = Path.cwd() / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    else:
        load_dotenv()

    if not os.getenv("OPENROUTER_API_KEY"):
        raise SystemExit("OPENROUTER_API_KEY is not set. Copy .env.example to .env and add your key.")

    request = " ".join(args.request)
    repo_context = summarize_rsps_repo.run()
    result = RspsCrew().crew().kickoff(
        inputs={
            "request": request,
            "repo_context": repo_context,
            "ponytail_policy": ponytail_policy(),
        }
    )
    print(result)


if __name__ == "__main__":
    run()
