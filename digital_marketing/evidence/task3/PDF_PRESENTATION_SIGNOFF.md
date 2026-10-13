# Task 3 PDF presentation sign-off evidence

**PDF source revision:** `f12a3c197493d3823e1693710340a0e9a4be9157`<br>
**Generated (UTC):** 2026-10-13T11:16:41Z

## Corrected issue

`table()` now creates header cells with an explicit white, `Helvetica-Bold`
`ParagraphStyle`. This avoids relying on `TableStyle` to override the dark body
paragraph color. The regression test checks both header and body cell styles.

## Actual verification

| Check | Result |
| --- | --- |
| Campaign data tests | 10 passed, 0 failed |
| PDF header-style regression test | 1 passed, 0 failed |
| Python regression suite | 54 passed, 0 failed |
| PDF metadata | 20 A4-landscape pages; 54,265 bytes |
| Text extraction | Required report sections found |
| Render inspection | All 20 pages rendered at 144 DPI and inspected in four contact sheets; headers are white and bold, and no clipping, corrupt text, or blank pages were observed |

**PDF SHA-256:**
`ecf3eef10ad417b71c31e5ab2bd986d933f4470195afb11f7283131a515159b8`
