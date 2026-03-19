import os
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st


# 临时添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.graphs.workflow import create_workflow
from src.graphs.mermaid import draw_mermaid_png
from src.tools.history import load_history, save_history
from src.logger_config import logger


def main():
    # 初始化会话状态
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'history' not in st.session_state:
        st.session_state.history = load_history()
    # 右侧对话栏宽度比例（0.1~0.5之间）
    if 'chat_width_ratio' not in st.session_state:
        st.session_state.chat_width_ratio = 0.01
    # 添加当前显示结果的状态
    if 'display_result' not in st.session_state:
        st.session_state.display_result = None

    # 创建工作流
    app = create_workflow()
    draw_mermaid_png(app)

    st.set_page_config(page_title="研报分析 Agent", layout="wide")

    # 左侧历史记录侧边栏
    with st.sidebar:
        st.header("历史记录")
        for i, record in enumerate(st.session_state.history):
            btn_key = f"history_{record.get('timestamp', i)}_{i}"
            if st.button(f"{record['timestamp']} - {record['filename']}", key=btn_key):
                st.session_state.display_result = record['data']
                st.rerun()

    # 计算宽度比例（中间区域 = 1 - 右侧比例）
    main_width = 1 - st.session_state.chat_width_ratio
    chat_width = st.session_state.chat_width_ratio

    # 主布局：中间区域 + 右侧对话栏
    main_area, chat_area = st.columns([main_width, chat_width])

    # 中间主内容区（保持原始功能）
    with main_area:
        st.title("📄研报分析 Agent")
        st.write("上传研报 PDF，AI 将基于研报内容生成投资策略")

        # 文件上传
        uploaded_file = st.file_uploader("选择文件", type=["txt", "md", "pdf"])

        # 提交按钮
        if st.button("🚀 开始分析研报", use_container_width=True):
            if not uploaded_file:
                st.error("⚠️ 请先上传研报文件")
                return

            with st.spinner("🔍 AI 正在深度分析研报，请稍候..."):
                initial_state = {
                    "file": uploaded_file,
                    "thoughts": []
                }

                thoughts_placeholder = st.empty()
                result_data = {}

                for step in app.stream(initial_state):
                    for node_name, output in step.items():
                        if "thoughts" in output:
                            with thoughts_placeholder.container():
                                with st.expander("处理进度", expanded=True):
                                    for i, thought in enumerate(output["thoughts"], 1):
                                        st.write(f"{i}. {thought}")

                        if 'strategy_markdown' in output:
                            result_data['strategy_markdown'] = "\n\n" + output.get("strategy_markdown", "")

                            st.subheader("投资策略", anchor='投资策略')
                            st.markdown(
                                f"""<div style="border: 1px solid #e5e7eb; padding: 1rem; border-radius: 0.5rem; background-color: #f9fafb;">{result_data['strategy_markdown']}</div>""",
                                unsafe_allow_html=True)

                        if 'strategy_pdf' in output:
                            result_data['strategy_pdf'] = output.get("strategy_pdf", "")

                            if  os.path.exists(result_data['strategy_pdf']):
                                st.text("")
                                with open(result_data['strategy_pdf'], "rb") as f:
                                    st.download_button(
                                        label="📥 下载投资策略 PDF",
                                        data=f,
                                        file_name=os.path.basename(result_data['strategy_pdf']),
                                        mime="application/pdf",
                                        key="download_strategy_pdf_new",
                                        use_container_width=True
                                    )

                        if 'read_triage_result' in output:
                            result_data['read_triage_result'] = "\n\n" + output.get("read_triage_result", "")

                            st.subheader("阅读价值评估", anchor='阅读价值评估')
                            st.markdown(
                                f"""<div style="border: 1px solid #e5e7eb; padding: 1rem; border-radius: 0.5rem; background-color: #f9fafb;">{result_data['read_triage_result']}</div>""",
                                unsafe_allow_html=True)

                # 保存历史记录
                history_record = {
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'filename': uploaded_file.name,
                    'data': result_data
                }
                st.session_state.history.insert(0, history_record)
                save_history(st.session_state.history)

                # 设置当前显示结果
                st.session_state.display_result = result_data
                st.rerun()

        # 显示结果（无论是新生成的还是历史的）
        if st.session_state.display_result:
            result_data = st.session_state.display_result

            if 'strategy_markdown' in result_data:
                st.subheader("投资策略", anchor='投资策略')
                st.markdown(
                    f"""<div style="border: 1px solid #e5e7eb; padding: 1rem; border-radius: 0.5rem; background-color: #f9fafb;">{result_data['strategy_markdown']}</div>""",
                    unsafe_allow_html=True)

            if 'strategy_pdf' in result_data and os.path.exists(result_data['strategy_pdf']):
                st.text("")
                pdf_path = result_data['strategy_pdf']
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📥 下载投资策略 PDF",
                        data=f,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf",
                        key=f"download_strategy_pdf_history_{os.path.basename(pdf_path)}",
                        use_container_width=True
                    )

            if 'read_triage_result' in result_data:
                st.subheader("阅读价值评估", anchor='阅读价值评估')
                st.markdown(
                    f"""<div style="border: 1px solid #e5e7eb; padding: 1rem; border-radius: 0.5rem; background-color: #f9fafb;">{result_data['read_triage_result']}</div>""",
                    unsafe_allow_html=True)


if __name__ == "__main__":
    main()