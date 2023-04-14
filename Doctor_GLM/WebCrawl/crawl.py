import enum
from tkinter.messagebox import NO
from bs4 import BeautifulSoup
import re
from bs4.element import PageElement
import requests
from googlesearch import search
from tqdm import tqdm
import json
import os

os.environ["http_proxy"]="http://127.0.0.1.1:7890"
os.environ["https_proxy"]="http://127.0.0.1:7890"

def ret_website(query:str):
    keyword = f"site:https://www.msdmanuals.cn/professional {query}"
    website = next(search(keyword, num=1, stop=1, pause=5))
    return website


def is_treatment_feature(tag:PageElement,feature: str):
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
        info["概述"] = primer
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
        info["概述"] = intro
    for s in sec:
        key=s.get_text().strip()
        value=s.find_next_sibling('div', class_='topic__content').get_text().strip()
        value=preclean(value)
        info[key]=value
    return info

def parser(soup,feature:str):
    # 查找包含指定关键字的Tag
    treatment_tag=soup.find_all(lambda tag: is_treatment_feature(tag, feature))
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

def parser_abs(soup):

    # 获取class为topic__explanation的标记元素
    start = soup.find('div', {'class': 'topic__explanation'})

    if start==None:
        return None

    # 获取class为topic__header--section的标记元素
    # end = soup.find('div', {'class': 'topic__header--section'})
    end = soup.find_all('h2', attrs='topic__header--section')
    if len(end)==0:
        return None
    else:
        end=end[0]

    proc=reversed(end.find_all_previous('div',{'class':"para"}))
    # 提取div里面的内容
    

    # 获取两个标记之间的文本
    text = start.text
    for tag in proc:
        for span_tag in tag.find_all('span', {'class': 'tooltip-content'}):
            span_tag.extract()
        text+=tag.text
    text=text.replace(" ","").replace("\n","")
        
    return text


def file_to_specific_attrs(features: list,filename:str,online: bool=False):
    info={}
    if online:
        soup = BeautifulSoup(requests.get(filename).content, 'html.parser')
    else:
        soup = BeautifulSoup(open(filename,encoding='utf-8').read(), 'html.parser')

    p_content=parser_abs(soup)
    # p_content=soup.find_all('div', {'class':'topic__explanation'})[0].text
    if p_content==None:
        pass
    else:
        info['概述']=p_content.replace("\n","").replace(" ","")
    # p_content=soup.find_all('div', {'class':'topic__explanation'})
    for f in features:
        p_content = parser(soup,f)
        if p_content !=None:
            info[f]=p_content
        # info.append(p_content)
    return info

def crawl_specific_attrs():
    # 返回 症状和体征 & 诊断 & 预后 & 治疗 和对应的subsection
    query_link={}
    log_step=100
    disease_info={}
    keys=["病因","预防","分类","症状和体征","诊断", "预后","治疗"]
    query_list=json.load(open('./Doctor_GLM/WebCrawl/query_MSD.json'))
    for i,elem in enumerate(tqdm(query_list)):
        # url=os.path.join("../",elem[0])
        url=elem[0]
        query=elem[1]
        info=file_to_specific_attrs(keys,url)
        if len(info)!=0:
            disease_info[query]=info
            query_link[query]=url
        if (i+1)%log_step==0:
            with open("../disease_info_features_v2.json",'w',encoding='utf-8') as f:
                json.dump(disease_info,f,indent=4, ensure_ascii=False)
    with open("../disease_info_features_v2.json",'w',encoding='utf-8') as f:
        json.dump(disease_info,f,indent=4, ensure_ascii=False)



if __name__=="__main__":
    crawl_specific_attrs()
    # target_site=ret_website("肺水肿")
    # target_site=ret_website("肠套叠")
    # keys=["病因","预防","分类","症状和体征","诊断", "预后","治疗"]
    # info=file_to_specific_attrs(keys, target_site,online=True)
    # print("hold")
    
