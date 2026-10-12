# Task 3 evidence history

The original demonstration files in this directory (`PREVIEW_MANIFEST.json`, `APPLY_MANIFEST.json`, `REPEAT_MANIFEST.json`, `MASTER.csv`, and `TEST_OUTPUT.txt`) are retained as historical evidence for source commit `091f990be18cdc8d2a30c9b4a1031bf8d732e396`.

Independent review found that version accepted unsafe output filenames and could replace an existing input or unrelated CSV. Source commit `534e39d86d57189c76f35bdec77d0c360124ca0c` corrects that behavior. The `REVIEW_FIX_*` files are the current evidence: they were generated from that corrected commit and show the CSV marker/regeneration behavior, rejected `.txt` output, unchanged input/canonical hashes, and a 30-test passing suite.

Final safety review found two further gaps: the artifacts parent was writable because containment allowed equality, and malformed logs were decoded only after moves. Source commit `3f578389706f258eb634f360aba4eed518ae83f8` corrects both. The `FINAL_SAFETY_*` files are the latest evidence: they show child-only writable roots, preflight UTF-8 failure before mutation, successful preview/apply/repeat behavior, unchanged input and canonical hashes, and a 33-test passing suite.
