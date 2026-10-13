# Task 4 quality-control record

| Check | Actual result |
| --- | --- |
| Historical direct source retrieval | Original four official pages and HTTP 403 B Lab result remain preserved in historical/reviewed-manifest.json; no new source retrieval is claimed |
| Reviewer source provenance | Passed; B Lab certification/2019 and LinkedIn 2018 statements are separately attributed reviewer observations received 13 October 2026; exact collection dates are unavailable and no unqualified year is adopted |
| Keyword and SEO coverage | Passed; 12 intent-labelled keywords and four full on-page map rows |
| Funnel and email coverage | Passed; accepted four-stage funnel unchanged; four workflows contain ten fully drafted messages with timed entry, preview, CTA, event, consent and exits |
| Email routing checks | Passed; every flow tested for ordered completion, duplicate/priority handling, 24h and rolling seven-day caps, consent/suppression, purchase, support pause, inactivity, cart resumption and completion |
| Budget and financial model | Passed; accepted GBP 12,000 budget and all media scenarios unchanged; separate all-in cost per customer is GBP 160.00 / 75.00 / 37.50; ROAS still uses media spend |
| Task 4 strategy and workflow tests | Passed; 28 standard-library tests, 0 failures |
| PDF tests | Passed; 2 tests verify white bold headers and PDF-versus-data correspondence for keywords, years, all-in costs, every subject, preview, full body and CTA |
| Approved Python suite | Passed; 54 standard-library tests, 0 failures |
| Main PDF output | Passed; six A4-landscape analytical pages, 19,192 bytes; main table text increased from 6.65 to 8pt |
| Supporting appendix | Passed; six A4-portrait pages, 13,180 bytes; full scripts rendered at 9pt body size |
| Text extraction | Passed; main and appendix text retained in review_outputs/; tests compare content with machine-readable data |
| Render inspection | Passed; all twelve pages rendered at 144 DPI and inspected in six sheets; dense main SEO page also inspected at full resolution; no clipping, overlap, contrast issue, corruption or blank page found |
| Accepted-work preservation | Passed; keyword/SEO/funnel/budget/observations and original financial fields compare identically with reviewed baseline; Python, Task 3 and blocked Task 2 paths have no changes |
| Privacy check | Passed; no participant identity, offer letter, credentials, or private material included |

Execution source revision: `6bdc2d33e55c7e026e9a3e5024175f3781430045`.
All commands, actual timestamps, exit codes, counts and retained-output hashes
are in `manifest.json`. Full test outputs are in `review_outputs/`; original
reviewed evidence is retained in `historical/`. Renders stay in ignored artifacts.

Main PDF SHA-256:
`c61cc2d5268f8b7691e433a427bda44dcda83171fd399e414e8d04b2129d1ce9`.

Supporting appendix SHA-256:
`56be92ee96117ccc4dac08dcc512efd0eca2ebbc36ca8ad2092e4099f47becf5`.

These are inactive campaign proposals. Upstream qualifying events, account
integration, factual product instructions and real consent/link handling need
separate authorized implementation. No email was sent or campaign activated.
