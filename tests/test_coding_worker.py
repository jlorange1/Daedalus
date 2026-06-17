from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rsps_crewai_team.runtime.coding_worker import build_worker_command


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


if __name__ == "__main__":
    unittest.main()
