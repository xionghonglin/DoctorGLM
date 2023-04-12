import enum
from bs4 import BeautifulSoup
import re
from bs4.element import PageElement
import glob
from googlesearch import search
from tqdm import tqdm
import json
from googlesearch import search


def ret_website(query:str):
    keyword = f"site:https://www.msdmanuals.cn/professional {query}"
    website = next(search(keyword, num=1, stop=1, pause=5))
    return website


def is_treatment(tag:PageElement,feature: str):
    return tag.name == 'h2' and tag.has_attr('class') and 'topic__header--section' in tag['class'] and feature in tag.get_text(strip=True)

def preclean(content:str):
    res = re.sub(r'\s+', '', content)
    return res

def text2subsec(content_elem:PageElement):
    head = content_elem.find_all('h3', attrs='topic__header--subsection')
    if len(head) == 0:
        return head
    if '参考文献' in head[-1].text:
        head = head[:-1]
    return head

def subsec2dict(content_elem:PageElement,sec:list):
    info={}
    intro_list = []
    # 如果没有subsection则直接返回字典
    if len(sec)==0:
        primer=content_elem.get_text()
        primer = re.sub(r'\s+', ' ', primer)
        info["开头"] = primer
        return info
    subsection_tag = content_elem.find('section', class_='topic__section GHead')
    if subsection_tag ==None:
        subsection_tag = content_elem.find('section', class_='topic__section HHead')
    for sibling in subsection_tag.previous_siblings:
        if sibling.name is not None:
            # 如果兄弟节点是一个标签，则将其文本内容添加到列表中
            intro_list.append(sibling.get_text().strip())
        else:
            pass
    if len(intro_list)!=0:
        intro = ""
        for elem in list(reversed(intro_list)):
            intro += elem+' '
        intro = re.sub(r'\s+', ' ', intro)
        info["开头"] = intro
    for s in sec:
        key=s.get_text().strip()
        value=s.find_next_sibling('div', class_='topic__content').get_text().strip()
        value=preclean(value)
        info[key]=value
    return info

def parser(soup,feature:str):
    # 查找包含指定关键字的Tag
    treatment_tag=soup.find_all(lambda tag: is_treatment(tag, feature))
    # 检查是否找到了符合条件的标签
    if treatment_tag:
        # 获取紧跟在目标标签后面的div标签
        content_div = treatment_tag[0].find_next_sibling('div', class_='topic__content')
        # 提取div里面的内容
        for span_tag in content_div.find_all('span', {'class': 'tooltip-content'}):
            span_tag.extract()
        heads=text2subsec(content_div)
        content=subsec2dict(content_div,heads)
        return content
    else:
        return None

def file_to_4_attr(filename:str):
    # 症状和体征 & 诊断 & 预后 & 治疗
    info=[]
    features=["症状","诊断","预后","治疗"]
    soup = BeautifulSoup(open(filename,encoding='utf-8').read(), 'html.parser')
    for f in features:
        p_content = parser(soup,f)
        # clean_p = preclean(p_content)
        info.append(p_content)
    return info


if __name__=="__main__":
    # 返回 症状和体征 & 诊断 & 预后 & 治疗 和对应的subsection
    query_link={}
    log_step=100
    disease_info={}
    keys=["症状和体征","诊断", "预后","治疗"]
    query_list=json.load(open('./query_MSD.json'))
    for i,elem in enumerate(tqdm(query_list)):
        url=elem[0]
        query=elem[1]
        info=file_to_4_attr(url)
        elem_info={}
        is_exist=False
        for j in range(len(keys)):
            if info[j] !=None:
                is_exist=True
                elem_info[keys[j]]=info[j]
        if is_exist:
            disease_info[query]=elem_info
            query_link[query]=url
        if (i+1)%log_step==0:
            with open("../disease_info.json",'w',encoding='utf-8') as f:
                json.dump(disease_info,f,indent=4, ensure_ascii=False)
    with open("../disease_info.json",'w',encoding='utf-8') as f:
        json.dump(disease_info,f,indent=4, ensure_ascii=False)
