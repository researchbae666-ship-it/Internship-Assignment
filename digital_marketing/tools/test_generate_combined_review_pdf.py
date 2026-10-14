"""Regression tests for final Digital Marketing review-PDF assembly."""

import json
import unittest

from pypdf import PdfReader

from generate_combined_review_pdf import OUTPUT, SOURCES, build, sha256


class CombinedReviewPdfTests(unittest.TestCase):
    def test_build_preserves_source_hashes_and_navigation(self):
        before = {path: sha256(path) for _title, path, _description in SOURCES}
        result = build()
        self.assertTrue(all(result["source_hashes_unchanged"].values()))
        self.assertEqual(38, result["page_count"])
        self.assertTrue(result["checks"]["bookmarks"])
        self.assertTrue(result["checks"]["page_labels"])
        self.assertTrue(result["checks"]["metadata_privacy"])
        self.assertEqual(before, {path: sha256(path) for _title, path, _description in SOURCES})
        reader = PdfReader(OUTPUT)
        self.assertGreaterEqual(len(reader.outline), 5)
        self.assertIn("pending organizer acceptance", "\n".join(page.extract_text() or "" for page in reader.pages).lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
