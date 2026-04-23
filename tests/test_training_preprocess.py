import numpy as np
import torch

from dfode_kit.training.train import _prepare_training_tensors


def test_prepare_training_tensors_handles_constant_feature_columns_without_nan():
    # Layout: [T, P, Y1, Y2, Y3, T_next, P_next, Y1_next, Y2_next, Y3_next]
    labeled = np.array([
        [1200.0, 101325.0, 0.20, 0.30, 0.50, 1210.0, 101325.0, 0.19, 0.31, 0.50],
        [1300.0, 101325.0, 0.25, 0.25, 0.50, 1312.0, 101325.0, 0.24, 0.26, 0.50],
        [1400.0, 101325.0, 0.30, 0.20, 0.50, 1415.0, 101325.0, 0.29, 0.21, 0.50],
    ], dtype=np.float32)

    tensors = _prepare_training_tensors(labeled, n_species=3, device=torch.device("cpu"))

    assert torch.isfinite(tensors["features"]).all()
    assert torch.isfinite(tensors["labels"]).all()
    assert torch.isfinite(tensors["features_std"]).all()
    assert torch.isfinite(tensors["labels_std"]).all()

    # Pressure is constant, so the normalized column should collapse cleanly to zero.
    pressure_column = tensors["features"][:, 1]
    assert torch.allclose(pressure_column, torch.zeros_like(pressure_column))
    assert tensors["features_std"][1].item() == 1.0
