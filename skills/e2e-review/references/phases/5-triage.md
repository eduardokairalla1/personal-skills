# Phase 5 — Triage

Goal: every red result explained and put in the right box. An unexplained red result is a potential bug you chose to ignore.

## The four boxes

| Box | How to recognise it | Goes to |
|---|---|---|
| Bug in the change | The control (old flow) passes; the change fails | `findings.md` → Bugs in the report |
| Pre-existing behaviour | The control fails the same way | Observations in the report |
| Invalid test data | The data does not satisfy a real rule (format, range) | Redo in phase 2/4 with realistic data |
| Environment | Neighbouring service down, account misconfigured, product timeout | Environment issues; work around and redo |

## Steps for each red result

1. **Read the service log and the network response**, not just the screen. "Failed to load" may be another service with no database.
2. **Run the control**: the same case with the old flow (old identifier, account without the change). If the control behaves the same, it is not a regression of the change.
3. **Run it in isolation** if it failed in a series: passing alone and failing in a series means interference between cases.
4. If invalid data is suspected, redo it with realistic data before concluding.
5. Record it in `findings.md`: title by effect, steps, expected, actual, evidence, control. A finding number is never reused.

## A suspicious green is red

Before accepting a green result, ask: if the change were broken, would this case fail? If you do not know, it proves nothing — fix the proof.

## Bug reported by the user

If the user describes a bug you did not catch: ask for the exact sequence, reproduce it without adapting it, run the control and show both results. Do not conclude from a similar sequence.

## Pitfalls of this phase

- **A strange number in a report.** Compare with the equivalent database query for the same period before calling it wrong; sometimes the count is by a different entity (contact × customer), and that is the finding.
- **A hypothesis about the cause.** The cause belongs to the developer. Here you record the behaviour and the evidence.
