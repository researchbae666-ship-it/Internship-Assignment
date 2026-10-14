# Ultimate red-team findings

## Fixed

| ID | Severity | Location | Evidence and impact | Fix / regression | Final status |
| --- | --- | --- | --- | --- | --- |
| UFR-001 | P1 material | `internship/task3.py:156-201`; `tests/test_task3.py:92-102` | A caller could construct `PlannedMove("input.txt", "../escape.txt")`. `apply_plan` joined the relative path before checking its lexical components, so the synthetic reproduction created a file outside the selected isolated child workspace. See `logs/red_team_pre_fix_failure.txt`. | Validate source as exactly one non-absolute component and destination as exactly two non-absolute components, rejecting `..`; add a unit regression. `python -m unittest discover -s tests -v` passes. | Fixed. |
| UFR-002 | P1 material | `digital_marketing/research/task3/build_campaign.py:315-335`; `test_campaign.py:93-98` | Deep-copying and appending an action left the campaign validator green. This could permit duplicate calendar entries and ambiguous spend/action reconciliation. See `logs/red_team_after_ufr001_failure.txt`. | Reject duplicate `action_id` values and duplicate `(day, platform)` schedule slots; add a unit regression. `python -m unittest -v test_campaign` passes. | Fixed. |
| UFR-003 | P1 material to evidence preservation | Initial audit-harness behavior in `tools/ultimate_red_team_checks.py`; final fix redirects both generator globals | The first safe-assembly harness redirected the output PDF but not the generator's historic QA manifest path, so it temporarily changed that historic manifest's `output` field. The approved PDF never changed and the historical manifest was restored before continuing. See `logs/preservation_side_effect_detected.txt`. | Redirect both `generate_combined_review_pdf.OUTPUT` and `.MANIFEST` to the temporary directory; the final full regression run confirms the historical manifest and all protected artifacts match baseline. | Fixed. |

## Verified pass

| ID | Scope | Evidence | Final status |
| --- | --- | --- | --- |
| UFR-004 | Protected original PDFs and source reports | Baseline manifest hashes, source-page stream/text/dimension comparison for all 36 included Marketing report pages, and post-review protected hashes | Pass. The 38-page approved Marketing PDF and 14-page approved Python PDF exactly match reviewed hashes. |
| UFR-005 | Candidate fidelity and navigation | Candidate build checks every page's content stream, text, media box, and rotation; 180-DPI raster comparison is 52/52 pixel-equal pairs | Pass. No page content was rasterized, rewritten, or visibly changed. Marketing has six ordered bookmarks, labels, and 11 verified public links; Python has eight ordered bookmarks and labels. |
| UFR-006 | Rendering, typography, tables and orientation | Every approved page was rendered and reviewed at 180 DPI; all candidate pages were freshly rendered. `render_review.json` records no blank pages, clipping/overlap, corrupt glyphs, contrast/margin failures, or mixed-orientation failures. | Pass. 104 final-audit page rasters were produced; 52 approved pages received individual visual inspection. |
| UFR-007 | Claims and research boundaries | Text extraction, source report review, campaign/strategy tests, and report-presentation suite | Pass. Task 2 stays evidence-limited; Task 3 remains fictional/proposed; Task 4 remains proposed/modeled. No live results are asserted. |
| UFR-008 | Privacy and metadata | `privacy_scan.json`: value-redacted repository/PDF scan, metadata check, JavaScript/encryption check | Pass. No unknown contact information, secret, identity value, suspicious file name, PDF JavaScript, or encryption found. Allowed synthetic `example.test` fixture values remain. |

## Accepted limitation

| ID | Severity | Exact scope | Evidence | Impact / required action | Final status |
| --- | --- | --- | --- | --- | --- |
| UFR-009 | External eligibility | Marketing Task 2, candidate pp. 3–6 | The report expressly describes third-party historical cumulative-count proxies and October vendor engagement estimates. It states that verified 15 September–12 October cadence, post-level engagement, full cross-platform inventory, LinkedIn and YouTube evidence are unavailable. | Technical quality cannot establish complete Task 2 rubric coverage. Do not claim organizer approval. Obtain organizer acceptance or collect the documented missing evidence. | Accepted limitation; Marketing remains conditional. |
| UFR-010 | P2 presentation | Marketing source URLs that wrap across multiple drawn text fragments | Coordinates are reliable for 11 exact, visible public URLs only. Some longer wrapped URLs have no single reliable hit rectangle. | Leaving those URLs as text avoids guessed/misaligned annotations and preserves source fidelity. | Accepted; no further safe improvement needed. |

## External blocker

| ID | Scope | Evidence | Required action | Final status |
| --- | --- | --- | --- | --- |
| UFR-011 | Google Form and submission rules | `Text Message 2.md` names the Google Form, says submit all tasks in one PDF, Google Form only, and gives 18 October 2026. A read-only HTTP request was blocked by this execution runtime, not shown closed. | Confirm form availability, login, per-track vs combined submission structure, allowed files/sizes/fields, and cutoff hour/timezone from an official source. | External confirmation required. |

## Requires owner decision

| ID | Scope | Decision needed | Final status |
| --- | --- | --- | --- |
| UFR-012 | Submission | Whether to submit the conditional Marketing package if Task 2 acceptance is still unanswered; whether a form permits Python-only or separate submissions; final authorization. | Owner decision required. |

No P0 defect, sensitive-data exposure, corrupted report page, material calculation error, or unpreserved source document remains.
