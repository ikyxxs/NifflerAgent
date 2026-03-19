from langchain_openai import ChatOpenAI

from src.config import APIConfig
from src.logger_config import logger
from src.tools.decorators import timeit

@timeit
def get_llm():
    return ChatOpenAI(api_key=APIConfig.OPENAI_API_KEY, model=APIConfig.OPENAI_MODEL, base_url=APIConfig.OPENAI_BASE_URL, timeout=600, max_retries=0)


@timeit
def ask_llm(prompt):
    try:
        llm = get_llm()
        answer = ''
        for chunk in llm.stream(prompt):
            if chunk.content:
                answer += chunk.content
        return answer
    except Exception as e:
        logger.error(f"ask_llm, 请求失败: {str(e)}")
    return ''
