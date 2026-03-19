# NifflerAgent

基于 LangGraph 的研报分析 Agent，自动解析研报 PDF 并生成投资策略。

## 功能特性

- 📄 **PDF 解析**：使用 PaddleOCR-VL 解析研报 PDF，提取文本和图表
- 🤖 **AI 分析**：基于 LLM 进行研报深度分析，提取核心投资逻辑
- 📊 **策略生成**：自动生成可执行的投资策略，包含标的配置、风险监控等
- 📝 **报告导出**：支持 PDF 格式的策略报告导出
- 💾 **历史记录**：保存分析历史，方便回顾查看

## 环境要求

- Python 3.11+
- Docker（可选）

## 快速开始

### 方式一：本地运行

#### 1. 克隆项目

```bash
git clone <repository-url>
cd NifflerAgent
```

#### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量

复制环境变量模板并填写配置：

```bash
cp .env_template .env
```

编辑 `.env` 文件，填写以下配置：

```env
# OpenAI API 配置
OPENAI_API_KEY='your-api-key'
OPENAI_BASE_URL='https://api.openai.com/v1'
OPENAI_MODEL='gpt-4'

# PaddleOCR API 配置（从 https://aistudio.baidu.com/paddleocr/task 获取）
PADDLE_OCR_API_URL='your-paddle-ocr-api-url'
PADDLE_OCR_TOKEN='your-paddle-ocr-token'
```

#### 5. 运行应用

```bash
streamlit run src/main.py
```

应用将在 http://localhost:8500 启动。

### 方式二：Docker 运行

#### 1. 构建镜像

```bash
docker build -t niffler-agent:latest .
```

#### 2. 运行容器

```bash
docker run -d \
  -p 8500:8500 \
  --name niffler-agent \
  -e OPENAI_API_KEY='your-api-key' \
  -e OPENAI_BASE_URL='https://api.openai.com/v1' \
  -e OPENAI_MODEL='gpt-4' \
  -e PADDLE_OCR_API_URL='your-paddle-ocr-api-url' \
  -e PADDLE_OCR_TOKEN='your-paddle-ocr-token' \
  niffler-agent:latest
```

或者使用环境变量文件：

```bash
docker run -d \
  -p 8500:8500 \
  --name niffler-agent \
  --env-file .env \
  niffler-agent:latest
```

应用将在 http://localhost:8500 启动。

#### 3. 停止容器

```bash
docker stop niffler-agent
docker rm niffler-agent
```

## 项目结构

```
NifflerAgent/
├── src/
│   ├── constatns/
│   │   └── prompt.py          # 提示词模板
│   ├── graphs/
│   │   ├── workflow.py        # LangGraph 工作流定义
│   │   └── mermaid.py         # 工作流图可视化
│   ├── nodes/
│   │   └── report_node.py     # 工作流节点实现
│   ├── tools/
│   │   ├── decorators.py      # 装饰器工具
│   │   ├── file_tool.py       # 文件操作工具
│   │   ├── history.py         # 历史记录管理
│   │   ├── llm_tool.py        # LLM 调用工具
│   │   ├── md_tool.py         # Markdown 转 PDF
│   │   ├── paddle_tool.py     # PaddleOCR 调用
│   │   ├── re_tool.py         # 正则工具
│   │   └── strategy_tool.py   # 策略处理工具
│   ├── config.py              # 配置管理
│   ├── logger_config.py       # 日志配置
│   ├── main.py                # Streamlit 应用入口
│   └── state.py               # 状态定义
├── static/                    # 静态资源
├── cache/                     # 缓存目录
├── ocr/                       # OCR 结果
├── logs/                      # 日志文件
├── db/                        # 数据存储
├── .env_template              # 环境变量模板
├── requirements.txt           # Python 依赖
├── Dockerfile                 # Docker 构建文件
└── README.md
```

## 工作流程

```
┌─────────────────┐
│  receive_report │  接收并解析 PDF
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ report_analysis │  AI 分析研报内容
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ generate_strategy_md    │  生成 Markdown 策略
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ generate_strategy_pdf   │  生成 PDF 策略报告
└────────┬────────────────┘
         │
         ▼
┌─────────────────┐
│  read_triage    │  阅读价值评估
└────────┬────────┘
         │
         ▼
       [END]
```

## 配置说明

| 环境变量 | 说明 | 必填 |
|---------|------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | ✅ |
| `OPENAI_BASE_URL` | OpenAI API 地址 | ✅ |
| `OPENAI_MODEL` | 使用的模型名称 | ✅ |
| `PADDLE_OCR_API_URL` | PaddleOCR API 地址（[获取地址](https://aistudio.baidu.com/paddleocr/task)） | ✅ |
| `PADDLE_OCR_TOKEN` | PaddleOCR 访问令牌（[获取地址](https://aistudio.baidu.com/paddleocr/task)） | ✅ |
| `LOG_LEVEL` | 日志级别（DEBUG/INFO/WARNING/ERROR） | ❌ |

## 技术栈

- **前端框架**：Streamlit
- **工作流引擎**：LangGraph
- **LLM 集成**：LangChain OpenAI
- **PDF 解析**：PaddleOCR-VL
- **PDF 生成**：WeasyPrint
- **Markdown 解析**：markdown-it-py

## License

[MIT License](LICENSE)
