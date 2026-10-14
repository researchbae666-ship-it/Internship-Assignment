"""Collect normal public responses without authentication or bypasses.

Raw HTML stays ignored because pages contain scripts and transient tokens.
Retained extracts include public metadata, headings, source-linked text and
social links only. A 200 response alone never establishes usable post evidence.
"""

import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT / "artifacts/digital_marketing/task2_recovery"
DEST = ROOT / "digital_marketing/evidence/task2/recovery"
WEBSITES = {
    "stanley": ("Stanley 1913", "https://www.stanley1913.com/"),
    "hydro": ("Hydro Flask", "https://www.hydroflask.com/"),
    "owala": ("Owala", "https://owalalife.com/"),
}


class PublicHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.text = []
        self.links = []
        self.headings = []
        self.metadata = []
        self.images = []
        self.current = None
        self.buffer = []

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if tag in ("script", "style"):
            self.skip += 1
        if tag == "a" and attributes.get("href"):
            self.links.append(attributes["href"])
        if tag == "meta" and (attributes.get("name") == "description" or attributes.get("property") in ("og:title", "og:description", "og:url")):
            self.metadata.append({"name": attributes.get("name") or attributes.get("property"), "content": attributes.get("content")})
        if tag in ("title", "h1", "h2", "h3"):
            self.current, self.buffer = tag, []
        if tag == "img" and attributes.get("alt"):
            self.images.append({"alt": attributes["alt"], "src": attributes.get("src")})

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        if tag == self.current:
            self.headings.append({"tag": tag, "text": " ".join(" ".join(self.buffer).split())})
            self.current = None

    def handle_data(self, text):
        if not self.skip:
            self.text.append(text)
            if self.current:
                self.buffer.append(text)


def extract(text):
    parser = PublicHTML()
    parser.feed(text)
    return {
        "metadata": parser.metadata, "headings": parser.headings,
        "public_text": " ".join(" ".join(parser.text).split()),
        "social_links": sorted({url for url in parser.links if re.search(r"https://(?:www\.)?(?:instagram.com|youtube.com|facebook.com|tiktok.com|linkedin.com)/", url)}),
        "public_post_links": sorted({url for url in parser.links if re.search(r"instagram.com/(p|reel)/|youtube.com/watch|youtu.be/", url)}),
        "image_alt_records": [image for image in parser.images if not (image.get("src") or "").startswith("data:")],
    }


def collect(identity, url, verification):
    start = datetime.now(timezone.utc).isoformat()
    path = RAW / (identity + ".html")
    result = subprocess.run(["curl", "--location", "--silent", "--show-error", "--connect-timeout", "15", "--max-time", "30", "--output", str(path), "--write-out", "%{http_code}\n%{url_effective}", url], capture_output=True, text=True)
    status, _, final_url = result.stdout.partition("\n")
    record = {
        "id": identity, "url": url, "collected_utc": start,
        "http_status": int(status) if status and status != "000" else None,
        "curl_http_code": status,
        "final_url": final_url, "transport_exit_code": result.returncode,
        "transport_error": result.stderr.strip(), "account_verification": verification,
        "sha256_raw": hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None,
        "raw_bytes": path.stat().st_size if path.exists() else 0,
        "method": "unauthenticated normal public GET",
    }
    if result.returncode == 0 and status == "200":
        record["extract"] = extract(path.read_text(encoding="utf-8"))
    return record


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    DEST.mkdir(parents=True, exist_ok=True)
    records = []
    for key, (_, url) in WEBSITES.items():
        records.append(collect(key, url, "user-approved official website; identity corroborated by branded page and outgoing official accounts"))
    targets = []
    for record in records:
        key = record["id"]
        for platform in ("instagram", "youtube"):
            links = [url for url in record.get("extract", {}).get("social_links", []) if platform + ".com/" in url]
            if links:
                targets.append((key + "-" + platform, links[0], "verified by outgoing link on " + record["url"]))
    candidates = [
        ("owala-youtube", "https://www.youtube.com/@owala", "unverified candidate; not an official-account finding"),
        ("stanley-linkedin", "https://www.linkedin.com/company/stanley1913/", "unverified candidate; not an official-account finding"),
        ("hydro-linkedin", "https://www.linkedin.com/company/hydro-flask/", "unverified candidate; not an official-account finding"),
        ("owala-linkedin", "https://www.linkedin.com/company/owala/", "unverified candidate; not an official-account finding"),
    ]
    for target in targets + candidates:
        records.append(collect(*target))
    (DEST / "source_records.json").write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for record in records:
        print(record["id"], record["http_status"], record["transport_exit_code"], record["account_verification"])


if __name__ == "__main__":
    main()
