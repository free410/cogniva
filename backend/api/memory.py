from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from core import get_db
from services import MemoryService
from models import User
from uuid import UUID

router = APIRouter(prefix="/api", tags=["memory"])

DEFAULT_USER_EMAIL = "default@local"


def get_default_user_id(db: Session) -> UUID:
    user = db.query(User).filter(User.email == DEFAULT_USER_EMAIL).first()
    if not user:
        user = User(email=DEFAULT_USER_EMAIL, username="default_user", name="Default User", settings={})
        db.add(user)
        db.commit()
        db.refresh(user)
    return user.id


class MemoryCreate(BaseModel):
    content: str
    category: Optional[str] = "general"
    importance: Optional[float] = 0.5


class MemoryUpdate(BaseModel):
    content: Optional[str] = None
    category: Optional[str] = None
    importance: Optional[float] = None


class MemoryResponse(BaseModel):
    id: str
    content: str
    category: str
    importance: float
    review_count: int
    next_review: Optional[str]
    created_at: str
    extra_metadata: Optional[dict] = None


class ReviewResponse(BaseModel):
    id: str
    review_count: int
    next_review: str
    quality_desc: str


@router.post("/memories")
async def create_memory(
    data: MemoryCreate,
    db: Session = Depends(get_db)
):
    user_id = get_default_user_id(db)
    service = MemoryService(db)
    memory = await service.create_memory(
        user_id=user_id,
        content=data.content,
        category=data.category or "general",
        importance=data.importance or 0.5
    )

    return {
        "id": str(memory.id),
        "content": memory.content,
        "category": memory.category,
        "importance": memory.importance,
        "review_count": memory.review_count,
        "next_review": memory.next_review.isoformat() if memory.next_review else None,
        "created_at": memory.created_at.isoformat(),
        "extra_metadata": memory.extra_metadata
    }


@router.get("/memories")
async def list_memories(
    category: Optional[str] = None,
    include_due: bool = False,
    db: Session = Depends(get_db)
):
    user_id = get_default_user_id(db)
    service = MemoryService(db)
    memories = await service.get_memories(user_id, category, include_due)

    return [{
        "id": str(m.id),
        "content": m.content,
        "category": m.category,
        "importance": m.importance,
        "review_count": m.review_count,
        "next_review": m.next_review.isoformat() if m.next_review else None,
        "created_at": m.created_at.isoformat(),
        "extra_metadata": m.extra_metadata
    } for m in memories]


@router.get("/memories/due")
async def get_due_memories(
    db: Session = Depends(get_db)
):
    user_id = get_default_user_id(db)
    service = MemoryService(db)
    memories = await service.get_due_memories(user_id)

    return [{
        "id": str(m.id),
        "content": m.content,
        "category": m.category,
        "importance": m.importance,
        "review_count": m.review_count,
        "next_review": m.next_review.isoformat() if m.next_review else None,
        "created_at": m.created_at.isoformat(),
        "extra_metadata": m.extra_metadata
    } for m in memories]


@router.get("/memories/upcoming")
async def get_upcoming_reviews(
    days: int = 7,
    db: Session = Depends(get_db)
):
    user_id = get_default_user_id(db)
    service = MemoryService(db)
    return await service.get_upcoming_reviews(user_id, days)


@router.post("/memories/{memory_id}/review")
async def review_memory(
    memory_id: str,
    quality: int,
    db: Session = Depends(get_db)
):
    user_id = get_default_user_id(db)
    service = MemoryService(db)

    try:
        memory = await service.review_memory(memory_id, user_id, quality)
        return {
            "id": str(memory.id),
            "review_count": memory.review_count,
            "next_review": memory.next_review.isoformat() if memory.next_review else None,
            "quality_desc": service.QUALITY_DESCRIPTIONS.get(quality, "未知")
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/memories/{memory_id}")
async def update_memory(
    memory_id: str,
    data: MemoryUpdate,
    db: Session = Depends(get_db)
):
    user_id = get_default_user_id(db)
    service = MemoryService(db)

    try:
        memory = await service.update_memory(
            memory_id=memory_id,
            user_id=user_id,
            content=data.content,
            category=data.category,
            importance=data.importance
        )
        return {
            "id": str(memory.id),
            "content": memory.content,
            "category": memory.category,
            "importance": memory.importance
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/memories/{memory_id}")
async def delete_memory(
    memory_id: str,
    db: Session = Depends(get_db)
):
    user_id = get_default_user_id(db)
    service = MemoryService(db)
    success = await service.delete_memory(memory_id, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")

    return {"message": "Memory deleted successfully"}


@router.post("/memories/extract-from-conversation")
async def extract_memories_from_conversation(
    conversation_id: str,
    extract_count: int = 3,
    db: Session = Depends(get_db)
):
    """从对话中提取记忆"""
    user_id = get_default_user_id(db)
    service = MemoryService(db)

    try:
        memories = await service.extract_memories_from_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            extract_count=extract_count
        )

        return {
            "extracted_count": len(memories),
            "memories": [{
                "id": str(m.id),
                "content": m.content,
                "category": m.category,
                "importance": m.importance,
                "created_at": m.created_at.isoformat()
            } for m in memories]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memories/statistics")
async def get_memory_statistics(
    db: Session = Depends(get_db)
):
    user_id = get_default_user_id(db)
    service = MemoryService(db)
    return await service.get_statistics(user_id)
