#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 Cogniva 项目文档图表
"""
import os
import sys

# 确保输出编码正确
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

os.makedirs("docs/images", exist_ok=True)

# ============= 1. 系统架构图 =============
architecture_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#f8fafc"/>
      <stop offset="100%" style="stop-color:#e2e8f0"/>
    </linearGradient>
    <linearGradient id="blueGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#3B82F6"/>
      <stop offset="100%" style="stop-color:#2563EB"/>
    </linearGradient>
    <linearGradient id="purpleGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#8B5CF6"/>
      <stop offset="100%" style="stop-color:#7C3AED"/>
    </linearGradient>
    <linearGradient id="cyanGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#06B6D4"/>
      <stop offset="100%" style="stop-color:#0891B2"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#1e293b" flood-opacity="0.1"/>
    </filter>
  </defs>
  
  <!-- Background -->
  <rect width="1200" height="800" fill="url(#bgGrad)"/>
  
  <!-- Title -->
  <text x="600" y="50" text-anchor="middle" font-family="Arial, sans-serif" font-size="28" font-weight="bold" fill="#1e293b">Cogniva 系统架构图</text>
  
  <!-- ========== FRONTEND LAYER ========== -->
  <rect x="50" y="80" width="1100" height="180" rx="12" fill="white" filter="url(#shadow)"/>
  <text x="80" y="110" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#3B82F6">前端层 Frontend</text>
  
  <!-- Next.js Box -->
  <rect x="80" y="130" width="200" height="110" rx="8" fill="url(#blueGrad)"/>
  <text x="180" y="165" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="white">Next.js 14</text>
  <text x="180" y="190" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#bfdbfe">React 18 + TypeScript</text>
  <text x="180" y="215" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#93c5fd">TailwindCSS + Zustand</text>
  
  <!-- Components -->
  <rect x="310" y="130" width="800" height="110" rx="8" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"/>
  <text x="330" y="155" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#475569">组件 Components</text>
  
  <!-- Chat -->
  <rect x="330" y="165" width="110" height="60" rx="6" fill="#EEF2FF"/>
  <text x="385" y="195" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#4338ca">💬 问答</text>
  <text x="385" y="212" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#6366f1">Chat</text>
  
  <!-- Documents -->
  <rect x="460" y="165" width="110" height="60" rx="6" fill="#FEF3C7"/>
  <text x="515" y="195" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#B45309">📄 知识库</text>
  <text x="515" y="212" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#D97706">Documents</text>
  
  <!-- Memory -->
  <rect x="590" y="165" width="110" height="60" rx="6" fill="#D1FAE5"/>
  <text x="645" y="195" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#047857">🧠 记忆</text>
  <text x="645" y="212" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#059669">Memory</text>
  
  <!-- Settings -->
  <rect x="720" y="165" width="110" height="60" rx="6" fill="#E0E7FF"/>
  <text x="775" y="195" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#4338CA">⚙️ 设置</text>
  <text x="775" y="212" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#6366f1">Settings</text>
  
  <!-- Auth -->
  <rect x="850" y="165" width="110" height="60" rx="6" fill="#FCE7F3"/>
  <text x="905" y="195" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#BE185D">🔐 认证</text>
  <text x="905" y="212" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#DB2777">Auth</text>
  
  <!-- ========== CONNECTOR ========== -->
  <path d="M600 260 L600 300 L600 320" stroke="#3B82F6" stroke-width="3" fill="none" marker-end="url(#arrowhead)"/>
  <text x="620" y="295" font-family="Arial, sans-serif" font-size="12" fill="#64748b">REST API</text>
  
  <!-- ========== BACKEND LAYER ========== -->
  <rect x="50" y="320" width="1100" height="200" rx="12" fill="white" filter="url(#shadow)"/>
  <text x="80" y="350" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#8B5CF6">后端层 Backend</text>
  
  <!-- FastAPI Box -->
  <rect x="80" y="370" width="200" height="130" rx="8" fill="url(#purpleGrad)"/>
  <text x="180" y="405" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="white">FastAPI</text>
  <text x="180" y="430" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#ddd6fe">Python 3.10+</text>
  <text x="180" y="455" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#c4b5fd">SQLAlchemy + Pydantic</text>
  <text x="180" y="480" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#c4b5fd">LangChain</text>
  
  <!-- Services -->
  <rect x="310" y="370" width="800" height="130" rx="8" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1"/>
  <text x="330" y="395" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#475569">服务 Services</text>
  
  <!-- Chat Service -->
  <rect x="330" y="410" width="120" height="75" rx="6" fill="#DBEAFE"/>
  <text x="390" y="440" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#1D4ED8">Chat Service</text>
  <text x="390" y="458" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#3B82F6">对话管理</text>
  
  <!-- Document Service -->
  <rect x="470" y="410" width="120" height="75" rx="6" fill="#FEF3C7"/>
  <text x="530" y="440" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#B45309">Doc Service</text>
  <text x="530" y="458" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#D97706">文档处理</text>
  
  <!-- RAG Service -->
  <rect x="610" y="410" width="120" height="75" rx="6" fill="#DCFCE7"/>
  <text x="670" y="440" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#047857">RAG Service</text>
  <text x="670" y="458" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#059669">向量检索</text>
  
  <!-- LLM Gateway -->
  <rect x="750" y="410" width="120" height="75" rx="6" fill="#F3E8FF"/>
  <text x="810" y="440" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#7C3AED">LLM Gateway</text>
  <text x="810" y="458" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#8B5CF6">模型网关</text>
  
  <!-- Memory Service -->
  <rect x="890" y="410" width="120" height="75" rx="6" fill="#CFFAFE"/>
  <text x="950" y="440" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#0E7490">Memory Service</text>
  <text x="950" y="458" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#06B6D4">间隔重复</text>
  
  <!-- ========== CONNECTOR ========== -->
  <path d="M600 520 L600 560" stroke="#8B5CF6" stroke-width="3" fill="none"/>
  <text x="620" y="545" font-family="Arial, sans-serif" font-size="12" fill="#64748b">Database / Cache</text>
  
  <!-- ========== DATA LAYER ========== -->
  <rect x="50" y="560" width="1100" height="180" rx="12" fill="white" filter="url(#shadow)"/>
  <text x="80" y="590" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#06B6D4">数据层 Data Layer</text>
  
  <!-- PostgreSQL -->
  <rect x="80" y="610" width="250" height="110" rx="8" fill="url(#cyanGrad)"/>
  <text x="205" y="650" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="white">PostgreSQL</text>
  <text x="205" y="675" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#cffafe">+ pgvector 扩展</text>
  <text x="205" y="695" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#a5f3fc">向量存储 | 结构化数据</text>
  
  <!-- Redis -->
  <rect x="360" y="610" width="200" height="110" rx="8" fill="#DC2626"/>
  <text x="460" y="650" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="white">Redis</text>
  <text x="460" y="675" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#fee2e2">缓存层</text>
  <text x="460" y="695" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#fecaca">会话缓存 | 限流</text>
  
  <!-- File Storage -->
  <rect x="590" y="610" width="200" height="110" rx="8" fill="#059669"/>
  <text x="690" y="650" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="white">File Storage</text>
  <text x="690" y="675" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#d1fae5">本地文件系统</text>
  <text x="690" y="695" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#a7f3d0">PDF | Word | Excel</text>
  
  <!-- LLM Providers -->
  <rect x="820" y="610" width="290" height="110" rx="8" fill="#7C3AED"/>
  <text x="965" y="640" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="white">LLM Providers</text>
  <text x="965" y="665" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#ddd6fe">DeepSeek | OpenAI | Claude</text>
  <text x="965" y="685" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#ddd6fe">通义千问 | Ollama</text>
  <text x="965" y="705" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#c4b5fd">外部 API</text>
  
  <!-- Footer -->
  <text x="600" y="770" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#94a3b8">Cogniva · 基于 RAG 技术的智能知识问答平台</text>
</svg>'''

with open("docs/images/architecture.svg", "w", encoding="utf-8") as f:
    f.write(architecture_svg)
print("[OK] system architecture diagram generated")

# ============= 2. RAG 流程图 =============
rag_flow_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700">
  <defs>
    <linearGradient id="bgGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#f8fafc"/>
      <stop offset="100%" style="stop-color:#e2e8f0"/>
    </linearGradient>
    <marker id="arrowBlue" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#3B82F6"/>
    </marker>
    <marker id="arrowGreen" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#10B981"/>
    </marker>
    <marker id="arrowPurple" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#8B5CF6"/>
    </marker>
    <filter id="shadow2" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#1e293b" flood-opacity="0.15"/>
    </filter>
  </defs>
  
  <rect width="1000" height="700" fill="url(#bgGrad2)"/>
  
  <!-- Title -->
  <text x="500" y="40" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#1e293b">RAG 检索增强生成流程</text>
  <text x="500" y="65" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#64748b">Retrieval Augmented Generation Workflow</text>
  
  <!-- ============= INgestion Pipeline (Left Side) ============= -->
  <rect x="30" y="90" width="280" height="500" rx="12" fill="white" filter="url(#shadow2)"/>
  <text x="170" y="115" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#059669">📥 文档摄入流程</text>
  <text x="170" y="135" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#64748b">Ingestion Pipeline</text>
  
  <!-- Step 1: Upload -->
  <rect x="50" y="155" width="240" height="55" rx="8" fill="#ECFDF5" stroke="#10B981" stroke-width="2"/>
  <text x="170" y="180" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#047857">📤 上传文档</text>
  <text x="170" y="198" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#059669">PDF, Word, Excel, TXT</text>
  
  <!-- Arrow -->
  <path d="M170 210 L170 235" stroke="#10B981" stroke-width="2" fill="none" marker-end="url(#arrowGreen)"/>
  
  <!-- Step 2: Parse -->
  <rect x="50" y="240" width="240" height="55" rx="8" fill="#ECFDF5" stroke="#10B981" stroke-width="2"/>
  <text x="170" y="265" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#047857">📑 文档解析</text>
  <text x="170" y="283" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#059669">文本提取 · 格式转换</text>
  
  <!-- Arrow -->
  <path d="M170 295 L170 320" stroke="#10B981" stroke-width="2" fill="none" marker-end="url(#arrowGreen)"/>
  
  <!-- Step 3: Chunk -->
  <rect x="50" y="325" width="240" height="55" rx="8" fill="#ECFDF5" stroke="#10B981" stroke-width="2"/>
  <text x="170" y="350" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#047857">✂️ 文本分块</text>
  <text x="170" y="368" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#059669">chunk_size=500, overlap=50</text>
  
  <!-- Arrow -->
  <path d="M170 380 L170 405" stroke="#10B981" stroke-width="2" fill="none" marker-end="url(#arrowGreen)"/>
  
  <!-- Step 4: Embed -->
  <rect x="50" y="410" width="240" height="55" rx="8" fill="#ECFDF5" stroke="#10B981" stroke-width="2"/>
  <text x="170" y="435" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#047857">🧮 向量化</text>
  <text x="170" y="453" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#059669">Sentence Transformers</text>
  
  <!-- Arrow -->
  <path d="M170 465 L170 490" stroke="#10B981" stroke-width="2" fill="none" marker-end="url(#arrowGreen)"/>
  
  <!-- Step 5: Store -->
  <rect x="50" y="495" width="240" height="55" rx="8" fill="#10B981"/>
  <text x="170" y="520" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="white">💾 存入向量库</text>
  <text x="170" y="538" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#a7f3d0">pgvector</text>
  
  <!-- ============= Query Pipeline (Right Side) ============= -->
  <rect x="340" y="90" width="300" height="500" rx="12" fill="white" filter="url(#shadow2)"/>
  <text x="490" y="115" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#3B82F6">🔍 查询流程</text>
  <text x="490" y="135" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#64748b">Query Pipeline</text>
  
  <!-- Step 1: Question -->
  <rect x="360" y="155" width="260" height="55" rx="8" fill="#EFF6FF" stroke="#3B82F6" stroke-width="2"/>
  <text x="490" y="180" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#1D4ED8">❓ 用户提问</text>
  <text x="490" y="198" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#3B82F6">"什么是机器学习？"</text>
  
  <!-- Arrow -->
  <path d="M490 210 L490 235" stroke="#3B82F6" stroke-width="2" fill="none" marker-end="url(#arrowBlue)"/>
  
  <!-- Step 2: Embed Query -->
  <rect x="360" y="240" width="260" height="55" rx="8" fill="#EFF6FF" stroke="#3B82F6" stroke-width="2"/>
  <text x="490" y="265" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#1D4ED8">🔮 向量化问题</text>
  <text x="490" y="283" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#3B82F6">生成查询向量</text>
  
  <!-- Arrow -->
  <path d="M490 295 L490 320" stroke="#3B82F6" stroke-width="2" fill="none" marker-end="url(#arrowBlue)"/>
  
  <!-- Step 3: Vector Search -->
  <rect x="360" y="325" width="260" height="55" rx="8" fill="#EFF6FF" stroke="#3B82F6" stroke-width="2"/>
  <text x="490" y="350" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#1D4ED8">🔍 向量检索</text>
  <text x="490" y="368" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#3B82F6">top_k=5 · 余弦相似度</text>
  
  <!-- Arrow -->
  <path d="M490 380 L490 405" stroke="#3B82F6" stroke-width="2" fill="none" marker-end="url(#arrowBlue)"/>
  
  <!-- Step 4: Get Chunks -->
  <rect x="360" y="410" width="260" height="55" rx="8" fill="#EFF6FF" stroke="#3B82F6" stroke-width="2"/>
  <text x="490" y="435" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#1D4ED8">📄 获取相关文档块</text>
  <text x="490" y="453" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#3B82F6">相关段落 + 来源信息</text>
  
  <!-- ============= Generation Pipeline (Far Right) ============= -->
  <rect x="670" y="90" width="300" height="300" rx="12" fill="white" filter="url(#shadow2)"/>
  <text x="820" y="115" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#8B5CF6">✨ 生成流程</text>
  <text x="820" y="135" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#64748b">Generation Pipeline</text>
  
  <!-- Step 1: Assemble -->
  <rect x="690" y="155" width="260" height="55" rx="8" fill="#F5F3FF" stroke="#8B5CF6" stroke-width="2"/>
  <text x="820" y="180" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#7C3AED">🔧 组装上下文</text>
  <text x="820" y="198" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#8B5CF6">问题 + 检索结果 → Prompt</text>
  
  <!-- Arrow -->
  <path d="M820 210 L820 235" stroke="#8B5CF6" stroke-width="2" fill="none" marker-end="url(#arrowPurple)"/>
  
  <!-- Step 2: LLM -->
  <rect x="690" y="240" width="260" height="55" rx="8" fill="#F5F3FF" stroke="#8B5CF6" stroke-width="2"/>
  <text x="820" y="265" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#7C3AED">🤖 LLM 处理</text>
  <text x="820" y="283" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#8B5CF6">DeepSeek / Claude / Ollama</text>
  
  <!-- Arrow -->
  <path d="M820 295 L820 320" stroke="#8B5CF6" stroke-width="2" fill="none" marker-end="url(#arrowPurple)"/>
  
  <!-- Step 3: Generate -->
  <rect x="690" y="325" width="260" height="55" rx="8" fill="#8B5CF6"/>
  <text x="820" y="350" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="white">💬 生成回答</text>
  <text x="820" y="368" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#e9d5ff">+ 引用来源标注</text>
  
  <!-- ============= Citation Flow ============= -->
  <rect x="670" y="410" width="300" height="180" rx="12" fill="white" filter="url(#shadow2)"/>
  <text x="820" y="435" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#F59E0B">📚 引用来源</text>
  
  <!-- Citation Example -->
  <rect x="690" y="450" width="260" height="120" rx="6" fill="#FFFBEB" stroke="#F59E0B" stroke-width="1"/>
  <text x="705" y="475" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#B45309">来源 1: 机器学习入门指南.pdf</text>
  <text x="705" y="495" font-family="Arial, sans-serif" font-size="9" fill="#D97706">chunk_id: 42 | 相似度: 0.92</text>
  <text x="705" y="520" font-family="Arial, sans-serif" font-size="9" fill="#64748b">"机器学习是人工智能的一个分支..."</text>
  <text x="705" y="540" font-family="Arial, sans-serif" font-size="9" fill="#64748b">"它通过算法让计算机从数据中学习..."</text>
  <text x="705" y="560" font-family="Arial, sans-serif" font-size="9" fill="#64748b">"...无需明确编程即可自动改进"</text>
  
  <!-- Arrow from Retrieval to Context -->
  <path d="M620 350 L690 350 L690 410" stroke="#3B82F6" stroke-width="2" stroke-dasharray="5,3" fill="none"/>
  <text x="655" y="340" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#64748b">检索结果</text>
  
  <!-- Footer -->
  <text x="500" y="680" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#94a3b8">Cogniva RAG 工作流程 · 支持 DeepSeek · Claude · 通义千问 · Ollama</text>
</svg>'''

with open("docs/images/rag-flow.svg", "w", encoding="utf-8") as f:
    f.write(rag_flow_svg)
print("[OK] RAG flow diagram generated")

# ============= 3. 项目结构图 =============
structure_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 650">
  <defs>
    <linearGradient id="bgGrad3" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#f8fafc"/>
      <stop offset="100%" style="stop-color:#e2e8f0"/>
    </linearGradient>
    <filter id="shadow3" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#1e293b" flood-opacity="0.1"/>
    </filter>
  </defs>
  
  <rect width="900" height="650" fill="url(#bgGrad3)"/>
  
  <!-- Title -->
  <text x="450" y="35" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#1e293b">项目目录结构</text>
  <text x="450" y="58" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#64748b">Project Structure</text>
  
  <!-- Root -->
  <rect x="300" y="75" width="300" height="40" rx="6" fill="#1E293B"/>
  <text x="450" y="100" text-anchor="middle" font-family="monospace" font-size="14" fill="white">📁 knowledge-assistant/</text>
  
  <!-- Root Level Files -->
  <rect x="50" y="75" width="220" height="40" rx="4" fill="#F1F5F9" stroke="#CBD5E1"/>
  <text x="160" y="100" text-anchor="middle" font-family="monospace" font-size="11" fill="#475569">📄 README.md</text>
  
  <rect x="630" y="75" width="220" height="40" rx="4" fill="#F1F5F9" stroke="#CBD5E1"/>
  <text x="740" y="100" text-anchor="middle" font-family="monospace" font-size="11" fill="#475569">📄 docker-compose.yml</text>
  
  <!-- Connection lines to children -->
  <path d="M300 115 L300 130" stroke="#94A3B8" stroke-width="1"/>
  <path d="M450 115 L450 130" stroke="#94A3B8" stroke-width="1"/>
  <path d="M600 115 L600 130" stroke="#94A3B8" stroke-width="1"/>
  <path d="M300 130 L600 130" stroke="#94A3B8" stroke-width="1"/>
  <path d="M300 130 L300 150" stroke="#94A3B8" stroke-width="1"/>
  <path d="M600 130 L600 150" stroke="#94A3B8" stroke-width="1"/>
  
  <!-- ========== BACKEND ========== -->
  <rect x="100" y="150" width="300" height="380" rx="8" fill="white" filter="url(#shadow3)"/>
  <rect x="100" y="150" width="300" height="35" rx="8" fill="#3B82F6"/>
  <rect x="100" y="175" width="300" height="10" fill="#3B82F6"/>
  <text x="250" y="173" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="white">📂 backend/</text>
  
  <!-- api folder -->
  <rect x="115" y="195" width="130" height="25" rx="4" fill="#EFF6FF" stroke="#3B82F6"/>
  <text x="180" y="212" text-anchor="middle" font-family="monospace" font-size="10" fill="#1D4ED8">📂 api/</text>
  
  <text x="260" y="210" font-family="monospace" font-size="9" fill="#64748B">chat.py</text>
  <text x="260" y="222" font-family="monospace" font-size="9" fill="#64748B">documents.py</text>
  <text x="260" y="234" font-family="monospace" font-size="9" fill="#64748B">memory.py</text>
  <text x="260" y="246" font-family="monospace" font-size="9" fill="#64748B">search.py</text>
  <text x="260" y="258" font-family="monospace" font-size="9" fill="#64748B">auth.py</text>
  <text x="260" y="270" font-family="monospace" font-size="9" fill="#64748B">settings.py</text>
  
  <!-- core folder -->
  <rect x="115" y="280" width="130" height="25" rx="4" fill="#EFF6FF" stroke="#3B82F6"/>
  <text x="180" y="297" text-anchor="middle" font-family="monospace" font-size="10" fill="#1D4ED8">📂 core/</text>
  
  <text x="260" y="295" font-family="monospace" font-size="9" fill="#64748B">config.py</text>
  <text x="260" y="307" font-family="monospace" font-size="9" fill="#64748B">database.py</text>
  <text x="260" y="319" font-family="monospace" font-size="9" fill="#64748B">auth.py</text>
  
  <!-- services folder -->
  <rect x="115" y="328" width="130" height="25" rx="4" fill="#EFF6FF" stroke="#3B82F6"/>
  <text x="180" y="345" text-anchor="middle" font-family="monospace" font-size="10" fill="#1D4ED8">📂 services/</text>
  
  <text x="260" y="343" font-family="monospace" font-size="9" fill="#64748B">rag_service.py</text>
  <text x="260" y="355" font-family="monospace" font-size="9" fill="#64748B">chat_service.py</text>
  <text x="260" y="367" font-family="monospace" font-size="9" fill="#64748B">document_service.py</text>
  <text x="260" y="379" font-family="monospace" font-size="9" fill="#64748B">memory_service.py</text>
  <text x="260" y="391" font-family="monospace" font-size="9" fill="#64748B">llm_gateway.py</text>
  
  <!-- models folder -->
  <rect x="115" y="400" width="130" height="25" rx="4" fill="#EFF6FF" stroke="#3B82F6"/>
  <text x="180" y="417" text-anchor="middle" font-family="monospace" font-size="10" fill="#1D4ED8">📂 models/</text>
  
  <text x="260" y="415" font-family="monospace" font-size="9" fill="#64748B">models.py</text>
  
  <!-- Root files -->
  <text x="180" y="445" text-anchor="middle" font-family="monospace" font-size="10" fill="#475569">main.py</text>
  <text x="180" y="460" text-anchor="middle" font-family="monospace" font-size="10" fill="#475569">requirements.txt</text>
  <text x="180" y="475" text-anchor="middle" font-family="monospace" font-size="10" fill="#475569">Dockerfile</text>
  
  <!-- ========== FRONTEND ========== -->
  <rect x="500" y="150" width="300" height="380" rx="8" fill="white" filter="url(#shadow3)"/>
  <rect x="500" y="150" width="300" height="35" rx="8" fill="#8B5CF6"/>
  <rect x="500" y="175" width="300" height="10" fill="#8B5CF6"/>
  <text x="650" y="173" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="white">📂 frontend/</text>
  
  <!-- app folder -->
  <rect x="515" y="195" width="130" height="25" rx="4" fill="#F5F3FF" stroke="#8B5CF6"/>
  <text x="580" y="212" text-anchor="middle" font-family="monospace" font-size="10" fill="#7C3AED">📂 app/</text>
  
  <text x="660" y="210" font-family="monospace" font-size="9" fill="#64748B">page.tsx</text>
  <text x="660" y="222" font-family="monospace" font-size="9" fill="#64748B">📂 chat/</text>
  <text x="660" y="234" font-family="monospace" font-size="9" fill="#64748B">📂 documents/</text>
  <text x="660" y="246" font-family="monospace" font-size="9" fill="#64748B">📂 memory/</text>
  <text x="660" y="258" font-family="monospace" font-size="9" fill="#64748B">📂 settings/</text>
  <text x="660" y="270" font-family="monospace" font-size="9" fill="#64748B">📂 auth/</text>
  
  <!-- components folder -->
  <rect x="515" y="280" width="130" height="25" rx="4" fill="#F5F3FF" stroke="#8B5CF6"/>
  <text x="580" y="297" text-anchor="middle" font-family="monospace" font-size="10" fill="#7C3AED">📂 components/</text>
  
  <text x="660" y="295" font-family="monospace" font-size="9" fill="#64748B">📂 chat/</text>
  <text x="660" y="307" font-family="monospace" font-size="9" fill="#64748B">📂 documents/</text>
  <text x="660" y="319" font-family="monospace" font-size="9" fill="#64748B">📂 memory/</text>
  <text x="660" y="331" font-family="monospace" font-size="9" fill="#64748B">📂 layout/</text>
  <text x="660" y="343" font-family="monospace" font-size="9" fill="#64748B">📂 ui/</text>
  
  <!-- stores folder -->
  <rect x="515" y="352" width="130" height="25" rx="4" fill="#F5F3FF" stroke="#8B5CF6"/>
  <text x="580" y="369" text-anchor="middle" font-family="monospace" font-size="10" fill="#7C3AED">📂 stores/</text>
  
  <text x="660" y="367" font-family="monospace" font-size="9" fill="#64748B">chatStore.ts</text>
  <text x="660" y="379" font-family="monospace" font-size="9" fill="#64748B">memoryStore.ts</text>
  <text x="660" y="391" font-family="monospace" font-size="9" fill="#64748B">documentStore.ts</text>
  
  <!-- Root files -->
  <text x="580" y="420" text-anchor="middle" font-family="monospace" font-size="10" fill="#475569">package.json</text>
  <text x="580" y="435" text-anchor="middle" font-family="monospace" font-size="10" fill="#475569">next.config.js</text>
  <text x="580" y="450" text-anchor="middle" font-family="monospace" font-size="10" fill="#475569">tailwind.config.js</text>
  <text x="580" y="465" text-anchor="middle" font-family="monospace" font-size="10" fill="#475569">tsconfig.json</text>
  <text x="580" y="480" text-anchor="middle" font-family="monospace" font-size="10" fill="#475569">Dockerfile</text>
  
  <!-- ========== Config Files ========== -->
  <rect x="200" y="545" width="500" height="80" rx="8" fill="white" filter="url(#shadow3)"/>
  <text x="450" y="565" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#64748b">配置文件 Config Files</text>
  
  <rect x="220" y="575" width="140" height="35" rx="4" fill="#FEF3C7" stroke="#F59E0B"/>
  <text x="290" y="598" text-anchor="middle" font-family="monospace" font-size="10" fill="#B45309">.env.example</text>
  
  <rect x="380" y="575" width="160" height="35" rx="4" fill="#FEF3C7" stroke="#F59E0B"/>
  <text x="460" y="598" text-anchor="middle" font-family="monospace" font-size="10" fill="#B45309">.env.docker.example</text>
  
  <rect x="560" y="575" width="120" height="35" rx="4" fill="#F1F5F9" stroke="#CBD5E1"/>
  <text x="620" y="598" text-anchor="middle" font-family="monospace" font-size="10" fill="#64748B">.gitignore</text>
  
  <!-- Footer -->
  <text x="450" y="630" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#94a3b8">FastAPI + Next.js + PostgreSQL + pgvector</text>
</svg>'''

with open("docs/images/project-structure.svg", "w", encoding="utf-8") as f:
    f.write(structure_svg)
print("[OK] project structure diagram generated")

# ============= 4. 部署架构图 =============
deploy_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 600">
  <defs>
    <linearGradient id="bgGrad4" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#f8fafc"/>
      <stop offset="100%" style="stop-color:#e2e8f0"/>
    </linearGradient>
    <linearGradient id="dockerGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#2496ED"/>
      <stop offset="100%" style="stop-color:#1D63ED"/>
    </linearGradient>
    <filter id="shadow4" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="3" stdDeviation="6" flood-color="#1e293b" flood-opacity="0.1"/>
    </filter>
  </defs>
  
  <rect width="1000" height="600" fill="url(#bgGrad4)"/>
  
  <!-- Title -->
  <text x="500" y="35" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#1e293b">Docker 部署架构</text>
  <text x="500" y="58" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#64748b">Docker Deployment Architecture</text>
  
  <!-- Docker Compose Box -->
  <rect x="50" y="80" width="900" height="480" rx="12" fill="white" stroke="#2496ED" stroke-width="3" filter="url(#shadow4)"/>
  <rect x="50" y="80" width="900" height="40" rx="12" fill="url(#dockerGrad)"/>
  <rect x="50" y="110" width="900" height="10" fill="url(#dockerGrad)"/>
  <text x="500" y="107" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="white">🐳 Docker Compose</text>
  
  <!-- ========== Services ========== -->
  
  <!-- Frontend Service -->
  <rect x="80" y="140" width="200" height="180" rx="8" fill="#F5F3FF" stroke="#8B5CF6" stroke-width="2"/>
  <rect x="80" y="140" width="200" height="35" rx="8" fill="#8B5CF6"/>
  <rect x="80" y="165" width="200" height="10" fill="#8B5CF6"/>
  <text x="180" y="163" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="white">🌐 frontend</text>
  
  <text x="180" y="200" text-anchor="middle" font-family="monospace" font-size="11" fill="#7C3AED">Next.js 14</text>
  <text x="180" y="220" text-anchor="middle" font-family="monospace" font-size="10" fill="#64748B">Port: 3000</text>
  <text x="180" y="245" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#475569">http://localhost:3000</text>
  <rect x="100" y="260" width="160" height="40" rx="4" fill="#E0E7FF"/>
  <text x="180" y="283" text-anchor="middle" font-family="monospace" font-size="9" fill="#4338CA">NEXT_PUBLIC_API_URL</text>
  
  <!-- Backend Service -->
  <rect x="300" y="140" width="200" height="180" rx="8" fill="#EFF6FF" stroke="#3B82F6" stroke-width="2"/>
  <rect x="300" y="140" width="200" height="35" rx="8" fill="#3B82F6"/>
  <rect x="300" y="165" width="200" height="10" fill="#3B82F6"/>
  <text x="400" y="163" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="white">⚡ backend</text>
  
  <text x="400" y="200" text-anchor="middle" font-family="monospace" font-size="11" fill="#1D4ED8">FastAPI</text>
  <text x="400" y="220" text-anchor="middle" font-family="monospace" font-size="10" fill="#64748B">Port: 8000</text>
  <text x="400" y="245" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#475569">http://localhost:8000</text>
  <rect x="320" y="260" width="160" height="40" rx="4" fill="#DBEAFE"/>
  <text x="400" y="283" text-anchor="middle" font-family="monospace" font-size="9" fill="#1D4ED8">LLM APIs (DeepSeek...)</text>
  
  <!-- PostgreSQL Service -->
  <rect x="520" y="140" width="200" height="180" rx="8" fill="#ECFDF5" stroke="#10B981" stroke-width="2"/>
  <rect x="520" y="140" width="200" height="35" rx="8" fill="#10B981"/>
  <rect x="520" y="165" width="200" height="10" fill="#10B981"/>
  <text x="620" y="163" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="white">🗄️ postgres</text>
  
  <text x="620" y="200" text-anchor="middle" font-family="monospace" font-size="11" fill="#047857">pgvector/pgvector</text>
  <text x="620" y="220" text-anchor="middle" font-family="monospace" font-size="10" fill="#64748B">Port: 5432</text>
  <text x="620" y="245" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#475569">knowledge_assistant</text>
  <rect x="540" y="260" width="160" height="40" rx="4" fill="#D1FAE5"/>
  <text x="620" y="283" text-anchor="middle" font-family="monospace" font-size="9" fill="#047857">向量存储 + 结构化数据</text>
  
  <!-- Redis Service -->
  <rect x="740" y="140" width="180" height="180" rx="8" fill="#FEF2F2" stroke="#EF4444" stroke-width="2"/>
  <rect x="740" y="140" width="180" height="35" rx="8" fill="#EF4444"/>
  <rect x="740" y="165" width="180" height="10" fill="#EF4444"/>
  <text x="830" y="163" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="white">🔴 redis</text>
  
  <text x="830" y="200" text-anchor="middle" font-family="monospace" font-size="11" fill="#DC2626">Redis 7 Alpine</text>
  <text x="830" y="220" text-anchor="middle" font-family="monospace" font-size="10" fill="#64748B">Port: 6379</text>
  <text x="830" y="245" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#475569">缓存层</text>
  <rect x="760" y="260" width="140" height="40" rx="4" fill="#FEE2E2"/>
  <text x="830" y="283" text-anchor="middle" font-family="monospace" font-size="9" fill="#DC2626">会话缓存 | 限流</text>
  
  <!-- ========== Connections ========== -->
  <!-- Frontend -> Backend -->
  <path d="M280 230 L300 230" stroke="#8B5CF6" stroke-width="2" fill="none" marker-end="url(#arr1)"/>
  <text x="290" y="220" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#64748B">HTTP</text>
  
  <!-- Backend -> PostgreSQL -->
  <path d="M500 230 L520 230" stroke="#3B82F6" stroke-width="2" fill="none"/>
  <text x="510" y="220" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#64748B">SQL</text>
  
  <!-- Backend -> Redis -->
  <path d="M500 250 L740 250" stroke="#3B82F6" stroke-width="2" fill="none"/>
  <text x="620" y="240" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#64748B">Cache</text>
  
  <!-- ========== Network Info ========== -->
  <rect x="80" y="340" width="840" height="200" rx="8" fill="#F8FAFC" stroke="#E2E8F0"/>
  <text x="100" y="365" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#1E293B">📋 启动命令</text>
  
  <rect x="100" y="380" width="800" height="40" rx="4" fill="#1E293B"/>
  <text x="500" y="405" text-anchor="middle" font-family="monospace" font-size="12" fill="#10B981">docker-compose up -d</text>
  
  <text x="100" y="450" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#1E293B">🌐 访问地址</text>
  
  <rect x="100" y="465" width="150" height="55" rx="4" fill="#F5F3FF"/>
  <text x="175" y="488" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#7C3AED">前端应用</text>
  <text x="175" y="505" text-anchor="middle" font-family="monospace" font-size="10" fill="#8B5CF6">localhost:3000</text>
  
  <rect x="270" y="465" width="150" height="55" rx="4" fill="#EFF6FF"/>
  <text x="345" y="488" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#1D4ED8">API 文档</text>
  <text x="345" y="505" text-anchor="middle" font-family="monospace" font-size="10" fill="#3B82F6">localhost:8000/docs</text>
  
  <rect x="440" y="465" width="150" height="55" rx="4" fill="#ECFDF5"/>
  <text x="515" y="488" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#047857">数据库</text>
  <text x="515" y="505" text-anchor="middle" font-family="monospace" font-size="10" fill="#10B981">localhost:5432</text>
  
  <rect x="610" y="465" width="150" height="55" rx="4" fill="#FEF2F2"/>
  <text x="685" y="488" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#DC2626">Redis</text>
  <text x="685" y="505" text-anchor="middle" font-family="monospace" font-size="10" fill="#EF4444">localhost:6379</text>
  
  <!-- Footer -->
  <text x="500" y="570" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#94a3b8">一键部署 · 数据持久化 · 自动重启</text>
</svg>'''

with open("docs/images/deployment.svg", "w", encoding="utf-8") as f:
    f.write(deploy_svg)
print("[OK] deployment diagram generated")

print("\n[SUCCESS] All diagrams generated to docs/images/")
print("   - architecture.svg")
print("   - rag-flow.svg")
print("   - project-structure.svg")
print("   - deployment.svg")
