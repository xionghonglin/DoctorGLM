from transformers import AutoTokenizer, AutoModel
from langchain.text_splitter import RecursiveCharacterTextSplitter, TextSplitter
from langchain.document_loaders import TextLoader   
import os
import json
# loader = TextLoader("内科学.txt", encoding='utf-8')
# doc = loader.load()[0]
# QA_generation(doc.page_content)

model_path = '6b/'

tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
model = AutoModel.from_pretrained(model_path, trust_remote_code=True).half().cuda()
model = model.eval()


idx = 0
data_path = 'zh_sentence/'
qa_dict = {}
for file_name in os.listdir(data_path):
    file_path = data_path + file_name
    print(file_name)
    loader = TextLoader(file_path, encoding='utf-8')
    doc = loader.load()[0]
    inputs = {"text": doc.page_content}
    text_splitter = TextSplitter
    docs = text_splitter.create_documents(RecursiveCharacterTextSplitter(chunk_size = 2000, chunk_overlap=200), [inputs["text"]])
    # print([{"text": d.page_content} for d in docs])
    for d in docs:
        idx += 1
        text = d.page_content
        
        templ = f"""你是一个聪明的助理。
        
        给你一段医学相关的文本，你必须依据文本想出一个问题和一个对应的答案。
        
        你想出的问题可以被用来测试医生的专业能力。
        
        你想出的问题和答案必须和所给文本相关。
        
        当你想出问题和答案后，你必须用以下格式回复：

        ```
        [
            "问题": "$你想出的问题放在这",
            "答案": "$你想出的答案放在这"
        ]
        ```

        所有在 ``` 中间的内容就是你要回答的格式。

        请想出一个问题与一个答案，用以上指定的列表回复，对于以下文本：
        ----------------
        {text}"""
        
        response, history = model.chat(tokenizer, templ, history=[],max_length=2048)
        
        while_count = 0
        if_good = True
        while ('以下哪' in response) or ('语言模型' in response) or ('文本' in response) or ('以下是' in response):
            response, history = model.chat(tokenizer, templ, history=[],max_length=2048)
            while_count += 1
            if while_count > 10:
                if_good = False
                break
        print(response)
        
        try:
            if if_good:
                question = response.split('答案：')[0][3:]
                answer = response.split('答案：')[1]
                qa = {}
                qa['问题'] = question
                qa['答案'] = answer
                qa_dict[idx] = qa
            else:
                pass
        except:
            pass
        json.dump(qa_dict, open('qa_dict.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)