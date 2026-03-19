from langgraph.constants import START
from langgraph.graph import StateGraph, END

from src.nodes.report_node import receive_report, report_analysis, generate_strategy_pdf, generate_strategy_markdown, \
    read_triage
from src.state import AgentState


def create_workflow():
    """创建工作流"""
    # 构建LangGraph工作流
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("receive_report", receive_report)
    workflow.add_node("report_analysis", report_analysis)
    workflow.add_node("generate_strategy_markdown", generate_strategy_markdown)
    workflow.add_node("generate_strategy_pdf", generate_strategy_pdf)
    workflow.add_node("read_triage", read_triage)

    # 定义节点之间的连接
    workflow.add_edge(START, "receive_report")
    workflow.add_edge("receive_report", "report_analysis")
    workflow.add_edge("report_analysis", "generate_strategy_markdown")
    workflow.add_edge("generate_strategy_markdown", "generate_strategy_pdf")
    workflow.add_edge("generate_strategy_pdf", "read_triage")
    workflow.add_edge("read_triage", END)

    # 编译工作流
    return workflow.compile()
