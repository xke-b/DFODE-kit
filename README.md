# DFODE-kit: Deep Learning Package for Combustion Kinetics

DFODE-kit is an open-source Python package designed to accelerate combustion simulations by efficiently solving flame chemical kinetics governed by high-dimensional stiff ordinary differential equations (ODEs). This package integrates deep learning methodologies to replace conventional numerical integration, enabling significant speedups and improved accuracy.

## Features
- **Efficient Sampling Module**: Extracts high-quality thermochemical states from low-dimensional manifolds in canonical flames.
- **Data Augmentation**: Enhances training datasets to approximate high-dimensional composition spaces in turbulent flames.
- **Neural Network Implementation**: Supports optimized training with physical constraints to ensure model fidelity.
- **Seamless Integration**: Easily deploy trained models within the DeepFlame CFD solver or other platforms like OpenFOAM.
- **Robust Performance**: Achieves high accuracy with up to two orders of magnitude speedup in various combustion scenarios.

## Environment Setup
Create a conda environment with Python 3.9:

```bash
conda create --name dfode_env python=3.9
conda activate dfode_env
```

## Installation
To install DFODE-kit, clone the repository and install the dependencies:

```bash
git clone https://github.com/deepflame-ai/DFODE-kit.git
cd DFODE-kit
pip install -e .
```

## Usage
Once you have installed DFODE-kit, you can use it to sample data, augment datasets, train models, and make predictions. Below is a basic command-line interface (CLI) format:

```bash
dfode-kit CMD ARGS
```


### Commands Available:
- `config`: Store machine-local runtime paths such as OpenFOAM, Conda, and DeepFlame activation scripts.
- `init`: Initialize canonical cases from explicit presets.
- `run-case`: Execute a case-local runner such as `Allrun` using stored runtime configuration.
- `sample`: Perform raw data sampling from canonical flame simulations.
- `augment`: Apply random noise and physical constraints to improve the training dataset.
- `label`: Generate supervised learning labels using Cantera's CVODE solver.
- `train`: Train neural network models based on the specified datasets and parameters.

For example, a validated end-to-end 1D flame workflow is:

```bash
# one-time machine-local runtime config
dfode-kit config set openfoam_bashrc /opt/openfoam7/etc/bashrc
dfode-kit config set conda_sh /home/xk/miniconda3/etc/profile.d/conda.sh
dfode-kit config set conda_env_name deepflame
dfode-kit config set deepflame_bashrc /home/xk/deepflame/df_1be82b6/deepflame-dev/bashrc

# init case from a DeepFlame-compatible Python env
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

# run case
python -m dfode_kit.cli_tools.main run-case \
  --case /home/xk/deepflame_runs/oneD_flame_CH4_phi1_cli \
  --apply --json

# sample case
python -m dfode_kit.cli_tools.main sample \
  --mech /home/xk/deepflame/df_1be82b6/deepflame-dev/mechanisms/CH4/gri30.yaml \
  --case /home/xk/deepflame_runs/oneD_flame_CH4_phi1_cli \
  --save /home/xk/deepflame_runs/oneD_flame_CH4_phi1_cli/ch4_phi1_sample.h5 \
  --include_mesh
```

Comprehensive tutorials are provided in the `tutorials/` directory, including step-by-step guides for 1D premixed flames and 2D HIT flames.

Note that running the simulations requires DeepFlame to be installed. Refer to the [DeepFlame GitHub repository](https://github.com/deepmodeling/deepflame-dev) and [documentation](https://deepflame.deepmodeling.com/en/latest/) for installation instructions.

## Directories
- **dfode-kit**: Main procedure and functions.
- **mechanisms**: Thermochemical mechanism folder.
- **canonical_cases**: Canonical cases for data sampling.
- **tutorials**: Tutorials with sampling cases. 

