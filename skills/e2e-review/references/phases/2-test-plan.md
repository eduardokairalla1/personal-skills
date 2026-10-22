# Phase 2 — Test plan

Goal: a numbered list of cases, each with "what it validates" and "how it is proven", covering what the change promises and what it may break — with the scope confirmed by the user.

## Personas

Create one persona per relevant variation of identity or payload, with a human name and fictitious values. Fixed names make logs, screens and the report readable ("Ana sends the second message" instead of "payload 3").

| Persona | Variation (example — adapt to the change) |
|---|---|
| A | new identifier only |
| B | new + old identifier |
| C | old identifier only — the **control** for regressions |
| P/Q | the same entity through two paths, already linked in the system |

- **A new identifier every round** (suffix with round number or timestamp). Otherwise "new entity" is only real on the first run.
- **Realistic data.** Hidden validation rules (mobile number format, check digits, valid ranges) turn fictitious data into false bugs.

## Mandatory axes

| Axis | Question |
|---|---|
| Happy path | What the change promises, in the expected format |
| Missing field | Each optional field missing, one at a time — including those the documentation says "may be omitted" |
| Unexpected field | null, empty, wrong type, size at and above the limit |
| New × existing | First time (creation) and repetition (update) |
| Idempotency | Does the same input twice duplicate anything? |
| Order | Events in immediate sequence; A before B and B before A |
| Concurrency | Two actions on the same resource at the same time |
| Dependency down | A service the change depends on is slow or down: does it lose, delay or block the caller? |
| Persistence | Does the state survive a restart of each service involved? |
| Regression | Does the **old** flow still behave the same? Other channels, accounts, types? |
| Display | How it shows on each screen, live and after reloading |
| Cleanup | Do block, delete and deactivate use the right identifier? |

## Sections that usually get forgotten

In the first version of a test plan these almost always go missing. Include them from the start:

- **Both directions of the flow**: receiving *and* opening/starting/sending — and every way of starting (from the list, from the entity, from history, from boards, from a report, from another channel or account).
- **Shared entities**: the same thing linked to two owners. If the screen does not allow building it, build it through the API and say so in the report.
- **Full life cycle** with the entity of the change active in the middle: create, associate, edit, transfer between users, finish, reopen, delete.
- **Another user with the same role**: cases that depend on "it is with someone else".
- **Every report and export** that shows or counts the entity: screens, CSV, history view, counts (unique, lost, totals). The numbers get checked against the database.
- **Error messages and warnings** shown to the user on failure paths.
- **Permissions per role**: what only the supervisor/admin sees or does.

## Case format

```markdown
### 3.4 24-hour window with a recent message ⬜
**Validates:** a customer who just wrote can receive free text.
**Proof:** text field enabled, no template warning; last-received record present in the database.
**Control:** same case with the old identifier.
**Layer:** front end + database.
```

Status: ✅ passed · 🔴 failed (bug #) · 🚫 blocked (reason + **what unblocks it**) · ➖ not applicable (reason) · ⬜ not tested.

**Layer:** what can be proven by a request or a query does not need the browser. Use the front end for display, interaction and user flows.

## Fix mode

The first section of the test plan is the bug itself: the exact case from the report, plus variations of it, each with the evidence that tells "still broken" from "fixed". Then comes the neighbourhood of the fix and the controls.

## Closing the phase

1. Write `cases.md`.
2. Show the user the size of the plan (sections and number of cases) and what it depends on (credentials, manual cases). **Confirm the scope** before executing.
3. If the user will run it alone, deliver the plan and stop here.
