# Getting Started

## Environment

A lightweight local verification environment can be created with:

```bash
make bootstrap-harness
source .venv/bin/activate
```

For full local usage of the CLI and training stack, install the project and its dependencies:

```bash
uv pip install --python .venv/bin/python -e '.[dev]'
```

## Verification

Run the standard local verification loop:

```bash
make verify
```

This currently performs:

- Python syntax checks via `compileall`
- the lightweight pytest suite

## Installation

Editable install:

```bash
git clone https://github.com/deepflame-ai/DFODE-kit.git
cd DFODE-kit
uv venv .venv
uv pip install --python .venv/bin/python -e '.[dev]'
```

## CLI entrypoint

If the console script is installed, use:

```bash
dfode-kit --help
```

A reliable fallback inside the repository is:

```bash
.venv/bin/python -m dfode_kit.cli.main --help
```

## Runtime environment split

Different stages of the workflow may require different dependencies:

- lightweight repository verification: local `.venv`
- canonical case initialization: Python environment with `cantera`
- case execution: configured OpenFOAM + Conda + DeepFlame runtime via `dfode-kit config` and `dfode-kit run-case`
- sampling / labeling: Python environment with `cantera`, `numpy`, and `h5py`

If you are starting with the case workflow, continue to:

1. [CLI](cli.md)
2. [Canonical Case Initialization](init.md)
3. [Runtime Configuration and Case Execution](run-case.md)
4. [Data Preparation and Training Workflow](data-workflow.md)

## Current focus

The project is being refactored toward:

- agent-friendly CLI behavior,
- dataset contracts,
- training/model registries,
- reproducible documentation and CI.
