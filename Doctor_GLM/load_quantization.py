from deep_training.data_helper import ModelArguments, TrainingArguments, DataArguments
from deep_training.nlp.models.chatglm import setup_model_profile, ChatGLMConfig
from deep_training.nlp.models.lora import LoraArguments
from transformers import HfArgumentParser
from data_utils import train_info_args, NN_DataHelper
from models import MyTransformer, ChatGLMTokenizer
import torch
import re
from collections import OrderedDict


def load_int(filename: str, q:int=4):
    print("Hi! this loading process will take up ~3 minutes.\n")
    train_info_args['seed'] = None
    parser = HfArgumentParser(
        (ModelArguments, TrainingArguments, DataArguments, LoraArguments))
    model_args, training_args, data_args, _ = parser.parse_dict(
        train_info_args)

    setup_model_profile()

    dataHelper = NN_DataHelper(model_args, training_args, data_args)
    tokenizer: ChatGLMTokenizer
    tokenizer, _, _, _ = dataHelper.load_tokenizer_and_config(
        tokenizer_class_name=ChatGLMTokenizer, config_class_name=ChatGLMConfig)

    config = ChatGLMConfig.from_pretrained('./ckpt/lora')
    config.initializer_weight = False

    lora_args = LoraArguments.from_pretrained('./ckpt/lora')

    assert lora_args.inference_mode == True

    config.initializer_weight = False
    weights_dict = torch.load(filename, map_location='cpu')

    weights_dict_new = OrderedDict()
    for k, v in (weights_dict['module'] if 'module' in weights_dict else weights_dict).items():
        weights_dict_new[re.sub(r'_forward_module\.', '', k)] = v
    pl_model = MyTransformer(
        config=config, model_args=model_args, training_args=training_args)

    model = pl_model.get_glm_model()
    model.quantize(q)

    model.load_state_dict(state_dict=weights_dict_new, strict=True)

    model.half().cuda()
    model = model.eval()
    return tokenizer, model
