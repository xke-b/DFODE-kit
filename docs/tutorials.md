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
