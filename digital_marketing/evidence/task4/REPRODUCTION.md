# Task 4 reproduction

Run from the repository root:

```bash
python digital_marketing/research/task4/build_strategy.py
python digital_marketing/research/task4/test_strategy.py
python digital_marketing/tools/test_generate_task4_report.py
python digital_marketing/tools/generate_task4_report.py
python -m unittest discover -s tests -v
pdfinfo digital_marketing/deliverables/DM_Task4_SEO_Acquisition_Strategy.pdf
pdftotext digital_marketing/deliverables/DM_Task4_SEO_Acquisition_Strategy.pdf /tmp/task4-report.txt
pdftoppm -png -r 144 digital_marketing/deliverables/DM_Task4_SEO_Acquisition_Strategy.pdf /tmp/task4-page
```

The strategy build rejects incomplete SEO rows, missing keyword intents, budget
mismatches, missing funnel/email stages, invalid financial denominators, and
inconsistent CPM/CTR/session/conversion/CAC/ROAS arithmetic. The PDF generator
reruns strategy validation before writing the report.
