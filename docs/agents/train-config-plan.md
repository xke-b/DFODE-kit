# Training/config refactor plan

## Scope
Keep changes tightly limited to `dfode_kit/dfode_core/{model,train}` and the train CLI surface needed to select registered components. Do not redesign data loading, labeling, or DeepFlame integration in this slice.

## Current audit
- `dfode_kit/dfode_core/train/train.py` hard-codes:
  - model architecture (`MLP([2+n_species, 400, 400, 400, 400, n_species-1])`)
  - optimizer (`Adam`)
  - loop hyperparameters (`max_epochs`, LR schedule, batch size)
  - physics loss composition
- The top-level `train()` function mixes config construction, data prep, model creation, optimizer setup, and the epoch loop.
- Adding a new architecture or training algorithm currently requires editing the monolithic train module.

## Minimal target design
1. **Typed training config**
   - Add small dataclass-based config objects for:
     - model selection + kwargs
     - optimizer hyperparameters
     - trainer selection + loop hyperparameters
   - Keep a default config equivalent to today’s behavior.
2. **Model registry**
   - Add a simple in-process registry keyed by string name.
   - Default-register `mlp`.
   - Construction contract: `factory(model_config, *, n_species, device)`.
3. **Trainer registry hook**
   - Add the same registry pattern for trainers, but keep only one default trainer in this slice.
   - This creates the extension seam without rewriting the full training algorithm ecosystem.
4. **Refactor train entrypoint**
   - Preserve the public `train(mech_path, source_file, output_path, time_step=...)` signature.
   - Add optional `config` parameter and route model/trainer creation through registries.
   - Move loop internals into a trainer implementation function/class.
5. **Tests for lightweight harness**
   - Add pure-Python tests for config defaults/overrides and registry behavior.
   - Avoid torch/cantera dependencies in harness tests.

## First implementation slice in this branch
- Add dataclass config module.
- Add model + trainer registries.
- Register current MLP architecture behind the registry.
- Refactor `train.py` to use default config + registries while keeping behavior unchanged.
- Add lightweight tests for config/registry contracts.

## Follow-up slices
- CLI flags or config-file loading (`--model`, `--trainer`, `--config`).
- Multiple trainer implementations (baseline supervised vs physics-informed variants).
- Synthetic smoke training test path that runs in the lightweight harness.
- Dataset schema validation before training starts.
