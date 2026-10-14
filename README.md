# Progree dual-track internship assignment

The repository now maintains two distinct Progree workstreams: **Python
Programming** and **Digital Marketing & Branding**. The Python Tasks 2–4 are
implemented, integrated, and preserved as an approved historical baseline. The
Digital Marketing Tasks 2–4 are active planning scope only; no Marketing task
is claimed complete. The deadline is **18 October 2026**; its exact time and
timezone are unconfirmed. Task 1 is optional and deferred for both tracks.

## Current status

Phase 5 generated and quality-checked [Progree_Python_Tasks_2_3_4.pdf](deliverables/Progree_Python_Tasks_2_3_4.pdf) from fresh, validated local evidence in `evidence/phase5/`. That Python report remains unchanged while dual-track plans are reviewed. The available Digital Marketing brief is now active scope and is governed by the separate dual-track plans. Original documents remain unchanged. No report is a form submission or certificate confirmation.

## Dual-track planning

The `python/` and `digital_marketing/` directories separate future workstream
guidance, research, evidence, and deliverables without relocating approved
Python code. The Digital Marketing plan proposes a reusable-hydration market
context. Initial Task 2 collection was blocked by the cloud proxy, so its
evidence records the actual access failure and contains no invented metrics or
audit conclusions. On 14 October, Task 2 website/profile access partly recovered:
three official websites and Instagram profiles provide source-backed qualitative
comparisons, but no dated posts or period metrics. A
[four-page recovery draft](digital_marketing/deliverables/DM_Task2_Competitor_Audit_RECOVERY_DRAFT.pdf)
and [completion blockers](digital_marketing/research/task2/recovery/COMPLETION_BLOCKERS.md)
record the precise remaining evidence needs. Task 2 is still incomplete.
Task 3 now has a reviewable fictional RefillLoop campaign
roadmap and [PDF](digital_marketing/deliverables/DM_Task3_30_Day_Campaign.pdf).
Its 53 actions each retain a primary keyword, supporting terms, discovery
intent, tags, a platform targeting reference, and distinct proposed copy. The
roadmap also reconciles every paid action to the proposed media budget and
separates low, base, high, and stretch funnel scenarios. It does not represent
a live product or campaign. Task 4 now has an evidence-backed Ocean Bottle SEO
and acquisition strategy at
[DM_Task4_SEO_Acquisition_Strategy.pdf](digital_marketing/deliverables/DM_Task4_SEO_Acquisition_Strategy.pdf).
It separates direct public-page observations from recommended SEO, email, paid
media, and financial-model actions; no campaign data, account data, ranking, or
search-volume claim is implied. Four proposed email workflows now contain ten
fully drafted messages and synthetic routing tests; the
[email appendix](digital_marketing/deliverables/DM_Task4_Email_Workflow_Appendix.pdf)
contains the full scripts. Media CAC/ROAS and all-in acquisition allocations
are separate, and the reviewer-sourced 2019/2018 founding-year discrepancy is
preserved. Read the [dual-track master plan](planning/DUAL_TRACK_MASTER_PLAN.md), [Marketing requirements](planning/DIGITAL_MARKETING_REQUIREMENTS.md), [research plan](planning/DIGITAL_MARKETING_RESEARCH_PLAN.md), [Python enhancement roadmap](planning/PYTHON_ENHANCEMENT_ROADMAP.md), and [submission strategy](planning/DUAL_TRACK_SUBMISSION_STRATEGY.md).

This public repository must never contain an offer letter, identity details,
student ID, contact details, private images, or credentials. Track eligibility
and whether one form response can submit both reports remain organizer questions.

## Planned programs and usage

Use Python 3.12 or newer from the existing cloud checkout. Tasks 2–4 commands are implemented:

```bash
python -m internship.task2 --count 10
python -m internship.task2 --count 0
python -m internship.task2 --benchmark --benchmark-counts 10 100 1000 --repeats 5 --number 100
python -m internship.task3 --root fixtures/task3
python -m internship.task3 --root artifacts/task3/your-synthetic-workspace --apply --csv master.csv
python -m internship.task4
python -m unittest discover -s tests -v
python tools/collect_phase5_evidence.py
python tools/generate_report.py
python tools/verify_pdf.py
```

`fibonacci(count)` returns exactly `count` terms, beginning `0, 1`. It accepts only non-negative plain integers; `bool`, float, string, and `None` are rejected. The CLI emits a JSON array for a sequence and JSON benchmark data for `--benchmark`; validation errors go to stderr with exit code 2. CLI output is limited to 10,000 terms. Benchmarking uses `timeit` to measure only `fibonacci(count)`, excluding printing, JSON encoding, and metadata collection. It reports sample totals and per-call min/median in seconds, plus Python and platform context. Timings vary by machine and are not performance guarantees.

The iterative algorithm performs O(count) loop steps and stores O(count) terms. Because Python integers have arbitrary precision, additions grow more expensive as Fibonacci values grow; the simplified constant-cost arithmetic assumption does not hold for large counts.

Task 3 requires an explicit existing workspace below `fixtures/task3` or `artifacts/task3`; it rejects other roots, `..` traversal, roots/path components that are symlinks, and symlinked children. Preview may inspect fixtures but changes nothing. `--apply` and CSV writes require a proper isolated child directory of `artifacts/task3`; the `artifacts/task3` parent and canonical fixtures are not writable workspaces. `--csv` must be a direct `.csv` filename. An existing CSV is rejected unless it is the unchanged master previously generated by Task 3 and authenticated by its `.task3-generated-csv.json` marker, which permits safe regeneration on repeat runs. Validation happens before planning/moving files.

Apply preflights every relevant `.log`/`.txt` file with strict UTF-8 decoding before it performs moves, then uses collision-safe same-filesystem hard-link/unlink moves and truthfully reports partial failures if later filesystem state changes. It scans only immediate files plus one organization-directory level, extracts synthetic records, and atomically writes/verifies a UTF-8 CSV. Its fixed columns are `source_path,line_number,kind,value`. CSV cells beginning `=`, `+`, `-`, or `@` are prefixed with an apostrophe to prevent spreadsheet formula interpretation. The regexes target conventional ASCII emails and `TXN-` plus 6–12 uppercase alphanumeric characters; they are deliberately not general email/transaction validators.

Task 4 is a local rule-based terminal chatbot. It has task, Python-learning, and submission help trees; Unicode-aware normalization; callable dictionary routing; explicit nested contextual decisions; and bounded in-memory session history. The routing order is exit, reset/cancel, global help, explicit topic switches, pending contextual choices, then fallback. State records the current tree, pending choice, the actual recognized or reported intent for every turn, turn count, and the most recent 20 normalized turns. A second unclear response in a pending tree gives explicit valid choices plus help/reset guidance; a recognized choice or topic switch clears that recovery count. Task 4 follow-ups distinguish operation, intent routing, normalization, and session-state questions from unrelated input. Nothing is saved, submitted, or sent externally. EOF and Ctrl+C end cleanly; unexpected internal errors return exit code 1 with a concise diagnostic.

## Planned deliverables

Tasks 2–4 source, real automated tests, reproducible CLI demonstrations, raw ignored output in `artifacts/`, historical task evidence in `evidence/task2/`, `evidence/task3/`, and `evidence/task4/`, and fresh Phase 5 evidence in `evidence/phase5/` are present. Task 3’s version-controlled `.log` fixtures are explicitly synthetic and are the only `.log` exception in `.gitignore`. The final deliverable is [one professional PDF](deliverables/Progree_Python_Tasks_2_3_4.pdf) covering Tasks 2–4. Its generator validates retained-output SHA-256 digests before it writes the report, and `tools/verify_pdf.py` checks its metadata, text, test claim, and rendered page count. No personal information or credentials belong in this repository.

Read [master plan](planning/MASTER_PLAN.md), [requirements](planning/REQUIREMENTS_MATRIX.md), [architecture](planning/ARCHITECTURE.md), [tests](planning/TEST_STRATEGY.md), [submission checklist](planning/SUBMISSION_CHECKLIST.md), [cloud environment](planning/CLOUD_ENVIRONMENT.md), and [status](planning/STATUS.md). Project rules are in [AGENTS.md](AGENTS.md).

The Google Form requires a separate authorized submission step. No submission or LinkedIn action has been performed.
# Task 2 secondary-source update

The independent reviewer public-source handoff is preserved in
`digital_marketing/research/task2/handoff/`. The new partial report is
`digital_marketing/deliverables/DM_Task2_Competitor_Audit_HANDOFF_DRAFT.pdf`.
Task 2 remains incomplete for measured-audit approval; no social metrics are
invented. Reproduce using
`python digital_marketing/tools/generate_task2_handoff_report.py` and validate
with `python -m unittest discover -s digital_marketing/research/task2/handoff -v`.
Execution records are in `digital_marketing/evidence/task2/handoff/`.

