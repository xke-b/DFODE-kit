# Worktree Workflow

Use separate git worktrees for parallel agent tasks.

## Current branches/worktrees
- integration branch: `agent-harness-refactor`
- `<worktree-root>/cli` -> `agent-cli-contract`
- `<worktree-root>/train` -> `agent-train-config`
- `<worktree-root>/data` -> `agent-data-io`
- `<worktree-root>/ci` -> `agent-ci-tests`

## Guidelines
- One worktree = one main concern.
- Avoid editing the same files from multiple active worktrees.
- Merge smaller mechanical changes first.
- Rebase/merge the integration branch into feature worktrees frequently.

## Useful commands
- List worktrees: `git worktree list`
- Add worktree: `git worktree add -b <branch> <path> agent-harness-refactor`
- Remove worktree: `git worktree remove <path>`
- Clean stale metadata: `git worktree prune`
