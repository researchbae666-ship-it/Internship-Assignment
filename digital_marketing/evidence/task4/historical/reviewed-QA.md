# Task 4 quality-control record

| Check | Actual result |
| --- | --- |
| Direct public-source retrieval | Four Ocean Bottle URLs returned HTTP 200; the supplied B Lab directory returned HTTP 403 and was excluded from independent validation |
| Source claim control | Passed; founding year, B Corp directory validation, rankings, volumes, analytics, and performance results are not claimed |
| Keyword and SEO coverage | Passed; 12 intent-labelled keywords and four full on-page map rows |
| Funnel and email coverage | Passed; four acquisition stages and four consent-aware email flows with exit rules |
| Budget and financial model | Passed; GBP 12,000 total and GBP 10,000 media allocation reconcile; low/base/high formulas and zero-denominator rejection tested |
| Strategy tests | Passed; 10 standard-library tests, 0 failures |
| PDF header-style test | Passed; 1 test confirms dark table headers use explicit white bold Paragraph styles |
| Approved Python suite | Passed; 54 standard-library tests, 0 failures |
| PDF output | Passed; six A4-landscape pages, 17,893 bytes |
| Text extraction | Passed; all six required report sections present |
| Render inspection | Passed; six pages rendered at 144 DPI and inspected; no clipping, contrast issue, corruption, or blank page found |
| Privacy check | Passed; no participant identity, offer letter, credentials, or private material included |

The PDF SHA-256 is `63cc5525f151ba36aef0b92defde15382adf7ef17cdc2c3eec21c1c7182a2f5c`.
Raw page records and command output are retained under ignored `artifacts/` paths.
