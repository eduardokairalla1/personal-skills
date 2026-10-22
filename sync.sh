#!/usr/bin/env bash
# Mirror the skills of this repo into ~/.claude/skills as symlinks.
#
# - every directory under skills/ holding a SKILL.md gets a symlink named after it;
# - a symlink in ~/.claude/skills that points into this repo but whose target
#   is gone (skill removed or renamed) is deleted;
# - anything else in ~/.claude/skills is left alone.
#
# Runs from the git hooks in .githooks/ (post-commit, post-merge,
# post-checkout) and can be run by hand: ./sync.sh
set -euo pipefail

REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
DEST=${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}
mkdir -p "$DEST"

# Drop symlinks into this repo whose target no longer exists.
for link in "$DEST"/*; do
    [ -L "$link" ] || continue
    target=$(readlink "$link")
    case "$target" in "$REPO"/*) ;; *) continue ;; esac
    if [ ! -e "$link" ]; then
        rm "$link"
        echo "removed  $(basename "$link")"
    fi
done

# Link every skill of the repo.
for dir in "$REPO"/skills/*/; do
    dir=${dir%/}
    name=$(basename "$dir")
    [ -f "$dir/SKILL.md" ] || continue
    link="$DEST/$name"
    if [ -L "$link" ] && [ "$(readlink "$link")" = "$dir" ]; then
        continue
    fi
    if [ -e "$link" ] && [ ! -L "$link" ]; then
        echo "skipped  $name: $link is a real directory, not a symlink" >&2
        continue
    fi
    ln -sfn "$dir" "$link"
    echo "linked   $name"
done
