---
name: review
description: "Review the changes since a fixed point (commit, branch, tag or merge-base) along three axes: Standards (does the code follow the repo's documented guidelines, my personal baseline and the smell list?), Spec (does it do what the issue, PR or spec asked?) and Build (do lint, typecheck and tests pass on this head, with more than zero tests run?). Runs the three in parallel sub-agents, verifies every finding with a triage sub-agent, applies what needs no decision and reports the rest as block / round / nit. Use on personal projects when the user wants to review a branch, a PR, work-in-progress changes, or says \"review since X\". Invoke with /review <fixed-point> [spec path]."
---

# Review

Three-axis review of the diff between `HEAD` and a fixed point the user
supplies:

- **Standards**: does the code follow the repo's documented guidelines, the
  personal baseline in `references/standards.md` and the smell list in
  `references/smells.md`?
- **Spec**: does it faithfully implement the originating issue, PR or spec?
- **Build**: do the repo's lint, typecheck and test commands pass on this
  head, and do the tests actually run?

The three axes run as **parallel sub-agents** so they do not pollute each
other's context. Every finding then goes to one **triage sub-agent**, which
checks it against the real code before anything is applied or reported.

The skill is language-agnostic: Python, TypeScript, Go, Dart, Java, shell.
Everything it needs about the repo comes from the repo itself (guidelines,
lint configs, scripts), never from assumptions about a host or a container.

## 1. Pin the fixed point

Whatever the user said is the fixed point (a sha, branch, tag, `main`,
`HEAD~5`...). Without one, ask.

```bash
git rev-parse --verify "<fixed-point>" >/dev/null   # must resolve
git log --oneline <fixed-point>..HEAD                # commit list
git diff <fixed-point>...HEAD --stat                 # must be non-empty
```

Three-dot, so the comparison is against the merge-base. A bad ref or an
empty diff fails here, not inside three sub-agents.

Also record whether the code is the user's own: the author of the commits
(`git log --format=%ae <fixed-point>..HEAD`) or the PR author on the host is
the user. This decides step 6.

## 2. Find the spec

In this order; the first hit wins:

1. A path the user passed as an argument.
2. Issue or PR references in the commit messages (`#123`, `Closes #45`,
   `!67`), fetched from the host (`gh issue view`, `gh pr view`, `glab
   issue view`, `glab mr view`).
3. A document in the repo that describes the change: `docs/` (a roadmap,
   an ADR, a feature note), `.scratch/`, a plan beside the branch name.
4. Ask the user. If there is none, the Spec axis is skipped and the report
   says "no spec available".

## 3. Find the standards

Three layers, loaded in this order; a lower layer never contradicts a
higher one:

1. **The repo's own documents.** Look for, and pass the **paths** of,
   whichever exist: `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`,
   `docs/code-guidelines.md`, `docs/guidelines.md`, `docs/development.md`,
   a `STYLE*` or `CODING*` file, and the per-package equivalents under
   `backend/`, `frontend/`, `src/`. The repo is canonical: where it
   overlaps the baseline, the repo wins.
2. **The personal baseline**, `~/.claude/skills/review/references/standards.md`.
   Rules carry ids (`G1`, `D2`, `K2`...) so findings can cite them.
3. **The smell baseline**, `~/.claude/skills/review/references/smells.md`.
   Always a judgement call ("possible Feature Envy"), never a hard
   violation.

Also note the tooling, so the Standards axis skips what it already
enforces: `pyproject.toml` (ruff, mypy), `eslint.config.*`, `.prettierrc*`,
`tsconfig.json`, `.editorconfig`, `go.mod` (gofmt, vet).

## 4. Spawn the three sub-agents in parallel

Send all three in one message. Each returns every finding as one line:
`[Standards|Spec|Build] <file>:<line> — <finding> — <rule id, spec line or
command output>`. They fix nothing.

**Standards sub-agent** (`general-purpose`). Give it the diff command, the
commit list, the paths from step 3 and the tooling note. Brief:

> Read every standards file in full before looking at the diff. Then, per
> file and hunk, report (a) every breach of a documented repo standard or
> of the personal baseline, citing the file and rule id (`docs/
> code-guidelines.md › Docstrings`, `standards.md › C1`); (b) every smell
> you spot, named and with the hunk quoted; (c) the commit messages
> against the commit rules (`K1`–`K5`: atomic, imperative, 50 characters,
> no prefix, no period, no AI attribution). Distinguish hard violations
> (documented standard) from judgement calls (smells, taste). Skip
> anything the linter, formatter or type checker already enforces. When the
> diff creates a module modelled on an existing one in the same repo (a
> new domain beside an old one, a new route, a new error class), read the
> exemplar and list every validation, limit, transition and error handling
> the exemplar has and the new module lacks; each absence is a finding
> with the exemplar's `file:line`.

**Spec sub-agent** (`general-purpose`). Give it the diff command, the commit
list and the spec (path or fetched text). Brief:

> Report (a) requirements the spec asks for that are missing or partial;
> (b) behaviour in the diff the spec did not ask for (scope creep); (c)
> requirements that look implemented but whose implementation looks wrong.
> Quote the spec line for each finding.

Skipped when there is no spec.

**Build sub-agent** (`general-purpose`). Give it the commit list and the
packages the diff touches (derived from its paths). Brief:

> For every touched package, find the lint, typecheck and test commands in
> what the repo documents, in this order: `CONTRIBUTING.md`, `README.md`,
> `docs/development.md`, a `scripts/test` or `Makefile` target, then the
> tool configs (`package.json` scripts, `pyproject.toml`, `go.mod`). Run
> each one on this head, the way the repo says to (locally, through `uv
> run`/`npm`/`go`, or inside the dev container if that is what the docs
> prescribe). Lint and typecheck may run on the touched files; the test
> suite runs whole. Report one line per command: the command, the exit
> code and the last meaningful line of output. A non-zero exit is a
> finding. A run that reports zero tests (`Ran 0 tests`, `0 passed`, `no
> test files`) is a finding too: a green run that tests nothing is not a
> gate. Never edit code, never install anything globally, never leave the
> tree changed.

Each Build finding is a 🔴 block when it is a build error, a type error or
a failing test, and a 🟡 round when it is lint or a zero-test run. The
triage sub-agent takes them as already verified: the command output is the
evidence.

## 5. Triage

When the three return, spawn **one triage sub-agent** (`general-purpose`)
with the diff command, the commit list, the spec path and every finding,
verbatim. Its brief:

1. **Group** the findings by file and hunk; drop exact duplicates between
   axes, keeping both axis tags on the merged line.
2. **Verify in parallel.** One verifier sub-agent (`Explore`) per group, all
   in a single message. Each verifier reads the real code around the hunk,
   not just the diff, and, when a finding depends on a contract between
   two parts (a request, a payload, an event, a schema), reads the other
   side too. It answers per finding: `holds` / `does not hold` /
   `depends`, with `file:line` evidence in one line. For every test the
   diff adds or changes, the verifier also **mutates** the function under
   test (invert the return, swap an argument, return the mock empty), runs
   only that test with the repo's runner, and reverts (`git checkout --
   <file>`). A test that stays green against the mutated code is a finding
   that holds, 🟡 round, "test passes regardless of the code", citing
   `standards.md › Te3`.
3. **Decide** from the verifier's answer:
   - `does not hold` → **discarded**, with the one-line reason.
   - `holds` and there is exactly one obvious fix (a comment reworded, a
     rename the standard dictates, a missing guard, a docstring tag) →
     **apply**.
   - `holds` but the fix has more than one reasonable shape, changes
     behaviour or a contract, or contradicts the spec → **decide**: the
     user chooses.
   - `depends` → **decide**, stating what it depends on.
4. **Classify** everything not discarded:
   - 🔴 **block**: wrong behaviour, a bug, a broken contract, a spec
     requirement missing or wrong, a failing build. Cannot merge as is.
   - 🟡 **round**: a hard violation of a documented standard or of the
     baseline, lint, a zero-test run. Fix in this round.
   - 🟢 **nit**: a judgement call: smells, naming taste, cosmetics.
5. **Return** three lists, each line `<emoji> [axis] <file>:<line> —
   <finding> — <fix or question>`: **apply** (with the exact fix),
   **decide** (with the question and a recommendation) and **discarded**.

If the triage sub-agent has no `Agent` tool, it returns the groups; this
skill spawns the verifiers itself and sends their answers back to it.

## 6. Apply and report

Apply every **apply** item in the user's current branch, without asking,
**only when the code is the user's own** (step 1). On someone else's PR,
apply nothing: those items are reported as 💬, a comment to leave on the
PR with the exact fix.

Then report, grouped by severity, the axis tag kept on every line so one
axis never hides behind another:

```
## 🔴 Block
- ✅ [Spec] src/rooms/room.service.ts:42 — <finding> — applied
- ❓ [Standards] src/config.py:10 — <finding> — <question>

## 🟡 Round
## 🟢 Nit

## Discarded
- [Standards] src/rooms/room.utils.ts:7 — <finding> — <reason>
```

`✅` applied, `💬` left as a PR comment, `❓` waiting for the user. Leave
out an empty section. End with one line of counts per severity and per
axis. Then bring the `❓` items to the user **one at a time**, 🔴 first.

Applied fixes stay uncommitted: the user decides how they fold into the
history (a fixup into the original commit, usually).

## Why three axes

- Code that follows every standard but implements the wrong thing:
  Standards pass, Spec fail.
- Code that does exactly what was asked but breaks the conventions: Spec
  pass, Standards fail.
- Code that reads right on both and still does not compile, or ships tests
  the CI never runs: Standards and Spec pass, Build fail.

Tagging each finding with its axis, even after triage groups them by
severity, stops one axis from masking another.
