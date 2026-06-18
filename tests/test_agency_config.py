from __future__ import annotations

import unittest

from rsps_crewai_team.runtime.agency import agency_status, validate_agency_config


class AgencyConfigTests(unittest.TestCase):
    def test_catalog_and_workflows_validate(self) -> None:
        dags = validate_agency_config()

        self.assertGreaterEqual(len(dags), 3)
        self.assertIn("server_building_watchdog", {dag.workflow_id for dag in dags})
        self.assertIn("feature_delivery_mesh", {dag.workflow_id for dag in dags})
        self.assertTrue(all(dag.step_count > 0 for dag in dags))
        self.assertTrue(all(dag.max_parallel >= 1 for dag in dags))

    def test_status_exposes_departments_and_dag_levels(self) -> None:
        status = agency_status()

        self.assertGreaterEqual(status["department_count"], 18)
        self.assertGreaterEqual(status["workflow_count"], 5)
        departments = {item["id"] for item in status["departments"]}
        self.assertTrue({"watcher", "thinker", "orchestrator", "reporter"} <= departments)
        server_build = next(item for item in status["workflows"] if item["id"] == "server_building_watchdog")
        self.assertEqual(server_build["levels"][0], ["watch"])
        self.assertIn("implementation", {step for level in server_build["levels"] for step in level})
        feature = next(item for item in status["workflows"] if item["id"] == "feature_delivery_mesh")
        self.assertEqual(feature["levels"][0], ["scope"])
        self.assertIn("qa", {step for level in feature["levels"] for step in level})
        self.assertIn("security", {step for level in feature["levels"] for step in level})


if __name__ == "__main__":
    unittest.main()
