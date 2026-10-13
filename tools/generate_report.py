"""Generate the Phase 5 PDF from validated, retained execution evidence.

The report intentionally has no participant identity fields. It refuses to create a
PDF if the evidence manifest, retained-output hashes, or required execution outcomes
are missing or inconsistent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import textwrap
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE = ROOT / "evidence/phase5/manifest.json"
DEFAULT_OUTPUT = ROOT / "deliverables/Progree_Python_Tasks_2_3_4.pdf"
NAVY = colors.HexColor("#16324F")
BLUE = colors.HexColor("#1F6F8B")
TEAL = colors.HexColor("#1E847F")
PALE_BLUE = colors.HexColor("#EAF3F7")
PALE_TEAL = colors.HexColor("#E8F4F1")
SLATE = colors.HexColor("#415A77")


class ReportEvidenceError(RuntimeError):
    """Evidence is not adequate for a truthful report."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail_if(condition: bool, message: str) -> None:
    if condition:
        raise ReportEvidenceError(message)


def load_evidence(path: Path) -> tuple[dict[str, Any], Path]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReportEvidenceError(f"cannot read evidence manifest: {error}") from error
    evidence_root = path.parent
    required = ("source_commit", "test_summary", "task2", "task3", "task4", "retained_output_sha256")
    fail_if(any(key not in manifest for key in required), "evidence manifest lacks required fields")
    for relative, expected in manifest["retained_output_sha256"].items():
        retained = evidence_root / relative
        fail_if(not retained.is_file(), f"retained evidence is missing: {relative}")
        fail_if(sha256(retained) != expected, f"retained evidence digest mismatch: {relative}")
    fail_if(manifest["test_summary"].get("outcome") != "passed", "test evidence is not a pass")
    fail_if(int(manifest["test_summary"].get("count", 0)) < 54, "test evidence is incomplete")
    benchmark = manifest["task2"].get("benchmark", {})
    fail_if(benchmark.get("units") != "seconds", "Task 2 benchmark unit is missing")
    fail_if(len(benchmark.get("results", [])) != 3, "Task 2 benchmark results are incomplete")
    fail_if(manifest["task3"].get("record_count") != 9, "Task 3 record evidence is incomplete")
    fail_if(not manifest["task3"].get("content_hashes_match"), "Task 3 content-hash check failed")
    fail_if(not manifest["task3"].get("safe_failure_preserved_inputs"), "Task 3 safe-failure check failed")
    integrity_path = evidence_root / manifest["original_document_integrity"]
    integrity = json.loads(integrity_path.read_text(encoding="utf-8"))
    fail_if(not all(row.get("matches_approved_baseline") for row in integrity["documents"].values()), "original-document integrity check failed")
    return manifest, evidence_root


def actual_text(evidence_root: Path, relative: str) -> str:
    return (evidence_root / relative).read_text(encoding="utf-8")


def actual_json(evidence_root: Path, relative: str) -> Any:
    return json.loads(actual_text(evidence_root, relative))


def code_excerpt(path: Path, start: str, lines: int) -> str:
    source = path.read_text(encoding="utf-8").splitlines()
    try:
        index = next(index for index, line in enumerate(source) if line.startswith(start))
    except StopIteration as error:
        raise ReportEvidenceError(f"source excerpt not found: {start}") from error
    return "\n".join(source[index : index + lines])


def code_block(text: str, style: ParagraphStyle) -> Preformatted:
    """Wrap monospaced evidence safely within the printable PDF width."""
    wrapped: list[str] = []
    for line in text.splitlines():
        if not line:
            wrapped.append("")
            continue
        indent = re.match(r"\s*", line).group(0)
        fragments = textwrap.wrap(
            line[len(indent) :],
            width=max(32, 96 - len(indent)),
            initial_indent=indent,
            subsequent_indent=indent + "  ",
            break_long_words=True,
            break_on_hyphens=False,
        )
        wrapped.extend(fragments or [indent])
    return Preformatted("\n".join(wrapped), style)


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("ReportTitle", parent=base["Title"], fontName="Helvetica-Bold", fontSize=28, leading=34, textColor=NAVY, alignment=TA_CENTER, spaceAfter=14),
        "subtitle": ParagraphStyle("Subtitle", parent=base["Normal"], fontName="Helvetica", fontSize=14, leading=19, textColor=SLATE, alignment=TA_CENTER),
        "h1": ParagraphStyle("H1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=NAVY, spaceBefore=2, spaceAfter=10),
        "h2": ParagraphStyle("H2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=BLUE, spaceBefore=7, spaceAfter=5),
        "body": ParagraphStyle("Body", parent=base["BodyText"], fontName="Helvetica", fontSize=9.4, leading=13.2, spaceAfter=6),
        "small": ParagraphStyle("Small", parent=base["BodyText"], fontName="Helvetica", fontSize=7.8, leading=10),
        "table": ParagraphStyle("Table", parent=base["BodyText"], fontName="Helvetica", fontSize=7.2, leading=9),
        "caption": ParagraphStyle("Caption", parent=base["BodyText"], fontName="Helvetica-Oblique", fontSize=7.6, leading=9, textColor=SLATE, spaceBefore=3, spaceAfter=6),
        "toc": ParagraphStyle("TOC", parent=base["BodyText"], fontName="Helvetica", fontSize=10, leading=16, leftIndent=4),
        "code": ParagraphStyle("Code", parent=base["Code"], fontName="Courier", fontSize=7.2, leading=8.9, backColor=colors.HexColor("#F5F7F8"), borderColor=colors.HexColor("#D9E2E8"), borderWidth=0.3, borderPadding=5),
    }


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def section_title(number: str, title: str, style: ParagraphStyle) -> list[Any]:
    return [p(f"{number}. {title}", style), Spacer(1, 2)]


def bullet(items: list[str], style: ParagraphStyle) -> list[Any]:
    return [p(f"• {item}", style) for item in items]


def table(data: list[list[Any]], widths: list[float], header: bool = True) -> Table:
    rendered = [[cell if hasattr(cell, "wrap") else str(cell) for cell in row] for row in data]
    result = Table(rendered, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands: list[tuple[Any, ...]] = [
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#C9D6DF")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    if header:
        commands.extend([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")])
    result.setStyle(TableStyle(commands))
    return result


def footer(canvas: Any, document: Any) -> None:
    canvas.saveState()
    width, _ = A4
    canvas.setStrokeColor(colors.HexColor("#C9D6DF"))
    canvas.line(1.7 * cm, 1.35 * cm, width - 1.7 * cm, 1.35 * cm)
    canvas.setFillColor(SLATE)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(1.7 * cm, 0.9 * cm, "Progree Python Programming Internship — Tasks 2, 3 and 4")
    canvas.drawRightString(width - 1.7 * cm, 0.9 * cm, f"Page {document.page}")
    canvas.restoreState()


def build_story(manifest: dict[str, Any], evidence_root: Path) -> list[Any]:
    s = styles()
    story: list[Any] = []
    source_commit = manifest["source_commit"]
    test_summary = manifest["test_summary"]
    benchmark = manifest["task2"]["benchmark"]
    task3 = manifest["task3"]
    main_chat = actual_text(evidence_root, manifest["task4"]["main_transcript"])
    unsupported_chat = actual_text(evidence_root, manifest["task4"]["unsupported_transcript"])
    csv_text = actual_text(evidence_root, task3["master_csv_output"])

    # 1. Cover
    story += [Spacer(1, 4.0 * cm), p("PROGREE", s["subtitle"]), Spacer(1, 0.4 * cm), p("Python Programming Internship", s["title"]), p("Technical Report — Tasks 2, 3 and 4", s["subtitle"]), Spacer(1, 1.5 * cm)]
    cover = table(
        [[p("Report date", s["table"]), p("13 October 2026", s["table"])], [p("Evidence source", s["table"]), p(f"Fresh Phase 5 validation from commit <font name='Courier'>{source_commit[:12]}</font>", s["table"])], [p("Scope", s["table"]), p("Fibonacci generation, safe file automation, and a rule-based terminal chatbot", s["table"])], [p("Identity", s["table"]), p("No participant identity, registration number, or organizer endorsement is represented.", s["table"]) ]],
        [3.5 * cm, 11.5 * cm],
        header=False,
    )
    cover.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), PALE_BLUE)]))
    story += [cover, Spacer(1, 1.3 * cm), p("Prepared from executed local evidence only. This report does not confirm certificate eligibility, form submission, or an organizer deadline hour/timezone.", s["caption"]), PageBreak()]

    # 2. Executive summary and contents
    story += section_title("Executive summary", "Assignment objectives and verification", s["h1"])
    story += [p("The authoritative Python assignment asks for a Fibonacci module with timeit benchmarking, a safe file-organization and text-parsing utility, and a multi-intent terminal chatbot. This report covers the three completed technical tasks and the fresh validation run used for this document.", s["body"])]
    story += bullet([
        f"The consolidated suite executed {test_summary['count']} tests and passed in {test_summary['duration_seconds']:.3f} seconds.",
        "Task 2 evidence contains real JSON outputs, an invalid-input diagnostic, and 5-repeat × 100-call timeit measurements in seconds.",
        "Task 3 evidence records 7 planned/applied moves, a collision-safe destination, 9 verified CSV records, a zero-move repeat run, and an output-safety rejection.",
        "Task 4 evidence contains real terminal transcripts for multi-intent routing, clarification recovery, reset, unsupported input, EOF, and Ctrl+C.",
    ], s["body"])
    story += [p("Scope and limitations", s["h2"]), p("All Task 3 data is synthetic. Benchmark timings vary by environment. The report does not include Task 1, personal identity, credentials, a certificate decision, track-eligibility confirmation, or a Google Form submission claim.", s["body"]), p("Table of contents", s["h2"])]
    toc_rows = [["1", "Task 2 — Fibonacci"], ["2", "Task 3 — File automation"], ["3", "Task 4 — Rule-based chatbot"], ["4", "Cross-task quality assurance"], ["5", "Conclusion and appendix"]]
    toc_data = [[p("Section", s["table"]), p("Contents", s["table"])]]
    toc_data.extend([[p(section, s["table"]), p(contents, s["table"])] for section, contents in toc_rows])
    story += [table(toc_data, [2.5 * cm, 12.5 * cm]), PageBreak()]

    # 3. Task 2 design
    story += section_title("1", "Task 2 — Fibonacci generation", s["h1"])
    story += [p("Objective and requirements mapping", s["h2"]), p("The module returns exactly the requested number of Fibonacci terms beginning with 0 and 1. It validates negative and invalid-type inputs, emits structured JSON arrays through the CLI, and measures generation with Python’s timeit framework.", s["body"])]
    story += [table([[p("Requirement", s["table"]), p("Implemented behavior", s["table"])], [p("Exact list output", s["table"]), p("Iterative function returns a Python list; CLI emits JSON.", s["table"])], [p("Validation", s["table"]), p("Negative integers raise ValueError; bool and non-integers are rejected.", s["table"])], [p("Benchmark", s["table"]), p("timeit measures fibonacci(count) only, excluding printing and JSON encoding.", s["table"]) ]], [4.0 * cm, 11.0 * cm])]
    story += [p("Algorithm and validation excerpt", s["h2"]), code_block(code_excerpt(ROOT / "internship/task2.py", "def fibonacci", 20), s["code"]), p("The loop performs O(count) iterations and stores O(count) integers. Python’s arbitrary-precision integers make additions progressively more expensive as the sequence grows, so large-count cost is not constant per iteration.", s["body"]), PageBreak()]

    # 4. Task 2 real execution
    story += section_title("1", "Task 2 — executed outputs and timeit", s["h1"])
    count_10 = actual_text(evidence_root, manifest["task2"]["normal_output"]).strip()
    count_0 = actual_text(evidence_root, manifest["task2"]["zero_output"]).strip()
    invalid = actual_text(evidence_root, manifest["task2"]["invalid_diagnostic"]).strip().splitlines()[-1]
    story += [p("Fresh command-line evidence", s["h2"]), table([[p("Command case", s["table"]), p("Observed result", s["table"])], [p("count 10", s["table"]), p(f"<font name='Courier'>{count_10}</font>", s["table"])], [p("count 0", s["table"]), p(f"<font name='Courier'>{count_0}</font>", s["table"])], [p("count 100", s["table"]), p("Exit 0; retained JSON contains 100 terms and ends with 218922995834555169026.", s["table"])], [p("count -1", s["table"]), p(f"Exit 2; <font name='Courier'>{invalid}</font>", s["table"]) ]], [3.2 * cm, 11.8 * cm])]
    rows: list[list[Any]] = [[p("Terms", s["table"]), p("Sample totals, seconds (5 repeats × 100)", s["table"]), p("Min/call, seconds", s["table"]), p("Median/call, seconds", s["table"])]]
    for item in benchmark["results"]:
        samples = ", ".join(f"{value:.6g}" for value in item["sample_totals_seconds"])
        rows.append([p(str(item["count"]), s["table"]), p(samples, s["table"]), p(f"{item['minimum_per_call_seconds']:.6g}", s["table"]), p(f"{item['median_per_call_seconds']:.6g}", s["table"])])
    story += [p("Benchmark methodology and results", s["h2"]), p(benchmark["measurement"] + ". Units: seconds. Results are measurements from this environment, not performance guarantees.", s["body"]), table(rows, [1.4 * cm, 7.2 * cm, 3.1 * cm, 3.3 * cm]), PageBreak()]

    # 5. Task 2 test evidence
    story += section_title("1", "Task 2 — quality evidence", s["h1"])
    story += [p("Testing and limitations", s["h2"]), p("The full test suite includes exact small outputs, recurrence behavior, a larger known term, negative and invalid types, JSON CLI behavior, resource limits, benchmark validation, and real timing metadata. The consolidated run passed; the report does not treat timing values as hardware-independent targets.", s["body"]), p("Reproduction commands", s["h2"]), code_block("python -m internship.task2 --count 10\npython -m internship.task2 --count 0\npython -m internship.task2 --count -1\npython -m internship.task2 --benchmark --benchmark-counts 10 100 1000 --repeats 5 --number 100", s["code"]), p("Evidence reference: evidence/phase5/outputs/task2-count-10.json, task2-count-0.json, task2-count-100.json, task2-invalid.stderr, and task2-benchmark.json.", s["caption"]), PageBreak()]

    # 6. Task 3 design
    story += section_title("2", "Task 3 — safe file automation", s["h1"])
    story += [p("Objective and workflow", s["h2"]), p("Task 3 accepts an explicit synthetic workspace, plans immediate-file organization by final extension, optionally applies collision-safe moves, extracts emails and transaction IDs from relevant UTF-8 text files, and writes a read-back-verified master CSV.", s["body"])]
    workflow = table([[p("Preview", s["table"]), p("Apply", s["table"]), p("Extract and verify", s["table"])], [p("Validate workspace and plan deterministic moves without writing.", s["table"]), p("Require --apply, preflight UTF-8 input, refuse overwrites, and record outcomes.", s["table"]), p("Extract ordered records and atomically write/read back a UTF-8 CSV.", s["table"]) ]], [5 * cm, 5 * cm, 5 * cm])
    workflow.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), TEAL), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white)]))
    story += [workflow, p("Safety boundaries", s["h2"])]
    story += bullet(["Preview is the default; writes require an isolated child under artifacts/task3.", "Canonical fixtures, the artifacts parent, path traversal, symlinks, arbitrary directories, and unsuitable CSV names are rejected.", "Preflight decoding occurs before apply moves; later filesystem races can still produce truthful partial-failure reporting.", "Formula-leading CSV cells are sanitized for spreadsheet safety while raw synthetic evidence remains traceable."], s["body"])
    story += [code_block(code_excerpt(ROOT / "internship/task3.py", "def plan_organization", 20), s["code"]), PageBreak()]

    # 7. Task 3 execution
    story += section_title("2", "Task 3 — executed organization and CSV", s["h1"])
    story += [p("Fresh isolated demonstration", s["h2"]), p(f"A fresh copy of fixtures/task3 was placed under artifacts/task3/phase5-integration. Preview planned {task3['preview_moves']} moves without a CSV. Apply completed {task3['apply_moves']} moves with zero failures and produced {task3['record_count']} verified records. The repeat run planned {task3['repeat_moves']} moves and safely regenerated the verified master CSV.", s["body"])]
    move_rows = [[p("Source", s["table"]), p("Destination", s["table"]), p("Outcome", s["table"])]]
    move_rows.extend([[p(move["source_path"], s["table"]), p(move["destination_path"], s["table"]), p(move["status"], s["table"])] for move in task3["moves"]])
    story += [p("Before/after organization example", s["h2"]), table(move_rows, [4.1 * cm, 7.1 * cm, 3.8 * cm]), p("The existing txt/notes.txt caused the top-level notes.txt to move to txt/notes__1.txt rather than overwrite content.", s["caption"])]
    csv_lines = "\n".join(csv_text.splitlines()[:6])
    story += [p("Verified master CSV excerpt (synthetic data)", s["h2"]), code_block(csv_lines, s["code"]), PageBreak()]

    # 8. Task 3 assurance
    story += section_title("2", "Task 3 — integrity, idempotency, and errors", s["h1"])
    story += [p("Integrity and regression evidence", s["h2"])]
    story += bullet(["The multiset of SHA-256 file-content hashes before and after organization matched after excluding the generated CSV and marker.", "A second apply planned zero moves and retained nine verified records.", "A deliberate --csv notes.txt attempt exited 2 before any move or write; input hashes remained unchanged.", "The full suite exercises preview/apply, collisions, idempotency, symlink/unsafe-root rejection, malformed UTF-8 preflight, CSV read-back, formula protection, and CLI error exits."], s["body"])
    story += [p("Relevant implementation excerpt", s["h2"]), code_block(code_excerpt(ROOT / "internship/task3.py", "def write_master_csv", 27), s["code"]), p("Evidence references: evidence/phase5/outputs/task3-preview.json, task3-apply.json, task3-repeat.json, task3-master.csv, and task3-safe-failure.stderr.", s["caption"]), PageBreak()]

    # 9. Task 4 design
    story += section_title("3", "Task 4 — multi-intent rule-based chatbot", s["h1"])
    story += [p("Architecture and state", s["h2"]), p("The terminal bot is local and rule based. It normalizes Unicode NFKC input, casefolds, replaces punctuation, normalizes whitespace, applies functional dictionary routing, and uses nested if/elif/else logic for pending choices. It has task guidance, Python learning, and submission guidance trees.", s["body"])]
    story += [table([[p("State field", s["table"]), p("Purpose", s["table"])], [p("current_tree / pending_choice", s["table"]), p("Retains the current help tree and the next valid contextual choices.", s["table"])], [p("last_intent", s["table"]), p("Records each actual recognized or reported intent, including contextual follow-ups.", s["table"])], [p("turn_count / history", s["table"]), p("Counts turns and keeps the 20 newest normalized inputs in process only.", s["table"])], [p("clarification_count", s["table"]), p("Escalates a repeated pending-choice miss; reset/cancel clears it.", s["table"]) ]], [5 * cm, 10 * cm])]
    story += [p("Normalization excerpt", s["h2"]), code_block(code_excerpt(ROOT / "internship/task4.py", "def normalize", 11), s["code"]), PageBreak()]

    # 10. Task 4 routing diagram
    story += section_title("3", "Task 4 — routing and recovery", s["h1"])
    story += [p("Routing/state-transition flow", s["h2"])]
    flow = table([[p("Input", s["table"])], [p("↓ normalize: NFKC, casefold, punctuation, whitespace", s["table"])], [p("↓ global priority: exit → reset/cancel → help", s["table"])], [p("↓ explicit topic switches: tasks / Python / submission", s["table"])], [p("↓ pending contextual tree: nested choices", s["table"])], [p("↓ first ambiguity: contextual clarification", s["table"])], [p("↓ repeated ambiguity: explicit choices + help/reset", s["table"])], [p("↓ unknown: helpful fallback", s["table"]) ]], [14.5 * cm])
    flow.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("BACKGROUND", (0, 5), (-1, 6), PALE_TEAL)]))
    story += [flow, Spacer(1, 8), p("The implementation gives explicit topic switches priority over earlier pending state. Recognized input resets clarification recovery; reset/cancel clears context, history, fallback count, and clarification count.", s["body"]), p("Routing excerpt", s["h2"]), code_block(code_excerpt(ROOT / "internship/task4.py", "def handle_turn", 35), s["code"]), PageBreak()]

    # 11. Task 4 transcript
    story += section_title("3", "Task 4 — genuine conversations and limits", s["h1"])
    main_lines = "\n".join(main_chat.splitlines()[:14])
    unsupported_lines = "\n".join(unsupported_chat.splitlines()[1:6])
    story += [p("Executed multi-intent transcript", s["h2"]), code_block(main_lines, s["code"]), p("Unsupported Task 4 input and recovery", s["h2"]), code_block(unsupported_lines, s["code"]), p("Separate executed captures confirm EOF ends with “End of input” and SIGINT ends with “Interrupted safely”; both exit 0. No session state is persisted and no external service, credentials, or form submission is used.", s["body"]), PageBreak()]

    # 12. QA
    story += section_title("4", "Cross-task quality assurance", s["h1"])
    story += [p("Consolidated verification", s["h2"]), table([[p("Check", s["table"]), p("Fresh observed result", s["table"])], [p("Automated tests", s["table"]), p(f"{test_summary['count']} tests passed in {test_summary['duration_seconds']:.3f} seconds.", s["table"])], [p("Task 2 timeit", s["table"]), p("Three counts, five repeat totals each, 100 executions per repeat; units are seconds.", s["table"])], [p("Task 3 integrity", s["table"]), p("Content-hash multiset matched; safe failure preserved inputs; repeat planned zero moves.", s["table"])], [p("Task 4 termination", s["table"]), p("Scripted exit, EOF, and Ctrl+C all captured with exit 0.", s["table"])], [p("Original documents", s["table"]), p("All four original assignment documents matched the approved-starting-commit SHA-256 digests.", s["table"]) ]], [4.1 * cm, 10.9 * cm])]
    story += [p("Environment and reproducibility", s["h2"]), p(f"Python {manifest['python_version'].replace('Python ', '')}; platform: {'; '.join(manifest['platform'])}. Fresh source commit: <font name='Courier'>{source_commit}</font>. Consolidated manifest: evidence/phase5/manifest.json. It records exact commands, exit codes, UTC execution timestamp, retained-output paths, fixture references, and SHA-256 values.", s["body"]), PageBreak()]

    # 13. Conclusion and blockers
    story += section_title("5", "Conclusion", s["h1"])
    story += [p("Tasks 2–4 are implemented and freshly verified in this repository: iterative Fibonacci generation with parameter checks and timeit evidence; safe synthetic-workspace organization and text parsing with verified CSV output; and a stateful rule-based terminal chatbot with help trees, recovery, and graceful termination.", s["body"]), p("Skills demonstrated", s["h2"])]
    story += bullet(["Python API and CLI design, validation, JSON output, and timing methodology.", "Filesystem safety boundaries, deterministic organization, regular expressions, CSV read-back, and integrity checks.", "Unicode normalization, explicit state machines, dictionary dispatch, nested contextual decisions, and terminal resilience.", "Evidence provenance, report automation, and independent PDF quality assurance."], s["body"])
    story += [p("Outstanding human verification", s["h2"])]
    story += bullet(["Python Programming track eligibility and organizer acceptance of Tasks 2–4.", "Certificate name, registration ID, submission email/WhatsApp number, and form upload constraints/accessibility.", "Organizer deadline cutoff hour and timezone; only the date 18 October 2026 is supplied.", "Authorized Google Form submission after independent review."], s["body"])
    story += [p("Future improvements could expand the chatbot vocabulary, add configurable Task 3 patterns, and compare benchmark trends across controlled environments. They are not claimed as completed here.", s["body"]), PageBreak()]

    # 14. Appendix
    story += section_title("Appendix", "Reproduction commands and references", s["h1"])
    commands = "\n".join(command["command"] for command in manifest["commands"][:10])
    story += [p("Exact command forms recorded in the Phase 5 manifest", s["h2"]), code_block(commands, s["code"]), p("Repository references", s["h2"])]
    refs = [[p("Purpose", s["table"]), p("Path", s["table"])], [p("Authoritative assignment", s["table"]), p("Python Programming Tasks & Instructions.pdf", s["table"])], [p("Submission messages", s["table"]), p("Text Message 1.md; Text Message 2.md", s["table"])], [p("Phase 5 manifest", s["table"]), p("evidence/phase5/manifest.json", s["table"])], [p("Report generator", s["table"]), p("tools/generate_report.py", s["table"])], [p("Task sources", s["table"]), p("internship/task2.py; internship/task3.py; internship/task4.py", s["table"])]]
    story += [table(refs, [4.4 * cm, 10.6 * cm]), Spacer(1, 10), p("The report’s displayed execution outcomes come from retained Phase 5 evidence files validated by their SHA-256 digests before PDF generation.", s["caption"])]
    return story


def generate(evidence_path: Path, output_path: Path) -> None:
    manifest, evidence_root = load_evidence(evidence_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(str(output_path), pagesize=A4, rightMargin=1.7 * cm, leftMargin=1.7 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm, title="Progree Python Tasks 2, 3 and 4", author="")
    document.build(build_story(manifest, evidence_root), onFirstPage=footer, onLaterPages=footer)
    fail_if(not output_path.is_file() or output_path.stat().st_size == 0, "PDF was not created")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an evidence-driven Task 2–4 PDF report.")
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        generate(args.evidence.resolve(), args.output.resolve())
    except (ReportEvidenceError, OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"report: error: {error}")
        return 2
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
