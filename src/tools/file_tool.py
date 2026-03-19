from src.logger_config import logger


def file_write(file_name, content):
    try:
        with open(file_name, "w", encoding="utf-8") as file:
            file.writelines(content)
    except Exception as e:
        logger.error(f"file_write error: {e}")
