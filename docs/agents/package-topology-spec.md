# Package topology target spec

## Status
Draft target architecture. This is a direction-setting spec, not a big-bang rewrite plan.

## Goal
Evolve `dfode_kit/` toward clearer subsystem boundaries that match the user-visible workflow and reduce mixed-responsibility modules.

Target shape:

```text
dfode_kit/
  cli/
    main.py
    command_loader.py
    commands/
  cases/
    init.py
    presets.py
    sampling.py
    deepflame.py
  data/
    contracts.py
    io_hdf5.py
    augment.py
    label.py
  models/
    mlp.py
    registry.py
  training/
    config.py
    registry.py
    supervised_physics.py
    train.py
  runtime/
    config.py
    run_case.py
  utils/
```

## Why this direction
The current package layout has the right broad pieces, but some names are historical and some modules mix concerns:

- `cli_tools/` is clear, but the `*_tools` naming is heavier than needed.
- `data_operations/` currently mixes contracts, HDF5 I/O, augmentation, labeling, and some model/integration helpers.
- `df_interface/` includes case initialization, case setup, and sampling concerns under a vague name.
- `dfode_core/` mixes models, training, preprocessing, and an in-package test directory.
- some modules carry more than one abstraction level, especially `h5_kit.py`.

The target layout moves toward domain-first naming and narrower module responsibility.

## Design principles

### 1. Name packages after stable responsibilities
Prefer names that tell a new contributor where code belongs:

- `cli`: command-line entrypoints and dispatch only
- `cases`: canonical case setup, case-local sampling, DeepFlame-facing case operations
- `data`: data contracts, storage I/O, augmentation, labeling
- `models`: neural-network architectures and model registry
- `training`: trainer config, trainer registry, training loops
- `runtime`: machine-local configuration and case execution helpers
- `utils`: small generic helpers only

### 2. Keep orchestration separate from primitives
Examples:
- `cases.init` should assemble a case plan and apply it
- `data.io_hdf5` should do HDF5 read/write/validation work
- `training.train` should orchestrate a training run
- `models.mlp` should define one architecture, not run the whole workflow

### 3. Avoid mixed abstraction levels in one module
A file named like an I/O helper should not also be the home for model inference or numerical integration orchestration.

### 4. Keep CLI modules thin
CLI command modules should:
- define arguments
- validate command-level options
- call importable library functions
- handle output formatting and exit behavior

They should not be the only place where business logic exists.

### 5. Preserve agent-friendly behavior
Refactors in this direction must preserve:
- lazy imports for heavy dependencies where possible
- deterministic CLI command ordering
- clean stdout/stderr behavior
- small, verifiable change slices

## Target package responsibilities

## `dfode_kit/cli/`
Owns command parsing, command registration, and command dispatch.

### Intended contents
- `main.py`: top-level argument parsing and exit-code contract
- `command_loader.py`: deterministic command specification/loading
- `commands/`: one module per user-facing subcommand

### Non-goals
- no domain logic that cannot be reused outside the CLI
- no heavy imports at top level when avoidable

## `dfode_kit/cases/`
Owns canonical case planning and DeepFlame/OpenFOAM-facing case operations.

### Intended contents
- `init.py`: case plan assembly and application helpers
- `presets.py`: named case-setup presets and preset metadata
- `sampling.py`: sample extraction from completed cases
- `deepflame.py`: DeepFlame/OpenFOAM case-specific helpers

### Notes
This package replaces the vaguer `df_interface/` name with a user-visible workflow concept: cases.

## `dfode_kit/data/`
Owns dataset contracts, file I/O, and state transformation steps.

### Intended contents
- `contracts.py`: HDF5/NPY schema checks and dataset ordering rules
- `io_hdf5.py`: HDF5 reading/writing and stack/reshape helpers
- `augment.py`: augmentation primitives and workflow helpers
- `label.py`: labeling primitives and workflow helpers

### Notes
This package should not become a second training or inference package. If a function is primarily model inference or time integration orchestration, it likely belongs elsewhere.

## `dfode_kit/models/`
Owns model architectures and model registration.

### Intended contents
- `mlp.py`: current MLP implementation
- `registry.py`: model factory registration and lookup

### Notes
Keep model creation separate from training-loop concerns.

## `dfode_kit/training/`
Owns trainer configuration, trainer registration, and training execution.

### Intended contents
- `config.py`: typed training configuration
- `registry.py`: trainer registry
- `supervised_physics.py`: current trainer implementation
- `train.py`: orchestration entrypoint for training runs

### Notes
Preprocessing that is training-specific may move here later if it is not reusable elsewhere.

## `dfode_kit/runtime/`
Owns machine-local runtime config and execution planning.

### Intended contents
- `config.py`: runtime config persistence and schema
- `run_case.py`: case execution planning/application helpers

### Notes
This separates workstation/runtime concerns from case-definition concerns.

## `dfode_kit/utils/`
Owns small generic helpers.

### Rule
If a helper is domain-specific enough to obviously belong to `cases`, `data`, `models`, `training`, or `runtime`, do not place it in `utils`.

## Migration mapping from current layout

### Current -> target
- `cli_tools/` -> `cli/`
- `df_interface/` -> `cases/`
- `data_operations/` -> `data/`
- `dfode_core/model/` -> `models/`
- `dfode_core/train/` -> `training/`
- `runtime_config.py` -> `runtime/config.py`

### Likely file moves
- `cli_tools/main.py` -> `cli/main.py`
- `cli_tools/command_loader.py` -> `cli/command_loader.py`
- `cli_tools/commands/*.py` -> `cli/commands/*.py`
- `df_interface/case_init.py` -> `cases/init.py`
- `df_interface/flame_configurations.py` -> `cases/presets.py`
- `df_interface/sample_case.py` -> `cases/sampling.py`
- `df_interface/oneDflame_setup.py` -> `cases/deepflame.py` or split across `init.py` + `deepflame.py`
- `data_operations/contracts.py` -> `data/contracts.py`
- `data_operations/h5_kit.py` -> split; pure HDF5 pieces to `data/io_hdf5.py`
- `data_operations/augment_data.py` -> `data/augment.py`
- `data_operations/label_data.py` -> `data/label.py`
- `dfode_core/model/mlp.py` -> `models/mlp.py`
- `dfode_core/model/registry.py` -> `models/registry.py`
- `dfode_core/train/config.py` -> `training/config.py`
- `dfode_core/train/registry.py` -> `training/registry.py`
- `dfode_core/train/supervised_physics.py` -> `training/supervised_physics.py`
- `dfode_core/train/train.py` -> `training/train.py`
- `runtime_config.py` -> `runtime/config.py`
- `cli_tools/commands/run_case_helpers.py` -> `runtime/run_case.py` or split between CLI and runtime library

## Compatibility expectations
This refactor direction should preserve current user-facing behavior during migration:

- keep the `dfode-kit` CLI command name unchanged
- keep subcommand names stable unless there is a strong reason to rename them
- preserve current import paths temporarily via compatibility shims where needed
- prefer deprecation windows over abrupt breakage

## What should not happen
- do not rewrite all packages in one PR
- do not move files without adding or updating tests for the moved contract
- do not change user-facing CLI behavior incidentally while only intending package moves
- do not put more domain-specific logic into `utils.py`
- do not mix rename-only moves with unrelated feature work

## Success criteria
A refactor slice is aligned with this spec if it:
- makes package names more domain-specific
- reduces mixed-responsibility modules
- keeps behavior stable or makes changes explicitly documented
- preserves agent-friendly CLI/test behavior
- leaves the repository easier to navigate for a new contributor

## Deferred questions
These can be answered incrementally rather than upfront:
- should `preprocess.py` become `training/preprocess.py`, `data/preprocess.py`, or be split?
- should case sampling stay under `cases/` or move partly into `data/` after extraction?
- should `runtime/` eventually hold more execution-plan/provenance helpers?
- should a future `workflows/` package exist for higher-level chained operations?
