# Runtime Configuration and Case Execution

DFODE-kit provides two CLI entrypoints for running DeepFlame/OpenFOAM cases reproducibly:

- `dfode-kit config`
- `dfode-kit run-case`

This document is the shared reference for both humans and AI agents.

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
dfode-kit config set openfoam_bashrc /opt/openfoam7/etc/bashrc
dfode-kit config set conda_sh /home/xk/miniconda3/etc/profile.d/conda.sh
dfode-kit config set conda_env_name deepflame
dfode-kit config set deepflame_bashrc /home/xk/deepflame/df_1be82b6/deepflame-dev/bashrc
```

These are the exact values validated in this environment.

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
  --openfoam-bashrc /opt/openfoam7/etc/bashrc \
  --conda-sh /home/xk/miniconda3/etc/profile.d/conda.sh \
  --conda-env deepflame \
  --deepflame-bashrc /home/xk/deepflame/df_1be82b6/deepflame-dev/bashrc
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
- `runtime_config`
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

## Validated example: CH4 / air / phi=1 in this environment

### 1. Store runtime config

```bash
dfode-kit config set openfoam_bashrc /opt/openfoam7/etc/bashrc
dfode-kit config set conda_sh /home/xk/miniconda3/etc/profile.d/conda.sh
dfode-kit config set conda_env_name deepflame
dfode-kit config set deepflame_bashrc /home/xk/deepflame/df_1be82b6/deepflame-dev/bashrc
```

### 2. Initialize the case

```bash
source /opt/openfoam7/etc/bashrc
source /home/xk/miniconda3/etc/profile.d/conda.sh
conda activate deepflame
source /home/xk/deepflame/df_1be82b6/deepflame-dev/bashrc

python -m dfode_kit.cli_tools.main init oneD-flame \
  --mech /home/xk/deepflame/df_1be82b6/deepflame-dev/mechanisms/CH4/gri30.yaml \
  --fuel CH4:1 \
  --oxidizer air \
  --phi 1.0 \
  --out /home/xk/deepflame_runs/oneD_flame_CH4_phi1_cli \
  --apply --force
```

### 3. Run the case

```bash
dfode-kit run-case \
  --case /home/xk/deepflame_runs/oneD_flame_CH4_phi1_cli \
  --apply --json
```

### 4. Sample the finished case

```bash
source /home/xk/miniconda3/etc/profile.d/conda.sh
conda activate deepflame
python -m dfode_kit.cli_tools.main sample \
  --mech /home/xk/deepflame/df_1be82b6/deepflame-dev/mechanisms/CH4/gri30.yaml \
  --case /home/xk/deepflame_runs/oneD_flame_CH4_phi1_cli \
  --save /home/xk/deepflame_runs/oneD_flame_CH4_phi1_cli/ch4_phi1_sample.h5 \
  --include_mesh
```
