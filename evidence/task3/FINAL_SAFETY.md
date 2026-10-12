# Final Task 3 safety evidence

Generated from source commit `3f578389706f258eb634f360aba4eed518ae83f8` on 12 October 2026.

```bash
python -m internship.task3 --root <artifact-child>
python -m internship.task3 --root <artifact-child> --apply --csv master.csv
python -m internship.task3 --root <artifact-child> --apply --csv master.csv
python -m internship.task3 --root <malformed-artifact-child> --apply --csv master.csv
python -m internship.task3 --root artifacts/task3 --apply
python -m unittest discover -s tests -v
```

Results:

- Preview exited 0 and planned seven moves without writing a CSV.
- Apply exited 0 with seven completed moves, `failure_count: 0`, and a verified nine-record CSV. Its records use post-move paths.
- Repeat exited 0 and planned zero moves; the verified generated `master.csv` was safely regenerated with its marker.
- The malformed-log apply exited 2 before moves/CSV output: `UTF-8 decoding failed for malformed.log: invalid start byte`.
- The artifacts parent apply exited 2: `apply and CSV writes require an isolated child workspace below artifacts/task3`.
- SHA-256 input-content lists before/after successful organization matched. The malformed workspace's complete before/after inventory hashes matched, and canonical fixture hashes before/after matched.
- The complete suite output ended with `Ran 33 tests in 0.842s` and `OK`.

The preflight minimizes malformed-input partial operations, but it is not a transactional guarantee if the filesystem changes after the check. Normal move failures remain accurately recorded in the apply manifest.
