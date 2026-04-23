from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ModelConfig:
    name: str = "mlp"
    params: Dict[str, Any] = field(default_factory=lambda: {
        "hidden_layers": [400, 400, 400, 400],
    })


@dataclass(frozen=True)
class OptimizerConfig:
    name: str = "adam"
    lr: float = 1e-3


@dataclass(frozen=True)
class TrainerConfig:
    name: str = "supervised_physics"
    max_epochs: int = 1500
    lr_decay_epoch: int = 500
    lr_decay_factor: float = 0.1
    batch_size: int = 20000
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TrainingConfig:
    model: ModelConfig = field(default_factory=ModelConfig)
    optimizer: OptimizerConfig = field(default_factory=OptimizerConfig)
    trainer: TrainerConfig = field(default_factory=TrainerConfig)
    time_step: float = 1e-6


def default_training_config() -> TrainingConfig:
    return TrainingConfig()


def with_overrides(
    config: Optional[TrainingConfig] = None,
    *,
    model: Optional[ModelConfig] = None,
    optimizer: Optional[OptimizerConfig] = None,
    trainer: Optional[TrainerConfig] = None,
    time_step: Optional[float] = None,
) -> TrainingConfig:
    base = config or default_training_config()
    return replace(
        base,
        model=model or base.model,
        optimizer=optimizer or base.optimizer,
        trainer=trainer or base.trainer,
        time_step=base.time_step if time_step is None else time_step,
    )
