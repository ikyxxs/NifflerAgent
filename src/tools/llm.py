import requests
from langchain_openai import ChatOpenAI

from src.config import APIConfig


def get_llm(model='zai-org/GLM-4.6'):
    """获取一个硅基流动的客户端"""
    return ChatOpenAI(api_key=get_key(), model=model, base_url=APIConfig.OPENAI_BASE_URL)


def get_key():
    """获取一个硅基流动的KEY"""
    key_list = ['sk-xxxxxxxxx']

    max_balance = -float('inf')  # 初始化最大余额为负无穷
    max_balance_key = None  # 记录余额最大的key

    for key in key_list:
        try:
            balance = get_balance(key)
        except Exception as e:
            print(f"获取key {key} 的余额失败: {e}")
            continue  # 跳过获取失败的key

        # 若余额大于2，直接返回当前key
        if balance > 2:
            return key

        # 更新最大余额及对应key
        if balance > max_balance:
            max_balance = balance
            max_balance_key = key

    # 所有key的余额都不大于2，返回余额最大的key
    return max_balance_key


def get_balance(api_key) -> float:
    """查询硅基流动账户余额"""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": 'Bearer ' + api_key
        }
        response = requests.get('https://api.siliconflow.cn/v1/user/info', headers=headers, timeout=5)
        return float(response.json()['data']['totalBalance'])
    except Exception as e:
        return 0
