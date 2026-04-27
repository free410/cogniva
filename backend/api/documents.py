from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from core import get_db
from models import User, Document
from services import DocumentService, ChatService, MemoryService

router = APIRouter(prefix="/api", tags=["documents"])

DEFAULT_USER_EMAIL = "default@local"


def get_default_user_id(db: Session) -> UUID:
    user = db.query(User).filter(User.email == DEFAULT_USER_EMAIL).first()
    if not user:
        user = User(email=DEFAULT_USER_EMAIL, username="default_user", name="Default User", settings={})
        db.add(user)
        db.commit()
        db.refresh(user)
    return user.id


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
    file: UploadFile = File(...),
    chunk_strategy: str = Query("recursive", description="切块策略: recursive, semantic, markdown, sliding_window, hybrid"),
    chunk_size: int = Query(None, description="块大小（字符数）"),
    overlap: int = Query(None, description="重叠大小（字符数）"),
    db: Session = Depends(get_db)
):
    user_id = get_default_user_id(db)

    service = DocumentService(db)
    document = await service.process_document(
        user_id=user_id,
        file=file,
        chunk_strategy=chunk_strategy,
        chunk_size=chunk_size,
        overlap=overlap
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
    db: Session = Depends(get_db)
):
    user_id = get_default_user_id(db)
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
    db: Session = Depends(get_db)
):
    user_id = get_default_user_id(db)
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": str(document.id),
        "filename": document.filename,
        "file_type": document.file_type,
        "file_size": document.file_size,
        "file_path": document.file_path,
        "status": document.status,
        "metadata": document.extra_metadata,
        "created_at": document.created_at.isoformat(),
        "chunk_count": len(document.chunks) if document.chunks else 0,
        "content_preview": document.chunks[0].content[:500] if document.chunks and document.chunks[0] else None
    }


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    user_id = get_default_user_id(db)
    service = DocumentService(db)
    success = await service.delete_document(document_id, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"message": "Document deleted successfully"}
