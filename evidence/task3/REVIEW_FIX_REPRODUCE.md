# Reproduce the Task 3 review fix

Run from the repository root. Create a temporary copy below `artifacts/task3`; `--apply` against `fixtures/task3` is deliberately rejected.

```bash
demo_root=$(mktemp -d -p artifacts/task3 task3-fix-demo-XXXXXX)
cp -a fixtures/task3/. "$demo_root/"
python -m internship.task3 --root "$demo_root"
python -m internship.task3 --root "$demo_root" --apply --csv master.csv
python -m internship.task3 --root "$demo_root" --apply --csv master.csv
python -m internship.task3 --root "$demo_root" --apply --csv notes.txt
python -m internship.task3 --root fixtures/task3 --apply --csv master.csv
python -m unittest discover -s tests -v
```

Expected results: preview and both `master.csv` applies exit 0; the repeat plans zero moves; the `.txt` output and canonical-fixture apply each exit 2 before moving files. The first apply creates `.task3-generated-csv.json`; only a matching unchanged marker/CSV pair authorizes master regeneration.
