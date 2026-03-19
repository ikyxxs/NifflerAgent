import json
import re

from src.logger_config import logger
from src.tools.llm_tool import ask_llm


def format_json(content):
    """
    将内容解析为JSON对象
    优先尝试直接解析，失败后使用LLM修复
    """
    content = remove_json_markup(content)
    content = escape_newlines_in_json_strings(content)
    
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        logger.warning(f"JSON解析失败，尝试修复: {content[:200]}...")
        fixed_content = fix_json(content)
        logger.info(f"LLM修复后的JSON: {fixed_content[:200]}...")
        return json.loads(fixed_content)


def remove_json_markup(content):
    """
    移除JSON字符串中的markdown标记和多余文本
    支持 ```json、``` 等代码块标记
    支持数组和对象两种JSON格式
    """
    if not content:
        return content
    
    content = content.strip()
    
    pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    matches = re.findall(pattern, content)
    
    if matches:
        return matches[0].strip()
    
    if '```' in content:
        content = re.sub(r'```\s*', '', content)
    
    first_array = content.find('[')
    first_object = content.find('{')
    
    if first_array == -1 and first_object == -1:
        return content
    
    if first_array != -1 and (first_object == -1 or first_array < first_object):
        start = first_array
        end = content.rfind(']') + 1
    else:
        start = first_object
        end = content.rfind('}') + 1
    
    if start != -1 and end > start:
        return content[start:end]
    
    return content


def escape_newlines_in_json_strings(content):
    """
    转义JSON字符串值中的未转义换行符
    处理大模型生成的JSON中字符串内包含真实换行符的问题
    """
    if not content:
        return content
    
    result = []
    i = 0
    in_string = False
    escape_next = False
    
    while i < len(content):
        char = content[i]
        
        if escape_next:
            result.append(char)
            escape_next = False
            i += 1
            continue
        
        if char == '\\' and in_string:
            result.append(char)
            escape_next = True
            i += 1
            continue
        
        if char == '"':
            in_string = not in_string
            result.append(char)
            i += 1
            continue
        
        if in_string and char in '\n\r\t':
            if char == '\n':
                result.append('\\n')
            elif char == '\r':
                result.append('\\r')
            elif char == '\t':
                result.append('\\t')
            i += 1
            continue
        
        result.append(char)
        i += 1
    
    return ''.join(result)


def fix_json(content):
    try:
        content = ask_llm(
            f"""
请严格校验并修复以下JSON的格式错误（如引号、括号、逗号、换行等），确保：
1.  不修改任何原始数据内容
2.  输出标准格式的JSON字符串
3.  除最终JSON外不包含任何额外文本、说明或标记
---
{content}
            """)
        content = remove_json_markup(content)
    except Exception as e:
        pass
    return content


def strategy_json_to_markdown(json_data):
    """投资策略JSON转Markdown"""
    # 如果输入是字符串，则解析为JSON
    if isinstance(json_data, str):
        try:
            data = format_json(json_data)
        except Exception as e:
            logger.error(f'strategy_json_to_markdown, format json error, {e}, json_data: \n{json_data}')
            return ''
    else:
        data = json_data

    markdown_output = "# 投资策略分析报告\n\n"

    # 遍历每个策略
    for i, strategy in enumerate(data, 1):
        if "可执行策略工具箱" not in strategy:
            continue

        markdown_output += f"## 策略 {i}\n\n"

        # 处理核心投资逻辑
        if "核心投资逻辑" in strategy:
            markdown_output += "### 核心投资逻辑\n\n"
            for index, logic in enumerate(strategy["核心投资逻辑"], start=1):
                assumption = logic.get("核心假设", "").replace("\n", " ")
                judgment = logic.get("综合判断与数据支撑", "").replace("\n", " ")
                timeframe = logic.get("验证时间窗", "")

                markdown_output += f"- **核心假设**: {assumption}<br>"
                markdown_output += f"**综合判断与数据支撑**: {judgment}<br>"
                markdown_output += f"**验证时间窗**: {timeframe}\n\n"

        # 处理可执行策略工具箱
        if "可执行策略工具箱" in strategy:
            toolbox = strategy["可执行策略工具箱"]
            markdown_output += "### 可执行策略工具箱\n\n"

            # 策略名称和机会窗口
            markdown_output += f"**策略名称**: {toolbox.get('策略名称', '')}\n\n"
            markdown_output += f"**机会窗口**: {toolbox.get('机会窗口', '')}\n\n"

            # 标的配置
            if "标的配置" in toolbox:
                markdown_output += "#### 标的配置\n\n"
                for index, asset in enumerate(toolbox["标的配置"], start=1):
                    core_asset = asset.get("核心标的", "").replace("\n", " ")
                    advantage = asset.get("核心优势", "").replace("\n", " ")
                    reason = asset.get("选择原因", "").replace("\n", " ")
                    operation = asset.get("操作要点", "").replace("\n", " ")
                    profit_condition = asset.get("止盈条件", "").replace("\n", " ")
                    stop_loss = asset.get("止损条件", "").replace("\n", " ")

                    markdown_output += f"{index}. **核心标的**: {core_asset}<br>"
                    markdown_output += f"**核心优势**: {advantage}<br>"
                    markdown_output += f"**选择原因**: {reason}<br>"
                    markdown_output += f"**操作要点**: {operation}<br>"
                    markdown_output += f"**止盈条件**: {profit_condition}<br>"
                    markdown_output += f"**止损条件**: {stop_loss}\n\n"

                markdown_output += "| 核心标的 | 仓位配置 |\n"
                markdown_output += "|----------|----------|\n"

                for asset in toolbox["标的配置"]:
                    core_asset = asset.get("核心标的", "").replace("\n", " ")
                    allocation = asset.get("仓位配置", "")

                    markdown_output += f"| {core_asset} | {allocation} |\n"

                markdown_output += "\n"

            # 机会评估
            if "机会评估" in toolbox:
                assessment = toolbox["机会评估"]
                markdown_output += "#### 机会评估\n\n"
                markdown_output += "| 确定性评级 | 预期回报周期 | Alpha | Beta | 夏普比率 | f1 | f2 | 综合排序 |\n"
                markdown_output += "|------------|--------------|-------|------|------|------|------|----------|\n"

                rating = assessment.get("确定性评级", "")
                return_period = assessment.get("预期回报周期", "")
                alpha = assessment.get("Alpha", "")
                beta = assessment.get("Beta", "")
                sharpe_ratio = assessment.get("夏普比率", "")
                f1 = assessment.get("f1", "")
                f2 = assessment.get("f2", "")
                ranking = assessment.get("综合排序", "")

                markdown_output += f"| {rating} | {return_period} | {alpha} | {beta} | {sharpe_ratio} | {f1} | {f2} | {ranking} |\n\n"

            # VaR值
            if "VaR值" in toolbox:
                markdown_output += "#### VaR 值\n\n"
                markdown_output += "```plaintext\n"
                markdown_output += toolbox["VaR值"] + "\n"
                markdown_output += "```\n\n"

            # 风险监控哨兵
            if "风险监控哨兵" in toolbox:
                markdown_output += "#### 风险监控哨兵\n\n"

                for index, sentinel in enumerate(toolbox["风险监控哨兵"], start=1):
                    level = sentinel.get("风险等级", "")
                    description = sentinel.get("风险描述", "").replace("\n", " ")
                    condition = sentinel.get("触发条件", "").replace("\n", " ")
                    response = sentinel.get("应对预案", "").replace("\n", " ")

                    markdown_output += f"- **风险等级**: {level}<br>"
                    markdown_output += f"**风险描述**: {description}<br>"
                    markdown_output += f"**触发条件**: {condition}<br>"
                    markdown_output += f"**应对预案**: {response}\n\n"

            # 关键跟踪指标
            if "关键跟踪指标" in toolbox:
                markdown_output += "#### 关键跟踪指标\n\n"
                for indicator in toolbox["关键跟踪指标"]:
                    # 清理指标格式
                    clean_indicator = re.sub(r'\*\*(.*?)\*\*', r'**\1**', indicator)
                    markdown_output += f"- {clean_indicator}\n"

                markdown_output += "\n"

            # 策略生成信息
            markdown_output += "> "
            if "策略生成日期" in toolbox:
                markdown_output += f"**策略生成日期**: {toolbox['策略生成日期']}  "
            if "策略生成来源" in toolbox:
                markdown_output += f"\n**策略生成来源**: {toolbox['策略生成来源']}"
            markdown_output += "\n\n"

        markdown_output += "------\n\n"

    return markdown_output


def merge_and_sort_strategies(strategy_list):
    # 定义确定性评级的排序权重
    rating_weights = {
        "★★★★★": 5,
        "★★★★☆": 4,
        "★★★☆☆": 3,
        "★★☆☆☆": 2,
        "★☆☆☆☆": 1
    }

    # 按确定性评级排序
    sorted_strategies = sorted(
        strategy_list,
        key=lambda x: rating_weights.get(
            x.get("可执行策略工具箱", {}).get("机会评估", {}).get("确定性评级", ""),
            0
        ),
        reverse=True
    )

    # 更新综合排序字段
    for index, strategy in enumerate(sorted_strategies, start=1):
        if "可执行策略工具箱" in strategy and "机会评估" in strategy["可执行策略工具箱"]:
            strategy["可执行策略工具箱"]["机会评估"]["综合排序"] = str(index)

    return sorted_strategies
