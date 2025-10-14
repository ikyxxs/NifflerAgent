import json
import re

from src.tools.llm import get_llm


def format_json(content):
    content = content.replace('```json', '')
    content = content[:content.rfind('```')] + '' + content[content.rfind('```') + len('```'):] if content.rfind('```') != -1 else content
    if is_valid_json(content):
        return json.loads(content)
    if '**": "' in content:
        tmp_content = content.replace('**": "', '**：')
        if is_valid_json(tmp_content):
            return json.loads(tmp_content)
    print(f"format_json,请求失败, content:{content}")
    content = fix_json(content)
    return json.loads(content)


def is_valid_json(json_str):
    try:
        json.loads(json_str)
        return True
    except ValueError:
        return False


def fix_json(content):
    try:
        llm = get_llm('THUDM/GLM-Z1-9B-0414')
        content = llm.invoke(
            f"这个json格式不正确，修复一下格式问题，不要改动内容，并且只返回修改后的json，不要有多余信息\n---\n{content}").content
        content = content.replace('```json', '')
        content = content[:content.rfind('```')] + '' + content[content.rfind('```') + len('```'):] if content.rfind(
            '```') != -1 else content
    except Exception as e:
        pass
    return content


def strategy_json_to_markdown(json_data):
    """投资策略JSON转Markdown"""
    # 如果输入是字符串，则解析为JSON
    if isinstance(json_data, str):
        try:
            json_data = json_data.replace('```json', '')
            json_data = json_data[:json_data.rfind('```')] + '' + json_data[json_data.rfind('```') + len(
                '```'):] if json_data.rfind('```') != -1 else json_data
            data = json.loads(json_data)
        except json.JSONDecodeError:
            return ''
    else:
        data = json_data

    markdown_output = "# 投资策略分析报告\n\n"

    # 遍历每个策略
    for i, strategy in enumerate(data, 1):
        markdown_output += f"## 策略 {i}\n\n"

        # 处理核心投资逻辑
        if "核心投资逻辑" in strategy:
            markdown_output += "### 核心投资逻辑\n\n"
            markdown_output += "| 核心假设 | 综合判断与数据支撑 | 验证时间窗 |\n"
            markdown_output += "|----------|-------------------|------------|\n"

            for logic in strategy["核心投资逻辑"]:
                assumption = logic.get("核心假设", "").replace("\n", " ")
                judgment = logic.get("综合判断与数据支撑", "").replace("\n", " ")
                timeframe = logic.get("验证时间窗", "")

                markdown_output += f"| {assumption} | {judgment} | {timeframe} |\n"

            markdown_output += "\n"

        # 处理可执行策略工具箱
        if "可执行策略工具箱" in strategy:
            toolbox = strategy["可执行策略工具箱"]
            markdown_output += "### 可执行策略工具箱\n\n"

            # 策略名称和机会窗口
            markdown_output += f"**策略名称**: {toolbox.get('策略名称', '')}  \n"
            markdown_output += f"**机会窗口**: {toolbox.get('机会窗口', '')}\n\n"

            # 标的配置
            if "标的配置" in toolbox:
                markdown_output += "#### 标的配置\n\n"
                markdown_output += "| 核心标的 | 仓位配置 | 核心优势 | 选择原因 | 操作要点 | 止盈条件 | 止损条件 |\n"
                markdown_output += "|----------|----------|----------|----------|----------|----------|----------|\n"

                for asset in toolbox["标的配置"]:
                    core_asset = asset.get("核心标的", "").replace("\n", " ")
                    allocation = asset.get("仓位配置", "")
                    advantage = asset.get("核心优势", "").replace("\n", " ")
                    reason = asset.get("选择原因", "").replace("\n", " ")
                    operation = asset.get("操作要点", "").replace("\n", " ")
                    profit_condition = asset.get("止盈条件", "").replace("\n", " ")
                    stop_loss = asset.get("止损条件", "").replace("\n", " ")

                    markdown_output += f"| {core_asset} | {allocation} | {advantage} | {reason} | {operation} | {profit_condition} | {stop_loss} |\n"

                markdown_output += "\n"

            # 机会评估
            if "机会评估" in toolbox:
                assessment = toolbox["机会评估"]
                markdown_output += "#### 机会评估\n\n"
                markdown_output += "| 确定性评级 | 预期回报周期 | Alpha | Beta | 综合排序 |\n"
                markdown_output += "|------------|--------------|-------|------|----------|\n"

                rating = assessment.get("确定性评级", "")
                return_period = assessment.get("预期回报周期", "")
                alpha = assessment.get("Alpha", "")
                beta = assessment.get("Beta", "")
                ranking = assessment.get("综合排序", "")

                markdown_output += f"| {rating} | {return_period} | {alpha} | {beta} | {ranking} |\n\n"

            # VaR值
            if "VaR值" in toolbox:
                markdown_output += "#### VaR 值\n\n"
                markdown_output += "```plaintext\n"
                markdown_output += toolbox["VaR值"] + "\n"
                markdown_output += "```\n\n"

            # 风险监控哨兵
            if "风险监控哨兵" in toolbox:
                markdown_output += "#### 风险监控哨兵\n\n"
                markdown_output += "| 风险等级 | 风险描述 | 触发条件 | 应对预案 |\n"
                markdown_output += "|----------|----------|----------|----------|\n"

                for sentinel in toolbox["风险监控哨兵"]:
                    level = sentinel.get("风险等级", "")
                    description = sentinel.get("风险描述", "").replace("\n", " ")
                    condition = sentinel.get("触发条件", "").replace("\n", " ")
                    response = sentinel.get("应对预案", "").replace("\n", " ")

                    markdown_output += f"| {level} | {description} | {condition} | {response} |\n"

                markdown_output += "\n"

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