# Cogniva · 智能知识问答平台

![Cogniva](docs/images/architecture.svg)

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

### 1. 环境要求

- Node.js >= 18
- Python >= 3.10
- PostgreSQL >= 14 (需启用 pgvector 扩展)
- Docker (用于数据库)

### 2. 启动数据库

```bash
docker-compose up -d
```

### 3. 配置后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制并编辑环境变量
cp ../.env.example .env
```

### 4. 启动后端

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 安装并启动前端

```bash
cd frontend

npm install
npm run dev
```

### 6. 访问应用

- 前端：http://localhost:3000
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

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
