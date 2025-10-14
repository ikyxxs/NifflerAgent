import json

import requests

from src.config import APIConfig
from src.tools.strategy_tool import format_json


def extract_thesis(file_name, file_content):
    thesis_list = []
    list_1 = format_json(file_content)
    for ele_1 in list_1:
        list_2 = ele_1['核心投资逻辑']
        for ele_2 in list_2:
            ele_2['来源'] = file_name
            thesis_list.append(ele_2)
    return thesis_list


def similar_thesis(new_thesis, old_thesis_list):
    thesis_list = []
    for old_thesis in old_thesis_list:
        if judge_thesis(new_thesis['核心假设'], old_thesis['核心假设']):
            thesis_list.append(old_thesis)
    return thesis_list


def judge_thesis(text1, text2):
    return ask_gpt(APIConfig.OPENAI_API_KEY, """
以下两段文本，是否是对于同一个主题的假设，不管假设是相同或者对立。只返回是或者否

---
text1 : "%s"
text2 : "%s"
""" % (text1, text2))


def ask_gpt(key, content):
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": 'Bearer ' + key
        }
        data = {
            "model": "THUDM/GLM-Z1-9B-0414",
            "messages": [{"role": "user", "content": content}]
        }
        response = requests.post('https://api.siliconflow.cn/v1/chat/completions',
                                 headers=headers, data=json.dumps(data), timeout=30)
        data = response.json()
        if 'choices' in data:
            resp_text = data['choices'][0]['message']['content']
            index = resp_text.find("</think>")
            if index != -1:
                resp_text = resp_text[index + len("</think>"):].lstrip()
            if '是' in resp_text:
                return True
        return False
    except Exception as e:
        return False


def thesis_json_to_markdown(json_data):
    if isinstance(json_data, str):
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError:
            return ""
    else:
        data = json_data

    # 创建Markdown表格头部
    markdown = "| 核心假设 | 综合判断与数据支撑 | 验证时间窗 | 来源 |\n"
    markdown += "|----------|-------------------|------------|------|\n"

    # 填充表格数据
    for item in data:
        core_assumption = item.get("核心假设", "").replace("|", "\\|")
        judgment = item.get("综合判断与数据支撑", "").replace("|", "\\|")
        time_window = item.get("验证时间窗", "").replace("|", "\\|")
        source = item.get("来源", "").replace("|", "\\|")

        markdown += f"| {core_assumption} | {judgment} | {time_window} | {source} |\n"

    return markdown