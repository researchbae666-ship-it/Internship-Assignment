"""Task 2: exact Fibonacci generation and reproducible timing measurements.

The public ``fibonacci`` function deliberately accepts only plain ``int`` values.
In particular, ``bool`` is rejected even though it is an ``int`` subclass in Python.
"""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import timeit
from collections.abc import Iterable
from typing import Any


DEFAULT_BENCHMARK_COUNTS = (10, 100, 1000)
DEFAULT_REPEATS = 5
DEFAULT_NUMBER = 100
CLI_MAX_COUNT = 10_000


def _validate_count(count: int, *, label: str = "count") -> None:
    """Validate a Fibonacci term count without coercing caller input."""
    if isinstance(count, bool) or not isinstance(count, int):
        raise TypeError(f"{label} must be an integer, not {type(count).__name__}")
    if count < 0:
        raise ValueError(f"{label} must be greater than or equal to zero")


def fibonacci(count: int) -> list[int]:
    """Return exactly ``count`` Fibonacci terms beginning with 0 and 1.

    The algorithm is iterative. It uses O(count) list storage, and each addition uses
    Python arbitrary-precision integers; additions become more expensive as values
    grow, so the usual constant-cost arithmetic simplification does not apply.
    """
    _validate_count(count)
    terms: list[int] = []
    previous, current = 0, 1
    for _ in range(count):
        terms.append(previous)
        previous, current = current, previous + current
    return terms


def _validate_positive(value: int, *, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be an integer, not {type(value).__name__}")
    if value <= 0:
        raise ValueError(f"{label} must be greater than zero")


def _validate_cli_limit(count: int, *, label: str) -> None:
    _validate_count(count, label=label)
    if count > CLI_MAX_COUNT:
        raise ValueError(f"{label} must not exceed {CLI_MAX_COUNT} for CLI output")


def run_benchmark(
    counts: Iterable[int] = DEFAULT_BENCHMARK_COUNTS,
    *,
    repeats: int = DEFAULT_REPEATS,
    number: int = DEFAULT_NUMBER,
) -> dict[str, Any]:
    """Time only Fibonacci generation and return JSON-serializable measurements.

    ``Timer.repeat`` invokes the statement ``number`` times for every sample. Printing,
    JSON encoding, metadata collection, and sample summarisation all happen outside the
    measured statement.
    """
    if isinstance(counts, (str, bytes)) or not isinstance(counts, Iterable):
        raise TypeError("counts must be an iterable of integers")
    normalized_counts = list(counts)
    if not normalized_counts:
        raise ValueError("counts must contain at least one value")
    _validate_positive(repeats, label="repeats")
    _validate_positive(number, label="number")

    measurements: list[dict[str, Any]] = []
    for count in normalized_counts:
        _validate_cli_limit(count, label="benchmark count")
        timer = timeit.Timer("fibonacci(count)", globals={"fibonacci": fibonacci, "count": count})
        samples = timer.repeat(repeat=repeats, number=number)
        per_call = [sample / number for sample in samples]
        measurements.append(
            {
                "count": count,
                "sample_totals_seconds": samples,
                "minimum_per_call_seconds": min(per_call),
                "median_per_call_seconds": statistics.median(per_call),
            }
        )

    return {
        "measurement": "timeit: fibonacci(count) only; excludes printing, JSON encoding, and metadata",
        "units": "seconds",
        "repeat_count": repeats,
        "executions_per_repeat": number,
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "results": measurements,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate an exact Fibonacci sequence or benchmark its generation."
    )
    parser.add_argument("--count", type=int, default=10, help="number of terms to emit (0-%(default)s; maximum 10000)")
    parser.add_argument("--benchmark", action="store_true", help="emit timeit benchmark results as JSON")
    parser.add_argument(
        "--benchmark-counts",
        nargs="+",
        type=int,
        default=list(DEFAULT_BENCHMARK_COUNTS),
        metavar="COUNT",
        help="term counts to measure (default: 10 100 1000)",
    )
    parser.add_argument("--repeats", type=int, default=DEFAULT_REPEATS, help="timeit samples per count")
    parser.add_argument("--number", type=int, default=DEFAULT_NUMBER, help="generation calls in each sample")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the Task 2 command line interface and return a shell exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.benchmark:
            payload = run_benchmark(
                args.benchmark_counts, repeats=args.repeats, number=args.number
            )
        else:
            _validate_cli_limit(args.count, label="count")
            payload = fibonacci(args.count)
    except (TypeError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(payload, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
