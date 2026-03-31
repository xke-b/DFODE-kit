"""Training configuration, registries, and execution helpers."""

from importlib import import_module


__all__ = [
    "ModelConfig",
    "OptimizerConfig",
    "TrainerConfig",
    "TrainingConfig",
    "default_training_config",
    "with_overrides",
    "create_trainer",
    "get_trainer_factory",
    "register_trainer",
    "registered_trainers",
    "DataPreprocessor",
    "train",
]

_ATTRIBUTE_MODULES = {
    "ModelConfig": ("dfode_kit.training.config", "ModelConfig"),
    "OptimizerConfig": ("dfode_kit.training.config", "OptimizerConfig"),
    "TrainerConfig": ("dfode_kit.training.config", "TrainerConfig"),
    "TrainingConfig": ("dfode_kit.training.config", "TrainingConfig"),
    "default_training_config": ("dfode_kit.training.config", "default_training_config"),
    "with_overrides": ("dfode_kit.training.config", "with_overrides"),
    "create_trainer": ("dfode_kit.training.registry", "create_trainer"),
    "get_trainer_factory": ("dfode_kit.training.registry", "get_trainer_factory"),
    "register_trainer": ("dfode_kit.training.registry", "register_trainer"),
    "registered_trainers": ("dfode_kit.training.registry", "registered_trainers"),
    "DataPreprocessor": ("dfode_kit.training.preprocess", "DataPreprocessor"),
    "train": ("dfode_kit.training.train", "train"),
}


def __getattr__(name):
    if name not in _ATTRIBUTE_MODULES:
        raise AttributeError(f"module 'dfode_kit.training' has no attribute '{name}'")

    module_name, attribute_name = _ATTRIBUTE_MODULES[name]
    module = import_module(module_name)
    value = getattr(module, attribute_name)
    globals()[name] = value
    return value
