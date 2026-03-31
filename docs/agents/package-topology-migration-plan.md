# Package topology migration plan

## Status
Draft staged plan for moving toward the target package topology in `package-topology-spec.md`.

## Goal
Reach the target topology through small, behavior-preserving slices that are easy to review and verify.

## Non-goals
- no big-bang rename of the whole package
- no simultaneous redesign of APIs and directory layout
- no broad feature work mixed into topology-only branches

## Refactor strategy
Prefer slices that follow this pattern:
1. extract or split logic behind tests
2. add compatibility imports/shims if needed
3. switch call sites
4. remove old path only after verification

This minimizes breakage and keeps diffs understandable.

## Phase 0: invariants before moves
Before major moves, preserve or add tests around:
- CLI command listing and help paths
- HDF5 contract helpers
- init plan behavior
- runtime config behavior
- run-case planning behavior
- training config/registry behavior

If a move lacks a small invariant test, add one first.

## Phase 1: rename only the most stable package boundary
### Candidate
`cli_tools/` -> `cli/`

### Why first
- package boundary is already conceptually clean
- command behavior is already tested
- low domain ambiguity

### Slice contents
- create `dfode_kit/cli/`
- move `main.py`, `command_loader.py`, `commands/`
- keep import compatibility from old paths temporarily if needed
- update tests/docs/import sites

### Success check
- `dfode-kit --list-commands` unchanged
- per-command `--help` behavior unchanged
- lazy command loading preserved

## Phase 2: split `h5_kit.py` by concern before broader package renames
### Why now
`h5_kit.py` is one of the clearest mixed-responsibility hotspots.

### Target outcome
- keep schema checks in `data/contracts.py`
- move pure HDF5 I/O helpers to `data/io_hdf5.py`
- move model/integration helpers to more appropriate modules later

### Suggested slices
1. extract read/write/stack helpers
2. switch callers
3. only then rename package path if useful

### Success check
- `h52npy` and sampling-related HDF5 paths behave identically
- no model/training logic remains hidden in an I/O-named module unless clearly temporary

## Phase 3: `data_operations/` -> `data/`
### Why after Phase 2
It is easier once the most confusing mixed module is split first.

### Target mapping
- `contracts.py` -> `data/contracts.py`
- `augment_data.py` -> `data/augment.py`
- `label_data.py` -> `data/label.py`
- extracted HDF5 helpers -> `data/io_hdf5.py`

### Success check
- user-facing CLI behavior unchanged
- internal imports simpler and more domain-named

## Phase 4: `df_interface/` -> `cases/`
### Why this is a later slice
There is some ambiguity in how to divide:
- presets
- case planning
- DeepFlame-specific setup
- case sampling

### Recommended sequence
1. stabilize public responsibilities first
2. rename package second
3. split files only where the split improves clarity immediately

### Target mapping
- `case_init.py` -> `cases/init.py`
- `flame_configurations.py` -> `cases/presets.py`
- `sample_case.py` -> `cases/sampling.py`
- `oneDflame_setup.py` -> `cases/deepflame.py` or split further

### Success check
- `init` and `sample` commands still work the same way
- preset behavior remains explicit and documented

## Phase 5: `dfode_core/` -> `models/` + `training/`
### Why this is larger
This is really two reorganizations:
- model code
- trainer/config/train loop code

### Recommended sequence
1. move model registry and model implementations to `models/`
2. move trainer config/registry/train loop to `training/`
3. relocate or split `preprocess.py` only after its actual ownership is clear
4. remove in-package `dfode_core/test/`

### Success check
- train command behavior preserved
- model/trainer registries still work
- package navigation becomes clearer for experimentation work

## Phase 6: `runtime_config.py` -> `runtime/config.py`
### Why this is a clean later slice
This is small and conceptually stable, but not urgent.

### Possible follow-up
- move reusable run-case planning/application helpers from CLI helper modules into `runtime/run_case.py`

### Success check
- runtime config file path/schema unchanged
- `config` and `run-case` CLI behavior unchanged

## Compatibility rules during migration
- prefer re-export shims for old import paths during transition
- mark old paths as deprecated in docs/comments before removing them
- remove shims only after downstream call sites are updated and verified

## Branching guidance
Keep branches focused by package boundary, for example:
- `refactor/cli-package-rename`
- `refactor/h5-io-split`
- `refactor/data-package-rename`
- `refactor/cases-package-rename`
- `refactor/models-training-split`
- `refactor/runtime-package`

## Verification checklist per slice
- update or add targeted unit tests
- run `make verify`
- build docs if docs or import paths changed
- smoke-check relevant CLI commands
- check for accidental eager heavy imports on help/list paths

## Initial recommended order
1. `cli_tools/` -> `cli/`
2. split `h5_kit.py`
3. `data_operations/` -> `data/`
4. `df_interface/` -> `cases/`
5. `dfode_core/model` -> `models/`
6. `dfode_core/train` -> `training/`
7. `runtime_config.py` -> `runtime/config.py`
8. evaluate remaining `preprocess.py` / utility cleanup

## Definition of done for the overall direction
The topology migration is meaningfully complete when:
- major package names match stable responsibilities
- mixed-responsibility files have been split at the obvious boundaries
- old compatibility paths are removed or minimized
- docs and tests refer to the new package structure
- a new contributor can infer where to add code without reading large amounts of historical context
