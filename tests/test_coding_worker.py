from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rsps_crewai_team.runtime.coding_worker import build_worker_command
from rsps_crewai_team.runtime import coding_worker


class CodingWorkerCommandTests(unittest.TestCase):
    def test_openrouter_free_alias_is_passed_as_openclaw_model_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            message_file = Path(tmp) / "message.md"
            message_file.write_text("hello", encoding="utf-8")

            env = {
                "RSPS_CODING_CLI": "openclaw",
                "RSPS_CODING_MODEL": "openrouter/free",
                "RSPS_OPENCLAW_BIN": "/tmp/openclaw",
            }
            with patch.dict(os.environ, env, clear=True):
                command = build_worker_command(message_file, agent_id="rsps-builder")

        self.assertIn("--model", command)
        self.assertEqual(command[command.index("--model") + 1], "free")

    def test_concrete_openrouter_model_keeps_provider_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            message_file = Path(tmp) / "message.md"
            message_file.write_text("hello", encoding="utf-8")

            env = {
                "RSPS_CODING_CLI": "openclaw",
                "RSPS_CODING_MODEL": "openrouter/qwen/qwen3-coder:free",
                "RSPS_OPENCLAW_BIN": "/tmp/openclaw",
            }
            with patch.dict(os.environ, env, clear=True):
                command = build_worker_command(message_file, agent_id="rsps-builder")

        self.assertEqual(command[command.index("--model") + 1], "openrouter/qwen/qwen3-coder:free")

    def test_custom_command_uses_assigned_repo_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            message_file = Path(tmp) / "message.md"
            message_file.write_text("hello", encoding="utf-8")
            assigned_repo = Path(tmp) / "assigned-worktree"

            env = {
                "RSPS_CODING_CLI": "custom",
                "RSPS_CODING_CLI_CMD": "worker --repo {repo} --message {message_file}",
            }
            with patch.dict(os.environ, env, clear=True):
                command = build_worker_command(message_file, agent_id="rsps-builder", repo=assigned_repo)

        self.assertEqual(command[command.index("--repo") + 1], str(assigned_repo))

    def test_worker_environment_points_to_assigned_repo_path(self) -> None:
        assigned_repo = Path("/tmp/assigned-rsps-worktree")
        with patch.dict(os.environ, {"RSPS_REPO_PATH": "/tmp/main-rsps-checkout"}, clear=True):
            env = coding_worker._shared_env(assigned_repo)

        self.assertEqual(env["RSPS_REPO_PATH"], str(assigned_repo))


if __name__ == "__main__":
    unittest.main()
