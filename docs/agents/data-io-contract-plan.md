# Data I/O contract plan

## Scope
Keep this branch focused on dataset layout and HDF5/NPY boundaries in `dfode_kit/data_operations`.

## Audit summary
- `dfode_kit/data_operations/h5_kit.py` currently mixes three concerns: HDF5 inspection/loading, reactor/model integration, and error reporting.
- HDF5 layout assumptions are implicit: code assumes a root `mechanism` attribute and a `scalar_fields` group of stack-compatible datasets.
- `dfode_kit/cli_tools/commands/h52npy.py` reimplements part of the HDF5 read path instead of sharing one validated loader.
- Some runtime contracts still rely on loose assumptions or non-deterministic dataset iteration.

## First slice
1. Extract lightweight HDF5 contract helpers into a focused module.
2. Define and enforce the `scalar_fields` layout contract:
   - required group name
   - deterministic dataset ordering
   - each dataset must be a 2D array
   - all datasets must share the same column count
   - required root attrs can be checked explicitly where needed
3. Reuse those helpers from `h5_kit.py` and the `h52npy` CLI command.
4. Add fast tests for the contract helpers.

## Follow-up slices
- Split pure HDF5 I/O from Cantera/Torch integration paths in `h5_kit.py`.
- Add NPY state-matrix contract helpers shared by labeling/augmentation commands.
- Add lightweight CLI smoke tests for `h52npy` and `label` contract failures.
