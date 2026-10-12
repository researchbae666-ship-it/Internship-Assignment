# Planned test and evidence strategy

## Executed tests

Tasks 2–3 have standard-library unittest coverage. The Phase 3 initial implementation run executed 25 tests and passed: 13 Task 2 tests and 12 Task 3 tests; its summary remains in `evidence/task3/TEST_OUTPUT.txt`. Following the output-safety review corrections, `python -m unittest discover -s tests -v` executed 30 tests and passed: 13 Task 2 tests and 17 Task 3 tests. The review-fix evidence records the full output and source revision. Tests use temporary directories below ignored `artifacts/task3/` and version-controlled synthetic fixtures; no testing dependency is required.

## Task 2

- Exact lists for 0,1,2,10; known 100th term, recurrence and count across representative bounds.
- Negative, float, string, None and bool rejected with specified exception; CLI invalid count yields exit 2 and no success output.
- JSON stdout parses as array; CLI resource cap tested.
- Real small timeit run verifies positive sample counts, units, metadata and numeric timings. No speed threshold; confirm printing is excluded by reviewed timer setup.

## Task 3 executed coverage

- Temporary sandbox with mixed-case extensions, multiple suffixes, no extension, dotfile, duplicate basenames and binary content. Assert destinations and unchanged byte hashes.
- Preview makes no modifications; apply performs exact planned moves; repeat run causes no new moves or duplicate records.
- Test occupied folders, collisions, unsafe roots, symlinks, traversal attempts, destination changes, permissions/I/O failures and partial-outcome reporting. Skip permission scenarios only with explicit reason where host capabilities prevent reproduction.
- Synthetic valid/invalid email and TXN patterns, repeated matches, punctuation, Unicode text, empty/no-match logs, non-UTF-8 input; source line references and deterministic ordering.
- CSV parsed using csv reader: stable schema/header, values, formula protection, newline correctness and atomic-output failure behavior. No real emails or transaction records.

Executed Task 3 coverage adds: preview inventory equality, applied content-hash equality, idempotent repeat apply, multi-suffix/case/dotfile/extensionless paths, deterministic occupied-destination naming, changed-state partial failure reporting, unsafe root/traversal/symlink rejection, strict UTF-8 failure, multiple match line tracing/stable duplicate removal, CSV formula protection/header/readback/atomic-replace failure, and CLI success/error exits.

Review-fix regression coverage additionally proves that `.txt`, `.LOG`, and non-CSV output names fail before planning/moves; the input inventory stays unchanged after rejection; an unrelated existing CSV cannot be overwritten; only a verified generated master with a matching marker/hash can be regenerated; canonical fixture apply/write public functions and CLI apply fail; and isolated artifact copies still apply successfully.

## Task 4 planned coverage

- Case/punctuation/whitespace/Unicode normalization and token-boundary false-positive checks.
- Every mapped intent and every help-tree state; follow-up, ambiguity, cross-tree switch, cancel, reset, bounded history and session independence.
- Unknown/empty input and repeated fallback; exit, EOF and KeyboardInterrupt; unexpected error does not produce a false success exit.
- Scripted CLI integration transcript: help -> task choice -> follow-up -> Python switch -> unknown -> reset -> exit. Assert responses and state transitions, not merely process survival.

## Planned future validation

`python -m unittest discover -s tests -v` followed by each README CLI example in isolated temporary workspaces. Record actual exit codes, test counts and output into ignored artifacts. Re-run affected tests after fixes; complete full relevant suite before phase review. Commands are proposed and have not executed.

## Planned report verification

Generate from recorded executions only. Compare tables/transcripts with raw evidence and source commit. Check PDF text with pdftotext, page count with pdfinfo, render all pages with pdftoppm and visually inspect readability, glyphs, wrapping, pagination and clipping. Confirm all three tasks, limits, actual test counts and benchmark units are included. Never substitute screenshot mockups or fabricated execution output.
