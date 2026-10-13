# Proposed technical architecture

> **Dual-track update — 13 October 2026:** Approved Python architecture remains
> in place. `python/` adds only compatibility-safe workstream guidance, while
> `digital_marketing/` holds separate research/evidence/deliverable areas. See
> `DUAL_TRACK_MASTER_PLAN.md`; no Python application architecture changed.

All interfaces below are specifications, not implemented features.

## Layout

`internship/task2.py`, `internship/task3.py`, `internship/task4.py`, `tests/`, `fixtures/task3/`, `fixtures/chatbot/`, `tools/generate_report.py`, ignored `artifacts/`, reviewed `deliverables/`. Standard library program dependencies; ReportLab only for reporting. No web service or external API.

## Task 2: Fibonacci module

`fibonacci(count: int) -> list[int]`: reject bool and non-int with TypeError; reject negatives with ValueError. Produce exactly count terms starting 0,1 using iteration and Python arbitrary-precision integers. Do not silently coerce decimals or truncate values. API has no arbitrary upper bound; CLI defaults to 10 and caps requested count at 10000 to limit output/resource use, with a clear validation error. JSON list goes to stdout; diagnostics to stderr; exit 0 on success and 2 for invalid CLI input.

Benchmark mode uses `timeit.Timer` on generation only, excluding printing and fixture creation. Counts 10,100,1000 by default; 5 repeats with 100 calls each. Preserve sample totals in seconds and derived per-call minimum/median, repeat/number/count, Python/platform metadata. All values originate in executed timeit calls. Validate configurable counts/repeat/number as positive, except generation supports zero. State timing variability and do not assert absolute performance thresholds. Loop arithmetic iterations are O(n); memory/output is O(n) integers, with growing integer bit sizes making bit-operation cost greater than constant per iteration.

## Task 3: safe organization and parsing

`plan_organization(root)`, `apply_plan(root, moves)`, `preflight_text_decoding(root)`, `extract_records(root)`, `write_master_csv(root, output, records)`. Explicit root required; default preview makes no directory/content changes. `--apply` opts into moves. Preview may inspect the version-controlled `fixtures/task3` source material, but all public apply/write paths require a proper isolated child directory under `artifacts/task3`; reject the artifacts parent itself, repository root, home, system roots, canonical-fixture writes, symlink roots, symlink files and destination links. Before any apply moves, decode all relevant current `.log`/`.txt` files as UTF-8; this reduces malformed-input partial operations but does not promise atomic behavior against later filesystem changes. Never operate on personal directories. Scan only immediate regular files; existing subdirectories stay untouched. Lowercase last suffix determines folder (e.g. archive.tar.gz -> gz); extensionless and dotfiles -> no_extension. Reject unsuitable destination paths. Stable sorted traversal.

No overwrite: deterministic collision suffix `name__1.ext`, etc., including existing files and planned moves. Recheck conflicts immediately before moving; abort/report changed state. Use same-filesystem rename where possible; report permission or I/O failures with nonzero exit and an actual per-file outcome manifest. Never describe partial moves as success or claim transactional rollback. A second run sees no top-level eligible files and must not create duplicate extraction rows.

Read only `.log` and `.txt` files from top level and recognized organization folders, not unrelated recursive trees; UTF-8 strict decoding; binary files organized but not parsed. Fail decoding clearly, retain original bytes, identify affected relative path and do not claim a complete CSV. Regex email grammar targets conventional ASCII local parts and dotted domains; not a full RFC validator. Transaction grammar: `\bTXN-[A-Z0-9]{6,12}\b`. Match original text, case-sensitive IDs, preserving matched values; deterministic source/line/match ordering and duplicate key `(source_path,line_number,kind,value)` removal.

CSV columns: `source_path,line_number,kind,value`; line numbers are 1-based, paths root-relative, kinds `email`/`transaction_id`. Record post-organization paths after apply, current paths in preview. Require a direct `.csv` filename, header even for zero matches, and UTF-8 `csv.DictWriter` output. Existing CSVs are rejected unless a non-symlinked Task 3 marker verifies the same output filename and SHA-256, which is the only regeneration path. Replace CSV atomically from a sibling temporary file; validate target/marker before planning moves; sanitize formula-leading cells in CSV export while retaining exact raw matches in JSON evidence. Return a manifest with mappings, skipped files and failures; use synthetic logs only. Batch execution can be scheduled later without a daemon.

## Task 4: terminal chatbot

`normalize(text)`, `detect_intent(text,state)`, `handle_turn(text,session)`, `run_cli(input_fn,output_fn)`. Normalize with Unicode NFKC, casefold, punctuation removal and whitespace collapse; preserve Unicode letters/digits, never use eval/exec. Help trees: tasks (2/3/4 explanations), Python (lists/loops/regex), submission (PDF/deadline and explicit unverified access warning). Callable dictionary maps dispatch intents; nested if/elif/else handles follow-up state within trees.

Session state: current_tree, pending_choice, last_intent, turn_count, bounded history of 20 normalized synthetic turns. Memory is in-process only, never saved by default. Priorities: exit, reset/cancel, global help, explicit tree/topic, pending follow-up, fallback. Exact tokens/phrases prevent substring matches (e.g. 'this' must not trigger 'hi'). Ambiguous input requests a choice and changes pending_choice, not fabricated intent. Cross-tree input switches context; reset clears context/history, with well-defined next turn count. Empty input offers help; unknown input suggests valid options; repeated failure offers reset. EOF/KeyboardInterrupt ends politely without traceback. Unexpected internal exceptions have a concise error and nonzero exit; do not hide defects as success. No network requests, promises of certificates, identity collection, or actual form submission.

## Evidence and combined PDF

Python report tool consumes genuine evidence JSON/CSV/transcripts, never hardcoded example results. Validate provenance fields and reject absent required results. Evidence manifest: command, relative cwd, UTC timestamp plus displayed client timezone when needed, exit code, Python version, source commit, sanitized output hash, test counts/outcomes. Hash original documents too. Avoid environment dumps, absolute personal paths and user identity.

Report: title/anonymous project identification; contents; assignment/source mapping; Task 2 design, executed examples and real timing table; Task 3 synthetic before/after manifest, extracted CSV and safety results; Task 4 flow diagram, real transcript and state-test evidence; aggregate validation; reproducibility; limitations; submission checklist and references. Target 12–18 pages, adjusted for readable evidence rather than padding. Consistent headings, page numbers, selectable text, readable tables/code; screenshots only from actual runs and only if useful. No name/offer letter until separately authorized. One PDF `deliverables/Progree_Python_Tasks_2_3_4.pdf`; verify parsing, content, page rendering and no clipping before review.
