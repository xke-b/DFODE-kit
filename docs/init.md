# Canonical Case Initialization

DFODE-kit now provides an explicit CLI for canonical case setup:

```bash
dfode-kit init oneD-flame ...
```

The design goal is **not** to claim that one set of setup heuristics is universally optimal. Instead, the CLI makes the current DFODE-kit logic:

- explicit,
- preset-based,
- previewable,
- overrideable,
- serializable to JSON for agent and human review.

## Current supported case type

- `oneD-flame`: one-dimensional freely propagating premixed flame

## Current preset

- `premixed-defaults-v1`

This preset preserves the current hardcoded empirical logic from `OneDFreelyPropagatingFlameConfig.update_config()`.

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

## Agent-readable output

Use `--json` and/or `--write-config` to make the init step reproducible and reviewable by coding agents.

The written JSON records:

- case type,
- preset name,
- template path,
- inputs,
- assumptions,
- resolved values,
- output directory.
