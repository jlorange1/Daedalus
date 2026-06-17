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


if __name__ == "__main__":
    unittest.main()
