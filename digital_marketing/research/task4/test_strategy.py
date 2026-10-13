"""Standard-library regression tests for the Task 4 strategy model."""

import copy
import unittest

from build_strategy import build_strategy, validate


class StrategyTests(unittest.TestCase):
    def setUp(self): self.data = build_strategy()

    def test_strategy_validates(self): self.assertEqual([], validate(self.data))
    def test_keyword_coverage_and_intents(self):
        self.assertGreaterEqual(len(self.data["keyword_map"]), 10)
        self.assertEqual({"informational", "commercial", "transactional"}, {x["intent"] for x in self.data["keyword_map"]})
    def test_seo_map_has_required_fields(self):
        for row in self.data["seo_map"]:
            self.assertTrue(row["proposed_title"]); self.assertTrue(row["proposed_meta_description"]); self.assertTrue(row["internal_links"])
    def test_budget_reconciles(self):
        budget=self.data["budget"]; self.assertEqual(12_000, sum(budget["allocation"].values())); self.assertEqual(10_000, budget["media_gbp"])
    def test_scenarios_reconcile_formulae(self):
        for row in self.data["scenarios"]:
            self.assertAlmostEqual(row["sessions"], row["impressions"] * row["ctr"])
            self.assertAlmostEqual(row["customers"], row["sessions"] * row["purchase_conversion_rate"])
            self.assertAlmostEqual(row["cac_gbp"], row["media_budget_gbp"] / row["customers"])
            self.assertAlmostEqual(row["roas"], row["attributed_revenue_gbp"] / row["media_budget_gbp"])
    def test_scenarios_are_ordered(self):
        low, base, high = self.data["scenarios"]
        self.assertLess(low["customers"], base["customers"]); self.assertLess(base["customers"], high["customers"])
    def test_zero_denominator_is_rejected(self):
        altered=copy.deepcopy(self.data); altered["scenarios"][0]["customers"] = 0
        self.assertIn("invalid financial denominator", validate(altered))
    def test_funnel_has_all_stages_and_measurement(self):
        self.assertEqual({"Awareness", "Consideration", "Conversion", "Retention"}, {x["stage"] for x in self.data["funnel"]})
        self.assertTrue(all(x["conversion_event"] and x["kpi"] for x in self.data["funnel"]))
    def test_email_flow_has_consent_and_exit_rules(self):
        self.assertGreaterEqual(len(self.data["emails"]), 4)
        self.assertTrue(all("consent" in x["entry"].lower() or x["id"] == "E4" for x in self.data["emails"]))
        self.assertTrue(all(x["exit_rule"] for x in self.data["emails"]))
    def test_observations_keep_blocked_source_separate(self):
        blocked = next(x for x in self.data["observations"] if x["id"] == "OB-05")
        self.assertEqual(403, blocked["status"]); self.assertIn("not used", blocked["observed"])


if __name__ == "__main__": unittest.main(verbosity=2)
