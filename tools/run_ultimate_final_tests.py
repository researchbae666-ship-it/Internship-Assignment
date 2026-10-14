#!/usr/bin/env python3
"""Run the complete safe final-audit regression set and retain raw logs."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence/ultimate_final_review"
LOGS = EVIDENCE / "logs"

CHECKS = (
    ("python_unit", ROOT, [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
    ("marketing_task2_handoff", ROOT / "digital_marketing/research/task2/handoff", [sys.executable, "-m", "unittest", "-v", "test_handoff"]),
    ("marketing_task2_recovery", ROOT / "digital_marketing/research/task2/recovery", [sys.executable, "-m", "unittest", "-v", "test_recovery"]),
    ("marketing_task2_secondary", ROOT / "digital_marketing/research/task2/secondary", [sys.executable, "-m", "unittest", "-v", "test_secondary"]),
    ("marketing_task3", ROOT / "digital_marketing/research/task3", [sys.executable, "-m", "unittest", "-v", "test_campaign"]),
    ("marketing_task4", ROOT / "digital_marketing/research/task4", [sys.executable, "-m", "unittest", "-v", "test_strategy", "test_email_workflows"]),
    ("marketing_report_presentation", ROOT / "digital_marketing/tools", [sys.executable, "-m", "unittest", "-v", "test_task2_recovery_report", "test_generate_task3_report", "test_generate_task4_report"]),
    ("candidate_build_and_validation", ROOT, [sys.executable, "tools/build_final_pdf_candidates.py"]),
    ("ultimate_adversarial_checks", ROOT, [sys.executable, "tools/ultimate_red_team_checks.py"]),
)


def main() -> int:
    LOGS.mkdir(parents=True, exist_ok=True)
    results = []
    for name, cwd, command in CHECKS:
        process = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
        (LOGS / f"{name}.stdout.log").write_text(process.stdout, encoding="utf-8")
        (LOGS / f"{name}.stderr.log").write_text(process.stderr, encoding="utf-8")
        joined = process.stdout + "\n" + process.stderr
        match = re.search(r"Ran (\d+) tests?", joined)
        results.append(
            {
                "name": name,
                "command": command,
                "cwd": str(cwd.relative_to(ROOT)) if cwd != ROOT else ".",
                "returncode": process.returncode,
                "test_count": int(match.group(1)) if match else None,
                "stdout_log": (LOGS / f"{name}.stdout.log").relative_to(ROOT).as_posix(),
                "stderr_log": (LOGS / f"{name}.stderr.log").relative_to(ROOT).as_posix(),
            }
        )
    output = {"schema": "progree-ultimate-test-results-v1", "checks": results, "all_passed": all(row["returncode"] == 0 for row in results)}
    (EVIDENCE / "test_results.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if output["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
