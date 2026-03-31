"""Compatibility shim for :mod:`dfode_kit.models.registry`."""

from dfode_kit.models.registry import create_model, get_model_factory, register_model, registered_models

__all__ = [
    "create_model",
    "get_model_factory",
    "register_model",
    "registered_models",
]
