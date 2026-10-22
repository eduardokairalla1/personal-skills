# Just my skills :)

My [Claude Code](https://claude.com/claude-code) skills, the ones I use every
day.

## Environment

- **Agent:** Claude Code
- **Hosts:** GitHub (`gh`) and GitLab (`glab`)

## Structure

```
.
├── skills/
│   ├── atomic-commit/          # Plan and execute atomic commits
│   ├── e2e-review/             # End-to-end review of a feature or fix
│   ├── humanizer/              # Remove AI writing patterns from text
│   ├── open-pr/                # Open a PR/MR for a branch
│   ├── retrofit-commit/        # Fold refactors back into the original commits
│   └── review/                 # Three-axis code review
├── .githooks/                  # Hooks that keep ~/.claude/skills in sync
└── sync.sh                     # Mirrors the skills as symlinks
```

## Skills

**atomic-commit**
- One change per commit, every commit leaves the code working
- Messages in English, imperative, 50 characters, no prefix, no period
- Dependencies, settings and version bumps get their own commits

**review**
- Three axes in parallel sub-agents: Standards, Spec and Build
- Standards come from the repo's own docs plus my baseline
  (`skills/review/references/standards.md`) and a smell list
- Every finding is verified before it is applied or reported
- Severities: block, round, nit

**open-pr**
- Detects GitHub or GitLab from the remote
- Reads the diff of the branch to write the title
- Uses the repo's PR template when there is one
- Never pushes: asks you to push first

**e2e-review**
- Validates a change in the real environment, by request and in the browser
- Phase by phase: understand, plan, set up, execute, triage, report, wrap up
- Ends in a facts-only Markdown report

**retrofit-commit**
- Rewrites a feature branch so later fixes land in the commit that introduced
  the code

**humanizer**
- [blader/humanizer](https://github.com/blader/humanizer), kept at the
  latest upstream version

## Installation

Requirements: Git, Bash and Claude Code. `open-pr` also needs
[`gh`](https://cli.github.com/) or [`glab`](https://gitlab.com/gitlab-org/cli)
and [`jq`](https://jqlang.github.io/jq/).

```bash
# 1. clone it anywhere you like
git clone https://github.com/eduardokairalla1/personal-skills.git
cd personal-skills

# 2. link every skill into ~/.claude/skills
./sync.sh

# 3. let git keep the links up to date after commits, merges and checkouts
git config core.hooksPath .githooks
```

`sync.sh` creates one symlink per skill, removes links whose skill is gone
and leaves everything else in `~/.claude/skills` alone. Edits in the clone
are live through the symlinks; new or removed skills show up on the next
commit, pull or `./sync.sh`.

To install a single skill without the repo, copy its folder from `skills/`
into `~/.claude/skills/`.

## Credits

- `humanizer` is [blader/humanizer](https://github.com/blader/humanizer),
  MIT, redistributed unchanged.

## Notes

These skills are tailored to my personal workflow but feel free to fork,
adapt, and experiment.
