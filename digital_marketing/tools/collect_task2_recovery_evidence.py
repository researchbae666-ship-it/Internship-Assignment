"""Execute recovery checks while preserving the original blocked records."""

import hashlib
import json
import platform
import re
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = "3fd0c7d4e84acb566395185064fea2eac1732b71"
EVIDENCE = ROOT / "digital_marketing/evidence/task2/recovery"
RAW = ROOT / "artifacts/digital_marketing/task2_recovery"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    outputs = EVIDENCE / "outputs"
    outputs.mkdir(exist_ok=True)
    tracked = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", BASELINE], cwd=ROOT, text=True).splitlines()
    prefixes = ("internship/", "tests/", "evidence/", "deliverables/", "fixtures/", "tools/", "digital_marketing/research/task2/", "digital_marketing/evidence/task2/", "digital_marketing/research/task3/", "digital_marketing/evidence/task3/", "digital_marketing/research/task4/", "digital_marketing/evidence/task4/", "digital_marketing/deliverables/")
    protected = [path for path in tracked if path.startswith(prefixes) or path.endswith("Tasks & Instructions.pdf") or path in ("Digital Marketing & Branding Tasks & Instructions.md", "Text Message 1.md", "Text Message 2.md")]
    for name in protected:
        original = subprocess.check_output(["git", "show", f"{BASELINE}:{name}"], cwd=ROOT)
        if not (ROOT / name).exists() or (ROOT / name).read_bytes() != original:
            raise RuntimeError("Protected baseline file changed: " + name)
    records = []
    commands = [
        ("build", [sys.executable, "digital_marketing/research/task2/recovery/build_audit.py"]),
        ("recovery-tests", [sys.executable, "-m", "unittest", "discover", "-s", "digital_marketing/research/task2/recovery", "-v"]),
        ("report-tests", [sys.executable, "digital_marketing/tools/test_task2_recovery_report.py"]),
        ("generate", [sys.executable, "digital_marketing/tools/generate_task2_recovery_report.py"]),
    ]
    for name, command in commands:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        text = (result.stdout + result.stderr).replace(str(ROOT), "<repository>")
        path = outputs / (name + ".txt")
        path.write_text(text, encoding="utf-8")
        record = {"command": shlex.join(command), "executed_utc": datetime.now(timezone.utc).isoformat(), "exit_code": result.returncode, "output": str(path.relative_to(ROOT)), "sha256": digest(path)}
        match = re.search(r"Ran (\d+) tests?", text)
        if match:
            record["tests_run"] = int(match.group(1))
            record["outcome"] = "passed" if not result.returncode else "failed"
        records.append(record)
        if result.returncode:
            raise RuntimeError("Failed: " + name)
    pdf = ROOT / "digital_marketing/deliverables/DM_Task2_Competitor_Audit_RECOVERY_DRAFT.pdf"
    metadata = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    (outputs / "pdfinfo.txt").write_text("\n".join(line.rstrip() for line in metadata.splitlines()) + "\n")
    subprocess.run(["pdftotext", str(pdf), str(outputs / "pdf-text.txt")], check=True)
    render = RAW / "report_render"
    render.mkdir(exist_ok=True)
    result = subprocess.run(["pdftoppm", "-png", "-r", "144", str(pdf), str(render / "page")], capture_output=True, text=True)
    (RAW / "render-output.txt").write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError("Rendering failed")
    pages = int(re.search(r"Pages:\s+(\d+)", metadata).group(1))
    if pages != 4 or len(list(render.glob("page-*.png"))) != pages:
        raise RuntimeError("Unexpected PDF / render page count")
    sources = json.loads((EVIDENCE / "source_records.json").read_text())
    browsers = json.loads((EVIDENCE / "browser_records.json").read_text())
    for source in sources:
        raw = RAW / (source["id"] + ".html")
        if source["sha256_raw"] and (not raw.exists() or digest(raw) != source["sha256_raw"]):
            raise RuntimeError("Raw source digest mismatch")
    for browser in browsers:
        if digest(ROOT / browser["screenshot_raw_path"]) != browser["screenshot_sha256"]:
            raise RuntimeError("Screenshot digest mismatch")
    manifest = {
        "status": "partial evidence-backed draft; period metrics blocked",
        "execution_source_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "baseline": BASELINE, "generated_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "protected_original_files_compared": len(protected), "protected_originals_result": "byte-for-byte unchanged",
        "source_coverage": {"direct_requests": len(sources), "usable_website_pages": 3, "partial_instagram_profiles": 3, "verified_social_links": 5, "browser_captures": len(browsers), "dated_posts_recovered": 0, "period_metrics": "unavailable; JSON null, never substituted zero"},
        "source_records": "digital_marketing/evidence/task2/recovery/source_records.json", "browser_records": "digital_marketing/evidence/task2/recovery/browser_records.json",
        "commands": records, "pdf": {"path": str(pdf.relative_to(ROOT)), "pages": pages, "bytes": pdf.stat().st_size, "sha256": digest(pdf), "pages_rendered": pages, "render_exit_code": result.returncode},
        "visual_qa": "pending manual inspection; see QA.md after reviewing all rendered pages",
        "retained_digests": {str(path.relative_to(ROOT)): digest(path) for path in sorted(outputs.glob("*"))},
    }
    for path in (EVIDENCE / "source_records.json", EVIDENCE / "browser_records.json", EVIDENCE / "metrics.json", ROOT / "digital_marketing/research/task2/recovery/observations.json"):
        manifest["retained_digests"][str(path.relative_to(ROOT))] = digest(path)
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"tests": [(row.get("tests_run"), row.get("outcome")) for row in records if "tests_run" in row], "pdf": manifest["pdf"], "protected_files": len(protected)}, indent=2))


if __name__ == "__main__":
    main()
