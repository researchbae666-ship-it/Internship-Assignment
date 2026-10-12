# Task 2 CLI demonstration

Executed from the repository root on 12 October 2026 against source commit `b238e2af575a22f621a52ef6c6cd846352b6ec9b`.

## Exact commands and observed results

```console
$ python -m internship.task2 --count 10
[0,1,1,2,3,5,8,13,21,34]

$ python -m internship.task2 --count 0
[]

$ python -m internship.task2 --count -1
usage: task2.py [-h] [--count COUNT] [--benchmark]
                [--benchmark-counts COUNT [COUNT ...]] [--repeats REPEATS]
                [--number NUMBER]
task2.py: error: count must be greater than or equal to zero
```

The first two commands exited 0. The negative-count command exited 2 and wrote no stdout. The raw, ignored captures have SHA-256 digests listed in [METADATA.json](METADATA.json).
