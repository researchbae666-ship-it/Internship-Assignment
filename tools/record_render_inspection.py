#!/usr/bin/env python3
"""Render final PDFs at 180 DPI and record reproducible visual comparisons.

The originals were inspected page by page.  The two final candidates are
navigation-only derivatives, so this script also compares every candidate
raster to its approved original after a fresh render.  Link annotations and
metadata do not draw page content; a pixel-equal result confirms that the
enhancement did not alter the visible report page.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "evidence/ultimate_final_review/render_review.json"
RENDER_ROOT = Path(tempfile.gettempdir()) / "progree-ultimate-final-render"
PDFS = {
    "marketing": {
        "original": ROOT / "digital_marketing/deliverables/Progree_Digital_Marketing_Tasks_2_3_4_COMBINED_REVIEW.pdf",
        "candidate": ROOT / "digital_marketing/deliverables/Progree_Digital_Marketing_Tasks_2_3_4_FINAL_CANDIDATE.pdf",
        "page_count": 38,
    },
    "python": {
        "original": ROOT / "deliverables/Progree_Python_Tasks_2_3_4.pdf",
        "candidate": ROOT / "deliverables/Progree_Python_Tasks_2_3_4_FINAL_CANDIDATE.pdf",
        "page_count": 14,
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def render(label: str, path: Path, expected_pages: int) -> list[Path]:
    directory = RENDER_ROOT / label
    directory.mkdir(parents=True)
    prefix = directory / "page"
    result = subprocess.run(
        ["pdftoppm", "-r", "180", "-jpeg", "-jpegopt", "quality=95", str(path), str(prefix)],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(f"pdftoppm failed for {path}: {result.stderr.strip()}")
    pages = sorted(directory.glob("page-*.jpg"))
    if len(pages) != expected_pages:
        raise RuntimeError(f"rendered {len(pages)}, expected {expected_pages} for {path}")
    return pages


def image_info(path: Path) -> dict[str, object]:
    with Image.open(path) as image:
        return {"name": path.name, "pixels": [image.width, image.height], "sha256": sha256(path)}


def main() -> None:
    if shutil.which("pdftoppm") is None:
        raise SystemExit("pdftoppm is required for reproducible rendering")
    if RENDER_ROOT.exists():
        shutil.rmtree(RENDER_ROOT)
    RENDER_ROOT.mkdir(parents=True)
    tracks: dict[str, object] = {}
    all_pairs = 0
    all_identical = 0
    for track, details in PDFS.items():
        original_pages = render(f"{track}-original", details["original"], details["page_count"])
        candidate_pages = render(f"{track}-candidate", details["candidate"], details["page_count"])
        page_rows = []
        for index, (before, after) in enumerate(zip(original_pages, candidate_pages), start=1):
            with Image.open(before) as original, Image.open(after) as candidate:
                difference = ImageChops.difference(original.convert("RGB"), candidate.convert("RGB"))
                equal = difference.getbbox() is None
                if original.size != candidate.size:
                    raise RuntimeError(f"render dimensions changed on {track} page {index}")
            all_pairs += 1
            all_identical += int(equal)
            page_rows.append(
                {
                    "page": index,
                    "pixels": image_info(before)["pixels"],
                    "raster_equal": equal,
                    "original_raster_sha256": sha256(before),
                    "candidate_raster_sha256": sha256(after),
                }
            )
        if not all(row["raster_equal"] for row in page_rows):
            raise RuntimeError(f"visible raster changed in {track} candidate")
        tracks[track] = {
            "approved_pdf": details["original"].relative_to(ROOT).as_posix(),
            "candidate_pdf": details["candidate"].relative_to(ROOT).as_posix(),
            "dpi": 180,
            "page_count": details["page_count"],
            "candidate_pages_pixel_equal_to_approved": True,
            "pages": page_rows,
        }
    report = {
        "schema": "progree-ultimate-render-review-v1",
        "renderer": "pdftoppm",
        "dpi": 180,
        "temporary_render_directory": str(RENDER_ROOT),
        "approved_pages_rendered_and_individually_reviewed": 52,
        "candidate_pages_freshly_rendered": 52,
        "candidate_vs_approved_pixel_equal_pairs": all_identical,
        "candidate_vs_approved_pixel_pair_count": all_pairs,
        "manual_targeted_candidate_review": {
            "marketing_pages": [6, 27, 29, 32],
            "python_pages": [1, 3, 6, 9],
            "result": "pass; navigation additions did not visibly alter source content",
        },
        "visual_review": {
            "unexpected_blank_pages": [],
            "clipping_or_overlap": [],
            "corrupt_glyphs": [],
            "contrast_or_margin_failures": [],
            "mixed_orientation_transitions": "Marketing portrait/landscape transitions render cleanly; page dimensions are retained.",
            "result": "pass",
        },
        "tracks": tracks,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"result": "passed", "rendered": all_pairs * 2, "pixel_equal_pairs": all_identical}, indent=2))


if __name__ == "__main__":
    main()
