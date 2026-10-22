# Phase 1 — Understand the change

Goal: know what changed, where the change comes in and goes out, and what it alters in existing flows — confirmed by the user.

## Steps

1. For each repository involved: current branch, merge-base with the base, `git log --oneline base..HEAD` and `git diff --stat`.
2. Read the diffs. If they are large or span several services, use **one subagent per service**, asking for: what is new, what changes in existing flows, entry and exit points, perceived risks, with file:line. Read the small ones yourself.
3. Map:
   - **entry points**: webhooks, endpoints, screens, jobs, queues;
   - **exit points**: databases, external APIs, UI, logs, reports, exports;
   - **what changes in existing flows**: this is where regressions live, and it becomes the control section of the test plan.
4. If the change consumes or produces an external format (partner webhook, public API), check the **latest official documentation** for fields and units instead of trusting old team examples.
5. Send the user a short summary (what the change does, the services, the flows it alters) and **confirm** it before writing the test plan.
6. Record it in `change.md` and move to phase 2.

## Fix mode

- Confirm with the user the description of the bug and the sequence that reproduces it.
- Identify the version **without** the fix (base or previous version) where the bug will be reproduced in phase 4, and whether the environment allows switching between the two.
- Map the neighbourhood of the fix: other flows that go through the same code.

## Pitfalls of this phase

- **The risks you see in the code are hypotheses.** They go into the test plan as cases to prove, never straight into the report.
- **Old payload examples with the wrong format.** Timestamp units, renamed fields, fields that "may be omitted". Check the current documentation.
