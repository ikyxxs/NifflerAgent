from pathlib import Path

from src.tools.thesis_tool import similar_thesis, extract_thesis, thesis_json_to_markdown


def extract_similar_thesis(state):
    """提取相似的投资假设"""
    thoughts = state.get("thoughts", [])
    thoughts.append("[投资假设对比](#投资假设对比)")

    new_thesis_file_name = state.get('file').name

    new_thesis_list = []
    old_thesis_list = []

    folder_path = Path("./cache")
    for file in folder_path.iterdir():
        if file.is_file():
            file_name = file.name.removesuffix('.txt')
            file_content = open(file, "r", encoding="utf-8").read()

            if file_name != new_thesis_file_name:
                old_thesis_list.extend(extract_thesis(file_name, file_content))
            else:
                new_thesis_list.extend(extract_thesis(file_name, file_content))

    result_thesis = []
    for new_thesis in new_thesis_list:
        thesis_list = similar_thesis(new_thesis, old_thesis_list)
        if len(thesis_list) > 0:
            result_thesis.append(new_thesis)
            for static in thesis_list:
                result_thesis.append(static)

    # 测试代码
    # result_thesis = [{'核心假设': '腾讯控股（0700.HK）将受益于AI技术在其各业务线的广泛应用，推动收入增长和利润率提升', '综合判断与数据支撑': '高盛报告显示，腾讯2Q25收入增速为四年来最快，毛利率创历史新高（GS para 5）。AI技术已显著提升广告点击率（+50%/50%/60% yoy in Video Accounts/Mini-Programs/Weixin Search）和游戏内容生产效率（VALORANT Mobile预计年化收入70亿人民币，GS Exhibit 4）', '验证时间窗': '2025Q4-2026Q2', '来源': 'GS-腾讯业绩.pdf'}, {'核心假设': '腾讯AI技术在各业务线的成功部署将持续推动收入增长和利润率提升', '综合判断与数据支撑': '摩根斯坦利报告显示腾讯2Q25全面超预期（Revenue +15% YoY，Non-IFRS OP +19% YoY），AI驱动游戏业务增长22%（MS Exhibit 1），广告业务eCPM提升推动20%增长。管理层提出通过(1)现有业务AI驱动增长、(2)混元模型质量、(3)AI应用参与度、(4)AI代理等创新产品四个维度追踪AI成效（MS正文第1页）', '验证时间窗': '2025Q4-2026Q1', '来源': 'MS-腾讯业绩.pdf'}]

    if len(result_thesis) > 0:
        thesis_markdown = thesis_json_to_markdown(result_thesis)
        return {"thoughts": thoughts, "similar_thesis_markdown": thesis_markdown}
    return {"thoughts": thoughts, "similar_thesis_markdown": "无"}
