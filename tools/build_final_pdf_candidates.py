#!/usr/bin/env python3
"""Build navigation-only final PDF candidates without changing approved inputs.

The candidates import every original page as a PDF page object.  They add only
document-level outlines/page labels and, for the Marketing report, URI
annotations over exact visible public URLs.  The script validates that every
page's extracted text, content stream and dimensions match its input before it
publishes a candidate.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import fitz
from pypdf import PdfReader, PdfWriter
from pypdf.constants import PageLabelStyle


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence/ultimate_final_review"
MARKETING_SOURCE = ROOT / "digital_marketing/deliverables/Progree_Digital_Marketing_Tasks_2_3_4_COMBINED_REVIEW.pdf"
MARKETING_CANDIDATE = ROOT / "digital_marketing/deliverables/Progree_Digital_Marketing_Tasks_2_3_4_FINAL_CANDIDATE.pdf"
PYTHON_SOURCE = ROOT / "deliverables/Progree_Python_Tasks_2_3_4.pdf"
PYTHON_CANDIDATE = ROOT / "deliverables/Progree_Python_Tasks_2_3_4_FINAL_CANDIDATE.pdf"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def contents(page: Any) -> bytes:
    stream = page.get_contents()
    return stream.get_data() if stream is not None else b""


def copy_with_navigation(
    source: Path,
    target: Path,
    outlines: list[tuple[str, int]],
    labels: list[tuple[int, int, str]],
    title: str,
    subject: str,
) -> None:
    reader = PdfReader(source)
    writer = PdfWriter()
    writer.append(reader, import_outline=False)
    for title, page_number in outlines:
        writer.add_outline_item(title, page_number)
    for first, last, prefix in labels:
        writer.set_page_label(first, last, PageLabelStyle.DECIMAL, prefix=prefix, start=1)
    original_metadata = {
        str(key): str(value)
        for key, value in (reader.metadata or {}).items()
        if value is not None
    }
    original_metadata["/Title"] = title
    original_metadata["/Subject"] = subject
    original_metadata["/Creator"] = "Progree ultimate final-audit navigation enhancement"
    original_metadata["/Producer"] = "pypdf"
    writer.add_metadata(original_metadata)
    with target.open("wb") as output:
        writer.write(output)


MARKETING_LINKS = (
    # (zero-indexed page, exact visible text, destination URI, hit number)
    (5, "https://www.stanley1913.com/", "https://www.stanley1913.com/", 0),
    (5, "https://www.hydroflask.com/", "https://www.hydroflask.com/", 0),
    (5, "https://owalalife.com/", "https://owalalife.com/", 0),
    # The first exact root URL on the site-observation page is the homepage.
    # Two other long URLs on that page wrap across drawn text fragments and are
    # omitted rather than linked with inferred rectangles.  The FAQ string has
    # one exact rectangle, so it is safe to annotate.
    (26, "https://oceanbottle.co/", "https://oceanbottle.co/", 0),
    (26, "https://oceanbottle.co/pages/faqs", "https://oceanbottle.co/pages/faqs", 0),
    (28, "https://oceanbottle.co/products/original-bottle", "https://oceanbottle.co/products/original-bottle", 0),
    (28, "https://oceanbottle.co/pages/ocean-impact", "https://oceanbottle.co/pages/ocean-impact", 0),
    (28, "https://oceanbottle.co/pages/faqs", "https://oceanbottle.co/pages/faqs", 0),
    (28, "https://oceanbottle.co/blogs/news", "https://oceanbottle.co/blogs/news", 0),
    (31, "https://www.bcorporation.net/en-us/find-a-b-corp/company/ocean-bottle/", "https://www.bcorporation.net/en-us/find-a-b-corp/company/ocean-bottle/", 0),
    (31, "https://www.linkedin.com/company/the-ocean-bottle/", "https://www.linkedin.com/company/the-ocean-bottle/", 0),
)


def set_candidate_metadata(document: fitz.Document, title: str, subject: str) -> None:
    metadata = document.metadata
    # PyMuPDF serializes a missing pypdf author as the literal "NullObject".
    # Use the approved anonymous project descriptor instead of that artifact.
    metadata["author"] = "Anonymous internship project"
    metadata["title"] = title
    metadata["subject"] = subject
    metadata["creator"] = "Progree ultimate final-audit navigation enhancement"
    metadata["producer"] = "pypdf"
    document.set_metadata(metadata)


def add_verified_marketing_links(path: Path, target: Path, title: str, subject: str) -> list[dict[str, Any]]:
    document = fitz.open(path)
    recorded: list[dict[str, Any]] = []
    try:
        for page_index, visible_text, uri, hit_number in MARKETING_LINKS:
            page = document[page_index]
            hits = page.search_for(visible_text)
            if len(hits) != 1 and not (visible_text == "https://oceanbottle.co/" and hit_number == 0 and len(hits) == 4):
                raise RuntimeError(
                    f"expected exactly one reliable rectangle for {visible_text!r} on page {page_index + 1}; found {len(hits)}"
                )
            rectangle = hits[hit_number]
            page.insert_link({"kind": fitz.LINK_URI, "from": rectangle, "uri": uri})
            recorded.append(
                {
                    "page": page_index + 1,
                    "visible_text": visible_text,
                    "uri": uri,
                    "rectangle": [round(value, 2) for value in rectangle],
                }
            )
        set_candidate_metadata(document, title, subject)
        document.save(target, garbage=0, deflate=False)
    finally:
        document.close()
    return recorded


def outline_entries(reader: PdfReader) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in reader.outline:
        result.append({"title": item["/Title"], "page": reader.get_destination_page_number(item) + 1})
    return result


def validate(source: Path, candidate: Path, expected_outlines: list[tuple[str, int]], expected_links: list[dict[str, Any]] | None) -> dict[str, Any]:
    original = PdfReader(source)
    enhanced = PdfReader(candidate)
    if len(original.pages) != len(enhanced.pages):
        raise RuntimeError("candidate page count changed")
    checks: list[dict[str, Any]] = []
    for index, (before, after) in enumerate(zip(original.pages, enhanced.pages), start=1):
        check = {
            "page": index,
            "text_equal": before.extract_text() == after.extract_text(),
            "content_stream_equal": contents(before) == contents(after),
            "media_box_equal": tuple(before.mediabox) == tuple(after.mediabox),
            "rotation_equal": before.rotation == after.rotation,
        }
        if not all(value for key, value in check.items() if key != "page"):
            raise RuntimeError(f"candidate changed source page {index}: {check}")
        checks.append(check)
    actual_outlines = outline_entries(enhanced)
    wanted_outlines = [{"title": title, "page": page + 1} for title, page in expected_outlines]
    if actual_outlines != wanted_outlines:
        raise RuntimeError(f"outline mismatch: {actual_outlines!r}")
    links: list[dict[str, Any]] = []
    fitz_document = fitz.open(candidate)
    try:
        for page_number, page in enumerate(fitz_document, start=1):
            for link in page.get_links():
                if link.get("kind") == fitz.LINK_URI:
                    links.append({"page": page_number, "uri": link["uri"]})
    finally:
        fitz_document.close()
    wanted_links = [] if expected_links is None else [
        {"page": item["page"], "uri": item["uri"]} for item in expected_links
    ]
    if sorted(links, key=lambda item: (item["page"], item["uri"])) != sorted(wanted_links, key=lambda item: (item["page"], item["uri"])):
        raise RuntimeError(f"URI annotation mismatch: {links!r}")
    return {
        "source": source.relative_to(ROOT).as_posix(),
        "candidate": candidate.relative_to(ROOT).as_posix(),
        "page_count": len(enhanced.pages),
        "bytes": candidate.stat().st_size,
        "sha256": sha256(candidate),
        "all_text_equal": True,
        "all_content_streams_equal": True,
        "all_page_dimensions_equal": True,
        "page_checks": checks,
        "outlines": actual_outlines,
        "uri_links": links,
    }


def build_marketing() -> dict[str, Any]:
    title = "Progree Digital Marketing & Branding — Tasks 2–4 Final Candidate"
    subject = "Navigation-enhanced final candidate; Task 2 remains evidence-limited and pending rubric acceptance"
    outlines = [
        ("Cover", 0),
        ("Contents", 1),
        ("Task 2 — Evidence-limited public-source audit", 2),
        ("Task 3 — RefillLoop proposed 30-day campaign", 6),
        ("Task 4 — Ocean Bottle proposed SEO strategy", 26),
        ("Task 4 supporting appendix — Proposed email workflows", 32),
    ]
    labels = [(0, 0, "Cover "), (1, 1, "Contents "), (2, 5, "Task 2 "), (6, 25, "Task 3 "), (26, 31, "Task 4 "), (32, 37, "Task 4 Appendix ")]
    with tempfile.TemporaryDirectory(prefix=".progree-marketing-candidate-", dir=MARKETING_CANDIDATE.parent) as temporary_directory:
        temporary = Path(temporary_directory)
        stage = temporary / "navigation.pdf"
        final = temporary / "final.pdf"
        copy_with_navigation(
            MARKETING_SOURCE,
            stage,
            outlines,
            labels,
            title,
            subject,
        )
        link_records = add_verified_marketing_links(stage, final, title, subject)
        os.replace(final, MARKETING_CANDIDATE)
    result = validate(MARKETING_SOURCE, MARKETING_CANDIDATE, outlines, link_records)
    result["link_annotation_details"] = link_records
    return result


def build_python() -> dict[str, Any]:
    title = "Progree Python Tasks 2, 3 and 4 — Final Candidate"
    subject = "Navigation-enhanced final candidate; approved report content preserved"
    outlines = [
        ("Cover", 0),
        ("Executive summary", 1),
        ("Task 2 — Fibonacci sequence and timing", 2),
        ("Task 3 — Safe file organisation and extraction", 5),
        ("Task 4 — Rule-based support chatbot", 8),
        ("Cross-task QA", 11),
        ("Conclusion", 12),
        ("Appendix", 13),
    ]
    labels = [(0, 0, "Cover "), (1, 1, "Summary "), (2, 4, "Task 2 "), (5, 7, "Task 3 "), (8, 10, "Task 4 "), (11, 11, "QA "), (12, 12, "Conclusion "), (13, 13, "Appendix ")]
    with tempfile.TemporaryDirectory(prefix=".progree-python-candidate-", dir=PYTHON_CANDIDATE.parent) as temporary_directory:
        stage = Path(temporary_directory) / "navigation.pdf"
        final = Path(temporary_directory) / "final.pdf"
        copy_with_navigation(
            PYTHON_SOURCE,
            stage,
            outlines,
            labels,
            title,
            subject,
        )
        document = fitz.open(stage)
        try:
            set_candidate_metadata(document, title, subject)
            document.save(final, garbage=0, deflate=False)
        finally:
            document.close()
        os.replace(final, PYTHON_CANDIDATE)
    return validate(PYTHON_SOURCE, PYTHON_CANDIDATE, outlines, [])


def main() -> None:
    if not MARKETING_SOURCE.is_file() or not PYTHON_SOURCE.is_file():
        raise SystemExit("approved source PDF missing")
    before_hashes = {"marketing": sha256(MARKETING_SOURCE), "python": sha256(PYTHON_SOURCE)}
    report = {"schema": "progree-final-candidate-build-v1", "marketing": build_marketing(), "python": build_python()}
    after_hashes = {"marketing": sha256(MARKETING_SOURCE), "python": sha256(PYTHON_SOURCE)}
    if before_hashes != after_hashes:
        raise RuntimeError("a protected source PDF changed while candidates were built")
    report["protected_source_hashes_unchanged"] = before_hashes == after_hashes
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "candidate_build.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
