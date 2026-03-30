# Agent-First Roadmap

## Phase 1: Harness
- Add `AGENTS.md`
- Add docs topology under `docs/agents/`
- Add `make check`, `make test`, `make verify`
- Add lightweight pytest + CI

## Phase 2: Contracts
- Define dataset layout contracts for HDF5/NPY
- Define training config schema
- Define CLI output/exit-code expectations

## Phase 3: Refactor for throughput
- Split mixed-responsibility modules (`h5_kit.py` first)
- Introduce model/training registries or config-driven training
- Add architecture-specific worktrees and smoke tests

## Phase 4: Experiment velocity
- Support multiple model architectures without editing core train loop
- Add repeatable benchmark scripts
- Add synthetic small-data smoke training paths for agent verification
