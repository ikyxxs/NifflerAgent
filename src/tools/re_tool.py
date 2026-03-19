import re


def extract_number(value_str):
    """
    从包含中文或符号的字符串中提取第一个浮点数。
    例如: "10%" -> 10.0, "约为1.2左右" -> 1.2
    """
    if isinstance(value_str, (int, float)):
        return float(value_str)

    # 正则表达式逻辑：
    # [-+]? : 可选的正负号
    # \d*\.\d+ : 浮点数 (如 .5, 1.2)
    # | : 或
    # \d+ : 整数 (如 10)
    pattern = r"[-+]?(?:\d*\.\d+|\d+)"
    match = re.search(pattern, str(value_str))

    if match:
        return float(match.group())
    return None
