# Architecture

## Current repository structure

- `dfode_kit/cli_tools/`: CLI entrypoints and subcommands
- `dfode_kit/data_operations/`: dataset I/O, contracts, labeling, augmentation, integration utilities
- `dfode_kit/dfode_core/`: models, training, registries, preprocessing
- `dfode_kit/cases/`: explicit case init, preset, sampling, and DeepFlame-facing helpers
- `dfode_kit/df_interface/`: compatibility layer for the legacy case-facing import paths
- `docs/agents/`: agent-facing operational and planning docs
- `tests/`: lightweight repository and harness tests

## Current refactor themes

### 1. Harness engineering
The repository now includes:

- `AGENTS.md`
- local verification commands
- lightweight CI
- documentation topology for agents and maintainers

### 2. Data contracts
A new contracts layer is being used to make HDF5 dataset assumptions explicit and testable.

### 3. Config-driven training
The training stack is moving toward explicit config objects and registries so new model architectures and trainer types can be added without editing a monolithic training loop.

### 4. Agent-friendly CLI
The CLI now uses lighter command discovery and deferred heavy imports for improved usability in minimal environments.
