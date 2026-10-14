"""Meaningful recovery validation; numerical cases are synthetic tests only."""

import copy
import json
import unittest
from pathlib import Path
from build_audit import EVIDENCE, validate
from collect_sources import extract
from metrics import WINDOW, calculate


def synthetic(platform="Instagram"):
    """No real brand data, estimates, or marketing results are implied."""
    return {"observation_window": WINDOW, "accounts": [{"brand": "SyntheticTest", "platform": platform, "window_inventory_complete": False}],
            "posts": [{"brand": "SyntheticTest", "platform": platform, "post_url": "https://example.test/post/1", "official_account_verified": True,
                       "published_utc": "2026-10-01T12:00:00Z", "collected_utc": "2026-10-14T06:00:00Z", "evidence_reference": "synthetic unit-test fixture only",
                       "visible_likes": 20, "visible_comments": 5, "visible_reactions": 30, "visible_followers": 1000, "follower_count_precision": "exact"}]}


class MetricTests(unittest.TestCase):
    def test_partial_sample_is_minimum_not_full_frequency(self):
        row = calculate(synthetic())["measurements"][0]
        self.assertEqual(0.25, row["weekly_activity"])
        self.assertEqual("observed minimum activity", row["cadence_classification"])

    def test_missing_sample_is_unavailable_not_zero(self):
        data = synthetic(); data["posts"] = []
        row = calculate(data)["measurements"][0]
        self.assertIsNone(row["weekly_activity"])
        self.assertFalse(row["engagement_available"])

    def test_verified_complete_inventory_can_be_true_zero(self):
        data = synthetic(); data["posts"] = []; data["accounts"][0]["window_inventory_complete"] = True
        self.assertEqual(0, calculate(data)["measurements"][0]["weekly_activity"])

    def test_instagram_and_linkedin_numerators_remain_distinct(self):
        ig = calculate(synthetic())["measurements"][0]["visible_interaction_proxies"][0]
        li = calculate(synthetic("LinkedIn"))["measurements"][0]["visible_interaction_proxies"][0]
        self.assertEqual(2.5, ig["proxy_percent"])
        self.assertAlmostEqual(3.5, li["proxy_percent"])
        self.assertNotEqual(ig["definition"], li["definition"])

    def test_youtube_never_uses_follower_proxy(self):
        self.assertEqual([], calculate(synthetic("YouTube"))["measurements"][0]["visible_interaction_proxies"])

    def test_missing_rounded_zero_and_invalid_denominators(self):
        for value in (None, 0, -1, True, "1K", 1000.0):
            data = synthetic(); data["posts"][0]["visible_followers"] = value
            self.assertIsNone(calculate(data)["measurements"][0]["visible_interaction_proxies"][0]["proxy_percent"])
        data = synthetic(); data["posts"][0]["follower_count_precision"] = "rounded"
        self.assertIsNone(calculate(data)["measurements"][0]["visible_interaction_proxies"][0]["proxy_percent"])

    def test_missing_or_invalid_interaction_not_zero(self):
        for value in (None, -1, True, "hidden"):
            data = synthetic(); data["posts"][0]["visible_likes"] = value
            self.assertIsNone(calculate(data)["measurements"][0]["visible_interaction_proxies"][0]["proxy_percent"])

    def test_publication_bounds_and_timezone(self):
        data = synthetic(); data["posts"][0]["published_utc"] = "2026-10-13T00:00:00Z"
        self.assertIsNone(calculate(data)["measurements"][0]["weekly_activity"])
        data["posts"][0]["published_utc"] = "2026-10-01T12:00:00"
        with self.assertRaises(ValueError): calculate(data)

    def test_duplicates_and_missing_provenance_rejected(self):
        data = synthetic(); data["posts"].append(copy.deepcopy(data["posts"][0]))
        with self.assertRaises(ValueError): calculate(data)
        data = synthetic(); data["posts"][0]["official_account_verified"] = False
        with self.assertRaises(ValueError): calculate(data)
        data = synthetic(); data["posts"][0]["evidence_reference"] = None
        with self.assertRaises(ValueError): calculate(data)

    def test_collection_before_publication_rejected(self):
        data = synthetic(); data["posts"][0]["collected_utc"] = "2026-09-01T00:00:00Z"
        with self.assertRaises(ValueError): calculate(data)


class RetainedEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(Path(__file__).with_name("observations.json").read_text())
        self.sources = json.loads((EVIDENCE / "source_records.json").read_text())
        self.browsers = json.loads((EVIDENCE / "browser_records.json").read_text())

    def test_real_sources_support_every_quote_and_verified_link(self):
        self.assertEqual([], validate(self.data, self.sources, self.browsers))
        self.assertEqual(12, len(self.data["facts"]))
        self.assertEqual(5, sum(account["verified"] for account in self.data["accounts"]))

    def test_real_metrics_remain_unavailable_for_all_nine_accounts(self):
        result = calculate(self.data)
        self.assertEqual(9, len(result["measurements"]))
        self.assertTrue(all(row["weekly_activity"] is None for row in result["measurements"]))
        self.assertFalse(result["has_dated_post_evidence"])
        self.assertEqual([], self.data["posts"])

    def test_unsupported_claim_and_false_completion_fail(self):
        self.data["facts"][0]["quote"] = "invented company performance claim"
        self.assertTrue(validate(self.data, self.sources, self.browsers))
        self.data["status"] = "completed audit"
        self.assertIn("Recovery must not claim completed measurement", validate(self.data, self.sources, self.browsers))

    def test_source_records_have_dates_and_statuses_without_fake_http_zero(self):
        self.assertEqual(12, len(self.sources))
        for source in self.sources:
            self.assertTrue(source["collected_utc"])
            self.assertNotEqual(0, source["http_status"])
            if source["http_status"] == 200:
                self.assertEqual(64, len(source["sha256_raw"]))
        self.assertEqual(6, len(self.browsers))

    def test_html_extract_omits_script_tokens_and_tracks_social_urls(self):
        html = '<script>secret_transient_token</script><style>hidden_css</style><h1>Public brand</h1><a href="https://www.instagram.com/example/">Public account</a>'
        result = extract(html)
        self.assertNotIn("secret_transient_token", str(result))
        self.assertNotIn("hidden_css", str(result))
        self.assertIn("Public brand", result["public_text"])
        self.assertEqual(["https://www.instagram.com/example/"], result["social_links"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
