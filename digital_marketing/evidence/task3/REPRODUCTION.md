# Task 3 reproduction and QA

Run these commands from the repository root:

```bash
python digital_marketing/research/task3/build_campaign.py
python digital_marketing/research/task3/test_campaign.py
python digital_marketing/tools/generate_task3_report.py
pdfinfo digital_marketing/deliverables/DM_Task3_30_Day_Campaign.pdf
pdftotext digital_marketing/deliverables/DM_Task3_30_Day_Campaign.pdf /tmp/task3-report.txt
pdftoppm -png -r 144 digital_marketing/deliverables/DM_Task3_30_Day_Campaign.pdf /tmp/task3-page
```

The build script rejects incomplete actions, missing days/platforms, and a
budget mismatch before writing the calendar. The tests check full 30-day and
platform coverage, every required action field, format mix, arithmetic, and
unsupported-achievement language. The PDF generator revalidates the calendar
before creating the deliverable.
