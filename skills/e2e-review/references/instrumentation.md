# Environment instrumentation

Instrumenting is what lets you see what the change really sends and simulate what is hard to trigger. All instrumentation is temporary: record in `environment.md` what was done and how to undo it **before** doing it, and revert it at wrap-up.

## Rules

- Follow the project's CLAUDE.md on where each command runs and what may be restarted. When in doubt, ask.
- Prefer changing things **inside** the container/process (temporary file, template edited with a backup) over changing the shared deploy repository.
- Do not create or change accounts, credentials, flags or shared configuration without explicit authorisation from the user. Automatic permission check denied = stop and ask.
- After reverting, prove it: original config back, proxy process dead, port free, no process in state `T` (stopped).

## Recording proxy

To see the real body the change sends to an external API (and control the response), put a proxy between the service and the API. `scripts/recording_proxy.py` does it:

- records each request (method, path, body) as JSON Lines;
- for configured routes, answers a stub instead of forwarding (useful when the external account is real and the identifier is fictitious);
- forwards everything else to the real upstream;
- optionally fires a callback (e.g. the status/ack webhook) after answering, with fields overridden by a control file — to test missing acks, missing fields, failures.

Steps:

1. Find out how the service reads the external API URL (static config, template rendered at boot, environment variable).
2. Start the proxy on a host the service can reach (e.g. the docker network gateway, `172.x.0.1`) and test connectivity **from inside** the container.
3. Point the service at the proxy (back up the original), restart if needed and wait for the healthcheck.
4. Run the cases reading the proxy log.
5. Revert the redirection, restart, confirm the original URL and kill the proxy.

Keep the PID in a file (`echo $! > /tmp/proxy.pid`) and kill by it. `pkill -f <name>` run over ssh can match the ssh command line itself and drop the session.

## Simulating a service down or slow

Do not take containers down: they lose their network alias and the orchestrator may recreate them, poisoning the following cases. Freeze the process instead:

```bash
PIDS=$(docker top <container> -eo pid | tail -n +2 | tr '\n' ' ')
kill -STOP $PIDS   # from the host; the container may not have `kill`
# ... run the case ...
kill -CONT $PIDS
```

Frozen, the service accepts connections and does not answer — the most realistic "slow/down" scenario (callers' timeouts show up). Measure the response time of whoever depends on it and compare with a control that does not.

For "restart" (persistence), restart the process/container as the project rules allow and wait for the healthcheck before the next step.

## In-memory state × database

Services often load state from the database at boot and then work in memory. Editing the database to age a value (e.g. "last message 48 h ago") only takes effect after restarting the service. This is also a good persistence test: the value must come back the same after the restart.

## Observation queries

Build a helper with subcommands for what you will query repeatedly: each service's API, SQL, document database, logs by time window. Always filter (`grep`, `cut -c1-300`, `limit`) — DEBUG logs and large JSON blow up the output.

If a service is not reachable from the host, query it from inside another container on the same network (`docker exec <other> curl http://<service>:<port>/...`).

Discover the schema before querying (`show tables`, `describe`, collection names) — table names and credentials are rarely what you imagine.

## Test data

- Build the state that is hard to build through the screen (e.g. the same entity under two owners) through the service API, and say in the report that it was built that way.
- Keep track of what you created so you can tell it apart from the real data in the environment. Do not delete anything you did not create.
