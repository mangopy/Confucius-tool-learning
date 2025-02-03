import random
import logging
from typing import Dict
import torch
import transformers
import sys
sys.path.append('../')
from utils import load_data,preprocess
from torch.utils.data import Dataset
from tqdm import tqdm
from pool import api_pool,task_pool


class SupervisedDataset(Dataset):
    """Dataset for supervised fine-tuning."""
    API_PROMPT_DICT = {
        "prompt_with_api": (
            "Below is an instruction that describes a question and some external API. You should select the appropriate API to complete the  and write a response as the answer. "
            "The format of the API is `[func(type: p) -> r]` where the `func` is the name of the API and the `r` is the result of the API. The `p` is the parameter, and the `type` is the parameter type.\n"
            "When calling the API, the API must be included in [ and ], and the parameter type should be given. You can use the following APIs:\n\n"
            "```\n"
            "{api}\n"
            "```\n\n"
            "Input: {input}\n"
            "Response: "
        ),
        "prompt_without_api": (
            "Below is an instruction that describes a task. The task can be done without external API. Write a response that appropriately completes the request.\n\n"
            "Input: {input}\n\n"
            "Response: "
        ),
    }
    api_pool=api_pool
    task_pool=task_pool

    def __init__(self, data_path,
                 tokenizer: transformers.PreTrainedTokenizer,
                 max_length:int=256,
                 train=True,
                 split=None,
                 num_api=3):
        super(SupervisedDataset, self).__init__()
        logging.warning("Loading data...")
        data = load_data(data_path)
        random.shuffle(data)
        if split==None:
            split=[10000000,0,0]
        list_data_dict=self.warmup_toolset(data[:split[0]])
        list_data_dict+=self.in_toolset(data=data[split[0]:split[0]+split[1]],num_api=num_api)
        list_data_dict += self.cross_toolset(data=data[split[0]+split[1]:],num_api=num_api)
        for line in list_data_dict:
            line['api']='\n'.join(line['api'])

        logging.warning("Formatting inputs...")
        prompt_input, prompt_no_input = self.API_PROMPT_DICT["prompt_with_api"], self.API_PROMPT_DICT["prompt_without_api"]
        self.sources = [
            prompt_input.format_map(example) if example.get("api", "") != "" else prompt_no_input.format_map(example)
            for example in list_data_dict
        ]
        self.targets = [f"{example['output']}{tokenizer.eos_token}" for example in list_data_dict]

        self.task=[line['task'] for line in list_data_dict]
        self.sources=[line.replace('→','->') for line in self.sources]
        self.targets=[line.replace('→','->') for line in self.targets]

        logging.warning("Tokenizing inputs, which may take some time...")
        data_dict = preprocess(self.sources, self.targets, tokenizer,max_length)

        self.input_ids = data_dict["input_ids"]
        self.labels = data_dict["labels"]
        self.sources_ids=data_dict['sources_ids']
        self.train=train

    def warmup_toolset(self,data):
        print('prepare warm up training set...')
        res = [{"api": list(set([e[-1] for e in line['api']])),
                "input": line['question'] ,
                "output": line['_answer'],
                'task':line['task']}
               for line in tqdm(data)]
        return res

    def in_toolset(self,data:list,num_api:int=3):
        print('prepare in category toolset dataset...')
        res=[]
        for line in tqdm(data):
            if line['api']==[]:
                res.append({ "api": [], "input": line['question'], "output": line["_answer"],'task':'no_api'})
                continue
            t1=list(set([e[-1] for e in line['api']]))
            t2=set()
            for i in range(2*num_api):
                idx=random.randint(0,10000000)%len(self.api_pool[line['task']])
                a=self.api_pool[line['task']][idx]
                if a not in t1:
                    t2.add(a)
            t2=list(t2)
            t1.extend(t2[:num_api])
            random.shuffle(t1)
            res.append({
                "api":t1,
                "input":line['question'],
                "output":line["_answer"],
                'task':line['task']
            })
        return res

    def cross_toolset(self,data:list,num_api:int=3):
        print('prepare cross category toolset...')
        res = []
        for line in tqdm(data):
            if line['api']==[]:
                res.append({ "api": [], "input": line['question'], "output": line["_answer"],'task':'no_api'})
                continue
            t1 = list(set([e[-1] for e in line['api']]))
            t2 = set()
            for i in range(2 * num_api):
                task=self.task_pool[random.randint(0, 10000000) % len(self.task_pool)]
                idx = random.randint(0, 10000000) % len(self.api_pool[task])
                a = self.api_pool[task][idx]
                if a not in t1:
                    t2.add(a)
            t2 = list(t2)
            t1.extend(t2[:num_api])
            random.shuffle(t1)
            res.append({
                "api": t1,
                "input": line['question'],
                "output": line["_answer"],
                'task':line['task']
            })
        return res

    def statistics(self):
        aver_input_ids=sum([len(line) for line in self.input_ids])
        aver_sources_ids=sum([len(line) for line in self.sources_ids])
        aver_labels=sum([len(line) for line in self.labels])
        print(f'************ average {aver_input_ids} tokens of input **********')
        print(f'************ average {aver_sources_ids} tokens of source **********')
        print(f'************ average {aver_labels} tokens of label **********')

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, i) -> Dict[str, torch.Tensor]:
        return dict(input_ids=self.input_ids[i], labels=self.labels[i],source_ids=self.sources_ids[i],sources=self.sources[i],targets=self.targets[i],task=self.task[i])


def prepare_inference_data(data,pool):
    for line in data:
        line['prompt'] = pool.get_prompt(line)
    return data


# test
from transformers import AutoTokenizer
# IGNORE_INDEX = -100
# DEFAULT_PAD_TOKEN = "[PAD]"
# DEFAULT_EOS_TOKEN = "</s>"
# DEFAULT_BOS_TOKEN = "</s>"
# DEFAULT_UNK_TOKEN = "</s>"
# tokenizer = AutoTokenizer.from_pretrained("huggingface/llama2-7b-chat-hf")
# special_tokens_dict = dict()
#
# if tokenizer.pad_token is None:
#     special_tokens_dict["pad_token"] = DEFAULT_PAD_TOKEN
# if tokenizer.eos_token is None:
#     special_tokens_dict["eos_token"] = DEFAULT_EOS_TOKEN
# if tokenizer.bos_token is None:
#     special_tokens_dict["bos_token"] = DEFAULT_BOS_TOKEN
# if tokenizer.unk_token is None:
#     special_tokens_dict["unk_token"] = DEFAULT_UNK_TOKEN
#
# num_new_tokens = tokenizer.add_special_tokens(special_tokens_dict)
#
# train_dataset = SupervisedDataset(tokenizer=tokenizer, data_path='dataset path', max_length=1024,
#                                       split=[100,100,30000])

