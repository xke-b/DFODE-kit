# Tutorials and Workflow

DFODE-kit is intended to support a workflow like:

1. **Sample** states from canonical flames
2. **Augment** underrepresented thermochemical regions
3. **Label** with CVODE/Cantera
4. **Train** a surrogate model
5. **Validate** in a priori / a posteriori simulations
6. **Deploy** in DeepFlame / CFD workflows

## Existing tutorial assets

The repository already includes notebook-based tutorial material under:

- `tutorials/oneD_freely_propagating_flame/`
- `tutorials/twoD_HIT_flame/`

## Documentation direction

A future docs iteration can bring notebook tutorials into the published site, but this first MkDocs setup focuses on:

- lightweight Markdown docs,
- repository architecture,
- CLI guidance,
- agent and maintainer workflow documentation.

## Practical workflow entry points

For reproducible command-line usage, use the published Markdown docs in this order:

1. [Getting Started](getting-started.md)
2. [CLI](cli.md)
3. [Canonical Case Initialization](init.md)
4. [Runtime Configuration and Case Execution](run-case.md)
5. [Data Preparation and Training Workflow](data-workflow.md)

That sequence reflects the currently validated path from case creation to sampled/training-ready datasets.
