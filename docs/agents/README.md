# Shared Operational Docs

This directory contains deeper operational docs used by both humans and coding agents.

Use this docs tree for information that is too detailed or too volatile for `AGENTS.md`.

## Documents
- `init-cli-spec.md`: pointer to the shared canonical init CLI reference in `docs/init.md`
- `verification.md`: required local/CI verification loop
- `worktrees.md`: parallel branch + worktree workflow
- `roadmap.md`: near-term harness and refactor priorities
- `topology.md`: documentation and repo topology guidance
- `ci-tests-plan.md`: narrow next-step plan for harness parity and docs invariants
- `cli-usability-plan.md`: CLI agent-usability improvement plan
- `data-io-contract-plan.md`: data I/O contract and refactor plan
- `train-config-plan.md`: training/config refactor plan for experiment throughput

## Philosophy
- `AGENTS.md` is the entrypoint for repository workflow.
- Documentation should be shared across humans and agents whenever possible.
- New durable rules should prefer tests, CI, or scripts over prose alone.
