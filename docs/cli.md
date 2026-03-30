# CLI

The current top-level command is:

```bash
dfode-kit --help
```

Available commands:

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

Future work should add:

- machine-readable JSON output,
- standardized stderr/stdout behavior,
- command-level error normalization.
