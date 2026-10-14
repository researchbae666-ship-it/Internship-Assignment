"""Check source-backed draft text and presentation; no invented metrics."""

import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from generate_task2_recovery_report import RESEARCH, EVIDENCE, build_pdf, table


class RecoveryReportTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((RESEARCH / "observations.json").read_text())
        self.sources = json.loads((EVIDENCE / "source_records.json").read_text())
        self.browsers = json.loads((EVIDENCE / "browser_records.json").read_text())

    def test_dark_header_has_white_bold_paragraphs(self):
        style = ParagraphStyle("TestBody", textColor=colors.black, fontName="Helvetica")
        result = table([["Header"], ["Body"]], [100], style)
        self.assertEqual(colors.white, result._cellvalues[0][0].style.textColor)
        self.assertEqual("Helvetica-Bold", result._cellvalues[0][0].style.fontName)
        self.assertEqual(colors.black, result._cellvalues[1][0].style.textColor)

    def test_four_page_draft_retains_claims_and_missing_metrics(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "draft.pdf"
            build_pdf(self.data, self.sources, self.browsers, path)
            text = " ".join(subprocess.check_output(["pdftotext", str(path), "-"], text=True).split())
            metadata = subprocess.check_output(["pdfinfo", str(path)], text=True)
            self.assertRegex(metadata, r"Pages:\s+4\b")
            self.assertIn("PARTIAL EVIDENCE DRAFT", text)
            self.assertIn("not a completed measured audit", text)
            self.assertIn("15 September", text)
            self.assertGreaterEqual(text.count("Unavailable"), 18)
            for fact in self.data["facts"]:
                self.assertIn(" ".join(fact["quote"].split()), text)
            for account in self.data["accounts"]:
                if account["verified"]:
                    self.assertIn(account["account_url"], text)

    def test_invalid_source_claim_prevents_pdf_output(self):
        self.data["facts"][0]["quote"] = "fabricated company claim"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "invalid.pdf"
            with self.assertRaises(ValueError):
                build_pdf(self.data, self.sources, self.browsers, path)
            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
