"""Standard-library checks for the generated RefillLoop campaign data."""

import unittest

from build_campaign import REQUIRED_ACTION_FIELDS, build_campaign, validate


class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.campaign = build_campaign()
        self.actions = self.campaign["actions"]

    def test_calendar_has_every_day_and_required_platform(self):
        self.assertEqual(set(range(1, 31)), {item["day"] for item in self.actions})
        self.assertEqual({"Instagram", "LinkedIn", "YouTube"}, {item["platform"] for item in self.actions})

    def test_every_action_has_complete_nonempty_fields(self):
        for item in self.actions:
            self.assertTrue(REQUIRED_ACTION_FIELDS <= set(item))
            for field in REQUIRED_ACTION_FIELDS:
                self.assertNotIn(item[field], (None, ""), f"{field} missing for day {item['day']}")

    def test_every_action_has_discovery_strategy_and_distinct_copy(self):
        copy_values = {item["copy_or_script"] for item in self.actions}
        self.assertGreater(len(copy_values), 45)
        for item in self.actions:
            strategy = item["keyword_strategy"]
            self.assertTrue(strategy["primary_keyword"])
            self.assertTrue(strategy["supporting_keywords"])
            self.assertTrue(strategy["hashtags_or_video_tags"])
            self.assertTrue(strategy["search_discovery_intent"])
            self.assertTrue(strategy["rationale"])
            self.assertTrue(item["ad_copy"])

    def test_targeting_specs_are_present_and_action_refs_are_consistent(self):
        specifications = self.campaign["targeting_specifications"]
        self.assertEqual({"Instagram", "LinkedIn", "YouTube"}, set(specifications))
        fields = {"targeting_id", "geography", "language", "age", "inclusion", "exclusion", "placement", "conversion_event", "privacy_policy"}
        ids = set()
        for spec in specifications.values():
            self.assertTrue(fields <= set(spec))
            self.assertTrue(all(spec[field] for field in fields))
            ids.add(spec["targeting_id"])
        self.assertTrue(all(item["targeting_id"] in ids for item in self.actions))

    def test_appropriate_platform_frequency_and_formats(self):
        formats = {(item["platform"], item["content_format"]) for item in self.actions}
        self.assertIn(("Instagram", "Reel"), formats)
        self.assertIn(("Instagram", "Carousel"), formats)
        self.assertIn(("Instagram", "Stories"), formats)
        self.assertIn(("LinkedIn", "Article"), formats)
        self.assertIn(("YouTube", "Short"), formats)
        self.assertIn(("YouTube", "Long-form"), formats)
        self.assertLess(sum(item["platform"] == "LinkedIn" for item in self.actions), 30)
        self.assertLess(sum(item["platform"] == "YouTube" for item in self.actions), 30)

    def test_budget_and_data_validation(self):
        self.assertEqual([], validate(self.campaign))
        budget = self.campaign["budget"]
        self.assertEqual(budget["total"], sum(budget["allocation"].values()))

    def test_pacing_maps_every_paid_action_and_reconciles(self):
        budget = self.campaign["budget"]
        pacing = self.campaign["budget_pacing"]
        paid_ids = {item["action_id"] for item in self.actions if item["distribution"] == "Paid"}
        self.assertEqual(paid_ids, {row["action_id"] for row in pacing})
        for platform, amount in budget["allocation"].items():
            self.assertEqual(amount, sum(row["proposed_spend_usd"] for row in pacing if row["platform"] == platform))

    def test_funnel_scenarios_reconcile(self):
        scenarios = self.campaign["funnel"]["scenarios"]
        self.assertEqual({"Low", "Base", "High", "Stretch"}, {row["name"] for row in scenarios})
        for row in scenarios:
            self.assertAlmostEqual(row["landing_sessions"], row["impressions"] * row["click_through_rate"])
            self.assertAlmostEqual(row["interest_completions"], row["landing_sessions"] * row["form_completion_rate"])
        base = next(row for row in scenarios if row["name"] == "Base")
        stretch = next(row for row in scenarios if row["name"] == "Stretch")
        self.assertEqual(30, base["interest_completions"])
        self.assertEqual(300, stretch["interest_completions"])

    def test_four_ab_tests_are_actionable(self):
        tests = self.campaign["ab_tests"]
        self.assertEqual(4, len(tests))
        for test in tests:
            self.assertTrue(all(test[field] for field in ("hypothesis", "control", "treatment", "audience", "primary_metric", "decision_criterion")))

    def test_no_action_claims_achieved_results(self):
        prohibited = ("proven", "guaranteed", "customers achieved", "scientifically", "market-leading")
        for item in self.actions:
            self.assertFalse(any(word in item["copy_or_script"].lower() for word in prohibited))


if __name__ == "__main__":
    unittest.main(verbosity=2)
