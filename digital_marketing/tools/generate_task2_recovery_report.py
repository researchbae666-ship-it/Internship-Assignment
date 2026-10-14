"""Generate a four-page partial-evidence audit; never label it completed."""

import json
import re
import sys
from pathlib import Path
import reportlab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "digital_marketing/research/task2/recovery"
EVIDENCE = ROOT / "digital_marketing/evidence/task2/recovery"
sys.path.insert(0, str(RESEARCH))
from build_audit import validate
from metrics import calculate

NAVY = colors.HexColor("#12324A")
TEAL = colors.HexColor("#197D82")
INK = colors.HexColor("#1E2A32")
FONT_DIR = Path(reportlab.__file__).resolve().parent / "fonts"
pdfmetrics.registerFont(TTFont("AuditSans", str(FONT_DIR / "Vera.ttf")))
pdfmetrics.registerFont(TTFont("AuditSans-Bold", str(FONT_DIR / "VeraBd.ttf")))
pdfmetrics.registerFontFamily("AuditSans", normal="AuditSans", bold="AuditSans-Bold")


def paragraph(value, style):
    return Paragraph(str(value).replace("&", "&amp;"), style)


def table(rows, widths, style):
    header = ParagraphStyle("RecoveryHeader", parent=style, textColor=colors.white, fontName="AuditSans-Bold")
    cells = [[paragraph(cell, header if index == 0 else style) for cell in row] for index, row in enumerate(rows)]
    result = Table(cells, colWidths=widths, repeatRows=1)
    result.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("GRID", (0, 0), (-1, -1), .3, colors.HexColor("#B7C8CD")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EAF3F3")]), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    return result


def footer(canvas, document):
    canvas.saveState()
    canvas.setFont("AuditSans", 8)
    canvas.setFillColor(NAVY)
    canvas.drawString(15*mm, 10*mm, "TASK 2 | PARTIAL EVIDENCE DRAFT | PERIOD METRICS NOT COMPLETED")
    canvas.drawRightString(document.pagesize[0]-15*mm, 10*mm, f"Page {document.page}")
    canvas.restoreState()


def build_pdf(data, sources, browsers, output):
    errors = validate(data, sources, browsers)
    if errors:
        raise ValueError("Source validation failed: " + "; ".join(errors))
    styles = getSampleStyleSheet()
    title = ParagraphStyle("RecoveryTitle", parent=styles["Heading1"], fontName="AuditSans-Bold", fontSize=20, leading=24, textColor=NAVY, spaceAfter=8)
    heading = ParagraphStyle("RecoveryHeading", parent=styles["Heading2"], fontName="AuditSans-Bold", fontSize=12, leading=15, textColor=TEAL, spaceBefore=7, spaceAfter=5)
    body = ParagraphStyle("RecoveryBody", parent=styles["BodyText"], fontName="AuditSans", fontSize=9.2, leading=12, textColor=INK, spaceAfter=6)
    small = ParagraphStyle("RecoveryTable", parent=body, fontSize=8.5, leading=10.2, spaceAfter=0)
    p = lambda text: paragraph(text, body)
    h = lambda text: paragraph(text, heading)
    story = [paragraph("Reusable hydration: competitor footprint audit", title), p("Stanley 1913 • Hydro Flask • Owala | Partial evidence-backed recovery draft | 14 October 2026"),
             p("<b>Review status:</b> qualitative source collection recovered; dated posting cadence and visible engagement remain evidence-blocked. This document is not a completed measured audit."),
             h("Scope and common period"), p("Approved post window: <b>15 September–12 October 2026 UTC (28 days)</b>. Website and profile snapshots were collected on 14 October 2026 UTC, outside that window. They support current positioning observations only. These brands share reusable hydration/insulated-drinkware categories; their wider portfolios are not assumed identical."),
             h("Verified footprint and access")]
    rows = [["Brand", "Verified official links", "Current collection outcome"]]
    for brand in ("Stanley 1913", "Hydro Flask", "Owala"):
        accounts = [account for account in data["accounts"] if account["brand"] == brand]
        website = next(source for source in sources if source["id"] == accounts[0]["verification_source_id"])
        verified = [account for account in accounts if account["verified"]]
        rows.append([brand, website["url"] + "<br/>" + "<br/>".join(account["platform"] + ": " + account["account_url"] for account in verified), "Website HTTP 200; Instagram HTTP 200 with profile text only. YouTube CONNECT 403 (no origin status); LinkedIn candidates HTTP 999. Owala YouTube and all LinkedIn candidate identities remain unverified." if brand == "Owala" else "Website HTTP 200; Instagram HTTP 200 with profile text only. Official YouTube link verified, content blocked by CONNECT 403; LinkedIn candidate HTTP 999 and unverified."])
    story.extend([table(rows, [32*mm, 112*mm, 116*mm], small), h("Evidence coverage"), p("Three websites and three official Instagram profiles retrieved. Five social links verified from brand websites: three Instagram and two YouTube. Twelve direct URL requests plus six unauthenticated browser captures are retained. <b>Zero dated posts recovered</b> is a collection result, not evidence of zero account activity. No passwords, private analytics or access-control bypass were used."), PageBreak()])

    story.extend([paragraph("Positioning and creative: supported comparisons", title), p("Direct quotations and captured visuals are observations. Audience, emotional appeal and positioning conclusions below are interpretations, not measured audience demographics or campaign results.")])
    rows = [["Brand", "Source-backed observations", "Interpretation / boundary"]]
    for brand in ("Stanley 1913", "Hydro Flask", "Owala"):
        facts = [fact for fact in data["facts"] if fact["brand"] == brand]
        rows.append([brand, "<br/>".join(f"<b>[{fact['id']}]</b> {fact['quote']}" for fact in facts), "<br/><br/>".join(fact["interpretation"] for fact in facts[:2]) + "<br/><br/>Full claim-by-claim interpretations and limitations are retained in observations.json."])
    story.extend([table(rows, [28*mm, 104*mm, 128*mm], small), h("Cross-channel consistency and conversion paths"), p("Stanley's collaboration/club pathways and #BuiltForLife bio offer a lifestyle/durability framing. Hydro Flask's seasonal edition, finder and hydration/style bio mix product choice with self-expression. Owala's benefit-led product labels, Color Drop and playful bio combine utility with novelty. Instagram highlight labels provide navigation clues only; no recurring post format, creator-post programme, engagement tactic effectiveness, LinkedIn strategy or YouTube editorial pattern was verified."), p("Stanley and Hydro Flask homepage screenshots were visually inspected. Owala styling/assets loaded incompletely: its colour description is attributed image alt text, not a complete visual identity judgement. Snapshot IDs, quoted-source IDs and hashes are retained alongside this report."), PageBreak()])

    story.extend([paragraph("Period metrics: explicit missing-value treatment", title), p("Each unavailable result is null in the structured worksheet. Rounded profile totals are not period post counts or exact engagement denominators.")])
    measures = calculate(data)
    rows = [["Brand", "Platform", "Retained dated sample", "28-day cadence", "Visible interaction proxy"]]
    for row in measures["measurements"]:
        rows.append([row["brand"], row["platform"], "0 recovered; activity unknown", "Unavailable", "Unavailable"])
    displays = []
    for account in data["accounts"]:
        if account["platform"] == "Instagram":
            match = re.search(r"([\d.,]+[KM]?) Followers", account["profile_html_display"] or "")
            displays.append(f"{account['brand']} HTML {match.group(1) if match else 'unavailable'} versus browser {account['profile_display'] or 'unavailable'}")
    story.extend([table(rows, [38*mm, 30*mm, 69*mm, 53*mm, 70*mm], small), h("Calculation rules"), p("With a verified full inventory: posts per week = observed period post count / 28 × 7. With a nonempty incomplete sample, the same arithmetic is labelled observed minimum activity. With no verifiable sample, cadence is unavailable. Instagram proxy = (visible likes + visible comments) / exact visible followers × 100; LinkedIn uses reactions + comments. YouTube views are not interchangeable with follower denominators. Every post requires official-account identity, URL, publication and collection dates, evidence and metric precision."), h("Profile-display discrepancy"), p("Rounded displays differed by response method: " + "; ".join(displays) + ". These are verbatim retrieval snapshots, not precise follower estimates or growth measurements. Neither method's figure is substituted into the unavailable period engagement calculation."), PageBreak()])

    story.extend([paragraph("Recommendations and completion gate", title), p("These are specific RefillLoop market-entry hypotheses grounded in accessible cues, not proven unmet demand or claims that competitors lack a strategy.")])
    rows = [["Priority / proposal", "Evidence / practical action", "Validation before asserting a gap"]]
    for recommendation in data["recommendations"]:
        rows.append([recommendation["priority"] + " — " + recommendation["title"], "[" + ", ".join(recommendation["evidence_ids"]) + "] " + recommendation["proposal"], recommendation["validation"]])
    story.extend([table(rows, [49*mm, 127*mm, 84*mm], small), h("What would unblock the measured audit?"), p("Supply the independent reviewer's source-linked handoff. For each brand/platform, provide a dated public post inventory covering the full 28-day window, or a clearly labelled comparable sample. Public screenshots should show official handle, post URL/date, visible likes/reactions/comments, and the collection date; provide the public follower count and its precision at collection if available. A complete-inventory assertion needs evidence of pagination/window boundaries. No private account credentials or analytics are needed."), h("Sources and reproducibility"), p("Website snapshots: https://www.stanley1913.com/ ; https://www.hydroflask.com/ ; https://owalalife.com/ . Official Instagram sources: https://www.instagram.com/stanley1913_brand/ ; https://www.instagram.com/hydroflask/ ; https://www.instagram.com/owala/ . Official YouTube links: https://www.youtube.com/@Stanley1913 ; https://www.youtube.com/user/hydroflask . Sources collected 14 October 2026 UTC; exact timestamps/statuses/digests in source_records.json and browser_records.json. Fact IDs S1–S4, H1–H4, O1–O4 resolve to those records in observations.json."), p("Reproduction: research/task2/recovery/collect_sources.py, collect_browser.py, build_audit.py and test_recovery.py. Original 13 October proxy-failure records remain unchanged outside recovery/. Alternative completion path: import attributed reviewer/public screenshot records, then recompute supported metrics; keep inaccessible fields unavailable. Until that evidence arrives, quantitative comparisons and final completion approval remain open.")])
    output.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(str(output), pagesize=landscape(A4), leftMargin=15*mm, rightMargin=15*mm, topMargin=14*mm, bottomMargin=20*mm, title="Task 2 Partial Competitor Audit Recovery Draft", author="Internship project")
    document.build(story, onFirstPage=footer, onLaterPages=footer)


def main():
    data = json.loads((RESEARCH / "observations.json").read_text())
    sources = json.loads((EVIDENCE / "source_records.json").read_text())
    browsers = json.loads((EVIDENCE / "browser_records.json").read_text())
    output = ROOT / "digital_marketing/deliverables/DM_Task2_Competitor_Audit_RECOVERY_DRAFT.pdf"
    build_pdf(data, sources, browsers, output)
    print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
