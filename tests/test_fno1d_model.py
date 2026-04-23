import torch

from dfode_kit.models import build_fno1d
from dfode_kit.training.config import ModelConfig


def test_build_fno1d_forward_shape_matches_species_delta_target():
    n_species = 7
    model = build_fno1d(
        model_config=ModelConfig(
            name="fno1d",
            params={"width": 16, "modes": 4, "n_layers": 3, "activation": "gelu"},
        ),
        n_species=n_species,
        device=torch.device("cpu"),
    )

    x = torch.randn(5, 2 + n_species)
    y = model(x)
    assert y.shape == (5, n_species - 1)


def test_build_fno1d_rejects_wrong_token_count():
    n_species = 7
    model = build_fno1d(
        model_config=ModelConfig(name="fno1d", params={"width": 8, "modes": 3, "n_layers": 2}),
        n_species=n_species,
        device=torch.device("cpu"),
    )

    bad = torch.randn(2, 2 + n_species + 1)
    try:
        model(bad)
    except ValueError as exc:
        assert "Expected token dimension" in str(exc)
    else:
        raise AssertionError("Expected ValueError for mismatched token dimension")
