from __future__ import annotations

import torch

from dfode_kit.training.config import ModelConfig


class SpectralConv1d(torch.nn.Module):
    def __init__(self, in_channels: int, out_channels: int, modes: int) -> None:
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.modes = modes
        scale = 1 / max(1, in_channels * out_channels)
        self.weights = torch.nn.Parameter(
            scale * torch.randn(in_channels, out_channels, modes, dtype=torch.cfloat)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, _, signal_length = x.shape
        x_ft = torch.fft.rfft(x, dim=-1)
        usable_modes = min(self.modes, x_ft.size(-1))
        out_ft = torch.zeros(
            batch_size,
            self.out_channels,
            x_ft.size(-1),
            dtype=torch.cfloat,
            device=x.device,
        )
        out_ft[:, :, :usable_modes] = torch.einsum(
            "bim,iom->bom",
            x_ft[:, :, :usable_modes],
            self.weights[:, :, :usable_modes],
        )
        return torch.fft.irfft(out_ft, n=signal_length, dim=-1)


class FNO1d(torch.nn.Module):
    def __init__(
        self,
        *,
        input_tokens: int,
        output_tokens: int,
        width: int = 32,
        modes: int = 8,
        n_layers: int = 4,
        activation: str = "gelu",
    ) -> None:
        super().__init__()
        if input_tokens <= 0:
            raise ValueError("input_tokens must be positive")
        if output_tokens <= 0:
            raise ValueError("output_tokens must be positive")
        if n_layers <= 0:
            raise ValueError("n_layers must be positive")
        if width <= 0:
            raise ValueError("width must be positive")

        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.width = width
        self.modes = min(modes, input_tokens // 2 + 1)
        self.n_layers = n_layers

        self.lift = torch.nn.Linear(1, width)
        self.spectral_layers = torch.nn.ModuleList(
            [SpectralConv1d(width, width, self.modes) for _ in range(n_layers)]
        )
        self.pointwise_layers = torch.nn.ModuleList(
            [torch.nn.Conv1d(width, width, kernel_size=1) for _ in range(n_layers)]
        )
        self.project_channels = torch.nn.Sequential(
            torch.nn.Linear(width, width),
            _make_activation(activation),
            torch.nn.Linear(width, 1),
        )
        self.project_tokens = torch.nn.Linear(input_tokens, output_tokens)
        self.activation = _make_activation(activation)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.ndim != 2:
            raise ValueError(f"Expected 2D input [batch, tokens], got shape {tuple(x.shape)}")
        if x.shape[1] != self.input_tokens:
            raise ValueError(
                f"Expected token dimension {self.input_tokens}, got {x.shape[1]}"
            )

        x = self.lift(x.unsqueeze(-1))  # [batch, tokens, width]
        x = x.permute(0, 2, 1)  # [batch, width, tokens]

        for spectral, pointwise in zip(self.spectral_layers, self.pointwise_layers):
            x = self.activation(spectral(x) + pointwise(x))

        x = x.permute(0, 2, 1)  # [batch, tokens, width]
        x = self.project_channels(x).squeeze(-1)  # [batch, tokens]
        return self.project_tokens(x)


def _make_activation(name: str) -> torch.nn.Module:
    normalized = name.lower()
    if normalized == "gelu":
        return torch.nn.GELU()
    if normalized in {"leaky_relu", "lrelu"}:
        return torch.nn.LeakyReLU()
    raise ValueError(f"Unsupported activation '{name}'")


def build_fno1d(*, model_config: ModelConfig, n_species: int, device):
    params = dict(model_config.params)
    model = FNO1d(
        input_tokens=2 + n_species,
        output_tokens=n_species - 1,
        width=int(params.get("width", 32)),
        modes=int(params.get("modes", 8)),
        n_layers=int(params.get("n_layers", 4)),
        activation=str(params.get("activation", "gelu")),
    )
    return model.to(device)
