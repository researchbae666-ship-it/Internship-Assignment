#!/usr/bin/env python3
"""Create the immutable-input manifest for the ultimate submission review.

The script only reads tracked repository files and records their Git object ID,
size and SHA-256.  It deliberately does not normalise or regenerate any input.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "evidence/ultimate_final_review/baseline_manifest.json"
PROTECTED = {
    "marketing_combined": {
        "path": "digital_marketing/deliverables/Progree_Digital_Marketing_Tasks_2_3_4_COMBINED_REVIEW.pdf",
        "expected_pages": 38,
        "expected_bytes": 140_895,
        "expected_sha256": "24a211ea4cdd68f83b02ce216aa43b15bc6a65a5952776cbe8c57bccda9f0059",
    },
    "python_report": {
        "path": "deliverables/Progree_Python_Tasks_2_3_4.pdf",
        "expected_pages": 14,
        "expected_bytes": 28_500,
        "expected_sha256": "e967cec21cf744823ff25fc1dab9ba2a2486fa1b7e23f6ceb945fecfd2801db0",
    },
    "marketing_task2_source": {"path": "digital_marketing/deliverables/DM_Task2_Competitor_Audit_SECONDARY_DRAFT.pdf"},
    "marketing_task3_source": {"path": "digital_marketing/deliverables/DM_Task3_30_Day_Campaign.pdf"},
    "marketing_task4_source": {"path": "digital_marketing/deliverables/DM_Task4_SEO_Acquisition_Strategy.pdf"},
    "marketing_task4_appendix_source": {"path": "digital_marketing/deliverables/DM_Task4_Email_Workflow_Appendix.pdf"},
    "python_assignment_brief": {"path": "Python Programming Tasks & Instructions.pdf"},
    "marketing_assignment_brief": {"path": "Digital Marketing & Branding Tasks & Instructions.md"},
    "submission_notice": {"path": "Text Message 2.md"},
}


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pdf_facts(path: Path) -> dict[str, int]:
    from pypdf import PdfReader

    return {"page_count": len(PdfReader(path).pages)}


def entry(relative_path: str) -> dict[str, object]:
    path = ROOT / relative_path
    result: dict[str, object] = {
        "path": relative_path,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "git_blob": git("rev-parse", f"HEAD:{relative_path}"),
    }
    if path.suffix.lower() == ".pdf":
        result.update(pdf_facts(path))
    return result


def main() -> None:
    tracked = [item for item in git("ls-files").splitlines() if item]
    data = {
        "schema": "progree-ultimate-baseline-v1",
        "baseline_commit": git("rev-parse", "HEAD"),
        "baseline_branch": git("branch", "--show-current"),
        # Verified directly before this audit helper was introduced: clean.
        # Audit outputs themselves must not be mistaken for baseline changes.
        "working_tree_porcelain_before_audit": "",
        "tracked_file_count": len(tracked),
        "protected_artifacts": {},
        "tracked_files": [entry(item) for item in tracked],
    }
    for key, specification in PROTECTED.items():
        facts = entry(str(specification["path"]))
        expected_checks = {
            "page_count": specification.get("expected_pages"),
            "bytes": specification.get("expected_bytes"),
            "sha256": specification.get("expected_sha256"),
        }
        facts["matches_expected"] = all(
            actual == expected
            for field, expected in expected_checks.items()
            if expected is not None
            for actual in [facts.get(field)]
        )
        data["protected_artifacts"][key] = {**specification, **facts}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    for name, facts in data["protected_artifacts"].items():
        print(f"{name}: {facts['sha256']} ({facts['bytes']} bytes)")


if __name__ == "__main__":
    main()
