"""Proposed email sequences and a pure, synthetic policy simulator.

No addresses, integrations, network calls, or sending capability are present.
Delays are hours from entry; policy is rechecked immediately before each send.
"""

from dataclasses import dataclass, field


POLICY = {
    "minimum_gap_hours": 24,
    "maximum_messages_rolling_7_days": 3,
    "priority": ["post_purchase", "cart", "browse", "welcome"],
    "entry_rule": "One active workflow per contact. Higher priority replaces lower; duplicate entry never restarts a clock.",
    "suppression": "Recheck marketing consent, unsubscribe, withdrawal, hard bounce, complaint and global suppression before every message.",
    "cap_rule": "Defer capped messages without advancing the step; expire at workflow deadline. Never burst-send overdue messages.",
    "inactivity_rule": "No tracked click or qualifying event by expiry ends the workflow. Opens are not required or treated as reliable intent.",
    "reentry_rule": "Completion or inactivity suppresses replay of that workflow in this proposed pilot; later reentry needs a new approved policy.",
}


def workflows():
    specifications = [
        ("welcome", "Welcome / nurture", "subscription_confirmed", "Confirmed marketing opt-in; no prior purchase, active cart or browse workflow.", 168, [
            (0, "Welcome to your next refill routine", "Start with product details, practical questions and a clear choice.",
             "Hello,\n\nThank you for choosing to hear from Ocean Bottle. If you are exploring a reusable bottle, start with the Original Bottle page to review the available features and options. Our FAQs cover delivery, returns and warranty questions so you can decide at your own pace.\n\nYou can also read how Ocean Bottle describes its collection model on the impact page. We do not ask you to take an environmental statement on trust: review the explanation before deciding.\n\nExplore the Original Bottle when you are ready.\n\nOcean Bottle team",
             "Explore Original Bottle", "/products/original-bottle", "qualified_product_view"),
            (48, "What would make refilling easier for you?", "A simple planning prompt for commuting, work or everyday use.",
             "Hello,\n\nThink about where a reusable bottle would fit into your day: the commute, your desk or a bag you already carry. Choose a practical routine first, then compare the Original Bottle details with what you need.\n\nIf you have questions about care, delivery or warranty, our FAQ page is a useful next stop. There is no need to make a choice before those questions are answered.\n\nRead the FAQs and return to the product page when it suits you.\n\nOcean Bottle team",
             "Read bottle FAQs", "/pages/faqs", "faq_visit"),
            (120, "Your reusable bottle questions, answered", "Review the details once more, or update what you want to hear about.",
             "Hello,\n\nThis is the last message in this welcome series. If you are still comparing options, the Original Bottle page brings the product information together, and the FAQs explain delivery and support topics.\n\nTake a look only if the bottle fits your needs. You can change your email preferences or unsubscribe at any time using the links below.\n\nThank you for considering Ocean Bottle.\n\nOcean Bottle team",
             "Review Original Bottle", "/products/original-bottle", "add_to_cart"),
        ]),
        ("browse", "Browsing without purchase", "product_view_twice", "Two consented product views within seven days; no cart or purchase.", 168, [
            (24, "Still comparing reusable bottle options?", "Review the Original Bottle details without rushing your decision.",
             "Hello,\n\nYou recently explored the Original Bottle. If you are still comparing options, return to the product page to review the current features, choices and availability.\n\nBefore ordering, check the delivery, warranty and returns information in our FAQs. This message is an invitation to review the details, not a promise that an item is reserved.\n\nFind the information you need before deciding.\n\nOcean Bottle team",
             "Review product details", "/products/original-bottle", "qualified_product_view"),
            (72, "What do you need to know before choosing?", "Delivery, warranty and care information in one place.",
             "Hello,\n\nChoosing a reusable bottle should include the practical details. Our FAQ sections cover delivery, returns, warranty and product questions. Use those answers to check whether the Original Bottle is right for you.\n\nIf a question remains, use the contact link on the website rather than guessing from an advertisement. We will stop this browsing series here unless you take another qualifying action under an approved future policy.\n\nOcean Bottle team",
             "Check delivery and warranty FAQs", "/pages/faqs", "faq_visit"),
        ]),
        ("cart", "Cart abandonment", "cart_abandoned", "Clock starts at last cart activity; only enroll when no purchase and separate marketing consent exists; first message requires four inactive hours.", 96, [
            (4, "Would you like to review your bottle choice?", "Return to the product information before placing an order.",
             "Hello,\n\nYou started considering an Ocean Bottle order. If you want to continue, review the Original Bottle page and select your preferred option again. Check the current price and availability on the website before ordering.\n\nIf delivery or returns were a concern, the FAQ page may help. We have not reserved stock or applied a discount in this message.\n\nContinue only when the choice works for you.\n\nOcean Bottle team",
             "Review Original Bottle", "/products/original-bottle", "checkout_started"),
            (52, "One last reminder, with the practical details", "Check delivery and support information if you are still deciding.",
             "Hello,\n\nThis is our final reminder about your earlier bottle selection. You can revisit the product page and check delivery, returns and warranty details before completing an order.\n\nIf you have already decided against it, no action is needed. This cart series will end, and you can update your email preferences or unsubscribe using the links below.\n\nThank you for considering Ocean Bottle.\n\nOcean Bottle team",
             "Check order FAQs", "/pages/faqs", "purchase"),
        ]),
        ("post_purchase", "Post-purchase re-engagement", "delivery_confirmed", "First purchase and confirmed delivery event; separate marketing consent; unresolved support issues pause entry.", 840, [
            (336, "Make the most of your reusable bottle", "Start with the current care and support information.",
             "Hello,\n\nWe hope the bottle is fitting into your routine. Please review the current care instructions and product FAQs before cleaning or using it in a new way.\n\nIf anything is unclear or there is a problem with the order, contact the support team through the website. We will pause promotional follow-ups while an unresolved support issue is being handled.\n\nOcean Bottle team",
             "Read care and support FAQs", "/pages/faqs", "care_guide_visit"),
            (504, "How is your refill routine working?", "Share a question or request help if something is not right.",
             "Hello,\n\nNow that you have had time to try the bottle, we would welcome a question or feedback about your experience. We do not assume that every purchase works perfectly for every person.\n\nIf you need help, use the website contact page and explain the issue. No public review is required, and support takes priority over further promotional messages.\n\nOcean Bottle team",
             "Contact support or share feedback", "/pages/contact", "feedback_or_support_contact"),
            (720, "Would another bottle fit a real need?", "Review current options only if you have a use for them.",
             "Hello,\n\nIf you are considering a gift or a second bottle for a different routine, you can review the current range on the website. Check product details and delivery information before ordering.\n\nThere is no need to buy again to take part in this email programme. This is the final message in our post-purchase series; use the preference links below to choose what you hear from us next.\n\nOcean Bottle team",
             "Explore the current bottle range", "/collections/water-bottles", "repeat_purchase"),
        ]),
    ]
    result = []
    for key, name, event, entry, expiry, steps in specifications:
        messages = []
        for index, (delay, subject, preview, body, cta, url, conversion) in enumerate(steps):
            messages.append({
                "id": f"{key}-{index + 1}", "trigger": event,
                "entry_criteria": entry + " Recheck eligibility immediately before sending.",
                "delay_hours_from_entry": delay, "subject": subject, "preview_text": preview,
                "body": body + "\n\n[Email preferences] | [Unsubscribe]\nProposed draft: links and factual product instructions need approval before activation.",
                "cta": cta, "cta_path": url, "conversion_event": conversion,
                "exit_condition": "Purchase ends pre-purchase flows; repeat purchase ends post-purchase flow. All flows exit on suppression, expiry or final-message completion.",
                "consent_handling": POLICY["suppression"], "suppression_handling": POLICY["cap_rule"],
            })
        result.append({"id": key, "name": name, "entry_event": event, "entry": entry,
                       "expires_after_hours": expiry, "messages": messages})
    return result


@dataclass
class State:
    """Synthetic per-contact state; never persisted or connected to email."""
    consent: bool = True
    suppressed: bool = False
    purchased: bool = False
    support_open: bool = False
    active: str | None = None
    entered_at: float = 0
    next_step: int = 0
    sent_at: list[float] = field(default_factory=list)
    finished: set[str] = field(default_factory=set)


def finish(state, reason):
    if state.active:
        state.finished.add(state.active)
    state.active = None
    state.next_step = 0
    return reason


def transition(state, event, now):
    """Process one synthetic event and return a decision, never send email."""
    flows = {flow["id"]: flow for flow in workflows()}
    if event in {"unsubscribe", "consent_withdrawal", "hard_bounce", "complaint", "suppression"}:
        state.consent = False
        state.suppressed = True
        return finish(state, "suppressed")
    if event == "support_open":
        state.support_open = True
        return "paused_support"
    if event == "support_resolved":
        state.support_open = False
        return "support_resolved"
    if event == "cart_activity" and state.active == "cart":
        return finish(state, "cart_resumed_exit")
    if event == "purchase":
        state.purchased = True
        return finish(state, "purchase_exit")
    if not state.consent or state.suppressed:
        return finish(state, "suppressed")
    if event == "inactivity":
        if state.active is None:
            return "no_action"
        if now - state.entered_at < flows[state.active]["expires_after_hours"]:
            return "waiting_inactivity_deadline"
        return finish(state, "inactivity_exit")
    requested = next((key for key, flow in flows.items() if flow["entry_event"] == event), None)
    if requested:
        if requested == "post_purchase" and (not state.purchased or state.support_open):
            return "ineligible"
        if requested != "post_purchase" and state.purchased:
            return "ineligible"
        if requested in state.finished or state.active == requested:
            return "duplicate_blocked"
        if state.active:
            if POLICY["priority"].index(requested) >= POLICY["priority"].index(state.active):
                return "lower_priority_blocked"
            finish(state, "replaced")
        state.active, state.entered_at, state.next_step = requested, now, 0
        return "entered"
    if event != "tick" or state.active is None:
        return "no_action"
    flow = flows[state.active]
    elapsed = now - state.entered_at
    if elapsed >= flow["expires_after_hours"]:
        return finish(state, "expired")
    if state.support_open:
        return "paused_support"
    message = flow["messages"][state.next_step]
    if elapsed < message["delay_hours_from_entry"]:
        return "waiting"
    recent = [time for time in state.sent_at if now - time < 168]
    if (recent and now - max(recent) < POLICY["minimum_gap_hours"]) or len(recent) >= POLICY["maximum_messages_rolling_7_days"]:
        return "deferred_frequency_cap"
    state.sent_at.append(now)
    state.next_step += 1
    if state.next_step == len(flow["messages"]):
        finish(state, "completed")
    return "eligible_draft:" + message["id"]
