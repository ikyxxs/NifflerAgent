FROM registry.cn-hangzhou.aliyuncs.com/brynhild/python:3.11

# 安装系统依赖（解决 libgobject 缺失问题，weasyprint要用）
#RUN #apt-get update && apt-get install -y \
#    gobject-introspection \
#    libcairo2 \
#    libpango-1.0-0 \
#    libpangocairo-1.0-0 \
#    fontconfig \
#    ttf-wqy-microhei \
#    ttf-wqy-zenhei \
#    fonts-noto-cjk \
#    && rm -rf /var/lib/apt/lists/* # 清理缓存,减小镜像体积

# 设置工作目录
WORKDIR /app

# 将当前目录的内容复制到工作目录中
COPY . /app

# 安装项目依赖
#RUN pip3 install fastapi
#RUN pip3 install uvicorn
#RUN pip3 install ipython
#RUN pip3 install langchain
#RUN pip3 install langchain_core
#RUN pip3 install langchain_openai
#RUN pip3 install langgraph
#RUN pip3 install python-dotenv
#RUN pip3 install Requests
#RUN pip3 install streamlit
#RUN pip3 install typing_extensions
#RUN pip3 install weasyprint

# 开放端口
EXPOSE 8501

# 运行应用程序
CMD ["streamlit", "run", "src/main.py", "--server.port", "8501", "--server.address", "0.0.0.0"]

# 增加HEALTHCHECK指令
HEALTHCHECK --interval=60s --timeout=3s  --retries=3 \
    CMD curl -fs http://localhost:8501/test || exit 1