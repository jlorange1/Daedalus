from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from rsps_crewai_team.runtime import work_orders


class WorkOrderSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self._original_dir = work_orders.WORK_ORDERS_DIR
        self._tmp = tempfile.TemporaryDirectory()
        work_orders.WORK_ORDERS_DIR = Path(self._tmp.name)

    def tearDown(self) -> None:
        work_orders.WORK_ORDERS_DIR = self._original_dir
        self._tmp.cleanup()

    def test_slugify_keeps_filename_safe_fallback(self) -> None:
        self.assertEqual(work_orders.slugify("  Build Starter Zone!  "), "build-starter-zone")
        self.assertEqual(work_orders.slugify("!!!"), "work-order")

    def test_create_next_and_move_work_order(self) -> None:
        created = work_orders.create_work_order("Smoke Order", "Check queue lifecycle.")

        self.assertEqual(created.parent.name, "inbox")
        self.assertTrue(created.name.endswith("-smoke-order.md"))
        self.assertEqual(created.read_text(encoding="utf-8"), "# Smoke Order\n\nCheck queue lifecycle.\n")

        order = work_orders.next_work_order()
        self.assertIsNotNone(order)
        assert order is not None
        self.assertEqual(order.title, "Smoke Order")
        self.assertIn("Check queue lifecycle.", order.body)

        done = work_orders.move_work_order(order, "done")
        self.assertEqual(done.parent.name, "done")
        self.assertTrue(done.exists())
        self.assertFalse(created.exists())

    def test_metadata_sidecar_moves_with_work_order(self) -> None:
        created = work_orders.create_work_order(
            "Workflow Order",
            "Check metadata.",
            metadata={"workflow_id": "profitability_review", "workflow_step_id": "business_scope"},
        )

        self.assertEqual(created.read_text(encoding="utf-8"), "# Workflow Order\n\nCheck metadata.\n")
        self.assertEqual(
            work_orders.read_work_order_metadata(created),
            {"workflow_id": "profitability_review", "workflow_step_id": "business_scope"},
        )
        order = work_orders.next_work_order()
        self.assertIsNotNone(order)
        assert order is not None
        self.assertEqual(order.metadata["workflow_id"], "profitability_review")

        done = work_orders.move_work_order(order, "done")
        self.assertTrue(work_orders.metadata_path(done).exists())
        self.assertFalse(work_orders.metadata_path(created).exists())

    def test_move_rejects_unknown_status(self) -> None:
        created = work_orders.create_work_order("Bad Status", "Should not move.")
        order = work_orders.WorkOrder(path=created, title="Bad Status", body="")

        with self.assertRaises(ValueError):
            work_orders.move_work_order(order, "archived")

    def test_validate_workflow_metadata_rejects_unknown_step(self) -> None:
        with self.assertRaises(ValueError):
            work_orders.validate_workflow_metadata("profitability_review", "not-a-step")


if __name__ == "__main__":
    unittest.main()
