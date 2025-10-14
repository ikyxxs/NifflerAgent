import os
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

# 临时添加项目根目录到Python路径（必要操作）
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.graphs.workflow import create_workflow
from src.graphs.mermaid import draw_mermaid_png
from src.tools.history import load_history, save_history


def main():
    # 创建工作流
    app = create_workflow()
    # 绘图
    draw_mermaid_png(app)

    # 初始化历史记录
    if 'history' not in st.session_state:
        st.session_state.history = load_history()

    # 构建Streamlit界面
    st.title("📄研报分析 Agent")
    st.write("上传研报 PDF，AI 将基于研报内容生成投资策略")
    # 确保页面布局设置
    st.set_page_config(page_title="研报分析 Agent", layout="wide")

    # 侧边栏显示说明和历史记录
    with st.sidebar:
        # st.header("使用说明")
        # st.markdown("""
        # 1. 上传文本文件（.txt、.md、.pdf等）
        # 2. 点击"分析研报"按钮
        # 3. 查看AI的分析结果
        #
        # 注意：请确保已在.env文件中设置了OPENAI_API_KEY
        # """)
        
        st.header("历史记录")
        # 显示历史记录
        for i, record in enumerate(st.session_state.history):
            if st.button(f"{record['timestamp']} - {record['filename']}", key=f"history_{i}"):
                # 恢复历史记录
                st.session_state.current_result = record['data']
                st.rerun()

    # 主内容区
    # 文件上传
    uploaded_file = st.file_uploader("选择文件", type=["txt", "md", "pdf"])

    # 问题输入
    addition = st.text_area("如有补充或者更正的信息，请在此输入", height=80)

    # 提交按钮
    if st.button("分析研报", use_container_width=True):
        if not uploaded_file:
            st.error("请上传研报文件")
            return

        # 显示加载状态
        with st.spinner("正在处理..."):
            # 准备初始状态
            initial_state = {
                "file": uploaded_file,
                "addition": addition,
                "thoughts": []
            }

            # 创建一个占位符来显示实时处理过程
            thoughts_placeholder = st.empty()
            
            # 存储结果数据
            result_data = {}

            # 使用stream方法逐步获取结果
            for step in app.stream(initial_state):
                # 每个step是一个字典，包含节点名称和对应的输出
                for node_name, output in step.items():
                    if "thoughts" in output:
                        # 更新思考过程显示
                        with thoughts_placeholder.container():
                            with st.expander("处理进度", expanded=True):
                                for i, thought in enumerate(output["thoughts"], 1):
                                    st.write(f"{i}. {thought}")

                    if 'strategy_markdown' in output:
                        st.subheader("投资策略", anchor='投资策略')
                        strategy_markdown = "\n\n" + output.get("strategy_markdown", "")
                        st.markdown(
                            f"""<div style="border: 1px solid #ccc; padding: 1rem; border-radius: 5px;">{strategy_markdown}</div>""",
                            unsafe_allow_html=True)
                        result_data['strategy_markdown'] = strategy_markdown

                    if 'strategy_pdf' in output:
                        st.text('')
                        strategy_pdf = output.get("strategy_pdf", "")
                        with open(strategy_pdf, "rb") as f:
                            st.download_button(
                                label="下载投资策略 PDF",
                                data=f,
                                file_name=os.path.basename(strategy_pdf),
                                mime="application/pdf"
                            )
                        result_data['strategy_pdf'] = strategy_pdf

                    if 'holdings' in output:
                        st.subheader("研报中的持仓信息", anchor='研报中的持仓信息')
                        holdings = "\n\n" + output.get("holdings", "")
                        st.markdown(
                            f"""<div style="border: 1px solid #ccc; padding: 1rem; border-radius: 5px;">{holdings}</div>""",
                            unsafe_allow_html=True)
                        result_data['holdings'] = holdings

                    if 'similar_thesis_markdown' in output:
                        st.subheader("投资假设对比", anchor='投资假设对比')
                        similar_thesis_markdown = "\n\n" + output.get("similar_thesis_markdown", "")
                        st.markdown(
                            f"""<div style="border: 1px solid #ccc; padding: 1rem; border-radius: 5px;">{similar_thesis_markdown}</div>""",
                            unsafe_allow_html=True)
                        result_data['similar_thesis_markdown'] = similar_thesis_markdown

                    if 'final_strategy_markdown' in output:
                        st.subheader("最终投资逻辑", anchor='最终投资逻辑')
                        final_strategy_markdown = "\n\n" + output.get("final_strategy_markdown", "")
                        st.markdown(
                            f"""<div style="border: 1px solid #ccc; padding: 1rem; border-radius: 5px;">{final_strategy_markdown}</div>""",
                            unsafe_allow_html=True)
                        result_data['final_strategy_markdown'] = final_strategy_markdown

                    if 'final_strategy_pdf' in output:
                        st.text("")
                        final_strategy_pdf = output.get("final_strategy_pdf", "")
                        with open(final_strategy_pdf, "rb") as f:
                            st.download_button(
                                label="下载最终投资策略 PDF",
                                data=f,
                                file_name=os.path.basename(final_strategy_pdf),
                                mime="application/pdf"
                            )
                        result_data['final_strategy_pdf'] = final_strategy_pdf
            
            # 添加到历史记录
            history_record = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'filename': uploaded_file.name,
                'data': result_data
            }
            st.session_state.history.insert(0, history_record)  # 插入到开头
            save_history(st.session_state.history)  # 保存到本地文件
    else:
        # 显示当前结果（从历史记录中恢复的）
        if 'current_result' in st.session_state:
            result_data = st.session_state.current_result

            if 'holdings' in result_data:
                st.subheader("研报中的持仓信息", anchor='研报中的持仓信息')
                st.markdown(
                    f"""<div style="border: 1px solid #ccc; padding: 1rem; border-radius: 5px;">{result_data['holdings']}</div>""",
                    unsafe_allow_html=True)

            if 'similar_thesis_markdown' in result_data:
                st.subheader("投资假设对比", anchor='投资假设对比')
                st.markdown(
                    f"""<div style="border: 1px solid #ccc; padding: 1rem; border-radius: 5px;">{result_data['similar_thesis_markdown']}</div>""",
                    unsafe_allow_html=True)
            
            if 'strategy_markdown' in result_data:
                st.subheader("投资策略", anchor='投资策略')
                st.markdown(
                    f"""<div style="border: 1px solid #ccc; padding: 1rem; border-radius: 5px;">{result_data['strategy_markdown']}</div>""",
                    unsafe_allow_html=True)
            
            if 'strategy_pdf' in result_data:
                st.text("")
                with open(result_data['strategy_pdf'], "rb") as f:
                    st.download_button(
                        label="下载投资策略 PDF",
                        data=f,
                        file_name=os.path.basename(result_data['strategy_pdf']),
                        mime="application/pdf"
                    )
            
            if 'final_strategy_markdown' in result_data:
                st.subheader("最终投资逻辑", anchor='最终投资逻辑')
                st.markdown(
                    f"""<div style="border: 1px solid #ccc; padding: 1rem; border-radius: 5px;">{result_data['final_strategy_markdown']}</div>""",
                    unsafe_allow_html=True)
            
            if 'final_strategy_pdf' in result_data:
                st.text("")
                with open(result_data['final_strategy_pdf'], "rb") as f:
                    st.download_button(
                        label="下载最终投资策略 PDF",
                        data=f,
                        file_name=os.path.basename(result_data['final_strategy_pdf']),
                        mime="application/pdf"
                    )
            
            # 清除current_result以便下次正常分析
            del st.session_state.current_result


if __name__ == "__main__":
    main()
