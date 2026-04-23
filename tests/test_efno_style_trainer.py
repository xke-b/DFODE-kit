import torch

from dfode_kit.training.config import OptimizerConfig, TrainerConfig
from dfode_kit.training.efno_style import build_efno_style_trainer


class TinyModel(torch.nn.Module):
    def __init__(self, in_dim: int, out_dim: int):
        super().__init__()
        self.linear = torch.nn.Linear(in_dim, out_dim)

    def forward(self, x):
        return self.linear(x)


def test_efno_style_trainer_runs_single_epoch_on_toy_batch():
    batch = 4
    n_species = 3
    features = torch.zeros(batch, 2 + n_species)
    labels = torch.zeros(batch, n_species - 1)
    features_mean = torch.zeros(2 + n_species)
    features_std = torch.ones(2 + n_species)
    labels_mean = torch.zeros(n_species - 1)
    labels_std = torch.ones(n_species - 1)
    sample_weights = torch.ones(batch)
    element_mass_matrix = torch.tensor(
        [
            [1.0, 0.0],
            [0.0, 1.0],
            [0.5, 0.5],
        ],
        dtype=torch.float32,
    )

    trainer = build_efno_style_trainer(
        trainer_config=TrainerConfig(name="efno_style", max_epochs=1, batch_size=2),
        optimizer_config=OptimizerConfig(name="adam", lr=1e-3),
    )
    model = TinyModel(in_dim=2 + n_species, out_dim=n_species - 1)

    trainer.fit(
        model=model,
        features=features,
        labels=labels,
        features_mean=features_mean,
        features_std=features_std,
        labels_mean=labels_mean,
        labels_std=labels_std,
        sample_weights=sample_weights,
        element_mass_matrix=element_mass_matrix,
        time_step=1e-6,
    )
