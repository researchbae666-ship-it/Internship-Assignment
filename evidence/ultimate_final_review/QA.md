# Final PDF and package QA

## Scope and outcome

This review starts from reviewed commit `e421f1b3286eb8ffcc913d33f5185957a87dfb27` on branch `submission/ultimate-final-audit`. It independently reviewed both approved PDFs, the four Marketing source PDFs, current task code/tests, task instructions, planning records, and official submission-message records.

| Track | Approved PDF | Final candidate | Technical result |
| --- | --- | --- | --- |
| Python | 14 pages, 28,500 bytes, `e967cec21cf744823ff25fc1dab9ba2a2486fa1b7e23f6ceb945fecfd2801db0` | 14 pages, 29,886 bytes, `8910c0aafccb8a575affc9794291b5c9910a23cfebdda3fa6b873c485bece284` | PASS |
| Marketing | 38 pages, 140,895 bytes, `24a211ea4cdd68f83b02ce216aa43b15bc6a65a5952776cbe8c57bccda9f0059` | 38 pages, 140,592 bytes, `571f801e92fd496b27dc8bcd1fb40066d22068f35b783ba2e151f36b7335bb5a` | CONDITIONAL PASS: technical pass; Task 2 acceptance remains external. |

## Rendered-page inspection

`pdftoppm` rendered all approved pages at 180 DPI: 38 Marketing plus 14 Python. Each of those 52 pages was individually reviewed, including dense tables, campaign calendar pages, financial tables, code excerpts, cover/contents, and Marketing portrait/landscape boundaries. All 52 final-candidate pages were freshly rendered at the same resolution. Candidate images are pixel-equal to their approved equivalent on all 52 page pairs.

Results:

- No unexpectedly blank or non-extractable pages.
- No clipping, text overlap, corrupt glyph, margin, contrast, footer, page-break, or table-header defect found.
- Marketing page dimensions/orientations are retained exactly across the cover/contents and landscape report pages.
- Body text, tables, scripts, code blocks, currency/symbol glyphs, and footers are readable at normal document viewing scale.
- The visual regression result does not rely only on structure checks: the inspection record is `render_review.json` and its temporary render output is reproducible with `python tools/record_render_inspection.py`.

## Content, navigation and link checks

- All 36 Marketing source-report pages match their pages in the approved combined PDF by decompressed content stream, extracted text, and page dimensions.
- Both candidates preserve every source page's text, content stream, dimensions, and rotation.
- Marketing candidate outline order: Cover p1; Contents p2; evidence-limited Task 2 p3; RefillLoop Task 3 p7; Ocean Bottle Task 4 p27; email appendix p33. Its page labels match these sections.
- Python candidate outline order: Cover p1; executive summary p2; Tasks 2, 3 and 4 at pp. 3, 6 and 9; QA p12; conclusion p13; appendix p14. Its page labels match these sections.
- The approved sources contained no URI annotations. The Marketing candidate intentionally adds 11 annotations only where the exact public URL and exact visible rectangle are verified. Long line-wrapped source URLs remain plain text rather than receiving an unsafe guessed annotation. Python has no visible external URLs that require annotation.

## Claim and privacy checks

- Task 2 is labelled an evidence-limited public-source audit. It does not claim verified 28-day cadence, post-level engagement, complete platform inventory, or organizer approval.
- Task 3 is a fictional RefillLoop campaign. It does not claim publishing, spend, customers, or performance.
- Task 4 is a proposed/modelled Ocean Bottle strategy. It distinguishes public-page observation from recommendations and modelled financial output; it does not claim actual campaign or customer performance.
- Privacy scan passes: no unknown personal email/phone, secret, private identifier, offer letter, signature, credential, JavaScript, encryption, or metadata leak was found. Public brand URLs and `example.test` fixtures are legitimate.

## Test execution

Raw stdout/stderr logs and exact commands are in `logs/`; structured results are in `test_results.json`.

| Suite or validator | Outcome | Tests |
| --- | ---: | ---: |
| Python root unit discovery | Pass | 55 |
| Marketing Task 2 handoff / recovery / secondary | Pass | 6 / 15 / 8 |
| Marketing Task 3 | Pass | 11 |
| Marketing Task 4 | Pass | 28 |
| Marketing report presentation | Pass | 6 |
| Candidate build and fidelity validation | Pass | validator |
| Adversarial synthetic checks | Pass | validator |

Total unit tests: **129**. Failed: **0**. Skipped: **0**. The historical combined-PDF builder was exercised through the adversarial harness with both its output and manifest redirected into a temporary directory, avoiding regeneration of the protected output.

## Open conditions

Technical readiness does not confirm certificate eligibility. Marketing remains conditional until the organizer accepts Task 2's limited evidence or asks for further evidence. The official message gives the date 18 October 2026 but not an exact cutoff time/timezone, form upload specifications, form accessibility, or separate-track submission arrangement. Final owner authorization remains outstanding.
