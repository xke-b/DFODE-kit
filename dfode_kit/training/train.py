from __future__ import annotations

import numpy as np
import torch

from dfode_kit.models.fno1d import build_fno1d
from dfode_kit.models.mlp import build_mlp
from dfode_kit.models.registry import create_model, register_model
from dfode_kit.training.config import TrainingConfig, default_training_config, with_overrides
from dfode_kit.training.efno_style import build_efno_style_trainer
from dfode_kit.training.formation import formation_calculate
from dfode_kit.training.registry import create_trainer, register_trainer
from dfode_kit.training.supervised_physics import build_supervised_physics_trainer
from dfode_kit.utils import BCT


def _safe_std(tensor: torch.Tensor, dim: int, eps: float = 1e-12) -> torch.Tensor:
    std = torch.std(tensor, dim=dim, unbiased=False)
    return torch.where(std < eps, torch.ones_like(std), std)


def _compute_sample_weights(thermochem_states1: np.ndarray, thermochem_states2: np.ndarray) -> torch.Tensor:
    delta = np.mean(np.abs(thermochem_states2[:, 2:] - thermochem_states1[:, 2:]), axis=1)
    q1 = float(np.quantile(delta, 0.25))
    q3 = float(np.quantile(delta, 0.75))
    iqr = q3 - q1
    low_threshold = q1 - iqr

    weights = np.full(delta.shape, 0.5, dtype=np.float32)
    weights[delta > q3] = 1.0
    weights[delta < low_threshold] = 0.1
    return torch.tensor(weights, dtype=torch.float32)



def _build_element_mass_matrix(gas) -> np.ndarray:
    matrix = np.zeros((gas.n_species, gas.n_elements), dtype=np.float32)
    for s_idx, species in enumerate(gas.species()):
        molecular_weight = gas.molecular_weights[s_idx]
        for e_idx, element_name in enumerate(gas.element_names):
            n_atoms = species.composition.get(element_name, 0.0)
            if n_atoms == 0:
                continue
            atomic_weight = gas.atomic_weights[e_idx]
            matrix[s_idx, e_idx] = n_atoms * atomic_weight / molecular_weight
    return matrix



def _prepare_training_tensors(labeled_data: np.ndarray, n_species: int, device):
    thermochem_states1 = labeled_data[:, 0 : 2 + n_species].copy()
    thermochem_states2 = labeled_data[:, 2 + n_species :].copy()

    print(thermochem_states1.shape, thermochem_states2.shape)
    thermochem_states1[:, 2:] = np.clip(thermochem_states1[:, 2:], 0, 1)
    thermochem_states2[:, 2:] = np.clip(thermochem_states2[:, 2:], 0, 1)

    features = torch.tensor(
        np.hstack((thermochem_states1[:, :2], BCT(thermochem_states1[:, 2:]))),
        dtype=torch.float32,
    ).to(device)
    labels = torch.tensor(
        BCT(thermochem_states2[:, 2:-1]) - BCT(thermochem_states1[:, 2:-1]),
        dtype=torch.float32,
    ).to(device)

    features_mean = torch.mean(features, dim=0)
    features_std = _safe_std(features, dim=0)
    labels_mean = torch.mean(labels, dim=0)
    labels_std = _safe_std(labels, dim=0)

    normalized_features = (features - features_mean) / features_std
    normalized_labels = (labels - labels_mean) / labels_std

    return {
        "features": normalized_features,
        "labels": normalized_labels,
        "features_mean": features_mean,
        "features_std": features_std,
        "labels_mean": labels_mean,
        "labels_std": labels_std,
        "sample_weights": _compute_sample_weights(thermochem_states1, thermochem_states2).to(device),
    }


def _register_defaults() -> None:
    register_model("mlp", build_mlp)
    register_model("fno1d", build_fno1d)
    register_trainer("supervised_physics", build_supervised_physics_trainer)
    register_trainer("efno_style", build_efno_style_trainer)



def train(
    mech_path: str,
    source_file: str,
    output_path: str,
    time_step: float = 1e-6,
    config: TrainingConfig | None = None,
) -> np.ndarray:
    """Train a model using registry-selected components.

    The default config preserves the previous hard-coded MLP + Adam +
    supervised-physics training behavior while making model/trainer selection
    replaceable without editing this entrypoint.
    """

    _register_defaults()
    effective_config = with_overrides(config or default_training_config(), time_step=time_step)
    import cantera as ct

    labeled_data = np.load(source_file)

    gas = ct.Solution(mech_path)
    n_species = gas.n_species
    formation_enthalpies = formation_calculate(mech_path)
    element_mass_matrix = _build_element_mass_matrix(gas)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = create_model(
        effective_config.model.name,
        model_config=effective_config.model,
        n_species=n_species,
        device=device,
    )

    training_tensors = _prepare_training_tensors(labeled_data, n_species, device)
    training_tensors["formation_enthalpies"] = torch.tensor(
        formation_enthalpies,
        dtype=torch.float32,
    ).to(device)
    training_tensors["element_mass_matrix"] = torch.tensor(
        element_mass_matrix,
        dtype=torch.float32,
    ).to(device)

    trainer = create_trainer(
        effective_config.trainer.name,
        trainer_config=effective_config.trainer,
        optimizer_config=effective_config.optimizer,
    )
    trainer.fit(model=model, time_step=effective_config.time_step, **training_tensors)

    torch.save(
        {
            "net": model.state_dict(),
            "data_in_mean": training_tensors["features_mean"].cpu().numpy(),
            "data_in_std": training_tensors["features_std"].cpu().numpy(),
            "data_target_mean": training_tensors["labels_mean"].cpu().numpy(),
            "data_target_std": training_tensors["labels_std"].cpu().numpy(),
            "training_config": {
                "model": {
                    "name": effective_config.model.name,
                    "params": dict(effective_config.model.params),
                },
                "optimizer": {
                    "name": effective_config.optimizer.name,
                    "lr": effective_config.optimizer.lr,
                },
                "trainer": {
                    "name": effective_config.trainer.name,
                    "max_epochs": effective_config.trainer.max_epochs,
                    "lr_decay_epoch": effective_config.trainer.lr_decay_epoch,
                    "lr_decay_factor": effective_config.trainer.lr_decay_factor,
                    "batch_size": effective_config.trainer.batch_size,
                    "params": dict(effective_config.trainer.params),
                },
                "time_step": effective_config.time_step,
            },
        },
        output_path,
    )
