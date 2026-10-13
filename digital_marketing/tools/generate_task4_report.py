"""Generate the Task 4 SEO and acquisition strategy PDF from validated data."""

from __future__ import annotations
import json, sys
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research" / "task4"))
from build_strategy import validate  # noqa: E402

NAVY=colors.HexColor("#12324A"); TEAL=colors.HexColor("#197D82"); MIST=colors.HexColor("#EAF3F3"); INK=colors.HexColor("#1E2A32")
def p(text, style): return Paragraph(str(text).replace("&", "&amp;"), style)
def footer(canvas, doc):
    canvas.saveState(); canvas.setStrokeColor(TEAL); canvas.line(15*mm,14*mm,doc.pagesize[0]-15*mm,14*mm); canvas.setFillColor(NAVY); canvas.setFont("Helvetica",7); canvas.drawString(15*mm,8.5*mm,"Ocean Bottle | proposed SEO and acquisition strategy | Task 4"); canvas.drawRightString(doc.pagesize[0]-15*mm,8.5*mm,f"Page {doc.page}"); canvas.restoreState()
def table(rows, widths, body, header=True):
    header_style=ParagraphStyle("Task4TableHeader",parent=body,fontName="Helvetica-Bold",textColor=colors.white)
    cells=[[p(cell, header_style if header and n==0 else body) for cell in row] for n,row in enumerate(rows)]
    t=Table(cells,colWidths=widths,repeatRows=1 if header else 0,hAlign="LEFT")
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY) if header else ("BACKGROUND",(0,0),(-1,-1),colors.white),("GRID",(0,0),(-1,-1),.25,colors.HexColor("#B7C8CD")),("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,MIST]),("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3),("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2)])); return t
def build_pdf(data, output):
    errors=validate(data)
    if errors: raise ValueError("strategy validation failed: "+"; ".join(errors))
    styles=getSampleStyleSheet(); title=ParagraphStyle("Title",parent=styles["Title"],fontName="Helvetica-Bold",fontSize=25,leading=30,textColor=NAVY,alignment=TA_CENTER); sub=ParagraphStyle("Sub",parent=styles["Normal"],fontSize=11,leading=14,textColor=TEAL,alignment=TA_CENTER); h1=ParagraphStyle("H1",parent=styles["Heading1"],fontName="Helvetica-Bold",fontSize=16,leading=19,textColor=NAVY,spaceAfter=6); h2=ParagraphStyle("H2",parent=styles["Heading2"],fontName="Helvetica-Bold",fontSize=10,leading=12,textColor=TEAL,spaceBefore=4,spaceAfter=3); body=ParagraphStyle("Body",parent=styles["BodyText"],fontSize=8.3,leading=10.5,textColor=INK,spaceAfter=4); small=ParagraphStyle("Small",parent=body,fontSize=8,leading=9.5,spaceAfter=0)
    doc=SimpleDocTemplate(str(output),pagesize=landscape(A4),leftMargin=15*mm,rightMargin=15*mm,topMargin=14*mm,bottomMargin=20*mm,title="Ocean Bottle SEO and Acquisition Strategy",author="Internship project")
    s=[]; subj=data["subject"]
    s += [Spacer(1,4*mm),p("OCEAN BOTTLE",title),p("Enterprise Search Authority & Growth Acquisition Strategy",sub),p("Task 4 | SEO map, acquisition funnel, email re-engagement, and modeled CAC/ROAS",sub),Spacer(1,3*mm),p("A research-backed planning report. Company claims are attributed to accessible public pages; keywords, targeting, budgets, and financial results are proposed assumptions, not performance claims.",body)]
    s += [p("1. Website context and research boundary",h1),p(subj["selection"],body),p("Verified page observations",h2)]
    obs=[["ID / page","Observed public structure","Use in strategy"]]
    for row in data["observations"]: obs.append([row["id"]+"<br/>"+row["url"],row["observed"],"Source-specific context" if row["status"]==200 else "Unavailable; excluded from validation"])
    s += [table(obs,[55*mm,133*mm,54*mm],small),p("Assessment",h2),p("The delivered pages expose canonical URLs, distinct titles, one visible H1 per sampled page, and links between product, FAQ, impact, collection, contact, and news routes. This supports a practical topic-to-page model. Mobile experience, CWV, crawl coverage, structured-data validity, indexing, accessibility conformance, rankings, and analytics were not tested and remain implementation checks.",body),p("Conversion-path interpretation",h2),p("Observed navigation and page relationships support a proposed path from impact or educational discovery to product review, then FAQ/delivery reassurance and add-to-cart. This is an interpretation of public structure, not evidence of user behavior or conversion performance.",body),PageBreak()]
    s += [p("2. Long-tail keyword architecture",h1),p("Keyword entries are qualitative opportunities created from page language, page roles, and customer questions. Search volume, difficulty, ranking position, and click forecasts were not accessed.",body)]
    kr=[["Keyword / intent","Target page","Priority / rationale"]]+[[x["keyword"]+"<br/><i>"+x["intent"]+"</i>",x["target_page"],x["priority"]+" — "+x["rationale"]] for x in data["keyword_map"]]
    s += [table(kr,[75*mm,59*mm,108*mm],small),p("Prioritization method",h2),p("P1/P2/P3 reflects closeness to an accessible product, impact, support, or proposed education page and clarity of intent—not market size. Start with P1 product and impact pages; use Search Console and analytics only after authorized access to verify queries, impressions, and outcomes.",body),PageBreak()]
    s += [p("3. On-page SEO optimization map",h1),p("Existing facts are limited to the sampled pages and their delivered metadata/headings. Titles, descriptions, hierarchy, links, and content changes below are proposed implementation work.",body)]
    for row in data["seo_map"]:
        s += [p(row["priority"]+" | "+row["page_role"]+" — "+row["existing_url"],h2),table([["Primary / secondary","Proposed title and meta","Proposed hierarchy and links","Gap / measurement"],[row["primary_keyword"]+"<br/>"+", ".join(row["secondary_keywords"]),row["proposed_title"]+"<br/><i>"+row["proposed_meta_description"]+"</i>","H1: "+row["proposed_h1"]+"<br/>H2: "+"; ".join(row["proposed_h2s"])+"<br/>Links: "+", ".join(row["internal_links"]),row["content_gap"]+"<br/><i>"+row["measurement"]+"</i>"]],[54*mm,62*mm,66*mm,60*mm],small),Spacer(1,2*mm)]
    s += [PageBreak(),p("4. Paid acquisition funnel and measurement",h1),p("All stages are proposed. Retargeting is conditional on valid consent, applicable policy, and authorized account controls.",body)]
    fr=[["Stage","Audience / channel","Message / landing page","CTA, event and KPI"]]+[[x["stage"],x["audience"]+"<br/><i>"+x["channel"]+"</i>",x["message"]+"<br/>"+x["landing_page"],x["cta"]+"<br/><b>Event:</b> "+x["conversion_event"]+"<br/><b>KPI:</b> "+x["kpi"]] for x in data["funnel"]]
    s += [table(fr,[27*mm,67*mm,82*mm,66*mm],small),p("Attribution and optimization",h2)]
    for x in data["measurement"]: s.append(p("• "+x,body))
    b=data["budget"]; br=[["Allocation","Proposed GBP","Planning role"]]+[[k,f"£{v:,.0f}","Media delivery" if k!="Measurement and creative" else "Creative, tracking and reporting readiness"] for k,v in b["allocation"].items()]
    s += [p("90-day proposed budget",h2),table(br,[93*mm,40*mm,109*mm],small),p(b["assumption"],body),PageBreak()]
    s += [p("5. Consent-aware email re-engagement",h1),p("These are proposed automation rules only. They require documented lawful basis, clear preference controls, a working unsubscribe mechanism, suppression of opted-out contacts, frequency caps, and review against the relevant privacy and email rules before activation.",body)]
    er=[["Workflow / entry","Sequence from entry","Conversion / exit"]]
    for flow in data["emails"]:
        sequence="<br/>".join(f"{m['delay_hours_from_entry']}h: {m['subject']}" for m in flow["messages"])
        er.append([flow["name"]+"<br/>"+flow["entry"], sequence, ", ".join(m["conversion_event"] for m in flow["messages"])+"<br/>"+flow["messages"][0]["exit_condition"]])
    s += [table(er,[70*mm,96*mm,76*mm],small),p("Automation decision table",h2)]
    decisions=[["Event / condition","Decision"],["Unsubscribe, consent withdrawal, bounce, complaint","Suppress immediately; clear active flow; no further marketing drafts."],["Purchase / repeat purchase","Exit pre-purchase / post-purchase sequence; care entry needs confirmed delivery and consent."],["Duplicate / priority","One flow at a time: post-purchase > cart > browse > welcome. Duplicate entries do not restart clocks."],["Frequency cap / support issue","At most one message per 24h and three per rolling seven days; defer without advancing. Support pauses all messages."],["Inactivity / deadline / completion","Expire or complete; no replay in pilot. Recheck consent and suppression before every message."]]
    s += [table(decisions,[75*mm,167*mm],small),p("Supporting appendix",h2),p("DM_Task4_Email_Workflow_Appendix.pdf contains every message’s full body, preview, CTA, conversion event and consent/exit rules. Machine-readable messages and a synthetic event simulator are in research/task4/. No automation is activated.",body),PageBreak()]
    s += [p("6. Financial model, implementation order, and limitations",h1),p("Formula: impressions = media budget ÷ blended CPM × 1,000; sessions = impressions × CTR; customers = sessions × purchase conversion rate; CAC = media spend ÷ customers; ROAS = attributed revenue ÷ media spend. The figures below are scenario inputs, not benchmarks, forecasts, or results.",body)]
    sr=[["Scenario","CPM / CTR","Impressions / sessions","Conv. / customers","AOV / revenue","Media CAC / ROAS","All-in cost / customer"]]+[[x["name"],f"£{x['blended_cpm_gbp']:.2f} / {x['ctr']:.1%}",f"{x['impressions']:,.0f} / {x['sessions']:,.0f}",f"{x['purchase_conversion_rate']:.1%} / {x['customers']:,.0f}",f"£{x['aov_gbp']:.0f} / £{x['attributed_revenue_gbp']:,.0f}",f"£{x['cac_gbp']:.2f} / {x['roas']:.2f}x",f"£{x['all_in_acquisition_cost_gbp']:.2f}"] for x in data["scenarios"]]
    s += [table(sr,[23*mm,31*mm,43*mm,36*mm,38*mm,35*mm,36*mm],small),p("Media versus all-in economics",h2),p("Media CAC retains the GBP 10,000 advertising denominator. Separately, all-in acquisition cost per customer = full GBP 12,000 project allocation / modeled customers: Low GBP 160.00, Base GBP 75.00, High GBP 37.50. These are planning allocations, not accounting outcomes. ROAS always remains attributed revenue / advertising spend; creative costs do not change its denominator.",body),p("Recommended sequence",h2),p("1. Validate claims, consent, tracking plan, and analytics governance. 2. Implement P1 product and impact maps. 3. Publish only approved, attributed content. 4. Instrument product, cart, purchase, and email events. 5. Launch a small authorized test with a spend cap; compare outcomes against the model, not against assumed figures. 6. Reallocate only after a documented attribution and quality review.",body),p("Sources and limitations",h2),p("Official page records: homepage, Original Bottle, FAQs, Ocean Impact (Codex retrieval, 13 October 2026 UTC). Codex’s B Lab retrieval returned 403. Separately, reviewer-supplied observations received 13 October 2026 report B Lab certification/founding in 2019 and LinkedIn founding in 2018; reviewer collection dates were not supplied. The discrepancy remains unresolved. URLs: https://www.bcorporation.net/en-us/find-a-b-corp/company/ocean-bottle/ and https://www.linkedin.com/company/the-ocean-bottle/. No real keyword metrics, rankings, analytics, conversion, revenue or technical performance was verified. Company environmental figures remain attributed, without independent outcome validation.",body)]
    output.parent.mkdir(parents=True,exist_ok=True); doc.build(s,onFirstPage=footer,onLaterPages=footer)
def build_email_appendix(data, output):
    errors = validate(data)
    if errors:
        raise ValueError("strategy validation failed: " + "; ".join(errors))
    styles = getSampleStyleSheet()
    heading = ParagraphStyle("AppendixHeading", parent=styles["Heading1"], fontSize=15, leading=18, textColor=NAVY)
    subheading = ParagraphStyle("AppendixSubheading", parent=styles["Heading2"], fontSize=11, leading=14, textColor=TEAL)
    body = ParagraphStyle("AppendixBody", parent=styles["BodyText"], fontSize=9, leading=11, spaceAfter=5, textColor=INK)
    story = []
    for flow in data["emails"]:
        for start in range(0, len(flow["messages"]), 2):
            if story:
                story.append(PageBreak())
            story.extend([p("Supporting appendix: " + flow["name"], heading), p("Proposed, inactive automation. Trigger: " + flow["entry_event"] + ". Entry: " + flow["entry"], body), p(f"Expiry: {flow['expires_after_hours']}h from entry. Policy: one per 24h; three per rolling seven days; no duplicate restart; recheck consent/suppression before each message.", body)])
            for message in flow["messages"][start:start + 2]:
                story.extend([
                    p(f"{message['id']} | +{message['delay_hours_from_entry']}h | {message['subject']}", subheading),
                    p("Preview: " + message["preview_text"], body),
                    p(message["body"].replace("\n", "<br/>"), body),
                    p(f"CTA: {message['cta']} ({message['cta_path']}) | Event: {message['conversion_event']}", body),
                ])
            story.extend([p("Exit: " + flow["messages"][0]["exit_condition"], body), p("Suppression: " + data["email_policy"]["suppression"], body)])
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output), pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=14*mm, bottomMargin=20*mm, title="Task 4 Supporting Email Workflow Appendix", author="Internship project")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def main():
    data=json.loads((ROOT/"research"/"task4"/"strategy_data.json").read_text(encoding="utf-8")); out=ROOT/"deliverables"/"DM_Task4_SEO_Acquisition_Strategy.pdf"; build_pdf(data,out); print(f"Wrote {out}")
    appendix = ROOT / "deliverables" / "DM_Task4_Email_Workflow_Appendix.pdf"
    build_email_appendix(data, appendix)
    print(f"Wrote {appendix}")
if __name__=="__main__": main()
