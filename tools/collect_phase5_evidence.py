"""Validate fresh Phase 5 executions and publish sanitized evidence.

This tool deliberately refuses to create a success manifest unless the retained raw
outputs demonstrate the required outcomes. It copies only synthetic, repository-local
command output into ``evidence/phase5/outputs`` and records SHA-256 digests.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_DOCUMENTS = (
    "Python Programming Tasks & Instructions.pdf",
    "Digital Marketing & Branding Tasks & Instructions.md",
    "Text Message 1.md",
    "Text Message 2.md",
)
RETAINED_OUTPUTS = (
    "full-tests.txt",
    "task2-count-10.json",
    "task2-count-0.json",
    "task2-count-100.json",
    "task2-invalid.stderr",
    "task2-benchmark.json",
    "task3-preview.json",
    "task3-apply.json",
    "task3-repeat.json",
    "task3-master.csv",
    "task3-safe-failure.stderr",
    "task4-main.txt",
    "task4-unsupported.txt",
    "task4-eof.txt",
    "task4-interrupt.txt",
    "pdf-qa.json",
)


class EvidenceError(RuntimeError):
    """Raised when fresh evidence is absent or does not meet its claimed outcome."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_exit(raw_dir: Path, stem: str) -> int:
    path = raw_dir / f"{stem}.exit"
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError) as error:
        raise EvidenceError(f"missing or invalid exit capture: {path.name}") from error


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise EvidenceError(f"invalid JSON evidence: {path.name}") from error


def require(condition: bool, message: str) -> None:
    if not condition:
        raise EvidenceError(message)


def hash_multiset(path: Path, excluded_names: set[str] | None = None) -> Counter[str]:
    excluded_names = excluded_names or set()
    return Counter(sha256(file) for file in path.rglob("*") if file.is_file() and file.name not in excluded_names)


def validate(raw_dir: Path) -> dict[str, Any]:
    """Parse and validate the actual execution captures."""
    for name in RETAINED_OUTPUTS:
        require((raw_dir / name).is_file(), f"required raw output is missing: {name}")

    expected_exits = {
        "full-tests": 0,
        "task2-count-10": 0,
        "task2-count-0": 0,
        "task2-count-100": 0,
        "task2-invalid": 2,
        "task2-benchmark": 0,
        "task3-preview": 0,
        "task3-apply": 0,
        "task3-repeat": 0,
        "task3-safe-failure": 2,
        "task4-main": 0,
        "task4-unsupported": 0,
        "task4-eof": 0,
        "task4-interrupt": 0,
    }
    for stem, expected in expected_exits.items():
        require(read_exit(raw_dir, stem) == expected, f"{stem} did not have expected exit code {expected}")

    tests = (raw_dir / "full-tests.txt").read_text(encoding="utf-8")
    test_match = re.search(r"Ran (\d+) tests in ([0-9.]+)s\s+OK\s*$", tests, flags=re.MULTILINE)
    require(test_match is not None, "full test output does not end in an OK result")
    test_count = int(test_match.group(1))
    require(test_count >= 54, "full test output did not include the expected Task 4 reset regression")

    count_10 = load_json(raw_dir / "task2-count-10.json")
    count_0 = load_json(raw_dir / "task2-count-0.json")
    count_100 = load_json(raw_dir / "task2-count-100.json")
    require(count_10 == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34], "Task 2 count 10 output is invalid")
    require(count_0 == [], "Task 2 zero output is invalid")
    require(isinstance(count_100, list) and len(count_100) == 100 and count_100[-1] == 218922995834555169026, "Task 2 count 100 output is invalid")
    invalid_text = (raw_dir / "task2-invalid.stderr").read_text(encoding="utf-8")
    require("count must be greater than or equal to zero" in invalid_text, "Task 2 invalid-count diagnostic is absent")

    benchmark = load_json(raw_dir / "task2-benchmark.json")
    require(benchmark.get("units") == "seconds", "Task 2 benchmark unit is not seconds")
    require(benchmark.get("repeat_count") == 5 and benchmark.get("executions_per_repeat") == 100, "Task 2 benchmark configuration is invalid")
    benchmark_results = benchmark.get("results")
    require(isinstance(benchmark_results, list) and [result.get("count") for result in benchmark_results] == [10, 100, 1000], "Task 2 benchmark counts are invalid")
    for result in benchmark_results:
        samples = result.get("sample_totals_seconds")
        require(isinstance(samples, list) and len(samples) == 5 and all(isinstance(value, (int, float)) and value > 0 for value in samples), "Task 2 benchmark samples are invalid")

    preview = load_json(raw_dir / "task3-preview.json")
    apply = load_json(raw_dir / "task3-apply.json")
    repeat = load_json(raw_dir / "task3-repeat.json")
    require(preview.get("mode") == "preview" and len(preview.get("planned_moves", [])) == 7 and preview.get("csv", {}).get("status") == "not_written_in_preview", "Task 3 preview evidence is invalid")
    require(apply.get("mode") == "apply" and apply.get("apply", {}).get("complete") is True and apply.get("apply", {}).get("failure_count") == 0, "Task 3 apply evidence is invalid")
    require(apply.get("csv", {}).get("status") == "written_and_verified" and len(apply.get("records", [])) == 9, "Task 3 CSV evidence is invalid")
    destinations = {move["destination_path"] for move in apply["apply"]["moves"]}
    require("txt/notes__1.txt" in destinations, "Task 3 collision result is absent")
    require(repeat.get("apply", {}).get("complete") is True and not repeat.get("planned_moves") and len(repeat.get("records", [])) == 9, "Task 3 repeat evidence is invalid")
    safe_error = (raw_dir / "task3-safe-failure.stderr").read_text(encoding="utf-8")
    require("CSV output filename must end in .csv" in safe_error, "Task 3 safe-failure diagnostic is absent")

    with (raw_dir / "task3-master.csv").open("r", encoding="utf-8", newline="") as source:
        csv_rows = list(csv.DictReader(source))
    require(len(csv_rows) == 9 and list(csv_rows[0]) == ["source_path", "line_number", "kind", "value"], "Task 3 master CSV read-back is invalid")

    integration_root = ROOT / "artifacts/task3/phase5-integration"
    safe_root = ROOT / "artifacts/task3/phase5-safe-failure"
    before = Counter(line.split()[0] for line in (raw_dir / "task3-before-hashes.txt").read_text(encoding="utf-8").splitlines())
    after = hash_multiset(integration_root, {"master.csv", ".task3-generated-csv.json"})
    safe_before = (raw_dir / "task3-safe-before-hashes.txt").read_text(encoding="utf-8")
    safe_after = (raw_dir / "task3-safe-after-hashes.txt").read_text(encoding="utf-8")
    require(before == after, "Task 3 organized file-content hashes differ")
    require(safe_before == safe_after, "Task 3 rejected output destination changed input files")

    main_chat = (raw_dir / "task4-main.txt").read_text(encoding="utf-8")
    unsupported_chat = (raw_dir / "task4-unsupported.txt").read_text(encoding="utf-8")
    eof_chat = (raw_dir / "task4-eof.txt").read_text(encoding="utf-8")
    interrupt_chat = (raw_dir / "task4-interrupt.txt").read_text(encoding="utf-8")
    for expected in ("Task 2 generates", "--benchmark", "Python learning", "still need a clear choice", "18 October 2026", "Context reset", "Goodbye"):
        require(expected in main_chat, f"Task 4 main conversation is missing: {expected}")
    for expected in ("do not recognize that as a Task 4 question", "still need a clear choice", "session keeps", "Goodbye"):
        require(expected in unsupported_chat, f"Task 4 unsupported-input conversation is missing: {expected}")
    require("End of input" in eof_chat, "Task 4 EOF outcome is absent")
    require("Interrupted safely" in interrupt_chat, "Task 4 interrupt outcome is absent")

    pdf_qa = load_json(raw_dir / "pdf-qa.json")
    require(pdf_qa.get("outcome") == "passed", "PDF QA did not pass")
    require(12 <= int(pdf_qa.get("page_count", 0)) <= 18, "PDF page count is outside the requested range")

    return {
        "test_count": test_count,
        "test_duration_seconds": float(test_match.group(2)),
        "benchmark": benchmark,
        "task3": {
            "preview_moves": len(preview["planned_moves"]),
            "apply_moves": len(apply["apply"]["moves"]),
            "record_count": len(apply["records"]),
            "csv_rows": csv_rows,
            "repeat_moves": len(repeat["planned_moves"]),
            "records": apply["records"],
            "moves": apply["apply"]["moves"],
            "content_hashes_match": True,
            "safe_failure_preserved_inputs": True,
        },
    }


def original_integrity(baseline: str) -> dict[str, Any]:
    documents: dict[str, dict[str, str | bool]] = {}
    for name in ORIGINAL_DOCUMENTS:
        current = ROOT / name
        result = subprocess.run(["git", "show", f"{baseline}:{name}"], cwd=ROOT, capture_output=True, check=False)
        if result.returncode != 0:
            raise EvidenceError(f"could not read approved baseline for {name}")
        current_digest = sha256(current)
        baseline_digest = hashlib.sha256(result.stdout).hexdigest()
        documents[name] = {
            "sha256": current_digest,
            "approved_baseline_sha256": baseline_digest,
            "matches_approved_baseline": current_digest == baseline_digest,
        }
    require(all(record["matches_approved_baseline"] for record in documents.values()), "an original assignment document changed")
    return {"approved_baseline": baseline, "documents": documents}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and package real Phase 5 execution evidence.")
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "artifacts/phase5")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "evidence/phase5")
    parser.add_argument("--approved-baseline", default="31cf193d4bf3b8e0c822875e6b4ba80f4f7d0a3d")
    args = parser.parse_args()

    raw_dir = args.raw_dir.resolve()
    output_dir = args.output_dir.resolve()
    summary = validate(raw_dir)
    source_commit = (raw_dir / "source-commit.txt").read_text(encoding="utf-8").strip()
    require(re.fullmatch(r"[0-9a-f]{40}", source_commit) is not None, "source commit capture is invalid")
    execution_utc = (raw_dir / "execution-started-utc.txt").read_text(encoding="utf-8").strip()
    require(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", execution_utc) is not None, "UTC execution timestamp is invalid")

    output_dir.mkdir(parents=True, exist_ok=True)
    retained_dir = output_dir / "outputs"
    retained_dir.mkdir(exist_ok=True)
    digests: dict[str, str] = {}
    for name in RETAINED_OUTPUTS:
        destination = retained_dir / name
        shutil.copyfile(raw_dir / name, destination)
        digests["outputs/" + name] = sha256(destination)

    integrity = original_integrity(args.approved_baseline)
    (retained_dir / "original_document_integrity.json").write_text(json.dumps(integrity, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    digests["outputs/original_document_integrity.json"] = sha256(retained_dir / "original_document_integrity.json")

    manifest = {
        "evidence_version": 1,
        "scope": "fresh Phase 5 integration validation; earlier task evidence remains historical",
        "source_commit": source_commit,
        "approved_starting_commit": args.approved_baseline,
        "execution_started_utc": execution_utc,
        "manifest_created_utc": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "working_directory": ".",
        "python_version": (raw_dir / "python-version.txt").read_text(encoding="utf-8").strip(),
        "platform": (raw_dir / "platform.txt").read_text(encoding="utf-8").splitlines(),
        "input_fixtures": ["fixtures/task3/ (copied to artifacts/task3/phase5-integration)", "fixtures/task3/ (copied to artifacts/task3/phase5-safe-failure)"],
        "commands": [
            {"command": "python -m unittest discover -s tests -v", "exit_code": 0, "outcome": f"{summary['test_count']} tests passed"},
            {"command": "python -m internship.task2 --count 10", "exit_code": 0},
            {"command": "python -m internship.task2 --count 0", "exit_code": 0},
            {"command": "python -m internship.task2 --count 100", "exit_code": 0},
            {"command": "python -m internship.task2 --count -1", "exit_code": 2},
            {"command": "python -m internship.task2 --benchmark --benchmark-counts 10 100 1000 --repeats 5 --number 100", "exit_code": 0},
            {"command": "python -m internship.task3 --root artifacts/task3/phase5-integration", "exit_code": 0},
            {"command": "python -m internship.task3 --root artifacts/task3/phase5-integration --apply --csv master.csv", "exit_code": 0},
            {"command": "python -m internship.task3 --root artifacts/task3/phase5-integration --apply --csv master.csv", "exit_code": 0},
            {"command": "python -m internship.task3 --root artifacts/task3/phase5-safe-failure --apply --csv notes.txt", "exit_code": 2},
            {"command": "python -m internship.task4 < scripted-input", "exit_code": 0},
            {"command": "python -m internship.task4 < /dev/null", "exit_code": 0},
            {"command": "SIGINT subprocess running python -m internship.task4", "exit_code": 0},
        ],
        "test_summary": {"count": summary["test_count"], "outcome": "passed", "duration_seconds": summary["test_duration_seconds"]},
        "task2": {"normal_output": "outputs/task2-count-10.json", "zero_output": "outputs/task2-count-0.json", "larger_output": "outputs/task2-count-100.json", "invalid_diagnostic": "outputs/task2-invalid.stderr", "benchmark_output": "outputs/task2-benchmark.json", "benchmark": summary["benchmark"]},
        "task3": {"preview_output": "outputs/task3-preview.json", "apply_output": "outputs/task3-apply.json", "repeat_output": "outputs/task3-repeat.json", "master_csv_output": "outputs/task3-master.csv", "safe_failure_output": "outputs/task3-safe-failure.stderr", **summary["task3"]},
        "task4": {"main_transcript": "outputs/task4-main.txt", "unsupported_transcript": "outputs/task4-unsupported.txt", "eof_transcript": "outputs/task4-eof.txt", "interrupt_transcript": "outputs/task4-interrupt.txt"},
        "pdf_qa_output": "outputs/pdf-qa.json",
        "original_document_integrity": "outputs/original_document_integrity.json",
        "retained_output_sha256": digests,
        "limitations": [
            "Benchmark samples are environment-dependent measurements, not performance guarantees.",
            "Task 3 evidence uses copied synthetic fixtures in an isolated artifact child workspace only.",
            "The report has no personal identity, eligibility decision, certificate approval, organizer deadline hour, or submission confirmation.",
        ],
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str((output_dir / "manifest.json").relative_to(ROOT)), "test_count": summary["test_count"], "source_commit": source_commit}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EvidenceError as error:
        print(f"phase5-evidence: error: {error}", file=__import__("sys").stderr)
        raise SystemExit(2)
