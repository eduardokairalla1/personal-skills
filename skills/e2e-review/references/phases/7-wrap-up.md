# Phase 7 — Wrap up

Goal: leave the environment as it was, with no stuck sessions, and the user knowing what is left.

## Steps

1. **Revert all instrumentation** recorded in `environment.md` (configs, proxy redirections, temporary flags).
2. **Prove it was reverted**:
   - running config back to its original values;
   - proxy processes dead and ports free;
   - no frozen process (state `T` in `/proc/<pid>/status`);
   - restarted services healthy.
3. **Log out every parallel session** (headless) through the product menu. A session that dies without logging out keeps receiving work.
4. Close the tabs you opened in the user's browser, unless they want to keep them.
5. Update the memory: `change.md` with phase "done" and what is pending.
6. Tell the user, in a few lines:
   - where the report is and the headline numbers;
   - what is left manual (something physical/real) and what only they can unblock (credentials, accounts, flags);
   - relevant test data left in the environment, in case they want to clean it up.
