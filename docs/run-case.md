# Runtime Configuration and Case Execution

DFODE-kit provides two CLI entrypoints for running DeepFlame/OpenFOAM cases reproducibly:

- `dfode-kit config`
- `dfode-kit run-case`

This document is the shared reference for both humans and AI agents.

Implementation note: runtime config helpers live under `dfode_kit.runtime.config`, and reusable run planning/execution helpers live under `dfode_kit.runtime.run_case`.

## Why a persistent runtime config exists

Running DeepFlame cases usually requires machine-local paths and environment activation steps that do not belong in case templates:

1. source OpenFOAM
2. source `conda.sh`
3. activate a Conda environment
4. source DeepFlame
5. run the case

Those machine-local settings are now stored through `dfode-kit config` instead of being retyped in every run command.

## Config file location

DFODE-kit stores runtime config in:

- `${XDG_CONFIG_HOME}/dfode-kit/config.json` when `XDG_CONFIG_HOME` is set
- otherwise `~/.config/dfode-kit/config.json`

Show the resolved config path:

```bash
dfode-kit config path
```

## Supported config keys

- `openfoam_bashrc`
- `conda_sh`
- `conda_env_name`
- `deepflame_bashrc`
- `python_executable`
- `default_np`
- `mpirun_command`

Show schema with descriptions and defaults:

```bash
dfode-kit config schema
```

## Basic config workflow

### Set values

```bash
dfode-kit config set openfoam_bashrc /path/to/openfoam/etc/bashrc
dfode-kit config set conda_sh /path/to/conda/etc/profile.d/conda.sh
dfode-kit config set conda_env_name deepflame
dfode-kit config set deepflame_bashrc /path/to/deepflame-dev/bashrc
```

Use paths appropriate for your local installation.

### Show current config

```bash
dfode-kit config show
```

### Show machine-readable config

```bash
dfode-kit config show --json
```

### Reset one key to its default

```bash
dfode-kit config unset python_executable
```

## Run a case

The `run-case` command currently executes a case-local runner script, defaulting to `Allrun`.

## Recommended environment split

In this environment, the workflow that was validated successfully is:

- use a DeepFlame-compatible Python environment for `dfode-kit init oneD-flame`
  - example: `conda activate deepflame`
- use persistent runtime config plus `dfode-kit run-case` for case execution
- use a Python environment with `cantera`, `numpy`, and `h5py` available for `dfode-kit sample`
  - in this environment, `conda activate deepflame` also works for sampling

### Preview without executing

```bash
dfode-kit run-case \
  --case /path/to/case \
  --preview --json
```

### Execute using stored config

```bash
dfode-kit run-case \
  --case /path/to/case \
  --apply
```

### Execute with one-off overrides

```bash
dfode-kit run-case \
  --case /path/to/case \
  --apply \
  --openfoam-bashrc /path/to/openfoam/etc/bashrc \
  --conda-sh /path/to/conda/etc/profile.d/conda.sh \
  --conda-env deepflame \
  --deepflame-bashrc /path/to/deepflame-dev/bashrc
```

## Current execution contract

`dfode-kit run-case` resolves a shell script equivalent to:

```bash
source <openfoam_bashrc>
source <conda_sh>
conda activate <conda_env_name>
source <deepflame_bashrc>
set -eo pipefail
which dfLowMachFoam
cd <case_dir>
chmod +x <runner>
./<runner>
```

## Required runtime config for `run-case`

The following keys must be available either from stored config or per-command overrides:

- `openfoam_bashrc`
- `conda_sh`
- `conda_env_name`
- `deepflame_bashrc`

## Output behavior

### `--preview --json`
Returns a JSON object containing:

- `case_type`
- `case_dir`
- `runner`
- `np`
- `dfode_kit.runtime.config`
- `shell_lines`
- `shell_script`

### `--apply`
Executes the resolved shell script.

In normal mode, stdout/stderr stream to the terminal.

In `--json` mode, stdout/stderr are written to:

- `log.dfode-run-case.stdout`
- `log.dfode-run-case.stderr`

and the JSON result reports those paths.

## Action rule

At least one of the following must be specified:

- `--preview`
- `--apply`

## Recommended workflow

1. Set runtime config once with `dfode-kit config set ...`
2. Create a case with `dfode-kit init oneD-flame ... --apply`
3. Preview the run plan with `dfode-kit run-case --preview --json`
4. Execute with `dfode-kit run-case --apply`
5. Sample the finished case with `dfode-kit sample`
6. Use per-command overrides only when machine-local config differs from the default workstation setup

## Example: CH4 / air / phi=1 workflow

### 1. Store runtime config

```bash
dfode-kit config set openfoam_bashrc /path/to/openfoam/etc/bashrc
dfode-kit config set conda_sh /path/to/conda/etc/profile.d/conda.sh
dfode-kit config set conda_env_name deepflame
dfode-kit config set deepflame_bashrc /path/to/deepflame-dev/bashrc
```

### 2. Initialize the case

```bash
source /path/to/openfoam/etc/bashrc
source /path/to/conda/etc/profile.d/conda.sh
conda activate deepflame
source /path/to/deepflame-dev/bashrc

python -m dfode_kit.cli.main init oneD-flame \
  --mech /path/to/mechanisms/CH4/gri30.yaml \
  --fuel CH4:1 \
  --oxidizer air \
  --phi 1.0 \
  --out /path/to/run/oneD_flame_CH4_phi1 \
  --apply --force
```

### 3. Run the case

```bash
dfode-kit run-case \
  --case /path/to/run/oneD_flame_CH4_phi1 \
  --apply --json
```

### 4. Sample the finished case

```bash
source /path/to/conda/etc/profile.d/conda.sh
conda activate deepflame
python -m dfode_kit.cli.main sample \
  --mech /path/to/mechanisms/CH4/gri30.yaml \
  --case /path/to/run/oneD_flame_CH4_phi1 \
  --save /path/to/run/oneD_flame_CH4_phi1/ch4_phi1_sample.h5 \
  --include_mesh
```
