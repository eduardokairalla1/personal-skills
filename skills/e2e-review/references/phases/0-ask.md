# Phase 0 — Ask

Goal: have all the context needed to investigate, without assuming anything that changes the work.

Everything that follows starts here. Assuming the wrong branch, the wrong executor or what may be changed costs hours and frustrates the user.

## Steps

1. Read the conversation and the repository. **Do not ask what is already answered** or discoverable (current branch, remotes, CLAUDE.md, previous memory in `~/.claude/memory/e2e/`).
2. Ask **a single round** with what is missing (AskUserQuestion with up to 4 questions, or one message with a numbered list).
3. Record the answers in `change.md` and move to phase 1.

## Checklist of what must be clear

| Topic | What to know |
|---|---|
| Type | New feature or fix? If a fix: what the bug is, how it shows up, where it was seen, how it reproduces today, which branch has the fix |
| Code | Which services/repositories changed, which branches or MRs, which base to compare against |
| Environment | Is the environment already running those branches/images? Who starts/stops services? May I restart them? |
| Who executes | Does the AI run everything, or only design the scenarios while the user runs them? Is there a part the user wants to do? |
| Access | Users for each role (e.g. operator, supervisor, **a second user with the same role** for "it is with someone else" cases), external accounts (real or sandbox) |
| Browser | May I use the user's main browser? With which login? |
| Limits | What I may change: config, accounts, flags, test data. What I must not touch |
| Manual | What depends on something physical or real (phone, payment, real e-mail) and is left for the end |
| Report | Who reads it, format (default: facts-only .md, no cause and no fix), where to save it |

If the user says "you decide", decide, record the decision and move on.

## Pitfalls of this phase

- **"I'll test it, I only want the scenarios."** This happened because nobody asked who executes. If the user runs the tests, the deliverable becomes the test plan (phase 2) with what they need to run it — stop there.
- **Credentials that only come up halfway.** Cases with two users of the same role, partner accounts, feature flags. Ask now, even if they are only used in phase 4.
- **Environment running different code than expected.** Ask whether the environment already runs the versions under test; phase 3 checks it, but it is better to know early.
