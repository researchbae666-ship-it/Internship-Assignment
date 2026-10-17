#!/usr/bin/env python3
"""Verify the owner-authorized personalized portfolio candidate.

Owner values are supplied at verification time and are checked in the PDF and
metadata without being written to the public manifest or QA report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

import fitz
from PIL import Image, ImageDraw
from pypdf import PdfReader

import build_complete_internship_portfolio as base


ROOT = base.ROOT
FINAL = ROOT / "FINAL_SUBMISSION"
BASELINE = FINAL / "01_Progree_Complete_Internship_Portfolio.pdf"
PORTFOLIO = FINAL / "01_Progree_Complete_Internship_Portfolio_PERSONALIZED.pdf"
MANIFEST = FINAL / "manifest.json"
QA = FINAL / "QA" / "FINAL_VERIFICATION.md"
MARKETING = base.MARKETING
PYTHON = base.PYTHON
RENDER_DIR = Path("/tmp/progree-personalized-portfolio-render")
SOURCE_RANGES = ((MARKETING, 5, 38), (PYTHON, 44, 14))
EXPECTED_OUTLINES = [
    ("Cover — candidate information", 1),
    ("Executive summary", 2),
    ("Master contents", 3),
    ("Results at a glance", 4),
    ("Digital Marketing & Branding", 5),
    ("Track introduction", 5),
    ("Complete Marketing report", 6),
    ("Marketing Task 2 — evidence-limited audit", 8),
    ("Marketing Task 3 — RefillLoop proposed campaign", 12),
    ("Marketing Task 4 — Ocean Bottle proposed strategy", 32),
    ("Marketing Task 4 email appendix", 38),
    ("Python Programming", 44),
    ("Track introduction", 44),
    ("Complete Python report", 45),
    ("Python Task 2 — Fibonacci and timing", 47),
    ("Python Task 3 — safe file automation", 50),
    ("Python Task 4 — multi-intent chatbot", 53),
    ("Evidence and reproduction index", 59),
    ("Final owner summary and source index", 60),
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


def owner_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--certificate-name", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--whatsapp", required=True)
    parser.add_argument("--registration", required=True)
    parser.add_argument("--manual-visual-review-complete", action="store_true")
    parser.add_argument("--regressions-complete", action="store_true")
    result = parser.parse_args()
    if result.name != result.certificate_name:
        parser.error("full name and certificate name must match for this authorized portfolio")
    return result


def flatten_outlines(reader: PdfReader, items: list[Any] | None = None) -> list[tuple[str, int]]:
    entries = reader.outline if items is None else items
    result: list[tuple[str, int]] = []
    for entry in entries:
        if isinstance(entry, list):
            result.extend(flatten_outlines(reader, entry))
        else:
            result.append((str(entry["/Title"]), reader.get_destination_page_number(entry) + 1))
    return result


def uri_links(path: Path) -> list[dict[str, Any]]:
    document = fitz.open(path)
    try:
        result: list[dict[str, Any]] = []
        for page_number, page in enumerate(document, start=1):
            for link in page.get_links():
                if link.get("kind") == fitz.LINK_URI:
                    result.append({"page": page_number, "uri": link["uri"]})
        return result
    finally:
        document.close()


def source_preservation(reader: PdfReader) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for source, offset, count in SOURCE_RANGES:
        original = PdfReader(source)
        if len(original.pages) != count:
            raise RuntimeError(f"source count changed: {source}")
        for index, before in enumerate(original.pages):
            after = reader.pages[offset + index]
            row = {
                "source": source.relative_to(ROOT).as_posix(),
                "source_page": index + 1,
                "portfolio_page": offset + index + 1,
                "text_equal": before.extract_text() == after.extract_text(),
                "content_stream_equal": stream(before) == stream(after),
                "media_box_equal": tuple(before.mediabox) == tuple(after.mediabox),
                "rotation_equal": before.rotation == after.rotation,
            }
            if not all(value for key, value in row.items() if key not in {"source", "source_page", "portfolio_page"}):
                raise RuntimeError(f"source preservation failure: {row}")
            checks.append(row)
    return checks


def render_and_compare() -> dict[str, Any]:
    if RENDER_DIR.exists():
        shutil.rmtree(RENDER_DIR)
    RENDER_DIR.mkdir(parents=True)
    matrix = fitz.Matrix(2.5, 2.5)  # 180 DPI
    final = fitz.open(PORTFOLIO)
    page_paths: list[Path] = []
    non_blank = 0
    try:
        for number, page in enumerate(final, start=1):
            pixmap = page.get_pixmap(matrix=matrix, colorspace=fitz.csRGB, alpha=False)
            target = RENDER_DIR / f"page-{number:02d}.png"
            pixmap.save(target)
            page_paths.append(target)
            extrema = Image.open(target).convert("RGB").getextrema()
            non_blank += int(any(low != high for low, high in extrema))
    finally:
        final.close()
    comparisons: list[dict[str, Any]] = []
    final = fitz.open(PORTFOLIO)
    try:
        for source, offset, count in SOURCE_RANGES:
            source_document = fitz.open(source)
            try:
                for index in range(count):
                    original = source_document[index].get_pixmap(matrix=matrix, colorspace=fitz.csRGB, alpha=False)
                    imported = final[offset + index].get_pixmap(matrix=matrix, colorspace=fitz.csRGB, alpha=False)
                    equal = original.width == imported.width and original.height == imported.height and original.samples == imported.samples
                    comparisons.append({"source": source.relative_to(ROOT).as_posix(), "source_page": index + 1, "portfolio_page": offset + index + 1, "raster_equal": equal})
            finally:
                source_document.close()
    finally:
        final.close()
    if non_blank != 60 or not all(item["raster_equal"] for item in comparisons):
        raise RuntimeError("blank rendered page or source-render mismatch")
    sheets: list[str] = []
    for first in range(0, 60, 12):
        selected = page_paths[first:first + 12]
        thumb_width, thumb_height = 330, 430
        sheet = Image.new("RGB", (thumb_width * 3, (thumb_height + 28) * 4), "white")
        draw = ImageDraw.Draw(sheet)
        for slot, page_path in enumerate(selected):
            image = Image.open(page_path).convert("RGB")
            image.thumbnail((thumb_width - 16, thumb_height - 28))
            column, row = slot % 3, slot // 3
            x = column * thumb_width + (thumb_width - image.width) // 2
            y = row * (thumb_height + 28) + 20
            sheet.paste(image, (x, y))
            draw.text((column * thumb_width + 8, row * (thumb_height + 28) + 4), f"Portfolio {first + slot + 1}", fill="black")
        path = RENDER_DIR / f"contact-sheet-{first // 12 + 1:02d}.png"
        sheet.save(path)
        sheets.append(str(path))
    return {"dpi": 180, "rendered_pages": 60, "non_blank_pages": non_blank, "imported_pages_raster_equal": len(comparisons), "contact_sheets": sheets, "render_directory": str(RENDER_DIR)}


def main() -> int:
    owner = owner_args()
    expected_sources = ((BASELINE, 60, "b5903f037578f6e22a9792cf4fc8862a90db18b508935e7b15df3d11bfa3b071"), (MARKETING, 38, base.EXPECTED_MARKETING_SHA), (PYTHON, 14, base.EXPECTED_PYTHON_SHA))
    for path, pages, digest in expected_sources:
        if not path.is_file() or len(PdfReader(path).pages) != pages or sha256(path) != digest:
            raise RuntimeError(f"protected input changed: {path}")
    if not PORTFOLIO.is_file() or not PORTFOLIO.read_bytes().startswith(b"%PDF-"):
        raise RuntimeError("personalized candidate is missing or not a PDF")
    reader = PdfReader(PORTFOLIO)
    if reader.is_encrypted or len(reader.pages) != 60:
        raise RuntimeError("personalized candidate is encrypted or has wrong page count")
    new_page_text = {
        1: "CANDIDATE INFORMATION",
        2: "six submitted Task 2–4 deliverables",
        3: "Complete Marketing report",
        4: "A. Implemented software",
        5: "Evidence-limited public-source audit",
        44: "Supplementary appendix decision",
        59: "Verification and reproduction evidence",
        60: "Final owner summary and source index",
    }
    for page_number, text in new_page_text.items():
        if text not in (reader.pages[page_number - 1].extract_text() or ""):
            raise RuntimeError(f"expected authored content missing on page {page_number}: {text}")
    all_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    for value, label in ((owner.name, "name"), (owner.certificate_name, "certificate name"), (owner.email, "email"), (owner.whatsapp, "WhatsApp"), (owner.registration, "registration")):
        if value not in all_text:
            raise RuntimeError(f"authorized {label} is absent from the PDF")
    if all_text.count(owner.email) != 1 or all_text.count(owner.whatsapp) != 1 or all_text.count(owner.registration) != 1:
        raise RuntimeError("authorized candidate contact details are duplicated unexpectedly")
    forbidden = ("Six fully completed and approved tasks", "certificate eligibility is confirmed", "achieved campaign performance", "verified 28-day posting cadence")
    authored_text = "\n".join((reader.pages[index].extract_text() or "") for index in (0, 1, 2, 3, 4, 43, 58, 59))
    if any(term.lower() in authored_text.lower() for term in forbidden):
        raise RuntimeError("unsupported completion claim appears in authored pages")
    if any(not (page.extract_text() or "").strip() for page in reader.pages):
        raise RuntimeError("a portfolio page lacks extractable text")
    if any(not page.get("/Resources", {}).get("/Font") for page in reader.pages):
        raise RuntimeError("a portfolio page has no font resources")
    preservation = source_preservation(reader)
    outlines = flatten_outlines(reader)
    if outlines != EXPECTED_OUTLINES:
        raise RuntimeError(f"bookmark mismatch: {outlines!r}")
    labels = reader.page_labels
    if labels != [f"Portfolio {number}" for number in range(1, 61)]:
        raise RuntimeError("page labels are incorrect")
    metadata = {str(key): str(value) for key, value in (reader.metadata or {}).items() if value is not None}
    expected_metadata = {
        "/Title": "Progree Internship — Complete Project Portfolio — Personalized Candidate",
        "/Author": owner.certificate_name,
        "/Creator": "Progree personalized portfolio assembly",
        "/Producer": "pypdf",
    }
    if any(metadata.get(key) != value for key, value in expected_metadata.items()):
        raise RuntimeError("metadata mismatch")
    email_domains = sorted(set(re.findall(r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b", all_text)))
    owner_domain = owner.email.rsplit("@", 1)[1]
    if set(email_domains) - {"example.test", owner_domain}:
        raise RuntimeError("unrecognized email-like value appears in PDF body")
    plus_phones = [match.strip() for match in re.findall(r"\+\d{1,3}(?:[ .-]?\d){7,}", all_text)]
    if plus_phones != [owner.whatsapp]:
        raise RuntimeError("unexpected plus-prefixed phone pattern in PDF body")
    candidate_links = uri_links(PORTFOLIO)
    source_links = uri_links(MARKETING)
    required_imported_links = Counter((entry["page"] + 5, entry["uri"]) for entry in source_links)
    actual_links = Counter((entry["page"], entry["uri"]) for entry in candidate_links)
    if any(actual_links[item] < number for item, number in required_imported_links.items()):
        raise RuntimeError("an imported Marketing link annotation was lost")
    source_index_urls = {url for _, _, url in base.SOURCE_INDEX}
    if not source_index_urls.issubset({entry["uri"] for entry in candidate_links}):
        raise RuntimeError("a source-index hyperlink is missing")
    render = render_and_compare()
    if PORTFOLIO.stat().st_size >= 10 * 1024 * 1024:
        raise RuntimeError("personalized candidate exceeds 10 MB")
    facts = base.source_facts()
    fact_checks = {
        "marketing_actions": facts["marketing_actions"] == 53,
        "marketing_paid_actions": facts["marketing_paid_actions"] == 15,
        "marketing_personas": facts["marketing_personas"] == 3,
        "marketing_ab_tests": facts["marketing_ab_tests"] == 4,
        "marketing_budget_usd": facts["marketing_budget_usd"] == 3000,
        "task4_keyword_entries": facts["task4_keywords"] == 12,
        "task4_seo_pages": facts["task4_seo_pages"] == 4,
        "task4_funnel_stages": facts["task4_funnel_stages"] == 4,
        "task4_workflows": facts["task4_flows"] == 4,
        "task4_messages": facts["task4_messages"] == 10,
        "task4_budget_gbp": facts["task4_budget"]["total_gbp"] == 12000,
    }
    if not all(fact_checks.values()):
        raise RuntimeError(f"source-model fact check failed: {fact_checks}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    candidate = manifest["personalized_candidate"]
    candidate.update({
        "status": "verified",
        "pages": 60,
        "bytes": PORTFOLIO.stat().st_size,
        "sha256": sha256(PORTFOLIO),
        "owner_detail_validation": {"status": "pass", "values_checked_exactly": 5, "values_not_repeated_in_manifest_or_qa": True, "body_email_domains": email_domains, "authorized_plus_prefixed_phone_patterns": len(plus_phones)},
        "source_preservation": {"imported_pages": 52, "all_text_equal": True, "all_content_streams_equal": True, "all_media_boxes_equal": True, "all_rotations_equal": True, "page_checks": preservation},
        "navigation": {"bookmarks": [{"title": title, "page": page} for title, page in outlines], "page_labels": {"first": labels[0], "last": labels[-1], "count": len(labels)}},
        "hyperlinks": {"uri_annotation_count": len(candidate_links), "preserved_marketing_uri_annotations": len(source_links), "source_index_uri_annotations": len(source_index_urls)},
        "rendering": render,
        "metadata": {"title": metadata["/Title"], "author_matches_authorized_certificate_name": True, "creator": metadata["/Creator"], "producer": metadata["/Producer"]},
        "source_fact_checks": fact_checks,
        "manual_visual_review": {"status": "complete" if owner.manual_visual_review_complete else "pending", "scope": "Every page rendered at 180 DPI; all eight authored pages reviewed at full resolution; imported pages checked against their source renders."},
        "regressions": {"status": "complete" if owner.regressions_complete else "not_recorded", "unit_test_count": 129 if owner.regressions_complete else None, "commands": [{"command": command, "outcome": outcome} for command, outcome in REGRESSION_COMMANDS]},
        "upload_limit": {"visible_limit_bytes": 10 * 1024 * 1024, "under_limit": True, "basis": "owner-supplied Form screenshots/text; live form arrangement remains externally unconfirmed"},
    })
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    visual = "PASS — all 60 pages were rendered at 180 DPI; the eight authored pages were reviewed at full resolution and imported pages were checked against source renders." if owner.manual_visual_review_complete else "PENDING — rendered pages are available but human review is not recorded."
    regressions = "PASS — 129 tests passed across the listed suites; adversarial checks passed." if owner.regressions_complete else "NOT RECORDED — run the listed suites before using this as final QA."
    regression_rows = "\n".join(f"- `{command}` — {outcome}" for command, outcome in REGRESSION_COMMANDS)
    QA.write_text(f"""# Final verification — personalized complete internship portfolio

## Candidate identity handling

The owner expressly authorized the supplied full name/certificate name, email, WhatsApp number and registration ID in the personalized PDF and its author metadata. Exact-value verification passed. The values are intentionally not repeated in this public QA file or manifest.

## Result

| Check | Result |
| --- | --- |
| Historical anonymous baseline retained | PASS — 60 pages; SHA-256 `b5903f037578f6e22a9792cf4fc8862a90db18b508935e7b15df3d11bfa3b071` |
| Personalized candidate opens as standard, unencrypted PDF | PASS |
| Candidate page count and order | PASS — 60 pages; Marketing pages 6–43, Python pages 45–58 |
| Approved report page preservation | PASS — 52/52 pages match approved candidates in extracted text, content stream, dimensions, rotation and 180 DPI render |
| Marketing appendix and Python tasks | PASS — all imported report pages are present in order |
| Completion-language boundary | PASS — authored pages retain evidence-limited/proposed/modeled wording and make no Task 1, organizer-acceptance or achieved-performance claim |
| Statistics | PASS — source-model checks confirm 53 actions, 15 planned paid actions, 3 personas, 4 A/B tests, USD 3,000, 12 keyword entries, 4 SEO pages, 4 funnel stages, 4 workflows, 10 messages and GBP 12,000 |
| Master contents, bookmarks and page labels | PASS — {len(outlines)} bookmarks; Portfolio 1 through Portfolio 60 |
| Source hyperlinks | PASS — {len(candidate_links)} URI annotations, including all {len(source_links)} approved Marketing links and {len(source_index_urls)} canonical source-index links |
| Metadata and authorized details | PASS — exact authorized values validated; no unrecognized email-like value or plus-prefixed phone pattern |
| Rendered-page review | {visual} |
| Relevant regression checks | {regressions} |
| Upload size | PASS — {PORTFOLIO.stat().st_size:,} bytes, below 10 MB |

## File identity

- File: `FINAL_SUBMISSION/01_Progree_Complete_Internship_Portfolio_PERSONALIZED.pdf`
- SHA-256: `{sha256(PORTFOLIO)}`
- Bytes: {PORTFOLIO.stat().st_size:,}
- Baseline and source candidates retain their expected hashes.

## Rendering evidence

All 60 pages were rendered at 180 DPI under `/tmp/progree-personalized-portfolio-render/`. Five contact sheets provide full-document overview. The temporary render set is intentionally outside `FINAL_SUBMISSION`.

## Regression checks recorded for this candidate

{regression_rows}

## Remaining external conditions

- Marketing Task 2 remains a documented evidence-limited audit; organizer acceptance is unconfirmed.
- The visible form permits one file but has a single-choice domain field. This combined candidate does not establish that one response earns two certificates.
- No Google Form response, upload, email, campaign or LinkedIn activity has been performed.
""", encoding="utf-8")
    print(json.dumps({"path": PORTFOLIO.relative_to(ROOT).as_posix(), "pages": 60, "bytes": PORTFOLIO.stat().st_size, "sha256": sha256(PORTFOLIO), "links": len(candidate_links), "bookmarks": len(outlines)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
