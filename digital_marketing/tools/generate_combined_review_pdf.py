"""Build and verify the anonymous combined Digital Marketing review PDF.

The approved task PDFs are read-only inputs.  This script creates only the
consolidated review copy, plus a machine-readable QA manifest.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.constants import PageLabelStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
DELIVERABLES = ROOT / "deliverables"
OUTPUT = DELIVERABLES / "Progree_Digital_Marketing_Tasks_2_3_4_COMBINED_REVIEW.pdf"
MANIFEST = ROOT / "evidence" / "final_submission" / "manifest.json"

SOURCES = (
    (
        "Task 2 — Evidence-Limited Public-Source Competitor Audit",
        DELIVERABLES / "DM_Task2_Competitor_Audit_SECONDARY_DRAFT.pdf",
        "Actual public-source and reviewer-supplied secondary evidence; cadence and engagement remain unavailable.",
    ),
    (
        "Task 3 — RefillLoop 30-Day Campaign",
        DELIVERABLES / "DM_Task3_30_Day_Campaign.pdf",
        "Fictional proposed campaign plan; no content was published and no media spend occurred.",
    ),
    (
        "Task 4 — Ocean Bottle SEO & Acquisition Strategy",
        DELIVERABLES / "DM_Task4_SEO_Acquisition_Strategy.pdf",
        "Modeled strategy; assumptions and scenario outputs are not measured results.",
    ),
    (
        "Task 4 Supporting Appendix — Email Workflows",
        DELIVERABLES / "DM_Task4_Email_Workflow_Appendix.pdf",
        "Proposed inactive email scripts and consent-aware workflow rules.",
    ),
)

NAVY = colors.HexColor("#12324A")
TEAL = colors.HexColor("#197D82")
INK = colors.HexColor("#1E2A32")
MIST = colors.HexColor("#EAF3F3")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def page_count(path: Path) -> int:
    return len(PdfReader(path).pages)


def draw_wrapped(c: canvas.Canvas, text: str, x: float, y: float, width: float, font: str, size: float, leading: float, color=INK) -> float:
    c.setFillColor(color)
    c.setFont(font, size)
    words = text.split()
    line = ""
    for word in words:
        candidate = (line + " " + word).strip()
        if stringWidth(candidate, font, size) > width and line:
            c.drawString(x, y, line)
            y -= leading
            line = word
        else:
            line = candidate
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


def build_front_matter(output: Path, source_pages: list[int]) -> None:
    c = canvas.Canvas(str(output), pagesize=A4)
    width, height = A4
    c.setTitle("Progree Digital Marketing & Branding — Tasks 2–4 Review Copy")
    c.setAuthor("Anonymous internship project")
    c.setSubject("Consolidated review copy; Task 2 remains evidence-limited and pending rubric acceptance")
    c.setCreator("Progree final-submission preparation")
    c.setFillColor(NAVY)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(width / 2, height - 78 * mm, "PROGREE")
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 94 * mm, "DIGITAL MARKETING & BRANDING")
    c.setFont("Helvetica", 13)
    c.drawCentredString(width / 2, height - 106 * mm, "Tasks 2, 3 and 4 — consolidated review copy")
    c.setStrokeColor(TEAL)
    c.setLineWidth(2)
    c.line(45 * mm, height - 116 * mm, width - 45 * mm, height - 116 * mm)
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, height - 132 * mm, "Reporting period: October 2026")
    c.drawCentredString(width / 2, height - 140 * mm, "Prepared for final independent PDF and submission review")
    c.setFont("Helvetica-Oblique", 8.5)
    c.drawCentredString(width / 2, 40 * mm, "Anonymous review document. It contains no personal identity information.")
    c.showPage()

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(25 * mm, height - 35 * mm, "Contents")
    c.setStrokeColor(TEAL)
    c.setLineWidth(1.2)
    c.line(25 * mm, height - 41 * mm, width - 25 * mm, height - 41 * mm)
    entries = [
        ("Cover", 1, "Anonymous title and reporting period"),
        ("Contents", 2, "Task navigation and evidence boundaries"),
    ]
    page = 3
    for (title, _path, description), pages in zip(SOURCES, source_pages):
        entries.append((title, page, description))
        page += pages
    y = height - 58 * mm
    for title, display_page, description in entries:
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(25 * mm, y, title)
        c.drawRightString(width - 25 * mm, y, str(display_page))
        y -= 5.5 * mm
        y = draw_wrapped(c, description, 29 * mm, y, width - 54 * mm, "Helvetica", 8.5, 4.4 * mm, INK)
        y -= 4.8 * mm
    c.setFillColor(MIST)
    c.roundRect(25 * mm, 25 * mm, width - 50 * mm, 28 * mm, 3 * mm, fill=1, stroke=0)
    c.setFillColor(INK)
    draw_wrapped(
        c,
        "Review status: Task 2 is an evidence-limited public-source audit and remains pending organizer acceptance of rubric coverage. Organizer confirmation and final user authorization are also pending. Tasks 3 and 4 are proposed or modeled work, not live campaign results.",
        30 * mm,
        46 * mm,
        width - 60 * mm,
        "Helvetica",
        8.3,
        4.2 * mm,
    )
    c.save()


def pdf_text(path: Path) -> str:
    return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)


def page_fonts(page) -> set[str]:
    resources = page.get("/Resources", {})
    fonts = resources.get("/Font", {})
    return {str(font.get_object().get("/BaseFont", "")) for font in fonts.values()}


def count_links(reader: PdfReader) -> int:
    total = 0
    for page in reader.pages:
        for annotation in page.get("/Annots", []) or []:
            obj = annotation.get_object()
            action = obj.get("/A", {})
            if action.get("/S") == "/URI" and action.get("/URI"):
                total += 1
    return total


def validate(output: Path, source_hashes: dict[str, str], source_pages: list[int], source_uri_links: int) -> dict:
    reader = PdfReader(output)
    expected_pages = 2 + sum(source_pages)
    if len(reader.pages) != expected_pages:
        raise ValueError(f"expected {expected_pages} pages, got {len(reader.pages)}")
    all_text = []
    empty_pages = []
    missing_fonts = []
    for number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        all_text.append(text)
        if not text.strip():
            empty_pages.append(number)
        if not page_fonts(page):
            missing_fonts.append(number)
    if empty_pages:
        raise ValueError(f"blank or non-extractable pages: {empty_pages}")
    if missing_fonts:
        raise ValueError(f"pages without embedded/referenced fonts: {missing_fonts}")
    text = "\n".join(all_text)
    required_phrases = (
        "EVIDENCE-LIMITED PUBLIC-SOURCE AUDIT",
        "not a completed measured audit",
        "fictional proposed campaign",
        "scenario inputs, not benchmarks, forecasts, or results",
        "Supporting appendix",
        "pending organizer acceptance",
    )
    absent = [phrase for phrase in required_phrases if phrase.lower() not in text.lower()]
    if absent:
        raise ValueError(f"required boundary text missing: {absent}")
    metadata = reader.metadata or {}
    metadata_text = " ".join(str(value) for value in metadata.values()).lower()
    prohibited_metadata = ("researchbae", "@", "offer letter", "student id")
    leaks = [item for item in prohibited_metadata if item in metadata_text]
    if leaks:
        raise ValueError(f"unintended personal metadata: {leaks}")
    labels = reader.trailer["/Root"].get("/PageLabels")
    if labels is None:
        raise ValueError("page labels missing")
    outline = reader.outline
    if len(outline) < 5:
        raise ValueError("expected front matter and task bookmarks")
    output_uri_links = count_links(reader)
    if output_uri_links != source_uri_links:
        raise ValueError(
            f"URI hyperlink count changed during assembly: {source_uri_links} source, {output_uri_links} output"
        )
    return {
        "result": "passed",
        "page_count": len(reader.pages),
        "source_page_count": sum(source_pages),
        "output_sha256": sha256(output),
        "extracted_text_characters": len(text),
        "pages_with_no_extractable_text": empty_pages,
        "pages_with_no_font_resources": missing_fonts,
        "source_uri_hyperlinks": source_uri_links,
        "uri_hyperlinks_retained": output_uri_links,
        "source_hashes_unchanged": {name: sha256(path) == source_hashes[str(path)] for name, path, _ in SOURCES},
        "metadata": {str(key): str(value) for key, value in metadata.items()},
        "checks": {
            "ordered_source_pages": True,
            "bookmarks": True,
            "page_labels": True,
            "text_extraction": True,
            "font_resources": True,
            "required_boundary_language": True,
            "metadata_privacy": True,
        },
    }


def build() -> dict:
    for _title, path, _description in SOURCES:
        if not path.is_file():
            raise FileNotFoundError(path)
    source_hashes = {str(path): sha256(path) for _title, path, _description in SOURCES}
    source_pages = [page_count(path) for _title, path, _description in SOURCES]
    source_uri_links = sum(count_links(PdfReader(path)) for _title, path, _description in SOURCES)
    front_matter = OUTPUT.with_name(".combined_front_matter.pdf")
    build_front_matter(front_matter, source_pages)
    writer = PdfWriter()
    writer.append(front_matter, outline_item="Cover and contents", import_outline=False)
    for title, path, _description in SOURCES:
        writer.append(path, outline_item=title, import_outline=True)
    starts = [0, 1, 2]
    for count in source_pages[:-1]:
        starts.append(starts[-1] + count)
    labels = ("Cover ", "Contents ", "Task 2 ", "Task 3 ", "Task 4 ", "Task 4 Appendix ")
    starts = [0, 1, 2, 2 + source_pages[0], 2 + source_pages[0] + source_pages[1], 2 + source_pages[0] + source_pages[1] + source_pages[2]]
    ends = [0, 1, starts[3] - 1, starts[4] - 1, starts[5] - 1, 1 + sum(source_pages)]
    for start, end, prefix in zip(starts, ends, labels):
        writer.set_page_label(start, end, style=PageLabelStyle.DECIMAL, prefix=prefix, start=1)
    writer.add_outline_item("Cover", 0)
    writer.add_outline_item("Contents", 1)
    writer.add_outline_item(SOURCES[0][0], 2)
    writer.add_outline_item(SOURCES[1][0], 2 + source_pages[0])
    writer.add_outline_item(SOURCES[2][0], 2 + source_pages[0] + source_pages[1])
    writer.add_outline_item(SOURCES[3][0], 2 + source_pages[0] + source_pages[1] + source_pages[2])
    writer.add_metadata({
        "/Title": "Progree Digital Marketing & Branding — Tasks 2–4 Review Copy",
        "/Author": "Anonymous internship project",
        "/Subject": "Consolidated review copy; Task 2 remains evidence-limited and pending rubric acceptance",
        "/Creator": "Progree final-submission preparation",
        "/Keywords": "Digital Marketing, Task 2, Task 3, Task 4, review copy",
    })
    with OUTPUT.open("wb") as file:
        writer.write(file)
    front_matter.unlink(missing_ok=True)
    result = validate(OUTPUT, source_hashes, source_pages, source_uri_links)
    result["source_documents"] = [
        {"path": str(path.relative_to(ROOT)), "pages": pages, "sha256": source_hashes[str(path)]}
        for (_title, path, _description), pages in zip(SOURCES, source_pages)
    ]
    result["output"] = str(OUTPUT.relative_to(ROOT))
    result["generated_utc_date"] = date.today().isoformat()
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    result = build()
    print(f"PASS: wrote {result['output']} ({result['page_count']} pages)")
    print(f"SHA-256: {result['output_sha256']}")


if __name__ == "__main__":
    main()
