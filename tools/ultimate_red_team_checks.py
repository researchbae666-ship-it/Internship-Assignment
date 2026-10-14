#!/usr/bin/env python3
"""Safe adversarial checks for the final dual-track submission review.

This is intentionally an audit harness, not product code.  It uses copied
campaign/strategy data and temporary approved Task 3 workspaces.  It never
contacts an external service, modifies an approved source PDF, or writes outside
the repository's synthetic-artifact directory.
"""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

import fitz
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "digital_marketing/research/task3"))
sys.path.insert(0, str(ROOT / "digital_marketing/research/task4"))
sys.path.insert(0, str(ROOT / "digital_marketing/tools"))

from internship.task2 import fibonacci, run_benchmark  # noqa: E402
from internship.task3 import (  # noqa: E402
    PlannedMove,
    Record,
    SafetyError,
    _export_record,
    apply_plan,
    validate_workspace,
)
from build_campaign import build_campaign, validate as validate_campaign  # noqa: E402
from build_strategy import build_strategy, validate as validate_strategy  # noqa: E402
from email_workflows import State, transition  # noqa: E402
import generate_combined_review_pdf as combined  # noqa: E402


PROTECTED = (
    ROOT / "digital_marketing/deliverables/Progree_Digital_Marketing_Tasks_2_3_4_COMBINED_REVIEW.pdf",
    ROOT / "deliverables/Progree_Python_Tasks_2_3_4.pdf",
    ROOT / "digital_marketing/deliverables/DM_Task2_Competitor_Audit_SECONDARY_DRAFT.pdf",
    ROOT / "digital_marketing/deliverables/DM_Task3_30_Day_Campaign.pdf",
    ROOT / "digital_marketing/deliverables/DM_Task4_SEO_Acquisition_Strategy.pdf",
    ROOT / "digital_marketing/deliverables/DM_Task4_Email_Workflow_Appendix.pdf",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stream(page) -> bytes:
    contents = page.get_contents()
    return contents.get_data() if contents is not None else b""


def check_fibonacci() -> str:
    for invalid in (True, False, -1, 1.5, "5", None):
        try:
            fibonacci(invalid)
        except (TypeError, ValueError):
            continue
        raise AssertionError(f"Fibonacci accepted invalid value {invalid!r}")
    for invalid_call in ({"repeats": 0}, {"number": 0}, {"counts": []}):
        try:
            if "counts" in invalid_call:
                run_benchmark(invalid_call["counts"])
            else:
                run_benchmark([1], **invalid_call)
        except (TypeError, ValueError):
            continue
        raise AssertionError(f"benchmark accepted {invalid_call!r}")
    return "Fibonacci and benchmark reject malformed, negative, and zero-denominator-style inputs."


def check_task3_paths() -> str:
    try:
        validate_workspace("artifacts/task3/../task3")
    except SafetyError:
        pass
    else:
        raise AssertionError("Task 3 accepted a traversal path")
    task3_root = ROOT / "artifacts/task3"
    task3_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ultimate-red-team-", dir=task3_root) as temporary:
        workspace = Path(temporary)
        source = workspace / "input.txt"
        source.write_text("synthetic only\n", encoding="utf-8")
        result = apply_plan(workspace, [PlannedMove("input.txt", "../escape.txt")])
        if result["complete"] or (workspace.parent / "escape.txt").exists():
            raise AssertionError("Task 3 traversal move escaped its isolated workspace")
    protected = _export_record(Record("input.txt", 1, "email", "=formula"))
    if protected["value"] != "'=formula":
        raise AssertionError("Task 3 did not neutralize a formula-leading CSV value")
    return "Task 3 rejects traversal and unsafe moves and neutralizes formula-leading CSV cells."


def check_campaign_and_strategy() -> str:
    campaign = build_campaign()
    duplicate = copy.deepcopy(campaign)
    duplicate["actions"].append(copy.deepcopy(duplicate["actions"][0]))
    if not validate_campaign(duplicate):
        raise AssertionError("campaign validator accepted a duplicate action")
    strategy = build_strategy()
    invalid_finance = copy.deepcopy(strategy)
    invalid_finance["scenarios"][0]["customers"] = 0
    if "invalid financial denominator" not in validate_strategy(invalid_finance):
        raise AssertionError("strategy validator accepted a zero customer denominator")
    return "Campaign duplicate events and Strategy zero-denominator financial data are rejected."


def check_workflow() -> str:
    state = State()
    if transition(state, "subscription_confirmed", 0) != "entered":
        raise AssertionError("welcome workflow did not enter")
    if transition(state, "consent_withdrawal", 1) != "suppressed":
        raise AssertionError("consent withdrawal did not suppress")
    if transition(state, "tick", 200) != "suppressed" or state.sent_at:
        raise AssertionError("suppressed contact received a draft")
    capped = State(sent_at=[-48, -24, 0])
    transition(capped, "subscription_confirmed", 0)
    if transition(capped, "tick", 24) != "deferred_frequency_cap" or capped.next_step != 0:
        raise AssertionError("frequency cap advanced or sent an overdue message")
    return "Consent withdrawal suppresses drafts and the rolling frequency cap defers without advancing."


def check_combined_and_candidates() -> str:
    marketing = PdfReader(PROTECTED[0])
    python_report = PdfReader(PROTECTED[1])
    if len(marketing.pages) != 38 or len(python_report.pages) != 14:
        raise AssertionError("approved report page count changed")
    if any(not (page.extract_text() or "").strip() for page in [*marketing.pages, *python_report.pages]):
        raise AssertionError("a report page has no extractable text")
    sources = [PdfReader(path) for path in PROTECTED[2:]]
    offsets = (2, 6, 26, 32)
    for source, offset in zip(sources, offsets):
        for source_page, merged_page in zip(source.pages, marketing.pages[offset : offset + len(source.pages)]):
            if stream(source_page) != stream(merged_page):
                raise AssertionError(f"combined Marketing page stream differs at offset {offset}")
    for source, candidate in (
        (PROTECTED[0], ROOT / "digital_marketing/deliverables/Progree_Digital_Marketing_Tasks_2_3_4_FINAL_CANDIDATE.pdf"),
        (PROTECTED[1], ROOT / "deliverables/Progree_Python_Tasks_2_3_4_FINAL_CANDIDATE.pdf"),
    ):
        original = PdfReader(source)
        enhanced = PdfReader(candidate)
        if len(original.pages) != len(enhanced.pages):
            raise AssertionError(f"candidate count changed for {candidate.name}")
        for before, after in zip(original.pages, enhanced.pages):
            if stream(before) != stream(after) or before.extract_text() != after.extract_text():
                raise AssertionError(f"candidate changed source page content for {candidate.name}")
    candidate_document = fitz.open(ROOT / "digital_marketing/deliverables/Progree_Digital_Marketing_Tasks_2_3_4_FINAL_CANDIDATE.pdf")
    try:
        uri_count = sum(1 for page in candidate_document for link in page.get_links() if link.get("kind") == fitz.LINK_URI)
    finally:
        candidate_document.close()
    if uri_count != 11:
        raise AssertionError(f"expected 11 reliable Marketing URI annotations, found {uri_count}")
    old_output = combined.OUTPUT
    old_manifest = combined.MANIFEST
    try:
        with tempfile.TemporaryDirectory(prefix=".ultimate-combined-assembly-", dir=ROOT / "digital_marketing" / "evidence") as temporary:
            combined.OUTPUT = Path(temporary) / "combined.pdf"
            combined.MANIFEST = Path(temporary) / "manifest.json"
            result = combined.build()
            if result["page_count"] != 38 or not all(result["source_hashes_unchanged"].values()):
                raise AssertionError("isolated combined-PDF assembly regression failed")
    finally:
        combined.OUTPUT = old_output
        combined.MANIFEST = old_manifest
    return "All source streams survive assembly/candidate navigation; candidates retain text and Marketing has 11 verified URI annotations."


def main() -> int:
    before = {path.relative_to(ROOT).as_posix(): sha256(path) for path in PROTECTED}
    checks = {
        "fibonacci_input_validation": check_fibonacci(),
        "task3_filesystem_safety": check_task3_paths(),
        "campaign_and_strategy_metrics": check_campaign_and_strategy(),
        "email_workflow_state": check_workflow(),
        "pdf_integrity_and_navigation": check_combined_and_candidates(),
    }
    after = {path.relative_to(ROOT).as_posix(): sha256(path) for path in PROTECTED}
    if before != after:
        raise AssertionError("a protected artifact changed during red-team checks")
    print(json.dumps({"outcome": "passed", "checks": checks, "protected_hashes_unchanged": True}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
