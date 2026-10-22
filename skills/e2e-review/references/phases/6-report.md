# Phase 6 — Report

Goal: a `.md` the responsible developer reads, reproduces and investigates without needing to ask anything.

**Observed facts only**: what was tested, what failed, how to reproduce it. No cause in the code and no suggested fix, unless the user asks for them — a wrong hypothesis written in the report sends the investigation the wrong way.

A fact is what was sent, what was expected, what happened, and the data that proves it (log line, database record, captured request body, screen text). An interpretation of the code is not a fact.

Write the report **in the user's language** (translate the headings of the template below).

## Template

````markdown
# QA report — <change>

Test date: <yyyy-mm-dd>, in the <name> environment.

How it was executed (short list: requests, screens, roles, where it was checked).

This document records observed facts only: what was tested, what failed and how to reproduce it. Investigating the cause is up to the responsible developer.

## Summary

| Result | Scenarios |
|---|---|
| Passed | N |
| Failed | N |
| Blocked | N |
| Not applicable | N |
| **Total** | **N** |

The N failed scenarios correspond to **M bugs**:

| # | Bug | Where it shows |
|---|---|---|
| 1 | <effect in one line> | <observable surface: screen, webhook, report> |

## Scope

| Service | Branch | Version under test |
|---|---|---|

Mismatches between what runs and the code.

## Environment and method

- Accounts/users used (no passwords).
- Personas and what each one represents.
- Temporary instrumentation used, and that it was reverted.
- Preconditions checked.

---

## Bugs

### Bug 1 — <title by effect>

**Scenarios:** <numbers>.

**How to reproduce**

1. step
2. step (full payload in a code block when it is a request)

**Expected:** …

**Actual:** …

**Evidence**

```
<log / query / captured body>
```

**Control:** the same case with the old flow, and its result.

---

## All tested scenarios

Legend: ✅ passed · 🔴 failed (bug shown) · 🚫 blocked · ➖ not applicable.

### 1. <section>

| # | Scenario | Result |
|---|---|---|
| 1.1 | <what was done and what was seen> | ✅ |

## Observations that are not bugs of the change

## Environment issues

## Not tested

(reason and what would unblock it)
````

Drop empty rows and sections (e.g. "Blocked" when there are none).

## Writing rules

- A bug title describes the **effect** ("Front end asks for a template with a message received 1 minute ago"), not the supposed cause.
- "Where it shows" is the observable surface, not the file.
- Steps someone else can follow without help, with the values used.
- A control for every bug that could be mistaken for old behaviour.
- A case that failed because of invalid data is not a bug: record only the result with valid data.
- No passwords, tokens or list of test data left in the environment, unless the user asks.

## Fix mode

Each case of the bug gets the table:

| Case | Before the fix | After the fix |
|---|---|---|
| <case> | 🔴 <evidence> | ✅ <evidence> |

## Closing the phase

1. Recount: `python scripts/count_status.py <file>` and compare with the Summary. Wrong counts undermine the credibility of everything else.
2. Save it where agreed.
3. If the user asks for changes, rewrite the whole file instead of patching pieces, and recount.
