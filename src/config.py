import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
# 静态资源目录
STATIC_DIR = os.path.join(PROJECT_ROOT, "static")
os.makedirs(STATIC_DIR, exist_ok=True)
# 投资策略缓存目录
CACHE_DIR = os.path.join(PROJECT_ROOT, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
# OCR目录
OCR_DIR = os.path.join(PROJECT_ROOT, "ocr")
os.makedirs(OCR_DIR, exist_ok=True)
# 日志文件目录
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
# 历史记录文件
DB_DIR = os.path.join(PROJECT_ROOT, "db")
os.makedirs(DB_DIR, exist_ok=True)
HISTORY_FILE = os.path.join(PROJECT_ROOT, "db/history.json")


# ------------------------------
# API 配置
# ------------------------------
class APIConfig:
    # OpenAI 相关配置
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL")

    # PaddleOCR 相关配置
    PADDLE_OCR_API_URL: str = os.getenv("PADDLE_OCR_API_URL")
    PADDLE_OCR_TOKEN: str = os.getenv("PADDLE_OCR_TOKEN")

    @staticmethod
    def validate() -> None:
        """静态方法：验证关键配置是否存在"""
        missing = []
        if not APIConfig.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY (请在.env中设置)")

        if missing:
            raise ValueError(f"缺少必要的API配置：\n{', '.join(missing)}")


# ------------------------------
# 应用程序配置
# ------------------------------
class AppConfig:
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")  # 日志级别：DEBUG, INFO, WARNING, ERROR
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # 缓存配置
    # CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "False").lower() == "true"
    # CACHE_TTL: int = int(os.getenv("CACHE_TTL", 3600))  # 缓存过期时间（秒）

    # 批处理配置
    # BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", 100))  # 批处理大小
    # MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", 3))  # 最大重试次数


# ------------------------------
# 使用示例（无需实例化，直接通过类名访问）
# ------------------------------
# if __name__ == "__main__":
#     # 访问静态属性
#     print(f"OpenAI模型: {APIConfig.OPENAI_MODEL}")
#     print(f"服务端口: {APIConfig.API_PORT}")
#
#     # 调用静态方法
#     try:
#         APIConfig.validate()
#         print("API配置验证通过")
#     except ValueError as e:
#         print(f"配置错误: {e}")
