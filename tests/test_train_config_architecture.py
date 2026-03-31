from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "dfode_kit" / "training" / "config.py"
MODEL_REGISTRY_PATH = ROOT / "dfode_kit" / "models" / "registry.py"
TRAINER_REGISTRY_PATH = ROOT / "dfode_kit" / "training" / "registry.py"
PLAN_PATH = ROOT / "docs" / "agents" / "train-config-plan.md"


def load_module(name: str, path: Path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


config = load_module("dfode_train_config_module", CONFIG_PATH)
model_registry = load_module("dfode_model_registry_module", MODEL_REGISTRY_PATH)
trainer_registry = load_module("dfode_trainer_registry_module", TRAINER_REGISTRY_PATH)


def test_train_config_defaults_preserve_current_baseline():
    cfg = config.default_training_config()
    assert cfg.model.name == "mlp"
    assert cfg.model.params["hidden_layers"] == [400, 400, 400, 400]
    assert cfg.optimizer.name == "adam"
    assert cfg.optimizer.lr == pytest.approx(1e-3)
    assert cfg.trainer.name == "supervised_physics"
    assert cfg.trainer.max_epochs == 1500
    assert cfg.trainer.lr_decay_epoch == 500
    assert cfg.trainer.batch_size == 20000
    assert cfg.time_step == pytest.approx(1e-6)


def test_with_overrides_replaces_selected_sections_only():
    base = config.default_training_config()
    updated = config.with_overrides(
        base,
        model=config.ModelConfig(name="toy", params={"depth": 2}),
        time_step=5e-7,
    )

    assert updated.model.name == "toy"
    assert updated.model.params == {"depth": 2}
    assert updated.optimizer == base.optimizer
    assert updated.trainer == base.trainer
    assert updated.time_step == pytest.approx(5e-7)


def test_model_registry_supports_lightweight_factory_injection():
    def factory(**kwargs):
        return {"kind": "model", **kwargs}

    model_registry.register_model("unit_test_model", factory)
    built = model_registry.create_model("unit_test_model", alpha=3)
    assert built == {"kind": "model", "alpha": 3}
    assert "unit_test_model" in model_registry.registered_models()


def test_trainer_registry_supports_lightweight_factory_injection():
    def factory(**kwargs):
        return {"kind": "trainer", **kwargs}

    trainer_registry.register_trainer("unit_test_trainer", factory)
    built = trainer_registry.create_trainer("unit_test_trainer", beta=7)
    assert built == {"kind": "trainer", "beta": 7}
    assert "unit_test_trainer" in trainer_registry.registered_trainers()


def test_registry_errors_include_available_names():
    with pytest.raises(KeyError) as excinfo:
        model_registry.get_model_factory("does_not_exist")
    assert "Unknown model 'does_not_exist'" in str(excinfo.value)


def test_canonical_training_and_model_modules_are_importable():
    canonical_config = import_module("dfode_kit.training.config")
    canonical_model_registry = import_module("dfode_kit.models.registry")
    canonical_trainer_registry = import_module("dfode_kit.training.registry")

    assert canonical_config.TrainingConfig is not None
    assert callable(canonical_model_registry.register_model)
    assert callable(canonical_trainer_registry.register_trainer)


def test_training_plan_doc_exists_and_mentions_registry_design():
    content = PLAN_PATH.read_text()
    assert "Model registry" in content
    assert "Typed training config" in content
    assert "First implementation slice" in content
    assert "dfode_kit/models" in content
    assert "dfode_kit/training" in content
