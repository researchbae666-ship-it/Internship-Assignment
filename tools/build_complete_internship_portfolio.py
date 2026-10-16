#!/usr/bin/env python3
"""Build the final one-file Progree internship portfolio.

This is a controlled assembly tool.  It creates eight new portfolio pages and
imports the two approved final-candidate PDFs as PDF page objects.  It never
rewrites, rasterizes, crops, or replaces either approved candidate.  Run the
companion verifier after building:

    python tools/build_complete_internship_portfolio.py
    python tools/verify_complete_internship_portfolio.py
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
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "FINAL_SUBMISSION"
OUTPUT = FINAL / "01_Progree_Complete_Internship_Portfolio.pdf"
README = FINAL / "00_READ_ME_FIRST.md"
MANIFEST = FINAL / "manifest.json"
QA = FINAL / "QA" / "FINAL_VERIFICATION.md"
MARKETING = ROOT / "digital_marketing/deliverables/Progree_Digital_Marketing_Tasks_2_3_4_FINAL_CANDIDATE.pdf"
PYTHON = ROOT / "deliverables/Progree_Python_Tasks_2_3_4_FINAL_CANDIDATE.pdf"
CAMPAIGN = ROOT / "digital_marketing/research/task3/campaign_calendar.json"
STRATEGY = ROOT / "digital_marketing/research/task4/strategy_data.json"

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT = 18 * mm
RIGHT = PAGE_WIDTH - 18 * mm
TOP = PAGE_HEIGHT - 18 * mm
BOTTOM = 16 * mm
NAVY = colors.HexColor("#12314A")
BLUE = colors.HexColor("#127B9C")
TEAL = colors.HexColor("#22A3A8")
GOLD = colors.HexColor("#D79D32")
INK = colors.HexColor("#1A2933")
MUTED = colors.HexColor("#59727F")
PALE = colors.HexColor("#EDF5F6")
PALE_GOLD = colors.HexColor("#FCF5E8")
WHITE = colors.white

GITHUB = "https://github.com/researchbae666-ship-it/Internship-Assignment"
EXPECTED_MARKETING_SHA = "571f801e92fd496b27dc8bcd1fb40066d22068f35b783ba2e151f36b7335bb5a"
EXPECTED_PYTHON_SHA = "8910c0aafccb8a575affc9794291b5c9910a23cfebdda3fa6b873c485bece284"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_facts() -> dict[str, Any]:
    campaign = json.loads(CAMPAIGN.read_text(encoding="utf-8"))
    strategy = json.loads(STRATEGY.read_text(encoding="utf-8"))
    actions = campaign["actions"]
    channels = {
        name: sum(action["platform"] == name for action in actions)
        for name in ("Instagram", "LinkedIn", "YouTube")
    }
    paid_actions = sum(action["distribution"] == "Paid" for action in actions)
    email_messages = sum(len(flow["messages"]) for flow in strategy["emails"])
    return {
        "marketing_actions": len(actions),
        "marketing_channels": channels,
        "marketing_paid_actions": paid_actions,
        "marketing_personas": len(campaign["personas"]),
        "marketing_ab_tests": len(campaign["ab_tests"]),
        "marketing_budget_usd": campaign["budget"]["total"],
        "marketing_budget_allocation": campaign["budget"]["allocation"],
        "marketing_funnel": [
            {"name": row["name"], "interest_completions": row["interest_completions"]}
            for row in campaign["funnel"]["scenarios"]
        ],
        "task4_keywords": len(strategy["keyword_map"]),
        "task4_seo_pages": len(strategy["seo_map"]),
        "task4_funnel_stages": len(strategy["funnel"]),
        "task4_flows": len(strategy["emails"]),
        "task4_messages": email_messages,
        "task4_budget": strategy["budget"],
        "task4_scenarios": [
            {
                "name": row["name"],
                "customers": row["customers"],
                "media_cac_gbp": row["cac_gbp"],
                "all_in_cost_gbp": row["all_in_acquisition_cost_gbp"],
                "roas": row["roas"],
            }
            for row in strategy["scenarios"]
        ],
    }


def content_stream(page: Any) -> bytes:
    stream = page.get_contents()
    return stream.get_data() if stream is not None else b""


def ensure_inputs() -> None:
    expected = ((MARKETING, 38, EXPECTED_MARKETING_SHA), (PYTHON, 14, EXPECTED_PYTHON_SHA))
    for path, page_count, expected_sha in expected:
        if not path.is_file():
            raise RuntimeError(f"required source PDF is missing: {path}")
        reader = PdfReader(path)
        if len(reader.pages) != page_count:
            raise RuntimeError(f"unexpected page count for {path}: {len(reader.pages)}")
        if sha256(path) != expected_sha:
            raise RuntimeError(f"protected candidate hash changed: {path}")
    if not CAMPAIGN.is_file() or not STRATEGY.is_file():
        raise RuntimeError("required source data is missing")


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "body": ParagraphStyle(
            "portfolio-body", parent=base["BodyText"], fontName="Helvetica", fontSize=9.4,
            leading=13.0, textColor=INK, alignment=TA_LEFT, spaceAfter=0,
        ),
        "small": ParagraphStyle(
            "portfolio-small", parent=base["BodyText"], fontName="Helvetica", fontSize=8.0,
            leading=10.4, textColor=INK,
        ),
        "tiny": ParagraphStyle(
            "portfolio-tiny", parent=base["BodyText"], fontName="Helvetica", fontSize=7.2,
            leading=8.8, textColor=INK,
        ),
        "table": ParagraphStyle(
            "portfolio-table", parent=base["BodyText"], fontName="Helvetica", fontSize=7.55,
            leading=9.3, textColor=INK,
        ),
        "table_head": ParagraphStyle(
            "portfolio-table-head", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=7.4,
            leading=9.0, textColor=WHITE,
        ),
        "link": ParagraphStyle(
            "portfolio-link", parent=base["BodyText"], fontName="Helvetica", fontSize=7.5,
            leading=9.2, textColor=BLUE,
        ),
    }


def para(canvas: Canvas, text: str, x: float, y: float, width: float, style: ParagraphStyle) -> float:
    block = Paragraph(text, style)
    _, height = block.wrap(width, 1000)
    block.drawOn(canvas, x, y - height)
    return y - height


def rule(canvas: Canvas, y: float, color: colors.Color = TEAL) -> None:
    canvas.setStrokeColor(color)
    canvas.setLineWidth(1.3)
    canvas.line(LEFT, y, RIGHT, y)


def footer(canvas: Canvas, label: str, page_number: int) -> None:
    canvas.setStrokeColor(colors.HexColor("#D7E3E5"))
    canvas.setLineWidth(0.45)
    canvas.line(LEFT, BOTTOM + 7 * mm, RIGHT, BOTTOM + 7 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(LEFT, BOTTOM + 3 * mm, label)
    text = f"Portfolio {page_number}"
    canvas.drawRightString(RIGHT, BOTTOM + 3 * mm, text)


def header(canvas: Canvas, kicker: str, title: str, page_number: int) -> float:
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 7.5)
    canvas.drawString(LEFT, TOP, kicker.upper())
    canvas.setFont("Helvetica-Bold", 20)
    canvas.setFillColor(INK)
    canvas.drawString(LEFT, TOP - 10 * mm, title)
    rule(canvas, TOP - 14 * mm)
    footer(canvas, "PROGREE INTERNSHIP • COMPLETE PROJECT PORTFOLIO", page_number)
    return TOP - 21 * mm


def metric_card(canvas: Canvas, x: float, y: float, width: float, height: float, value: str, label: str, accent: colors.Color) -> None:
    canvas.setFillColor(PALE)
    canvas.roundRect(x, y - height, width, height, 3 * mm, fill=1, stroke=0)
    canvas.setFillColor(accent)
    canvas.roundRect(x, y - height, 4 * mm, height, 2 * mm, fill=1, stroke=0)
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 18)
    canvas.drawString(x + 8 * mm, y - 10 * mm, value)
    canvas.setFont("Helvetica", 7.9)
    canvas.setFillColor(INK)
    for index, line in enumerate(label.split("\n")):
        canvas.drawString(x + 8 * mm, y - 16 * mm - index * 3.6 * mm, line)


def draw_table(canvas: Canvas, rows: list[list[str]], widths: list[float], x: float, y: float, style_map: dict[str, ParagraphStyle], font_size: str = "table") -> float:
    data: list[list[Paragraph]] = []
    for row_index, row in enumerate(rows):
        selected = style_map["table_head"] if row_index == 0 else style_map[font_size]
        data.append([Paragraph(cell, selected) for cell in row])
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D7E3E5")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FBFB")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4.2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4.2),
        ("TOPPADDING", (0, 0), (-1, -1), 3.6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.6),
    ]))
    _, height = table.wrap(sum(widths), 1000)
    table.drawOn(canvas, x, y - height)
    return y - height


def draw_cover(canvas: Canvas) -> None:
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.circle(PAGE_WIDTH - 13 * mm, PAGE_HEIGHT - 17 * mm, 23 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.circle(PAGE_WIDTH - 35 * mm, PAGE_HEIGHT - 48 * mm, 8 * mm, fill=1, stroke=0)
    canvas.setStrokeColor(colors.HexColor("#5EC5C7"))
    canvas.setLineWidth(1.3)
    canvas.line(LEFT, PAGE_HEIGHT - 57 * mm, LEFT + 53 * mm, PAGE_HEIGHT - 57 * mm)
    canvas.setFillColor(colors.HexColor("#B9DDDE"))
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(LEFT, PAGE_HEIGHT - 43 * mm, "PROGREE INTERNSHIP")
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 27)
    canvas.drawString(LEFT, PAGE_HEIGHT - 77 * mm, "COMPLETE PROJECT")
    canvas.drawString(LEFT, PAGE_HEIGHT - 89 * mm, "PORTFOLIO")
    canvas.setFont("Helvetica", 13)
    canvas.setFillColor(colors.HexColor("#DDEFF0"))
    canvas.drawString(LEFT, PAGE_HEIGHT - 108 * mm, "Digital Marketing & Branding")
    canvas.drawString(LEFT, PAGE_HEIGHT - 117 * mm, "+")
    canvas.drawString(LEFT, PAGE_HEIGHT - 126 * mm, "Python Programming")
    canvas.setFillColor(colors.HexColor("#B9DDDE"))
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(LEFT, PAGE_HEIGHT - 153 * mm, "COMPLETED TASKS 2, 3 AND 4 IN EACH TRACK")
    canvas.setFont("Helvetica", 9.2)
    canvas.setFillColor(WHITE)
    canvas.drawString(LEFT, PAGE_HEIGHT - 166 * mm, "Evidence-backed portfolio assembly • final review candidate")
    canvas.setFillColor(colors.HexColor("#B9DDDE"))
    canvas.setFont("Helvetica", 8)
    canvas.drawString(LEFT, 25 * mm, "Prepared for owner review • No form submission or certificate claim is made by this document")
    canvas.showPage()


def draw_executive(canvas: Canvas, s: dict[str, ParagraphStyle]) -> None:
    y = header(canvas, "Portfolio overview", "Executive summary", 2)
    y = para(canvas, "This portfolio brings together two completed project tracks: <b>Digital Marketing &amp; Branding</b> and <b>Python Programming</b>. It combines the approved final-candidate reports with concise evidence pages that map the work to its canonical research, code, tests and QA records.", LEFT, y, RIGHT - LEFT, s["body"]) - 4 * mm
    y = para(canvas, "It represents <b>six completed Task 2–4 deliverables</b>. The document distinguishes researched observations, proposed or modeled work, and tested software behavior. It does not claim that any proposed campaign ran, that modeled results were achieved, or that either certificate has been accepted.", LEFT, y, RIGHT - LEFT, s["body"]) - 7 * mm
    card_width = (RIGHT - LEFT - 7 * mm) / 2
    metric_card(canvas, LEFT, y, card_width, 30 * mm, "2", "complete project tracks", TEAL)
    metric_card(canvas, LEFT + card_width + 7 * mm, y, card_width, 30 * mm, "6", "represented Tasks 2–4", GOLD)
    y -= 37 * mm
    rows = [
        ["Evidence category", "What this portfolio shows", "Boundary retained"],
        ["Digital Marketing", "A 38-page audit, campaign and SEO/acquisition report with its complete email appendix.", "Task 2 remains an evidence-limited public-source audit pending organizer acceptance."],
        ["Python Programming", "A 14-page report covering Fibonacci timing, safe file automation and a rule-based chatbot.", "The report preserves code explanations, outputs, tests and stated limitations."],
        ["Verification", "Source preservation, PDF QA, model checks and cross-track unit-test evidence are indexed.", "Technical readiness does not confirm external certificate eligibility."],
    ]
    draw_table(canvas, rows, [34 * mm, 72 * mm, 58 * mm], LEFT, y, s)
    canvas.showPage()


def draw_contents(canvas: Canvas, s: dict[str, ParagraphStyle]) -> None:
    y = header(canvas, "Navigation", "Contents", 3)
    y = para(canvas, "The printed page references use the physical page order of this portfolio. The PDF outline supplies matching internal navigation.", LEFT, y, RIGHT - LEFT, s["body"]) - 5 * mm
    rows = [
        ["Section", "Portfolio page", "Purpose"],
        ["Cover", "1", "Document identity"],
        ["Executive summary", "2", "Scope and evidence boundaries"],
        ["Results at a glance", "4", "Verified project scale and model coverage"],
        ["Digital Marketing & Branding introduction", "5", "Research and proposal boundaries"],
        ["Approved Digital Marketing report", "6–43", "Task 2 audit; Task 3 campaign; Task 4 strategy and email appendix"],
        ["Task 2 / Task 3 / Task 4 / appendix starts", "8 / 12 / 32 / 38", "Internal locations in the approved Marketing report"],
        ["Python Programming introduction", "44", "Implementation scope and evidence"],
        ["Approved Python report", "45–58", "Tasks 2, 3 and 4"],
        ["Python Task 2 / Task 3 / Task 4 starts", "47 / 50 / 53", "Internal locations in the approved Python report"],
        ["Selective verification and project evidence", "59", "Preservation, tests and QA summary"],
        ["Conclusion and source / reproduction index", "60", "Canonical paths and GitHub links"],
    ]
    draw_table(canvas, rows, [76 * mm, 31 * mm, 57 * mm], LEFT, y, s)
    canvas.showPage()


def draw_results(canvas: Canvas, s: dict[str, ParagraphStyle], facts: dict[str, Any]) -> None:
    y = header(canvas, "Verified project results", "Results at a glance", 4)
    y = para(canvas, "The figures below are drawn from the retained task models, approved reports and final-audit records. Proposed and modeled values are identified as such; they are not campaign or customer outcomes.", LEFT, y, RIGHT - LEFT, s["body"]) - 5 * mm
    gap = 4 * mm
    card_width = (RIGHT - LEFT - gap * 2) / 3
    card_height = 25 * mm
    metric_card(canvas, LEFT, y, card_width, card_height, "3", "competitor brands\nresearched", TEAL)
    metric_card(canvas, LEFT + card_width + gap, y, card_width, card_height, str(facts["marketing_actions"]), "planned cross-channel\nactions", GOLD)
    metric_card(canvas, LEFT + 2 * (card_width + gap), y, card_width, card_height, "30", "campaign days\nmodeled", TEAL)
    y -= card_height + 6 * mm
    metric_card(canvas, LEFT, y, card_width, card_height, "4", "planned A/B\nexperiments", GOLD)
    metric_card(canvas, LEFT + card_width + gap, y, card_width, card_height, str(facts["task4_messages"]), "draft email\nmessages", TEAL)
    metric_card(canvas, LEFT + 2 * (card_width + gap), y, card_width, card_height, "129", "cross-track unit tests\nrecorded in final audit", GOLD)
    y -= card_height + 7 * mm
    allocation = facts["marketing_budget_allocation"]
    scenarios = facts["task4_scenarios"]
    rows = [
        ["Workstream", "Verified scope", "Planning / test result"],
        ["RefillLoop campaign", f"{facts['marketing_channels']['Instagram']} Instagram, {facts['marketing_channels']['LinkedIn']} LinkedIn and {facts['marketing_channels']['YouTube']} YouTube actions; {facts['marketing_personas']} audience personas; {facts['marketing_paid_actions']} planned paid placements.", f"Proposed USD {facts['marketing_budget_usd']:,} media budget: Instagram USD {allocation['Instagram']:,}, LinkedIn USD {allocation['LinkedIn']:,}, YouTube USD {allocation['YouTube']:,}."],
        ["Ocean Bottle strategy", f"{facts['task4_keywords']} keyword-intent entries; {facts['task4_seo_pages']}-page SEO map; {facts['task4_funnel_stages']}-stage funnel; {facts['task4_flows']} consent-aware email workflows.", "Proposed GBP 12,000 total / GBP 10,000 media model. Low / base / high: 75 / 160 / 320 modeled customers; media CAC GBP 133.33 / 62.50 / 31.25; ROAS 0.34 / 0.88 / 2.08."],
        ["Python implementation", "Three approved modules: Fibonacci and timing, safe file automation, and a multi-intent rule-based chatbot.", "Final audit records 55 Python-suite tests within 129 cross-track unit tests and two corrected P1 code defects."],
    ]
    draw_table(canvas, rows, [36 * mm, 73 * mm, 55 * mm], LEFT, y, s)
    canvas.showPage()


def draw_marketing_intro(canvas: Canvas, s: dict[str, ParagraphStyle], facts: dict[str, Any]) -> None:
    y = header(canvas, "Track one", "Digital Marketing & Branding", 5)
    y = para(canvas, "The following <b>complete 38-page approved report</b> is imported unchanged. It contains Task 2, Task 3, Task 4 and the supporting Task 4 email appendix in the approved internal order.", LEFT, y, RIGHT - LEFT, s["body"]) - 5 * mm
    rows = [
        ["Task", "Complete included deliverable", "Evidence / claim boundary"],
        ["Task 2", "Competitor footprint audit of Stanley 1913, Hydro Flask and Owala.", "Evidence-limited public-source audit. Historical net-count changes are proxies; HypeAuditor engagement values are vendor estimates; verified 15 Sep–12 Oct posting cadence and organizer acceptance remain unavailable."],
        ["Task 3", "RefillLoop 30-day plan covering 53 actions, three channels, three targeting specifications, four A/B tests and proposed USD 3,000 media pacing.", "Fictional proposed campaign. No product launch, media spend, achieved performance or customer result is claimed."],
        ["Task 4", "Ocean Bottle keyword, SEO, acquisition and email-workflow strategy: 12 keyword entries, four workflows and ten full message drafts.", "Recommendations and GBP financial scenarios are proposed models, not observed marketing activity or customer performance."],
    ]
    y = draw_table(canvas, rows, [24 * mm, 72 * mm, 68 * mm], LEFT, y, s) - 7 * mm
    canvas.setFillColor(PALE_GOLD)
    canvas.roundRect(LEFT, y - 30 * mm, RIGHT - LEFT, 30 * mm, 3 * mm, fill=1, stroke=0)
    para(canvas, "<b>Navigation:</b> the imported report begins on Portfolio page 6. Its Task 2 section begins on page 8, Task 3 on page 12, Task 4 on page 32 and its email appendix on page 38. The portfolio outline contains matching destinations.", LEFT + 5 * mm, y - 6 * mm, RIGHT - LEFT - 10 * mm, s["body"])
    canvas.showPage()


def draw_python_intro(canvas: Canvas, s: dict[str, ParagraphStyle]) -> None:
    y = header(canvas, "Track two", "Python Programming", 44)
    y = para(canvas, "The following <b>complete 14-page approved report</b> is imported unchanged. It covers the three completed programming tasks, including implementation approach, demonstrations, test evidence and the stated limitations.", LEFT, y, RIGHT - LEFT, s["body"]) - 5 * mm
    rows = [
        ["Task", "Implementation focus", "Verified evidence retained"],
        ["Task 2", "Fibonacci sequence generation with input handling and timing measurements.", "Structured output, edge-case coverage, benchmark context and computational limits."],
        ["Task 3", "Safe file organization and text extraction using standard-library filesystem tools.", "Validation, overwrite prevention, error handling and the corrected crafted path-traversal case."],
        ["Task 4", "Multi-intent terminal chatbot using rule-based normalization and conversation routing.", "Input validation, fallback handling, demonstrations, tests and known rule-based limitations."],
    ]
    y = draw_table(canvas, rows, [23 * mm, 73 * mm, 68 * mm], LEFT, y, s) - 7 * mm
    canvas.setFillColor(PALE)
    canvas.roundRect(LEFT, y - 38 * mm, RIGHT - LEFT, 38 * mm, 3 * mm, fill=1, stroke=0)
    para(canvas, "<b>Reproducibility:</b> complete code is retained in <font name='Courier'>internship/task2.py</font>, <font name='Courier'>internship/task3.py</font> and <font name='Courier'>internship/task4.py</font>; corresponding automated tests are in <font name='Courier'>tests/</font>. The final audit records 55 Python-suite tests within its 129 cross-track unit tests.", LEFT + 5 * mm, y - 7 * mm, RIGHT - LEFT - 10 * mm, s["body"])
    para(canvas, "The imported report begins on Portfolio page 45. Its Task 2, Task 3 and Task 4 sections begin on pages 47, 50 and 53 respectively.", LEFT + 5 * mm, y - 27 * mm, RIGHT - LEFT - 10 * mm, s["body"])
    canvas.showPage()


def draw_verification(canvas: Canvas, s: dict[str, ParagraphStyle]) -> None:
    y = header(canvas, "Selective evidence", "Verification and project evidence", 59)
    y = para(canvas, "This portfolio adds navigation and context pages around the approved candidates. The imported report pages are preserved as PDF page objects; they are not rasterized or redesigned. Final mechanical and visual checks are recorded in the package QA report.", LEFT, y, RIGHT - LEFT, s["body"]) - 5 * mm
    rows = [
        ["Evidence", "Portfolio location", "Validation basis"],
        ["Marketing candidate", "Pages 6–43 (38 pages)", "Every imported page is compared with the approved Marketing final candidate for text, content stream, dimensions, rotation and rendered pixels."],
        ["Python candidate", "Pages 45–58 (14 pages)", "Every imported page is compared with the approved Python final candidate using the same preservation checks."],
        ["Research and models", "Canonical digital_marketing/research/ paths", "Task 3 calendar and Task 4 strategy data supply the figures on page 4; claims stay labeled fictional, proposed, modeled or evidence-limited."],
        ["Implementation and tests", "internship/ and tests/", "The retained final audit records 129 cross-track unit tests, including 55 in the Python suite; the current portfolio verifier checks document assembly."],
        ["Historical QA", "evidence/ultimate_final_review/", "Preservation manifests, rendered-page review, privacy scan, findings and remediation records remain in their canonical locations."],
    ]
    y = draw_table(canvas, rows, [34 * mm, 42 * mm, 88 * mm], LEFT, y, s) - 7 * mm
    canvas.setFillColor(PALE_GOLD)
    canvas.roundRect(LEFT, y - 31 * mm, RIGHT - LEFT, 31 * mm, 3 * mm, fill=1, stroke=0)
    para(canvas, "<b>Important qualification:</b> technical preservation and QA show that the files are ready for owner review. They do not establish form acceptance, two-track certificate eligibility or organizer acceptance of Marketing Task 2's documented evidence limitations.", LEFT + 5 * mm, y - 7 * mm, RIGHT - LEFT - 10 * mm, s["body"])
    canvas.showPage()


SOURCE_INDEX = [
    ("Python Task 2", "internship/task2.py", f"{GITHUB}/blob/main/internship/task2.py"),
    ("Python Task 3", "internship/task3.py", f"{GITHUB}/blob/main/internship/task3.py"),
    ("Python Task 4", "internship/task4.py", f"{GITHUB}/blob/main/internship/task4.py"),
    ("Python tests", "tests/", f"{GITHUB}/tree/main/tests"),
    ("Marketing Task 2 research", "digital_marketing/research/task2/", f"{GITHUB}/tree/main/digital_marketing/research/task2"),
    ("Marketing Task 3 model", "digital_marketing/research/task3/build_campaign.py", f"{GITHUB}/blob/main/digital_marketing/research/task3/build_campaign.py"),
    ("Marketing Task 4 strategy", "digital_marketing/research/task4/build_strategy.py", f"{GITHUB}/blob/main/digital_marketing/research/task4/build_strategy.py"),
    ("Marketing Task 4 workflows", "digital_marketing/research/task4/email_workflows.py", f"{GITHUB}/blob/main/digital_marketing/research/task4/email_workflows.py"),
    ("Final audit QA", "evidence/ultimate_final_review/QA.md", f"{GITHUB}/blob/main/evidence/ultimate_final_review/QA.md"),
    ("Final audit manifest", "evidence/ultimate_final_review/manifest.json", f"{GITHUB}/blob/main/evidence/ultimate_final_review/manifest.json"),
]


def draw_conclusion(canvas: Canvas, s: dict[str, ParagraphStyle]) -> None:
    y = header(canvas, "Close and reproduce", "Conclusion and source index", 60)
    y = para(canvas, "This single-PDF review candidate presents Digital Marketing &amp; Branding first and Python Programming second, with all 52 approved candidate-report pages preserved in order. The project remains transparent about proposed work, model outputs and the unresolved administrative conditions for submission.", LEFT, y, RIGHT - LEFT, s["body"]) - 5 * mm
    canvas.setFillColor(PALE)
    canvas.roundRect(LEFT, y - 19 * mm, RIGHT - LEFT, 19 * mm, 3 * mm, fill=1, stroke=0)
    para(canvas, "<b>Reproduce:</b> from the repository root, run <font name='Courier'>python tools/build_complete_internship_portfolio.py --replace</font> followed by <font name='Courier'>python tools/verify_complete_internship_portfolio.py</font>. The verification report and manifest are written into this package.", LEFT + 5 * mm, y - 5 * mm, RIGHT - LEFT - 10 * mm, s["small"])
    y -= 26 * mm
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(LEFT, y, "CANONICAL SOURCE AND REPRODUCTION INDEX")
    y -= 5 * mm
    row_height = 10.5 * mm
    table_width = RIGHT - LEFT
    col_one = 45 * mm
    col_two = 88 * mm
    col_three = table_width - col_one - col_two
    canvas.setFillColor(NAVY)
    canvas.rect(LEFT, y - 7 * mm, table_width, 7 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 7.5)
    canvas.drawString(LEFT + 4, y - 4.6 * mm, "Task / evidence")
    canvas.drawString(LEFT + col_one + 4, y - 4.6 * mm, "Canonical repository path")
    canvas.drawString(LEFT + col_one + col_two + 4, y - 4.6 * mm, "Link")
    y -= 7 * mm
    for index, (label, path, url) in enumerate(SOURCE_INDEX):
        fill = colors.HexColor("#F8FBFB") if index % 2 == 0 else WHITE
        canvas.setFillColor(fill)
        canvas.rect(LEFT, y - row_height, table_width, row_height, fill=1, stroke=0)
        canvas.setStrokeColor(colors.HexColor("#D7E3E5"))
        canvas.setLineWidth(0.35)
        canvas.rect(LEFT, y - row_height, table_width, row_height, fill=0, stroke=1)
        canvas.setFillColor(INK)
        canvas.setFont("Helvetica", 7.35)
        canvas.drawString(LEFT + 4, y - 5.8 * mm, label)
        canvas.setFont("Courier", 6.5)
        canvas.drawString(LEFT + col_one + 4, y - 5.8 * mm, path)
        link_label = "Open on GitHub"
        link_x = LEFT + col_one + col_two + 4
        canvas.setFont("Helvetica-Bold", 7.2)
        canvas.setFillColor(BLUE)
        canvas.drawString(link_x, y - 5.8 * mm, link_label)
        link_width = stringWidth(link_label, "Helvetica-Bold", 7.2)
        canvas.linkURL(url, (link_x, y - 7.7 * mm, link_x + link_width, y - 3.6 * mm), relative=0, thickness=0)
        y -= row_height
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.3)
    canvas.drawString(LEFT, BOTTOM + 12 * mm, "Portfolio ends here. Submission remains an owner decision; no form or external service has been used.")
    canvas.showPage()


def create_authored_pages(path: Path, facts: dict[str, Any]) -> None:
    s = styles()
    canvas = Canvas(str(path), pagesize=A4, pageCompression=1)
    canvas.setTitle("Progree Internship — Complete Project Portfolio")
    canvas.setAuthor("Anonymous internship project")
    canvas.setSubject("Digital Marketing and Python Tasks 2–4 portfolio; Marketing Task 2 remains evidence-limited")
    canvas.setCreator("Progree portfolio assembly")
    draw_cover(canvas)
    draw_executive(canvas, s)
    draw_contents(canvas, s)
    draw_results(canvas, s, facts)
    draw_marketing_intro(canvas, s, facts)
    draw_python_intro(canvas, s)
    draw_verification(canvas, s)
    draw_conclusion(canvas, s)
    canvas.save()


def build_pdf(stage: Path) -> None:
    authored = PdfReader(stage / "authored.pdf")
    marketing = PdfReader(MARKETING)
    python = PdfReader(PYTHON)
    if len(authored.pages) != 8:
        raise RuntimeError(f"authored page count changed: {len(authored.pages)}")
    writer = PdfWriter()
    for page in authored.pages[:5]:
        writer.add_page(page)
    for page in marketing.pages:
        writer.add_page(page)
    writer.add_page(authored.pages[5])
    for page in python.pages:
        writer.add_page(page)
    for page in authored.pages[6:]:
        writer.add_page(page)
    if len(writer.pages) != 60:
        raise RuntimeError(f"unexpected portfolio page count: {len(writer.pages)}")
    cover = writer.add_outline_item("Cover", 0)
    writer.add_outline_item("Executive summary", 1)
    writer.add_outline_item("Contents", 2)
    writer.add_outline_item("Results at a glance", 3)
    marketing_root = writer.add_outline_item("Digital Marketing & Branding", 4)
    writer.add_outline_item("Track introduction", 4, parent=marketing_root)
    writer.add_outline_item("Approved report", 5, parent=marketing_root)
    writer.add_outline_item("Task 2 — evidence-limited public-source audit", 7, parent=marketing_root)
    writer.add_outline_item("Task 3 — RefillLoop proposed 30-day campaign", 11, parent=marketing_root)
    writer.add_outline_item("Task 4 — Ocean Bottle proposed SEO strategy", 31, parent=marketing_root)
    writer.add_outline_item("Task 4 supporting appendix — proposed email workflows", 37, parent=marketing_root)
    python_root = writer.add_outline_item("Python Programming", 43)
    writer.add_outline_item("Track introduction", 43, parent=python_root)
    writer.add_outline_item("Approved report", 44, parent=python_root)
    writer.add_outline_item("Task 2 — Fibonacci and timing", 46, parent=python_root)
    writer.add_outline_item("Task 3 — safe file automation", 49, parent=python_root)
    writer.add_outline_item("Task 4 — multi-intent rule-based chatbot", 52, parent=python_root)
    writer.add_outline_item("Selective verification and project evidence", 58)
    writer.add_outline_item("Conclusion and source / reproduction index", 59)
    writer.set_page_label(0, 59, PageLabelStyle.DECIMAL, prefix="Portfolio ", start=1)
    writer.add_metadata({
        "/Title": "Progree Internship — Complete Project Portfolio",
        "/Author": "Anonymous internship project",
        "/Subject": "Digital Marketing and Python Tasks 2–4 portfolio; Marketing Task 2 remains evidence-limited and pending acceptance",
        "/Creator": "Progree portfolio assembly",
        "/Producer": "pypdf",
    })
    with (stage / "portfolio.pdf").open("wb") as handle:
        writer.write(handle)


def page_map() -> list[dict[str, Any]]:
    return [
        {"section": "Cover", "pages": [1, 1]},
        {"section": "Executive summary", "pages": [2, 2]},
        {"section": "Contents", "pages": [3, 3]},
        {"section": "Results at a glance", "pages": [4, 4]},
        {"section": "Digital Marketing introduction", "pages": [5, 5]},
        {"section": "Approved Digital Marketing candidate", "pages": [6, 43], "source_pages": [1, 38]},
        {"section": "Python introduction", "pages": [44, 44]},
        {"section": "Approved Python candidate", "pages": [45, 58], "source_pages": [1, 14]},
        {"section": "Selective verification and project evidence", "pages": [59, 59]},
        {"section": "Conclusion and source / reproduction index", "pages": [60, 60]},
    ]


def output_metadata(path: Path) -> dict[str, Any]:
    return {"path": path.relative_to(ROOT).as_posix(), "pages": len(PdfReader(path).pages), "bytes": path.stat().st_size, "sha256": sha256(path)}


def write_initial_package(facts: dict[str, Any]) -> None:
    final_info = output_metadata(OUTPUT)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    manifest = {
        "schema": "progree-complete-portfolio-v1",
        "status": "built_pending_final_verification",
        "source_commit": commit,
        "generated_by": "tools/build_complete_internship_portfolio.py",
        "output": final_info,
        "source_candidates": [
            {"path": MARKETING.relative_to(ROOT).as_posix(), "pages": 38, "bytes": MARKETING.stat().st_size, "sha256": sha256(MARKETING), "portfolio_pages": [6, 43]},
            {"path": PYTHON.relative_to(ROOT).as_posix(), "pages": 14, "bytes": PYTHON.stat().st_size, "sha256": sha256(PYTHON), "portfolio_pages": [45, 58]},
        ],
        "page_map": page_map(),
        "verified_source_facts": facts,
        "administrative_qualification": "This review candidate satisfies the owner-requested one-file package. The form's single-domain selection does not confirm two-track certificate eligibility, and Marketing Task 2 remains evidence-limited pending organizer acceptance.",
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    README.write_text(
        "# Progree complete internship portfolio\n\n"
        "## Primary upload candidate\n\n"
        f"`01_Progree_Complete_Internship_Portfolio.pdf` is the single owner-review PDF. It places Digital Marketing & Branding first and Python Programming second, and includes Tasks 2, 3 and 4 for both tracks.\n\n"
        f"- Pages: **{final_info['pages']}**\n"
        f"- Bytes: **{final_info['bytes']:,}**\n"
        f"- SHA-256: `{final_info['sha256']}`\n"
        "- Upload-size check: below the visible 10 MB limit supplied by the owner.\n"
        "- Reproduce: `python tools/build_complete_internship_portfolio.py --replace` then `python tools/verify_complete_internship_portfolio.py`.\n\n"
        "## Included order\n\n"
        "1. New portfolio cover, executive summary, contents, results and Digital Marketing introduction\n"
        "2. Complete 38-page approved Digital Marketing final candidate\n"
        "3. Python introduction\n"
        "4. Complete 14-page approved Python final candidate\n"
        "5. Verification evidence and source/reproduction index\n\n"
        "## Important owner qualification\n\n"
        "Marketing Task 2 remains a transparent evidence-limited public-source audit. It does not establish verified posting cadence for the requested observation window or organizer acceptance. The owner-supplied form details describe one upload and a single domain choice; this one-file portfolio does not prove that one response earns two track certificates. No form was submitted.\n\n"
        "`manifest.json` and `QA/FINAL_VERIFICATION.md` provide machine-readable traceability and final verification.\n",
        encoding="utf-8",
    )
    QA.write_text(
        "# Final verification\n\n"
        "Run `python tools/verify_complete_internship_portfolio.py` to replace this build placeholder with the completed verification record.\n",
        encoding="utf-8",
    )


def remove_previous_package() -> None:
    """Remove only a package previously made by this tool, never source material."""
    allowed_files = {OUTPUT, README, MANIFEST, QA}
    actual_files = {path for path in FINAL.rglob("*") if path.is_file()}
    unexpected = actual_files - allowed_files
    if unexpected:
        raise RuntimeError(f"refusing to remove unexpected final-package files: {sorted(str(path) for path in unexpected)}")
    for path in allowed_files:
        if path.exists():
            path.unlink()
    qa_directory = FINAL / "QA"
    if qa_directory.exists():
        qa_directory.rmdir()
    FINAL.rmdir()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replace", action="store_true", help="safely replace only a package previously created by this tool")
    arguments = parser.parse_args()
    ensure_inputs()
    if FINAL.exists() and any(FINAL.iterdir()):
        if not arguments.replace:
            raise RuntimeError(f"final package already exists; rerun with --replace: {FINAL}")
        remove_previous_package()
    FINAL.mkdir(parents=True, exist_ok=False)
    (FINAL / "QA").mkdir()
    facts = source_facts()
    with tempfile.TemporaryDirectory(prefix="progree-complete-portfolio-", dir="/tmp") as directory:
        stage = Path(directory)
        create_authored_pages(stage / "authored.pdf", facts)
        build_pdf(stage)
        # /tmp and the checkout can be different filesystems in the cloud
        # environment, so an atomic rename is not available across this
        # boundary.  The source candidates are never touched; this copies only
        # the newly staged portfolio into its new package location.
        shutil.copyfile(stage / "portfolio.pdf", OUTPUT)
    write_initial_package(facts)
    print(json.dumps({"output": output_metadata(OUTPUT), "page_map": page_map()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
