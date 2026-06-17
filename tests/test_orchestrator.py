from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from rsps_crewai_team.runtime import orchestrator, work_orders


class OrchestratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self._original_orders = work_orders.WORK_ORDERS_DIR
        self._original_runs = orchestrator.AGENCY_RUNS_DIR
        root = Path(self._tmp.name)
        work_orders.WORK_ORDERS_DIR = root / "work_orders"
        orchestrator.AGENCY_RUNS_DIR = root / "agency-runs"

    def tearDown(self) -> None:
        work_orders.WORK_ORDERS_DIR = self._original_orders
        orchestrator.AGENCY_RUNS_DIR = self._original_runs
        self._tmp.cleanup()

    def test_create_workflow_run_enqueues_first_level(self) -> None:
        manifest = orchestrator.create_workflow_run("profitability_review")

        self.assertEqual(manifest["workflow_id"], "profitability_review")
        self.assertEqual(manifest["levels"][0], ["business_scope"])
        self.assertEqual(manifest["steps"]["business_scope"]["status"], "queued")
        order = work_orders.next_work_order()
        self.assertIsNotNone(order)
        assert order is not None
        self.assertEqual(order.metadata["workflow_id"], "profitability_review")
        self.assertEqual(order.metadata["step_id"], "business_scope")
        self.assertFalse(order.metadata["writes_code"])

    def test_list_workflow_runs_summarizes_manifest(self) -> None:
        created = orchestrator.create_workflow_run("incident_recovery")
        runs = orchestrator.list_workflow_runs()

        self.assertEqual(runs[0]["run_id"], created["run_id"])
        self.assertEqual(runs[0]["workflow_id"], "incident_recovery")
        self.assertGreaterEqual(runs[0]["queued"], 1)

    def test_advancing_first_step_queues_parallel_dependents(self) -> None:
        manifest = orchestrator.create_workflow_run("profitability_review")
        run_id = manifest["run_id"]

        advanced = orchestrator.update_step_status(run_id, "business_scope", "done")

        self.assertEqual(advanced["steps"]["business_scope"]["status"], "done")
        self.assertEqual(advanced["steps"]["economy_analysis"]["status"], "queued")
        self.assertEqual(advanced["steps"]["player_experience"]["status"], "queued")
        self.assertEqual(advanced["steps"]["security_abuse"]["status"], "queued")

    def test_code_step_waits_for_review_before_queueing(self) -> None:
        manifest = orchestrator.create_workflow_run("visual_product_pass")
        run_id = manifest["run_id"]
        manifest = orchestrator.update_step_status(run_id, "creative_direction", "done")
        manifest = orchestrator.update_step_status(run_id, "art_audio_review", "done")
        manifest = orchestrator.update_step_status(run_id, "client_plan", "done")

        self.assertEqual(manifest["steps"]["implementation"]["status"], "awaiting_review")
        self.assertIsNone(manifest["steps"]["implementation"]["work_order"])

        approved = orchestrator.approve_step(run_id, "implementation")
        self.assertEqual(approved["steps"]["implementation"]["status"], "queued")
        self.assertIsNotNone(approved["steps"]["implementation"]["work_order"])

    def test_step_artifact_is_recorded(self) -> None:
        manifest = orchestrator.create_workflow_run("profitability_review")
        run_id = manifest["run_id"]
        artifact = {
            "changed_files": ["src/example.py"],
            "changed_file_count": 1,
            "validation": {"worker_exit_code": 0, "log_path": "logs/example.log"},
        }

        advanced = orchestrator.update_step_status(
            run_id,
            "business_scope",
            "done",
            worker_run_id="worker-run-1",
            artifact=artifact,
        )

        self.assertEqual(advanced["steps"]["business_scope"]["worker_run_id"], "worker-run-1")
        self.assertEqual(advanced["steps"]["business_scope"]["artifact"]["changed_file_count"], 1)


if __name__ == "__main__":
    unittest.main()
