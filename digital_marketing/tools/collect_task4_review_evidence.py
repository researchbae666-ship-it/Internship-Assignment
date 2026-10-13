"""Execute Task 4 review checks and retain actual sanitized evidence."""

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
BASELINE = "f11bb3deabb53e4aa9be2e9dded2a4b4b04d941c"
EVIDENCE = ROOT / "digital_marketing/evidence/task4"
RAW = ROOT / "artifacts/digital_marketing/task4_review"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    output = EVIDENCE / "review_outputs"
    output.mkdir(parents=True, exist_ok=True)
    historical = EVIDENCE / "historical"
    historical.mkdir(parents=True, exist_ok=True)
    original_manifest = subprocess.check_output(["git", "show", f"{BASELINE}:digital_marketing/evidence/task4/manifest.json"], cwd=ROOT)
    (historical / "reviewed-manifest.json").write_bytes(original_manifest)
    (historical / "reviewed-QA.md").write_bytes(subprocess.check_output(["git", "show", f"{BASELINE}:digital_marketing/evidence/task4/QA.md"], cwd=ROOT))
    commands = [
        ("build", [sys.executable, "digital_marketing/research/task4/build_strategy.py"]),
        ("task4-tests", [sys.executable, "-m", "unittest", "discover", "-s", "digital_marketing/research/task4", "-v"]),
        ("pdf-tests", [sys.executable, "digital_marketing/tools/test_generate_task4_report.py"]),
        ("python-tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
        ("generate", [sys.executable, "digital_marketing/tools/generate_task4_report.py"]),
        ("preservation", ["git", "diff", "--exit-code", BASELINE, "--", "internship", "tests", "evidence", "deliverables", "tools", "fixtures", "digital_marketing/research/task3", "digital_marketing/evidence/task3", "digital_marketing/research/task2", "digital_marketing/evidence/task2", "digital_marketing/deliverables/DM_Task3_30_Day_Campaign.pdf"]),
    ]
    records = []
    for name, command in commands:
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        text = (result.stdout + result.stderr).replace(str(ROOT), "<repository>")
        path = output / (name + ".txt")
        path.write_text(text, encoding="utf-8")
        record = {"command": shlex.join(command), "executed_utc": datetime.now(timezone.utc).isoformat(), "exit_code": result.returncode, "output": str(path.relative_to(ROOT)), "sha256": digest(path)}
        match = re.search(r"Ran (\d+) tests?", text)
        if match:
            record["tests_run"] = int(match.group(1))
            record["outcome"] = "passed" if result.returncode == 0 else "failed"
        records.append(record)
        if result.returncode:
            raise RuntimeError(f"{name} failed; inspect {path}")
    pdfs = []
    for name in ("DM_Task4_SEO_Acquisition_Strategy", "DM_Task4_Email_Workflow_Appendix"):
        path = ROOT / "digital_marketing/deliverables" / (name + ".pdf")
        metadata = subprocess.check_output(["pdfinfo", str(path)], text=True)
        (output / (name + "-pdfinfo.txt")).write_text(metadata, encoding="utf-8")
        text_path = output / (name + "-text.txt")
        subprocess.run(["pdftotext", str(path), str(text_path)], check=True)
        rendered = RAW / name
        rendered.mkdir(exist_ok=True)
        rendering = subprocess.run(["pdftoppm", "-png", "-r", "144", str(path), str(rendered / "page")], capture_output=True, text=True)
        (RAW / (name + "-render.txt")).write_text(rendering.stdout + rendering.stderr)
        if rendering.returncode:
            raise RuntimeError("PDF rendering failed")
        pages = int(re.search(r"Pages:\s+(\d+)", metadata).group(1))
        if len(list(rendered.glob("page-*.png"))) != pages:
            raise RuntimeError("Rendered page count mismatch")
        pdfs.append({"path": str(path.relative_to(ROOT)), "pages": pages, "bytes": path.stat().st_size, "sha256": digest(path), "pages_rendered": pages, "renderer_exit_code": rendering.returncode})
    data_path = ROOT / "digital_marketing/research/task4/strategy_data.json"
    data = json.loads(data_path.read_text())
    original = json.loads(subprocess.check_output(["git", "show", f"{BASELINE}:digital_marketing/research/task4/strategy_data.json"], cwd=ROOT))
    for field in ("keyword_map", "seo_map", "funnel", "budget", "observations"):
        if data[field] != original[field]:
            raise RuntimeError(f"Accepted {field} changed")
    for old, new in zip(original["scenarios"], data["scenarios"]):
        if any(new[key] != value for key, value in old.items()):
            raise RuntimeError("Accepted media-based scenario changed")
    manifest = {
        "kind": "task4-targeted-review-evidence", "execution_source_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "reviewed_baseline": BASELINE, "generated_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "historical_source_manifest": "digital_marketing/evidence/task4/historical/reviewed-manifest.json",
        "reviewer_sources": data["reviewer_sources"], "commands": records, "pdfs": pdfs,
        "strategy_data_sha256": digest(data_path), "email_workflows": len(data["emails"]),
        "email_messages": sum(len(flow["messages"]) for flow in data["emails"]),
        "financial_scenarios": data["scenarios"], "accepted_data_preservation": "passed",
        "visual_inspection": "pending; see QA.md after manual rendered-page inspection",
    }
    manifest["retained_output_digests"] = {str(path.relative_to(ROOT)): digest(path) for path in sorted(output.glob("*"))}
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"tests": [(record.get("tests_run"), record.get("outcome")) for record in records if "tests_run" in record], "pdfs": pdfs}, indent=2))


if __name__ == "__main__":
    main()
