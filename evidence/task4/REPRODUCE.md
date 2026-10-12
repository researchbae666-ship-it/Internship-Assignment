# Reproduce Task 4 evidence

Run from the repository root at source revision `7c23159507b94caccebcbffc32eccf0705c22408`.

```bash
python -m unittest discover -s tests -v
python -m compileall -q internship
printf 'help\ntask 2\nhow do i benchmark it\npython concepts\nexplain it\nlists\nsubmission\ndeadline\nunrecognized wording\nreset\nexit\n' | python -m internship.task4
printf 'mystery request\nanother mystery\nreset\nexit\n' | python -m internship.task4
python -m internship.task4 < /dev/null
```

For an interactive session:

```bash
python -m internship.task4
```

The program uses only the Python standard library and needs no credentials, network service, or persistent storage.
