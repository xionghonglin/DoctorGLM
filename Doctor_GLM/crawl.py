from bs4 import BeautifulSoup
import re
from bs4.element import PageElement


def is_treatment(tag:PageElement,feature: str):
    return tag.name == 'h2' and tag.has_attr('class') and 'topic__header--section' in tag['class'] and feature in tag.get_text(strip=True)
    # return tag.name == 'h2' and tag.has_attr('class') and 'topic__header--section' in tag['class'] and tag.get_text(strip=True) == feature

def preclean(content:str):
    res = re.sub(r'\s+', '', content)
    return res

def text2subsec(content_elem:PageElement):
    head = content_elem.find_all('h3', attrs='topic__header--subsection')
    # head = content_elem.find_next_siblings('h3', attrs='topic__header--subsection')
    # head=content_elem.find_all_next('section', class_='topic__section GHead')
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
        # 是否过滤href的内容
        # info["开头"] = preclean(rm_link(content_elem))
        primer=content_elem.get_text()
        primer = re.sub(r'\s+', ' ', primer)
        info["开头"] = primer
        return info
    subsection_tag = content_elem.find('section', class_='topic__section GHead')
    for sibling in subsection_tag.previous_siblings:
        if sibling.name is not None:
            # 如果兄弟节点是一个标签，则将其文本内容添加到列表中
            intro_list.append(sibling.get_text().strip())
            # intro = ""
            # for elem in list(reversed(intro_list)):
            #     intro += elem+' '
            # info["开头"] = intro
        else:
        # 如果兄弟节点是一个字符串，则直接将其添加到列表中
            pass
            # intro_list.append(sibling.get_text().strip())
            # intro_list.append(rm_link(sibling).strip())
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
    # 查找data-originaltitle="治疗"的标签
    treatment_tag=soup.find_all(lambda tag: is_treatment(tag, feature))
    # treatment_tag = soup.find_all(attrs={"data-originaltitle": feature})
    # # head = soup.find_all('h2', attrs='topic__header--section')
    # # treatment_tag=soup.find('section', class_='topic__section FHead')
    # if not treatment_tag:
    #     # head = soup.find_all('h2', attrs='topic__header--section')
    #     treatment_tag=soup.find_all(lambda tag: is_treatment(tag, feature))
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
    # 该features出于爬虫目的设计
    # 保存为字典时请记录为["症状和体征","诊断","预后","治疗"]
    features=["症状","诊断","预后","治疗"]
    soup = BeautifulSoup(open(filename,encoding='utf-8').read(), 'html.parser')
    for f in features:
        p_content = parser(soup,f)
        # clean_p = preclean(p_content)
        info.append(p_content)
    return info


if __name__=="__main__":
    # 返回 症状和体征 & 诊断 & 预后 & 治疗 和对应的subsection
    # 二尖瓣狭窄： ../MSD/{D2F11D5E-75DD-43D9-9932-5EC561FCCC2E}.html
    # 支原体感染：../MSD/{2B5089C6-BFCF-4649-BBC9-6A0D8A9DB525}.html
    # 高血压：../MSD/{6DE49BCA-DE4B-4666-B0A2-49FC9C8F357A}.html
    # 肛门直肠痿：../ MSD/{D7E4E1ED-E2C8-4418-A337-915596F5A756}.html
    ret=file_to_4_attr(filename='../MSD/{D2F11D5E-75DD-43D9-9932-5EC561FCCC2E}.html')
print("hold")
