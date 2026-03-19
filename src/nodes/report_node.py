import json

from langchain_core.messages import SystemMessage, HumanMessage

from src.config import CACHE_DIR, OCR_DIR
from src.constatns.prompt import SYSTEM_PROMPT_REPORT_ANALYSIS, SYSTEM_PROMPT_READ_TRIAGE
from src.logger_config import logger
from src.tools import paddle_tool
from src.tools.decorators import timeit
from src.tools.file_tool import file_write
from src.tools.llm_tool import get_llm, ask_llm
from src.tools.md_tool import markdown2pdf
from src.tools.re_tool import extract_number
from src.tools.strategy_tool import strategy_json_to_markdown, format_json


def receive_report(state):
    """研报PDF转Markdown"""
    file = state.get("file")

    file_content = paddle_tool.pdf2markdown(file.getvalue())
    if not file_content:
        raise SystemError("研报解析异常，请联系管理员")

    # 缓存到文件
    file_write(OCR_DIR + '/' + file.name + ".md", file_content)

    # 更新思考过程
    thoughts = [f"接收到研报《{file.name}》"]
    logger.info(f"研报PDF转Markdown: {file.name}")

    # 更新状态，传递给下一个节点
    return {"file_content": file_content, "thoughts": thoughts}


@timeit
def report_analysis(state):
    """分析研报生成投资策略JSON"""
    logger.info('生成投资策略JSON')

    # 更新思考过程
    thoughts = state.get("thoughts", [])
    thoughts.append("分析研报")

    # 处理文件内容
    file = state.get("file")
    file_content = state.get("file_content", '')

    # 构建提示词
    user_prompt = f"""
            研报内容
            {file_content}
            ---
            分析研报内容并建立投资策略。输出的策略使用中文。输出格式为标准的JSON
            """
    messages = [
        SystemMessage(content=SYSTEM_PROMPT_REPORT_ANALYSIS),
        HumanMessage(content=user_prompt)
    ]

    # 调用OpenAI API
    try:
        answer = get_llm().invoke(messages).content
        logger.info('degrade, 投资逻辑JSON:\n' + answer)
    except Exception as e:
        logger.error(f"report_analysis,again, 请求失败: {str(e)}")
        answer = f"分析研报失败: {str(e)}"
        thoughts.append(f"分析研报失败: {str(e)}")

    strategy_json = format_json(answer)
    #  额外计算
    calculate_f1_f2(strategy_json)

    # 持久化(临时先用本地文件代替)
    if '分析研报失败' not in answer:
        with open(CACHE_DIR + '/' + file.name + ".txt", "w", encoding="utf-8") as file:
            json.dump(strategy_json, file, ensure_ascii=False, indent=2)

    # 返回最终结果
    return {"thoughts": thoughts, "strategy_json": strategy_json}


def generate_strategy_markdown(state):
    """生成投资策略Markdown"""
    logger.info('生成投资策略 Markdown')

    strategy_json = state.get('strategy_json')
    strategy_markdown = strategy_json_to_markdown(strategy_json)

    # 更新思考过程
    thoughts = state.get("thoughts", [])
    thoughts.append("[生成投资策略 Markdown](#投资策略)")

    return {"thoughts": thoughts, "strategy_markdown": strategy_markdown}


def generate_strategy_pdf(state):
    """生成投资策略PDF"""
    logger.info('生成投资策略 PDF')

    file = state.get("file")
    file_name = f"《{file.name}》投资策略"
    strategy_markdown = state.get("strategy_markdown")
    strategy_pdf = markdown2pdf(file_name, strategy_markdown)

    # 更新思考过程
    thoughts = state.get("thoughts", [])
    thoughts.append("生成投资策略 PDF")

    # 更新状态，传递给下一个节点
    return {"file": state.get('file'), "strategy_pdf": strategy_pdf, "thoughts": thoughts}


def read_triage(state):
    """判断研报原文是否值得阅读"""
    logger.info('判断研报原文是否值得阅读')

    file_content = state.get('file_content')
    # 构建提示词
    user_prompt = f"""
               研报内容
               {file_content}
               """
    messages = [
        SystemMessage(content=SYSTEM_PROMPT_READ_TRIAGE),
        HumanMessage(content=user_prompt)
    ]

    try:
        answer = ask_llm(messages)
        logger.info('判断研报原文是否值得阅读:\n' + answer)
    except Exception as e:
        logger.error(f"判断研报原文是否值得阅读, 请求失败: {str(e)}")
        answer = ''

    # 更新思考过程
    thoughts = state.get("thoughts", [])
    thoughts.append("[判断研报原文是否值得阅读](#阅读价值评估)")

    return {"thoughts": thoughts, "read_triage_result": answer}


def calculate_f1_f2(strategy_json):
    """
    递归遍历JSON数据，找到所有的 "机会评估" 字典，
    提取 Alpha 和 Beta，计算 f1 和 f2 并插入。
    公式：
    f1 = alpha x 10 / beta
    f2 = alpha / (beta - 1)
    """
    logger.info('计算f和f1')

    try:
        for i, strategy in enumerate(strategy_json, 1):
            if "可执行策略工具箱" in strategy:
                toolbox = strategy["可执行策略工具箱"]
                if "机会评估" in toolbox:
                    assessment = toolbox["机会评估"]
                    alpha = extract_number(assessment.get("Alpha", ""))
                    if alpha is not None:
                        alpha = alpha / 100
                    beta = extract_number(assessment.get("Beta", ""))
                    if alpha is None or beta is None or beta == 0:
                        continue
                    f1 = (alpha * 10) / beta
                    f2 = alpha / (beta - 1)

                    # 插入计算结果 (保留2位小数)
                    assessment["f1"] = round(f1, 2)
                    assessment["f2"] = round(f2, 2)
    except Exception as e:
        logger.error(f'计算f和f1失败: {str(e)}')
