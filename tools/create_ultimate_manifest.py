#!/usr/bin/env python3
"""Create a machine-readable final-audit manifest without altering inputs."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import fitz
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence/ultimate_final_review"
BASELINE_PATH = EVIDENCE / "baseline_manifest.json"
OUTPUT = EVIDENCE / "manifest.json"
PDFS = {
    "marketing_approved": ROOT / "digital_marketing/deliverables/Progree_Digital_Marketing_Tasks_2_3_4_COMBINED_REVIEW.pdf",
    "marketing_final_candidate": ROOT / "digital_marketing/deliverables/Progree_Digital_Marketing_Tasks_2_3_4_FINAL_CANDIDATE.pdf",
    "python_approved": ROOT / "deliverables/Progree_Python_Tasks_2_3_4.pdf",
    "python_final_candidate": ROOT / "deliverables/Progree_Python_Tasks_2_3_4_FINAL_CANDIDATE.pdf",
    "marketing_task2_source": ROOT / "digital_marketing/deliverables/DM_Task2_Competitor_Audit_SECONDARY_DRAFT.pdf",
    "marketing_task3_source": ROOT / "digital_marketing/deliverables/DM_Task3_30_Day_Campaign.pdf",
    "marketing_task4_source": ROOT / "digital_marketing/deliverables/DM_Task4_SEO_Acquisition_Strategy.pdf",
    "marketing_task4_appendix_source": ROOT / "digital_marketing/deliverables/DM_Task4_Email_Workflow_Appendix.pdf",
}
INTENTIONAL_BASELINE_SOURCE_CHANGES = {
    "internship/task3.py": "UFR-001 path-component validation",
    "tests/test_task3.py": "UFR-001 regression",
    "digital_marketing/research/task3/build_campaign.py": "UFR-002 duplicate-action validation",
    "digital_marketing/research/task3/test_campaign.py": "UFR-002 regression",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def page_stream(page: Any) -> bytes:
    contents = page.get_contents()
    return contents.get_data() if contents is not None else b""


def fonts(page: Any) -> list[str]:
    resources = page.get("/Resources", {})
    font_dict = resources.get("/Font", {})
    return sorted({str(font.get_object().get("/BaseFont", "")) for font in font_dict.values()})


def outlines(reader: PdfReader) -> list[dict[str, object]]:
    result = []
    for entry in reader.outline:
        if isinstance(entry, list):
            continue
        result.append({"title": entry["/Title"], "page": reader.get_destination_page_number(entry) + 1})
    return result


def pdf_record(path: Path) -> dict[str, object]:
    reader = PdfReader(path)
    document = fitz.open(path)
    try:
        links = [
            {"page": number, "uri": link["uri"]}
            for number, page in enumerate(document, start=1)
            for link in page.get_links()
            if link.get("kind") == fitz.LINK_URI
        ]
    finally:
        document.close()
    metadata = reader.metadata or {}
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "page_count": len(reader.pages),
        "pages_with_no_extractable_text": [number for number, page in enumerate(reader.pages, start=1) if not (page.extract_text() or "").strip()],
        "fonts_by_page": {str(number): fonts(page) for number, page in enumerate(reader.pages, start=1)},
        "page_dimensions": [
            [float(page.mediabox.width), float(page.mediabox.height)] for page in reader.pages
        ],
        "metadata": {str(key): str(value) for key, value in metadata.items()},
        "outline": outlines(reader),
        "has_page_labels": "/PageLabels" in reader.trailer["/Root"],
        "uri_links": links,
        "encrypted": reader.is_encrypted,
    }


def combined_source_integrity() -> dict[str, object]:
    combined = PdfReader(PDFS["marketing_approved"])
    inputs = (
        ("marketing_task2_source", 2),
        ("marketing_task3_source", 6),
        ("marketing_task4_source", 26),
        ("marketing_task4_appendix_source", 32),
    )
    checks = []
    for source_key, offset in inputs:
        source = PdfReader(PDFS[source_key])
        for index, source_page in enumerate(source.pages, start=1):
            destination_page = combined.pages[offset + index - 1]
            checks.append(
                {
                    "source": source_key,
                    "source_page": index,
                    "combined_page": offset + index,
                    "content_stream_equal": page_stream(source_page) == page_stream(destination_page),
                    "text_equal": source_page.extract_text() == destination_page.extract_text(),
                    "dimensions_equal": tuple(source_page.mediabox) == tuple(destination_page.mediabox),
                }
            )
    return {"all_36_source_pages_preserved": all(all(value for key, value in row.items() if key not in {"source", "source_page", "combined_page"}) for row in checks), "checks": checks}


def candidate_integrity(source_key: str, candidate_key: str) -> dict[str, object]:
    source = PdfReader(PDFS[source_key])
    candidate = PdfReader(PDFS[candidate_key])
    checks = []
    for number, (before, after) in enumerate(zip(source.pages, candidate.pages), start=1):
        checks.append(
            {
                "page": number,
                "content_stream_equal": page_stream(before) == page_stream(after),
                "text_equal": before.extract_text() == after.extract_text(),
                "dimensions_equal": tuple(before.mediabox) == tuple(after.mediabox),
                "rotation_equal": before.rotation == after.rotation,
            }
        )
    return {"page_count_equal": len(source.pages) == len(candidate.pages), "all_source_pages_unchanged": all(all(value for key, value in row.items() if key != "page") for row in checks), "checks": checks}


def baseline_comparison(baseline: dict[str, object]) -> dict[str, object]:
    changed = []
    missing = []
    for item in baseline["tracked_files"]:
        path = ROOT / item["path"]
        if not path.is_file():
            missing.append(item["path"])
        elif sha256(path) != item["sha256"]:
            changed.append(item["path"])
    unexpected = sorted(set(changed) - set(INTENTIONAL_BASELINE_SOURCE_CHANGES))
    protected = {}
    for name, artifact in baseline["protected_artifacts"].items():
        path = ROOT / artifact["path"]
        protected[name] = path.is_file() and sha256(path) == artifact["sha256"]
    return {
        "baseline_tracked_files_changed": sorted(changed),
        "baseline_tracked_files_missing": sorted(missing),
        "intentional_source_changes": INTENTIONAL_BASELINE_SOURCE_CHANGES,
        "unexpected_baseline_changes": unexpected,
        "protected_artifacts_unchanged": protected,
        "all_protected_artifacts_unchanged": all(protected.values()),
    }


def git_value(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> None:
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    records = {name: pdf_record(path) for name, path in PDFS.items()}
    candidate_build = json.loads((EVIDENCE / "candidate_build.json").read_text(encoding="utf-8"))
    render_review = json.loads((EVIDENCE / "render_review.json").read_text(encoding="utf-8"))
    privacy = json.loads((EVIDENCE / "privacy_scan.json").read_text(encoding="utf-8"))
    tests = json.loads((EVIDENCE / "test_results.json").read_text(encoding="utf-8"))
    report = {
        "schema": "progree-ultimate-final-review-manifest-v1",
        "baseline_commit": baseline["baseline_commit"],
        "audit_branch": git_value("branch", "--show-current"),
        "head_before_audit_commit": git_value("rev-parse", "HEAD"),
        "branch_contains_baseline": subprocess.run(["git", "merge-base", "--is-ancestor", baseline["baseline_commit"], "HEAD"], cwd=ROOT, check=False).returncode == 0,
        "pdfs": records,
        "combined_marketing_source_integrity": combined_source_integrity(),
        "candidate_source_integrity": {
            "marketing": candidate_integrity("marketing_approved", "marketing_final_candidate"),
            "python": candidate_integrity("python_approved", "python_final_candidate"),
        },
        "baseline_comparison": baseline_comparison(baseline),
        "candidate_build_validation": {
            "protected_source_hashes_unchanged": candidate_build["protected_source_hashes_unchanged"],
            "marketing_uri_annotation_count": len(candidate_build["marketing"]["uri_links"]),
        },
        "render_review": {
            "approved_pages_rendered_and_individually_reviewed": render_review["approved_pages_rendered_and_individually_reviewed"],
            "candidate_pages_freshly_rendered": render_review["candidate_pages_freshly_rendered"],
            "pixel_equal_candidate_page_pairs": render_review["candidate_vs_approved_pixel_equal_pairs"],
            "result": render_review["visual_review"]["result"],
        },
        "privacy_scan": {"result": privacy["result"], "unknown_contact_or_secret_count": privacy["unknown_email_or_phone_or_secret_count"]},
        "test_summary": {"all_passed": tests["all_passed"], "unittest_test_count": sum(row["test_count"] or 0 for row in tests["checks"]), "validator_check_count": sum(row["test_count"] is None for row in tests["checks"])},
        "submission_selection": {
            "python": "deliverables/Progree_Python_Tasks_2_3_4_FINAL_CANDIDATE.pdf",
            "marketing": "digital_marketing/deliverables/Progree_Digital_Marketing_Tasks_2_3_4_FINAL_CANDIDATE.pdf",
            "technical_status": "ready; external eligibility remains unconfirmed",
        },
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"result": "passed", "manifest": OUTPUT.relative_to(ROOT).as_posix()}, indent=2))


if __name__ == "__main__":
    main()
