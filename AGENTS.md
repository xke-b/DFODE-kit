# AGENTS.md

This repository contains DFODE-kit, a Python toolkit for sampling combustion states, augmenting and labeling datasets, and training neural-network surrogates for stiff chemistry integration.

## Goals
- Keep changes small, reviewable, and verifiable.
- Optimize for agent legibility and fast iteration.
- Improve experimentation throughput for model architectures, training algorithms, and data pipelines.

## Commands
- Bootstrap lightweight harness env: `make bootstrap-harness`
- Bootstrap docs env: `make bootstrap-docs`
- Activate env: `source .venv/bin/activate`
- Fast syntax check: `make check`
- Run tests: `make test`
- Build docs locally: `make docs-build`
- Full local verification: `make verify`

## Workflow
- Plan before editing for multi-file or ambiguous work.
- Read relevant files before changing them.
- Prefer focused PRs/branches with one main concern each.
- Run `make verify` before proposing a merge.
- If adding a new invariant, encode it in tests or CI.

## Structure
- `dfode_kit/cli_tools/`: CLI entrypoints and subcommands
- `dfode_kit/data_operations/`: dataset I/O, labeling, augmentation, integration utilities
- `dfode_kit/dfode_core/`: models, training, preprocessing
- `dfode_kit/df_interface/`: DeepFlame/OpenFOAM-facing helpers
- `docs/agents/`: deeper agent-facing docs and workflow conventions
- `tests/`: lightweight harness tests; keep them fast

## Rules
- Do not put large architecture essays in this file; add them under `docs/agents/` and link here.
- Prefer deterministic, non-interactive commands.
- Prefer explicit exceptions over bare asserts for runtime validation changes.
- Keep stdout clean for result output; use logs/errors sparingly.
- Do not mix unrelated refactors in the same branch.

## Read next
- `docs/agents/README.md`
- `docs/init.md`
- `docs/agents/verification.md`
- `docs/agents/worktrees.md`
- `docs/agents/roadmap.md`
