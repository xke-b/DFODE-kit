# Data Preparation and Training Workflow

This page documents the currently exposed CLI stages after a case has been initialized and run successfully.

It focuses on the data pipeline from:

1. finished DeepFlame/OpenFOAM case outputs
2. sampled HDF5 state data
3. optional HDF5-to-NumPy conversion
4. augmented state datasets
5. labeled supervised-learning datasets
6. trained surrogate model artifacts

## Stage boundaries

The current CLI presents the data workflow as a sequence of artifact transformations.

### 1. `sample`
Input:
- a finished case directory
- a mechanism file

Output:
- an HDF5 file containing sampled scalar fields
- optionally mesh datasets

Example:

```bash
dfode-kit sample \
  --mech /path/to/gri30.yaml \
  --case /path/to/run/oneD_flame_CH4_phi1 \
  --save /path/to/run/oneD_flame_CH4_phi1/ch4_phi1_sample.h5 \
  --include_mesh
```

Typical contents include:
- root metadata such as `mechanism`
- `scalar_fields/` datasets keyed by output time
- optional mesh datasets

### 2. `h52npy`
Input:
- sampled HDF5 file

Output:
- stacked NumPy array of scalar fields

Example:

```bash
dfode-kit h52npy \
  --source /path/to/run/oneD_flame_CH4_phi1/ch4_phi1_sample.h5 \
  --save_to /path/to/data/ch4_phi1_sample.npy
```

Use this when downstream workflows need a single NumPy array rather than time-indexed HDF5 datasets.

### 3. `augment`
Input:
- sampled HDF5 file
- mechanism file

Output:
- augmented NumPy dataset

Example:

```bash
dfode-kit augment \
  --source /path/to/run/oneD_flame_CH4_phi1/ch4_phi1_sample.h5 \
  --mech /path/to/gri30.yaml \
  --save /path/to/data/ch4_phi1_aug.npy \
  --preset random-local-combustion-v1 \
  --target-size 20000 \
  --apply
```

Minimal public contract:
- `--source`
- `--mech`
- `--save` (required for `--apply`)
- `--preset`
- `--target-size`
- `--seed` (optional)
- `--preview`
- `--apply`
- `--json`
- `--write-config`
- `--from-config`

## Current note on `augment`

The augmentation CLI is intentionally preset-driven and keeps the public flag surface small. For more advanced tuning, use `--preview --write-config` and apply later with `--from-config`.

### 4. `label`
Input:
- mechanism file
- NumPy state dataset
- reactor advancement time step

Output:
- labeled NumPy dataset suitable for supervised learning

Example:

```bash
dfode-kit label \
  --mech /path/to/gri30.yaml \
  --time 1e-6 \
  --source /path/to/data/ch4_phi1_aug.npy \
  --save /path/to/data/ch4_phi1_labeled.npy
```

Conceptually, this stage advances each sampled state with Cantera/CVODE and writes paired source/target state data.

### 5. `train`
Input:
- mechanism file
- labeled NumPy dataset

Output:
- trained model artifact written to the requested output path

Example:

```bash
dfode-kit train \
  --mech /path/to/gri30.yaml \
  --source_file /path/to/data/ch4_phi1_labeled.npy \
  --output_path /path/to/models/ch4_phi1_model.pt
```

## Recommended artifact layout

A practical directory layout is:

```text
<project-root>/
  runs/
    oneD_flame_CH4_phi1/
      ch4_phi1_sample.h5
  data/
    ch4_phi1_sample.npy
    ch4_phi1_aug.npy
    ch4_phi1_labeled.npy
  models/
    ch4_phi1_model.pt
```

This keeps:
- case-run artifacts near the case directory
- derived training datasets under a separate `data/` area
- trained models under a separate `models/` area

## Current limitations and documentation gaps

The CLI surface for the data pipeline is usable, but not yet as normalized as `init` and `run-case`.

Current gaps include:
- limited machine-readable JSON output for `sample`, `label`, and `train`
- older option naming conventions still present on some commands such as `--source_file`
- thinner published documentation for training outputs and configuration detail than for case init/run

These are good future cleanup targets, but the commands above describe the current behavior on `main`.

## Validated minimal sequence

For a validated 1D flame workflow, the current practical sequence is:

```bash
dfode-kit init oneD-flame ... --apply
dfode-kit run-case --case /path/to/case --apply --json
dfode-kit sample --mech /path/to/gri30.yaml --case /path/to/case --save /path/to/sample.h5 --include_mesh
```

After sampling, continue with either:

```bash
dfode-kit h52npy --source /path/to/sample.h5 --save_to /path/to/sample.npy
```

or directly with augmentation/labeling:

```bash
dfode-kit augment ...
dfode-kit label ...
dfode-kit train ...
```
