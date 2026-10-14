import copy
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import secondary_metrics as metrics
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'digital_marketing/tools'))
import generate_task2_secondary_report as report


class SecondaryTests(unittest.TestCase):
    def setUp(self):
        self.data = metrics.load()

    def test_arithmetic_and_vendor_rates(self):
        rows = metrics.calculate(self.data)
        for row, change, proxy, rate in zip(rows, (15, 15, 17), (4.04, 4.04, 4.58), (1.19, 2.38, 2.71)):
            self.assertEqual(change, row['net_change'])
            self.assertAlmostEqual(proxy, row['nominal_net_change_per_week_proxy'], places=2)
            self.assertEqual(rate, row['vendor_estimated_october_engagement_percent'])
            self.assertIn('NOT verified publication frequency', row['proxy_unit'])

    def test_period_values_remain_null(self):
        for row in metrics.calculate(self.data):
            self.assertIsNone(row['verified_period_post_count'])
            self.assertIsNone(row['exact_28_day_posts_per_week'])
            self.assertIsNone(row['independently_calculated_period_engagement_percent'])

    def test_wrong_account_or_source_rejected(self):
        for field, value in [('handle', 'owala'), ('url', 'https://example.org/')]:
            data = copy.deepcopy(self.data)
            data['rows'][0][field] = value
            with self.assertRaises(ValueError): metrics.validate(data)

    def test_numbers_must_match_supplied_note(self):
        for field, value in [('start_total', 2460), ('end_total', 2475), ('vendor_estimated_october_engagement_percent', 1.20)]:
            data = copy.deepcopy(self.data)
            data['rows'][0][field] = value
            with self.assertRaises(ValueError): metrics.validate(data)

    def test_missing_invalid_and_bool_values_rejected(self):
        for field in ('start_total', 'end_total', 'vendor_estimated_october_engagement_percent'):
            for value in (None, True, -1, '1.19'):
                data = copy.deepcopy(self.data)
                data['rows'][0][field] = value
                with self.assertRaises(ValueError): metrics.validate(data)

    def test_date_mismatch_and_duplicate_brands_rejected(self):
        for field, value in [('snapshot_start', '2026-09-15'), ('nominal_interval_days', 28), ('collected_date_utc', '2026-10-13'), ('engagement_month', '2026-09')]:
            data = copy.deepcopy(self.data); data[field] = value
            with self.assertRaises(ValueError): metrics.validate(data)
        self.data['rows'][1] = copy.deepcopy(self.data['rows'][0])
        with self.assertRaises(ValueError): metrics.validate(self.data)

    def test_false_first_party_provenance_and_cadence_rejected(self):
        self.data['provenance'] = 'direct retrieval'
        with self.assertRaises(ValueError): metrics.validate(self.data)
        for field in ('verified_period_post_count', 'exact_28_day_posts_per_week', 'independently_calculated_period_engagement_percent'):
            data = metrics.load(); data['rows'][0][field] = 0
            with self.assertRaises(ValueError): metrics.validate(data)

    def test_pdf_matches_all_metrics_and_limitations(self):
        with tempfile.TemporaryDirectory() as directory:
            output = report.build(Path(directory) / 'report.pdf')
            info = subprocess.check_output(['pdfinfo', str(output)], text=True)
            self.assertRegex(info, r'Pages:\s+4\b')
            text = ' '.join(subprocess.check_output(['pdftotext', str(output), '-'], text=True).split())
            for row in metrics.calculate(self.data):
                for value in (row['brand'], row['handle'], str(row['start_total']), str(row['end_total']), f"{row['vendor_estimated_october_engagement_percent']:.2f}%", f"{row['nominal_net_change_per_week_proxy']:.2f}"):
                    self.assertIn(value, text)
            for phrase in ('NOT verified publication frequency', 'proprietary estimates', 'nominal 26-day interval', 'Codex direct retrieval remained blocked', 'incomplete for measured-audit approval', '28-day cadence'):
                self.assertIn(phrase, text)


if __name__ == '__main__': unittest.main(verbosity=2)
