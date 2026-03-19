FROM python:3.11-slim

LABEL maintainer="NifflerAgent"
LABEL description="NifflerAgent Application"
LABEL version="1.0"

RUN apt-get update && apt-get install -y --no-install-recommends \
    gobject-introspection \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    fontconfig \
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    fonts-noto-cjk \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --retries 5 --timeout 120

COPY . /app

EXPOSE 8500

HEALTHCHECK --interval=60s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -fs http://localhost:8500/test || exit 1

CMD ["streamlit", "run", "src/main.py", "--server.port", "8500", "--server.address", "0.0.0.0"]
