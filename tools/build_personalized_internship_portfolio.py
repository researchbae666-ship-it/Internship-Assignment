#!/usr/bin/env python3
"""Build the authorized personalized Progree portfolio without changing its baseline.

Personal details are accepted as command-line arguments so they are embedded in
the owner-authorized PDF but not duplicated in repository scripts, manifests or
QA documentation.  This script imports the 52 approved report pages as PDF page
objects and creates only the eight portfolio-context pages around them.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from pypdf import PdfReader, PdfWriter
from pypdf.constants import PageLabelStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

import build_complete_internship_portfolio as base


ROOT = base.ROOT
FINAL = ROOT / "FINAL_SUBMISSION"
BASELINE = FINAL / "01_Progree_Complete_Internship_Portfolio.pdf"
OUTPUT = FINAL / "01_Progree_Complete_Internship_Portfolio_PERSONALIZED.pdf"
README = FINAL / "00_READ_ME_FIRST.md"
MANIFEST = FINAL / "manifest.json"
QA = FINAL / "QA" / "FINAL_VERIFICATION.md"
MARKETING = base.MARKETING
PYTHON = base.PYTHON


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validated_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="owner-authorized full name to embed in the PDF")
    parser.add_argument("--certificate-name", required=True, help="owner-authorized certificate name to embed in the PDF")
    parser.add_argument("--email", required=True, help="owner-authorized email to embed in the PDF")
    parser.add_argument("--whatsapp", required=True, help="owner-authorized WhatsApp number to embed in the PDF")
    parser.add_argument("--registration", required=True, help="owner-authorized registration ID to embed in the PDF")
    parser.add_argument("--replace", action="store_true", help="replace only the existing personalized candidate")
    arguments = parser.parse_args()
    for field in ("name", "certificate_name", "email", "whatsapp", "registration"):
        if not getattr(arguments, field).strip():
            parser.error(f"--{field.replace('_', '-')} must not be blank")
    if arguments.name != arguments.certificate_name:
        parser.error("--name and --certificate-name must match for this authorized candidate")
    return arguments


def ensure_inputs() -> None:
    expected = (
        (BASELINE, 60, "b5903f037578f6e22a9792cf4fc8862a90db18b508935e7b15df3d11bfa3b071"),
        (MARKETING, 38, base.EXPECTED_MARKETING_SHA),
        (PYTHON, 14, base.EXPECTED_PYTHON_SHA),
    )
    for path, page_count, expected_sha in expected:
        if not path.is_file():
            raise RuntimeError(f"required PDF missing: {path}")
        if len(PdfReader(path).pages) != page_count:
            raise RuntimeError(f"page count changed for {path}")
        if sha256(path) != expected_sha:
            raise RuntimeError(f"protected baseline hash changed for {path}")


def cover(canvas: Canvas, owner: argparse.Namespace) -> None:
    width, height = A4
    left = base.LEFT
    canvas.setFillColor(base.NAVY)
    canvas.rect(0, 0, width, height, fill=1, stroke=0)
    canvas.setFillColor(base.TEAL)
    canvas.circle(width - 13 * mm, height - 17 * mm, 23 * mm, fill=1, stroke=0)
    canvas.setFillColor(base.GOLD)
    canvas.circle(width - 35 * mm, height - 48 * mm, 8 * mm, fill=1, stroke=0)
    canvas.setStrokeColor(colors.HexColor("#5EC5C7"))
    canvas.setLineWidth(1.3)
    canvas.line(left, height - 52 * mm, left + 53 * mm, height - 52 * mm)
    canvas.setFillColor(colors.HexColor("#B9DDDE"))
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(left, height - 39 * mm, "PROGREE INTERNSHIP")
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 26)
    canvas.drawString(left, height - 70 * mm, "COMPLETE PROJECT")
    canvas.drawString(left, height - 82 * mm, "PORTFOLIO")
    canvas.setFont("Helvetica", 12)
    canvas.setFillColor(colors.HexColor("#DDEFF0"))
    canvas.drawString(left, height - 99 * mm, "Digital Marketing & Branding")
    canvas.drawString(left, height - 108 * mm, "+")
    canvas.drawString(left, height - 117 * mm, "Python Programming")
    canvas.setFillColor(colors.HexColor("#B9DDDE"))
    canvas.setFont("Helvetica-Bold", 8.4)
    canvas.drawString(left, height - 134 * mm, "SIX SUBMITTED TASK DELIVERABLES ACROSS TWO INTERNSHIP TRACKS")
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica", 8.9)
    canvas.drawString(left, height - 145 * mm, "Includes one evidence-limited competitor audit; organizer acceptance remains pending.")

    panel_x, panel_y, panel_w, panel_h = left, 35 * mm, width - 2 * left, 74 * mm
    canvas.setFillColor(colors.HexColor("#17445E"))
    canvas.roundRect(panel_x, panel_y, panel_w, panel_h, 3 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#B9DDDE"))
    canvas.setFont("Helvetica-Bold", 7.6)
    canvas.drawString(panel_x + 6 * mm, panel_y + panel_h - 10 * mm, "CANDIDATE INFORMATION")
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 8.4)
    canvas.drawString(panel_x + 6 * mm, panel_y + panel_h - 21 * mm, "Prepared by")
    canvas.setFont("Helvetica", 10.2)
    canvas.drawString(panel_x + 6 * mm, panel_y + panel_h - 29 * mm, owner.certificate_name)
    canvas.setFont("Helvetica-Bold", 8.4)
    canvas.drawString(panel_x + 6 * mm, panel_y + panel_h - 42 * mm, "Registration")
    canvas.setFont("Helvetica", 9.6)
    canvas.drawString(panel_x + 6 * mm, panel_y + panel_h - 49 * mm, owner.registration)
    right_x = panel_x + 86 * mm
    canvas.setFont("Helvetica-Bold", 8.4)
    canvas.drawString(right_x, panel_y + panel_h - 21 * mm, "Email")
    canvas.setFont("Helvetica", 9.2)
    canvas.drawString(right_x, panel_y + panel_h - 29 * mm, owner.email)
    canvas.setFont("Helvetica-Bold", 8.4)
    canvas.drawString(right_x, panel_y + panel_h - 42 * mm, "WhatsApp")
    canvas.setFont("Helvetica", 9.2)
    canvas.drawString(right_x, panel_y + panel_h - 49 * mm, owner.whatsapp)
    canvas.setStrokeColor(colors.HexColor("#5EC5C7"))
    canvas.setLineWidth(0.5)
    canvas.line(panel_x + 6 * mm, panel_y + 16 * mm, panel_x + panel_w - 6 * mm, panel_y + 16 * mm)
    canvas.setFillColor(colors.HexColor("#DDEFF0"))
    canvas.setFont("Helvetica", 7.9)
    canvas.drawString(panel_x + 6 * mm, panel_y + 8 * mm, "Domains: Digital Marketing & Branding • Python Programming • Submission period: October 2026")
    canvas.showPage()


def executive(canvas: Canvas, styles: dict[str, Any]) -> None:
    y = base.header(canvas, "Portfolio overview", "Executive summary", 2)
    y = base.para(canvas, "This personalized candidate presents <b>six submitted Task 2–4 deliverables across two internship tracks</b>. It places Digital Marketing &amp; Branding first, then Python Programming, while preserving each approved task report as original PDF pages.", base.LEFT, y, base.RIGHT - base.LEFT, styles["body"]) - 4 * mm
    y = base.para(canvas, "The portfolio differentiates implemented and tested software from proposed campaign/SEO work, modeled financial scenarios, and the evidence-limited competitor audit. It does not represent Task 1 as complete, any campaign as launched, any modeled outcome as achieved, or certificate eligibility as confirmed.", base.LEFT, y, base.RIGHT - base.LEFT, styles["body"]) - 7 * mm
    width = (base.RIGHT - base.LEFT - 7 * mm) / 2
    base.metric_card(canvas, base.LEFT, y, width, 29 * mm, "2", "internship domains", base.TEAL)
    base.metric_card(canvas, base.LEFT + width + 7 * mm, y, width, 29 * mm, "6", "submitted Task 2–4\ndeliverables", base.GOLD)
    y -= 36 * mm
    rows = [
        ["Portfolio evidence", "What is included", "Status and boundary"],
        ["Digital Marketing", "Complete 38-page report: Task 2 audit, Task 3 RefillLoop campaign, Task 4 Ocean Bottle strategy and email appendix.", "Task 2 is evidence-limited; Task 3 and Task 4 are proposed plans/models, not executed campaigns."],
        ["Python Programming", "Complete 14-page report: Fibonacci timing, safe file automation and a multi-intent chatbot.", "Tasks 2–4 were implemented and tested; the report retains commands, outputs, source references and limitations."],
        ["Verification", "Source preservation, model tests, project tests and current PDF QA are indexed in the final pages.", "Technical review does not establish organizer acceptance or two-track certificate eligibility."],
    ]
    base.draw_table(canvas, rows, [34 * mm, 72 * mm, 58 * mm], base.LEFT, y, styles)
    canvas.showPage()


def contents(canvas: Canvas, styles: dict[str, Any]) -> None:
    y = base.header(canvas, "Navigation", "Master contents", 3)
    y = base.para(canvas, "Portfolio page numbers below refer to the full 60-page personalized candidate. Imported reports retain their own internal numbering; the outline provides named destinations for both systems.", base.LEFT, y, base.RIGHT - base.LEFT, styles["body"]) - 5 * mm
    rows = [
        ["Portfolio section", "Pages", "Navigation meaning"],
        ["Cover and executive summary", "1–2", "Candidate information and evidence boundaries"],
        ["Master contents and results", "3–4", "Full-document navigation and verified scope"],
        ["Digital Marketing introduction", "5", "Status, claim boundaries and report guide"],
        ["Complete Marketing report", "6–43", "Imported 38-page approved report"],
        ["Marketing Task 2 / 3 / 4 / email appendix", "8 / 12 / 32 / 38", "Starts within the full portfolio"],
        ["Python Programming introduction", "44", "Implementation scope and self-contained evidence guide"],
        ["Complete Python report", "45–58", "Imported 14-page approved report"],
        ["Python Task 2 / 3 / 4", "47 / 50 / 53", "Starts within the full portfolio"],
        ["Evidence and reproduction index", "59", "Preservation, testing and QA evidence"],
        ["Final owner summary and source index", "60", "Canonical sources and administrative conditions"],
    ]
    base.draw_table(canvas, rows, [78 * mm, 28 * mm, 58 * mm], base.LEFT, y, styles)
    canvas.showPage()


def results(canvas: Canvas, styles: dict[str, Any], facts: dict[str, Any]) -> None:
    y = base.header(canvas, "Verified project evidence", "Results at a glance", 4)
    y = base.para(canvas, "This page separates implemented work, proposed deliverables, modeled scenarios, automated testing and the remaining research limitation. Counts and financial values are calculated from the retained task models and audit records.", base.LEFT, y, base.RIGHT - base.LEFT, styles["body"]) - 4 * mm
    rows = [
        ["Evidence category", "Verified achievement", "Interpretation boundary"],
        ["A. Implemented software", "Three Python modules: Fibonacci generation/timing; safe file organization, extraction and CSV export; multi-intent terminal chatbot.", "Implemented and tested software. The report includes representative code, commands, actual outputs and limitations."],
        ["B. Proposed marketing deliverables", f"Three brands; {facts['marketing_actions']} proposed actions across {facts['marketing_channels']['Instagram']} Instagram, {facts['marketing_channels']['LinkedIn']} LinkedIn and {facts['marketing_channels']['YouTube']} YouTube actions; {facts['marketing_paid_actions']} paid placements; {facts['marketing_personas']} personas; {facts['marketing_ab_tests']} A/B tests.", f"RefillLoop is fictional. These are proposed actions, targeting and USD {facts['marketing_budget_usd']:,} media planning—not published posts or spend."],
        ["C. Modeled financial scenarios", f"Ocean Bottle: {facts['task4_keywords']} keyword-intent entries, {facts['task4_seo_pages']} SEO pages, {facts['task4_funnel_stages']} funnel stages, {facts['task4_flows']} workflows and {facts['task4_messages']} drafted messages.", "Proposed GBP 12,000 planning budget (GBP 10,000 media). Low/base/high modeled customers 75/160/320; media CAC GBP 133.33/62.50/31.25; ROAS 0.34/0.88/2.08."],
        ["D. Verified automated testing", "55 Python-suite tests within 129 cross-track unit tests recorded in the final audit; current regression rerun is indexed in QA.", "Tests verify code, model calculations, report presentation and safety boundaries—not real campaign performance."],
        ["E. Documented research limitation", "Task 2 covers Stanley 1913, Hydro Flask and Owala with verified account references and bounded secondary-source evidence.", "Historical count changes are not verified cadence; vendor engagement is estimated; organizer acceptance is unconfirmed."],
    ]
    base.draw_table(canvas, rows, [35 * mm, 70 * mm, 59 * mm], base.LEFT, y, styles, "tiny")
    canvas.showPage()


def marketing_intro(canvas: Canvas, styles: dict[str, Any], facts: dict[str, Any]) -> None:
    y = base.header(canvas, "Track one", "Digital Marketing & Branding", 5)
    y = base.para(canvas, "The next <b>38 pages are the complete approved Marketing final candidate, imported unchanged</b>. Its internal cover and contents are retained intentionally as the report's original navigation; this portfolio's master contents and outline give the full-document page locations.", base.LEFT, y, base.RIGHT - base.LEFT, styles["body"]) - 5 * mm
    rows = [
        ["Task", "Included evidence", "Accurate interpretation"],
        ["Task 2", "Stanley 1913, Hydro Flask and Owala positioning, official account references, creative observations, historical third-party snapshots and vendor estimates.", "Evidence-limited public-source audit: no verified 15 Sep–12 Oct posting cadence, complete post inventory, post-level engagement or organizer acceptance."],
        ["Task 3", f"RefillLoop {facts['marketing_actions']}-action, 30-day roadmap on three channels, {facts['marketing_paid_actions']} planned paid actions, three personas, four A/B tests and proposed USD {facts['marketing_budget_usd']:,} media budget.", "Fictional proposed campaign. No product was launched, no ads were run and no sales/performance result is claimed."],
        ["Task 4", f"Ocean Bottle keyword/SEO/acquisition strategy with {facts['task4_keywords']} keyword entries, {facts['task4_funnel_stages']} stages, {facts['task4_flows']} workflows and {facts['task4_messages']} full drafts in its appendix.", "Proposed recommendations and financial model. No ranking, acquisition, revenue or customer performance is claimed."],
    ]
    y = base.draw_table(canvas, rows, [23 * mm, 76 * mm, 65 * mm], base.LEFT, y, styles) - 7 * mm
    canvas.setFillColor(base.PALE_GOLD)
    canvas.roundRect(base.LEFT, y - 29 * mm, base.RIGHT - base.LEFT, 29 * mm, 3 * mm, fill=1, stroke=0)
    base.para(canvas, "<b>Full-document navigation:</b> Marketing starts at Portfolio page 6. Task 2 begins on page 8, Task 3 on page 12, Task 4 on page 32 and the complete email appendix on page 38. The imported report's own numbering remains visible only within that report.", base.LEFT + 5 * mm, y - 6 * mm, base.RIGHT - base.LEFT - 10 * mm, styles["body"])
    canvas.showPage()


def python_intro(canvas: Canvas, styles: dict[str, Any]) -> None:
    y = base.header(canvas, "Track two", "Python Programming", 44)
    y = base.para(canvas, "The next <b>14 pages are the complete approved Python final candidate, imported unchanged</b>. It is deliberately self-contained: it includes representative implementation excerpts, executed sample outputs, commands, algorithm explanations, safety boundaries, test results and source-file references.", base.LEFT, y, base.RIGHT - base.LEFT, styles["body"]) - 5 * mm
    rows = [
        ["Task", "Implemented capability", "Evidence retained in the report"],
        ["Task 2", "Fibonacci sequence generation with validation and timeit measurement.", "Input constraints, structured output, benchmark configuration, CLI examples and computational limitations."],
        ["Task 3", "Safe file organization, text extraction, CSV export and integrity checks.", "Preview-first workflow, path validation, overwrite prevention, synthetic examples and the corrected path-traversal case."],
        ["Task 4", "Multi-intent rule-based terminal chatbot with normalization, state and recovery logic.", "State flow, routing excerpts, transcript evidence, error handling and known rule-based limits."],
    ]
    y = base.draw_table(canvas, rows, [23 * mm, 73 * mm, 68 * mm], base.LEFT, y, styles) - 7 * mm
    canvas.setFillColor(base.PALE)
    canvas.roundRect(base.LEFT, y - 39 * mm, base.RIGHT - base.LEFT, 39 * mm, 3 * mm, fill=1, stroke=0)
    base.para(canvas, "<b>Supplementary appendix decision:</b> no additional Python appendix is added because the approved report already provides the necessary readable excerpts, real execution evidence, reproduction commands and source references. Duplicating full code here would reduce readability without adding evaluation evidence.", base.LEFT + 5 * mm, y - 7 * mm, base.RIGHT - base.LEFT - 10 * mm, styles["body"])
    base.para(canvas, "Complete runnable sources remain in <font name='Courier'>internship/task2.py</font>, <font name='Courier'>internship/task3.py</font> and <font name='Courier'>internship/task4.py</font>; tests are in <font name='Courier'>tests/</font>. The imported report starts on Portfolio page 45; Tasks 2, 3 and 4 start on pages 47, 50 and 53.", base.LEFT + 5 * mm, y - 27 * mm, base.RIGHT - base.LEFT - 10 * mm, styles["body"])
    canvas.showPage()


def evidence(canvas: Canvas, styles: dict[str, Any]) -> None:
    y = base.header(canvas, "Selective evidence", "Verification and reproduction evidence", 59)
    y = base.para(canvas, "The personalized candidate changes only its eight portfolio-authored pages. Its 52 imported report pages are preserved as PDF page objects and compared against their approved sources for text, content streams, dimensions, rotation and 180 DPI rendering.", base.LEFT, y, base.RIGHT - base.LEFT, styles["body"]) - 5 * mm
    rows = [
        ["Evidence", "Location", "Validation"],
        ["Historical portfolio baseline", "FINAL_SUBMISSION/01_Progree_Complete_Internship_Portfolio.pdf", "Retained unchanged at its approved 60 pages and SHA-256 before personalization."],
        ["Marketing candidate", "Portfolio pages 6–43", "38 source pages compared against the approved Marketing candidate; appendix included."],
        ["Python candidate", "Portfolio pages 45–58", "14 source pages compared against the approved Python candidate; all three tasks included."],
        ["Models and tests", "digital_marketing/research/, internship/, tests/", "Counts are recalculated from Task 3/4 model data; final audit records 129 cross-track tests, including 55 Python tests."],
        ["Portfolio QA", "FINAL_SUBMISSION/QA/FINAL_VERIFICATION.md", "Current personalized PDF checks, rendering evidence, metadata review and owner-authorized detail verification."],
    ]
    y = base.draw_table(canvas, rows, [34 * mm, 53 * mm, 77 * mm], base.LEFT, y, styles) - 7 * mm
    canvas.setFillColor(base.PALE_GOLD)
    canvas.roundRect(base.LEFT, y - 32 * mm, base.RIGHT - base.LEFT, 32 * mm, 3 * mm, fill=1, stroke=0)
    base.para(canvas, "<b>Administrative boundary:</b> this personalized PDF meets the visible one-file and 10 MB constraints supplied by the owner. A single-choice Form domain field does not establish that one response earns both certificates. Marketing Task 2 remains evidence-limited pending organizer acceptance. No form action has occurred.", base.LEFT + 5 * mm, y - 7 * mm, base.RIGHT - base.LEFT - 10 * mm, styles["body"])
    canvas.showPage()


def conclusion(canvas: Canvas, styles: dict[str, Any]) -> None:
    y = base.header(canvas, "Close and reproduce", "Final owner summary and source index", 60)
    y = base.para(canvas, "This personalized candidate contains the complete Digital Marketing report first and the complete Python report second. Candidate identity details appear only on the cover and in document metadata; all task-report pages retain their approved content and original internal page numbering.", base.LEFT, y, base.RIGHT - base.LEFT, styles["body"]) - 5 * mm
    canvas.setFillColor(base.PALE)
    canvas.roundRect(base.LEFT, y - 20 * mm, base.RIGHT - base.LEFT, 20 * mm, 3 * mm, fill=1, stroke=0)
    base.para(canvas, "<b>Reproduce:</b> run <font name='Courier'>python tools/build_personalized_internship_portfolio.py --help</font> for the owner-authorized parameters, then run <font name='Courier'>python tools/verify_personalized_internship_portfolio.py --help</font> using the same values. Personal values are intentionally not written into the build instructions.", base.LEFT + 5 * mm, y - 5 * mm, base.RIGHT - base.LEFT - 10 * mm, styles["small"])
    y -= 27 * mm
    canvas.setFillColor(base.NAVY)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(base.LEFT, y, "CANONICAL SOURCE AND REPRODUCTION INDEX")
    y -= 5 * mm
    table_width = base.RIGHT - base.LEFT
    col_one, col_two = 45 * mm, 88 * mm
    row_height = 10.5 * mm
    canvas.setFillColor(base.NAVY)
    canvas.rect(base.LEFT, y - 7 * mm, table_width, 7 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 7.5)
    canvas.drawString(base.LEFT + 4, y - 4.6 * mm, "Task / evidence")
    canvas.drawString(base.LEFT + col_one + 4, y - 4.6 * mm, "Canonical repository path")
    canvas.drawString(base.LEFT + col_one + col_two + 4, y - 4.6 * mm, "Link")
    y -= 7 * mm
    for index, (label, path, url) in enumerate(base.SOURCE_INDEX):
        canvas.setFillColor(colors.HexColor("#F8FBFB") if index % 2 == 0 else colors.white)
        canvas.rect(base.LEFT, y - row_height, table_width, row_height, fill=1, stroke=0)
        canvas.setStrokeColor(colors.HexColor("#D7E3E5"))
        canvas.setLineWidth(0.35)
        canvas.rect(base.LEFT, y - row_height, table_width, row_height, fill=0, stroke=1)
        canvas.setFillColor(base.INK)
        canvas.setFont("Helvetica", 7.35)
        canvas.drawString(base.LEFT + 4, y - 5.8 * mm, label)
        canvas.setFont("Courier", 6.5)
        canvas.drawString(base.LEFT + col_one + 4, y - 5.8 * mm, path)
        label_text = "Open on GitHub"
        link_x = base.LEFT + col_one + col_two + 4
        canvas.setFont("Helvetica-Bold", 7.2)
        canvas.setFillColor(base.BLUE)
        canvas.drawString(link_x, y - 5.8 * mm, label_text)
        canvas.linkURL(url, (link_x, y - 7.7 * mm, link_x + stringWidth(label_text, "Helvetica-Bold", 7.2), y - 3.6 * mm), relative=0, thickness=0)
        y -= row_height
    canvas.setFillColor(base.MUTED)
    canvas.setFont("Helvetica", 7.3)
    canvas.drawString(base.LEFT, base.BOTTOM + 12 * mm, "Owner review is still required. No Google Form response, submission, upload, email or campaign action has been performed.")
    canvas.showPage()


def authored_pages(path: Path, owner: argparse.Namespace) -> None:
    facts = base.source_facts()
    styles = base.styles()
    canvas = Canvas(str(path), pagesize=A4, pageCompression=1)
    canvas.setTitle("Progree Internship — Complete Project Portfolio — Personalized Candidate")
    canvas.setAuthor(owner.certificate_name)
    canvas.setSubject("Personalized Digital Marketing and Python Tasks 2–4 portfolio; Marketing Task 2 remains evidence-limited and pending acceptance")
    canvas.setCreator("Progree personalized portfolio assembly")
    cover(canvas, owner)
    executive(canvas, styles)
    contents(canvas, styles)
    results(canvas, styles, facts)
    marketing_intro(canvas, styles, facts)
    python_intro(canvas, styles)
    evidence(canvas, styles)
    conclusion(canvas, styles)
    canvas.save()


def build_pdf(stage: Path, owner: argparse.Namespace) -> None:
    authored = PdfReader(stage / "authored.pdf")
    marketing = PdfReader(MARKETING)
    python = PdfReader(PYTHON)
    if len(authored.pages) != 8:
        raise RuntimeError("personalized authored-page count changed")
    writer = PdfWriter()
    for page in authored.pages[:5]: writer.add_page(page)
    for page in marketing.pages: writer.add_page(page)
    writer.add_page(authored.pages[5])
    for page in python.pages: writer.add_page(page)
    for page in authored.pages[6:]: writer.add_page(page)
    if len(writer.pages) != 60:
        raise RuntimeError("personalized portfolio must remain 60 pages")
    writer.add_outline_item("Cover — candidate information", 0)
    writer.add_outline_item("Executive summary", 1)
    writer.add_outline_item("Master contents", 2)
    writer.add_outline_item("Results at a glance", 3)
    marketing_root = writer.add_outline_item("Digital Marketing & Branding", 4)
    writer.add_outline_item("Track introduction", 4, parent=marketing_root)
    writer.add_outline_item("Complete Marketing report", 5, parent=marketing_root)
    writer.add_outline_item("Marketing Task 2 — evidence-limited audit", 7, parent=marketing_root)
    writer.add_outline_item("Marketing Task 3 — RefillLoop proposed campaign", 11, parent=marketing_root)
    writer.add_outline_item("Marketing Task 4 — Ocean Bottle proposed strategy", 31, parent=marketing_root)
    writer.add_outline_item("Marketing Task 4 email appendix", 37, parent=marketing_root)
    python_root = writer.add_outline_item("Python Programming", 43)
    writer.add_outline_item("Track introduction", 43, parent=python_root)
    writer.add_outline_item("Complete Python report", 44, parent=python_root)
    writer.add_outline_item("Python Task 2 — Fibonacci and timing", 46, parent=python_root)
    writer.add_outline_item("Python Task 3 — safe file automation", 49, parent=python_root)
    writer.add_outline_item("Python Task 4 — multi-intent chatbot", 52, parent=python_root)
    writer.add_outline_item("Evidence and reproduction index", 58)
    writer.add_outline_item("Final owner summary and source index", 59)
    writer.set_page_label(0, 59, PageLabelStyle.DECIMAL, prefix="Portfolio ", start=1)
    writer.add_metadata({
        "/Title": "Progree Internship — Complete Project Portfolio — Personalized Candidate",
        "/Author": owner.certificate_name,
        "/Subject": "Personalized Digital Marketing and Python Tasks 2–4 portfolio; Marketing Task 2 remains evidence-limited and pending acceptance",
        "/Creator": "Progree personalized portfolio assembly",
        "/Producer": "pypdf",
    })
    with (stage / "portfolio.pdf").open("wb") as handle:
        writer.write(handle)


def write_support_docs(owner: argparse.Namespace) -> None:
    baseline_manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    info = {"path": OUTPUT.relative_to(ROOT).as_posix(), "pages": len(PdfReader(OUTPUT).pages), "bytes": OUTPUT.stat().st_size, "sha256": sha256(OUTPUT)}
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    baseline_manifest["personalized_candidate"] = {
        "status": "built_pending_final_verification",
        "source_commit": commit,
        "path": info["path"],
        "pages": info["pages"],
        "bytes": info["bytes"],
        "sha256": info["sha256"],
        "baseline_portfolio": {"path": BASELINE.relative_to(ROOT).as_posix(), "pages": 60, "sha256": sha256(BASELINE)},
        "source_candidates": [
            {"path": MARKETING.relative_to(ROOT).as_posix(), "pages": 38, "sha256": sha256(MARKETING), "portfolio_pages": [6, 43]},
            {"path": PYTHON.relative_to(ROOT).as_posix(), "pages": 14, "sha256": sha256(PYTHON), "portfolio_pages": [45, 58]},
        ],
        "owner_detail_handling": "The owner explicitly authorized four supplied personal fields in the personalized PDF and its author metadata. Their values are intentionally not duplicated in this manifest or support documents.",
        "page_map": base.page_map(),
        "administrative_qualification": "One combined PDF meets the visible one-file constraint but does not establish that a single-choice form response earns both certificates. Marketing Task 2 remains evidence-limited pending organizer acceptance.",
    }
    MANIFEST.write_text(json.dumps(baseline_manifest, indent=2) + "\n", encoding="utf-8")
    README.write_text(
        "# Progree complete internship portfolio\n\n"
        "## Owner-reviewed PDF candidates\n\n"
        "- `01_Progree_Complete_Internship_Portfolio.pdf` — historical anonymous 60-page baseline, retained unchanged.\n"
        f"- `01_Progree_Complete_Internship_Portfolio_PERSONALIZED.pdf` — owner-authorized personalized candidate: **{info['pages']} pages**, **{info['bytes']:,} bytes**, SHA-256 `{info['sha256']}`.\n\n"
        "Both order Digital Marketing & Branding first and Python Programming second, with the complete approved Marketing and Python reports preserved as PDF pages. The personalized candidate adds identity information only to its cover and author metadata.\n\n"
        "## Upload preparation\n\n"
        "The personalized candidate is below the owner-supplied visible 10 MB file limit. It is a review candidate, not an executed submission. The form's single domain choice does not establish that one response earns two certificates.\n\n"
        "## Reproduce\n\n"
        "Use `python tools/build_personalized_internship_portfolio.py --help` and `python tools/verify_personalized_internship_portfolio.py --help`. Supply the owner-authorized fields privately; the support documentation deliberately does not repeat them.\n\n"
        "Marketing Task 2 remains an evidence-limited public-source audit pending organizer acceptance. No form, email, campaign or LinkedIn activity has occurred.\n",
        encoding="utf-8",
    )
    QA.write_text("# Personalized final verification\n\nRun the personalized verifier to record final structural, rendering, privacy and regression checks.\n", encoding="utf-8")


def main() -> int:
    owner = validated_args()
    ensure_inputs()
    if OUTPUT.exists() and not owner.replace:
        raise RuntimeError("personalized candidate exists; rerun with --replace")
    if OUTPUT.exists():
        OUTPUT.unlink()
    with tempfile.TemporaryDirectory(prefix="progree-personalized-portfolio-", dir="/tmp") as temporary:
        stage = Path(temporary)
        authored_pages(stage / "authored.pdf", owner)
        build_pdf(stage, owner)
        shutil.copyfile(stage / "portfolio.pdf", OUTPUT)
    write_support_docs(owner)
    print(json.dumps({"path": OUTPUT.relative_to(ROOT).as_posix(), "pages": 60, "bytes": OUTPUT.stat().st_size, "sha256": sha256(OUTPUT)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
