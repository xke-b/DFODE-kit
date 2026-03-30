from __future__ import annotations

from typing import Callable, Dict


ModelFactory = Callable[..., object]
_MODEL_REGISTRY: Dict[str, ModelFactory] = {}


def register_model(name: str, factory: ModelFactory) -> None:
    if not name:
        raise ValueError("Model name must be non-empty.")
    _MODEL_REGISTRY[name] = factory


def get_model_factory(name: str) -> ModelFactory:
    try:
        return _MODEL_REGISTRY[name]
    except KeyError as exc:
        available = ", ".join(sorted(_MODEL_REGISTRY)) or "<none>"
        raise KeyError(f"Unknown model '{name}'. Available models: {available}") from exc


def create_model(name: str, **kwargs):
    return get_model_factory(name)(**kwargs)


def registered_models():
    return tuple(sorted(_MODEL_REGISTRY))
