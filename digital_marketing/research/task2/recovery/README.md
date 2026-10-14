# Task 2 recovery — 14 October 2026

**State: partial evidence-backed draft; period metrics remain blocked.**

The three official websites and Instagram profile text now load. Five official
social links are verified from those websites: three Instagram and two YouTube.
YouTube content is blocked by CONNECT 403; LinkedIn candidates return HTTP 999.
Owala's YouTube candidate and all LinkedIn candidates remain unverified.

No public post URLs, publication dates, likes/comments/reactions or complete
inventories for 15 September–12 October 2026 UTC were recovered. Snapshots from
14 October cannot establish activity in that fixed period. The 12 source-linked
facts support qualitative comparisons only. Missing metrics are JSON null;
zero retained posts does not mean zero account activity.

The draft PDF is `digital_marketing/deliverables/DM_Task2_Competitor_Audit_RECOVERY_DRAFT.pdf`.
It is not a completed measured audit or a final submission. The independent
reviewer handoff has not been supplied in this turn.

## Reproduction

From repository root:

```bash
python digital_marketing/research/task2/recovery/collect_sources.py
python digital_marketing/research/task2/recovery/collect_browser.py
python digital_marketing/research/task2/recovery/build_audit.py
python -m unittest discover -s digital_marketing/research/task2/recovery -v
python digital_marketing/tools/test_task2_recovery_report.py
python digital_marketing/tools/generate_task2_recovery_report.py
```

Collectors make ordinary public GET/browser requests. No credentials, hidden
APIs, CAPTCHA bypass, authenticated session or gate bypass is used. The browser
collector needs installed Playwright and `/usr/bin/chromium`; other collection
and metrics code uses the standard library. PDF generation needs ReportLab.
New responses may change and must be reviewed; the claim validator fails rather
than carrying unsupported quotations into a report.

Original 13 October source/observation/access/evidence files outside recovery/
remain byte-for-byte unchanged. New evidence is under
`digital_marketing/evidence/task2/recovery/`. Raw HTML and screenshots remain in
ignored `artifacts/`; no third-party brand imagery is reproduced in the PDF.
