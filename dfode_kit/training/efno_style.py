from __future__ import annotations

import torch

from dfode_kit.training.config import OptimizerConfig, TrainerConfig
from dfode_kit.utils import inverse_BCT_torch


class EFNOStyleTrainer:
    """Paper-oriented training slice for EFNO-style experiments.

    This trainer is not claimed to be the exact paper implementation. It is a
    practical approximation of the paper's stated ingredients:
    - weighted data loss
    - mass-fraction-sum conservation
    - element conservation

    The current DFODE-kit data contract still predicts only species updates, so
    temperature is not yet part of this trainer's supervised target.
    """

    def __init__(
        self,
        trainer_config: TrainerConfig,
        optimizer_config: OptimizerConfig,
    ) -> None:
        self.trainer_config = trainer_config
        self.optimizer_config = optimizer_config
        self.params = dict(trainer_config.params)

    def _build_optimizer(self, model):
        if self.optimizer_config.name != "adam":
            raise ValueError(
                f"Unsupported optimizer '{self.optimizer_config.name}'. Only 'adam' is implemented in this slice."
            )
        return torch.optim.Adam(model.parameters(), lr=self.optimizer_config.lr)

    def _loss_weights(self) -> tuple[float, float, float]:
        return (
            float(self.params.get("lambda_data", 1.0)),
            float(self.params.get("lambda_elements", 1.0)),
            float(self.params.get("lambda_mass", 1.0)),
        )

    def _decode_species_updates(
        self,
        *,
        batch_features,
        batch_labels,
        preds,
        features_mean,
        features_std,
        labels_mean,
        labels_std,
    ):
        base_y_full = inverse_BCT_torch(
            batch_features[:, 2:] * features_std[2:] + features_mean[2:],
            lam=0.1,
        )
        base_y_main = base_y_full[:, :-1]

        pred_delta_bct = preds * labels_std + labels_mean
        true_delta_bct = batch_labels * labels_std + labels_mean

        y_pred_main = inverse_BCT_torch(base_y_main.add(pred_delta_bct), lam=0.1)
        y_true_main = inverse_BCT_torch(base_y_main.add(true_delta_bct), lam=0.1)

        y_pred_last = torch.clamp(1.0 - y_pred_main.sum(dim=1, keepdim=True), min=0.0)
        y_true_last = torch.clamp(1.0 - y_true_main.sum(dim=1, keepdim=True), min=0.0)

        y_pred = torch.cat((y_pred_main, y_pred_last), dim=1)
        y_true = torch.cat((y_true_main, y_true_last), dim=1)

        y_pred = y_pred / torch.clamp(y_pred.sum(dim=1, keepdim=True), min=1e-12)
        y_true = y_true / torch.clamp(y_true.sum(dim=1, keepdim=True), min=1e-12)
        return y_pred, y_true

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
        sample_weights,
        element_mass_matrix,
        time_step: float,
        **_,
    ) -> None:
        del time_step
        optimizer = self._build_optimizer(model)
        model.train()
        lambda_data, lambda_elements, lambda_mass = self._loss_weights()

        for epoch in range(self.trainer_config.max_epochs):
            if epoch > 0 and epoch % self.trainer_config.lr_decay_epoch == 0:
                for param_group in optimizer.param_groups:
                    param_group["lr"] *= self.trainer_config.lr_decay_factor

            total_data_loss = 0.0
            total_element_loss = 0.0
            total_mass_loss = 0.0
            total_loss = 0.0

            for i in range(0, len(features), self.trainer_config.batch_size):
                batch_features = features[i:i + self.trainer_config.batch_size]
                batch_labels = labels[i:i + self.trainer_config.batch_size]
                batch_weights = sample_weights[i:i + self.trainer_config.batch_size]

                optimizer.zero_grad()
                preds = model(batch_features)

                y_pred, y_true = self._decode_species_updates(
                    batch_features=batch_features,
                    batch_labels=batch_labels,
                    preds=preds,
                    features_mean=features_mean,
                    features_std=features_std,
                    labels_mean=labels_mean,
                    labels_std=labels_std,
                )

                pointwise_sq = (y_pred - y_true).pow(2).mean(dim=1)
                data_loss = (batch_weights * pointwise_sq).mean()

                pred_element_mass = y_pred @ element_mass_matrix
                true_element_mass = y_true @ element_mass_matrix
                element_loss = torch.nn.functional.l1_loss(pred_element_mass, true_element_mass)

                mass_loss = torch.nn.functional.l1_loss(
                    y_pred.sum(dim=1),
                    torch.ones(y_pred.shape[0], device=y_pred.device),
                )

                loss = (
                    lambda_data * data_loss
                    + lambda_elements * element_loss
                    + lambda_mass * mass_loss
                )
                loss.backward()
                optimizer.step()

                total_data_loss += data_loss.item()
                total_element_loss += element_loss.item()
                total_mass_loss += mass_loss.item()
                total_loss += loss.item()

            batches = len(features) / self.trainer_config.batch_size
            total_data_loss /= batches
            total_element_loss /= batches
            total_mass_loss /= batches
            total_loss /= batches

            print(
                "Epoch: {}, DataLoss: {:4e}, ElementLoss: {:4e}, MassLoss: {:4e}, Loss: {:4e}".format(
                    epoch + 1,
                    total_data_loss,
                    total_element_loss,
                    total_mass_loss,
                    total_loss,
                )
            )



def build_efno_style_trainer(*, trainer_config: TrainerConfig, optimizer_config: OptimizerConfig):
    return EFNOStyleTrainer(trainer_config=trainer_config, optimizer_config=optimizer_config)
