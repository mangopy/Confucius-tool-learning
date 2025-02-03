from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning.callbacks import LearningRateMonitor
from pytorch_lightning.strategies import DeepSpeedStrategy
from data import *
from utils import *
from model import *
from torch.nn import  CrossEntropyLoss
from pytorch_lightning import loggers as pl_loggers
from torch.utils.data import DataLoader

def train(args):
    # load the model and tokenizer, we provide the llama-based model
    model,tokenizer=make_model_tokenizer(args.model_name_or_path,model_max_length=args.max_length,cache_dir=args.cache_dir,load_in_8bit=args.load_in_8bit)
    # load the dataset
    train_dataset = SupervisedDataset(tokenizer=tokenizer, data_path=args.train_data_path, max_length=args.train_length,
                                      split=[args.warmup, args.in_category, args.corss_category])

    train_data_collator = DataCollatorForTuning(tokenizer=tokenizer,train=True)

    #build the dataloader with the customized collate function
    train_dataloaders = DataLoader(train_dataset, batch_size=args.per_device_train_batch_size,
                                   collate_fn=train_data_collator, num_workers=args.num_works,pin_memory=args.pin_memory,shuffle=True)

    every_n_steps = None if args.checkpoint_every_n_steps == 0 else args.checkpoint_every_n_steps
    every_n_epochs = None if args.checkpoint_every_n_epochs == 0  or args.checkpoint_every_n_steps > 0  else args.checkpoint_every_n_epochs
    print(f"every_n_steps={every_n_steps},every_n_epochs={every_n_epochs}")

    deep_strategy = DeepSpeedStrategy(
        stage=3,
        offload_optimizer=True,
        offload_parameters=True,
        pin_memory=args.pin_memory,
    )

    checkpoint_callback = ModelCheckpoint(
        monitor='global-step',
        mode='max',
        save_top_k=2,
        verbose=True,
        dirpath="/data/checkpoint",
        every_n_train_steps=every_n_steps,
        every_n_epochs=every_n_epochs,
        filename="llama-{epoch:02d}-{global-step}",
    )
    lr_monitor = LearningRateMonitor(logging_interval='step')

    tb_logger = pl_loggers.CSVLogger('logs',name="my_exp_name",flush_logs_every_n_steps=1)

    # build pytorch-lightning  trainer
    trainer = pl.Trainer(devices=args.num_device_per_node,
                         accelerator=args.accelerator,
                         strategy=deep_strategy,
                         num_nodes=args.num_nodes,
                         accumulate_grad_batches=args.gradient_accumulation_steps,
                         log_every_n_steps=args.log_every_n_steps,
                         min_epochs=args.min_epochs,
                         max_epochs=args.max_epochs,
                         max_steps=args.max_steps,
                         enable_checkpointing=True,
                         precision=args.precision,
                         gradient_clip_val=args.gradient_clip_val,
                         logger=tb_logger,
                         callbacks=[checkpoint_callback, lr_monitor],
                         # ckpt_path=training_args.resume_model_path,
                         )
    # warp with the pytorch-lightning library to enable the deepspeed training.
    pl_model = PLModel(
        model=model,
        learning_rate=args.learning_rate
    )
    trainer.fit(model=pl_model,
                train_dataloaders=train_dataloaders,
                # ckpt_path=training_args.resume_model_path,
                # val_dataloaders=eval_dataloaders
                )
    trainer.save_checkpoint(args.output_dir)

# Filter the dataset with ppl, which can be reflected with the log likelihood loss of language modeling objective
def update(model_name_or_path,data,naive,in_category,corss_category,batch_size=4,max_length=1024,cache_dir=None,load_in_8bit=None,num_works=4):
    model, tokenizer = make_model_tokenizer(model_name_or_path, model_max_length=max_length,cache_dir=cache_dir, load_in_8bit=load_in_8bit,train=False)
    # load the dataset as training process to enable the batch computation
    train_dataset = SupervisedDataset(tokenizer=tokenizer, data_path=data, max_length=max_length,
                                      split=[naive, in_category, corss_category])
    train_data_collator = DataCollatorForTuning(tokenizer=tokenizer,train=False)
    train_dataloaders = DataLoader(train_dataset, batch_size=batch_size,
                                   collate_fn=train_data_collator, num_workers=num_works,shuffle=False)
    model.eval()
    # 
    # model.to(device) 

    losses=[]
    loss_fct=CrossEntropyLoss(reduction='mean')
    with torch.no_grad():
        for line in tqdm(train_dataloaders):
           logits=model(input_ids=line['input_ids'].to(model.device),attention_mask=line['attention_mask'].to(model.device))['logits']
           labels=line['labels']
           # Shift so that tokens < n predict n
           shift_logits = logits[..., :-1, :].contiguous()
           shift_labels = labels[..., 1:].contiguous()
           shift_labels = shift_labels.to(shift_logits.device)
           for slabel,slogit in zip(shift_labels,shift_logits):
               loss = loss_fct(slogit,slabel)
               losses.append(loss.item())

    for line,loss in zip(data,losses):
        line['loss']=loss

    data=sorted(data,key=lambda x: x['loss'])
    for line in data:
        # loss=line.pop('loss')
        print(line['_answer'])
        print(line['loss'])
    return data


