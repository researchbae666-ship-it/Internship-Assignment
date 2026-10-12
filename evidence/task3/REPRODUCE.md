# Reproduce Task 3 evidence

Run from the repository root. Use an empty directory created below `artifacts/task3`; the utility rejects arbitrary locations and allows writes only below that directory by design. See [REVIEW_FIX_REPRODUCE.md](REVIEW_FIX_REPRODUCE.md) for the current output-safety controls.

```bash
demo_root=$(mktemp -d -p artifacts/task3 task3-demo-XXXXXX)
cp -a fixtures/task3/. "$demo_root/"
python -m internship.task3 --root "$demo_root"
python -m internship.task3 --root "$demo_root" --apply --csv master.csv
python -m internship.task3 --root "$demo_root" --apply --csv master.csv
python -m unittest discover -s tests -v
```

The first command is preview-only. The second command organizes seven immediate files, writes `master.csv`, and verifies it by reading it back. The third is the idempotency check: it plans zero moves. Actual evidence values are in the committed manifests and CSV. Do not point this program at a personal or non-synthetic directory: it will reject it.
