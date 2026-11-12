# Cogniva · 智能知识问答平台

基于 RAG（检索增强生成）技术的智能知识问答平台，支持本地部署，保护隐私安全。

## 功能特性

- **智能问答** - 基于文档内容的上下文感知问答，支持多轮对话
- **知识库管理** - 支持多种文档格式（PDF、Word、Excel、文本等）的导入和管理
- **语义搜索** - 使用向量数据库实现文档内容的语义检索
- **长期记忆** - 基于间隔重复算法的记忆系统，支持遗忘曲线复习
- **多 LLM 支持** - 兼容 OpenAI、Claude、通义千问、Ollama 等多种大语言模型
- **本地部署** - 数据完全存储在本地，保护隐私安全

## 系统架构

![系统架构](docs/images/architecture.svg)

## RAG 工作流程

![RAG 流程](docs/images/rag-flow.svg)

## 项目截图

### 登录页面

![登录页面](docs/screenshots/login.png)

### 智能问答

![智能问答](docs/screenshots/chat.png)

### 知识库管理

![知识库管理](docs/screenshots/documents.png)

### 记忆系统

![记忆系统](docs/screenshots/memory.png)

### 设置页面

![设置页面](docs/screenshots/settings.png)

## 项目结构

![项目结构](docs/images/project-structure.svg)

## 技术栈

### 前端
- Next.js 14
- React 18
- TypeScript
- TailwindCSS
- Zustand (状态管理)
- shadcn/ui 组件

### 后端
- FastAPI
- SQLAlchemy
- PostgreSQL + pgvector
- LangChain
- Sentence Transformers

## 快速开始

### 方式一：Docker 一键启动（推荐）

环境要求：Docker Desktop（或 Docker Engine + Compose v2）

```bash
# 1. 准备配置文件
copy .env.example .env                    # Windows: copy / Linux: cp
copy backend\.env.example backend\.env    # 填入 LLM 与向量化 API Key

# 2. 一键启动（首次会自动构建镜像）
docker compose up -d

# 3. 访问 http://localhost
```

启动后的服务：

| 服务 | 说明 | 端口 |
|------|------|------|
| nginx | 统一入口，`/` 转前端、`/api` 转后端 | 80 |
| backend | FastAPI 后端 | 127.0.0.1:8000（仅本机调试） |
| frontend | Next.js 前端 | 内部 3000 |
| postgres | PostgreSQL + pgvector | 127.0.0.1:5433 |
| redis | 检索结果缓存 | 6379 |

常用命令：

```bash
docker compose ps                 # 查看状态
docker compose logs -f backend    # 跟踪后端日志
docker compose up -d --build      # 改代码后重新构建并启动
docker compose down               # 停止（数据保留在卷中）
```

> 精排模型位于 `models/bge-reranker-v2-m3`（约 2.1GB），以只读方式挂载给容器，未打进镜像。换机器部署时需一并拷贝该目录，否则容器会尝试从 HuggingFace 在线下载。

### 方式二：本地开发

环境要求：Node.js >= 18、Python >= 3.10、PostgreSQL >= 14（启用 pgvector）

```bash
# 1. 只启动数据库和缓存
docker compose up -d postgres redis

# 2. 启动后端
cd backend
python -m venv venv
venv\Scripts\activate          # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env         # 填入 API Key
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 3. 启动前端
cd frontend
npm install
npm run dev
```

### 访问应用

- 前端（Docker）：http://localhost
- 前端（本地开发）：http://localhost:3000
- 后端 API：http://localhost/api
- API 文档：http://localhost/docs


## 部署架构

![部署架构](docs/images/deployment.svg)

## API 文档

### 对话 API

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/conversations` | 创建新对话 |
| GET | `/api/conversations` | 获取对话列表 |
| GET | `/api/conversations/{id}` | 获取对话详情 |
| POST | `/api/conversations/{id}/messages` | 发送消息 |
| DELETE | `/api/conversations/{id}` | 删除对话 |

### 文档 API

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/documents/upload` | 上传文档 |
| GET | `/api/documents` | 获取文档列表 |
| DELETE | `/api/documents/{id}` | 删除文档 |

### 记忆 API

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/memories` | 创建记忆 |
| GET | `/api/memories` | 获取记忆列表 |
| GET | `/api/memories/due` | 获取待复习记忆 |
| POST | `/api/memories/{id}/review` | 复习记忆 |
| DELETE | `/api/memories/{id}` | 删除记忆 |

### 搜索 API

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/search` | 语义搜索 |

## 配置说明

编辑 `.env` 文件配置以下选项：

```env
# 数据库
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/knowledge_assistant

# LLM API Keys (可选)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
DASHSCOPE_API_KEY=your_key_here

# Ollama (本地模型)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# 应用密钥
APP_SECRET=your_secret_key
```

## 许可证

MIT License
