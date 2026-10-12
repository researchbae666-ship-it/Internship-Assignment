# Intent and help-tree coverage

Source revision: `7c23159507b94caccebcbffc32eccf0705c22408`

`tests/test_task4.py` executed each supported routing family and asserts both response content and state where appropriate:

| Intent / tree | Executed coverage |
| --- | --- |
| Global help | Opens the root choice prompt. |
| Task guidance | Explains Tasks 2, 3, and 4; Task 2 follow-up covers the real benchmark command. |
| Python learning | Covers fundamentals, lists and loops, functions and validation, and regex and file handling. |
| Submission guidance | Covers three-of-four, one-PDF, 18 October 2026, optional Task 1/LinkedIn, and its stated uncertainty boundaries. |
| Topic changes | Explicit Python and submission requests override an earlier pending choice. |
| Ambiguous input | Requests a scoped clarification instead of inventing a choice. |
| Fallback | Covers first and repeated unrecognized input. |
| Global controls | Covers reset, cancel, exit, EOF, and KeyboardInterrupt. |

Matching is token based after Unicode NFKC normalization, casefolding, punctuation replacement, and whitespace normalization. The test `test_exact_token_matching_avoids_accidental_substrings` verifies that `this` does not accidentally route as a supported intent.
