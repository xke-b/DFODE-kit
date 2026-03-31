# Init CLI Spec

This document defines the current DFODE-kit canonical-case init contract for coding agents and maintainers.

## Command

```bash
dfode-kit init oneD-flame [options]
```

## Purpose

Create or preview a parameterized copy of the canonical one-dimensional freely propagating premixed flame case.

## Supported preset

- `premixed-defaults-v1`

This preset preserves the current empirical defaults implemented in:

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

## Overrideable resolved fields

- `--domain-length`
- `--domain-width`
- `--ignition-region`
- `--sim-time-step`
- `--sim-time`
- `--sim-write-interval`
- `--num-output-steps`
- `--inlet-speed`

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

## Intended agent workflow

1. Run `--preview --json`
2. Inspect resolved values
3. Optionally persist with `--write-config`
4. Apply with `--apply`
5. Record the generated `dfode-init-plan.json` as provenance
