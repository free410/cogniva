from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from core import get_db
from models import User, Document, Chunk
from services import DocumentService, ChatService, MemoryService
from api.auth import require_auth
from core.cache import cache_incr

router = APIRouter(prefix="/api", tags=["documents"])


async def _process_document_in_background(
    document_id: str,
    chunk_strategy: str,
    chunk_size: int,
    overlap: int
):
    """后台上传处理：使用独立会话，避免依赖请求生命周期"""
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        service = DocumentService(db)
        document = await service.process_document_chunks(
            document_id,
            chunk_size=chunk_size,
            overlap=overlap,
            chunk_strategy=chunk_strategy
        )
        # 语料变化后使该用户的检索缓存失效
        if document and document.status == "completed":
            await cache_incr(f"rag:corpus:{document.user_id}")
    except Exception as e:
        print(f"Document processing failed: {e}")
    finally:
        db.close()


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    file_path: str
    status: str
    metadata: Optional[dict] = None
    created_at: str


class DocumentDetailResponse(DocumentResponse):
    chunk_count: int
    content_preview: Optional[str] = None


@router.post("/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    chunk_strategy: str = Query("recursive", description="切块策略: recursive, semantic, markdown, sliding_window, hybrid"),
    chunk_size: int = Query(None, description="块大小（字符数）"),
    overlap: int = Query(None, description="重叠大小（字符数）"),
    db: Session = Depends(get_db),
    user: User = Depends(require_auth)
):
    user_id = user.id

    service = DocumentService(db)
    try:
        document = await service.create_document(user_id, file, chunk_strategy)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 解析、切块、embedding 移到后台，避免长时间占用请求
    background_tasks.add_task(
        _process_document_in_background,
        str(document.id),
        chunk_strategy,
        chunk_size,
        overlap
    )

    return {
        "id": str(document.id),
        "filename": document.filename,
        "status": document.status,
        "message": "文档上传成功，正在处理中...",
        "chunk_strategy": chunk_strategy,
        "chunk_count": document.extra_metadata.get("chunk_count") if document.extra_metadata else None
    }


@router.get("/documents")
async def list_documents(
    db: Session = Depends(get_db),
    user: User = Depends(require_auth)
):
    user_id = user.id
    service = DocumentService(db)
    documents = await service.get_documents(user_id)

    return [{
        "id": str(doc.id),
        "filename": doc.filename,
        "file_type": doc.file_type,
        "file_size": doc.file_size,
        "status": doc.status,
        "metadata": doc.extra_metadata,
        "created_at": doc.created_at.isoformat()
    } for doc in documents]


@router.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth)
):
    user_id = user.id
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # 只查计数和首个分块，避免懒加载把全部 chunk 正文读入内存
    chunk_count = db.query(Chunk).filter(Chunk.document_id == document.id).count()
    first_chunk = db.query(Chunk).filter(
        Chunk.document_id == document.id
    ).order_by(Chunk.chunk_index).first()

    return {
        "id": str(document.id),
        "filename": document.filename,
        "file_type": document.file_type,
        "file_size": document.file_size,
        "file_path": document.file_path,
        "status": document.status,
        "metadata": document.extra_metadata,
        "created_at": document.created_at.isoformat(),
        "chunk_count": chunk_count,
        "content_preview": first_chunk.content[:500] if first_chunk else None
    }


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth)
):
    user_id = user.id
    service = DocumentService(db)
    success = await service.delete_document(document_id, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Document not found")

    # 语料变化后使该用户的检索缓存失效
    await cache_incr(f"rag:corpus:{user_id}")

    return {"message": "Document deleted successfully"}
