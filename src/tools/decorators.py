import time
from functools import wraps

from src.logger_config import logger


def timeit(func):
    """耗时统计装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            logger.info(f"函数 {func.__name__} 执行耗时: {elapsed_time:.2f}s")
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"函数 {func.__name__} 执行出错，耗时: {elapsed_time:.2f}s", exc_info=True)
            raise
    return wrapper
