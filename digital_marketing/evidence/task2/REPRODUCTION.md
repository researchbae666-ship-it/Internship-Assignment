# Reproduction and QA

Run from the repository root after network access to the listed public domains
is available:

```bash
python digital_marketing/research/task2/calculate_metrics.py \
  digital_marketing/research/task2/observations.json \
  --output digital_marketing/evidence/task2/metrics_summary.json
python -m json.tool digital_marketing/research/task2/observations.json >/dev/null
python -m json.tool digital_marketing/evidence/task2/metrics_summary.json >/dev/null
```

Before a final report, independently check every account and post URL, date,
numerator, denominator, formula result, and report/table reference against the
source registry. Check that no private identity appears in committed files.
