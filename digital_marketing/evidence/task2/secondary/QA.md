# Secondary-evidence QA — 14 October 2026 UTC

Executed reproduction:
`python digital_marketing/tools/collect_task2_secondary_evidence.py`.
The exact execution revision, commands, timestamps, outcomes and output digests
are in manifest.json. Retained source is the user's inline reviewer note, with
normalized Markdown spacing, not a successful Codex vendor retrieval.

## Executed checks

| Suite | Passed | Failed |
| --- | ---: | ---: |
| New secondary mapping, arithmetic, missing values, provenance and PDF tests | 8 | 0 |
| Existing handoff tests | 6 | 0 |
| Marketing Task 3 campaign | 10 | 0 |
| Marketing Task 4 strategy and email workflows | 28 | 0 |
| Marketing Task 3 PDF style | 1 | 0 |
| Marketing Task 4 PDF style/content | 2 | 0 |
| Existing Task 2 recovery | 15 | 0 |
| Existing Task 2 PDF tests | 3 | 0 |
| Approved Python regression suite | 54 | 0 |
| **Total** | **127** | **0** |

An initial new-test run encountered an import collision between two modules
named metrics. The new module was renamed secondary_metrics before the complete
passing runs above. No approved application was changed or test disabled.

- All 164 protected historical files compared against reviewed commit 319eb71
  remain byte-for-byte unchanged, including prior Task 2 reports/evidence,
  Python software/reports and Marketing Tasks 3 and 4.
- Three ordinary curl vendor requests returned CONNECT 403, exit 56, no origin
  status and no body. Exact URLs and UTC times are in access-results.json.
- All snapshot totals and percentages validated against the supplied note;
  brand handles and source URLs checked. Full precision proxy values retained
  in calculated-metrics.json. No financial assumptions or models changed.
- New PDF: 4 pages, 51,092 bytes. pdfinfo/pdftotext passed; all four pages
  rendered at 110 DPI and individually inspected after final generation.
  Text and tables are readable; white bold headers; no clipped or overlapping
  elements, corrupt glyphs or blank pages. URL wrapping does not change source
  mapping; exact full URLs are in the retained JSON and source note.
- Identity-neutral text and metadata; no offer letter, student identifier,
  personal contacts or credentials added. No live campaign, messages, submission
  or main merge performed.

Final PDF SHA-256:
`7d997791e61c901c1ac7c901c16d4bcc4a70c3e4255f092c166a6afb889d49a3`.

## Completion gate

**Incomplete for unconditional Task 2 approval.** This is a usable openly limited
public-source draft, not a fully measured competitor audit. The reviewer note
does not resolve verified social content patterns, exact 28-day cadence or
cross-platform engagement. Resolution requires a comparable dated post sample
or inventory with public interactions and valid denominators, or explicit
organizer acceptance of the documented limited methodology. Neither is claimed.
