"""Four-page secondary-source update; historical recovery remains untouched."""
import hashlib
import json
import sys
from pathlib import Path
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_task2_recovery_report import ROOT, table, footer
import importlib.util
spec = importlib.util.spec_from_file_location('secondary_metrics', ROOT / 'digital_marketing/research/task2/secondary/secondary_metrics.py')
metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics)

SOURCE = ROOT / 'digital_marketing/research/task2/handoff/PUBLIC_SOURCE_HANDOFF_2026-10-13.md'
OUTPUT = ROOT / 'digital_marketing/deliverables/DM_Task2_Competitor_Audit_SECONDARY_DRAFT.pdf'


def historical_delta(start, end):
    if type(start) is not int or type(end) is not int or min(start, end) < 0:
        raise ValueError('Cumulative snapshots require nonnegative integers')
    return {'net_change': end - start, 'verified_published_posts': None,
            'posts_per_week': None, 'engagement_rate': None}


def validate_source():
    text = SOURCE.read_text(encoding='utf-8')
    for required in ('2026-10-13', 'not collected by the Codex Cloud runtime',
                     'https://www.stanley1913.com/', 'https://www.hydroflask.com/',
                     'https://owalalife.com/', 'https://www.linkedin.com/showcase/owala-hydration/',
                     'No measured 28-day publication totals'):
        if required not in text:
            raise ValueError('Missing handoff provenance or account evidence: ' + required)
    return text


def build(output=OUTPUT):
    validate_source()
    data = metrics.load()
    calculated = metrics.calculate(data)
    base = getSampleStyleSheet()['BodyText']
    body = ParagraphStyle('HandoffBody', parent=base, fontName='AuditSans', fontSize=10, leading=14, spaceAfter=9)
    heading = ParagraphStyle('HandoffHeading', parent=body, fontName='AuditSans-Bold', fontSize=19, leading=24, textColor=colors.HexColor('#12324A'), spaceAfter=14)
    small = ParagraphStyle('HandoffTable', parent=body, fontSize=9, leading=12)
    p = lambda text: Paragraph(text, body)
    h = lambda text: Paragraph(text, heading)
    story = [h('Reusable hydration: competitor footprint audit'),
      p('Stanley 1913 • Hydro Flask • Owala | Secondary-evidence integration | 14 October 2026'),
      p('<b>PARTIAL DRAFT — NOT A COMPLETED MEASURED AUDIT.</b> Three brands are compared using direct 14 October website/profile snapshots and separately attributed independent research dated 13 October. No social campaign was executed.'),
      p('<b>Common social observation window:</b> 15 September–12 October 2026 UTC, 28 days. Current website observations are outside this period and support positioning only.'),
      h('Provenance and account identity'),
      table([['Brand', 'Primary website / Instagram', 'Independent LinkedIn observation'],
        ['Stanley 1913', 'stanley1913.com / @stanley1913_brand', 'linkedin.com/company/stanley-1913'],
        ['Hydro Flask', 'hydroflask.com / @hydroflask', 'linkedin.com/company/hydro-flask'],
        ['Owala', 'owalalife.com / @owala', 'linkedin.com/showcase/owala-hydration/']], [40*mm,100*mm,120*mm], small),
      p('Owala is an affiliated brand showcase. Trove Brands is parent-company context; its posts must not be substituted for Owala posts. LinkedIn references above were independently observed, not directly retrieved by Codex. Hydro Flask and Stanley YouTube links were verified from brand websites; channel content was inaccessible.'),
      p('The handoff is a source-discovery and qualitative starter, explicitly not an exhaustive period dataset. Original proxy failures, later successful website/profile captures, and the supplied original text remain separate records.'), PageBreak(),
      h('Positioning and creative comparison'),
      p('The following observations are attributed to the independent 13 October handoff and linked official websites. Audience and differentiation conclusions are analytical interpretations, not verified demographics.'),
      table([['Brand', 'Reviewer-observed website cues', 'Interpretation and conversion emphasis'],
       ['Stanley 1913', 'Quenchers; leakproof products; accessories; colour-led navigation; fall/Halloween and collaborative collections.', 'Collection-led lifestyle identity and fandom provide multiple routes to shop. Interpretation: relevance extends beyond basic hydration utility.'],
       ['Hydro Flask', 'Limited seasonal editions; customization; everyday hydration; lightweight products; Ocean Conservancy partnership.', 'Functional choice and personal expression coexist. Partnership presence is observed; no environmental outcome or effectiveness is inferred.'],
       ['Owala', 'FreeSip; customization; Color Drop; accessories; playful language.', 'Product functionality is packaged as novelty and self-expression. Interpretation: accessible, expressive product discovery rather than evidence of a measured audience.']], [35*mm,110*mm,115*mm], small),
      p('Direct 14 October recovery evidence corroborates seasonal merchandising, product choice and playful messaging: Stanley Devin Booker/Join the Club; Hydro Flask Midnight Glimmer/Find your bottle; Owala Cupholder friendly/Color Drop. Full claim-level citations remain in recovery/observations.json.'),
      p('<b>Visual evidence boundary:</b> Stanley and Hydro Flask rendered homepages were inspected in the earlier recovery. Owala assets loaded incompletely; colour comments rely on image alt text. No unlicensed brand images are reproduced. Social editorial frequency, creator-post diversity and channel-specific effectiveness are not demonstrated.'), PageBreak(),
      h('Secondary Instagram comparison: explicit limits'),
      p('HypeAuditor account pages were independently revisited through ChatGPT public web research on 14 October 2026 UTC. Codex direct retrieval remained blocked. No independent raw HTML snapshot was supplied. These are reviewer-attributed vendor records, not first-party Instagram observations.'),
      table([['Brand / vendor profile', '16 Sep total', '12 Oct total', 'Net change', 'Nominal net change/week', 'October vendor estimate']] +
        [[r['brand'] + '<br/>hypeauditor.com/instagram/' + r['handle'] + '/', str(r['start_total']), str(r['end_total']), '+' + str(r['net_change']), f"{r['nominal_net_change_per_week_proxy']:.2f}", f"{r['vendor_estimated_october_engagement_percent']:.2f}%"] for r in calculated], [76*mm,32*mm,32*mm,28*mm,46*mm,46*mm], small),
      p('<b>Proxy formula:</b> net cumulative count change / 26 × 7. Snapshot dates are a nominal 26-day interval, not the full 15 September–12 October inclusive 28-day period. The proxy is <b>NOT verified publication frequency</b>: removals, archiving and vendor data handling may affect cumulative totals. No September 15 total is inferred.'),
      p('<b>Engagement classification:</b> the October percentages are HypeAuditor proprietary estimates. They were not independently computed from visible likes/comments and exact followers and are not restricted to the assignment window. The method is not established as equivalent to a visible-interaction proxy. Higher displayed estimates do not establish better conversion, ROI or causal advantage.'),
      p('<b>Interpretation:</b> Owala has the largest reported net-count change and vendor estimate in this limited secondary table; Stanley and Hydro Flask share the same net change. This describes vendor records only. It does not establish superior posting volume, campaign effectiveness or cross-platform performance.'),
      p('<b>Still unavailable:</b> verified dated post counts, exact 28-day cadence and independently calculated period engagement for all three brands. LinkedIn and YouTube rates and period inventories remain unavailable; never substitute these Instagram estimates across platforms. Missing primary measurements remain null, not zero.'),
      p('Evidence: research/task2/secondary/observations.json and VERIFIED_SOURCE_NOTE_2026-10-14.md. The table URLs identify the vendor accounts; full precision calculations are reproducible in secondary/secondary_metrics.py. Original proxy errors remain in historical evidence.'), PageBreak(),
      h('RefillLoop opportunities and completion decision'),
      table([['Priority', 'Specific hypothesis grounded in observed cues', 'Required validation'],
       ['1: utility proof', 'Pair modular replacement demonstrations with transparent compatibility guidance; counterbalance collection-led discovery with practical ownership information.', 'Test comprehension and click intent; do not claim competitors lack utility content.'],
       ['2: guided choice', 'A use-case chooser for commute, office and travel connects function, personalization and clearly specified trade-offs.', 'Prototype usability test; compare with existing competitor selection pathways.'],
       ['3: coherent education', 'Coordinate Instagram short demonstrations, LinkedIn workplace use cases and YouTube detailed walkthroughs around one verifiable feature.', 'Validate proposed product capability and audience response before launch.']], [42*mm,134*mm,84*mm], small),
      p('These recommendations are proposed market-entry hypotheses, not proven unmet gaps or achieved RefillLoop results. Website cues do not prove recurring social themes, community strategy, creator effectiveness or cross-platform consistency.'),
      p('<b>Completion recommendation:</b> retain Task 2 as incomplete for measured-audit approval. The report now supports a limited third-party Instagram snapshot comparison alongside qualitative positioning. Material grading risks remain: no verified social content sample, exact posting cadence, or cross-platform engagement. A dated comparable post inventory with public interactions would resolve the evidence gaps; organizer acceptance of the explicitly disclosed limited method could resolve the grading scope. Do not claim completion without that evidence or approval.'),
      p('<b>References:</b> https://www.stanley1913.com/ ; https://www.hydroflask.com/ ; https://owalalife.com/ . Full newsroom, press-kit and account links plus review date/provenance appear in research/task2/handoff/PUBLIC_SOURCE_HANDOFF_2026-10-13.md. Direct source timestamps/digests: evidence/task2/recovery/source_records.json and browser_records.json.'),
      p('<b>Reproduction:</b> python digital_marketing/tools/generate_task2_secondary_report.py . Original assignment brief: Digital Marketing &amp; Branding Tasks &amp; Instructions.md. Earlier reports are historical and unchanged.')]
    output.parent.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(str(output), pagesize=landscape(A4), leftMargin=15*mm, rightMargin=15*mm, topMargin=14*mm, bottomMargin=20*mm, title='Hydration Competitor Audit — Limited Secondary-Evidence Draft', author='Internship project').build(story, onFirstPage=footer, onLaterPages=footer)
    return output


if __name__ == '__main__':
    print(build().relative_to(ROOT))
