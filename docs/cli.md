# CLI

The current top-level command is:

```bash
dfode-kit --help
```

Available commands:

- `config`
- `init`
- `run-case`
- `sample`
- `augment`
- `label`
- `train`
- `h52npy`

List commands deterministically:

```bash
dfode-kit --list-commands
```

## Command overview

### `config`
Store and inspect machine-local runtime configuration such as OpenFOAM, Conda, and DeepFlame activation paths.

Example:

```bash
dfode-kit config set openfoam_bashrc /path/to/openfoam/etc/bashrc
```

### `init`
Initialize canonical cases from explicit presets. The current supported case is `oneD-flame`, which preserves the current DFODE-kit empirical setup logic while making it previewable, overrideable, and serializable to JSON.

Example:

```bash
dfode-kit init oneD-flame \
  --mech /path/to/gri30.yaml \
  --fuel CH4:1 \
  --oxidizer air \
  --phi 1.0 \
  --out /tmp/ch4_phi1_case \
  --preview --json
```

### `run-case`
Run a case-local runner such as `Allrun` using the stored runtime configuration from `dfode-kit config`.

Example:

```bash
dfode-kit run-case --case /path/to/case --preview --json
```

### `sample`
Sample thermochemical states from canonical flame simulation outputs and save them to HDF5.

Example:

```bash
dfode-kit sample \
  --mech /path/to/gri30.yaml \
  --case /path/to/case \
  --save /path/to/output.h5 \
  --include_mesh
```

### `augment`
Apply perturbation-based dataset augmentation to sampled states.

Example:

```bash
dfode-kit augment \
  --source /path/to/sample.h5 \
  --mech /path/to/gri30.yaml \
  --save /path/to/augmented.npy \
  --preset random-local-combustion-v1 \
  --target-size 20000 \
  --apply
```

### `label`
Generate supervised learning targets using Cantera/CVODE time advancement.

Example:

```bash
dfode-kit label \
  --mech /path/to/gri30.yaml \
  --time 1e-6 \
  --source /path/to/augmented.npy \
  --save /path/to/labeled.npy
```

### `train`
Train a neural-network surrogate for chemistry integration.

Example:

```bash
dfode-kit train \
  --mech /path/to/gri30.yaml \
  --source_file /path/to/labeled.npy \
  --output_path /path/to/model.pt
```

### `h52npy`
Convert HDF5 scalar-field datasets into a stacked NumPy array.

Example:

```bash
dfode-kit h52npy \
  --source /path/to/sample.h5 \
  --save_to /path/to/sample.npy
```

## Current design notes

Recent CLI refactors improved:

- deterministic command ordering,
- stable top-level command listing,
- lazy command loading for lighter help paths,
- more predictable command dispatch behavior.

The new `init` command already supports machine-readable JSON output for planning/provenance, and `run-case` supports JSON output for preview/apply results.

For augmentation specifically, see [Data Augmentation](augment.md).
For the end-to-end artifact flow between `sample`, `augment`, `label`, `h52npy`, and `train`, see [Data Preparation and Training Workflow](data-workflow.md).

Future work should still add:

- broader machine-readable JSON output across all commands,
- standardized stderr/stdout behavior,
- command-level error normalization.
