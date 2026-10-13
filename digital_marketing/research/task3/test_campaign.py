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

    def test_no_action_claims_achieved_results(self):
        prohibited = ("proven", "guaranteed", "customers achieved", "scientifically")
        for item in self.actions:
            self.assertFalse(any(word in item["copy_or_script"].lower() for word in prohibited))


if __name__ == "__main__":
    unittest.main(verbosity=2)
