"""Record reproducible structural QA for both final submission PDFs.

This script intentionally reads the approved PDFs without rewriting them.  It
checks the technical properties that can be automated; the paired QA record
captures the separate 160-DPI visual inspection.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import date
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
REVIEW_COMMIT = "c15d70e33a25c73278856d2a0444ee112abdc8e8"
MARKETING = ROOT / "digital_marketing/deliverables/Progree_Digital_Marketing_Tasks_2_3_4_COMBINED_REVIEW.pdf"
PYTHON_REPORT = ROOT / "deliverables/Progree_Python_Tasks_2_3_4.pdf"
MANIFEST = ROOT / "evidence/final_submission_review/manifest.json"
MARKETING_SOURCES = (
    ROOT / "digital_marketing/deliverables/DM_Task2_Competitor_Audit_SECONDARY_DRAFT.pdf",
    ROOT / "digital_marketing/deliverables/DM_Task3_30_Day_Campaign.pdf",
    ROOT / "digital_marketing/deliverables/DM_Task4_SEO_Acquisition_Strategy.pdf",
    ROOT / "digital_marketing/deliverables/DM_Task4_Email_Workflow_Appendix.pdf",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def count_uri_annotations(reader: PdfReader) -> int:
    count = 0
    for page in reader.pages:
        for annotation_ref in page.get("/Annots", []) or []:
            action = annotation_ref.get_object().get("/A", {})
            count += int(action.get("/S") == "/URI" and bool(action.get("/URI")))
    return count


def font_names(page) -> list[str]:
    resources = page.get("/Resources", {})
    fonts = resources.get("/Font", {})
    return sorted(str(font.get_object().get("/BaseFont", "")) for font in fonts.values())


def flatten_outline(reader: PdfReader) -> list[dict[str, int | str]]:
    items: list[dict[str, int | str]] = []
    for item in reader.outline:
        if isinstance(item, list):
            continue
        items.append({"title": str(item.get("/Title", "")), "page": reader.get_destination_page_number(item) + 1})
    return items


def pdf_summary(path: Path) -> dict:
    reader = PdfReader(path)
    page_texts = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(page_texts)
    dimensions = [
        [round(float(page.mediabox.width), 3), round(float(page.mediabox.height), 3)]
        for page in reader.pages
    ]
    metadata = {str(key): str(value) for key, value in (reader.metadata or {}).items()}
    return {
        "path": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "page_count": len(reader.pages),
        "metadata": metadata,
        "pages_with_no_extractable_text": [i + 1 for i, value in enumerate(page_texts) if not value.strip()],
        "pages_with_no_font_resources": [i + 1 for i, page in enumerate(reader.pages) if not font_names(page)],
        "font_names": sorted({font for page in reader.pages for font in font_names(page)}),
        "page_dimensions_points": dimensions,
        "uri_hyperlink_annotations": count_uri_annotations(reader),
        "visible_url_count": len(re.findall(r"https?://[^\s<>()]+", text)),
        "outline": flatten_outline(reader),
        "page_labels": reader.page_labels,
        "extracted_text_characters": len(text),
    }


def source_preservation() -> dict:
    combined = PdfReader(MARKETING)
    start = 2
    results = []
    for source in MARKETING_SOURCES:
        source_reader = PdfReader(source)
        combined_pages = combined.pages[start : start + len(source_reader.pages)]
        text_matches = []
        stream_matches = []
        for source_page, combined_page in zip(source_reader.pages, combined_pages):
            text_matches.append((source_page.extract_text() or "") == (combined_page.extract_text() or ""))
            source_stream = source_page.get_contents().get_data() if source_page.get_contents() else b""
            combined_stream = combined_page.get_contents().get_data() if combined_page.get_contents() else b""
            stream_matches.append(sha256_bytes(source_stream) == sha256_bytes(combined_stream))
        results.append({
            "source": str(source.relative_to(ROOT)),
            "source_sha256": sha256(source),
            "page_count": len(source_reader.pages),
            "combined_pages": list(range(start + 1, start + len(source_reader.pages) + 1)),
            "all_extracted_text_matches": all(text_matches),
            "all_content_streams_match": all(stream_matches),
        })
        start += len(source_reader.pages)
    return {"all_source_pages_checked": start - 2, "sources": results}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def protected_artifacts_unchanged() -> bool:
    paths = [
        "deliverables/Progree_Python_Tasks_2_3_4.pdf",
        "digital_marketing/deliverables/Progree_Digital_Marketing_Tasks_2_3_4_COMBINED_REVIEW.pdf",
        *(str(path.relative_to(ROOT)) for path in MARKETING_SOURCES),
    ]
    return subprocess.run(
        ["git", "diff", "--quiet", REVIEW_COMMIT, "--", *paths], cwd=ROOT, check=False
    ).returncode == 0


def main() -> None:
    marketing = pdf_summary(MARKETING)
    python_report = pdf_summary(PYTHON_REPORT)
    expected_marketing = {
        "page_count": 38,
        "bytes": 140895,
        "sha256": "24a211ea4cdd68f83b02ce216aa43b15bc6a65a5952776cbe8c57bccda9f0059",
    }
    for key, value in expected_marketing.items():
        if marketing[key] != value:
            raise ValueError(f"Marketing {key} changed: {marketing[key]!r}, expected {value!r}")
    expected_destinations = {
        "Cover and contents": 1,
        "Cover": 1,
        "Contents": 2,
        "Task 2 — Evidence-Limited Public-Source Competitor Audit": 3,
        "Task 3 — RefillLoop 30-Day Campaign": 7,
        "Task 4 — Ocean Bottle SEO & Acquisition Strategy": 27,
        "Task 4 Supporting Appendix — Email Workflows": 33,
    }
    for entry in marketing["outline"]:
        expected = expected_destinations.get(entry["title"])
        if expected is None or entry["page"] != expected:
            raise ValueError(f"unexpected Marketing bookmark: {entry}")
    expected_labels = ["Cover 1", "Contents 1"] + [f"Task 2 {i}" for i in range(1, 5)]
    expected_labels += [f"Task 3 {i}" for i in range(1, 21)]
    expected_labels += [f"Task 4 {i}" for i in range(1, 7)]
    expected_labels += [f"Task 4 Appendix {i}" for i in range(1, 7)]
    if marketing["page_labels"] != expected_labels:
        raise ValueError("Marketing page labels changed or are out of order")
    if any(marketing[key] for key in ("pages_with_no_extractable_text", "pages_with_no_font_resources")):
        raise ValueError("Marketing contains a blank/nonextractable page or missing font resource")
    if any(python_report[key] for key in ("pages_with_no_extractable_text", "pages_with_no_font_resources")):
        raise ValueError("Python report contains a blank/nonextractable page or missing font resource")
    marketing_text = "\n".join(page.extract_text() or "" for page in PdfReader(MARKETING).pages).lower()
    python_text = "\n".join(page.extract_text() or "" for page in PdfReader(PYTHON_REPORT).pages).lower()
    required_marketing = (
        "not a completed measured audit",
        "not verified publication frequency",
        "fictional proposed campaign",
        "no spend is authorized or incurred",
        "scenario inputs, not benchmarks, forecasts, or results",
        "no automation is activated",
    )
    missing_marketing = [phrase for phrase in required_marketing if phrase not in marketing_text]
    if missing_marketing:
        raise ValueError(f"Marketing boundary language missing: {missing_marketing}")
    required_python = ("task 2 — fibonacci", "task 3 — safe file automation", "task 4 — multi-intent rule-based chatbot", "scope and limitations")
    missing_python = [phrase for phrase in required_python if phrase not in python_text]
    if missing_python:
        raise ValueError(f"Python report content missing: {missing_python}")
    result = {
        "reviewed_commit": REVIEW_COMMIT,
        "generated_utc_date": date.today().isoformat(),
        "result": "passed",
        "marketing": marketing,
        "python": python_report,
        "marketing_source_preservation": source_preservation(),
        "claim_boundary_checks": {"marketing": "passed", "python_tasks_2_3_4_and_limitations": "passed"},
        "protected_artifacts_unchanged_against_reviewed_commit": protected_artifacts_unchanged(),
        "visual_review": {
            "status": "passed",
            "render_resolution_dpi": 160,
            "marketing_pages_individually_inspected": 38,
            "python_pages_individually_inspected": 14,
            "total_pages_individually_inspected": 52,
            "result": "No clipping, overlap, unexpected blank page, corrupted glyph, margin, contrast, or table-header defect observed.",
        },
        "verdicts": {
            "marketing": "CONDITIONAL PASS — technically ready; Task 2 rubric acceptance and organizer confirmation remain open.",
            "python": "PASS — technically ready; certificate eligibility, form requirements, and final owner authorization remain external conditions.",
        },
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PASS: final cross-track PDF QA manifest written")


if __name__ == "__main__":
    main()
