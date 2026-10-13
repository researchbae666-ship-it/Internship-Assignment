# Task 3 reproduction and QA

Run these commands from the repository root:

```bash
python digital_marketing/research/task3/build_campaign.py
python digital_marketing/research/task3/test_campaign.py
python -m unittest discover -s tests -v
python digital_marketing/tools/generate_task3_report.py
pdfinfo digital_marketing/deliverables/DM_Task3_30_Day_Campaign.pdf
pdftotext digital_marketing/deliverables/DM_Task3_30_Day_Campaign.pdf /tmp/task3-report.txt
pdftoppm -png -r 144 digital_marketing/deliverables/DM_Task3_30_Day_Campaign.pdf /tmp/task3-page
```

The build script rejects incomplete action data, missing days or platforms,
missing keyword/targeting/copy records, invalid targeting references, paid
pacing mismatches, funnel arithmetic errors, incomplete A/B-test definitions,
and a budget mismatch before it writes the calendar. The dedicated tests cover
30-day and platform coverage, 18 required action fields, discovery strategy,
distinct copy, targeting, format mix, budget and pacing reconciliation, funnel
scenarios, actionable A/B tests, and claim control. The PDF generator reruns
the calendar validation before writing the deliverable.
