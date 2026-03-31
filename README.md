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
- `init`: Initialize canonical cases from explicit presets.
- `sample`: Perform raw data sampling from canonical flame simulations.
- `augment`: Apply random noise and physical constraints to improve the training dataset.
- `label`: Generate supervised learning labels using Cantera's CVODE solver.
- `train`: Train neural network models based on the specified datasets and parameters.

For example, preview a parameterized 1D premixed flame case:

```bash
dfode-kit init oneD-flame \
  --mech /path/to/gri30.yaml \
  --fuel CH4:1 \
  --oxidizer air \
  --phi 1.0 \
  --out /tmp/ch4_phi1_case \
  --preview --json
```


Comprehensive tutorials are provided in the `tutorials/` directory, including step-by-step guides for 1D premixed flames and 2D HIT flames.

Note that running the simulations requires DeepFlame to be installed. Refer to the [DeepFlame GitHub repository](https://github.com/deepmodeling/deepflame-dev) and [documentation](https://deepflame.deepmodeling.com/en/latest/) for installation instructions.

## Directories
- **dfode-kit**: Main procedure and functions.
- **mechanisms**: Thermochemical mechanism folder.
- **canonical_cases**: Canonical cases for data sampling.
- **tutorials**: Tutorials with sampling cases. 

