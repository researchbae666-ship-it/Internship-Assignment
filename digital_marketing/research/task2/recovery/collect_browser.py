"""Capture public browser text with no logins, scrolling, or gate bypass."""

import asyncio
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT / "artifacts/digital_marketing/task2_recovery"
DEST = ROOT / "digital_marketing/evidence/task2/recovery"


async def collect():
    sources = json.loads((DEST / "source_records.json").read_text())
    targets = [record for record in sources if record["id"] in {"stanley", "hydro", "owala", "stanley-instagram", "hydro-instagram", "owala-instagram"}]
    records = []
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(executable_path="/usr/bin/chromium", headless=True, args=["--no-sandbox"])
        for target in targets:
            record = {"id": target["id"] + "-browser", "url": target["url"], "collected_utc": datetime.now(timezone.utc).isoformat(), "method": "normal unauthenticated Chromium public page; no login, gate bypass or hidden API"}
            page = await browser.new_page(viewport={"width": 1280, "height": 900})
            try:
                response = await page.goto(record["url"], wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2500)
                text = await page.locator("body").inner_text(timeout=10000)
                links = await page.locator("a[href]").evaluate_all("els => els.map(x => ({url:x.href,text:x.innerText}))")
                screenshot = RAW / (record["id"] + ".png")
                await page.screenshot(path=str(screenshot), full_page=False)
                record.update(http_status=response.status if response else None, final_url=page.url, title=await page.title(), public_text=text, links=links, screenshot_raw_path=str(screenshot.relative_to(ROOT)), screenshot_sha256=hashlib.sha256(screenshot.read_bytes()).hexdigest())
            except Exception as error:
                record["error"] = str(error).replace(str(ROOT), "<repository>")
            records.append(record)
            print(record["id"], record.get("http_status"), record.get("error", ""), flush=True)
            await page.close()
        await browser.close()
    (DEST / "browser_records.json").write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    RAW.mkdir(parents=True, exist_ok=True)
    DEST.mkdir(parents=True, exist_ok=True)
    asyncio.run(collect())
