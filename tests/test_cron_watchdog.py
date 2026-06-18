from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from rsps_crewai_team import cron
from rsps_crewai_team.runtime import work_orders


class CronWatchdogTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self._original_project_root = cron.PROJECT_ROOT
        self._original_orders = work_orders.WORK_ORDERS_DIR
        root = Path(self._tmp.name)
        cron.PROJECT_ROOT = root
        work_orders.WORK_ORDERS_DIR = root / "work_orders"

    def tearDown(self) -> None:
        cron.PROJECT_ROOT = self._original_project_root
        work_orders.WORK_ORDERS_DIR = self._original_orders
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


if __name__ == "__main__":
    unittest.main()
