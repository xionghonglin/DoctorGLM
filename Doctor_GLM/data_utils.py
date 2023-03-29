# @Time    : 2023/1/22 16:22
# @Author  : tk
# @FileName: data_utils.py


import copy
import json
import os
import random
import typing
from enum import Enum

import numpy as np
import torch
from deep_training.data_helper import DataHelper, ModelArguments, TrainingArguments, DataArguments
from deep_training.nlp.models.chatglm import ChatGLMConfig
from deep_training.nlp.models.lora import LoraArguments
from deep_training.utils.func import is_chinese_char
from fastdatasets.record import load_dataset as Loader, RECORD, WriterObject, gfile
from tqdm import tqdm
from transformers import HfArgumentParser
from tokenization_chatglm import ChatGLMTokenizer

train_info_args = {
    'devices': 1,
    'data_backend': 'record',
    'model_type': 'chatglm',
    # 预训练模型路径 , 从0训练，则置空
    'model_name_or_path': "THUDM/chatglm-6b",
    'config_name': './config/config.json',
    'tokenizer_name': "THUDM/chatglm-6b",

    'convert_onnx': False, # 转换onnx模型
    'do_train': True,
    'train_file':  [ './andriatria.json'],
    'max_epochs': 20,
    'max_steps': -1,
    'optimizer': 'lion', # one of adamw,adam,lamb,lion
    'train_batch_size': 1,
    'eval_batch_size': 1,
    'test_batch_size': 1,
    'learning_rate': 2e-5,  #
    'adam_epsilon': 1e-8,
    'gradient_accumulation_steps': 1,
    'max_grad_norm': 1.0,
    'weight_decay': 0,
    'warmup_steps': 0,
    'output_dir': './output',
    'max_seq_length': 512,
    'max_target_length': 100,  # 预测最大长度
    'use_fast_tokenizer': False,
    'do_lower_case': False,

    ##############  lora模块
    'with_lora': True,  # 是否启用lora模块
    'inference_mode': False, # 推理模型, 不需要手动设置
    'r': 8,
    'target_modules': ['query_key_value'],
    'target_dtype': '16',
    'lora_alpha': 32,
    # 'enable_lora': [True],
    'enable_lora': None,
    'lora_dropout': 0.1,
    'bias': 'none',  # Bias type for Lora. Can be 'none', 'all' or 'lora_only'"
}




class NN_DataHelper(DataHelper):
    index = 1


    def on_data_ready(self):
        self.index = -1


    # 切分词
    def on_data_process(self, data: typing.Any, mode: str):
        self.index += 1
        prompt = data[0]
        answer = data[1]

        tokenizer: ChatGLMTokenizer
        max_seq_length = self.max_seq_length_dict[mode]
        tokenizer = self.tokenizer

        if not hasattr(self, 'sptoken'):
            self.sptoken = tokenizer.encode(text="")[-2:]

        ds = []
        a_ids = tokenizer.encode(text=prompt, add_special_tokens=False)
        b_ids = tokenizer.encode(text=answer, add_special_tokens=False)

        input_ids_qa = a_ids + self.sptoken + b_ids + [tokenizer.eos_token_id] * 2
        q_length = input_ids_qa.index(self.sptoken[-1])
        pos = 0
        while pos < len(input_ids_qa):
            if self.sptoken[0] in input_ids_qa[pos:max_seq_length] and self.sptoken[1] in input_ids_qa[pos:max_seq_length]:
                input_ids = input_ids_qa[pos:max_seq_length]
                pos += max_seq_length
            elif self.sptoken[0] in input_ids_qa[pos:max_seq_length]:
                input_ids = input_ids_qa[pos:max_seq_length -1] + [self.sptoken[-1]]
                pos += max_seq_length - 1
            else:
                input_ids = self.sptoken + input_ids_qa[pos:max_seq_length -2] if pos > q_length else input_ids_qa[pos:max_seq_length -2] +self.sptoken
                pos += max_seq_length - 2


            seq_length = input_ids.index(self.sptoken[-1])
            mask_position = seq_length - 1
            position_ids = list(range(seq_length)) + [mask_position] * (max_seq_length - seq_length)
            block_position_ids = [0] * seq_length + list(range(1,max_seq_length - seq_length + 1))

            attention_mask = np.ones((1, max_seq_length,max_seq_length))
            attention_mask = np.tril(attention_mask)
            attention_mask[..., :seq_length] = 1
            attention_mask = (attention_mask < 0.5)
            labels = [-100] * seq_length + input_ids[mask_position+1:]

            seqlen = np.asarray(len(input_ids), dtype=np.int32)
            pad_len = max_seq_length - seqlen
            input_ids = np.asarray(input_ids, dtype=np.int32)
            attention_mask = np.asarray(attention_mask, dtype=np.int32)
            position_ids = np.asarray(position_ids, dtype=np.int32)
            block_position_ids = np.asarray(block_position_ids, dtype=np.int32)

            if pad_len:
                pad_val = tokenizer.pad_token_id
                input_ids = np.pad(input_ids, (0, pad_len), 'constant', constant_values=(pad_val, pad_val))
                labels = np.pad(labels, (0, pad_len), 'constant', constant_values=(-100, -100))

            d = {
                'input_ids': input_ids,
                "attention_mask": attention_mask,
                "position_ids": np.stack([position_ids,block_position_ids],axis=0),
                'labels': labels,
                'seqlen': seqlen
            }
            ds.append(d)

        if not ds:
            return None

        if self.index < 3:
            print(ds[0])
        return ds


    # 读取文件
    def on_get_corpus(self, files: typing.List, mode: str):
        D = []
        for file in files:
            with open(file, mode='r', encoding='utf-8', newline='\n') as f:
                lines = f.readlines()

            for line_id, line in enumerate(lines):
                jd = json.loads(line)
                if not jd:
                    continue
                paragraph = jd['paragraph']
                if line_id < 10:
                    print(paragraph)
                paragraph = [(preprocess(session['q']),preprocess('\n'.join(session['a']))) for session in paragraph]
                for sid,(q,a) in enumerate(paragraph):
                    if sid == 0:
                        D.append((q, a))
                    else:
                        prompt_text = ''
                        for j in range(sid + 1):
                            if j == sid:
                                prompt_text += "[Round {}]\n问：{}\n答：".format(sid, paragraph[j][0])
                            else:
                                prompt_text += "[Round {}]\n问：{}\n答：{}".format(sid, paragraph[j][0], paragraph[j][1])
                        D.append((prompt_text,a))
        return D

    def collate_fn(self,batch):
        if not hasattr(self,'sptoken'):
            self.sptoken = self.tokenizer.encode(text="")[-2:]

        o = {}
        for i, b in enumerate(batch):
            if i == 0:
                for k in b:
                    o[k] = [torch.tensor(b[k])]
            else:
                for k in b:
                    o[k].append(torch.tensor(b[k]))
        for k in o:
            o[k] = torch.stack(o[k])

        seqlens = o.pop('seqlen')
        max_len = torch.max(seqlens)
        o['input_ids'] = o['input_ids'][:, :max_len].long()
        o['attention_mask'] = o['attention_mask'][:,:, :max_len,:max_len].bool()
        o['position_ids'] = o['position_ids'][:,:, :max_len].long()
        o['labels'] = o['labels'][:, :max_len].long()
        return o



