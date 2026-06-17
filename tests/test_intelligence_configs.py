from __future__ import annotations

import unittest

from rsps_crewai_team.runtime.intelligence import intelligence_status, profitability_scenarios, validate_intelligence_configs


class IntelligenceConfigTests(unittest.TestCase):
    def test_integrated_configs_validate(self) -> None:
        summary = validate_intelligence_configs()

        self.assertGreaterEqual(summary["source_count"], 9)
        self.assertGreaterEqual(summary["artifact_type_count"], 5)
        self.assertGreaterEqual(summary["prompt_pattern_count"], 4)
        self.assertGreaterEqual(summary["skill_count"], 6)

    def test_profitability_model_has_scenarios_and_ethics(self) -> None:
        scenarios = profitability_scenarios()
        status = intelligence_status()

        self.assertEqual([item["id"] for item in scenarios], ["downside", "base", "upside"])
        self.assertLess(scenarios[0]["net"], scenarios[-1]["net"])
        self.assertIn("Avoid pay-to-win mechanics, gambling loops, deceptive scarcity, and minors-targeted pressure.", status["profitability"]["ethics_policy"])


if __name__ == "__main__":
    unittest.main()
