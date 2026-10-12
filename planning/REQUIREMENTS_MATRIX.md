# Requirements matrix

Source inspection: 12 October 2026. Python PDF: one page, extracted using `pdftotext -layout`. All original files read. Tasks 2–3 are implemented and tested; Task 4 remains planned.

| ID | Source requirement | Planned acceptance evidence |
| --- | --- | --- |
| T2.1 | Clean Python function processing integer sequence bounds | Implemented: `fibonacci(count)` exact integer list; tests cover 0, 1, 2, 10, 100, and recurrence |
| T2.2 | Sanitize negative bounds | Implemented: negative integers raise ValueError; bool/float/string/None raise TypeError; CLI errors use exit 2 |
| T2.3 | Structured list arrays | Implemented: Python list return and compact JSON array CLI output |
| T2.4 | Runtime benchmarks using timeit | Implemented: raw repeat samples, counts and runtime metadata originate from `timeit` |
| T3.1 | Standard system libraries for folder automation | Implemented with pathlib/os/re/csv/json/argparse and isolated synthetic-workspace integration tests |
| T3.2 | Sort files into extension subdirectories | Implemented: preview, `--apply`, extension case/multi-suffix/dotfile handling, deterministic collision names, byte checks, repeat-run test |
| T3.3 | Regex extraction from flat logs | Implemented: synthetic email/transaction fixtures, multiple matches, stable deduplication and source/line traceability |
| T3.4 | Clean master CSV | Implemented: stable UTF-8 schema, header-only zero-record output, read-back verification, formula protection and atomic replace |
| T4.1 | Complex terminal loop, modular flows | Real scripted terminal sessions covering multiple intents |
| T4.2 | Case conversion and character stripping | Normalization tests covering mixed case, punctuation, whitespace, Unicode |
| T4.3 | Nested if/elif/else and functional dictionary maps | Explicit state handlers plus callable intent map, transition tests |
| T4.4 | Session variations and graceful fallback | Context changes, reset, unknown input, EOF and interrupt tests |
| S.1 | At least 3 of 4 tasks for certificate (messages) | Tasks 2–4 mapped to actual report evidence; eligibility remains organizer decision |
| S.2 | Combine tasks into ONE PDF (message 2) | One readable PDF, all three task sections, traceable evidence and page inspection |
| S.3 | Google Form only; no late submissions; 18 October 2026 | Checklist and explicit later submission authorization; no confirmation fabricated |
| D.1 | User: preserve documents; Phase 1 only | Git diff confirms originals unchanged; no implementation or task execution claims |

## Proposed interpretations requiring Phase 1 review

- Fibonacci bounds mean number of terms: n=0 gives [], n=1 gives [0], n=2 gives [0,1]. The PDF does not specify count versus maximum value; count is the proposed explicit contract.
- Log extraction will demonstrate both synthetic email addresses and `TXN-` IDs. The PDF gives examples, not a mandatory production log grammar.
- Chatbot help trees will cover task guidance, Python concepts, and submission guidance. No external APIs, accounts, personal data, or organizer claims.
- “Background automation” will be a noninteractive batch utility suitable for scheduling. Installing a persistent daemon is not required by the PDF.
- “Production-ready” will mean documented safe behavior, deterministic routing, validation, failure handling, and tested terminal operation within this assignment scope; no scalability or production-deployment claim.
