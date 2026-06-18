from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from rsps_crewai_team import cron
from rsps_crewai_team.runtime import orchestrator, work_orders


class CronWatchdogTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self._original_project_root = cron.PROJECT_ROOT
        self._original_orders = work_orders.WORK_ORDERS_DIR
        self._original_runs = orchestrator.AGENCY_RUNS_DIR
        root = Path(self._tmp.name)
        cron.PROJECT_ROOT = root
        work_orders.WORK_ORDERS_DIR = root / "work_orders"
        orchestrator.AGENCY_RUNS_DIR = root / "agency-runs"

    def tearDown(self) -> None:
        cron.PROJECT_ROOT = self._original_project_root
        work_orders.WORK_ORDERS_DIR = self._original_orders
        orchestrator.AGENCY_RUNS_DIR = self._original_runs
        self._tmp.cleanup()

    def test_running_work_order_marks_rsps_work_active(self) -> None:
        self.assertFalse(cron.is_rsps_work_active())

        running = cron.PROJECT_ROOT / "work_orders" / "running"
        running.mkdir(parents=True, exist_ok=True)
        (running / "active.md").write_text("# Active\n\nWorker is running.\n", encoding="utf-8")

        self.assertTrue(cron.is_rsps_work_active())

    def test_scheduler_templates_use_one_minute_watchdog(self) -> None:
        self.assertIn("* * * * *", cron.CRON_TEMPLATE)
        self.assertNotIn("*/30 * * * *", cron.CRON_TEMPLATE)
        self.assertIn("OnUnitActiveSec=1min", cron.SYSTEMD_TIMER_TEMPLATE)
        self.assertNotIn("OnUnitActiveSec=30min", cron.SYSTEMD_TIMER_TEMPLATE)

    def test_self_filling_backlog_uses_server_building_workflow(self) -> None:
        cron.ensure_self_fulfilling_backlog()

        order = work_orders.next_work_order()
        self.assertIsNotNone(order)
        assert order is not None
        self.assertEqual(order.metadata["workflow_id"], "server_building_watchdog")
        self.assertEqual(order.metadata["step_id"], "watch")
        self.assertEqual(order.metadata["department"], "watcher")


if __name__ == "__main__":
    unittest.main()
