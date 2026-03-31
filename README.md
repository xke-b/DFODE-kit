# DFODE-kit

DFODE-kit is a Python toolkit for building machine-learning surrogates for combustion chemistry integration.
It helps users move from **canonical flame simulations** to **sampled datasets**, **augmented and labeled training data**, and finally to **trained neural-network models** that can be deployed in DeepFlame/OpenFOAM workflows.

In practice, DFODE-kit sits between:
- **DeepFlame / OpenFOAM**, which generate and run reacting-flow cases, and
- **ML training workflows**, which need clean, structured, reproducible chemistry datasets.

## Documentation

- Project documentation: https://deepflame-ai.github.io/DFODE-kit/
- DeepFlame documentation: https://deepflame.deepmodeling.com/en/latest/
- DeepFlame source: https://github.com/deepmodeling/deepflame-dev

## What DFODE-kit does

DFODE-kit currently supports the core workflow below:

1. **Configure runtime paths** for OpenFOAM, Conda, and DeepFlame
2. **Initialize** canonical flame cases from explicit presets
3. **Run** those cases reproducibly
4. **Sample** thermochemical states into HDF5
5. **Augment** sampled datasets
6. **Label** them with Cantera/CVODE integration
7. **Train** neural-network surrogates

## Current CLI commands

- `config` — store machine-local runtime paths
- `init` — initialize canonical cases from explicit presets
- `run-case` — execute a case-local runner such as `Allrun`
- `sample` — convert case outputs to HDF5 datasets
- `augment` — augment sampled states
- `label` — generate supervised labels
- `train` — train a neural-network model
- `h52npy` — convert HDF5 scalar fields to NumPy arrays

List commands locally with:

```bash
dfode-kit --list-commands
```

## Installation

Clone the repository and install the package in editable mode:

```bash
git clone https://github.com/deepflame-ai/DFODE-kit.git
cd DFODE-kit
pip install -e .
```

If you want the lightweight local verification environment used in this repository:

```bash
uv venv .venv
uv pip install --python .venv/bin/python -e '.[dev]'
```

## Runtime requirements

DFODE-kit itself is a Python package, but some workflows also require local installations of:

- **OpenFOAM**
- **DeepFlame**
- **Conda** (or an equivalent Python environment manager)
- **Cantera** for case initialization and labeling workflows

For DeepFlame/OpenFOAM-backed case execution, you must configure machine-local runtime paths with `dfode-kit config`.

## Quickstart: 1D CH4 flame workflow

The example below shows a portable workflow for a 1D freely propagating premixed CH4/air flame at equivalence ratio 1.0.

### 1. Store machine-local runtime configuration

```bash
dfode-kit config set openfoam_bashrc /path/to/openfoam/etc/bashrc
dfode-kit config set conda_sh /path/to/conda/etc/profile.d/conda.sh
dfode-kit config set conda_env_name deepflame
dfode-kit config set deepflame_bashrc /path/to/deepflame-dev/bashrc
```

### 2. Initialize a canonical 1D flame case

Run this from a Python environment that has Cantera available:

```bash
source /path/to/openfoam/etc/bashrc
source /path/to/conda/etc/profile.d/conda.sh
conda activate deepflame
source /path/to/deepflame-dev/bashrc

python -m dfode_kit.cli_tools.main init oneD-flame \
  --mech /path/to/mechanisms/CH4/gri30.yaml \
  --fuel CH4:1 \
  --oxidizer air \
  --phi 1.0 \
  --out /path/to/run/oneD_flame_CH4_phi1 \
  --apply --force
```

### 3. Run the case

```bash
python -m dfode_kit.cli_tools.main run-case \
  --case /path/to/run/oneD_flame_CH4_phi1 \
  --apply --json
```

### 4. Sample the finished case into HDF5

```bash
python -m dfode_kit.cli_tools.main sample \
  --mech /path/to/mechanisms/CH4/gri30.yaml \
  --case /path/to/run/oneD_flame_CH4_phi1 \
  --save /path/to/run/oneD_flame_CH4_phi1/ch4_phi1_sample.h5 \
  --include_mesh
```

## Recommended documentation entry points

If you are using the CLI, start with:
- https://deepflame-ai.github.io/DFODE-kit/cli/
- https://deepflame-ai.github.io/DFODE-kit/init/
- https://deepflame-ai.github.io/DFODE-kit/run-case/

If you are working on the repository itself, see:
- `AGENTS.md`
- `docs/agents/README.md`

## Repository layout

- `dfode_kit/cli_tools/` — CLI entrypoints and subcommands
- `dfode_kit/df_interface/` — DeepFlame/OpenFOAM-facing helpers and case setup
- `dfode_kit/data_operations/` — dataset I/O, sampling, augmentation, labeling
- `dfode_kit/dfode_core/` — model and training code
- `canonical_cases/` — canonical flame case templates
- `tutorials/` — tutorial notebooks and workflow examples
- `docs/` — published project documentation
- `tests/` — lightweight verification tests

## Related papers

The following papers provide scientific context for DFODE-kit and closely related workflows:

### DFODE-kit package paper

```bibtex
@article{li2025dfode,
  title={DFODE-kit: Deep learning package for solving Flame chemical kinetics with high-dimensional stiff Ordinary Differential Equations},
  author={Li, Han and Xiao, Ke and Xu, Yangchen and Zhang, Haoze and Chen, Zhenyi and Mao, Runze and Chen, Zhi X},
  journal={Computer Physics Communications},
  pages={110013},
  year={2025},
  publisher={Elsevier}
}
```

### Multi-fuel generalization and a posteriori validation

```bibtex
@article{li2025comprehensive,
  title={Comprehensive deep learning for combustion chemistry integration: Multi-fuel generalization and a posteriori validation in reacting flow},
  author={Li, Han and Yang, Ruixin and Xu, Yangchen and Zhang, Min and Mao, Runze and Chen, Zhi X},
  journal={Physics of Fluids},
  volume={37},
  number={1},
  year={2025},
  publisher={AIP Publishing}
}
```

### Physics-aware data augmentation and scale separation

```bibtex
@article{xiao2026enhancing,
  title={Enhancing deep learning of ammonia/natural gas combustion kinetics via physics-aware data augmentation and scale separation},
  author={Xiao, Ke and Xu, Yangchen and Li, Han and Chen, Zhi X},
  journal={Fuel},
  volume={419},
  pages={138904},
  year={2026},
  publisher={Elsevier}
}
```

## Design principles in the current refactor

Recent work in this repository focuses on making DFODE-kit:

- easier to use from the CLI,
- easier for coding agents to operate safely,
- more reproducible for scientific workflows,
- more explicit about empirical setup assumptions,
- more modular for experimentation with model and training changes.

## Verification for contributors

This repository includes a lightweight local verification loop:

```bash
make bootstrap-harness
make verify
```

## License

This project is distributed under the terms in [`LICENSE`](LICENSE).
