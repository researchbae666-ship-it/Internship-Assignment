# Combined-review PDF reproduction

Run from the repository root with Python 3.12 or newer and the repository's
installed `reportlab` and `pypdf` packages:

```bash
python digital_marketing/tools/generate_combined_review_pdf.py
python digital_marketing/tools/test_generate_combined_review_pdf.py
```

The generator reads only these approved source PDFs and writes the review copy
and machine-readable result manifest:

- `deliverables/DM_Task2_Competitor_Audit_SECONDARY_DRAFT.pdf`
- `deliverables/DM_Task3_30_Day_Campaign.pdf`
- `deliverables/DM_Task4_SEO_Acquisition_Strategy.pdf`
- `deliverables/DM_Task4_Email_Workflow_Appendix.pdf`

It records SHA-256 values before combining, adds an anonymous two-page front
matter section, imports the source pages without rasterization, adds bookmarks
and page labels, and verifies the generated copy. The source PDFs are never
written by this process.
