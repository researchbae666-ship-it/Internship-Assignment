"""Build validated, privacy-safe data for the Task 4 SEO strategy report."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
REQUIRED_SEO_FIELDS = {
    "existing_url", "page_role", "primary_keyword", "secondary_keywords",
    "proposed_title", "proposed_meta_description", "proposed_h1",
    "proposed_h2s", "internal_links", "content_gap", "priority", "measurement",
}


def source_revision() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT.parents[2], text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def modeled_scenario(name: str, cpm_gbp: float, ctr: float, conversion_rate: float, aov_gbp: float) -> dict[str, Any]:
    media_budget = 10_000.0
    impressions = media_budget / cpm_gbp * 1000
    sessions = impressions * ctr
    customers = sessions * conversion_rate
    revenue = customers * aov_gbp
    return {
        "name": name,
        "media_budget_gbp": media_budget,
        "blended_cpm_gbp": cpm_gbp,
        "ctr": ctr,
        "impressions": impressions,
        "sessions": sessions,
        "purchase_conversion_rate": conversion_rate,
        "customers": customers,
        "aov_gbp": aov_gbp,
        "attributed_revenue_gbp": revenue,
        "cac_gbp": media_budget / customers if customers else None,
        "roas": revenue / media_budget if media_budget else None,
    }


def build_strategy() -> dict[str, Any]:
    observations = [
        {
            "id": "OB-01", "url": "https://oceanbottle.co/", "status": 200,
            "observed": "Canonical homepage; title ‘The World's Most Needed Reusable Water Bottle’; description and H1 frame reusable bottles and ocean-plastic collection; navigation links to collections, product pages, impact, FAQs, contact, and news.",
        },
        {
            "id": "OB-02", "url": "https://oceanbottle.co/products/original-bottle", "status": 200,
            "observed": "Canonical product page; title ‘Ocean Bottle Original | Insulated Reusable Water Bottle’; product H1 ‘Original Bottle’; delivered markup links to related products, FAQs, and the impact page.",
        },
        {
            "id": "OB-03", "url": "https://oceanbottle.co/pages/faqs", "status": 200,
            "observed": "Canonical FAQ page; title ‘FAQs | Ocean Bottle’; H1 ‘Frequently Asked Questions’; visible section headings cover plastic collection, returns, delivery, warranty, pre-orders, product, engraving, and discounts.",
        },
        {
            "id": "OB-04", "url": "https://oceanbottle.co/pages/ocean-impact", "status": 200,
            "observed": "Canonical impact page; title and description make Ocean Bottle’s plastic-collection statement; H1 ‘Our Impact’; headings include ‘1 for 1000’, ‘How it works’, partners, and a company statement about B Corp certification.",
        },
        {
            "id": "OB-05", "url": "https://www.bcorporation.net/en-us/find-a-b-corp/company/ocean-bottle/", "status": 403,
            "observed": "B Lab directory could not be retrieved from this cloud environment; it is not used to validate certification.",
        },
    ]
    keyword_map = [
        ("insulated reusable water bottle", "transactional", "/products/original-bottle", "High", "Product title and description explicitly use insulated and reusable."),
        ("reusable water bottle with ocean plastic collection", "commercial", "/pages/ocean-impact", "High", "Impact message is present on homepage and impact page."),
        ("double walled insulated reusable bottle", "transactional", "/products/original-bottle", "High", "Derived from the product-page description; no volume claim."),
        ("how does ocean plastic collection work", "informational", "/pages/ocean-impact", "Medium", "Maps to the observed ‘How it works’ section."),
        ("reusable bottle warranty and returns", "informational", "/pages/faqs", "Medium", "Maps to observed FAQ categories."),
        ("reusable water bottle delivery information", "informational", "/pages/faqs", "Medium", "Maps to observed delivery FAQ section."),
        ("ocean bottle original features", "commercial", "/products/original-bottle", "Medium", "Brand-plus-product phrase mapped to the Original Bottle page."),
        ("reusable bottle engraving gift", "transactional", "/pages/engraving", "Medium", "Existing navigation exposes an engraving route; page content was not audited."),
        ("sustainable corporate reusable bottle gifting", "commercial", "/pages/co-brand", "Medium", "Existing navigation exposes co-brand route; page content was not audited."),
        ("why use a reusable water bottle", "informational", "/blogs/news", "Low", "Proposed educational article cluster; no volume or ranking claim."),
        ("how to clean an insulated reusable bottle", "informational", "/pages/faqs", "Low", "Proposed support-content expansion from product FAQ intent."),
        ("reusable bottle workplace wellbeing gift", "commercial", "/pages/wholesale", "Low", "Proposed B2B discovery topic; wholesale navigation was observed but content was not audited."),
    ]
    seo_map = [
        {
            "existing_url": "https://oceanbottle.co/products/original-bottle", "page_role": "Product",
            "primary_keyword": "insulated reusable water bottle", "secondary_keywords": ["double walled reusable bottle", "Ocean Bottle Original features"],
            "proposed_title": "Original Bottle | Insulated Reusable Water Bottle | Ocean Bottle",
            "proposed_meta_description": "Explore the Ocean Bottle Original, an insulated reusable water bottle. Review features, FAQs and Ocean Bottle’s stated collection model.",
            "proposed_h1": "Original insulated reusable water bottle",
            "proposed_h2s": ["Original Bottle features", "How the stated 1 for 1000 model works", "Delivery, warranty and care FAQs"],
            "internal_links": ["/pages/ocean-impact", "/pages/faqs", "/collections/water-bottles"],
            "content_gap": "Add scannable feature-to-benefit copy, care guidance, and a contextual FAQ block without adding unsupported environmental or material claims.",
            "priority": "P1", "measurement": "Organic landing sessions, add-to-cart rate, FAQ-link clicks, and purchase rate in consented analytics.",
        },
        {
            "existing_url": "https://oceanbottle.co/pages/ocean-impact", "page_role": "Impact explainer",
            "primary_keyword": "reusable water bottle with ocean plastic collection", "secondary_keywords": ["how ocean plastic collection works", "ocean plastic collection model"],
            "proposed_title": "How Ocean Bottle’s Plastic Collection Model Works",
            "proposed_meta_description": "Learn how Ocean Bottle describes its stated 1 for 1000 plastic-collection model, the questions it answers, and related reusable bottle pages.",
            "proposed_h1": "How Ocean Bottle describes its collection model",
            "proposed_h2s": ["The stated 1 for 1000 model", "Questions to answer before purchase", "Explore reusable bottle options"],
            "internal_links": ["/products/original-bottle", "/pages/faqs", "/collections/water-bottles"],
            "content_gap": "Create a concise explanatory summary with dated methodology links and a product-to-impact decision path; retain clear attribution for company claims.",
            "priority": "P1", "measurement": "Organic entrances, product-page click-through, engaged time, and assisted add-to-cart events.",
        },
        {
            "existing_url": "https://oceanbottle.co/pages/faqs", "page_role": "Support / trust",
            "primary_keyword": "reusable bottle warranty and returns", "secondary_keywords": ["reusable water bottle delivery information", "insulated bottle care"],
            "proposed_title": "Reusable Bottle FAQs: Delivery, Warranty and Care | Ocean Bottle",
            "proposed_meta_description": "Find Ocean Bottle FAQs about delivery, warranty, returns, product care, engraving and the company’s stated collection model.",
            "proposed_h1": "Ocean Bottle delivery, warranty and care FAQs",
            "proposed_h2s": ["Delivery and returns", "Warranty and product care", "Collection-model questions"],
            "internal_links": ["/products/original-bottle", "/pages/ocean-impact", "/pages/contact"],
            "content_gap": "Add jump links, concise answer summaries, and product-context links; validate structured-data eligibility before implementation.",
            "priority": "P2", "measurement": "Organic FAQ entrances, support-contact rate, product click-through, and return-visit rate.",
        },
        {
            "existing_url": "https://oceanbottle.co/blogs/news", "page_role": "Proposed educational hub",
            "primary_keyword": "why use a reusable water bottle", "secondary_keywords": ["reusable bottle habit guide", "how to clean an insulated reusable bottle"],
            "proposed_title": "Reusable Bottle Guides and Care Advice | Ocean Bottle",
            "proposed_meta_description": "Browse proposed reusable bottle guides, care explainers and impact-model context, with links to relevant Ocean Bottle product and FAQ pages.",
            "proposed_h1": "Reusable bottle guides and care advice",
            "proposed_h2s": ["Choose a reusable bottle", "Care and cleaning guidance", "Understand the stated collection model"],
            "internal_links": ["/products/original-bottle", "/pages/faqs", "/pages/ocean-impact"],
            "content_gap": "Build a small topic cluster with author/date governance and links to commercial and support pages; the current blog content was not audited.",
            "priority": "P3", "measurement": "Indexed pages, organic non-brand entrances, assisted product clicks, and content-to-product CTR.",
        },
    ]
    funnel = [
        ("Awareness", "New reusable-hydration and gift researchers", "Google non-brand search; Meta/YouTube prospecting", "Problem/utility and attributed impact explainer", "/pages/ocean-impact", "Read the model", "Engaged visit", "Reach, qualified clicks, engaged sessions"),
        ("Consideration", "Visitors who viewed product or impact pages", "Search remarketing only where consented; Meta/YouTube retargeting where permitted", "Feature, care, FAQ and comparison-oriented proof", "/products/original-bottle", "Explore Original Bottle", "Product view / FAQ interaction", "Product CTR, add-to-cart rate"),
        ("Conversion", "High-intent product viewers and cart visitors", "Brand and product search; consented cart retargeting", "Clear product choice, delivery/warranty pathway", "/products/original-bottle", "Add to cart", "Purchase", "Cost per purchase, CAC, revenue"),
        ("Retention", "Consented purchasers and subscribers", "Email only; no paid retargeting without separate consent", "Care, use and timely replenishment/accessory education", "/pages/faqs", "Get care guidance", "Repeat purchase / support resolution", "Repeat purchase rate, unsubscribes, support contacts"),
    ]
    emails = [
        ("E1", "Consented subscriber; no purchase", "Immediately", "A reusable routine starts with one choice", "Welcome message; link to product, FAQs, and attributed impact explanation.", "Product-view event; exit on purchase"),
        ("E2", "Viewed product twice; no cart; marketing consent", "2 days", "Questions before choosing a reusable bottle?", "Decision-support email with product, delivery, warranty and care links.", "Product-view or add-to-cart event; exit on purchase/unsubscribe"),
        ("E3", "Cart started; no purchase; marketing consent", "4 hours", "Your Ocean Bottle selection is waiting", "Single reminder with product link and delivery/returns path; no urgency claim unless verified.", "Purchase, unsubscribe, or 7-day timeout"),
        ("E4", "Purchaser; marketing consent", "14 days after delivery-status event if available", "Care guidance for your reusable bottle", "Useful care and FAQ links; invite feedback without assuming product satisfaction.", "Repeat purchase, unsubscribe, or preference update"),
    ]
    scenarios = [
        modeled_scenario("Low", 12.8, 0.008, 0.012, 45.0),
        modeled_scenario("Base", 10.0, 0.008, 0.020, 55.0),
        modeled_scenario("High", 8.0, 0.008, 0.032, 65.0),
    ]
    return {
        "subject": {
            "name": "Ocean Bottle", "website": "https://oceanbottle.co/",
            "selection": "Retained as the task’s startup website subject because an active direct-to-consumer website is publicly accessible. The 2019 founding-year statement supplied in the task authorization was not independently verified in this collection, so the report does not state it as a fact.",
        },
        "collection_utc": "2026-10-13T11:20:00Z", "observations": observations,
        "keyword_map": [dict(keyword=k, intent=i, target_page=p, priority=pr, rationale=r) for k, i, p, pr, r in keyword_map],
        "seo_map": seo_map,
        "funnel": [dict(stage=s, audience=a, channel=c, message=m, landing_page=l, cta=cta, conversion_event=e, kpi=k) for s,a,c,m,l,cta,e,k in funnel],
        "emails": [dict(id=i, entry=e, delay=d, subject=s, body=b, exit_rule=x) for i,e,d,s,b,x in emails],
        "budget": {"currency": "GBP", "total_gbp": 12_000, "media_gbp": 10_000, "allocation": {"Google Search": 4_500, "Meta prospecting": 3_000, "YouTube": 1_500, "Consented retargeting reserve": 1_000, "Measurement and creative": 2_000}, "assumption": "Proposed 90-day planning budget; no spend is authorized or incurred."},
        "scenarios": scenarios,
        "measurement": ["Use consent-aware analytics and a documented UTM taxonomy: source, medium, campaign, content, term.", "Keep paid-platform reporting separate from analytics attribution; reconcile purchase events only after consent and implementation review.", "Define CAC as media spend divided by attributed new customers; define ROAS as attributed revenue divided by media spend. Zero denominators produce an explicit unavailable result."],
        "source_revision": source_revision(),
    }


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if len(data.get("keyword_map", [])) < 10: errors.append("keyword map needs at least 10 entries")
    if {x["intent"] for x in data.get("keyword_map", [])} != {"informational", "commercial", "transactional"}: errors.append("keyword map lacks required intents")
    if len(data.get("seo_map", [])) < 4: errors.append("SEO map needs at least four pages")
    for row in data.get("seo_map", []):
        if not REQUIRED_SEO_FIELDS <= set(row) or any(not row[field] for field in REQUIRED_SEO_FIELDS): errors.append("incomplete SEO map row")
    budget = data.get("budget", {})
    if budget.get("total_gbp") != sum(budget.get("allocation", {}).values()): errors.append("budget allocations do not sum to total")
    if budget.get("media_gbp") != sum(v for k,v in budget.get("allocation", {}).items() if k != "Measurement and creative"): errors.append("media allocation does not reconcile")
    if len(data.get("funnel", [])) != 4 or len(data.get("emails", [])) < 4: errors.append("missing funnel or email stages")
    for row in data.get("scenarios", []):
        if row["blended_cpm_gbp"] <= 0 or row["media_budget_gbp"] <= 0 or row["customers"] <= 0:
            errors.append("invalid financial denominator")
            continue
        if abs(row["impressions"] - row["media_budget_gbp"] / row["blended_cpm_gbp"] * 1000) > 1e-7: errors.append("impression formula mismatch")
        if abs(row["sessions"] - row["impressions"] * row["ctr"]) > 1e-7: errors.append("session formula mismatch")
        if abs(row["customers"] - row["sessions"] * row["purchase_conversion_rate"]) > 1e-7: errors.append("customer formula mismatch")
        if abs(row["cac_gbp"] - row["media_budget_gbp"] / row["customers"]) > 1e-7: errors.append("CAC formula mismatch")
        if abs(row["roas"] - row["attributed_revenue_gbp"] / row["media_budget_gbp"]) > 1e-7: errors.append("ROAS formula mismatch")
    return errors


def main() -> int:
    data = build_strategy(); errors = validate(data)
    if errors: raise ValueError("; ".join(errors))
    output = ROOT / "strategy_data.json"
    output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output} with {len(data['keyword_map'])} keywords and {len(data['seo_map'])} SEO-map rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
