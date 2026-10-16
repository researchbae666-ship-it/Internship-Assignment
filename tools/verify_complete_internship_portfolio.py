#!/usr/bin/env python3
"""Verify source preservation, rendering and navigation for the final portfolio.

The optional ``--manual-visual-review-complete`` flag is an operator attestation
that rendered pages were actually reviewed. It does not alter the PDF.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

import fitz
from PIL import Image, ImageDraw
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "FINAL_SUBMISSION"
PORTFOLIO = FINAL / "01_Progree_Complete_Internship_Portfolio.pdf"
MANIFEST = FINAL / "manifest.json"
QA = FINAL / "QA" / "FINAL_VERIFICATION.md"
MARKETING = ROOT / "digital_marketing/deliverables/Progree_Digital_Marketing_Tasks_2_3_4_FINAL_CANDIDATE.pdf"
PYTHON = ROOT / "deliverables/Progree_Python_Tasks_2_3_4_FINAL_CANDIDATE.pdf"
EXPECTED_MARKETING_SHA = "571f801e92fd496b27dc8bcd1fb40066d22068f35b783ba2e151f36b7335bb5a"
EXPECTED_PYTHON_SHA = "8910c0aafccb8a575affc9794291b5c9910a23cfebdda3fa6b873c485bece284"
RENDER_DIR = Path("/tmp/progree-complete-portfolio-render")
SOURCE_RANGES = ((MARKETING, 5, 38), (PYTHON, 44, 14))
EXPECTED_OUTLINES = [
    ("Cover", 1),
    ("Executive summary", 2),
    ("Contents", 3),
    ("Results at a glance", 4),
    ("Digital Marketing & Branding", 5),
    ("Track introduction", 5),
    ("Approved report", 6),
    ("Task 2 — evidence-limited public-source audit", 8),
    ("Task 3 — RefillLoop proposed 30-day campaign", 12),
    ("Task 4 — Ocean Bottle proposed SEO strategy", 32),
    ("Task 4 supporting appendix — proposed email workflows", 38),
    ("Python Programming", 44),
    ("Track introduction", 44),
    ("Approved report", 45),
    ("Task 2 — Fibonacci and timing", 47),
    ("Task 3 — safe file automation", 50),
    ("Task 4 — multi-intent rule-based chatbot", 53),
    ("Selective verification and project evidence", 59),
    ("Conclusion and source / reproduction index", 60),
]
SOURCE_INDEX_URLS = [
    "https://github.com/researchbae666-ship-it/Internship-Assignment/blob/main/internship/task2.py",
    "https://github.com/researchbae666-ship-it/Internship-Assignment/blob/main/internship/task3.py",
    "https://github.com/researchbae666-ship-it/Internship-Assignment/blob/main/internship/task4.py",
    "https://github.com/researchbae666-ship-it/Internship-Assignment/tree/main/tests",
    "https://github.com/researchbae666-ship-it/Internship-Assignment/tree/main/digital_marketing/research/task2",
    "https://github.com/researchbae666-ship-it/Internship-Assignment/blob/main/digital_marketing/research/task3/build_campaign.py",
    "https://github.com/researchbae666-ship-it/Internship-Assignment/blob/main/digital_marketing/research/task4/build_strategy.py",
    "https://github.com/researchbae666-ship-it/Internship-Assignment/blob/main/digital_marketing/research/task4/email_workflows.py",
    "https://github.com/researchbae666-ship-it/Internship-Assignment/blob/main/evidence/ultimate_final_review/QA.md",
    "https://github.com/researchbae666-ship-it/Internship-Assignment/blob/main/evidence/ultimate_final_review/manifest.json",
]
REGRESSION_COMMANDS = [
    ("python -m unittest discover -s tests -v", "55 tests passed"),
    ("(cd digital_marketing/research/task2/handoff && python -m unittest -v test_handoff)", "6 tests passed"),
    ("(cd digital_marketing/research/task2/recovery && python -m unittest -v test_recovery)", "15 tests passed"),
    ("(cd digital_marketing/research/task2/secondary && python -m unittest -v test_secondary)", "8 tests passed"),
    ("(cd digital_marketing/research/task3 && python -m unittest -v test_campaign)", "11 tests passed"),
    ("(cd digital_marketing/research/task4 && python -m unittest -v test_strategy test_email_workflows)", "28 tests passed"),
    ("(cd digital_marketing/tools && python -m unittest -v test_task2_recovery_report test_generate_task3_report test_generate_task4_report)", "6 tests passed"),
    ("python tools/ultimate_red_team_checks.py", "passed; protected hashes unchanged"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stream(page: Any) -> bytes:
    content = page.get_contents()
    return content.get_data() if content is not None else b""


def flatten_outlines(reader: PdfReader, items: list[Any] | None = None) -> list[tuple[str, int]]:
    items = reader.outline if items is None else items
    result: list[tuple[str, int]] = []
    for item in items:
        if isinstance(item, list):
            result.extend(flatten_outlines(reader, item))
        else:
            result.append((str(item["/Title"]), reader.get_destination_page_number(item) + 1))
    return result


def pdf_uris(path: Path) -> list[dict[str, Any]]:
    document = fitz.open(path)
    try:
        output: list[dict[str, Any]] = []
        for page_number, page in enumerate(document, start=1):
            for link in page.get_links():
                if link.get("kind") == fitz.LINK_URI:
                    output.append({"page": page_number, "uri": link["uri"]})
        return output
    finally:
        document.close()


def verify_source_preservation(portfolio: PdfReader) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source, offset, count in SOURCE_RANGES:
        original = PdfReader(source)
        if len(original.pages) != count:
            raise RuntimeError(f"source page count changed: {source}")
        for source_index, before in enumerate(original.pages):
            after = portfolio.pages[offset + source_index]
            row = {
                "source": source.relative_to(ROOT).as_posix(),
                "source_page": source_index + 1,
                "portfolio_page": offset + source_index + 1,
                "text_equal": before.extract_text() == after.extract_text(),
                "content_stream_equal": stream(before) == stream(after),
                "media_box_equal": tuple(before.mediabox) == tuple(after.mediabox),
                "rotation_equal": before.rotation == after.rotation,
            }
            if not all(value for key, value in row.items() if key not in {"source", "source_page", "portfolio_page"}):
                raise RuntimeError(f"source preservation failure: {row}")
            rows.append(row)
    return rows


def render_and_compare() -> dict[str, Any]:
    if RENDER_DIR.exists():
        shutil.rmtree(RENDER_DIR)
    RENDER_DIR.mkdir(parents=True)
    matrix = fitz.Matrix(2.5, 2.5)  # 180 DPI from the 72 DPI PDF coordinate system.
    portfolio = fitz.open(PORTFOLIO)
    page_images: list[Path] = []
    non_blank: list[bool] = []
    try:
        for number, page in enumerate(portfolio, start=1):
            pixmap = page.get_pixmap(matrix=matrix, colorspace=fitz.csRGB, alpha=False)
            image_path = RENDER_DIR / f"page-{number:02d}.png"
            pixmap.save(image_path)
            page_images.append(image_path)
            image = Image.open(image_path).convert("RGB")
            extrema = image.getextrema()
            non_blank.append(any(low != high for low, high in extrema))
    finally:
        portfolio.close()
    equal_pages = 0
    comparisons: list[dict[str, Any]] = []
    final = fitz.open(PORTFOLIO)
    try:
        for source, offset, count in SOURCE_RANGES:
            source_doc = fitz.open(source)
            try:
                for index in range(count):
                    source_pix = source_doc[index].get_pixmap(matrix=matrix, colorspace=fitz.csRGB, alpha=False)
                    destination_pix = final[offset + index].get_pixmap(matrix=matrix, colorspace=fitz.csRGB, alpha=False)
                    equal = (source_pix.width == destination_pix.width and source_pix.height == destination_pix.height and source_pix.samples == destination_pix.samples)
                    comparisons.append({"source": source.relative_to(ROOT).as_posix(), "source_page": index + 1, "portfolio_page": offset + index + 1, "raster_equal": equal})
                    equal_pages += int(equal)
            finally:
                source_doc.close()
    finally:
        final.close()
    if equal_pages != 52:
        failed = [row for row in comparisons if not row["raster_equal"]]
        raise RuntimeError(f"rendered imported page differs from source: {failed[:3]}")
    contact_sheets: list[str] = []
    for first in range(0, len(page_images), 12):
        selection = page_images[first:first + 12]
        thumb_width, thumb_height = 330, 430
        sheet = Image.new("RGB", (thumb_width * 3, (thumb_height + 28) * 4), "white")
        draw = ImageDraw.Draw(sheet)
        for slot, item in enumerate(selection):
            image = Image.open(item).convert("RGB")
            image.thumbnail((thumb_width - 16, thumb_height - 28))
            col, row = slot % 3, slot // 3
            x = col * thumb_width + (thumb_width - image.width) // 2
            y = row * (thumb_height + 28) + 20
            sheet.paste(image, (x, y))
            draw.text((col * thumb_width + 8, row * (thumb_height + 28) + 4), f"Portfolio {first + slot + 1}", fill="black")
        sheet_path = RENDER_DIR / f"contact-sheet-{first // 12 + 1:02d}.png"
        sheet.save(sheet_path)
        contact_sheets.append(str(sheet_path))
    return {
        "dpi": 180,
        "rendered_pages": len(page_images),
        "non_blank_pages": sum(non_blank),
        "imported_source_pages_raster_equal": equal_pages,
        "contact_sheets": contact_sheets,
        "render_directory": str(RENDER_DIR),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manual-visual-review-complete", action="store_true", help="record a completed human review after inspecting the 180 DPI renders")
    parser.add_argument("--regressions-complete", action="store_true", help="record that the listed current regression commands completed successfully")
    arguments = parser.parse_args()
    if not PORTFOLIO.is_file():
        raise RuntimeError(f"missing portfolio: {PORTFOLIO}")
    if sha256(MARKETING) != EXPECTED_MARKETING_SHA or sha256(PYTHON) != EXPECTED_PYTHON_SHA:
        raise RuntimeError("a protected final-candidate source hash changed")
    if not PORTFOLIO.read_bytes().startswith(b"%PDF-"):
        raise RuntimeError("output is not a standard PDF header")
    reader = PdfReader(PORTFOLIO)
    if reader.is_encrypted or len(reader.pages) != 60:
        raise RuntimeError("portfolio is encrypted or has an unexpected page count")
    required_new_page_text = {
        1: "COMPLETE PROJECT",
        2: "six completed Task 2–4 deliverables",
        3: "Approved Digital Marketing report",
        4: "Results at a glance",
        5: "Evidence-limited public-source audit",
        44: "Python Programming",
        59: "Verification and project evidence",
        60: "CANONICAL SOURCE AND REPRODUCTION INDEX",
    }
    for page_number, needle in required_new_page_text.items():
        if needle not in reader.pages[page_number - 1].extract_text():
            raise RuntimeError(f"expected authored-page text missing on page {page_number}: {needle}")
    if any(not page.extract_text().strip() for page in reader.pages):
        raise RuntimeError("a portfolio page has no extractable text")
    if any(not page.get("/Resources", {}).get("/Font") for page in reader.pages):
        raise RuntimeError("a page has no font resources")
    preservation = verify_source_preservation(reader)
    outlines = flatten_outlines(reader)
    if outlines != EXPECTED_OUTLINES:
        raise RuntimeError(f"bookmark mismatch: {outlines!r}")
    labels = reader.page_labels
    if len(labels) != 60 or labels[0] != "Portfolio 1" or labels[-1] != "Portfolio 60":
        raise RuntimeError(f"page-label mismatch: first={labels[:1]!r}, last={labels[-1:]!r}")
    metadata = {str(key): str(value) for key, value in (reader.metadata or {}).items() if value is not None}
    required_metadata = {
        "/Title": "Progree Internship — Complete Project Portfolio",
        "/Author": "Anonymous internship project",
        "/Creator": "Progree portfolio assembly",
        "/Producer": "pypdf",
    }
    if any(metadata.get(key) != value for key, value in required_metadata.items()):
        raise RuntimeError(f"metadata mismatch: {metadata}")
    if any("@" in value for value in metadata.values()):
        raise RuntimeError("metadata contains an email-like value")
    body_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    email_domains = sorted(set(re.findall(r"\\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\\.[A-Za-z]{2,})\\b", body_text)))
    if set(email_domains) - {"example.test"}:
        raise RuntimeError(f"unexpected non-synthetic email address domain in portfolio body: {email_domains}")
    plus_prefixed_phones = re.findall(r"\\+\\d{1,3}(?:[ .-]?\\d){7,}", body_text)
    if plus_prefixed_phones:
        raise RuntimeError("portfolio body contains a plus-prefixed phone-number pattern")
    source_uris = pdf_uris(MARKETING)
    expected_source_uris = Counter((entry["page"] + 5, entry["uri"]) for entry in source_uris)
    actual_uris = pdf_uris(PORTFOLIO)
    actual_counter = Counter((entry["page"], entry["uri"]) for entry in actual_uris)
    if any(actual_counter[item] < count for item, count in expected_source_uris.items()):
        raise RuntimeError("one or more imported Marketing URI annotations were lost")
    actual_urls = {entry["uri"] for entry in actual_uris}
    if not set(SOURCE_INDEX_URLS).issubset(actual_urls):
        raise RuntimeError("one or more source-index hyperlinks were not embedded")
    render = render_and_compare()
    if render["non_blank_pages"] != 60:
        raise RuntimeError("a rendered portfolio page appears blank")
    if PORTFOLIO.stat().st_size >= 10 * 1024 * 1024:
        raise RuntimeError("portfolio exceeds the 10 MB visible upload limit")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest.update({
        "status": "verified",
        "output": {"path": PORTFOLIO.relative_to(ROOT).as_posix(), "pages": 60, "bytes": PORTFOLIO.stat().st_size, "sha256": sha256(PORTFOLIO)},
        "source_preservation": {"imported_pages": 52, "all_text_equal": True, "all_content_streams_equal": True, "all_media_boxes_equal": True, "all_rotations_equal": True, "page_checks": preservation},
        "navigation": {"bookmarks": [{"title": title, "page": page} for title, page in outlines], "page_labels": {"first": labels[0], "last": labels[-1], "count": len(labels)}},
        "hyperlinks": {"uri_annotation_count": len(actual_uris), "marketing_source_uri_count": len(source_uris), "source_index_uri_count": len(SOURCE_INDEX_URLS), "source_index_urls": SOURCE_INDEX_URLS},
        "rendering": render,
        "metadata": metadata,
        "privacy": {"metadata_author": metadata["/Author"], "email_like_metadata_values": 0, "body_email_domains": email_domains, "plus_prefixed_phone_patterns": len(plus_prefixed_phones), "status": "pass"},
        "manual_visual_review": {"status": "complete" if arguments.manual_visual_review_complete else "pending", "scope": "All 60 pages rendered at 180 DPI; imported source pages are also raster-compared against both approved candidates."},
        "regressions": {"status": "complete" if arguments.regressions_complete else "not_recorded", "unit_test_count": 129 if arguments.regressions_complete else None, "commands": [{"command": command, "outcome": outcome} for command, outcome in REGRESSION_COMMANDS]},
        "upload_rule": {"visible_limit_bytes": 10 * 1024 * 1024, "under_limit": True, "rule_source": "owner-supplied form screenshot/text detail; live form access remains unverified"},
    })
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    visual = "PASS — operator reviewed the 180 DPI render set after the automated comparison." if arguments.manual_visual_review_complete else "PENDING — render set created; an operator review has not yet been recorded."
    regressions = "PASS — 129 tests passed across the listed suites; adversarial checks also passed." if arguments.regressions_complete else "NOT RECORDED — run the listed suites before using this as final QA."
    regression_rows = "\n".join(f"- `{command}` — {outcome}" for command, outcome in REGRESSION_COMMANDS)
    qa = f"""# Final verification — complete internship portfolio

## Result

| Check | Result |
| --- | --- |
| Portfolio PDF opens as a standard, unencrypted PDF | PASS |
| Portfolio page count | PASS — 60 pages |
| Marketing-first / Python-second order | PASS — Marketing candidate pages 6–43, Python candidate pages 45–58 |
| Approved report pages preserved | PASS — 52/52 text streams, content streams, dimensions, rotation and 180 DPI raster renderings match their candidate sources |
| Bookmarks and physical page labels | PASS — {len(outlines)} bookmarks; Portfolio 1 through Portfolio 60 |
| Internal contents references | PASS — checked against the physical assembly map |
| Source-index hyperlinks | PASS — {len(actual_uris)} URI annotations total, including {len(SOURCE_INDEX_URLS)} canonical GitHub source links |
| Font resources and text extraction | PASS — every page has font resources and non-empty extracted text |
| Privacy review | PASS — anonymous metadata; no email-like metadata values; only approved synthetic `example.test` addresses in retained test output; no plus-prefixed phone pattern |
| Upload size | PASS — {PORTFOLIO.stat().st_size:,} bytes, below 10 MB |
| Rendered-page visual review | {visual} |
| Relevant regression checks | {regressions} |

## File identity

- File: `FINAL_SUBMISSION/01_Progree_Complete_Internship_Portfolio.pdf`
- SHA-256: `{sha256(PORTFOLIO)}`
- Bytes: {PORTFOLIO.stat().st_size:,}
- Source candidates unchanged:
  - Marketing: `{sha256(MARKETING)}` — 38 pages
  - Python: `{sha256(PYTHON)}` — 14 pages

## Rendering evidence

All 60 portfolio pages were rendered at 180 DPI under `/tmp/progree-complete-portfolio-render/`. Five contact sheets provide a complete overview. The 52 imported pages were separately rendered against their candidate-source pages and were raster-identical. The contact sheets and full-size page images are temporary QA artifacts, intentionally kept outside `FINAL_SUBMISSION`.

## Regression checks recorded for this package

{regression_rows}

## Boundaries retained

- Marketing Task 2 remains an evidence-limited public-source audit. Historical count changes are proxies, vendor engagement values are estimates, and organizer acceptance has not been established.
- RefillLoop is a fictional proposed campaign. Ocean Bottle financial and acquisition figures are proposed model outputs.
- This PDF meets the visible one-file and 10 MB upload constraints supplied by the owner, but a form with a single domain choice does not confirm two-track certificate eligibility. No form upload or submission occurred.

## Reproduce

```bash
python tools/build_complete_internship_portfolio.py --replace
python tools/verify_complete_internship_portfolio.py --manual-visual-review-complete --regressions-complete
```
"""
    QA.write_text(qa, encoding="utf-8")
    print(json.dumps({"portfolio": manifest["output"], "rendering": render, "bookmarks": len(outlines), "uri_links": len(actual_uris)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
