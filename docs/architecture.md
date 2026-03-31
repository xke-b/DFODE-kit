# Architecture

## Current repository structure

- `dfode_kit/cli/`: CLI entrypoints and subcommands
- `dfode_kit/cases/`: explicit case init, presets, sampling, and DeepFlame-facing helpers
- `dfode_kit/data/`: contracts, HDF5 I/O, and integration utilities
- `dfode_kit/data_operations/`: augmentation and labeling workflows
- `dfode_kit/models/`: model architectures and registries
- `dfode_kit/training/`: training configuration, training loops, registries, and preprocessing
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
