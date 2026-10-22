# Phase 3 — Environment

Goal: make sure the environment runs the code under test, that you can observe everything the test plan needs to prove, and that every change is reversible.

Half of the red results of a first round are environment, not code.

## Steps

1. **Read the environment rules** in the project's CLAUDE.md: where each command runs, what may be restarted, what is forbidden.
2. **Versions.** For each service, compare the running image/tag or process with the HEAD of the branch. A mismatch goes into the scope section of the report.
3. **Observation.** Build a helper with subcommands for what you will query hundreds of times: each service's API, SQL, document database, logs filtered by time window. See `references/instrumentation.md`, section "Observation queries".
4. **Configuration of the accounts/entities the test plan uses.** Read it before executing: an account without the feature configured looks like a bug later.
5. **Instrumentation**, only if the plan needs it and always reversible: a recording proxy to see what goes out to external APIs, freezing a process for "service down or slow". See `references/instrumentation.md`. Record in `environment.md` **what was done and how to undo it before doing it**.
6. If you will drive the front end, prepare access (the user's Chrome or headless) — see `references/browser.md`, sections "The user's Chrome" and "Headless browser".
7. Record it in `environment.md` and move to phase 4.

## Pitfalls of this phase

| Symptom | Cause | What to do |
|---|---|---|
| Service unreachable from the host | Only exists on the internal network | `docker exec <other-container> curl ...` |
| `kill` does not exist in the container | Minimal image | `kill -STOP/-CONT` from the host with the PIDs from `docker top` |
| ssh session drops when killing a process | `pkill -f` matched the ssh command line itself | PID in a file, `kill $(cat pidfile)` |
| Edited config reverts on restart | File rendered from a template at boot | Edit the template (with a backup) and restart |
| Reverse proxy 404 right after a restart | Service not healthy yet | Wait for the healthcheck with an `until` loop |
| A database change has no effect | State loaded into memory at boot | Restart the service (and use it as a persistence test) |
| Container IP changed | Container was recreated | Look the IP up again before pointing callbacks at it |
| Table/collection "does not exist" | Different name or authentication | `show tables`, `describe`, database credentials |
| A feature "does not work" on an account | Account lacks the required configuration (workflow, agents, flag) | Read the config first; use the right account |
| Empty screen (e.g. a board with no columns) | Feature enabled but not configured | Configure the minimum through the admin screen and record it |
| The automatic permission check denied a change | Shared resource | Stop, explain, let the user decide |
