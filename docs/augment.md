# Data Augmentation

DFODE-kit provides a preset-driven CLI for data augmentation:

```bash
dfode-kit augment ...
```

This page is the canonical reference for the current augmentation command.

## Purpose

Create an augmented NumPy dataset from a sampled HDF5 state file using a named augmentation preset.

The current design goal is to keep the public CLI surface small while still supporting:

- preview before execution
- machine-readable JSON output
- config round-trip through JSON files
- reproducible execution through an explicit seed

## Command

```bash
dfode-kit augment [options]
```

## Minimal public contract

### Required

- `--source`
- `--mech`

### Usually required

- `--save` (required for `--apply`)
- `--preset`
- `--target-size`

### Workflow controls

- `--preview`
- `--apply`
- `--json`
- `--write-config`
- `--from-config`

### Optional but high-value

- `--seed`
- `--time` (repeatable snapshot index/slice selector)

## Current preset

- `random-local-combustion-v1`

This preset currently preserves the mainline augmentation behavior while keeping the public flag surface minimal.

## Common workflow

### Preview the resolved plan

```bash
dfode-kit augment \
  --source /path/to/sample.h5 \
  --mech /path/to/gri30.yaml \
  --preset random-local-combustion-v1 \
  --target-size 20000 \
  --time 0:12 \
  --preview --json
```

### Write a machine-readable config

```bash
dfode-kit augment \
  --source /path/to/sample.h5 \
  --mech /path/to/gri30.yaml \
  --preset random-local-combustion-v1 \
  --target-size 20000 \
  --preview \
  --write-config /path/to/augment-plan.json
```

### Apply directly

```bash
dfode-kit augment \
  --source /path/to/sample.h5 \
  --mech /path/to/gri30.yaml \
  --save /path/to/aug.npy \
  --preset random-local-combustion-v1 \
  --target-size 20000 \
  --time ::10 \
  --seed 1234 \
  --apply
```

### Apply from a saved config

```bash
dfode-kit augment \
  --from-config /path/to/augment-plan.json \
  --save /path/to/aug.npy \
  --apply
```

## Time snapshot selection

When `--time` is omitted, augmentation uses all snapshots in the sampled HDF5 source.

When `--time` is provided, it selects snapshots from the ordered HDF5 snapshot list by index expression.

Supported forms include:

- single index: `--time 0`
- negative index: `--time -1`
- slice: `--time 0:12`
- stride: `--time ::10`
- repeated selectors: `--time 0:5 --time -1`

Selection is applied to snapshots only; all rows from each selected snapshot are included.

## Output behavior

### `--preview --json`
Prints a JSON object containing the resolved augmentation plan.

### `--write-config`
Writes the resolved plan to a JSON file for review, editing, and later execution.

### `--apply`
Runs augmentation and writes the output `.npy` dataset.

In `--json` mode, the command reports a structured completion record including:

- source path
- output path
- preset
- requested row count
- returned row count
- seed
- resolved snapshot count
- resolved snapshot names

## Action rule

At least one of the following must be specified:

- `--preview`
- `--apply`
- `--write-config`

## Design note

The current augmentation CLI intentionally avoids exposing a large number of tuning flags.

The preferred model is:

1. choose a named preset
2. preview the resolved plan
3. optionally persist the plan with `--write-config`
4. apply the plan directly or via `--from-config`

This keeps everyday CLI usage short while still supporting reproducible, machine-readable workflows.
