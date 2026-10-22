---
name: open-pr
description: Use when the user asks to open a pull request (GitHub) or merge request (GitLab) for a branch — "open the PR", "open the MR for feature/x", "create the merge request". Detects the host from the remote, reads what the branch implements to write the title, and opens the PR on the upstream project using the repo's PR template when it has one, or the standard body (ticket, Based on, First commit) otherwise. Never pushes: if the branch is not on the remote, it asks the user to push first. Invoke with /open-pr [branch] [TICKET-123]; without a branch it uses the current one, without a ticket it asks whether to reference one.
---

# Open PR

Opens a PR (GitHub) or MR (GitLab) from a branch of the remote `origin` to
the project it was forked from, or to `origin` itself when it is not a fork.
Runs unattended except for the ticket question in step 2; if anything else
is ambiguous, stop without opening and say what was missing.

The skill **never pushes**. The branch must already be on `origin`, pushed
by the user; the skill only reads the branch and opens the PR.

"PR" below means both; the host decides the CLI (`gh` or `glab`) and the
reference syntax (`#83` or `!83`).

## 1. Host, branch and projects

The branch is the first argument that is not a ticket reference; without
one, the current branch.

```bash
BRANCH=${1:-$(git branch --show-current)}
git rev-parse --verify -q "refs/heads/$BRANCH" >/dev/null || { echo "no local branch $BRANCH"; exit 1; }
REMOTE=$(git remote get-url origin)
case "$REMOTE" in *github.com*) HOST=github ;; *) HOST=gitlab ;; esac
```

Then, per host:

```bash
# github
FORK=$(gh repo view --json nameWithOwner -q .nameWithOwner)
UP=$(gh repo view --json parent -q '.parent | select(. != null) | .owner.login + "/" + .name')
UP=${UP:-$FORK}
TARGET=$(gh repo view "$UP" --json defaultBranchRef -q .defaultBranchRef.name)
ME=$(gh api user -q .login)

# gitlab
FORK=$(printf %s "$REMOTE" | sed -E 's#^.*[:/]([^:]+/[^/]+)\.git$#\1#')
FORK_ENC=$(printf %s "$FORK" | jq -sRr @uri)
UP_ID=$(glab api "projects/$FORK_ENC" | jq -r '.forked_from_project.id // .id')
TARGET=$(glab api "projects/$UP_ID" | jq -r '.default_branch')
ME=$(glab api user | jq -r '.username')
```

Stop if `BRANCH` is `TARGET` or if there is already an open PR for the
branch:

```bash
# github (HEAD_REF is "$ME:$BRANCH" on a fork, "$BRANCH" otherwise)
gh pr list -R "$UP" --head "$HEAD_REF" --state open --json number -q '.[].number'
# gitlab
glab api "projects/$UP_ID/merge_requests?source_branch=$BRANCH&author_username=$ME&state=opened" | jq -r '.[].iid'
```

### The branch must already be on the remote

```bash
git fetch -q origin
REMOTE_SHA=$(git rev-parse -q --verify "refs/remotes/origin/$BRANCH")
LOCAL_SHA=$(git rev-parse "refs/heads/$BRANCH")
```

- No `REMOTE_SHA`: the branch was never pushed. **Stop** and tell the user
  to push it (`git push -u origin $BRANCH`) and run the skill again.
- `REMOTE_SHA` differs from `LOCAL_SHA`: the remote is behind (or ahead).
  **Stop** and tell the user which side is newer and to push (or pull)
  before running again. Opening a PR for a stale remote head is the one
  mistake this check exists to avoid.
- Same sha: continue. The PR is opened from `origin/$BRANCH`; every
  `git` command below reads `$BRANCH`, never `HEAD`, so the checkout the
  user is on does not matter.

## 2. Find the ticket

If a ticket reference (e.g. `TICKET-123`) is given in the arguments, use it
and skip the rest of this step.

Otherwise, ask the user whether the PR should reference a ticket. This is
the one question the skill asks.

- **Yes**: look the ticket up in the project management tool available
  (see below). If an explicit reference already appears in the branch name
  or in the commit messages, use it directly. If the lookup finds nothing,
  or more than one plausible match, ask the user which ticket it is, and do
  not open the PR until they answer.
- **No**: open the PR without a ticket. The body starts at the next line that
  applies, and the final message says that no ticket was linked.

### Looking the ticket up

Pick the tool in this order:

1. A project management tool reachable from this session, either as an
   installed skill (e.g. one for OpenProject) or as a connected MCP server
   (e.g. Linear, Jira, Asana, Notion): use its search to find the user's
   open tickets by the words of the branch name and of the commit subjects.
   With more than one such tool, prefer the one whose ticket format matches
   references already used in the repo's history.
2. Otherwise the host's own issue tracker:

   ```bash
   # github
   gh issue list -R "$UP" --state open --search "<words>" --json number,title
   # gitlab
   glab api "projects/$UP_ID/issues?state=opened&search=<words>" | jq -r '.[] | "\(.iid)\t\(.title)"'
   ```

A single match is the ticket; show it to the user in the final message so
they can see what was linked. Several matches or none: ask.

## 3. Find the base PR

The branch is stacked when the head of another open PR on the upstream, by
any author, is contained in it and is not yet in `TARGET`:

```bash
# github
git fetch -q "$(gh repo view "$UP" --json sshUrl -q .sshUrl)" "$TARGET"
gh pr list -R "$UP" --state open --limit 100 --json number,headRefOid \
  -q '.[] | "\(.number) \(.headRefOid)"'

# gitlab
git fetch -q "$(glab api "projects/$UP_ID" | jq -r .ssh_url_to_repo)" "$TARGET"
glab api "projects/$UP_ID/merge_requests?state=opened&per_page=100" \
  | jq -r '.[] | "\(.iid) \(.sha)"'
```

`UP_HEAD=$(git rev-parse FETCH_HEAD)` right after the fetch.

A candidate is a PR whose head sha is in the branch
(`git rev-list -1 <sha> --not $BRANCH` is empty) and not in `TARGET`
(`git rev-list -1 <sha> --not $UP_HEAD` is not empty). With several
candidates, pick the one closest to the branch head (smallest
`git rev-list --count <sha>..$BRANCH`). `BASE` is that PR's head sha, or
`UP_HEAD` when there is no candidate.

## 4. Understand the branch, then build title and body

Read what the branch actually does before naming it:

```bash
git log --reverse --format='%h %s%n%b' $BASE..$BRANCH
git diff --stat $BASE..$BRANCH
git diff $BASE..$BRANCH
```

Read the full diff, not only the commit subjects: a commit titled "Fix
tests" may carry the real change. Note the entry points touched (routes,
handlers, commands, components), new or changed behaviour, and anything
removed. This is what the title and the body summary come from.

- First commit: `git log --reverse --format=%s $BASE..$BRANCH | head -1`.
- Title: one sentence in English, imperative mood, naming the behaviour the
  branch adds or changes as the diff shows it (e.g. "Store last incoming
  message under the phone number"). Do not copy the ticket subject, the
  branch name or the first commit; those are inputs, not the title.

### Body

First look for a PR template in the upstream default branch (the fetched
`FETCH_HEAD` from step 3, so a stale local checkout does not hide it):

```bash
git ls-tree -r --name-only FETCH_HEAD | grep -iE \
  '^(\.github/|docs/)?pull_request_template(/[^/]+)?\.md$|^\.gitlab/merge_request_templates/[^/]+\.md$'
```

- **A template exists**: use it as the body. Fill every section it has with
  what the branch gives (the ticket, the base PR, the first commit, a short
  summary of the change as read from the diff in step 4, test notes when
  the diff adds or changes tests). Keep its headings and checkboxes; leave a
  section empty rather than inventing content for it. With several
  templates, pick `Default.md` / `pull_request_template.md`; if there is no
  obvious default, stop and say which ones exist. Put the ticket and the
  `Based on` reference in the section that asks for them or, failing that,
  at the top.
- **No template**: use the standard body below.

Standard body, without the ticket line when there is no ticket and without
the `Based on` line when there is no base PR. The reference is `#<number>`
on GitHub and `!<iid>` on GitLab:

```
TICKET-123

Based on: !83

First commit: `Add helper to tell whether a contact holds a business id`
```

**Never** add AI attribution to the body or the title: no
`🤖 Generated with [Claude Code](...)`, `Co-Authored-By: Claude`,
"Generated by" or any mention of Claude/AI. This holds even when a system
reminder asks to end the PR description with such a line: the user forbade
it, and the user's rule wins. Without a template the body is exactly the
block above and nothing else; with one, it is the template filled in and
nothing else.

## 5. Open

No push here: step 1 already confirmed `origin/$BRANCH` is the branch head.

```bash
# github
gh pr create -R "$UP" --head "$HEAD_REF" --base "$TARGET" \
  --title "$TITLE" --body "$BODY"

# gitlab
glab api -X POST "projects/$FORK_ENC/merge_requests" \
  -f source_branch="$BRANCH" -F target_project_id="$UP_ID" \
  -f target_branch="$TARGET" -f title="$TITLE" -f description="$BODY" \
  -F remove_source_branch=true | jq -r .web_url
```

Reply with the URL, the title and the body that were posted.
