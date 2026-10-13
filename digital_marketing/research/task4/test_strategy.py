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
        self.assertEqual(10, sum(len(x["messages"]) for x in self.data["emails"]))
        for flow in self.data["emails"]:
            for message in flow["messages"]:
                self.assertGreater(len(message["body"]), 300)
                self.assertTrue(message["exit_condition"])
                self.assertIn("Unsubscribe", message["body"])

    def test_all_in_cost_and_media_roas_are_separate(self):
        for row, expected in zip(self.data["scenarios"], (160, 75, 37.5)):
            self.assertEqual(expected, row["all_in_acquisition_cost_gbp"])
            self.assertAlmostEqual(row["cac_gbp"], 10000 / row["customers"])
            self.assertAlmostEqual(row["roas"], row["attributed_revenue_gbp"] / 10000)

    def test_corrupted_all_in_calculation_is_rejected(self):
        self.data["scenarios"][0]["all_in_acquisition_cost_gbp"] += 1
        self.assertIn("all-in acquisition cost mismatch", validate(self.data))

    def test_reviewer_provenance_and_unresolved_years(self):
        sources = self.data["reviewer_sources"]
        self.assertEqual({2018, 2019}, {x["founding_year_statement"] for x in sources})
        self.assertTrue(all(x["collection_date"] is None for x in sources))
        self.assertTrue(all("not directly retrieved" in x["provenance"] for x in sources))
        self.assertIn("neither", self.data["subject"]["selection"].lower())

    def test_missing_email_copy_and_invalid_delay_are_rejected(self):
        self.data["emails"][0]["messages"][0]["preview_text"] = ""
        self.data["emails"][0]["messages"][1]["delay_hours_from_entry"] = -1
        self.assertIn("incomplete email message", validate(self.data))
        self.assertIn("invalid email timing", validate(self.data))
    def test_observations_keep_blocked_source_separate(self):
        blocked = next(x for x in self.data["observations"] if x["id"] == "OB-05")
        self.assertEqual(403, blocked["status"]); self.assertIn("not used", blocked["observed"])


if __name__ == "__main__": unittest.main(verbosity=2)
