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


def action(day: int, phase: str, platform: str, content_format: str, theme: str,
           concept: str, persona: str, copy: str, cta: str, distribution: str,
           time: str, kpi: str, role: str, production: str) -> dict[str, Any]:
    return {
        "day": day, "phase": phase, "platform": platform,
        "content_format": content_format, "campaign_theme": theme,
        "creative_concept": concept, "target_persona": persona,
        "copy_or_script": copy, "cta": cta, "distribution": distribution,
        "proposed_publication_time": time, "kpi": kpi,
        "responsible_role": role, "production_requirements": production,
    }


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
            f"RefillLoop — proposed modular hydration for the moments your routine changes. {concept}",
            cta, paid, "18:30 audience local time (test variable)",
            "Reach / 3-second view rate" if content_format == "Reel" else "Saves, replies, or poll participation",
            "Social lead", "Vertical edit or 4–6 slide layout; accessibility captions; legal/claim review."
        ))
    for day, (content_format, theme, concept, cta) in LINKEDIN.items():
        actions.append(action(
            day, "Prelaunch" if day <= 7 else "Launch" if day <= 12 else "Education" if day <= 18 else "Optimization" if day <= 22 else "Conversion",
            "LinkedIn", content_format, theme, concept, "Aisha — workplace wellbeing lead",
            f"RefillLoop planning note: {concept}", cta,
            "Paid" if day in {7, 15, 23, 28} else "Organic",
            "09:00 target professional local time (test variable)",
            "Document opens / qualified clicks / poll votes", "B2B content lead",
            "Professional copy edit; document design or article QA; UTM link and claim review."
        ))
    for day, (content_format, theme, concept, cta) in YOUTUBE.items():
        actions.append(action(
            day, "Tease" if day <= 6 else "Launch" if day <= 11 else "Education" if day <= 17 else "Optimization" if day <= 22 else "Conversion",
            "YouTube", content_format, theme, concept, "Sam — active routine builder",
            f"RefillLoop concept video: {concept}", cta,
            "Paid" if day in {8, 15, 22, 29} else "Organic",
            "17:00 audience local time (test variable)",
            "Average view duration / end-screen CTR" if content_format == "Long-form" else "Shorts views / viewed-versus-swiped-away",
            "Video producer", "Script, storyboard, voiceover, captions, thumbnail, end screen, and concept disclaimer."
        ))
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
            {"objective": "Generate early-access intent", "smart_target": "Model 300 proposed qualified interest-form completions, with the actual result reported only after a live, consented launch.", "baseline_assumption": "Illustrative 1.5% landing-page completion rate; not a forecast.", "measurement": "Consent-aware form-completion event and source UTM."},
        ],
        "budget": {"currency": "USD", "total": 3000, "allocation": {"Instagram": 1350, "LinkedIn": 1050, "YouTube": 600}, "assumption": "Illustrative media-only planning budget; no spend is authorized or incurred."},
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
    budget = campaign["budget"]
    if sum(budget["allocation"].values()) != budget["total"]:
        errors.append("Paid-media allocation does not equal total budget.")
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
