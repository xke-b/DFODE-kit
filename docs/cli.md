# CLI

The current top-level command is:

```bash
dfode-kit --help
```

Available commands:

- `init`
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

### `sample`
Sample thermochemical states from canonical flame simulation outputs and save them to HDF5.

### `augment`
Apply perturbation-based dataset augmentation to sampled states.

### `label`
Generate supervised learning targets using Cantera/CVODE time advancement.

### `train`
Train a neural-network surrogate for chemistry integration.

### `h52npy`
Convert HDF5 scalar-field datasets into a stacked NumPy array.

## Current design notes

Recent CLI refactors improved:

- deterministic command ordering,
- stable top-level command listing,
- lazy command loading for lighter help paths,
- more predictable command dispatch behavior.

The new `init` command already supports machine-readable JSON output for planning/provenance.

Future work should still add:

- broader machine-readable JSON output across all commands,
- standardized stderr/stdout behavior,
- command-level error normalization.
