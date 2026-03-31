"""Compatibility shim for :mod:`dfode_kit.training.registry`."""

from dfode_kit.training.registry import create_trainer, get_trainer_factory, register_trainer, registered_trainers

__all__ = [
    "create_trainer",
    "get_trainer_factory",
    "register_trainer",
    "registered_trainers",
]
