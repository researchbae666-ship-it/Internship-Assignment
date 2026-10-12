# Reproduce Task 2 evidence

Run these commands from the repository root with Python 3.12 or newer:

```bash
python -m unittest discover -s tests -v
python -m internship.task2 --count 10
python -m internship.task2 --count 0
python -m internship.task2 --count -1
python -m internship.task2 --benchmark --benchmark-counts 10 100 1000 --repeats 5 --number 100
```

The negative-count command is expected to exit 2. The last command is a genuine `timeit` measurement and will produce different samples on another run or machine. It measures `fibonacci(count)` only; its reported units are seconds.
