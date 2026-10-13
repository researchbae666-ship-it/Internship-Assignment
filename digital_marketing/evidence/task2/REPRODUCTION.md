# Reproduction and QA

Run from the repository root after network access to the listed public domains
is available. First record the source-access result; a failure is evidence and
must not be treated as a successful collection:

```bash
for url in \
  https://www.stanley1913.com/ \
  https://www.hydroflask.com/ \
  https://owalalife.com/ \
  https://www.instagram.com/ \
  https://www.linkedin.com/ \
  https://www.youtube.com/; do
  curl -L --max-time 20 -sS -o /dev/null \
    -w 'http_status=%{http_code} effective_url=%{url_effective}\n' "$url"
done
```

Then run the calculation only after populating verified observations:

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
