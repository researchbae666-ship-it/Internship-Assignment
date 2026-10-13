# Requirements matrix

Source inspection: Python PDF extracted using `pdftotext -layout`; the supplied
Digital Marketing brief is available as a Markdown transcription. The approved
Python Tasks 2–4 are implemented and tested. Digital Marketing Tasks 2–4 are
planned only under the dual-track scope activated on 13 October 2026.

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
| T4.1 | Complex terminal loop, modular flows | Implemented: interactive local terminal loop, three help trees, real scripted subprocess conversations |
| T4.2 | Case conversion and character stripping | Implemented: NFKC/casefold/punctuation/whitespace normalization with Unicode tests |
| T4.3 | Nested if/elif/else and functional dictionary maps | Implemented: callable intent map plus nested pending-choice state handlers |
| T4.4 | Session variations and graceful fallback | Implemented: context switches, bounded in-memory history, reset/cancel, ambiguity, unknown, EOF, interrupt, and internal-error tests |
| S.1 | At least 3 of 4 tasks for certificate (messages) | Tasks 2–4 mapped to actual report evidence; eligibility remains organizer decision |
| S.2 | Combine tasks into ONE PDF (message 2) | Implemented: `deliverables/Progree_Python_Tasks_2_3_4.pdf`; 14 A4 pages, text extraction and 14-page render verification recorded in `evidence/phase5/outputs/pdf-qa.json` |
| S.3 | Google Form only; no late submissions; 18 October 2026 | Submission checklist records later human authorization/access requirements; no submission confirmation fabricated |
| D.1 | User: preserve documents | Fresh Phase 5 SHA-256 check confirms all four originals match approved commit `31cf193d4bf3b8e0c822875e6b4ba80f4f7d0a3d` |

## Digital Marketing & Branding — planned evidence matrix

| ID | Source requirement | Required evidence and completion criterion | Current state |
| --- | --- | --- | --- |
| DM2.1 | Audit three competing consumer brands | Sector rationale, three profiles, public source URLs/dates, comparable observation window | Evidence-blocked; no metrics collected |
| DM2.2 | Analyze cadence, engagement, and brand position | Observable post records, transparent rate formulas or unavailable labels, visual/theme comparison | Evidence-blocked |
| DM2.3 | Identify gaps and recommendations (3–4 pages) | Findings traceable to observations; practical recommendations separated from facts | Evidence-blocked |
| DM3.1 | 30-day integrated campaign | Product rationale, personas, positioning, target KPI assumptions, complete editorial matrix | Complete; independently approved |
| DM3.2 | Instagram, LinkedIn, and YouTube execution | Channel-specific asset, copy, CTA, targeting, hashtags/keywords, owner, KPI per scheduled action | Complete; independently approved |
| DM3.3 | Paid and optimization plan | Proposed allocations, testing/measurement/risk plan; no launched campaign or achieved result claim | Complete; independently approved |
| DM4.1 | Enterprise search strategy for target startup | Public website observation log, intent clusters, long-tail research provenance and prioritization | Complete; awaiting independent review |
| DM4.2 | On-page SEO map | Proposed titles, metas, URL, headers, pillars, internal links; actual versus recommended clearly separated | Complete; awaiting independent review |
| DM4.3 | Growth acquisition funnel | Proposed funnel, landing/conversion events, email drip, model formulas/assumptions and sensitivity | Complete; awaiting independent review |
| DM-S.1 | Shared notice: at least three of four tasks | Tasks 2–4 must each reach independently reviewed completion; certificate remains organizer decision | Pending |
| DM-S.2 | Shared notice: one PDF | Future Marketing PDF; optional combined portfolio only after organizer clarification | Pending |

## Proposed interpretations requiring Phase 1 review

- Fibonacci bounds mean number of terms: n=0 gives [], n=1 gives [0], n=2 gives [0,1]. The PDF does not specify count versus maximum value; count is the proposed explicit contract.
- Log extraction will demonstrate both synthetic email addresses and `TXN-` IDs. The PDF gives examples, not a mandatory production log grammar.
- Chatbot help trees will cover task guidance, Python concepts, and submission guidance. No external APIs, accounts, personal data, or organizer claims.
- “Background automation” will be a noninteractive batch utility suitable for scheduling. Installing a persistent daemon is not required by the PDF.
- “Production-ready” will mean documented safe behavior, deterministic routing, validation, failure handling, and tested terminal operation within this assignment scope; no scalability or production-deployment claim.
