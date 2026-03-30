# Worktree Workflow

Use separate git worktrees for parallel agent tasks.

## Current branches/worktrees
- integration branch: `agent-harness-refactor`
- `/mnt/d/u_deepflame_agent/Projects/dfode-wt/cli` -> `agent-cli-contract`
- `/mnt/d/u_deepflame_agent/Projects/dfode-wt/train` -> `agent-train-config`
- `/mnt/d/u_deepflame_agent/Projects/dfode-wt/data` -> `agent-data-io`
- `/mnt/d/u_deepflame_agent/Projects/dfode-wt/ci` -> `agent-ci-tests`

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
