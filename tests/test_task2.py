"""Automated tests for Task 2's public API, CLI, and genuine timeit measurements."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from internship.task2 import CLI_MAX_COUNT, fibonacci, run_benchmark


ROOT = Path(__file__).resolve().parents[1]


class FibonacciFunctionTests(unittest.TestCase):
    def test_exact_small_sequences(self) -> None:
        self.assertEqual(fibonacci(0), [])
        self.assertEqual(fibonacci(1), [0])
        self.assertEqual(fibonacci(2), [0, 1])
        self.assertEqual(fibonacci(10), [0, 1, 1, 2, 3, 5, 8, 13, 21, 34])

    def test_large_sequence_has_known_final_term(self) -> None:
        values = fibonacci(100)
        self.assertEqual(len(values), 100)
        self.assertEqual(values[-1], 218922995834555169026)

    def test_recurrence_holds_for_a_larger_sequence(self) -> None:
        values = fibonacci(250)
        for index in range(2, len(values)):
            self.assertEqual(values[index], values[index - 1] + values[index - 2])

    def test_negative_count_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            fibonacci(-1)

    def test_invalid_types_are_rejected(self) -> None:
        for value in (True, False, 1.0, "10", None):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    fibonacci(value)  # type: ignore[arg-type]


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "internship.task2", *arguments],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_sequence_is_a_valid_json_array(self) -> None:
        result = self.run_cli("--count", "10")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), fibonacci(10))
        self.assertEqual(result.stderr, "")

    def test_negative_count_has_usage_error_exit_code(self) -> None:
        result = self.run_cli("--count", "-1")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("count must be greater than or equal to zero", result.stderr)

    def test_non_integer_count_has_usage_error_exit_code(self) -> None:
        result = self.run_cli("--count", "1.5")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("invalid int value", result.stderr)

    def test_resource_limit_has_usage_error_exit_code(self) -> None:
        result = self.run_cli("--count", str(CLI_MAX_COUNT + 1))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("must not exceed", result.stderr)

    def test_benchmark_is_valid_json_with_real_samples(self) -> None:
        result = self.run_cli(
            "--benchmark", "--benchmark-counts", "0", "10", "--repeats", "2", "--number", "3"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["units"], "seconds")
        self.assertEqual(payload["repeat_count"], 2)
        self.assertEqual(payload["executions_per_repeat"], 3)
        self.assertEqual([row["count"] for row in payload["results"]], [0, 10])
        for row in payload["results"]:
            self.assertEqual(len(row["sample_totals_seconds"]), 2)
            self.assertTrue(all(sample > 0 for sample in row["sample_totals_seconds"]))
            self.assertGreater(row["median_per_call_seconds"], 0)

    def test_benchmark_rejects_invalid_configuration(self) -> None:
        cases = (("--repeats", "0"), ("--number", "0"), ("--benchmark-counts", "-1"))
        for flag, value in cases:
            with self.subTest(flag=flag, value=value):
                result = self.run_cli("--benchmark", flag, value)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")


class BenchmarkFunctionTests(unittest.TestCase):
    def test_real_benchmark_metadata_and_format(self) -> None:
        payload = run_benchmark([1], repeats=2, number=2)
        self.assertEqual(payload["units"], "seconds")
        self.assertIn("fibonacci(count) only", payload["measurement"])
        self.assertIn("python_version", payload)
        self.assertIn("platform", payload)
        row = payload["results"][0]
        self.assertEqual(row["count"], 1)
        self.assertEqual(len(row["sample_totals_seconds"]), 2)
        self.assertTrue(all(isinstance(sample, float) and sample > 0 for sample in row["sample_totals_seconds"]))

    def test_benchmark_configuration_validation(self) -> None:
        invalid_calls = [
            lambda: run_benchmark([], repeats=1, number=1),
            lambda: run_benchmark([1], repeats=0, number=1),
            lambda: run_benchmark([1], repeats=1, number=0),
            lambda: run_benchmark([True], repeats=1, number=1),
            lambda: run_benchmark("10", repeats=1, number=1),
        ]
        for invalid_call in invalid_calls:
            with self.assertRaises((TypeError, ValueError)):
                invalid_call()


if __name__ == "__main__":
    unittest.main()
