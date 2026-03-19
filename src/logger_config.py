"""
日志配置模块 - 按日期轮转版本
每天午夜自动创建新的日志文件
"""
import logging
import os
from logging.handlers import TimedRotatingFileHandler

from src.config import LOG_DIR


def setup_logging():
    """配置并返回logger实例"""

    # 创建logger
    logger = logging.getLogger('niffler-agent')
    logger.setLevel(logging.INFO)

    # 避免重复添加handler
    if logger.handlers:
        return logger

    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]',
        '%Y-%m-%d %H:%M:%S'
    )

    # 1. 创建控制台handler（保留控制台输出）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. 创建按日期轮转的文件handler
    # 每天午夜创建新文件，保留30天日志
    file_handler = TimedRotatingFileHandler(
        os.path.join(LOG_DIR, 'app.log'),  # 基础文件名
        when='midnight',                   # 轮转时间点：午夜
        interval=1,                        # 间隔1天
        backupCount=30,                    # 保留30天日志
        encoding='utf-8',                  # 支持中文
        utc=False                          # 使用本地时间
    )

    # 设置日志文件后缀格式（YYYYMMDD）
    file_handler.suffix = "%Y%m%d"

    # 设置文件handler的级别和格式
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# 创建全局logger实例
logger = setup_logging()