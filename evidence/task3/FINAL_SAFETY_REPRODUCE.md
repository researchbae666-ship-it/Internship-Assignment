# Reproduce final Task 3 safety checks

From the repository root:

```bash
demo_root=$(mktemp -d -p artifacts/task3 task3-final-demo-XXXXXX)
malformed_root=$(mktemp -d -p artifacts/task3 task3-final-malformed-XXXXXX)
cp -a fixtures/task3/. "$demo_root/"
cp -a fixtures/task3/. "$malformed_root/"
printf '\377\376' > "$malformed_root/malformed.log"
python -m internship.task3 --root "$demo_root"
python -m internship.task3 --root "$demo_root" --apply --csv master.csv
python -m internship.task3 --root "$demo_root" --apply --csv master.csv
python -m internship.task3 --root "$malformed_root" --apply --csv master.csv
python -m internship.task3 --root artifacts/task3 --apply
python -m unittest discover -s tests -v
```

The first three commands exit 0. The malformed-child and artifacts-parent applies exit 2 and must not create a CSV, marker, or move directories. The artifact parent is deliberately not an isolated writable workspace.
