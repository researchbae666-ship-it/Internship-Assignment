# Phase 5 fresh evidence

`manifest.json` is the consolidated, sanitized evidence manifest for the fresh Phase 5 integration run. It identifies the executed source commit, UTC start time, commands and exit codes, environment, fixture references, benchmark samples/units, output paths, and SHA-256 digests.

The `outputs/` files are direct retained copies of the fresh synthetic command captures. `tools/collect_phase5_evidence.py` validates their required outcomes and digests before it writes the manifest. `outputs/pdf-qa.json` records the machine-checkable PDF metadata, text, and rendering checks.

Earlier task evidence under `evidence/task2/`, `evidence/task3/`, and `evidence/task4/` remains historical evidence with its own source-commit provenance. It was not relabeled as Phase 5 evidence.
