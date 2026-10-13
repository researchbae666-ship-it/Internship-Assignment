# Python enhancement roadmap

## Baseline to protect

The Phase 5 Python deliverable is a known-good historical baseline at commit
`6fda8d6000a0f3db097c4fc12d673323ded84384`, with existing Task 2–4 code,
tests, evidence, and PDF retained in place. The initial setup suite completed
with 54 passing tests. That result validates the existing baseline only; it is
not a claim about unimplemented future enhancements.

## Audit criteria

Any proposed change will be evaluated against functionality, maintainability,
edge cases, reliability, security, user experience, performance, real-world
utility, test depth, documentation, and reproducibility. Changes that add
complexity without a measurable safety or usability benefit should not proceed.

## Prioritized candidates

| Priority | Area | Candidate | Expected value | Gate before implementation |
| --- | --- | --- | --- | --- |
| P0 | All | Re-run complete tests and evidence checks before any edit; preserve approved interfaces and historical report | Prevent regression and misleading documentation | Enhancement review |
| P1 | Task 3 | Assess an explicit, opt-in real-directory workflow with stronger root confirmation, extension policy configuration, and clearer partial-failure recovery | Useful only if it retains the synthetic-workspace safety boundary | Threat-model and test-plan review |
| P1 | Task 4 | Assess clearer command discovery, synonym coverage, and end-to-end dialogue regression cases | Improves terminal usability while retaining rule-based routing | Conversation/test review |
| P2 | Task 2 | Assess additional output formats and boundary/property tests while retaining JSON-array default and iterative generation | Small usability and verification benefit | Interface compatibility review |
| P2 | All | Improve reproducibility documentation only where new verified evidence justifies it | Easier independent review | Documentation review |

## Deferred decisions

No Python enhancement is authorized by this roadmap. Task 3 will never test
destructive behavior against personal directories. Task 4 will remain a
rule-based, dictionary-routed assistant; it will not be replaced by an LLM.
