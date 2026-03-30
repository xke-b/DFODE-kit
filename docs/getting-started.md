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

## Current focus

The project is being refactored toward:

- agent-friendly CLI behavior,
- dataset contracts,
- training/model registries,
- reproducible documentation and CI.
