# Canonical Case Initialization

DFODE-kit provides an explicit CLI for canonical case setup:

```bash
dfode-kit init oneD-flame ...
```

This document is the **single canonical reference** for the init command, for both humans and AI agents.

The design goal is **not** to claim that one set of setup heuristics is universally optimal. Instead, the CLI makes the current DFODE-kit logic:

- explicit,
- preset-based,
- previewable,
- overrideable,
- serializable to JSON for review and provenance.

## Command

```bash
dfode-kit init oneD-flame [options]
```

## Purpose

Create or preview a parameterized copy of the canonical one-dimensional freely propagating premixed flame case.

## Current supported case type

- `oneD-flame`: one-dimensional freely propagating premixed flame

## Current preset

- `premixed-defaults-v1`

This preset preserves the current hardcoded empirical logic from:

- `dfode_kit/df_interface/flame_configurations.py`
- method: `OneDFreelyPropagatingFlameConfig.update_config()`

## Stable intent

The command is a **preset instantiator**, not a claim of universal best practice.

## Inputs

### Required unless `--from-config` is used

- `--mech`
- `--fuel`
- `--oxidizer`
- `--phi`

### Optional scalar inputs

- `--T0` default `300.0`
- `--p0` default `101325.0`
- `--preset` default `premixed-defaults-v1`
- `--template` default `DFODE_ROOT/canonical_cases/oneD_freely_propagating_flame`
- `--inert-specie` default `N2`

### Output/config controls

- `--out`
- `--preview`
- `--apply`
- `--json`
- `--write-config`
- `--from-config`
- `--force`

## Oxidizer alias

`--oxidizer air` resolves to:

```text
O2:1, N2:3.76
```

## Environment note

The `oneD-flame` init command computes flame properties through Cantera. In practice, run it from a Python environment that has Cantera available.

In this environment, the validated choice was:

```bash
source /opt/openfoam7/etc/bashrc
source /home/xk/miniconda3/etc/profile.d/conda.sh
conda activate deepflame
source /home/xk/deepflame/df_1be82b6/deepflame-dev/bashrc
```

## Core workflow

### Preview a plan

```bash
dfode-kit init oneD-flame \
  --mech /path/to/gri30.yaml \
  --fuel CH4:1 \
  --oxidizer air \
  --phi 1.0 \
  --out /tmp/ch4_phi1_case \
  --preview --json
```

### Write a machine-readable config

```bash
dfode-kit init oneD-flame \
  --mech /path/to/gri30.yaml \
  --fuel CH4:1 \
  --oxidizer air \
  --phi 1.0 \
  --out /tmp/ch4_phi1_case \
  --preview \
  --write-config /tmp/ch4_phi1_case.plan.json
```

### Apply a plan directly

```bash
dfode-kit init oneD-flame \
  --mech /path/to/gri30.yaml \
  --fuel CH4:1 \
  --oxidizer air \
  --phi 1.0 \
  --out /tmp/ch4_phi1_case \
  --apply
```

If the output directory already exists, add:

```bash
--force
```

### Apply from a saved config

```bash
dfode-kit init oneD-flame \
  --from-config /tmp/ch4_phi1_case.plan.json \
  --out /tmp/ch4_phi1_case \
  --apply
```

## Why presets instead of "best practices"

Canonical case setup often depends on empirical defaults such as:

- domain length,
- ignition region,
- output interval,
- end time.

Those choices are useful starter policies, but they should not be presented as universally correct. DFODE-kit therefore treats them as:

- **named presets**,
- with explicit assumptions,
- plus user overrides for resolved fields.

## Overrideable resolved fields

The current CLI allows overriding:

- `--domain-length`
- `--domain-width`
- `--ignition-region`
- `--sim-time-step`
- `--sim-time`
- `--sim-write-interval`
- `--num-output-steps`
- `--inlet-speed`
- `--inert-specie`

## Preset assumptions in `premixed-defaults-v1`

- `domain_length = flame_thickness / 10 * 500`
- `domain_width = domain_length / 10`
- `ignition_region = domain_length / 2`
- `sim_time_step = 1e-6`
- `num_output_steps = 100`
- `sim_write_interval = (flame_thickness / flame_speed) * 10 / num_output_steps`
- `sim_time = sim_write_interval * (num_output_steps + 1)`
- `inlet_speed = flame_speed`
- `inert_specie = "N2"`

## Output contract

### `--preview --json`
Print a JSON object containing:

- `schema_version`
- `case_type`
- `preset`
- `preset_summary`
- `template`
- `output_dir`
- `config_path`
- `inputs`
- `assumptions`
- `notes`
- `resolved`

### `--write-config`
Writes the same init plan JSON to disk.

### `--apply`
Creates the case directory and writes:

- parameterized OpenFOAM case files
- `dfode-init-plan.json`

## Action rule

At least one of the following must be specified:

- `--preview`
- `--apply`
- `--write-config`

## Provenance and review

Use `--json` and/or `--write-config` to make the init step reproducible and reviewable.

The written JSON records:

- case type,
- preset name,
- template path,
- inputs,
- assumptions,
- resolved values,
- output directory.

## Recommended workflow

1. Run `--preview --json`
2. Inspect resolved values
3. Optionally persist with `--write-config`
4. Apply with `--apply`
5. Record the generated `dfode-init-plan.json` as provenance
