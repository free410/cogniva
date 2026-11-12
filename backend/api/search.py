from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from core import get_db
from models import User
from api.auth import require_auth

router = APIRouter(prefix="/api", tags=["search"])


class SearchResult(BaseModel):
    chunk_id: str
    content: str
    document_id: str
    similarity: float
    metadata: dict


@router.post("/search")
async def search(
    query: str,
    top_k: Optional[int] = 5,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth)
):
    """语义搜索"""
    from services import RAGService
    
    rag = RAGService(db)
    results = await rag.retrieve(query, top_k=top_k, user_id=user.id)
    
    return {"results": results, "query": query}


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "Cogniva API is running"}