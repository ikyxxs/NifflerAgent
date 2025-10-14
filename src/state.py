from typing import TypedDict, List


# 定义状态结构
class AgentState(TypedDict):
    thoughts: List

    addition: str

    file: str
    file_id: str
    file_content: str

    holdings: str
    similar_thesis_markdown: str

    strategy_json: str
    strategy_markdown: str
    strategy_pdf: str

    final_strategy_markdown: str
    final_strategy_pdf: str

