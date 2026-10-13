# Task 4 reproduction

Run from the repository root:

```bash
python digital_marketing/research/task4/build_strategy.py
python digital_marketing/research/task4/test_strategy.py
python -m unittest discover -s digital_marketing/research/task4 -v
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

For a complete fresh review record (including workflow tests, the approved
Python suite, actual command exit codes, PDF metadata, hashes and rendering), run:

```bash
python digital_marketing/tools/collect_task4_review_evidence.py
```

This creates the main report and a separate supporting email appendix. Inspect
every rendered page under `artifacts/digital_marketing/task4_review/` before
updating the visual QA record. The collector preserves the reviewed manifest
and QA in `historical/`; tests and PDF text are retained in `review_outputs/`.
No public-source retrieval is performed or claimed by this correction run.
