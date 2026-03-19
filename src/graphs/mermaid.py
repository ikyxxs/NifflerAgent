import os
import subprocess
import sys

from langchain_core.runnables.graph import MermaidDrawMethod

from src.config import STATIC_DIR
from src.logger_config import logger


def draw_mermaid_png(graph):
    try:
        mermaid_png = graph.get_graph(xray=1).draw_mermaid_png(draw_method=MermaidDrawMethod.API)
        output_folder = "."
        os.makedirs(output_folder, exist_ok=True)
        filename = os.path.join(output_folder, STATIC_DIR + "/graph.png")
        with open(filename, "wb") as f:
            f.write(mermaid_png)
        # if sys.platform.startswith("darwin"):
        #     subprocess.call(('open', filename))
        # elif sys.platform.startswith("linux"):
        #     subprocess.call(('xdg-open', filename))
        # elif sys.platform.startswith("win"):
        #     os.startfile(filename)
    except Exception as e:
        logger.error(f"draw_mermaid_png,请求失败: {str(e)}")