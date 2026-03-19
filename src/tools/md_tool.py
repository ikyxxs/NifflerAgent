import os

from markdown_it import MarkdownIt
from weasyprint import HTML

from src.config import STATIC_DIR


def markdown2pdf(file_name, md_text: str):
    """Markdown转PDF"""
    return html2pdf(file_name, markdown2html(md_text))


def markdown2html(md_text: str) -> str:
    """Markdown转HTML"""
    md = MarkdownIt("commonmark").enable(['table', 'list'])
    html_content = md.render(md_text)

    # 4. 嵌入CSS样式（美化表格、代码框等）
    styled_html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <title>Markdown 转换 PDF</title>
            <style>
                /* PDF页面边距设置（核心控制打印边距） */
                @page {{
                    margin-top: 0.6cm;
                    margin-right: 0.5cm;
                    margin-bottom: 0.6cm;
                    margin-left: 0.5cm;
                    size: A4;
                }}

                /* 全局样式重置与基础设置 */
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
                                "Helvetica Neue", Arial, sans-serif;
                    font-size: 13px;  /* 基础字体进一步缩小 */
                    line-height: 1.5;
                    color: #666666;
                    background-color: #f7f8fa;
                    padding: 0.8rem 0;
                }}

                /* 内容容器样式 */
                .vue-container {{
                    max-width: 920px;
                    margin: 0 auto;
                    padding: 1.8rem;  /* 紧凑的内边距 */
                    background-color: #ffffff;
                    border-radius: 6px;
                    box-shadow: 0 1px 6px rgba(0, 0, 0, 0.03);
                }}

                /* 标题样式（按比例缩小） */
                h1, h2, h3, h4, h5, h6 {{
                    color: #333333;
                    margin-top: 1.4rem;
                    margin-bottom: 0.7rem;
                    font-weight: 600;
                }}
                h1 {{
                    font-size: 1.6rem;
                    border-bottom: 1px solid #eaecef;
                    padding-bottom: 0.35rem;
                    color: #42b983;
                }}
                h2 {{
                    font-size: 1.2rem;
                    border-left: 4px solid #42b983;
                    padding-left: 0.65rem;
                }}
                h3 {{
                    font-size: 1.0rem;
                    color: #42b983;
                }}
                h4, h5, h6 {{
                    font-size: 0.95rem;
                }}

                /* 段落样式 */
                p {{
                    margin-bottom: 0.75rem;
                    line-height: 1.55;
                }}

                /* 表格样式（极致紧凑） */
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 1.0rem 0;
                    font-size: 0.7rem;  /* 表格字体进一步缩小 */
                }}
                th, td {{
                    padding: 0.35rem 0.5rem;  /* 最小化内边距 */
                    text-align: left;
                    border: 1px solid #eaecef;
                    line-height: 1.4;  /* 紧凑行高 */
                }}
                th {{
                    background-color: #fafbfc;
                    color: #333333;
                    font-weight: 600;
                    font-size: 0.73rem;  /* 表头略大于内容 */
                }}
                tr:hover {{
                    background-color: #f7f8fa;
                }}

                /* 代码块样式 */
                pre {{
                    background-color: #f5f5f5;
                    border: 1px solid #eaecef;
                    border-radius: 4px;
                    padding: 0.75rem;
                    margin: 1.1rem 0;
                    overflow-x: auto;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    font-family: "SFMono-Regular", Consolas, "Liberation Mono", 
                                Menlo, monospace;
                    font-size: 0.75rem;  /* 代码字体缩小 */
                    line-height: 1.45;
                }}
                code {{
                    font-family: inherit;
                    font-size: inherit;
                    color: #333333;
                    background-color: #f5f5f5;
                    padding: 0.12rem 0.25rem;
                    border-radius: 3px;
                }}
                p code, li code {{
                    padding: 0.07rem 0.2rem;
                    background-color: #f0f4f8;
                    font-size: 0.8em;
                }}

                /* 列表样式 */
                ul, ol {{
                    margin-left: 1.1rem;
                    margin-bottom: 0.75rem;
                }}
                li {{
                    margin-bottom: 0.3rem;
                }}
                li > ul, li > ol {{
                    margin-top: 0.2rem;
                    margin-left: 0.9rem;
                    margin-bottom: 0;
                }}

                /* 链接样式 */
                a {{
                    color: #42b983;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}

                /* 图片样式（确保不超出容器） */
                img {{
                    max-width: 100%;
                    height: auto;
                    margin: 1.2rem 0;
                    border-radius: 4px;
                }}

                /* 特殊符号样式 */
                .math-symbol {{
                    font-family: "Times New Roman", serif;
                }}

                /* 代码字体兼容性设置 */
                pre, code {{
                    font-family: 
                        "Consolas", 
                        "SimHei", "Microsoft YaHei", "Heiti SC",
                        "WenQuanYi Micro Hei", "Heiti TC",
                        "PingFang SC", "Hiragino Sans GB",
                        monospace;
                }}
            </style>
        </head>
        <body>
            <div class="vue-container">
                {html_content}
            </div>
        </body>
        </html>
        """

    return styled_html


def html2pdf(file_name, html_content):
    """HTML转PDF"""
    file_path = STATIC_DIR + '/pdf/' + file_name + '.pdf'
    os.makedirs(STATIC_DIR + '/pdf/', exist_ok=True)
    HTML(string=html_content).write_pdf(file_path)
    return file_path
