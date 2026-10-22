---
name: retrofit-commit
description: Retrofits uncommitted refactors into the existing commits of a feature branch, so the history reads as if the code had been written correctly from the start. Use when the user has already committed a feature and then refactored/fixed/adjusted that same code, and wants those changes folded back into the original commits instead of appended as new ones. Triggers on "fix commits", "fixup", "dar fixup", "jogar essa mudança pro commit original", "rebase -i", "reescrever a história", "como se tivesse sido feito desde o começo", "esse arquivo não deveria existir", or any request to reorganize/rewrite an existing branch's history.
---

# retrofit-commit

The user built a feature across many commits, then refactored that same code. The refactor must disappear into the original commits: whoever reads the final history should see the feature built correctly the first time, with no trace of the intermediate design.

This is NOT `atomic-commit` (which organizes new work into new commits). Here every change is absorbed into commits that already exist.

## The two modes

Decide this first — it changes everything downstream.

**Fixup mode.** The original commits were right, they just need adjusting. Let git name and place the commits for you: `git commit --fixup=<target-sha>` produces `fixup! <subject>`, and `git rebase -i --autosquash <base>` positions and marks every one of them on its own. No hand-written todo, no sequence editor, nothing to get wrong. The target commit survives.

**Rewrite mode.** The refactor says something *should never have existed* — a module deleted, a function that moved, a layer collapsed. A fixup cannot express this: it only adds a later diff, so the artifact still appears and then disappears. You must rewrite the original commits so the artifact never appears at all, which may drop, split, reorder or rename them.

The tell: if the user says "that file doesn't exist anymore, so that commit shouldn't exist either", they want rewrite mode. **Ask which mode when a deletion or a move is involved** — fixup mode silently produces a create-then-delete history, which is exactly what they are trying to avoid.

## The three rules that prevent every conflict

These were learned the hard way. Violating any of them produces cascading conflicts that are not worth "resolving" — restructure instead.

**Rule 1 — a fixup can only touch code that exists at its target.**
The fixup is applied at the target commit's position. Files created by *later* commits do not exist there. Before committing anything, verify:

```bash
for f in $(git diff --cached --name-only); do
  git cat-file -e <target>:"$f" 2>/dev/null || echo "NOVO: $f"
done
```
"NOVO" is fine only for files the fixup itself creates, or files created by an earlier fixup in your own sequence.

**Rule 2 — code you delete must be deleted at or after the last commit that touches it.**
If commit #35 edits `_dequeue`, you cannot delete `_dequeue` in a fixup at #8: #35 will fail to replay. Find the real last toucher:

```bash
git log --reverse --format='%h %s' <base>..HEAD -S'<symbol>' -- <paths>
```

**Rule 3 — the fixup's diff carries context from the branch tip, not from the target.**
Even with the right target, if neighbouring lines changed between target and tip, the 3-way merge conflicts. The safe default: **target the last commit that touches that file**, so tip content and target content are identical. Check with:

```bash
git log --reverse --format='%h %s' <base>..HEAD -- <file>
```

When rules 2/3 push a change onto a late commit, semantic precision suffers. Say so explicitly rather than silently accepting a bad attribution — and offer reordering (below) as the fix.

## Reordering beats splitting

When a change makes commit A depend on something introduced later in commit B, the instinct is to split the change in two. Usually the right answer is to **move B before A** and let A be born correct.

Concretely: `bootstrap` was introduced before `upsert`, and the refactor made `bootstrap` call `upsert`. Splitting gives two half-changes; moving `upsert` earlier gives one complete change and a history where `bootstrap` never had the inline version. Prefer the reorder. When you reorder, the moved commit may have to take over creating a file the other one used to create.

## A broken intermediate commit is worse than a conflict

A conflict costs the user a minute. A commit that imports a symbol that no longer exists breaks `git bisect` silently. Never remove a function in an earlier commit than its callers — keep the old code alive, duplicated if necessary, until the commit that removes its last caller. Transient dead code and transient duplication are acceptable; a broken import is not.

## Execution

Work on the branch, not in your head.

**Confirm where you are, and that nobody moved it.** The user may be working in this repo from another terminal while you plan. Never trust a branch name you read minutes ago:

```bash
git symbolic-ref -q HEAD || echo "DETACHED"
git reflog HEAD --date=iso | head -10
```

`git status -sb` printing `## HEAD (no branch)` usually means someone ran `git checkout origin/<branch>` — checking out a remote-tracking ref detaches HEAD. If the reflog shows `wip`, `reset` or `commit` entries that are not yours, the tree you analysed is not the tree you are about to rewrite: re-read before continuing.

Snapshot **immediately before the rebase**, not at the start of the analysis — otherwise you back up a state the user has since moved past, and restoring it would destroy their work. This is what lets you restart without losing anything:

```bash
git add -A
T=$(git stash create "target"); git update-ref refs/tmp/target "$T"; git reset
git update-ref refs/tmp/backup HEAD
```

`refs/tmp/target` is the ground truth for the final state. Every verification compares against it.

Then reset the working tree and rebuild the commits forward, one per target, **in the chronological order of their targets** so their diffs stack correctly.

### Dry-run the rebase before handing it over

Never hand the user a sequence you have not replayed. In fixup mode there is no todo to write — replay on a throwaway branch, compare against the snapshot, then run the same command for real:

```bash
git checkout -q -B tmp/test HEAD
GIT_SEQUENCE_EDITOR=true GIT_EDITOR=true git rebase -i --autosquash <base>
git diff refs/tmp/target tmp/test --stat    # must be empty
```

Zero conflicts is the target. If it conflicts, do not resolve — go back and fix the targets.

When handing over, drop `GIT_SEQUENCE_EDITOR` and let the user's editor open: autosquash arrives with the plan already positioned, so they only read and save instead of typing `fixup` on N lines.

### Writing the todo by hand (rewrite mode only)

Only rewrite mode needs a `GIT_SEQUENCE_EDITOR` script — autosquash cannot drop, split, reorder or rename commits.

**The todo format is not `pick <sha> <subject>`.** Git 2.55 writes the subject behind a `# `, and appends ` # empty` to empty commits:

```
pick aa083ba # first subject
pick 15dc91b # second subject # empty
```

So never match on subject text; the sha is the only stable field. Key your target map by sha.

**Assert the parse before writing the file.** If the number of `pick` lines you recognised is not `git rev-list --count <base>..HEAD`, abort saying exactly that. A parser that recognises nothing writes back an unchanged todo, and the rebase then runs the *original plan* — a silent success indistinguishable from a real one. Word the failure after the cause: "parsed 0 of 26 pick lines" points at the format, while "could not find my fixup lines" sends you hunting through subjects that were never the problem.

`sed -i` is the obvious way to write these scripts and usually works. On some mounts it does not — sshfs, for one, refuses the permission-preserving rename and prints `sed: preserving permissions for '.git/rebase-merge/sedXXXX': Operation not permitted`, after which the todo is silently unedited and the rebase runs the *original* plan. If you see that, or if a rebase completes without doing what you asked, rewrite the editor in Python (`open(path).read()` → transform → `open(path,'w').write(...)`), which edits in place and does not touch permissions.

The same message on a *source* file (`sed: preserving permissions for 'src/sedXXXX'`) is harmless noise — the content is written. Confirm with `git diff` rather than trusting or distrusting the message.

### The `--amend` trap

At a rebase stop, **check whether the commit exists before amending**:

```bash
git log --oneline -1 && git status --short
```

- Stop with a clean tree (an `edit` that applied): the commit exists → `git commit --amend` is correct.
- Stop with conflict markers (`UU`/`DU`/`AA`): the commit does **not** exist yet → `--amend` will silently fold your work into the *previous* commit and destroy the one being applied. Resolve, then `git commit -C <original-sha>` to create it with its original message and author.

This mistake is easy to make and hard to spot afterwards. Check every time.

### Regex on conflict blocks

If you script conflict resolution, beware patterns like `(?:\s+'.*?\n)*` meant to match a key's continuation lines — they happily eat the *following* entries too. Always diff the result against `refs/tmp/target` afterwards; that check is what catches it.

## Verification (all of it, every time)

```bash
# 1. final tree must equal the snapshot
git diff refs/tmp/target HEAD --stat        # must be empty

# 2. every commit must parse
for c in $(git rev-list <base>..HEAD); do
  for f in $(git show --pretty= --name-only --diff-filter=ACMR $c | grep '\.py$'); do
    git show "$c:$f" | python -c "import ast,sys; ast.parse(sys.stdin.read())" || echo "ERRO $c $f"
  done
done

# 3. no commit may import a symbol that does not exist there (bisect safety)
#    resolve the module path and look for def/class/assignment — not just `def`

# 4. in rewrite mode, the removed artifacts must appear in ZERO commits
git log --oneline <base>..HEAD -S'<symbol>' -- conversis/ tests/
git log --oneline <base>..HEAD -- <deleted-file>
```

Run these as separate one-purpose commands rather than one block. Permission classifiers routinely deny long compound shell scripts, and a denial halfway through verification is indistinguishable from a failure.

Distinguish problems you introduced from ones that were already there: re-run the check against the pre-rewrite backup before reporting anything as a regression. Report pre-existing issues as pre-existing.

## Sibling branches

Stacked branches (`eduardo/feature-part-1`, `part-2`) point into the middle of this history. Two ways to keep them right:

- Rebase from a base *after* them, so their commits are never rewritten — simplest when all targets are late.
- `--update-refs`, which moves them along. It composes with everything else: `git rebase -i --autosquash --update-refs <base>`.

Find them first — a ref you did not notice is a ref you orphan — and back up the ones inside the range:

```bash
for r in $(git for-each-ref --format='%(refname:short)' refs/heads); do
  git merge-base --is-ancestor "$r" HEAD 2>/dev/null &&
  git merge-base --is-ancestor <base> "$r" 2>/dev/null &&
  echo "$r $(git log --oneline -1 "$r")"
done
git update-ref refs/tmp/backup-<sibling> <sibling>
```

Afterwards confirm they are still ancestors:

```bash
git merge-base --is-ancestor <sibling> HEAD && echo OK
```

All of them need a force-push once rewritten. Say so.

## Reporting

Give the user a table of change → target commit. Call out explicitly:

- any target chosen for conflict-avoidance rather than semantics, and why
- commits that became empty and were dropped
- commits that were reordered, split or renamed
- what you could not verify (test suites that will not run in the environment)

Then leave the backup refs in place and tell them how to delete them:

```bash
git for-each-ref --format='%(refname)' refs/tmp | xargs -n1 git update-ref -d
```
