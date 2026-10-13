"""Presentation regression test for the Task 4 report tables."""
import unittest
import tempfile
import subprocess
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from generate_task4_report import table, build_pdf, build_email_appendix
from build_strategy import build_strategy
class ReportTableTests(unittest.TestCase):
    def test_dark_header_uses_explicit_white_bold_paragraph_style(self):
        body=ParagraphStyle("body",fontName="Helvetica",textColor=colors.HexColor("#1E2A32")); rendered=table([["Header"],["Body"]],[100],body)
        self.assertEqual(colors.white,rendered._cellvalues[0][0].style.textColor); self.assertEqual("Helvetica-Bold",rendered._cellvalues[0][0].style.fontName)
        self.assertEqual(colors.HexColor("#1E2A32"),rendered._cellvalues[1][0].style.textColor)

    def test_report_and_appendix_match_machine_readable_content(self):
        data = build_strategy()
        with tempfile.TemporaryDirectory() as folder:
            main = Path(folder) / "main.pdf"
            appendix = Path(folder) / "appendix.pdf"
            build_pdf(data, main)
            build_email_appendix(data, appendix)
            text = " ".join(subprocess.check_output(["pdftotext", str(main), "-"], text=True).split())
            appendix_text = " ".join(subprocess.check_output(["pdftotext", str(appendix), "-"], text=True).split())
            for keyword in data["keyword_map"]:
                self.assertIn(keyword["keyword"], text)
            for row in data["scenarios"]:
                self.assertIn(f"£{row['all_in_acquisition_cost_gbp']:.2f}", text)
            for flow in data["emails"]:
                for message in flow["messages"]:
                    self.assertIn(message["subject"], text)
                    self.assertIn(message["subject"], appendix_text)
                    self.assertIn(message["preview_text"], appendix_text)
                    self.assertIn(message["cta"], appendix_text)
                    self.assertIn(" ".join(message["body"].split()), appendix_text)
            self.assertIn("2018", text)
            self.assertIn("2019", text)
            self.assertIn("reviewer collection dates were not supplied", text.lower())
if __name__=="__main__": unittest.main(verbosity=2)
