from langgraph.constants import START
from langgraph.graph import StateGraph, END

from src.nodes.report_node import receive_report, report_analysis, generate_strategy_pdf, generate_strategy_markdown, \
    extract_holdings
from src.nodes.stragy import generate_final_strategy_markdown, generate_final_strategy_pdf
from src.nodes.thesis import extract_similar_thesis
from src.state import AgentState


def create_workflow():
    """创建工作流"""
    # 构建LangGraph工作流
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("receive_report", receive_report)
    workflow.add_node("report_analysis", report_analysis)
    workflow.add_node("extract_holdings", extract_holdings)
    workflow.add_node("extract_similar_thesis", extract_similar_thesis)
    workflow.add_node("generate_strategy_markdown", generate_strategy_markdown)
    workflow.add_node("generate_strategy_pdf", generate_strategy_pdf)
    workflow.add_node("generate_final_strategy_markdown", generate_final_strategy_markdown)
    workflow.add_node("generate_final_strategy_pdf", generate_final_strategy_pdf)

    # 定义节点之间的连接
    workflow.add_edge(START, "receive_report")
    workflow.add_edge("receive_report", "report_analysis")
    workflow.add_edge("report_analysis", "extract_holdings")
    workflow.add_edge("extract_holdings", "extract_similar_thesis")
    workflow.add_edge("extract_similar_thesis", "generate_strategy_markdown")
    workflow.add_edge("generate_strategy_markdown", "generate_strategy_pdf")
    workflow.add_edge("generate_strategy_pdf", "generate_final_strategy_markdown")
    workflow.add_edge("generate_final_strategy_markdown", "generate_final_strategy_pdf")
    workflow.add_edge("generate_final_strategy_pdf", END)

    # 编译工作流
    return workflow.compile()
