from train import *
import argparse
import os


if __name__ == '__main__':
    os.environ['OMP_NUM_THREADS']='60'
    model2path = {
         'llama':'your path',
    }
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name_or_path", default='llama', type=str)
    parser.add_argument("--load_in_8bit", default=False, type=bool)

    parser.add_argument("--train_data_path", type=str)
    parser.add_argument("--train_length", default=400, type=int)

    parser.add_argument("--resume_model_path", default='', type=str)
    parser.add_argument("--checkpoint_every_n_steps", default=20, type=int)
    parser.add_argument("--checkpoint_every_n_epochs", default=0, type=int)

    parser.add_argument("--gradient_accumulation_steps", default=16, type=int)
    parser.add_argument("--gradient_clip_val", default=1., type=float)
    parser.add_argument("--strategy", default='ddp', type=str)
    parser.add_argument("--accelerator", default='gpu', type=str)
    parser.add_argument("--precision", default=16)
    parser.add_argument("--pin_memory", default=False)

    parser.add_argument("--num_device_per_node", default=1, type=int)
    parser.add_argument("--num_nodes", default=2, type=int)
    parser.add_argument("--num_works", default=4, type=int)
    parser.add_argument("--enable_checkpointing", default=True, type=bool)
    parser.add_argument("--per_device_train_batch_size", default=1, type=int)
    parser.add_argument("--per_device_eval_batch_size", default=2, type=int)
    parser.add_argument("--log_every_n_steps", default=1, type=int)
    parser.add_argument("--min_epochs", default=20, type=int)
    parser.add_argument("--max_epochs", default=50, type=int)

    parser.add_argument("--max_steps", default=100000, type=int)
    parser.add_argument("--learning_rate", default=2e-5, type=float)
    parser.add_argument("--max_length", default=512, type=float)

    parser.add_argument("--output_dir", default='./new', type=str)
    parser.add_argument("--cache_dir", default=None, type=str)

    parser.add_argument("--warmup", default=30000,type=int)
    parser.add_argument("--in_category", default=50000,type=int)
    parser.add_argument("--cross_category", default=6000,type=int)

    args = parser.parse_args()

    args.model_name_or_path = model2path[args.model_name_or_path]

    train(args)
