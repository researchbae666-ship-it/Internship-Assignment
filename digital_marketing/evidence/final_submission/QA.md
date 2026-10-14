# Final Digital Marketing submission-preparation QA

The generated `manifest.json` is the current machine-readable execution record.
Run the reproduction commands before relying on it after a source or toolchain
change.

## Required checks

| Check | Expected result |
| --- | --- |
| Input integrity | SHA-256 recorded for each of the four exact approved source PDFs before combining and unchanged afterwards |
| Assembly | Two anonymous front-matter pages followed by Task 2, Task 3, Task 4 main report, then Task 4 email appendix |
| Fidelity | Source pages are appended as PDF pages through pypdf; no rasterization or image conversion is used |
| Navigation | Bookmarks and decimal page labels exist for cover, contents, each task, and the appendix |
| Text and fonts | Each page has extractable text and referenced font resources; required boundary language is present |
| Hyperlinks | URI annotations in the source PDFs are counted and the final count must match |
| Privacy | Metadata is checked for the defined unintended-identity markers; cover and contents contain no participant identity |
| Content limits | Task 2 remains explicitly evidence-limited and pending rubric acceptance; Task 3 is fictional; Task 4 is modeled; no organizer approval or live performance is implied |

## Submission-readiness checklist

- [x] Consolidated review PDF prepared with the four supplied source documents.
- [x] Task 2 boundary language retained: evidence-limited public-source audit with unavailable cadence/engagement evidence.
- [x] Task 3 clearly separated as the fictional proposed RefillLoop campaign.
- [x] Task 4 clearly separated as a modeled Ocean Bottle strategy and inactive email workflows.
- [x] Source content, references, limitations, budget calculations, and scripts retained through page-preserving PDF assembly.
- [x] Combined PDF QA executed and recorded in `manifest.json`.
- [ ] Task 2 rubric acceptance by the organizer remains pending.
- [ ] Organizer confirmation remains pending.
- [ ] Final user authorization to submit remains pending.

Do not submit a form, send email, publish social content, or merge this branch
until those final review and authorization gates are satisfied.
