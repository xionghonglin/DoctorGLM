from bs4 import BeautifulSoup
import re
from bs4.element import PageElement

def preclean(content:str):
    res = re.sub(r'\s+', ' ', content)
    res=res.replace("阅读更多","")
    res=res.replace(" ","\n").split('\n')
    res = [re.sub(r'\s+', ' ',x) for x in res if len(re.sub(r'\s+', ' ',x)) >= 3]
    res= [item for item in res if re.search('[\u4e00-\u9fa5]', item)]
    new_list = []
    for item in res:
        # if ('（' in item and '）' not in item) or ('）' in item and '（' not in item):
        #     continue
        if item not in new_list:
            new_list.append(item)
    clean_res=' '.join(new_list)
    return clean_res

def text2subsec(content_elem:PageElement):
    head = content_elem.find_all('h3', attrs='topic__header--subsection')
    # head = content_elem.find_next_siblings('h3', attrs='topic__header--subsection')
    # head=content_elem.find_all_next('h3', attrs='topic__header--subsection')
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
        info["开头"] = preclean(content_elem.get_text())
        return info
    subsection_tag = content_elem.find('section', class_='topic__section GHead')
    for sibling in subsection_tag.previous_siblings:
        if sibling.name is not None:
        # 如果兄弟节点是一个标签，则将其文本内容添加到列表中
        #     intro_list.append(rm_link(sibling).strip())
            intro_list.append(sibling.get_text().strip())
            intro = ""
            for elem in list(reversed(intro_list)):
                intro += elem
            info["开头"] = preclean(intro)
        else:
        # 如果兄弟节点是一个字符串，则直接将其添加到列表中
            pass
            # intro_list.append(sibling.get_text().strip())
            # intro_list.append(rm_link(sibling).strip())
    # intro=""
    # for elem in list(reversed(intro_list)):
    #     intro+=elem
    # info["开头"]=preclean(intro)
    for s in sec:
        # key = rm_link(s).strip()
        key=s.get_text().strip()
        # value = rm_link(s.find_next_sibling('div', class_='topic__content')).strip()
        value=s.find_next_sibling('div', class_='topic__content').get_text().strip()
        value=preclean(value)
        info[key]=value
    return info

def parser(soup,feature:str):
    # 查找data-originaltitle="治疗"的标签
    treatment_tag = soup.find_all(attrs={"data-originaltitle": feature})
    # 检查是否找到了符合条件的标签
    if treatment_tag:
    # 获取紧跟在目标标签后面的div标签
        content_div = treatment_tag[0].find_next_sibling('div', class_='topic__content')
    # 提取div里面的内容
        heads=text2subsec(content_div)
        content=subsec2dict(content_div,heads)
        return content
    else:
        return None

def file_to_4_attr(filename:str):
    # 症状和体征 & 诊断 & 预后 & 治疗
    info=[]
    # features = ["症状和体征", "治疗"]
    features=["症状和体征","诊断","预后","治疗"]
    soup = BeautifulSoup(open(filename,encoding='utf-8').read(), 'html.parser')
    for f in features:
        p_content = parser(soup,f)
        # clean_p = preclean(p_content)
        info.append(p_content)
    return info


if __name__=="__main__":
    # 返回 症状和体征 & 诊断 & 预后 & 治疗 和对应的subsection
    ret=file_to_4_attr(filename='{6DE49BCA-DE4B-4666-B0A2-49FC9C8F357A}.html')
print("hold")
