"""Build and validate the fictional RefillLoop 30-day campaign calendar."""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = Path(__file__).with_name("campaign_calendar.json")
REQUIRED_ACTION_FIELDS = {
    "day", "phase", "platform", "content_format", "campaign_theme",
    "creative_concept", "target_persona", "copy_or_script", "cta",
    "distribution", "proposed_publication_time", "kpi", "responsible_role",
    "production_requirements",
    "action_id", "targeting_id", "keyword_strategy", "ad_copy",
}

DAY_THEMES = [
    ("Tease", "The daily carry problem", "A quick-cut commute montage asks: ‘One bottle, one routine?’", "Save the launch reminder."),
    ("Tease", "Modular by design", "Exploded-view carousel introduces the proposed replaceable components.", "Join the early-access list."),
    ("Tease", "Your refill friction", "Question sticker: ‘What makes reusable habits hard to keep?’", "Reply with one barrier."),
    ("Tease", "Built for handoffs", "Desk-to-gym transition shows a proposed modular carry routine.", "Comment with your daily switch."),
    ("Tease", "Routine reset", "Before/after bag-pack sequence frames refill preparation as a simple ritual.", "Save the packing checklist."),
    ("Tease", "Countdown", "Five-second timer and component silhouettes introduce launch week.", "Turn on reminders."),
    ("Prelaunch", "Choose your loop", "Story poll compares commuting, training, and desk-day routines.", "Vote for your routine."),
    ("Launch", "Reveal", "Hero reel reveals the fictional RefillLoop concept and its proposed module system.", "Visit the concept page."),
    ("Launch", "What changes", "Carousel contrasts a single-use habit with a planned refill routine without environmental performance claims.", "Explore the proposed system."),
    ("Launch", "First-use flow", "Short demonstration shows proposed assemble, fill, carry, and clean steps.", "Watch the full demo."),
    ("Launch", "Design choices", "Macro shots highlight texture, closure, and module transitions as creative concepts.", "Save the feature guide."),
    ("Launch", "Routine proof", "Creator-style POV follows a fictional commuter’s refill prompts.", "Share your refill cue."),
    ("Education", "Module logic", "Carousel explains which proposed component fits work, travel, or training.", "Build a routine."),
    ("Education", "Care without claims", "Step-by-step care animation presents a proposed maintenance checklist.", "Download the checklist."),
    ("Education", "Habit stack", "Reel pairs filling a bottle with an existing morning habit.", "Try one habit stack."),
    ("Education", "What is modular?", "Question box answers common concept questions in plain language.", "Ask a question."),
    ("Education", "Carry confidence", "Packing sequence demonstrates a proposed workday configuration.", "Save this setup."),
    ("Education", "Community prompt", "Story asks followers to post their refill station setup.", "Tag the campaign prompt."),
    ("Optimization", "Feature preference", "Two creative directions invite a preference vote: utility-first or lifestyle-first.", "Vote in the poll."),
    ("Optimization", "Objection clinic", "Carousel addresses proposed buyer questions about fit, care, and routine.", "Send a question."),
    ("Optimization", "Behind the brief", "Reel explains that RefillLoop is a proposed modular-product concept.", "Follow for build updates."),
    ("Optimization", "Desk-day system", "Fast-cut workflow shows proposed hydration cues between meetings.", "Save the desk routine."),
    ("Conversion", "Choose your starting point", "Carousel routes three fictional personas to their suggested configuration.", "Choose your path."),
    ("Conversion", "Early-access value", "Reel states the proposed early-access benefit without promising availability.", "Request early access."),
    ("Conversion", "FAQ recap", "Story sequence answers the most common campaign questions collected to date.", "Review the concept FAQ."),
    ("Conversion", "Workplace challenge", "Reel invites teams to test a proposed refill-routine prompt internally.", "Download the team prompt."),
    ("Conversion", "Last-call reminder", "Countdown creative reminds viewers that early-access interest is still proposed.", "Join the interest list."),
    ("Conversion", "Community thank-you", "Carousel recaps ideas shared during the fictional campaign exercise.", "Share one improvement."),
    ("Conversion", "Next-loop preview", "Reel previews post-campaign concept testing and feedback review.", "Stay on the list."),
    ("Conversion", "Close and learn", "Story survey asks what content would help a future buyer decide.", "Complete the one-question survey."),
]

LINKEDIN = {
    2: ("Document post", "The hidden cost of fragmented routines", "A proposed product brief: why commuters, facilities teams, and wellbeing leads need fewer hydration handoffs.", "Read the concept brief."),
    4: ("Founder-style text post", "Designing for routines, not novelty", "Professional storytelling frames RefillLoop as a fictional exercise in modular service design.", "Comment with a workflow friction."),
    7: ("Carousel", "Workplace refill prompt", "Five slides show a proposed facilities-team activation: location cue, owner, message, measure, learn.", "Save the activation template."),
    9: ("Poll", "Which barrier matters most?", "Poll options test time, carry convenience, cleaning, and forgetting as assumed barriers.", "Vote and explain."),
    12: ("Case-style post", "A day in a hybrid-work routine", "A fictional persona illustrates proposed use across commute, desk, and training.", "Review the use-case map."),
    15: ("Article", "From awareness to habit", "Thought-leadership article explains the proposed campaign’s behavior-design logic and measurement plan.", "Read the full framework."),
    18: ("Carousel", "What teams can measure", "A proposed dashboard defines reach, qualified visits, waitlist intent, and feedback—not claimed outcomes.", "Download KPI definitions."),
    21: ("Text post", "What the audience told us to test", "States planned A/B questions, not results: utility versus lifestyle framing and CTA wording.", "Follow the test plan."),
    23: ("Document post", "Modular product storytelling", "Shows how one concept becomes a consumer reel, a workplace brief, and a demonstration script.", "Save the content map."),
    26: ("Poll", "What earns early-access interest?", "Poll tests clarity, utility, design, and community as proposed message routes.", "Choose one factor."),
    28: ("Carousel", "Implementation checklist", "Practical checklist covers creative approval, landing-page QA, tagging, consent, and response ownership.", "Share with a launch lead."),
    30: ("Text post", "Campaign learning handoff", "Closes the fictional exercise with what to preserve, test, and validate before a real launch.", "Request the planning template."),
}

YOUTUBE = {
    3: ("Short", "The refill friction in 20 seconds", "Vertical script: bag, desk, gym; caption: ‘What would make your routine easier?’", "Subscribe for the concept series."),
    6: ("Short", "A proposed module swap", "Vertical script: show an animated module change with labels for the fictional components.", "Watch the launch reveal."),
    8: ("Long-form", "RefillLoop concept walkthrough", "Four-minute narrated demonstration explains the fictional concept, intended users, care assumptions, and open questions.", "Visit the concept page."),
    11: ("Short", "Three routine cues", "Vertical script gives three proposed prompts: bag check, desk reset, post-workout refill.", "Try one cue."),
    15: ("Long-form", "How a modular routine is planned", "Five-minute behind-the-brief video distinguishes design assumptions from verified product claims.", "Comment with a test question."),
    17: ("Short", "Desk-to-door carry setup", "Vertical transition follows a fictional hybrid worker through a proposed configuration.", "Save the setup idea."),
    20: ("Short", "Care checklist preview", "Vertical checklist introduces simple proposed care steps; no health or material-performance claim.", "Watch the detailed guide."),
    22: ("Long-form", "Workplace refill challenge toolkit", "Six-minute tutorial gives a proposed internal-activation playbook for people teams and facilities leads.", "Download the toolkit."),
    25: ("Short", "Choose your loop", "Vertical quiz asks viewers to select commuter, trainer, or desk-day configuration.", "Comment with your route."),
    27: ("Short", "FAQ in 30 seconds", "Answer three campaign questions: what is modular, who is it for, and what is still being tested.", "Ask another question."),
    29: ("Long-form", "Campaign learning recap", "Five-minute recap covers proposed experiments, feedback collection, and real-launch prerequisites.", "Join the interest list."),
}

IG_COPY = [
    ("Your day has more than one stop.", "A proposed RefillLoop routine starts by mapping the moments when your carry setup changes."),
    ("What if your bottle routine could change with your day?", "Explore a fictional modular concept built around switching contexts, not a promised product feature."),
    ("The hard part is often remembering the next refill.", "Tell us where your routine breaks: leaving home, arriving at work, or after training."),
    ("Commute. Desk. Training. One routine map.", "This concept creative follows the handoffs that make reusable habits harder to repeat."),
    ("A better routine begins before the bag leaves the door.", "Save this proposed packing cue and adapt it to your own day."),
    ("Something new is being explored for changing routines.", "Follow the concept countdown; availability is not being promised."),
    ("Which moment needs the clearest refill cue?", "Vote: commute, desk day, or training. The answer informs a future concept test."),
    ("Meet RefillLoop — a proposed modular hydration concept.", "This reveal introduces an idea to test, not a product ready to buy."),
    ("A reusable habit needs a plan for the in-between moments.", "See how a proposed routine map can connect carry, fill, and reset."),
    ("Four proposed steps: assemble, fill, carry, reset.", "Watch the concept flow, then decide which step needs more clarity."),
    ("Design details only matter when they support a routine.", "Zoom in on the fictional components and share the question you would ask first."),
    ("A refill cue can travel with the rest of your routine.", "This creator-style scenario is illustrative; share the cue that works for you."),
    ("Choose a proposed configuration for work, travel, or training.", "Start with the context, then test what you actually need."),
    ("Care guidance should be clear before it is persuasive.", "Save this proposed checklist; final product instructions would require validation."),
    ("Try linking one refill action to a habit you already have.", "A calendar reminder, bag check, or desk reset can become the cue."),
    ("Questions make a concept stronger.", "Ask about modules, routine prompts, or what still needs testing."),
    ("A workday carry setup should be easy to explain.", "Save this fictional configuration as a discussion prompt, not a performance claim."),
    ("Show the place where your refill routine starts.", "Use the campaign prompt to share a setup idea; do not share personal data."),
    ("Would you rather see utility-first or lifestyle-first creative?", "Vote so the next proposed message test begins with a clear audience preference."),
    ("Fit, care, and routine are questions worth answering plainly.", "Send the question that would prevent you from trying a new concept."),
    ("Behind every concept is a list of assumptions to test.", "This brief separates planned design language from verified product claims."),
    ("A desk routine needs a cue that fits between meetings.", "Save this proposed reset sequence for your next workday experiment."),
    ("Start with the routine that changes most often.", "Choose commuter, desk-day, or training to see the relevant concept path."),
    ("Early access begins with informed interest, not urgency.", "Request a future update if the concept is relevant to your routine."),
    ("FAQ first, assumptions second.", "Review the questions this fictional campaign is designed to answer."),
    ("Teams can test a refill cue without making a product claim.", "Download the proposed internal prompt and adapt it with workplace approval."),
    ("Still curious about the proposed concept?", "Join the interest list only if you want a future, consent-aware update."),
    ("Community ideas can improve a concept before a launch exists.", "Share one change that would make your routine easier to repeat."),
    ("The next loop is feedback, testing, and clearer decisions.", "Follow for future concept-development updates, not availability promises."),
    ("What content would help you decide later?", "Answer one question so a future launch can explain the right thing first."),
]

LI_COPY = {
    day: f"{theme}. {concept} This is a proposed planning exercise for teams that want to make routine prompts easier to test."
    for day, (_, theme, concept, _) in LINKEDIN.items()
}
YT_COPY = {
    day: {
        "title": f"RefillLoop concept: {theme}",
        "description": f"{concept} This video describes a fictional proposed campaign concept; it does not claim product availability or outcome.",
        "outline": "Hook the routine friction; demonstrate the proposed concept; label assumptions; invite a specific feedback action."
    }
    for day, (_, theme, concept, _) in YOUTUBE.items()
}

PLATFORM_TARGETING = {
    "Instagram": {
        "targeting_id": "IG-KHI-01",
        "geography": "Proposed initial test market: Karachi metropolitan area; rationale: one defined urban test area makes creative learning easier to interpret. This is not evidence of demand.",
        "language": "English creative; review Urdu adaptation for comprehension and platform capability before launch.",
        "age": "Proposed 23–40 where available; verify current platform controls.",
        "inclusion": "Policy-compliant interest/context tests around commuting, hybrid work, productivity, fitness routines, and reusable products; verify availability before use.",
        "exclusion": "Exclude existing interest-form completers from conversion retargeting where a lawful consent-aware audience is available; do not infer sensitive traits.",
        "placement": "Reels, Stories, and Feed tested separately; retain placement-level reporting.",
        "conversion_event": "Consent-aware early-interest form completion or qualified concept-page visit.",
        "privacy_policy": "Use platform-approved controls only; verify options and privacy requirements before a live campaign."
    },
    "LinkedIn": {
        "targeting_id": "LI-KHI-01",
        "geography": "Proposed initial test market: Karachi metropolitan area; use a single professional-context test area for interpretable learning.",
        "language": "English professional copy; review Urdu adaptation separately if supported and appropriate.",
        "age": "No age-based professional targeting is proposed; use platform-approved professional context only.",
        "inclusion": "Verify current targeting for people operations, workplace experience, facilities, and operations functions; use role/function contexts, not sensitive inferences.",
        "exclusion": "Exclude current employees and completed interest-form audiences only where lawful, consented, and supported by the platform.",
        "placement": "Feed and document/article formats; compare sponsored document with text-post treatment.",
        "conversion_event": "Qualified toolkit download or consent-aware early-interest form completion.",
        "privacy_policy": "Platform controls and minimum-audience rules must be verified before launch."
    },
    "YouTube": {
        "targeting_id": "YT-KHI-01",
        "geography": "Proposed initial test market: Karachi metropolitan area; separate geographic expansion from the first creative test.",
        "language": "English spoken/captioned creative; review Urdu captions or alternate creative before use.",
        "age": "Proposed adult audience only where age controls are available and policy-compliant; verify current options.",
        "inclusion": "Contextual tests around commuting organization, workplace productivity, fitness routines, and reusable-product education; verify placement controls.",
        "exclusion": "Exclude made-for-children content and unsuitable placements using current documented controls; do not profile sensitive audiences.",
        "placement": "Shorts for discovery; skippable long-form/contextual inventory for demonstrations; report format separately.",
        "conversion_event": "Qualified concept-page session or consent-aware early-interest form completion.",
        "privacy_policy": "Verify current YouTube/Google Ads targeting, placement, and consent requirements before launch."
    },
}

KEYWORD_CLUSTERS = {
    "routine": {"primary": "reusable hydration routine", "supporting": ["daily refill habit", "routine design", "carry routine"], "intent": "Discover practical routine prompts for a proposed reusable-hydration concept."},
    "commute": {"primary": "commuter hydration routine", "supporting": ["hybrid work commute", "bag packing routine", "desk to gym"], "intent": "Find ideas for changing locations and carry contexts."},
    "modular": {"primary": "modular reusable bottle concept", "supporting": ["modular product design", "reusable hydration", "product concept"], "intent": "Understand the proposed modular-product framing."},
    "workplace": {"primary": "workplace wellbeing routine", "supporting": ["workplace hydration prompt", "hybrid team wellbeing", "facilities activation"], "intent": "Find a proposed workplace implementation or discussion tool."},
    "education": {"primary": "refill habit education", "supporting": ["hydration routine checklist", "care checklist", "habit stacking"], "intent": "Learn a proposed routine or care framework without performance claims."},
}


def keyword_strategy(platform: str, theme: str, phase: str) -> dict[str, Any]:
    lower = (theme + " " + phase).lower()
    cluster_name = "workplace" if "work" in lower or "team" in lower else "commute" if any(word in lower for word in ("carry", "commut", "desk")) else "modular" if any(word in lower for word in ("module", "design", "reveal")) else "education" if any(word in lower for word in ("care", "habit", "faq", "logic")) else "routine"
    cluster = KEYWORD_CLUSTERS[cluster_name]
    labels = {
        "Instagram": ["#RefillLoopConcept", "#ReusableHydration", "#RoutineDesign"],
        "LinkedIn": ["#WorkplaceWellbeing", "#RoutineDesign", "#ProductConcept"],
        "YouTube": ["refill routine", "reusable hydration", "modular product concept"],
    }[platform]
    return {
        "cluster": cluster_name,
        "primary_keyword": cluster["primary"],
        "supporting_keywords": cluster["supporting"],
        "hashtags_or_video_tags": labels,
        "search_discovery_intent": cluster["intent"],
        "rationale": f"Connects the {platform} format to the {cluster_name} discovery cluster; no search volume or ranking is claimed."
    }


def action(day: int, phase: str, platform: str, content_format: str, theme: str,
           concept: str, persona: str, copy: str, cta: str, distribution: str,
           time: str, kpi: str, role: str, production: str, ad_copy: dict[str, str],
           ab_test_id: str | None = None) -> dict[str, Any]:
    item = {
        "action_id": f"{platform.lower()}-{day:02d}",
        "day": day, "phase": phase, "platform": platform,
        "content_format": content_format, "campaign_theme": theme,
        "creative_concept": concept, "target_persona": persona,
        "copy_or_script": copy, "cta": cta, "distribution": distribution,
        "proposed_publication_time": time, "kpi": kpi,
        "responsible_role": role, "production_requirements": production,
        "targeting_id": PLATFORM_TARGETING[platform]["targeting_id"],
        "keyword_strategy": keyword_strategy(platform, theme, phase),
        "ad_copy": ad_copy,
    }
    if ab_test_id:
        item["ab_test_id"] = ab_test_id
    return item


def build_campaign() -> dict[str, Any]:
    actions: list[dict[str, Any]] = []
    formats = ["Reel", "Carousel", "Stories", "Reel", "Stories"]
    personas = ["Maya — hybrid commuter", "Sam — active routine builder", "Aisha — workplace wellbeing lead"]
    for day, (phase, theme, concept, cta) in enumerate(DAY_THEMES, start=1):
        content_format = formats[(day - 1) % len(formats)]
        paid = "Paid" if day in {8, 10, 15, 19, 23, 24, 27} else "Organic"
        actions.append(action(
            day, phase, "Instagram", content_format, theme, concept,
            personas[(day - 1) % len(personas)],
            IG_COPY[day - 1][1],
            cta, paid, "18:30 audience local time (test variable)",
            "Reach / 3-second view rate" if content_format == "Reel" else "Saves, replies, or poll participation",
            "Social lead", "Vertical edit or 4–6 slide layout; accessibility captions; legal/claim review.",
            {"primary_text": IG_COPY[day - 1][1], "headline_or_hook": IG_COPY[day - 1][0], "cta_line": cta},
            {8: "AB-01", 19: "AB-04", 23: "AB-04"}.get(day)
        ))
    for day, (content_format, theme, concept, cta) in LINKEDIN.items():
        actions.append(action(
            day, "Prelaunch" if day <= 7 else "Launch" if day <= 12 else "Education" if day <= 18 else "Optimization" if day <= 22 else "Conversion",
            "LinkedIn", content_format, theme, concept, "Aisha — workplace wellbeing lead",
            LI_COPY[day], cta,
            "Paid" if day in {7, 15, 23, 28} else "Organic",
            "09:00 target professional local time (test variable)",
            "Document opens / qualified clicks / poll votes", "B2B content lead",
            "Professional copy edit; document design or article QA; UTM link and claim review.",
            {"primary_text": LI_COPY[day], "headline_or_hook": theme, "cta_line": cta},
            {15: "AB-02", 23: "AB-02"}.get(day)
        ))
    for day, (content_format, theme, concept, cta) in YOUTUBE.items():
        actions.append(action(
            day, "Tease" if day <= 6 else "Launch" if day <= 11 else "Education" if day <= 17 else "Optimization" if day <= 22 else "Conversion",
            "YouTube", content_format, theme, concept, "Sam — active routine builder",
            YT_COPY[day]["description"] + " Outline: " + YT_COPY[day]["outline"], cta,
            "Paid" if day in {8, 15, 22, 29} else "Organic",
            "17:00 audience local time (test variable)",
            "Average view duration / end-screen CTR" if content_format == "Long-form" else "Shorts views / viewed-versus-swiped-away",
            "Video producer", "Script, storyboard, voiceover, captions, thumbnail, end screen, and concept disclaimer.",
            {"video_title": YT_COPY[day]["title"], "description": YT_COPY[day]["description"], "script_outline": YT_COPY[day]["outline"], "cta_line": cta},
            {22: "AB-03"}.get(day)
        ))
    pacing = [
        ("instagram-08", "Instagram", 8, "Launch", 300), ("instagram-10", "Instagram", 10, "Launch", 180),
        ("instagram-15", "Instagram", 15, "Education", 180), ("instagram-19", "Instagram", 19, "Optimization", 180),
        ("instagram-23", "Instagram", 23, "Conversion", 180), ("instagram-24", "Instagram", 24, "Conversion", 180),
        ("instagram-27", "Instagram", 27, "Conversion", 150),
        ("linkedin-07", "LinkedIn", 7, "Prelaunch", 150), ("linkedin-15", "LinkedIn", 15, "Education", 300),
        ("linkedin-23", "LinkedIn", 23, "Conversion", 300), ("linkedin-28", "LinkedIn", 28, "Conversion", 300),
        ("youtube-08", "YouTube", 8, "Launch", 150), ("youtube-15", "YouTube", 15, "Education", 150),
        ("youtube-22", "YouTube", 22, "Optimization", 150), ("youtube-29", "YouTube", 29, "Conversion", 150),
    ]
    return {
        "campaign": {
            "name": "RefillLoop: Make the refill routine easier to repeat",
            "classification": "Fictional proposed campaign; no product launch, performance, customer, or environmental claim.",
            "product_assumptions": [
                "RefillLoop is a proposed modular reusable hydration system with replaceable carry components.",
                "A proposed companion experience supplies optional routine prompts; no health, scientific, or impact benefit is claimed.",
                "Illustrative early-access price hypothesis: USD 44–64; validate willingness to pay before a real launch."
            ],
            "positioning": "A proposed routine-design system for people whose hydration needs shift across commute, desk, training, and travel—not a claim of market leadership.",
            "differentiation": ["Modular routine framing", "Cross-channel habit education", "Workplace activation toolkit", "Feedback-led concept validation"],
        },
        "personas": [
            {"name": "Maya — hybrid commuter", "segment": "Urban professionals, 24–38", "motivation": "Reduce carry friction across changing locations", "pain_point": "Forgets or abandons routines when plans change", "targeting": "Interest/context test: commuting, hybrid work, productivity; exclude unsupported demographic inference."},
            {"name": "Sam — active routine builder", "segment": "Active adults, 22–35", "motivation": "Keep a repeatable work-to-training routine", "pain_point": "Needs simple cues and portable organization", "targeting": "Interest/context test: training routines, wellbeing content, reusable products; test creative, do not assume conversion."},
            {"name": "Aisha — workplace wellbeing lead", "segment": "People, facilities, and operations practitioners", "motivation": "Offer low-friction routine prompts for hybrid teams", "pain_point": "Needs practical, measurable internal activations", "targeting": "LinkedIn job-function/context test: people operations, workplace experience, facilities; use platform policy-compliant targeting only."},
        ],
        "objectives": [
            {"objective": "Build qualified concept awareness", "smart_target": "Over 30 days, deliver 120,000 proposed paid-and-organic impressions while recording platform-native reach separately.", "baseline_assumption": "No prior audience or account baseline is available.", "measurement": "Platform reach exports and UTM-tagged landing-page sessions."},
            {"objective": "Validate message routes", "smart_target": "Run at least four planned A/B creative or CTA comparisons and retain a decision log by Day 30.", "baseline_assumption": "No prior creative winner is assumed.", "measurement": "Predefined primary KPI per test; do not call a winner without adequate delivery and context."},
            {"objective": "Generate early-access intent", "smart_target": "Model 30 base-scenario qualified interest-form completions over 30 days; report 300 only as a stretch scenario with separate traffic conditions.", "baseline_assumption": "Base scenario uses 120,000 impressions, 1.0% assumed CTR, and 2.5% assumed form completion; not a forecast.", "measurement": "Consent-aware form-completion event and source UTM."},
        ],
        "budget": {"currency": "USD", "total": 3000, "allocation": {"Instagram": 1350, "LinkedIn": 1050, "YouTube": 600}, "assumption": "Illustrative media-only planning budget; no spend is authorized or incurred."},
        "targeting_specifications": PLATFORM_TARGETING,
        "funnel": {
            "formula": "interest completions = impressions × click-through rate × landing-form completion rate",
            "units": {"impressions": "impressions", "click_through_rate": "decimal share", "landing_sessions": "sessions", "form_completion_rate": "decimal share", "interest_completions": "completed consent-aware forms"},
            "scenarios": [
                {"name": "Low", "impressions": 75000, "click_through_rate": 0.006, "landing_sessions": 450, "form_completion_rate": 0.015, "interest_completions": 6.75, "classification": "illustrative planning scenario"},
                {"name": "Base", "impressions": 120000, "click_through_rate": 0.01, "landing_sessions": 1200, "form_completion_rate": 0.025, "interest_completions": 30, "classification": "primary planned target; assumptions only"},
                {"name": "High", "impressions": 180000, "click_through_rate": 0.016, "landing_sessions": 2880, "form_completion_rate": 0.035, "interest_completions": 100.8, "classification": "illustrative upside scenario"},
                {"name": "Stretch", "impressions": 240000, "click_through_rate": 0.025, "landing_sessions": 6000, "form_completion_rate": 0.05, "interest_completions": 300, "classification": "not a primary target; requires 6,000 sessions and materially stronger traffic conditions or additional authorized reach"},
            ]
        },
        "budget_pacing": [{"action_id": action_id, "platform": platform, "day": day, "phase": phase, "proposed_spend_usd": spend, "note": "Proposed media-only spend; not incurred."} for action_id, platform, day, phase, spend in pacing],
        "ab_tests": [
            {"id": "AB-01", "hypothesis": "A routine-friction hook earns more qualified concept clicks than a general product-reveal hook.", "control": "Day 8 utility-led reveal", "treatment": "Day 8 routine-friction opening", "audience": "IG-KHI-01 / Maya creative route", "primary_metric": "UTM-tagged concept-page click-through rate", "decision_criterion": "Pre-agree a minimum delivery threshold; retain the variant with the stronger primary metric and document context."},
            {"id": "AB-02", "hypothesis": "A LinkedIn document explaining implementation earns more qualified clicks than a professional text post.", "control": "Text-post treatment", "treatment": "Document-post treatment", "audience": "LI-KHI-01 / Aisha creative route", "primary_metric": "Qualified toolkit or concept-page clicks", "decision_criterion": "Compare only after equivalent planned delivery conditions; record no winner if evidence is insufficient."},
            {"id": "AB-03", "hypothesis": "A workplace-toolkit video opening sustains more qualified attention than a feature-led opening.", "control": "Feature-led opening", "treatment": "Workplace-toolkit opening", "audience": "YT-KHI-01 / Aisha contextual route", "primary_metric": "Average view duration and end-screen click-through rate", "decision_criterion": "Use a pre-agreed attention threshold and report both measures, not views alone."},
            {"id": "AB-04", "hypothesis": "‘Choose your path’ creates more qualified interest than ‘request early access’ for undecided routine seekers.", "control": "Request early access", "treatment": "Choose your path", "audience": "IG-KHI-01 / Maya and Sam retargeting only if lawful and consent-aware", "primary_metric": "Consent-aware form completion rate", "decision_criterion": "Require comparable landing experience and documented delivery before deciding."},
        ],
        "sources": [
            {"reference": "Digital Marketing & Branding Tasks & Instructions.md", "use": "Task 3 required platforms and deliverable scope."},
            {"reference": "planning/DIGITAL_MARKETING_RESEARCH_PLAN.md", "use": "Approved fictional RefillLoop campaign context."}
        ],
        "actions": sorted(actions, key=lambda item: (item["day"], item["platform"])),
    }


def validate(campaign: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    actions = campaign["actions"]
    if set(range(1, 31)) - {item["day"] for item in actions}:
        errors.append("One or more of the 30 days has no planned action.")
    platforms = Counter(item["platform"] for item in actions)
    for platform in ("Instagram", "LinkedIn", "YouTube"):
        if not platforms[platform]:
            errors.append(f"Missing required platform: {platform}.")
    for index, item in enumerate(actions, start=1):
        missing = REQUIRED_ACTION_FIELDS - set(item)
        if missing:
            errors.append(f"Action {index} is missing: {sorted(missing)}")
        if item["day"] not in range(1, 31):
            errors.append(f"Action {index} has an invalid day.")
    action_ids = [item.get("action_id") for item in actions]
    if len(action_ids) != len(set(action_ids)):
        errors.append("Campaign contains duplicate action IDs.")
    schedule_slots = [(item.get("day"), item.get("platform")) for item in actions]
    if len(schedule_slots) != len(set(schedule_slots)):
        errors.append("Campaign contains duplicate platform/day actions.")
    for index, item in enumerate(actions, start=1):
        keyword = item.get("keyword_strategy", {})
        if not keyword.get("primary_keyword") or not keyword.get("hashtags_or_video_tags"):
            errors.append(f"Action {index} has no usable keyword/tag strategy.")
        if item.get("targeting_id") not in {spec["targeting_id"] for spec in campaign.get("targeting_specifications", {}).values()}:
            errors.append(f"Action {index} has an invalid targeting specification.")
    budget = campaign["budget"]
    if sum(budget["allocation"].values()) != budget["total"]:
        errors.append("Paid-media allocation does not equal total budget.")
    pacing = campaign.get("budget_pacing", [])
    pacing_by_platform = Counter()
    for row in pacing:
        pacing_by_platform[row["platform"]] += row["proposed_spend_usd"]
    if dict(pacing_by_platform) != budget["allocation"]:
        errors.append("Budget pacing does not reconcile to platform allocation.")
    paid_action_ids = {item["action_id"] for item in actions if item["distribution"] == "Paid"}
    if paid_action_ids != {row["action_id"] for row in pacing}:
        errors.append("Every paid action must have exactly one pacing allocation.")
    for scenario in campaign.get("funnel", {}).get("scenarios", []):
        sessions = scenario["impressions"] * scenario["click_through_rate"]
        completions = sessions * scenario["form_completion_rate"]
        if abs(sessions - scenario["landing_sessions"]) > 1e-9 or abs(completions - scenario["interest_completions"]) > 1e-9:
            errors.append(f"Funnel arithmetic does not reconcile for {scenario['name']}.")
    for test in campaign.get("ab_tests", []):
        if not all(test.get(field) for field in ("hypothesis", "control", "treatment", "audience", "primary_metric", "decision_criterion")):
            errors.append(f"A/B test {test.get('id', 'unknown')} is incomplete.")
    return errors


def current_revision() -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()


def main() -> int:
    campaign = build_campaign()
    errors = validate(campaign)
    if errors:
        raise SystemExit("\n".join(errors))
    campaign["source_revision"] = current_revision()
    OUTPUT.write_text(json.dumps(campaign, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(campaign['actions'])} actions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
