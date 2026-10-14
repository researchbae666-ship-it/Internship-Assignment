"""Build a truthful partial audit from retained public responses."""

import json
import re
from pathlib import Path
from metrics import WINDOW, calculate

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / "digital_marketing/evidence/task2/recovery"
RESEARCH = Path(__file__).resolve().parent
BRANDS = {"stanley": "Stanley 1913", "hydro": "Hydro Flask", "owala": "Owala"}


def norm(text):
    return " ".join(text.casefold().split())


def validate(data, sources, browsers):
    errors = []
    source_map = {source["id"]: source for source in sources + browsers}
    if data["status"] != "partial evidence-backed draft; period metrics blocked":
        errors.append("Recovery must not claim completed measurement")
    if data["observation_window"] != WINDOW:
        errors.append("Incorrect shared window")
    for claim in data["facts"]:
        source = source_map.get(claim["source_id"])
        if not source:
            errors.append("Missing claim source")
            continue
        if claim["type"] == "quoted_public_text":
            extract = source.get("extract", {})
            public = source.get("public_text", extract.get("public_text", ""))
            public += " " + " ".join(image["alt"] for image in extract.get("image_alt_records", []))
            if norm(claim["quote"]) not in norm(public):
                errors.append("Unsupported quote: " + claim["id"])
        elif claim["type"] == "visual_observation":
            if not source.get("screenshot_sha256"):
                errors.append("Visual observation has no screenshot evidence")
        else:
            errors.append("Unknown factual claim type")
    for account in data["accounts"]:
        if account["verified"]:
            source = source_map[account["source_id"]]
            if account["account_url"] not in source_map[account["verification_source_id"]]["extract"]["social_links"]:
                errors.append("Account not linked by official website")
    calculate(data)
    return errors


def build(sources, browsers):
    source_map = {source["id"]: source for source in sources}
    browser_map = {source["id"]: source for source in browsers}
    facts = []
    def fact(identity, brand, source, quote, implication):
        facts.append({"id": identity, "brand": BRANDS[brand], "source_id": source, "type": "quoted_public_text", "quote": quote, "interpretation": implication})
    fact("S1", "stanley", "stanley", "The Stanley 1913 x Devin Booker Collection.", "Named collaboration anchors the current homepage; creator-led lifestyle appeal is a plausible positioning interpretation, not verified conversion performance.")
    fact("S2", "stanley", "stanley", "Join the Club", "Membership is an observable acquisition pathway. Creator-fund and loyalty labels are visible, but programme effectiveness and post collaborations are unmeasured.")
    fact("S3", "stanley", "stanley-instagram-browser", "#BuiltForLife", "The profile bio reinforces durability/adventure wording. This is profile consistency, not proof of repeated post themes.")
    fact("H1", "hydro", "hydro", "Seasonal sips inspired by the night sky.", "Seasonal design/lifestyle language sits beside product features and limited-edition commerce.")
    fact("H2", "hydro", "hydro", "Find your bottle", "The bottle-finder and customization paths offer functional decision support; no completion or conversion data is available.")
    fact("H3", "hydro", "hydro-instagram-browser", "Your hydration, your style.", "Profile wording connects hydration and self-expression. Clean & Care and Customize highlight labels indicate visible profile organization, not post cadence.")
    fact("O1", "owala", "owala", "Cupholder-friendly.", "The FreeSip Sway label supplies a concise everyday-use benefit; appeal to carry/commute contexts is an interpretation.")
    fact("O2", "owala", "owala", "Color Drop", "Color Drop and Customize are observable navigation concepts. Their popularity and release frequency were not measured.")
    fact("O3", "owala", "owala-instagram-browser", "Where Boring Ends.", "Playful differentiation is visible in the bio. Owala IRL and Owala Fam are profile highlight labels; community outcomes remain unknown.")
    fact("O4", "owala", "owala", "Owala FreeSip, hot pink insulated stainless steel bottle with matching flip cap and carry loop.", "Official image alt text describes a bright product colour. Owala page styling and images loaded incompletely, so this is textual visual evidence rather than a full rendered-design judgement.")
    facts.extend([
        {"id": "S4", "brand": BRANDS["stanley"], "source_id": "stanley-browser", "type": "visual_observation", "quote": "Captured homepage hero uses woodland lifestyle photography, with black/white navigation and a Shop Now CTA.", "interpretation": "In this capture, the collection is contextualized within an outdoor scene; do not generalize this one hero to all social creative."},
        {"id": "H4", "brand": BRANDS["hydro"], "source_id": "hydro-browser", "type": "visual_observation", "quote": "Captured Midnight Glimmer hero shows product bottles against a dark blue star-like background, with a limited-edition shopping CTA.", "interpretation": "This capture foregrounds the product/colour edition, contrasting with Stanley's captured lifestyle-led hero."},
    ])
    accounts = []
    for key, brand in BRANDS.items():
        for platform in ("Instagram", "LinkedIn", "YouTube"):
            identity = key + "-" + platform.lower()
            source = source_map[identity]
            verified = source["account_verification"].startswith("verified by outgoing")
            account = {"brand": brand, "platform": platform, "account_url": source["url"], "verified": verified, "source_id": identity, "verification_source_id": key if verified else None, "window_inventory_complete": False,
                       "availability": "public profile metadata only; posts unavailable" if platform == "Instagram" else "proxy CONNECT blocked; origin HTTP response unavailable" if platform == "YouTube" else "HTTP 999; content unavailable and candidate identity unverified",
                       "profile_display": None, "profile_html_display": None, "exact_followers": None}
            if platform == "Instagram":
                text = browser_map[identity + "-browser"].get("public_text", "")
                match = re.search(r"([\d.,]+[KM]?) followers", text, re.I)
                account["profile_display"] = match.group(1) if match else None
                account["profile_html_display"] = next((row["content"] for row in source["extract"]["metadata"] if row["name"] == "og:description"), None)
                account["display_limitation"] = "Rounded current profile snapshot; HTTP and browser displays differ. Neither is treated as an exact or period-matched denominator."
            accounts.append(account)
    return {"status": "partial evidence-backed draft; period metrics blocked", "observation_window": WINDOW,
            "source_ids": [source["id"] for source in sources], "browser_source_ids": [source["id"] for source in browsers],
            "accounts": accounts, "posts": [], "facts": facts,
            "recommendations": [
                {"priority": "P1", "title": "Routine-first comparison aid", "evidence_ids": ["H2", "O1", "S1"], "proposal": "For fictional RefillLoop, test a commute/desk/training decision carousel with explicit carry and maintenance questions. This complements observed collection and product-benefit framing; it does not claim competitors lack functional guidance.", "validation": "Compare qualified concept-page clicks for routine-led versus collection-led copy in a future authorized test."},
                {"priority": "P2", "title": "Practical care and module-choice content", "evidence_ids": ["H3", "O1", "S3"], "proposal": "Develop a clearly hypothetical module/care explainer answering everyday-use questions. Hydro Flask's visible Clean & Care label is a reason to meet that user need, not a claim that the category ignores it.", "validation": "Test saves and FAQ clicks; verify actual product instructions before making factual claims."},
                {"priority": "P3", "title": "Recognizable community participation", "evidence_ids": ["S2", "O3"], "proposal": "Plan a low-effort refill-friction prompt with a clear response and privacy path. Membership and community labels show participation cues already exist; research audience response before asserting a market gap.", "validation": "Track voluntary useful replies, moderation burden and consent in a future authorized campaign."},
            ],
            "limitations": ["Website/profile snapshots were collected on 14 October 2026, outside the fixed post window; they cannot establish period activity.", "No dated public posts or interaction numerators were recovered; sample size is zero retained posts, not evidence of zero account activity.", "All period cadence and engagement metrics remain null. Rounded profile displays differ across response methods and are not precise denominators.", "LinkedIn candidates and the Owala YouTube candidate are unverified; failure does not imply absent accounts or strategies.", "Owala assets/CSS and Instagram assets loaded incompletely. Owala visual interpretation uses attributed alt text; no complete website or social-grid design assessment is claimed.", "No reviewer handoff or user-supplied public screenshots have been provided in this recovery turn."]}


def main():
    sources = json.loads((EVIDENCE / "source_records.json").read_text())
    browsers = json.loads((EVIDENCE / "browser_records.json").read_text())
    # Represent curl 000 explicitly as no origin response, not an HTTP status.
    for source in sources:
        source.setdefault("curl_http_code", "000" if source["http_status"] == 0 else str(source["http_status"]))
        if source["http_status"] == 0:
            source["http_status"] = None
    (EVIDENCE / "source_records.json").write_text(json.dumps(sources, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    data = build(sources, browsers)
    errors = validate(data, sources, browsers)
    if errors:
        raise ValueError("; ".join(errors))
    (RESEARCH / "observations.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (EVIDENCE / "metrics.json").write_text(json.dumps(calculate(data), indent=2) + "\n", encoding="utf-8")
    registry = ["# Task 2 recovery source registry", "", "Original 13 October failure records outside recovery/ remain unchanged. These records were collected on 14 October 2026 UTC. HTTP 200 alone does not prove post availability. No reviewer handoff has been supplied.", "", "| ID | Requested URL | UTC collection | Origin HTTP / transport | Identity / provenance | Raw SHA-256 |", "| --- | --- | --- | --- | --- | --- |"]
    for source in sources:
        registry.append(f"| {source['id']} | {source['url']} | {source['collected_utc']} | {source['http_status'] if source['http_status'] is not None else 'Unavailable (curl 000)'} / curl {source['transport_exit_code']} | {source['account_verification']} | {source['sha256_raw'] or 'No body received'} |")
    registry.extend(["", "## Browser sources", "", "All browser captures are normal unauthenticated pages, without login or access-control bypass. Text records and screenshot digests are in browser_records.json; raw screenshots stay ignored. Instagram has no recovered dated post links. Owala and Instagram assets/CSS loaded incompletely.", "", "| ID | URL | UTC collection | HTTP | Screenshot SHA-256 |", "| --- | --- | --- | --- | --- |"])
    for source in browsers:
        registry.append(f"| {source['id']} | {source['url']} | {source['collected_utc']} | {source.get('http_status', 'Unavailable')} | {source.get('screenshot_sha256', 'Unavailable')} |")
    (RESEARCH / "SOURCE_REGISTRY.md").write_text("\n".join(registry) + "\n", encoding="utf-8")
    matrix = ["# Source-backed competitor positioning matrix — partial recovery", "", "Current website/profile snapshots are outside the fixed post window. No cadence, post-format pattern or engagement performance is inferred.", "", "| Brand | Fact ID | Direct observation | Interpretation (not measured result) | Evidence ID |", "| --- | --- | --- | --- | --- |"]
    for fact in data["facts"]:
        matrix.append(f"| {fact['brand']} | {fact['id']} | {fact['quote']} | {fact['interpretation']} | {fact['source_id']} |")
    (RESEARCH / "POSITIONING_MATRIX.md").write_text("\n".join(matrix) + "\n", encoding="utf-8")
    print(f"Validated {len(data['facts'])} source-linked qualitative facts; 0 dated posts. Period metrics remain unavailable.")


if __name__ == "__main__":
    main()
