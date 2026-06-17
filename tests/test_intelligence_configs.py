from __future__ import annotations

import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from rsps_crewai_team.runtime.intelligence import intelligence_status, profitability_scenarios, validate_intelligence_configs


class IntelligenceConfigTests(unittest.TestCase):
    def test_integrated_configs_validate(self) -> None:
        summary = validate_intelligence_configs()

        self.assertGreaterEqual(summary["source_count"], 9)
        self.assertGreaterEqual(summary["artifact_type_count"], 5)
        self.assertGreaterEqual(summary["prompt_pattern_count"], 4)
        self.assertGreaterEqual(summary["skill_count"], 6)

    def test_profitability_without_live_metrics_is_unavailable(self) -> None:
        status = intelligence_status()

        self.assertEqual(status["profitability"]["status"], "unavailable")
        self.assertEqual(status["profitability"]["scenarios"], [])
        self.assertIn("Avoid pay-to-win mechanics, gambling loops, deceptive scarcity, and minors-targeted pressure.", status["profitability"]["ethics_policy"])

    def test_profitability_model_uses_live_metric_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "metrics.json"
            path.write_text(
                """
{
  "metrics": {
    "monthly_active_players": 450,
    "payer_conversion": 4.0,
    "arppu": 12.0,
    "hosting_cost": 85,
    "tooling_cost": 35,
    "asset_budget": 40
  }
}
""".strip(),
                encoding="utf-8",
            )
            with patch.dict(os.environ, {"RSPS_PROFITABILITY_METRICS_PATH": str(path)}, clear=False):
                scenarios = profitability_scenarios()
                status = intelligence_status()

        self.assertEqual(status["profitability"]["status"], "live")
        self.assertEqual([item["id"] for item in scenarios], ["downside", "base", "upside"])
        self.assertLess(scenarios[0]["net"], scenarios[-1]["net"])


if __name__ == "__main__":
    unittest.main()
