# Task 2 test execution

The following command ran against source commit `b238e2af575a22f621a52ef6c6cd846352b6ec9b` on 12 October 2026:

```console
python -m unittest discover -s tests -v
```

Observed outcome:

```text
Ran 13 tests in 1.009s

OK
```

The 13 passing tests cover exact output for counts 0, 1, 2, 10 and 100; recurrence through 250 terms; negative and invalid values; CLI JSON output and exit-2 errors; the 10,000-term CLI resource limit; benchmark validation; and real timeit metadata/samples. The raw verbose test output is intentionally ignored in `artifacts/`; its SHA-256 is in [METADATA.json](METADATA.json).
