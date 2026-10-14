import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'digital_marketing/tools'))
import generate_task2_handoff_report as report


class HandoffTests(unittest.TestCase):
    def test_historical_arithmetic_is_not_publication_count(self):
        for before, after, expected in [(2459, 2474, 15), (3834, 3849, 15), (1104, 1121, 17)]:
            row = report.historical_delta(before, after)
            self.assertEqual(expected, row['net_change'])
            for key in ('verified_published_posts', 'posts_per_week', 'engagement_rate'):
                self.assertIsNone(row[key])

    def test_missing_and_invalid_values_fail(self):
        for value in (None, True, '2459', -1, 2.5):
            with self.assertRaises(ValueError):
                report.historical_delta(value, 2474)

    def test_decreasing_cumulative_total_not_rejected_as_impossible(self):
        self.assertEqual(-1, report.historical_delta(10, 9)['net_change'])

    def test_provenance_and_showcase_identity_preserved(self):
        text = report.validate_source()
        self.assertIn('2026-10-13', text)
        self.assertIn('not collected by the Codex Cloud runtime', text)
        self.assertIn('showcase/owala-hydration/', text)
        self.assertIn('Parent-company posts must not be substituted', text)

    def test_invalid_handoff_prevents_report(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'invalid.md'
            source.write_text('unsupported')
            output = Path(folder) / 'invalid.pdf'
            with patch.object(report, 'SOURCE', source), self.assertRaises(ValueError):
                report.build(output)
            self.assertFalse(output.exists())

    def test_pdf_has_four_pages_and_honest_missing_data(self):
        with tempfile.TemporaryDirectory() as folder:
            output = report.build(Path(folder) / 'report.pdf')
            meta = subprocess.check_output(['pdfinfo', str(output)], text=True)
            self.assertRegex(meta, r'Pages:\s+4\b')
            text = ' '.join(subprocess.check_output(['pdftotext', str(output), '-'], text=True).split())
            for phrase in ('not directly retrieved by Codex', 'nominal 26-day interval',
                           'not verified publications', 'incomplete for measured-audit approval',
                           'showcase/owala-hydration/', 'Unavailable'):
                self.assertIn(phrase, text)


if __name__ == '__main__':
    unittest.main(verbosity=2)
