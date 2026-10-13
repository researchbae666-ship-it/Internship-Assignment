"""Calculate Task 2 cadence and visible-interaction proxies from retained data."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def calculate(dataset: dict[str, Any]) -> dict[str, Any]:
    """Return only calculations supported by complete retained inputs."""
    days = dataset["observation_window"]["days"]
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for post in dataset.get("posts", []):
        grouped[(post["brand"], post["platform"])].append(post)

    cadence = [
        {
            "brand": brand,
            "platform": platform,
            "included_posts": len(posts),
            "observation_days": days,
            "posts_per_week": len(posts) / days * 7,
        }
        for (brand, platform), posts in sorted(grouped.items())
    ]
    engagement: list[dict[str, Any]] = []
    for post in dataset.get("posts", []):
        likes = post.get("visible_likes")
        comments = post.get("visible_comments")
        followers = post.get("visible_followers")
        if all(isinstance(value, int) and value >= 0 for value in (likes, comments, followers)) and followers:
            engagement.append(
                {
                    "post_url": post["post_url"],
                    "visible_interaction_proxy_percent": (likes + comments) / followers * 100,
                    "numerator": likes + comments,
                    "denominator_visible_followers": followers,
                }
            )
    return {
        "observation_window": dataset["observation_window"],
        "cadence": cadence,
        "visible_interaction_proxy": engagement,
        "unavailable_reason": (
            None
            if cadence or engagement
            else "No verified post observations were available in the retained dataset."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with args.dataset.open(encoding="utf-8") as handle:
        result = calculate(json.load(handle))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
