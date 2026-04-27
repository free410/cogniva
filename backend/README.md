# Cogniva 后端服务

基于 FastAPI 的智能知识问答平台后端服务。

## 功能特性

- **RAG 检索增强生成**：基于向量检索的智能问答
- **多 LLM 支持**：OpenAI、Claude、通义千问、Ollama
- **文档处理**：支持 PDF、Word、Excel、TXT 等格式
- **间隔重复学习**：基于遗忘曲线的记忆系统

## 快速开始

### 1. 环境准备

```bash
# 启动 PostgreSQL (使用 Docker)
docker-compose up -d

# 或确保本地 PostgreSQL 已安装并运行
```

### 2. 安装依赖

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp ../.env.example .env
# 编辑 .env 配置数据库和 API Keys
```

### 4. 启动服务

```bash
python main.py
# 或
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API 文档

启动服务后访问: http://localhost:8000/docs

## 主要 API 端点

### 文档管理
- `POST /api/documents/upload` - 上传文档
- `GET /api/documents` - 获取文档列表
- `DELETE /api/documents/{id}` - 删除文档

### 对话
- `POST /api/conversations` - 创建对话
- `GET /api/conversations` - 获取对话列表
- `POST /api/conversations/{id}/messages` - 发送消息
- `DELETE /api/conversations/{id}` - 删除对话

### 记忆
- `POST /api/memories` - 创建记忆
- `GET /api/memories` - 获取记忆列表
- `GET /api/memories/due` - 获取待复习记忆
- `POST /api/memories/{id}/review` - 复习记忆

### 搜索
- `POST /api/search` - 语义搜索

## 技术栈

- FastAPI
- SQLAlchemy
- PostgreSQL + pgvector
- LangChain
- Sentence Transformers