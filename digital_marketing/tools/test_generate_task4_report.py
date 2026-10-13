"""Presentation regression test for the Task 4 report tables."""
import unittest
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from generate_task4_report import table
class ReportTableTests(unittest.TestCase):
    def test_dark_header_uses_explicit_white_bold_paragraph_style(self):
        body=ParagraphStyle("body",fontName="Helvetica",textColor=colors.HexColor("#1E2A32")); rendered=table([["Header"],["Body"]],[100],body)
        self.assertEqual(colors.white,rendered._cellvalues[0][0].style.textColor); self.assertEqual("Helvetica-Bold",rendered._cellvalues[0][0].style.fontName)
        self.assertEqual(colors.HexColor("#1E2A32"),rendered._cellvalues[1][0].style.textColor)
if __name__=="__main__": unittest.main(verbosity=2)
