import json
import glob
from text2vec import SentenceModel
import re
from bs4 import BeautifulSoup
import numpy as np
import json
from transformers import AutoTokenizer, AutoModel
from tqdm import tqdm
import os
import pickle as pkl


emb_d = pkl.load(open('disease_sent_emb.pkl','rb'))
disease_info_dict = json.load(open('disease_info.json'))


def get_disease_info(patient_discription:str, model, tokenizer):
    input = '这是一个病人的描述：\n' + patient_discription + '\n' + '请用一个专业医学名词来代替上述描述，必须是疾病名称，且不超过六个字，回复格式仅包含该名词，不超过六个字，不要回复超过六个字，仅用中文。'
    disease_name, _ = model.chat(tokenizer, input, history=[], max_length=200)
    m = SentenceModel()
    d_emb = m.encode(disease_name)
    largest = 0
    temp_t = ''
    for t, emb in emb_d.items():
        sim = d_emb @ emb
        if sim > largest:
            temp_t = t
            largest = sim

    if largest < 250:
        return None
    else:
        return disease_info_dict[temp_t]
    