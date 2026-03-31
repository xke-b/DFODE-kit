"""Compatibility shim for :mod:`dfode_kit.training.supervised_physics`."""

from dfode_kit.training.supervised_physics import (
    SupervisedPhysicsTrainer,
    build_supervised_physics_trainer,
)

__all__ = ["SupervisedPhysicsTrainer", "build_supervised_physics_trainer"]
