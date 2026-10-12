# Progree Python internship assignment

Task 2 (Fibonacci) is implemented and ready for independent review. Tasks 3 and 4 remain unimplemented and require separate approval. The deadline is **18 October 2026**; its exact time and timezone are unconfirmed. Task 1 is optional and deferred.

## Current status

Phase 2 Task 2 is implemented, tested, demonstrated, and benchmarked with genuine local evidence in `evidence/task2/`. The Python PDF is authoritative; the Digital Marketing document is context only. Original documents remain unchanged. Task 3, Task 4, and the final report/PDF are not started.

## Planned programs and usage

Use Python 3.12 or newer from the existing cloud checkout. Task 2 commands are implemented:

```bash
python -m internship.task2 --count 10
python -m internship.task2 --count 0
python -m internship.task2 --benchmark --benchmark-counts 10 100 1000 --repeats 5 --number 100
python -m unittest discover -s tests -v
```

`fibonacci(count)` returns exactly `count` terms, beginning `0, 1`. It accepts only non-negative plain integers; `bool`, float, string, and `None` are rejected. The CLI emits a JSON array for a sequence and JSON benchmark data for `--benchmark`; validation errors go to stderr with exit code 2. CLI output is limited to 10,000 terms. Benchmarking uses `timeit` to measure only `fibonacci(count)`, excluding printing, JSON encoding, and metadata collection. It reports sample totals and per-call min/median in seconds, plus Python and platform context. Timings vary by machine and are not performance guarantees.

The iterative algorithm performs O(count) loop steps and stores O(count) terms. Because Python integers have arbitrary precision, additions grow more expensive as Fibonacci values grow; the simplified constant-cost arithmetic assumption does not hold for large counts.

Task 3 will preview/apply safe extension organization and extract log patterns into CSV. Task 4 will provide a terminal chatbot with multiple help trees and session memory. Neither command is implemented yet.

## Planned deliverables

Task 2 source, real automated tests, reproducible CLI demonstrations, raw ignored output in `artifacts/`, and sanitized reviewable evidence in `evidence/task2/` are present. Future deliverables are synthetic fixtures, Task 3/4 source and tests, and one professional PDF covering Tasks 2–4. All report results must be traceable to genuine executions. No personal information or credentials belong in this repository.

Read [master plan](planning/MASTER_PLAN.md), [requirements](planning/REQUIREMENTS_MATRIX.md), [architecture](planning/ARCHITECTURE.md), [tests](planning/TEST_STRATEGY.md), [submission checklist](planning/SUBMISSION_CHECKLIST.md), [cloud environment](planning/CLOUD_ENVIRONMENT.md), and [status](planning/STATUS.md). Project rules are in [AGENTS.md](AGENTS.md).

The Google Form requires a separate authorized submission step. No submission or LinkedIn action has been performed.
