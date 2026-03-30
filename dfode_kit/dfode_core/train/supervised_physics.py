from __future__ import annotations

import torch

from dfode_kit.dfode_core.train.config import OptimizerConfig, TrainerConfig


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
    ) -> None:
        loss_fn = torch.nn.L1Loss()
        optimizer = self._build_optimizer(model)
        model.train()

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
                loss1 = loss_fn(preds, batch_labels)

                base_y = batch_features[:, 2:-1] * features_std[2:-1] + features_mean[2:-1]
                Y_in = (base_y * 0.1 + 1) ** 10
                Y_out = (((preds * labels_std + labels_mean) + base_y) * 0.1 + 1) ** 10
                Y_target = (((batch_labels * labels_std + labels_mean) + base_y) * 0.1 + 1) ** 10

                loss2 = loss_fn(Y_out.sum(axis=1), Y_in.sum(axis=1))

                Y_out_total = torch.cat((Y_out, (1 - Y_out.sum(axis=1)).reshape(Y_out.shape[0], 1)), axis=1)
                Y_target_total = torch.cat((Y_target, (1 - Y_target.sum(axis=1)).reshape(Y_target.shape[0], 1)), axis=1)

                loss3 = loss_fn(
                    (formation_enthalpies * Y_out_total).sum(axis=1),
                    (formation_enthalpies * Y_target_total).sum(axis=1),
                ) / time_step
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
