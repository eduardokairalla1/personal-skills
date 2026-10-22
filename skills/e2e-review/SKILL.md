---
name: e2e-review
description: End-to-end review (QA) of a new feature or a bug fix, run in the real environment — requests to the entry points (webhooks, APIs), the front end driven in the browser as the end user would, verification in databases and logs — ending in a facts-only .md report for the responsible developer. Use it whenever the user asks to validate, test, sign off or QA a feature or fix end to end ("testa essa feature", "faz o QA", "homologar", "valida essa correção"), to design and run test scenarios for a branch or MR, to check that a fix solved the bug without breaking anything else, or to put together a bug report for a developer — even if they never say "e2e". Do not use it to write or fix automated tests (Playwright/Jest/pytest suites, a broken CI); that is coding work, not a review.
---

# e2e-review

Validate a change in the real environment, the way the end user and the neighbouring systems use it, and hand the developer a facts-only report: what was tested, what failed and how to reproduce it.

The product is not "having tested". It is the confidence that every path was exercised, every red result was explained, and every reported bug can be reproduced by someone else.

It covers **new features** and **bug fixes**. In fix mode, phases 1, 4 and 6 have their own block (reproduce before the fix, confirm after it, before/after report).

## How this skill works

The review moves through phases. **Read only the file of the phase you are in**; each one holds the steps and the pitfalls of that phase. When a phase ends, update the memory and only then open the next file. This keeps the context lean and stops rules of one phase from leaking into another.

Going back to an earlier phase is normal (e.g. triage asks to redo a case with realistic data → reopen the test plan). Just reopen that phase's file.

| Phase | What happens | File |
|---|---|---|
| 0. Ask | Get from the user the context you cannot discover alone: type of work, services and branches, environment, who executes, access, limits, what is manual, report format | `references/phases/0-ask.md` |
| 1. Understand | Read the diffs, map entry and exit points and what changes in existing flows; send a summary for the user to confirm | `references/phases/1-understand.md` |
| 2. Test plan | Write numbered cases with "how it is proven", covering the mandatory axes and the sections that usually get forgotten; confirm the scope | `references/phases/2-test-plan.md` |
| 3. Environment | Confirm the right code is running, set up observation and reversible instrumentation | `references/phases/3-environment.md` |
| 4. Execute | Run the cases section by section, by request and through the front end, with a short status in the chat | `references/phases/4-execute.md` |
| 5. Triage | Explain every red result and sort it into change bug, pre-existing behaviour, invalid test data or environment | `references/phases/5-triage.md` |
| 6. Report | Write the facts-only .md and check the counts | `references/phases/6-report.md` |
| 7. Wrap up | Revert and prove it, log out, list what is left manual | `references/phases/7-wrap-up.md` |

Phases 4 and 5 alternate: run one section of the plan, triage its red results, record, move on to the next section.

Technical reference material, opened by the phases when the task needs it:

- `references/browser.md` — driving the front end (the user's Chrome, headless Playwright, tricky fields, verifying without downloading);
- `references/instrumentation.md` — recording proxy, service down or slow, in-memory state, observation queries;
- `scripts/recording_proxy.py` — HTTP proxy that records requests, answers stubs and fires callbacks;
- `scripts/count_status.py` — recounts the statuses in the report tables.

## Rules for every phase

- **Ask instead of assuming** when the answer changes what you will do. A wrong assumption at the start costs hours at the end. If the user describes a bug in their own words, ask for the exact sequence before testing.
- **Confirm the scope before large work.** Show the size (how many cases, how many files) and let the user adjust it; large work nobody agreed on ends up as "hold on, why all this?".
- **Respect who executes.** If the user wants to do a part themselves, deliver what they asked for and stop there.
- **Do not change accounts, credentials or shared configuration without explicit authorisation.** If the automatic permission check denies an action, stop, explain what you needed and let the user decide. Do not work around it.
- **In the user's browser, say what you are about to click and why** before anything that may look destructive (log out, block, delete).
- **Do not touch data you did not create.** The environment may carry real traffic.
- **Follow the environment rules** in the project's CLAUDE.md (where each command runs, what may be restarted).
- **Short status in the chat** at the end of each section: what passed, what failed, what comes next.
- **Talk to the user and write the report in the user's language**, even though this skill is written in English.

## Memory

Keep the state in `~/.claude/memory/e2e/<change-slug>/`, so an interrupted session or the next round continues where it stopped:

- `change.md` — what it is, type (feature or fix), services, branches, running versions, entry and exit points, **current phase** and next step;
- `cases.md` — numbered test plan with status (✅ 🔴 🚫 ➖ ⬜) and one line of evidence;
- `findings.md` — numbered bugs with reproduction and evidence (a number is never reused);
- `environment.md` — how to observe, active instrumentation and how to undo it, new pitfalls found.

**When starting**, look for that directory. If it exists, read `change.md`, resume at the recorded phase and open only its file. Update the memory at the end of every phase and every executed section. Use absolute dates.
