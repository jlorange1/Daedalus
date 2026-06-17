from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rsps_crewai_team.runtime import git_sync


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True, check=False)


class GitSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        _git(self.repo, "init")
        _git(self.repo, "config", "user.name", "Daedalus Test")
        _git(self.repo, "config", "user.email", "daedalus@example.invalid")
        (self.repo / "README.md").write_text("seed\n", encoding="utf-8")
        _git(self.repo, "add", "README.md")
        _git(self.repo, "commit", "-m", "seed")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_remote_name_comes_from_env(self) -> None:
        with patch.dict(os.environ, {"RSPS_GIT_REMOTE": "github"}, clear=False):
            self.assertEqual(git_sync.git_remote_name(), "github")

    def test_push_refuses_protected_upstream_remote(self) -> None:
        _git(self.repo, "remote", "add", "github", "https://gitlab.com/2009scape/2009scape.git")

        with patch.dict(os.environ, {"RSPS_GIT_REMOTE": "github"}, clear=False):
            result = git_sync.push_current_branch(self.repo)

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Refusing to push autonomous work", result.output)

    def test_changed_files_reports_porcelain_paths(self) -> None:
        (self.repo / "README.md").write_text("changed\n", encoding="utf-8")
        (self.repo / "new.txt").write_text("new\n", encoding="utf-8")

        files = git_sync.changed_files(self.repo)

        self.assertIn("README.md", files)
        self.assertIn("new.txt", files)


if __name__ == "__main__":
    unittest.main()
