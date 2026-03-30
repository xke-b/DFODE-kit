from __future__ import annotations

import torch

from dfode_kit.dfode_core.train.config import ModelConfig


class MLP(torch.nn.Module):
    def __init__(self, layer_info):
        super().__init__()

        self.net = torch.nn.Sequential()
        n = len(layer_info) - 1
        for i in range(n - 1):
            self.net.add_module(f"linear_layer_{i}", torch.nn.Linear(layer_info[i], layer_info[i + 1]))
            self.net.add_module(f"gelu_layer_{i}", torch.nn.GELU())
        self.net.add_module(f"linear_layer_{n - 1}", torch.nn.Linear(layer_info[n - 1], layer_info[n]))

    def forward(self, x):
        return self.net(x)


def build_mlp(*, model_config: ModelConfig, n_species: int, device):
    hidden_layers = list(model_config.params.get("hidden_layers", [400, 400, 400, 400]))
    layer_info = [2 + n_species, *hidden_layers, n_species - 1]
    return MLP(layer_info).to(device)
