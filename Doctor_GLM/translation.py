from transformers import pipeline
import json
from tqdm import tqdm

def dict2str(elem: dict):
    p="\"input\": "+"\""+elem['input']+"\"\n"+"\"output\":"+"\""+elem['output']+"\""
    return p

def data(info_todo):
    for i,elem in enumerate(tqdm(info_todo)):
        yield dict2str(elem)

def str2dict(conver: str):
    if len(conver.split('"'))!=9:
        return None
    # assert len(conver.split('"'))==9
    # 提取输入和输出文本内容
    input_str = conver.split('"')[3]
    output_str = conver.split('"')[7]
    # 创建字典对象
    return {'instruction':"如果您是医生，请根据患者的描述回答医学问题。",'input': input_str, 'output': output_str}

if __name__=="__main__":
    # load our fine-tuned translation model
    generator = pipeline(model="zhaozh/medical_chat-en-zh",device=0,max_length=500,truncation=True)
    info=json.load(open("./GenMedGPT-5k.json"))
    res=[]
    step=20
    for i, output in enumerate(generator(data(info))):
        message=output[0]['translation_text']
        message=message.replace("“", "\"")
        info_dict=str2dict(message)
        # Here we simply skip the failure example (only 1%)
        if info_dict == None:
            print(f"fail {message}")
            continue
        res.append(info_dict)
        if (i + 1) % step == 0:
            with open('./GenMedGPT-5k-ch.json', 'w', encoding='utf-8') as file:
                json.dump(res, file, indent=4, ensure_ascii=False)

    with open('./GenMedGPT-5k-ch.json', 'w', encoding='utf-8') as file:
        json.dump(res, file, indent=4, ensure_ascii=False)

