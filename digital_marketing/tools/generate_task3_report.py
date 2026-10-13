"""Generate the RefillLoop Task 3 PDF from validated campaign JSON."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (PageBreak, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)


DM_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DM_ROOT / "research" / "task3"))
from build_campaign import validate  # noqa: E402


NAVY = colors.HexColor("#12324A")
TEAL = colors.HexColor("#197D82")
MIST = colors.HexColor("#EAF3F3")
GOLD = colors.HexColor("#D9A441")
INK = colors.HexColor("#1E2A32")


def para(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text.replace("&", "&amp;"), style)


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(TEAL)
    canvas.setLineWidth(0.8)
    canvas.line(15 * mm, 14 * mm, landscape(A4)[0] - 15 * mm, 14 * mm)
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(15 * mm, 8.5 * mm, "RefillLoop | fictional proposed campaign | Task 3")
    canvas.drawRightString(landscape(A4)[0] - 15 * mm, 8.5 * mm, f"Page {doc.page}")
    canvas.restoreState()


def table(rows, widths, small, header=True):
    converted = [[para(str(cell), small) for cell in row] for row in rows]
    result = Table(converted, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY) if header else ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white) if header else ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#B7C8CD")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, MIST]),
    ]))
    return result


def build_pdf(data: dict, output: Path) -> None:
    errors = validate(data)
    if errors:
        raise ValueError("Campaign validation failed: " + "; ".join(errors))
    output.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=27, leading=31, textColor=NAVY, alignment=TA_CENTER, spaceAfter=12)
    subtitle = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=12, leading=16, textColor=TEAL, alignment=TA_CENTER)
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=NAVY, spaceBefore=7, spaceAfter=8)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=TEAL, spaceBefore=6, spaceAfter=4)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=9, leading=12, textColor=INK, spaceAfter=6)
    small = ParagraphStyle("Small", parent=body, fontSize=7.1, leading=8.5, spaceAfter=0)
    doc = SimpleDocTemplate(str(output), pagesize=landscape(A4), leftMargin=15*mm, rightMargin=15*mm, topMargin=14*mm, bottomMargin=20*mm, title="RefillLoop 30-Day Campaign Roadmap", author="Internship project")
    story = []
    c = data["campaign"]
    story += [Spacer(1, 28*mm), para("REFILLLOOP", title), para("30-Day Multi-Channel Campaign Execution Roadmap", subtitle), Spacer(1, 8*mm), para("Instagram • LinkedIn • YouTube", subtitle), Spacer(1, 16*mm), para("A fictional proposed modular reusable-hydration campaign. All product features, audiences, budgets, KPI values, and outcomes are planning assumptions or targets—not live-market facts, customer results, or a published campaign.", body), PageBreak()]

    story += [para("Campaign premise and positioning", h1), para(c["classification"], body), para(c["positioning"], body), para("Proposed differentiation", h2), table([["Route", "Planning use"]] + [[x, "A campaign design choice to test; not a verified market advantage."] for x in c["differentiation"]], [62*mm, 180*mm], body), Spacer(1, 5*mm), para("30-day narrative", h2), para("Days 1–7 frame everyday refill friction; Days 8–12 reveal the concept; Days 13–18 educate around proposed routines; Days 19–22 run planned message tests; Days 23–30 invite early-access interest and capture learning for a future authorized launch.", body), para("Product and pricing assumptions", h2)]
    for assumption in c["product_assumptions"]:
        story.append(para("• " + assumption, body))
    story.append(PageBreak())

    story += [para("Audience, objectives, and channel roles", h1), para("Personas are planning devices, not research-derived customer profiles.", body)]
    persona_rows = [["Persona", "Motivation / pain point", "Targeting assumption"]] + [[p["name"], p["motivation"] + "<br/>" + p["pain_point"], p["targeting"]] for p in data["personas"]]
    story += [table(persona_rows, [58*mm, 88*mm, 96*mm], body), Spacer(1, 5*mm), para("SMART objectives", h2)]
    objective_rows = [["Objective", "Target / assumption", "Measurement"]] + [[o["objective"], o["smart_target"] + "<br/><i>Baseline: " + o["baseline_assumption"] + "</i>", o["measurement"]] for o in data["objectives"]]
    story += [table(objective_rows, [55*mm, 128*mm, 59*mm], body), Spacer(1, 5*mm), para("Channel roles", h2), para("Instagram delivers routine prompts, visual saves, polls, and community response. LinkedIn delivers professional storytelling, workplace use cases, and toolkit content. YouTube uses Shorts for discovery and long-form video for concept demonstration and implementation detail.", body), PageBreak()]

    story += [para("Targeting and keyword strategy", h1), para("All filters below are proposed and must be checked against current platform policy, account eligibility, controls, consent obligations, and minimum-audience rules before launch. They are not evidence that a filter is available or that an audience will perform.", body)]
    targeting_rows = [["Platform", "Proposed audience / inclusion", "Placement, event, and safeguard"]]
    for platform, spec in data["targeting_specifications"].items():
        targeting_rows.append([platform, f"<b>Market:</b> {spec['geography']}<br/><b>Language:</b> {spec['language']}<br/><b>Age:</b> {spec['age']}<br/><b>Include:</b> {spec['inclusion']}", f"<b>Placement:</b> {spec['placement']}<br/><b>Event:</b> {spec['conversion_event']}<br/><b>Exclude:</b> {spec['exclusion']}<br/><b>Policy:</b> {spec['privacy_policy']}"])
    story += [table(targeting_rows, [31*mm, 112*mm, 99*mm], small), Spacer(1, 5*mm), para("Keyword and tag clusters", h2)]
    clusters = {}
    for item in data["actions"]:
        strategy = item["keyword_strategy"]
        clusters.setdefault(strategy["cluster"], strategy)
    keyword_rows = [["Cluster", "Primary and supporting terms", "Discovery intent / proposed tags"]]
    for name, strategy in sorted(clusters.items()):
        keyword_rows.append([name.title(), "<b>Primary:</b> " + strategy["primary_keyword"] + "<br/>" + ", ".join(strategy["supporting_keywords"]), strategy["search_discovery_intent"] + "<br/>" + ", ".join(strategy["hashtags_or_video_tags"])])
    story += [table(keyword_rows, [42*mm, 104*mm, 96*mm], body), PageBreak()]

    story += [para("Paid media, measurement, testing, and safeguards", h1)]
    budget = data["budget"]
    budget_rows = [["Platform", "Proposed media allocation", "Role"]] + [[p, f"{budget['currency']} {amount:,.0f}", "Amplify the platform role; no spend incurred."] for p, amount in budget["allocation"].items()] + [["Total", f"{budget['currency']} {budget['total']:,.0f}", budget["assumption"]]]
    story += [table(budget_rows, [55*mm, 65*mm, 122*mm], body), para("Budget pacing", h2)]
    pacing_rows = [["Day / action", "Platform / phase", "Proposed spend", "Purpose"]]
    for row in data["budget_pacing"]:
        pacing_rows.append([f"Day {row['day']}<br/>{row['action_id']}", row["platform"] + "<br/>" + row["phase"], f"USD {row['proposed_spend_usd']:,.0f}", row["note"]])
    story += [table(pacing_rows, [38*mm, 42*mm, 35*mm, 127*mm], small), PageBreak()]

    funnel = data["funnel"]
    story += [para("Funnel mathematics and measurement", h1), para("Formula: " + funnel["formula"] + ". Rates are decimal assumptions; outputs are modeled planning arithmetic, not benchmarks or forecasts.", body)]
    funnel_rows = [["Scenario", "Impressions", "CTR", "Landing sessions", "Form rate", "Modeled completions", "Classification"]]
    for row in funnel["scenarios"]:
        funnel_rows.append([row["name"], f"{row['impressions']:,}", f"{row['click_through_rate']:.1%}", f"{row['landing_sessions']:,.0f}", f"{row['form_completion_rate']:.1%}", f"{row['interest_completions']:,.2f}", row["classification"]])
    story += [table(funnel_rows, [25*mm, 28*mm, 20*mm, 32*mm, 24*mm, 32*mm, 81*mm], small), para("Dashboard specification", h2), para("Track platform-native reach and video attention separately; tag campaign links with source, medium, campaign, content, and test variant; record consent-aware interest-form completions; and maintain a qualitative feedback-theme log. No metric becomes a business result until a real authorized campaign runs.", body), para("A/B testing and optimization rules", h2)]
    ab_rows = [["Test", "Hypothesis and variants", "Audience / metric / decision"]]
    for test in data["ab_tests"]:
        ab_rows.append([test["id"], test["hypothesis"] + "<br/><b>Control:</b> " + test["control"] + "<br/><b>Treatment:</b> " + test["treatment"], "<b>Audience:</b> " + test["audience"] + "<br/><b>Metric:</b> " + test["primary_metric"] + "<br/><b>Decision:</b> " + test["decision_criterion"]])
    story += [table(ab_rows, [22*mm, 102*mm, 118*mm], small), para("Risk register", h2)]
    risk_rows = [["Risk", "Control / contingency owner"] , ["Fictional concept mistaken for a live product", "Use a clear proposed-concept disclaimer; social lead pauses or corrects creative."], ["Unsupported environmental, material, or health claim", "Legal/claim review before release; substitute factual concept language."], ["Comment or consent issue", "Community lead uses an approved response and escalation path."], ["Production or platform-delivery delay", "Keep a tested static fallback and reschedule with a logged reason."]]
    story += [table(risk_rows, [92*mm, 150*mm], body), PageBreak()]

    story += [para("Editorial calendar", h1), para("Every action below is planned. Proposed publication times are test variables in the audience’s local time; they are not evidence of optimal behavior.", body)]
    actions = data["actions"]
    for start in range(1, 31, 3):
        subset = [item for item in actions if start <= item["day"] < start + 3]
        story.append(para(f"Days {start}–{min(start + 2, 30)}", h2))
        rows = [["Day / platform", "Format & theme", "Creative / copy or script", "CTA / distribution", "Time / KPI", "Owner / production"]]
        for item in subset:
            rows.append([
                f"Day {item['day']}<br/>{item['platform']}<br/>{item['phase']}",
                f"{item['content_format']}<br/>{item['campaign_theme']}<br/><b>Keyword:</b> {item['keyword_strategy']['primary_keyword']}<br/><b>Tags:</b> {', '.join(item['keyword_strategy']['hashtags_or_video_tags'])}",
                item["creative_concept"] + "<br/><i>" + item["copy_or_script"] + "</i>",
                item["cta"] + "<br/>" + item["distribution"],
                item["proposed_publication_time"] + "<br/>" + item["kpi"],
                item["responsible_role"] + "<br/>" + item["production_requirements"],
            ])
        story.append(table(rows, [21*mm, 33*mm, 68*mm, 33*mm, 38*mm, 49*mm], small))
        story.append(Spacer(1, 3*mm))
        if start + 3 <= 30:
            story.append(PageBreak())

    story += [PageBreak(), para("Copy, implementation, and references", h1), para("Copy variations", h2)]
    for text in ["Utility: ‘Your day changes. Your refill routine can have a plan.’ — Explore the concept.", "Routine: ‘One small cue can make the next refill easier to remember.’ — Try a habit stack.", "Professional: ‘Workplace wellbeing ideas need an owner, a cue, and a way to learn.’ — Save the activation template.", "Feedback: ‘What would make a reusable routine easier to repeat?’ — Share one barrier."]:
        story.append(para("• " + text, body))
    story += [para("Implementation readiness checklist", h2), para("Before any real campaign: validate product claims and availability; confirm privacy/consent flow; approve creative and accessibility captions; create landing page and UTM taxonomy; configure permitted platform targeting; assign community response coverage; validate conversion events; and obtain separate authorization for publication or paid spend.", body), para("Sources and attribution", h2)]
    for source in data["sources"]:
        story.append(para("• " + source["reference"] + " — " + source["use"], body))
    story += [para("Limitations", h2), para("This is a fictional campaign plan. It does not report market research, competitor performance, an existing product, environmental impact, scientific benefit, customer result, campaign result, advertising spend, or publication. The prior Task 2 competitor audit remains evidence-blocked and is not used as a completed finding here.", body)]
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)


def main() -> int:
    source = DM_ROOT / "research" / "task3" / "campaign_calendar.json"
    output = DM_ROOT / "deliverables" / "DM_Task3_30_Day_Campaign.pdf"
    data = json.loads(source.read_text(encoding="utf-8"))
    build_pdf(data, output)
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
