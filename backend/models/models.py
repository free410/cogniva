import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, Float, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)
    name = Column(String(100), nullable=True)
    avatar = Column(String(500), nullable=True)
    settings = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    conversations = relationship("Conversation", back_populates="user")
    documents = relationship("Document", back_populates="user")
    memories = relationship("Memory", back_populates="user")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), default="新对话")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON, default=dict)
    evidence_ = Column("evidence", JSON, nullable=True)  # 存储证据报告
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")
    citations = relationship("Citation", back_populates="message", cascade="all, delete-orphan")

    @property
    def extra_metadata(self):
        return self.metadata_

    @extra_metadata.setter
    def extra_metadata(self, value):
        self.metadata_ = value

    @property
    def evidence(self):
        return self.evidence_

    @evidence.setter
    def evidence(self, value):
        self.evidence_ = value


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="documents")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

    @property
    def extra_metadata(self):
        return self.metadata_

    @extra_metadata.setter
    def extra_metadata(self, value):
        self.metadata_ = value


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    token_count = Column(Integer, default=0)
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="chunks")
    vector = relationship("Vector", back_populates="chunk", uselist=False, cascade="all, delete-orphan")
    citations = relationship("Citation", back_populates="chunk", cascade="all, delete-orphan")
    
    @property
    def extra_metadata(self):
        return self.metadata_

    @extra_metadata.setter
    def extra_metadata(self, value):
        self.metadata_ = value


class Vector(Base):
    __tablename__ = "vectors"

    chunk_id = Column(UUID(as_uuid=True), ForeignKey("chunks.id"), primary_key=True)
    embedding = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    chunk = relationship("Chunk", back_populates="vector")


class Citation(Base):
    __tablename__ = "citations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"), nullable=False)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("chunks.id"), nullable=False)
    similarity = Column(Float, nullable=False)
    reranker_score = Column(Float, nullable=True)  # Reranker原始分数
    vector_score = Column(Float, nullable=True)    # 向量相似度分数
    bm25_score = Column(Float, nullable=True)     # BM25分数
    keyword_score = Column(Float, nullable=True)   # 关键词匹配分数
    matched_terms = Column(JSON, nullable=True)    # 命中的关键词列表
    rank = Column(Integer, nullable=True)           # 排序名次
    chunk_content = Column(Text, nullable=True)     # 块内容预览
    chunk_index = Column(Integer, nullable=True)   # 块在文档中的索引
    # 意图相关性验证字段
    intent_match_ratio = Column(Float, nullable=True)  # 意图匹配比例
    topic_match = Column(Boolean, nullable=True)      # 主题是否匹配
    entity_match_score = Column(Float, nullable=True)  # 实体匹配分数
    term_match_score = Column(Float, nullable=True)    # 术语匹配分数
    matched_entities = Column(JSON, nullable=True)    # 命中的实体列表
    phrase_score = Column(Float, nullable=True)      # 精确短语匹配分数
    created_at = Column(DateTime, default=datetime.utcnow)

    message = relationship("Message", back_populates="citations")
    chunk = relationship("Chunk", back_populates="citations")


class Memory(Base):
    __tablename__ = "memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), default="general")
    importance = Column(Float, default=0.5)
    review_count = Column(Integer, default=0)
    next_review = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    extra_metadata = Column(JSON, nullable=True, default=dict)

    user = relationship("User", back_populates="memories")