from __future__ import annotations

from typing import Callable, Dict


TrainerFactory = Callable[..., object]
_TRAINER_REGISTRY: Dict[str, TrainerFactory] = {}


def register_trainer(name: str, factory: TrainerFactory) -> None:
    if not name:
        raise ValueError("Trainer name must be non-empty.")
    _TRAINER_REGISTRY[name] = factory


def get_trainer_factory(name: str) -> TrainerFactory:
    try:
        return _TRAINER_REGISTRY[name]
    except KeyError as exc:
        available = ", ".join(sorted(_TRAINER_REGISTRY)) or "<none>"
        raise KeyError(f"Unknown trainer '{name}'. Available trainers: {available}") from exc


def create_trainer(name: str, **kwargs):
    return get_trainer_factory(name)(**kwargs)


def registered_trainers():
    return tuple(sorted(_TRAINER_REGISTRY))
