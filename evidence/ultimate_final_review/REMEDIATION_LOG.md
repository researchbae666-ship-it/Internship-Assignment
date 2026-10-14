# Remediation log

| Order | Finding | Change | Why this is minimal | Verification |
| ---: | --- | --- | --- | --- |
| 1 | UFR-001 | Added lexical component validation in `apply_plan` and a direct crafted-move test. | It rejects only moves that were never valid under the stated immediate-file/immediate-extension safety model. Normal planned moves retain their path shape and behavior. | Targeted unit test, 55 Python tests, and the final adversarial harness pass. |
| 2 | UFR-002 | Added duplicate action-ID and day/platform-slot validation to the RefillLoop campaign validator, with a deep-copy regression test. | It leaves the approved 30-day data unchanged and rejects only ambiguous duplicate entries. | Task 3 suite (11 tests) and final adversarial harness pass. |
| 3 | UFR-003 | Changed the audit harness's isolated assembly block to redirect both output PDF and historic manifest into one temporary directory. | The test continues to exercise real assembly logic without touching historic evidence. | Final full suite passes; baseline comparison reports no unexpected historic-file changes. |
| 4 | P2 navigation | Created separate final-candidate PDFs. Marketing removes redundant top-level bookmark duplication, adds clear section bookmarks/labels and 11 reliable public URL annotations. Python adds section bookmarks and labels. Candidate author metadata is the anonymous project descriptor. | Page content streams, extracted text, media boxes, rotations, and final raster images remain equal to approved inputs. | Candidate build validation; 52 fresh candidate render pages; 52/52 pixel-equal comparisons; privacy scan passes. |

The approved PDFs were never overwritten. The approved Marketing source PDFs, research evidence, prior QA material, original combined PDF, and original Python PDF retain their baseline hashes. The current candidates are separate files selected only because the navigation improvements are objectively beneficial and fully regression-tested.
