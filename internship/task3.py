"""Task 3: safe synthetic-workspace file organization and log extraction.

This utility intentionally refuses arbitrary user directories. Its CLI accepts only
non-symlink directories below this repository's ``fixtures/task3`` or
``artifacts/task3`` workspaces. Preview is the default; ``--apply`` is required for
any move or CSV write.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
APPROVED_WORKSPACES = (REPOSITORY_ROOT / "fixtures" / "task3", REPOSITORY_ROOT / "artifacts" / "task3")
TEXT_EXTENSIONS = {".log", ".txt"}
CSV_FIELDS = ("source_path", "line_number", "kind", "value")
EMAIL_PATTERN = re.compile(
    r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+"
)
TRANSACTION_PATTERN = re.compile(r"\bTXN-[A-Z0-9]{6,12}\b")


class Task3Error(Exception):
    """Expected, user-facing Task 3 failure."""


class SafetyError(Task3Error):
    """Unsafe path or symlink detected."""


class ExtractionError(Task3Error):
    """A relevant log could not be extracted safely."""


@dataclass(frozen=True)
class PlannedMove:
    source_path: str
    destination_path: str


@dataclass(frozen=True)
class Record:
    source_path: str
    line_number: int
    kind: str
    value: str


def _is_below(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _has_symlink_component(path: Path) -> bool:
    """Return True when an existing component from the repo down is a symlink."""
    try:
        relative = path.absolute().relative_to(REPOSITORY_ROOT)
    except ValueError:
        return True
    current = REPOSITORY_ROOT
    for part in relative.parts:
        current /= part
        if current.exists() and current.is_symlink():
            return True
    return False


def validate_workspace(root: str | Path) -> Path:
    """Resolve and validate a dedicated synthetic workspace directory."""
    requested = Path(root)
    if ".." in requested.parts:
        raise SafetyError("path traversal ('..') is not allowed")
    if requested.is_symlink() or _has_symlink_component(requested):
        raise SafetyError("workspace and its repository-relative path components must not be symlinks")
    if not requested.is_dir():
        raise SafetyError("root must be an existing directory")
    resolved = requested.resolve(strict=True)
    if not any(_is_below(resolved, workspace.resolve()) for workspace in APPROVED_WORKSPACES):
        raise SafetyError("root must be inside fixtures/task3 or artifacts/task3")
    return resolved


def _safe_immediate_files(root: Path, *, excluded_names: set[str] | None = None) -> list[Path]:
    excluded_names = excluded_names or set()
    files: list[Path] = []
    for child in sorted(root.iterdir(), key=lambda item: (item.name.casefold(), item.name)):
        if child.name in excluded_names:
            continue
        if child.is_symlink():
            raise SafetyError(f"symlink is not allowed: {child.name}")
        if child.is_file():
            files.append(child)
    return files


def _bucket_for(source: Path) -> str:
    suffix = source.suffix.casefold()
    return suffix[1:] if suffix else "no_extension"


def _collision_free_destination(root: Path, source: Path, reserved: set[Path]) -> Path:
    destination_dir = root / _bucket_for(source)
    if destination_dir.exists() and destination_dir.is_symlink():
        raise SafetyError(f"destination directory is a symlink: {destination_dir.name}")
    candidate = destination_dir / source.name
    index = 1
    while candidate.exists() or candidate.is_symlink() or candidate in reserved:
        suffix = source.suffix
        stem = source.name[: -len(suffix)] if suffix else source.name
        candidate = destination_dir / f"{stem}__{index}{suffix}"
        index += 1
    return candidate


def plan_organization(root: str | Path, *, exclude_names: set[str] | None = None) -> list[PlannedMove]:
    """Plan deterministic moves of immediate regular files without changing the filesystem."""
    workspace = validate_workspace(root)
    reserved: set[Path] = set()
    moves: list[PlannedMove] = []
    for source in _safe_immediate_files(workspace, excluded_names=exclude_names):
        destination = _collision_free_destination(workspace, source, reserved)
        reserved.add(destination)
        moves.append(
            PlannedMove(
                source_path=source.relative_to(workspace).as_posix(),
                destination_path=destination.relative_to(workspace).as_posix(),
            )
        )
    return moves


def apply_plan(root: str | Path, moves: Iterable[PlannedMove]) -> dict[str, Any]:
    """Apply planned moves without overwriting; report every completed or failed move."""
    workspace = validate_workspace(root)
    outcomes: list[dict[str, str]] = []
    for move in moves:
        source = workspace / move.source_path
        destination = workspace / move.destination_path
        try:
            if source.parent != workspace or not source.is_file() or source.is_symlink():
                raise SafetyError("source is no longer an immediate regular file")
            if not _is_below(destination, workspace) or destination.parent.parent != workspace:
                raise SafetyError("destination is outside an immediate extension directory")
            if destination.parent.exists() and destination.parent.is_symlink():
                raise SafetyError("destination directory is a symlink")
            destination.parent.mkdir(exist_ok=True)
            if destination.exists() or destination.is_symlink():
                raise FileExistsError("destination became occupied before move")
            # link() fails if the destination appears between the preceding check and
            # this operation, preventing an accidental overwrite. unlink() then turns
            # the same-filesystem hard link into a move.
            os.link(source, destination)
            try:
                source.unlink()
            except OSError as error:
                outcomes.append({"source_path": move.source_path, "destination_path": move.destination_path, "status": "partial", "detail": f"destination linked but source retained: {error}"})
            else:
                outcomes.append({"source_path": move.source_path, "destination_path": move.destination_path, "status": "completed"})
        except (OSError, SafetyError) as error:
            outcomes.append({"source_path": move.source_path, "destination_path": move.destination_path, "status": "failed", "detail": str(error)})
    failures = [outcome for outcome in outcomes if outcome["status"] != "completed"]
    return {"moves": outcomes, "failure_count": len(failures), "complete": not failures}


def _safe_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for child in sorted(root.iterdir(), key=lambda item: (item.name.casefold(), item.name)):
        if child.is_symlink():
            raise SafetyError(f"symlink is not allowed: {child.name}")
        if child.is_file() and child.suffix.casefold() in TEXT_EXTENSIONS:
            files.append(child)
        elif child.is_dir():
            if child.is_symlink():
                raise SafetyError(f"symlink is not allowed: {child.name}")
            for nested in sorted(child.iterdir(), key=lambda item: (item.name.casefold(), item.name)):
                if nested.is_symlink():
                    raise SafetyError(f"symlink is not allowed: {nested.relative_to(root).as_posix()}")
                if nested.is_file() and nested.suffix.casefold() in TEXT_EXTENSIONS:
                    files.append(nested)
    return files


def extract_records(root: str | Path) -> list[Record]:
    """Extract deterministically ordered synthetic email and transaction records."""
    workspace = validate_workspace(root)
    seen: set[tuple[str, int, str, str]] = set()
    records: list[Record] = []
    for text_file in _safe_text_files(workspace):
        relative = text_file.relative_to(workspace).as_posix()
        try:
            lines = text_file.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError as error:
            raise ExtractionError(f"UTF-8 decoding failed for {relative}: {error.reason}") from error
        except OSError as error:
            raise ExtractionError(f"could not read {relative}: {error}") from error
        for line_number, line in enumerate(lines, start=1):
            matches = [(match.start(), "email", match.group()) for match in EMAIL_PATTERN.finditer(line)]
            matches += [(match.start(), "transaction_id", match.group()) for match in TRANSACTION_PATTERN.finditer(line)]
            for _, kind, value in sorted(matches, key=lambda item: (item[0], item[1], item[2])):
                key = (relative, line_number, kind, value)
                if key not in seen:
                    seen.add(key)
                    records.append(Record(*key))
    return records


def _sanitize_cell(value: str) -> str:
    return f"'{value}" if value[:1] in {"=", "+", "-", "@"} else value


def _export_record(record: Record) -> dict[str, str | int]:
    return {
        "source_path": _sanitize_cell(record.source_path),
        "line_number": record.line_number,
        "kind": record.kind,
        "value": _sanitize_cell(record.value),
    }


def _validate_csv_target(workspace: Path, output: str | Path) -> Path:
    """Validate a direct, non-symlinked filename below an approved workspace."""
    requested = Path(output)
    if requested.is_absolute() or ".." in requested.parts or len(requested.parts) != 1:
        raise SafetyError("CSV output must be a filename directly inside the workspace")
    target = workspace / requested
    if target.is_symlink():
        raise SafetyError("CSV output must not be a symlink")
    return target


def write_master_csv(root: str | Path, output: str | Path, records: Iterable[Record]) -> list[dict[str, str | int]]:
    """Atomically write and read back a sanitized master CSV inside a workspace."""
    workspace = validate_workspace(root)
    target = _validate_csv_target(workspace, output)
    exported = [_export_record(record) for record in records]
    temporary_name: str | None = None
    try:
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=workspace, prefix=".task3-", suffix=".tmp", delete=False) as temporary:
                temporary_name = temporary.name
                writer = csv.DictWriter(temporary, fieldnames=CSV_FIELDS, lineterminator="\n")
                writer.writeheader()
                writer.writerows(exported)
            os.replace(temporary_name, target)
            temporary_name = None
        except OSError as error:
            raise ExtractionError(f"could not safely write {target.name}: {error}") from error
    finally:
        if temporary_name:
            Path(temporary_name).unlink(missing_ok=True)
    with target.open("r", encoding="utf-8", newline="") as csv_file:
        read_back = list(csv.DictReader(csv_file))
    expected = [{key: str(row[key]) for key in CSV_FIELDS} for row in exported]
    if read_back != expected:
        raise ExtractionError("CSV read-back verification did not match exported records")
    return exported


def run(root: str | Path, *, csv_name: str, apply: bool) -> tuple[dict[str, Any], int]:
    """Run a preview or apply workflow and return its manifest and exit status."""
    workspace = validate_workspace(root)
    _validate_csv_target(workspace, csv_name)
    plan = plan_organization(workspace, exclude_names={csv_name})
    plan_manifest = [asdict(move) for move in plan]
    if not apply:
        records = extract_records(workspace)
        return {
            "mode": "preview",
            "workspace": workspace.relative_to(REPOSITORY_ROOT).as_posix(),
            "planned_moves": plan_manifest,
            "records": [asdict(record) for record in records],
            "csv": {"status": "not_written_in_preview"},
        }, 0

    apply_manifest = apply_plan(workspace, plan)
    if not apply_manifest["complete"]:
        return {
            "mode": "apply",
            "workspace": workspace.relative_to(REPOSITORY_ROOT).as_posix(),
            "planned_moves": plan_manifest,
            "apply": apply_manifest,
            "csv": {"status": "not_written_after_partial_failure"},
        }, 1
    records = extract_records(workspace)
    exported = write_master_csv(workspace, csv_name, records)
    return {
        "mode": "apply",
        "workspace": workspace.relative_to(REPOSITORY_ROOT).as_posix(),
        "planned_moves": plan_manifest,
        "apply": apply_manifest,
        "records": [asdict(record) for record in records],
        "csv": {"status": "written_and_verified", "path": csv_name, "record_count": len(exported)},
    }, 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Safely organize a synthetic workspace and extract its log records.")
    parser.add_argument("--root", required=True, help="explicit workspace below fixtures/task3 or artifacts/task3")
    parser.add_argument("--csv", default="master.csv", help="CSV filename written only with --apply")
    parser.add_argument("--apply", action="store_true", help="perform planned moves and write/verify the CSV")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        manifest, exit_code = run(args.root, csv_name=args.csv, apply=args.apply)
    except Task3Error as error:
        print(f"task3: error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
