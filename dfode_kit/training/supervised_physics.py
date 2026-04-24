from __future__ import annotations

import torch

from dfode_kit.training.config import OptimizerConfig, TrainerConfig
from dfode_kit.utils import inverse_BCT_torch, inverse_power_transform_torch


class SupervisedPhysicsTrainer:
    def __init__(
        self,
        trainer_config: TrainerConfig,
        optimizer_config: OptimizerConfig,
    ) -> None:
        self.trainer_config = trainer_config
        self.optimizer_config = optimizer_config

    def _build_optimizer(self, model):
        if self.optimizer_config.name != "adam":
            raise ValueError(
                f"Unsupported optimizer '{self.optimizer_config.name}'. Only 'adam' is implemented in this slice."
            )
        return torch.optim.Adam(model.parameters(), lr=self.optimizer_config.lr)

    def fit(
        self,
        *,
        model,
        features,
        labels,
        features_mean,
        features_std,
        labels_mean,
        labels_std,
        formation_enthalpies,
        time_step: float,
        target_mode: str = "species_only",
        power_lambda: float = 0.1,
        **_,
    ) -> None:
        optimizer = self._build_optimizer(model)
        model.train()

        raw_channel_weights = self.trainer_config.params.get("species_loss_channel_weights")
        channel_weights = None
        if raw_channel_weights is not None:
            channel_weights = torch.tensor(raw_channel_weights, dtype=torch.float32, device=features.device)

        for epoch in range(self.trainer_config.max_epochs):
            if epoch > 0 and epoch % self.trainer_config.lr_decay_epoch == 0:
                for param_group in optimizer.param_groups:
                    param_group["lr"] *= self.trainer_config.lr_decay_factor

            total_loss1 = 0.0
            total_loss2 = 0.0
            total_loss3 = 0.0
            total_loss = 0.0

            for i in range(0, len(features), self.trainer_config.batch_size):
                batch_features = features[i:i + self.trainer_config.batch_size]
                batch_labels = labels[i:i + self.trainer_config.batch_size]

                optimizer.zero_grad()

                preds = model(batch_features)

                species_offset = 1 if batch_labels.shape[1] == batch_features.shape[1] - 2 else 0
                pred_species = preds[:, species_offset:]
                label_species = batch_labels[:, species_offset:]
                label_mean_species = labels_mean[species_offset:]
                label_std_species = labels_std[species_offset:]

                if species_offset > 0:
                    loss_temp = torch.mean(torch.abs(preds[:, :species_offset] - batch_labels[:, :species_offset]))
                else:
                    loss_temp = torch.tensor(0.0, device=preds.device)

                if channel_weights is not None:
                    if channel_weights.numel() != pred_species.shape[1]:
                        raise ValueError(
                            f"species_loss_channel_weights length {channel_weights.numel()} does not match species output dim {pred_species.shape[1]}"
                        )
                    loss_species = (torch.abs(pred_species - label_species) * channel_weights.unsqueeze(0)).mean()
                else:
                    loss_species = torch.mean(torch.abs(pred_species - label_species))

                loss1 = loss_temp + loss_species
                base_species_bct = batch_features[:, 2:-1] * features_std[2:-1] + features_mean[2:-1]
                Y_in = inverse_BCT_torch(base_species_bct)
                pred_species_raw = pred_species * label_std_species + label_mean_species
                label_species_raw = label_species * label_std_species + label_mean_species
                if target_mode == "species_power_delta":
                    Y_out = torch.clamp(Y_in + inverse_power_transform_torch(pred_species_raw, lam=power_lambda), 0.0, 1.0)
                    Y_target = torch.clamp(Y_in + inverse_power_transform_torch(label_species_raw, lam=power_lambda), 0.0, 1.0)
                else:
                    Y_out = inverse_BCT_torch(pred_species_raw + base_species_bct)
                    Y_target = inverse_BCT_torch(label_species_raw + base_species_bct)

                loss2 = torch.mean(torch.abs(Y_out.sum(axis=1) - Y_in.sum(axis=1)))

                Y_out_total = torch.cat((Y_out, (1 - Y_out.sum(axis=1)).reshape(Y_out.shape[0], 1)), axis=1)
                Y_target_total = torch.cat((Y_target, (1 - Y_target.sum(axis=1)).reshape(Y_target.shape[0], 1)), axis=1)

                loss3 = torch.mean(torch.abs(
                    (formation_enthalpies * Y_out_total).sum(axis=1)
                    - (formation_enthalpies * Y_target_total).sum(axis=1)
                )) / time_step
                loss = loss1 + loss2 + loss3 / 1e13

                total_loss1 += loss1.item()
                total_loss2 += loss2.item()
                total_loss3 += loss3.item()
                total_loss += loss.item()

                loss.backward()
                optimizer.step()

            batches = len(features) / self.trainer_config.batch_size
            total_loss1 /= batches
            total_loss2 /= batches
            total_loss3 /= batches
            total_loss /= batches

            print(
                "Epoch: {}, Loss1: {:4e}, Loss2: {:4e}, Loss3: {:4e}, Loss: {:4e}".format(
                    epoch + 1,
                    total_loss1,
                    total_loss2,
                    total_loss3,
                    total_loss,
                )
            )


def build_supervised_physics_trainer(*, trainer_config: TrainerConfig, optimizer_config: OptimizerConfig):
    return SupervisedPhysicsTrainer(trainer_config=trainer_config, optimizer_config=optimizer_config)
