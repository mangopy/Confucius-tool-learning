import copy
import sys
sys.path.append('../')
import pickle
import multiprocessing
import json
import torch
import os
from tqdm import tqdm
from collections import OrderedDict
from transformers import PreTrainedModel
from pytorch_lightning.utilities.deepspeed import convert_zero_checkpoint_to_fp32_state_dict
import torch.multiprocessing as mp
import transformers
from dataclasses import dataclass, field
from typing import Optional, Dict, Sequence

IGNORE_INDEX = -100
DEFAULT_PAD_TOKEN = "[PAD]"
DEFAULT_EOS_TOKEN = "</s>"
DEFAULT_BOS_TOKEN = "</s>"
DEFAULT_UNK_TOKEN = "</s>"


def preprocess(
        sources: Sequence[str],
        targets: Sequence[str],
        tokenizer: transformers.PreTrainedTokenizer,
        max_length: int = 512,
        IGNORE_INDEX=-100
) -> Dict:
    """Preprocess the data by tokenizing."""
    examples = [s + t for s, t in zip(sources, targets)]
    examples_tokenized, sources_tokenized = [_tokenize_fn(strings, tokenizer, max_length=max_length) for strings in (examples, sources)]
    input_ids = examples_tokenized["input_ids"]
    labels = copy.deepcopy(input_ids)
    for label, source_len in zip(labels, sources_tokenized["input_ids_lens"]):
        label[:source_len] = IGNORE_INDEX
    return dict(input_ids=input_ids, labels=labels, sources_ids=sources_tokenized['input_ids'])


def _tokenize_fn(strings: Sequence[str], tokenizer: transformers.PreTrainedTokenizer, max_length: int = 512) -> Dict:
    """Tokenize a list of strings."""
    tokenized_list = [
        tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            max_length=max_length,
            truncation=True,
        )
        for text in tqdm(strings)
    ]

    input_ids = labels = [tokenized.input_ids[0] for tokenized in tokenized_list]
    input_ids_lens = labels_lens = [
        tokenized.input_ids.ne(tokenizer.pad_token_id).sum().item() for tokenized in tokenized_list
    ]
    return dict(input_ids=input_ids, labels=labels, input_ids_lens=input_ids_lens, labels_lens=labels_lens, )


@dataclass
class DataCollatorForTuning(object):
    """Collate examples for fine-tuning."""

    def __init__(self, tokenizer: transformers.PreTrainedTokenizer, train: bool = True):
        self.tokenizer = tokenizer
        self.train = train

    def __call__(self, instances: Sequence[Dict]) -> Dict[str, torch.Tensor]:
        input_ids, label_ids, source_ids, sources, targets = tuple([instance[key] for instance in instances] for key in ("input_ids", "labels", "source_ids", "sources", 'targets'))
        input_ids = torch.nn.utils.rnn.pad_sequence(
            input_ids, batch_first=True, padding_value=self.tokenizer.pad_token_id
        )
        source_ids = torch.nn.utils.rnn.pad_sequence(
            source_ids, batch_first=True, padding_value=self.tokenizer.pad_token_id
        )
        label_ids = torch.nn.utils.rnn.pad_sequence(label_ids, batch_first=True, padding_value=IGNORE_INDEX)
        if self.train:
            return dict(
                input_ids=input_ids,
                labels=label_ids,
                attention_mask=input_ids.ne(self.tokenizer.pad_token_id),
            )
        else:
            return dict(
                input_ids=input_ids,
                labels=label_ids,
                attention_mask=input_ids.ne(self.tokenizer.pad_token_id),
                source_ids=source_ids,
                source_ids_mask=source_ids.ne(self.tokenizer.pad_token_id),
                sources=sources,
                targets=targets,
            )


def smart_tokenizer_and_embedding_resize(
        special_tokens_dict: Dict,
        tokenizer: transformers.PreTrainedTokenizer,
        model: transformers.PreTrainedModel,
):
    """Resize tokenizer and embedding.

    Note: This is the unoptimized version that may make your embedding size not be divisible by 64.
    """
    num_new_tokens = tokenizer.add_special_tokens(special_tokens_dict)
    model.resize_token_embeddings(len(tokenizer))

    if num_new_tokens > 0:
        input_embeddings = model.get_input_embeddings().weight.data
        output_embeddings = model.get_output_embeddings().weight.data

        input_embeddings_avg = input_embeddings[:-num_new_tokens].mean(dim=0, keepdim=True)
        output_embeddings_avg = output_embeddings[:-num_new_tokens].mean(dim=0, keepdim=True)

        input_embeddings[-num_new_tokens:] = input_embeddings_avg
        output_embeddings[-num_new_tokens:] = output_embeddings_avg


def make_model_tokenizer(model_name_or_path,
                         model_max_length=512,
                         cache_dir=None,
                         load_in_8bit=False,
                         train=True):
    model = transformers.AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        cache_dir=cache_dir,
        load_in_8bit=load_in_8bit,
        device_map="auto" if train == False else None,
        torch_dtype=torch.float16
    )
    tokenizer = transformers.AutoTokenizer.from_pretrained(
        model_name_or_path,
        model_max_length=model_max_length,
        padding_side="right" if train else 'left',
        use_fast=False,
    )
    # tokenizer.pad_token = tokenizer.eos_token
    tokenizer.add_special_tokens({'pad_token': '[PAD]'})

    special_tokens_dict = dict()
    if tokenizer.pad_token is None:
        special_tokens_dict["pad_token"] = DEFAULT_PAD_TOKEN
    if tokenizer.eos_token is None:
        special_tokens_dict["eos_token"] = DEFAULT_EOS_TOKEN
    if tokenizer.bos_token is None:
        special_tokens_dict["bos_token"] = DEFAULT_BOS_TOKEN
    if tokenizer.unk_token is None:
        special_tokens_dict["unk_token"] = DEFAULT_UNK_TOKEN

    smart_tokenizer_and_embedding_resize(
        special_tokens_dict=special_tokens_dict,
        tokenizer=tokenizer,
        model=model,
    )
    return model, tokenizer


def load_pl_ds_checkpoint(model: PreTrainedModel,
                          save_ckpt_path: str,
                          huggingface_ckpt_path: str,
                          tag='checkpoint'
                          ):
    """
    :param model: transformers.LlamaForCausalLM or something else
    :param save_path: the path for saving the deepseed style weight with pytorch-lightning library + deepepeed
    :param output_path: the save path for the huggingface style weight
    :return:
    """
    if not os.path.exists(huggingface_ckpt_path):
        os.makedirs(huggingface_ckpt_path)
    huggingface_ckpt_path = os.path.join(huggingface_ckpt_path, 'pytorch_model.bin')
    # convert the deepspeed zero2/3 format to torch.load/load_state_dict format
    if os.path.exists(huggingface_ckpt_path) == False:
        convert_zero_checkpoint_to_fp32_state_dict(save_ckpt_path, huggingface_ckpt_path, tag=tag)
    ckpt = torch.load(huggingface_ckpt_path)
    state = OrderedDict({k[6:]: v for k, v in ckpt['state_dict'].items()})
    if model == None:
        return None
    else:
        model.load_state_dict(state_dict=state)
        return model


def load_jsonl(ids, data):
    data = [json.loads(line) for line in tqdm(data)]
    return ids, data


def multi_load_jsonl(filename, num_processes=10):
    """

    :param filename: the jsonl file with big size
    :param num_processes:
    :return:
    """
    with open(filename, 'r', encoding='utf-8') as f:
        data = [line.strip() for line in f]
        if len(data) <= 20000:
            _, data = load_jsonl(0, data)
            return data

    length = len(data) // num_processes + 1
    pool = multiprocessing.Pool(processes=num_processes)
    collects = []
    for ids in range(num_processes):
        collect = data[ids * length:(ids + 1) * length]
        collects.append(pool.apply_async(load_jsonl, (ids, collect)))

    pool.close()
    pool.join()
    results = []
    for i, result in enumerate(collects):
        ids, res = result.get()
        assert ids == i
        results.extend(res)
    return results


def write_file(data, filename, indent=4):
    if filename.endswith('.json'):
        json.dump(data, open(filename, 'w'), indent=indent)
    elif filename.endswith('.jsonl'):
        with open(filename, 'w') as f:
            for line in data:
                f.write(json.dumps(line) + '\n')
    elif filename.endswith('.txt'):
        with open(filename, 'w') as f:
            for line in data:
                f.write(str(line) + '\n')
        raise "no suitable function to write data"

def load_data(filename, num_processes=10, folder=False, custom_load='json'):
    if filename.endswith('.jsonl'):
        return multi_load_jsonl(filename, num_processes)
    elif filename.endswith('.json'):
        return json.load(open(filename, 'r'))
    elif filename.endswith('.pkl'):
        return pickle.load(filename)
    elif filename.endswith('.txt'):
        with open(filename, 'r') as f:
            data = [line.strip() for line in f]
            return data
    elif folder == True and custom_load != None:
        data = []
        for line in os.listdir(filename):
            if line.endswith(custom_load):
                data.extend(load_data(line))
        return data
    else:
        raise "no suitable function to load data"


def multi_process_cuda(data_path, ranks, func, kwargs):
    """

    :param data_path: data path 
    :param ranks: gpu device id 
    :param func: the function for batch 
    :param kwargs: the 'dict', indicating the parameter to pass into the 'func'
    :return:
    """
    cuda_pool = mp.Pool(processes=len(ranks))
    data = load_data(data_path)
    length = len(data) // len(ranks) + 1
    collects = []
    for ids, rank in enumerate(ranks):
        collect = data[ids * length:(ids + 1) * length]
        collects.append(cuda_pool.apply_async(func, (collect, rank, kwargs)))
    cuda_pool.close()
    cuda_pool.join()
    results = []
    for rank, result in zip(ranks, collects):
        r, res = result.get()
        assert r == rank
        results.extend(res)
    return results


def multi_process_cuda_data(data, ranks, func, kwargs):
    """

    :param data: the data
    :param ranks: gpu device ids
    :param func:
    :param kwargs:
    :return:
    """
    torch.multiprocessing.set_start_method('spawn', force=True)
    cuda_pool = mp.Pool(processes=len(ranks))
    length = len(data) // len(ranks) + 1
    collects = []
    for ids, rank in enumerate(ranks):
        collect = data[ids * length:(ids + 1) * length]
        collects.append(cuda_pool.apply_async(func, (collect, rank, kwargs)))
    cuda_pool.close()
    cuda_pool.join()
    results = []
    for rank, result in zip(ranks, collects):
        r, res = result.get()
        assert r == rank
        results.extend(res)
    return results
