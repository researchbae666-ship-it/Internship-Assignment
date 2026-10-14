"""Calculate only source-supported, same-platform, fixed-window measures."""

from datetime import datetime, timezone

WINDOW = {"start_utc": "2026-09-15T00:00:00+00:00", "end_utc": "2026-10-12T23:59:59+00:00", "days": 28}


def timestamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("An explicit timezone is required")
    return result.astimezone(timezone.utc)


def valid_count(value):
    return type(value) is int and value >= 0


def calculate(data):
    if data["observation_window"] != WINDOW:
        raise ValueError("Use the approved common 28-day window")
    start, end = timestamp(WINDOW["start_utc"]), timestamp(WINDOW["end_utc"])
    included = []
    seen = set()
    for post in data["posts"]:
        key = (post["brand"], post["platform"], post["post_url"])
        if key in seen:
            raise ValueError("Duplicate public post")
        seen.add(key)
        if not post.get("evidence_reference") or not post.get("official_account_verified"):
            raise ValueError("Posts require evidence and a verified official account")
        published = timestamp(post["published_utc"])
        if timestamp(post["collected_utc"]) < published:
            raise ValueError("Collection cannot predate publication")
        if start <= published <= end:
            included.append(post)
    measures = []
    for account in data["accounts"]:
        posts = [post for post in included if post["brand"] == account["brand"] and post["platform"] == account["platform"]]
        complete = account.get("window_inventory_complete") is True
        weekly = len(posts) / WINDOW["days"] * 7 if complete or posts else None
        rates = []
        for post in posts:
            if account["platform"] == "YouTube":
                continue  # No follower-based comparison with a view denominator.
            numerator_fields = ("visible_likes", "visible_comments") if account["platform"] == "Instagram" else ("visible_reactions", "visible_comments")
            values = [post.get(field) for field in numerator_fields]
            followers = post.get("visible_followers")
            rate = None
            if all(valid_count(value) for value in values) and valid_count(followers) and followers > 0 and post.get("follower_count_precision") == "exact":
                rate = sum(values) / followers * 100
            rates.append({"post_url": post["post_url"], "proxy_percent": rate, "definition": "+".join(numerator_fields) + " / exact visible followers × 100", "limitation": "Visible interaction proxy, not first-party engagement analytics; collection-time follower denominator."})
        measures.append({"brand": account["brand"], "platform": account["platform"], "verified_posts_in_window": len(posts), "inventory_complete": complete,
                         "weekly_activity": weekly, "cadence_classification": "complete inventory frequency" if complete else "observed minimum activity" if posts else "unavailable; no verifiable dated post sample",
                         "visible_interaction_proxies": rates, "engagement_available": any(rate["proxy_percent"] is not None for rate in rates)})
    return {"observation_window": WINDOW, "measurements": measures, "has_dated_post_evidence": bool(included)}
