#!/usr/bin/env python3
"""Record a conservative, value-redacted privacy and secret scan of tracked files."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "evidence/ultimate_final_review/privacy_scan.json"
EMAIL = re.compile(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# Require a country prefix or an explicit area-code parenthesis.  A broad
# digit-and-dash expression would turn report dates, scenario ranges and
# public metric values into false phone-number findings.
PHONE = re.compile(r"(?<!\w)(?:\+\d[\d .()-]{6,}\d|\(\d{2,4}\)[ .-]?\d{3,4}[ .-]?\d{3,4})(?!\w)")
SECRET = re.compile(r"(?i)\b(?:api[_-]?key|secret|access[_-]?token|private[_-]?key|password)\b\s*[:=]\s*[^\s]{8,}")
IDENTITY = re.compile(r"(?i)\b(?:student\s*(?:id|identifier)|offer\s+letter|signature|passport|registration\s*(?:id|number))\b")


def tracked_files() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True)
    return [ROOT / item for item in output.splitlines() if item]


def untracked_files() -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, text=True
    )
    return [ROOT / item for item in output.splitlines() if item]


def audit_files() -> list[Path]:
    files = set(tracked_files())
    files.update(untracked_files())
    files.update(
        path
        for path in (
            ROOT / "digital_marketing/deliverables/Progree_Digital_Marketing_Tasks_2_3_4_FINAL_CANDIDATE.pdf",
            ROOT / "deliverables/Progree_Python_Tasks_2_3_4_FINAL_CANDIDATE.pdf",
        )
        if path.is_file()
    )
    return sorted(files)


def text_for(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return ""


def add_category(rows: list[dict[str, object]], category: str, path: Path, match_count: int, classification: str) -> None:
    if match_count:
        rows.append({"category": category, "path": path.relative_to(ROOT).as_posix(), "match_count": match_count, "classification": classification})


def main() -> int:
    findings: list[dict[str, object]] = []
    pdf_metadata: list[dict[str, object]] = []
    suspicious_filenames: list[str] = []
    files = audit_files()
    for path in files:
        lower_name = path.name.casefold()
        if any(marker in lower_name for marker in ("offer", "credential", "passport", "signature", ".env")):
            suspicious_filenames.append(path.relative_to(ROOT).as_posix())
        text = text_for(path)
        emails = EMAIL.findall(text)
        synthetic = sum(value.casefold().endswith("example.test") for value in emails)
        add_category(findings, "email", path, synthetic, "allowed synthetic test fixture")
        add_category(findings, "email", path, len(emails) - synthetic, "requires review")
        add_category(findings, "phone", path, len(PHONE.findall(text)), "requires review")
        secret_classification = (
            "scanner expression; no value recorded"
            if path.resolve() == Path(__file__).resolve()
            else "requires review"
        )
        add_category(findings, "secret_assignment", path, len(SECRET.findall(text)), secret_classification)
        add_category(findings, "identity_reference", path, len(IDENTITY.findall(text)), "policy/reference wording; no value recorded")
        if path.suffix.lower() == ".pdf":
            reader = PdfReader(path)
            metadata = reader.metadata or {}
            pdf_metadata.append(
                {
                    "path": path.relative_to(ROOT).as_posix(),
                    "author": str(metadata.get("/Author", "")),
                    "creator": str(metadata.get("/Creator", "")),
                    "title": str(metadata.get("/Title", "")),
                    "has_javascript": "/JavaScript" in reader.trailer["/Root"],
                    "encrypted": reader.is_encrypted,
                }
            )
    requires_review = [item for item in findings if item["classification"] == "requires review"]
    report = {
        "schema": "progree-ultimate-privacy-scan-v1",
        "tracked_file_count": len(tracked_files()),
        "additional_untracked_files_scanned": len(untracked_files()),
        "findings": findings,
        "suspicious_filenames": suspicious_filenames,
        "pdf_metadata": pdf_metadata,
        "unknown_email_or_phone_or_secret_count": len(requires_review),
        "result": "pass" if not requires_review and not suspicious_filenames else "review_required",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
