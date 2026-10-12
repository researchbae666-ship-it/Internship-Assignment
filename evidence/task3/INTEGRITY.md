# Demonstration integrity checks

The input inventory contained eight files. Apply completed seven moves because `txt/notes.txt` was intentionally pre-organized to exercise the deterministic collision result `txt/notes__1.txt`.

SHA-256 hashes of all input files were calculated before apply and compared with hashes of every non-CSV file after apply. The sorted hash lists were identical. The command exited 0 and printed:

```text
PASS: content hashes match before/after organization
```

The apply manifest records `failure_count: 0`, and the repeat manifest records zero planned/completed moves. The CLI was also run with `--csv ../outside.csv`; it exited 2, wrote no stdout, and reported `CSV output must be a filename directly inside the workspace`.
