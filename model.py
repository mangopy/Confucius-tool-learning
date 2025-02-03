from transformers import get_linear_schedule_with_warmup
import pytorch_lightning  as pl
from deepspeed.ops.adam import DeepSpeedCPUAdam
import torch
from deepspeed.accelerator import get_accelerator


class PLModel(pl.LightningModule):
    def __init__(
        self,
        model,
        cache_dir: str = None,
        num_new_tokens: int  = 0,
        len_tokenizer: int = None,
        learning_rate: float = 2e-5,
        adam_epsilon: float = 1e-8,
        warmup_step_rate: float = 0.1,
        weight_decay: float = 0.99,
        **kwargs
    ):
        super().__init__()
        self.save_hyperparameters(ignore=['model'])
        self.learning_rate=learning_rate
        self.cache_dir = cache_dir
        self.num_new_tokens = num_new_tokens
        self.len_tokenizer = len_tokenizer
        self.model=model

    def forward(self, *args, **kwargs):
        # in lightning, forward defines the prediction/inference actions
        output = self.model(*args, **kwargs)
        return output

    def training_step(self, batch, batch_idx):
        output = self.model(**batch)
        loss = output['loss']
        self.log("train-loss", loss.item())
        self.log('global-step', self.global_step * 1.0)
        get_accelerator().empty_cache()
        torch.cuda.empty_cache()
        return loss

    def validation_step(self, batch, batch_idx):
        gen_kwargs = {
            "max_new_tokens": 256,
            "num_beams": 2,
            "do_sample": True,
            "temperature": 0.5,
        }
        output = self.model.generate(input_ids=batch['input_ids'],
                                     attention_mask=batch['attention_mask'],
                                     **gen_kwargs)
        print(output)
        # print('***********evaluate**************')
        # print(output)
        # self.log_dict({'val_loss': loss, 'val_acc': val_acc})


    def configure_optimizers(self):
        """Prepare optimizer and schedule (linear warmup and decay)"""
        model = self.model
        no_decay = ["bias", "LayerNorm.weight"]
        optimizer_grouped_parameters = [
            {
                "params": [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)],
                "weight_decay": 0.0,
            },
            {
                "params": [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)],
                "weight_decay": 0.0,
            },
        ]
        print('*****************')
        print(self.hparams.learning_rate)
        print('*****************')
        optimizer = DeepSpeedCPUAdam(optimizer_grouped_parameters, lr=self.hparams.learning_rate, eps=self.hparams.adam_epsilon)
        # optimizer = AdamW(optimizer_grouped_parameters, lr=self.hparams.learning_rate, eps=self.hparams.adam_epsilon)

        self.stepping_batches = self.trainer.estimated_stepping_batches

        # scheduler = get_cosine_schedule_with_warmup(
        #     optimizer,
        #     num_warmup_steps=int(self.stepping_batches * self.hparams.warmup_step_rate),
        #     num_training_steps=self.stepping_batches,
        # )
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=100,
            num_training_steps=1000000,
        )
        scheduler = {"scheduler": scheduler, "interval": "step", "frequency": 1}

        return [optimizer], [scheduler]
