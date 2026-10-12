"""Real filesystem and CLI tests for Task 3's synthetic-workspace utility."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from internship import task3


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "task3"
ARTIFACT_PARENT = ROOT / "artifacts" / "task3"


def inventory(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


class Task3WorkspaceTest(unittest.TestCase):
    def setUp(self) -> None:
        ARTIFACT_PARENT.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=ARTIFACT_PARENT)
        self.workspace = Path(self.temporary.name) / "workspace"
        shutil.copytree(FIXTURE, self.workspace)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_preview_plans_without_any_filesystem_change(self) -> None:
        before = inventory(self.workspace)
        manifest, code = task3.run(self.workspace, csv_name="master.csv", apply=False)
        self.assertEqual(code, 0)
        self.assertEqual(manifest["mode"], "preview")
        self.assertEqual(manifest["csv"]["status"], "not_written_in_preview")
        self.assertEqual(before, inventory(self.workspace))
        self.assertFalse((self.workspace / "master.csv").exists())
        moves = {(move["source_path"], move["destination_path"]) for move in manifest["planned_moves"]}
        self.assertIn(("inbound.LOG", "log/inbound.LOG"), moves)
        self.assertIn(("archive.tar.GZ", "gz/archive.tar.GZ"), moves)
        self.assertIn(("readme", "no_extension/readme"), moves)
        self.assertIn((".metadata", "no_extension/.metadata"), moves)
        self.assertIn(("notes.txt", "txt/notes__1.txt"), moves)

    def test_apply_moves_files_preserves_bytes_and_is_idempotent(self) -> None:
        before = inventory(self.workspace)
        manifest, code = task3.run(self.workspace, csv_name="master.csv", apply=True)
        self.assertEqual(code, 0)
        self.assertTrue(manifest["apply"]["complete"])
        self.assertEqual(manifest["csv"]["status"], "written_and_verified")
        self.assertEqual((self.workspace / "log" / "inbound.LOG").read_bytes(), (FIXTURE / "inbound.LOG").read_bytes())
        self.assertEqual((self.workspace / "txt" / "notes__1.txt").read_bytes(), (FIXTURE / "notes.txt").read_bytes())
        self.assertTrue((self.workspace / "no_extension" / ".metadata").is_file())
        after = inventory(self.workspace)
        self.assertEqual(
            sorted(before.values()),
            sorted(value for key, value in after.items() if key != "master.csv"),
        )
        repeat, repeat_code = task3.run(self.workspace, csv_name="master.csv", apply=True)
        self.assertEqual(repeat_code, 0)
        self.assertEqual(repeat["planned_moves"], [])
        self.assertEqual(repeat["apply"]["moves"], [])

    def test_occupied_destination_after_plan_is_truthful_partial_failure(self) -> None:
        plan = task3.plan_organization(self.workspace)
        target = self.workspace / next(move.destination_path for move in plan if move.source_path == "inbound.LOG")
        target.parent.mkdir()
        target.write_text("occupied", encoding="utf-8")
        manifest = task3.apply_plan(self.workspace, plan)
        failed = [item for item in manifest["moves"] if item["source_path"] == "inbound.LOG"]
        self.assertEqual(failed[0]["status"], "failed")
        self.assertEqual(target.read_text(encoding="utf-8"), "occupied")
        self.assertTrue((self.workspace / "inbound.LOG").is_file())

    def test_collision_name_is_deterministic(self) -> None:
        (self.workspace / "report.TXT").write_text("new", encoding="utf-8")
        (self.workspace / "txt").mkdir(exist_ok=True)
        (self.workspace / "txt" / "report.TXT").write_text("old", encoding="utf-8")
        planned = task3.plan_organization(self.workspace)
        destinations = {move.source_path: move.destination_path for move in planned}
        self.assertEqual(destinations["report.TXT"], "txt/report__1.TXT")

    def test_unsafe_roots_traversal_and_symlinks_are_rejected(self) -> None:
        with self.assertRaises(task3.SafetyError):
            task3.validate_workspace(ROOT)
        with self.assertRaises(task3.SafetyError):
            task3.validate_workspace("fixtures/task3/../task3")
        link = self.workspace / "linked.log"
        link.symlink_to(self.workspace / "inbound.LOG")
        with self.assertRaises(task3.SafetyError):
            task3.plan_organization(self.workspace)

    def test_extracts_multiple_matches_line_numbers_and_stable_deduplication(self) -> None:
        records = task3.extract_records(self.workspace)
        tuples = [(record.source_path, record.line_number, record.kind, record.value) for record in records]
        self.assertIn(("inbound.LOG", 2, "email", "demo.alpha@example.test"), tuples)
        self.assertIn(("inbound.LOG", 2, "email", "demo.beta@example.test"), tuples)
        self.assertIn(("inbound.LOG", 2, "transaction_id", "TXN-A1B2C3"), tuples)
        self.assertIn(("notes.txt", 1, "email", "unicode.user@example.test"), tuples)
        self.assertNotIn(("notes.txt", 2, "email", "bad@localhost"), tuples)
        repeated = [row for row in tuples if row == ("notes.txt", 3, "transaction_id", "TXN-ABCDE1")]
        self.assertEqual(len(repeated), 1)
        self.assertEqual(records, task3.extract_records(self.workspace))

    def test_invalid_utf8_is_reported_without_writing_csv(self) -> None:
        (self.workspace / "broken.log").write_bytes(b"\xff\xfe")
        with self.assertRaises(task3.ExtractionError):
            task3.extract_records(self.workspace)
        self.assertFalse((self.workspace / "master.csv").exists())

    def test_csv_has_header_deterministic_rows_and_formula_protection(self) -> None:
        records = [
            task3.Record("notes.txt", 1, "email", "demo.alpha@example.test"),
            task3.Record("=formula.txt", 2, "transaction_id", "=SUM(A1:A2)"),
        ]
        exported = task3.write_master_csv(self.workspace, "master.csv", records)
        self.assertEqual(exported[1]["source_path"], "'=formula.txt")
        self.assertEqual(exported[1]["value"], "'=SUM(A1:A2)")
        with (self.workspace / "master.csv").open("r", encoding="utf-8", newline="") as source:
            rows = list(csv.DictReader(source))
        self.assertEqual(rows[0], {"source_path": "notes.txt", "line_number": "1", "kind": "email", "value": "demo.alpha@example.test"})
        self.assertEqual(rows[1]["value"], "'=SUM(A1:A2)")
        self.assertTrue((self.workspace / "master.csv").read_bytes().startswith(b"source_path,line_number,kind,value\n"))

    def test_empty_records_still_produce_a_header(self) -> None:
        task3.write_master_csv(self.workspace, "master.csv", [])
        self.assertEqual((self.workspace / "master.csv").read_text(encoding="utf-8"), "source_path,line_number,kind,value\n")

    def test_csv_output_path_and_atomic_failure_protect_existing_file(self) -> None:
        old = self.workspace / "master.csv"
        old.write_text("preserved\n", encoding="utf-8")
        with self.assertRaises(task3.SafetyError):
            task3.write_master_csv(self.workspace, "../outside.csv", [])
        with mock.patch("internship.task3.os.replace", side_effect=OSError("simulated replace failure")):
            with self.assertRaises(task3.ExtractionError):
                task3.write_master_csv(self.workspace, "master.csv", [])
        self.assertEqual(old.read_text(encoding="utf-8"), "preserved\n")

    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "internship.task3", *arguments],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_cli_preview_success_and_apply_success(self) -> None:
        before = inventory(self.workspace)
        preview = self.run_cli("--root", str(self.workspace))
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertEqual(json.loads(preview.stdout)["mode"], "preview")
        self.assertEqual(before, inventory(self.workspace))
        applied = self.run_cli("--root", str(self.workspace), "--apply")
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertEqual(json.loads(applied.stdout)["csv"]["status"], "written_and_verified")

    def test_cli_invalid_argument_and_failure_exit_codes(self) -> None:
        invalid_root = self.run_cli("--root", str(ROOT))
        self.assertEqual(invalid_root.returncode, 2)
        self.assertIn("root must be inside", invalid_root.stderr)
        invalid_output = self.run_cli("--root", str(self.workspace), "--apply", "--csv", "../outside.csv")
        self.assertEqual(invalid_output.returncode, 2)
        self.assertIn("CSV output", invalid_output.stderr)
        preview_invalid_output = self.run_cli("--root", str(self.workspace), "--csv", "../outside.csv")
        self.assertEqual(preview_invalid_output.returncode, 2)
        self.assertIn("CSV output", preview_invalid_output.stderr)


if __name__ == "__main__":
    unittest.main()
