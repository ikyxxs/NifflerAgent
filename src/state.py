from typing import TypedDict, List


# 定义状态结构
class AgentState(TypedDict):
    thoughts: List

    file: str
    file_content: str

    strategy_json: str
    strategy_markdown: str
    strategy_pdf: str

    read_triage_result: str

