"""Compatibility shim for :mod:`dfode_kit.training.config`."""

from dfode_kit.training.config import (
    ModelConfig,
    OptimizerConfig,
    TrainerConfig,
    TrainingConfig,
    default_training_config,
    with_overrides,
)

__all__ = [
    "ModelConfig",
    "OptimizerConfig",
    "TrainerConfig",
    "TrainingConfig",
    "default_training_config",
    "with_overrides",
]
