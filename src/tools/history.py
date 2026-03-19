import json
import os

from src.logger_config import logger
from src.config import HISTORY_FILE


def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if not content.strip():
                    return []
                return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error(f"历史记录文件格式错误: {e}")
    except Exception as e:
        logger.error(f"加载历史记录失败: {e}")
    return []


def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"保存历史记录失败: {e}")
        return False