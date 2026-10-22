# Phase 4 — Execute

Goal: run the cases of the test plan section by section, collecting the evidence each one calls for.

Phases 4 and 5 alternate: run a section, triage its red results (open `5-triage.md`), update `cases.md` and `findings.md`, post a status in the chat and move to the next section.

## By request

- Build payloads from the personas, with a new identifier every round. A simple generator (a script with one subcommand per event type and flags to drop or swap fields) pays for itself by the second section.
- Send **in sequence** unless the case is about concurrency; concurrent sends shuffle the order because of the test, not the change.
- To see what the change sends out, read the recording proxy log (phase 3). To force responses (failure, callback missing a field), use the control file of `scripts/recording_proxy.py`.

## Through the front end

Read `references/browser.md` before the first section that uses the front end.

- Act as the end user: the same click path, not a shortcut.
- In the user's main browser, use the agreed login. Before switching users ("Log out") or any click that may look destructive, say what you are about to do.
- Parallel users (a second user with the same role, the supervisor) go in a **headless browser**, always logged out at the end.
- Reload the page (F5) in at least one case per screen: what shows live and what comes from the backend may differ.

## Collecting evidence

For each case, keep one line that proves the result: log excerpt, query result, request body, screen text, URL. Screenshots only when the proof is visual.

## Fix mode

1. **Before the fix**: run the bug cases on the version without the fix and record the red result with the same evidence the report will use. Without that red result, the green one afterwards proves nothing.
2. **After the fix**: the same cases on the fixed version — they must turn green **for the right reason** (the observation that failed now passes).
3. Neighbourhood and controls.

## Pitfalls of this phase

| Symptom | Cause | What to do |
|---|---|---|
| `/chrome` empty, no Chrome tools | Session started without the integration | The user quits and comes back with `claude --chrome --resume`, then `/chrome` |
| Placeholders in English in headless mode | Default locale | Set `locale` or select by input type |
| "strict mode violation" in Playwright | Text matches several elements | `get_by_role(..., exact=True)` |
| A click does nothing | Modal still closing, tooltip on top, element off screen | Wait, move the mouse away, click via JS |
| Wrong number typed in a masked field | Fixed prefix of the mask | Delete, check what is left, type the rest |
| "Copied!" but the clipboard does not change | Window without focus | Intercept `navigator.clipboard.writeText` |
| Screen of another entity/tab after an action | The front end picks the tab/entity by its own rule | Check the URL and the tab tooltip before acting |
| Supervisor login as operator returns 401 | Different roles | Ask for credentials of another user with that role |
| New work goes to a user who "left" | A session closed without logout still counts as online | Always log out through the menu; if it happened, log in and out again |
| The entity disappears mid-test | Product inactivity timeout | Find out the timeout; keep steps short |
| Data you did not create shows up | Real traffic in the environment | Do not touch it; filter by your identifiers |
| Message dropped or absurd date | Wrong timestamp unit | Check the unit of each integration |
| Callback/ack has no effect | Arrived outside the service's waiting window | Fire it right after the response (proxy callback) |
| Order swapped | Concurrent sends | Send in sequence |
| Huge command output | DEBUG logs, JSON | `grep`, `cut -c1-300`, `limit` |
| Download blocked | Downloads need authorisation | Read the generated content in the page; the real file is left for the user |
