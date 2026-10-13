"""Regression tests for Task 3 PDF presentation helpers."""

import unittest

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle

from generate_task3_report import table


class TablePresentationTests(unittest.TestCase):
    def test_header_cells_use_explicit_white_bold_paragraph_style(self):
        body = ParagraphStyle("Body", fontName="Helvetica", textColor=colors.HexColor("#1E2A32"))
        rendered = table(
            [["Column one", "Column two"], ["Value one", "Value two"]],
            [100, 100],
            body,
        )

        for header_cell in rendered._cellvalues[0]:
            self.assertEqual(colors.white, header_cell.style.textColor)
            self.assertEqual("Helvetica-Bold", header_cell.style.fontName)

        for body_cell in rendered._cellvalues[1]:
            self.assertEqual(colors.HexColor("#1E2A32"), body_cell.style.textColor)
            self.assertEqual("Helvetica", body_cell.style.fontName)


if __name__ == "__main__":
    unittest.main(verbosity=2)
