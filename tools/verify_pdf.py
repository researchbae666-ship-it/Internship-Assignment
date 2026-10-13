"""Perform machine-checkable Phase 5 PDF quality checks from retained evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str], cwd: Path) -> str:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}\n{result.stderr}")
    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify final PDF structure, text, and renders.")
    parser.add_argument("--pdf", type=Path, default=ROOT / "deliverables/Progree_Python_Tasks_2_3_4.pdf")
    parser.add_argument("--manifest", type=Path, default=ROOT / "evidence/phase5/manifest.json")
    parser.add_argument("--render-dir", type=Path, default=ROOT / "artifacts/phase5/pdf-qa-render")
    args = parser.parse_args()
    try:
        pdf = args.pdf.resolve()
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        if not pdf.is_file() or pdf.stat().st_size == 0:
            raise RuntimeError("PDF is missing or empty")
        info = run(["pdfinfo", str(pdf)], ROOT)
        page_match = re.search(r"^Pages:\s+(\d+)$", info, flags=re.MULTILINE)
        if not page_match:
            raise RuntimeError("pdfinfo did not report a page count")
        page_count = int(page_match.group(1))
        if not 12 <= page_count <= 18:
            raise RuntimeError(f"unexpected page count: {page_count}")
        text_path = args.render_dir.parent / "pdf-qa-extracted.txt"
        args.render_dir.mkdir(parents=True, exist_ok=True)
        run(["pdftotext", "-layout", str(pdf), str(text_path)], ROOT)
        extracted = text_path.read_text(encoding="utf-8")
        expected = ("Python Programming Internship", "Task 2 — Fibonacci", "Task 3 — File automation", "Task 4 — multi-intent", "Cross-task quality assurance", "Appendix")
        missing = [value for value in expected if value not in extracted]
        if missing:
            raise RuntimeError("PDF text is missing expected sections: " + ", ".join(missing))
        expected_tests = f"{manifest['test_summary']['count']} tests passed"
        if expected_tests not in extracted:
            raise RuntimeError("PDF test claim does not match the evidence manifest")
        if "units are seconds" not in extracted:
            raise RuntimeError("PDF benchmark units are not present")
        for image in args.render_dir.glob("page-*.png"):
            image.unlink()
        run(["pdftoppm", "-png", "-r", "144", str(pdf), str(args.render_dir / "page")], ROOT)
        images = sorted(args.render_dir.glob("page-*.png"))
        if len(images) != page_count or any(image.stat().st_size == 0 for image in images):
            raise RuntimeError("PDF rendering did not produce one nonempty image per page")
        payload = {
            "outcome": "passed",
            "pdf": "deliverables/Progree_Python_Tasks_2_3_4.pdf",
            "sha256": sha256(pdf),
            "size_bytes": pdf.stat().st_size,
            "page_count": page_count,
            "pdfinfo": {line.split(":", 1)[0]: line.split(":", 1)[1].strip() for line in info.splitlines() if ":" in line and line.split(":", 1)[0] in {"Title", "Producer", "Pages", "Page size", "Encrypted"}},
            "text_checks": {"expected_sections_present": True, "test_claim_matches_manifest": True, "benchmark_units_present": True},
            "render_checks": {"renderer": "pdftoppm", "dpi": 144, "rendered_page_count": len(images), "all_rendered_files_nonempty": True},
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError, RuntimeError) as error:
        print(json.dumps({"outcome": "failed", "error": str(error)}, indent=2, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
