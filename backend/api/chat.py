from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from core import get_db
from services import ChatService
from models import User, Citation
from core.auth import decode_access_token
import uuid
import json
import asyncio

router = APIRouter(prefix="/api", tags=["chat"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_authenticated_user_id(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> uuid.UUID:
    """获取认证用户 ID，未登录返回默认用户"""
    if token:
        payload = decode_access_token(token)
        if payload:
            user_id = payload.get("sub")
            if user_id:
                try:
                    user = db.query(User).filter(User.id == user_id).first()
                    if user:
                        return user.id
                except:
                    pass
    
    default_user = db.query(User).filter(User.username == "default_user").first()
    if default_user:
        return default_user.id
    
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


class MessageCreate(BaseModel):
    content: str
    provider: Optional[str] = "deepseek"
    use_rag: Optional[bool] = True
    use_memory: Optional[bool] = True
    document_ids: Optional[List[str]] = None


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: str


class ConversationCreate(BaseModel):
    title: Optional[str] = "新对话"


class ConversationUpdate(BaseModel):
    title: str


class ConversationResponse(BaseModel):
    id: str
    title: str
    updated_at: str


@router.post("/conversations")
async def create_conversation(
    data: ConversationCreate,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id)
):
    service = ChatService(db)
    conversation = await service.create_conversation(user_id, data.title or "新对话")

    return {
        "id": str(conversation.id),
        "title": conversation.title,
        "created_at": conversation.created_at.isoformat()
    }


@router.get("/conversations")
async def list_conversations(
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id)
):
    service = ChatService(db)
    conversations = await service.get_conversations(user_id)

    return [{
        "id": str(conv.id),
        "title": conv.title,
        "updated_at": conv.updated_at.isoformat()
    } for conv in conversations]


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id)
):
    service = ChatService(db)
    conversation = await service.get_conversation(conversation_id, user_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = conversation.messages

    message_list = []
    for m in messages:
        evidence = m.evidence if hasattr(m, 'evidence') and m.evidence else None
        chunks_data = []

        if not evidence:
            citations = db.query(Citation).filter(Citation.message_id == str(m.id)).all()

            if citations:
                from models import Chunk, Document

                sorted_citations = sorted(citations, key=lambda x: x.rank or 999)

                for c in sorted_citations:
                    chunk = db.query(Chunk).filter(Chunk.id == c.chunk_id).first()
                    doc = None
                    if chunk:
                        doc = db.query(Document).filter(Document.id == chunk.document_id).first()

                    full_content = c.chunk_content if c.chunk_content else (chunk.content if chunk and chunk.content else "")
                    content_preview = full_content

                    real_similarity = c.similarity if c.similarity else 0
                    real_reranker = c.reranker_score if c.reranker_score else real_similarity
                    real_bm25 = c.bm25_score if c.bm25_score else None
                    real_matched_terms = c.matched_terms if c.matched_terms else []
                    real_intent_ratio = c.intent_match_ratio if c.intent_match_ratio else 0
                    real_topic_match = c.topic_match if c.topic_match is not None else True
                    real_entity_score = c.entity_match_score if c.entity_match_score else None
                    real_term_score = c.term_match_score if c.term_match_score else None
                    real_matched_entities = c.matched_entities if c.matched_entities else []

                    chunks_data.append({
                        "id": str(c.chunk_id),
                        "source": doc.filename if doc else "Unknown",
                        "content": chunk.content if chunk and chunk.content else "",
                        "content_preview": content_preview,
                        "similarity": real_similarity,
                        "score": real_similarity,
                        "rank": c.rank if c.rank else len(chunks_data) + 1,
                        "method": "multi-strategy",
                        "bm25_score": real_bm25,
                        "reranker_score": real_reranker,
                        "matched_terms": real_matched_terms,
                        "term_match_ratio": len(real_matched_terms) / 10.0 if real_matched_terms else real_intent_ratio,
                        "intent_match_ratio": real_intent_ratio,
                        "topic_match": real_topic_match,
                        "entity_match_score": real_entity_score,
                        "term_match_score": real_term_score,
                        "matched_entities": real_matched_entities
                    })

                from services.rag_service import RAGService
                rag_svc = RAGService(db)
                evidence_report = rag_svc.build_evidence_report(chunks_data, m.content)
                evidence = {
                    "confidence": evidence_report.get("confidence", 0),
                    "confidence_level": evidence_report.get("confidence_level", "未知"),
                    "relevance_verified": evidence_report.get("relevance_verified", False),
                    "chunks_strategy": evidence_report.get("chunks_strategy", "recursive"),
                    "retrieval_method": evidence_report.get("retrieval_method", "Multi-Strategy Hybrid"),
                    "rerank_model": evidence_report.get("rerank_model", "Multi-Factor Reranking"),
                    "top_similarity": evidence_report.get("top_similarity", 0),
                    "avg_similarity": evidence_report.get("avg_similarity", 0),
                    "rerank_before_score": evidence_report.get("rerank_before_score"),
                    "rerank_after_score": evidence_report.get("rerank_after_score"),
                    "term_coverage": evidence_report.get("term_coverage", 0),
                    "chunks": chunks_data
                }
            else:
                evidence = None

        if evidence and evidence.get('top_similarity', 0) < 0.3:
            evidence = {
                "confidence": 0,
                "confidence_level": "无检索结果",
                "relevance_verified": False,
                "chunks_strategy": "N/A",
                "retrieval_method": "N/A",
                "rerank_model": "N/A",
                "top_similarity": 0,
                "avg_similarity": 0,
                "term_coverage": 0,
                "chunks": [],
                "note": "检索结果置信度过低"
            }

        citations = db.query(Citation).filter(Citation.message_id == str(m.id)).all()
        valid_citations = [c for c in citations if c.chunk_id]

        message_list.append({
            "id": str(m.id),
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at.isoformat(),
            "metadata": m.extra_metadata,
            "citations": [{
                "chunk_id": str(c.chunk_id),
                "document_id": str(c.chunk.document_id) if c.chunk else None,
                "document_title": c.chunk.document.filename if c.chunk and c.chunk.document else "Unknown",
                "similarity": c.similarity or 0
            } for c in valid_citations],
            "evidence": evidence
        })

    return {
        "id": str(conversation.id),
        "title": conversation.title,
        "messages": message_list
    }


@router.put("/conversations/{conversation_id}")
async def update_conversation(
    conversation_id: str,
    data: ConversationUpdate,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id)
):
    service = ChatService(db)

    try:
        conversation = await service.update_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            title=data.title
        )
        return {
            "id": str(conversation.id),
            "title": conversation.title,
            "updated_at": conversation.updated_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    data: MessageCreate,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id)
):
    """发送消息（非流式）"""
    try:
        service = ChatService(db)

        result = await service.send_message(
            conversation_id=conversation_id,
            user_id=user_id,
            content=data.content,
            provider=data.provider or "deepseek",
            use_rag=data.use_rag if data.use_rag is not None else True,
            use_memory=data.use_memory if data.use_memory is not None else True,
            document_ids=data.document_ids
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/conversations/{conversation_id}/messages/stream")
async def stream_message(
    conversation_id: str,
    data: MessageCreate,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id)
):
    """发送消息（流式响应）"""
    import traceback
    
    async def event_generator(service: ChatService):
        try:
            print(f"[Stream] Starting stream for conversation {conversation_id}")
            async for chunk in service.stream_message(
                conversation_id=conversation_id,
                user_id=user_id,
                content=data.content,
                provider=data.provider or "deepseek",
                use_rag=data.use_rag if data.use_rag is not None else True,
                use_memory=data.use_memory if data.use_memory is not None else True,
                document_ids=data.document_ids
            ):
                print(f"[Stream] Yielding chunk: {chunk}")
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.01)
        except ValueError as e:
            print(f"[Stream] ValueError: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)}, ensure_ascii=False)}\n\n"
        except Exception as e:
            print(f"[Stream] Exception: {e}")
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)}, ensure_ascii=False)}\n\n"

    print(f"[Stream] Request received for conversation {conversation_id}, content: {data.content[:50]}...")
    
    service = ChatService(db)

    return StreamingResponse(
        event_generator(service),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id)
):
    try:
        service = ChatService(db)
        success = await service.delete_conversation(conversation_id, user_id)

        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.post("/conversations/bulk-delete")
async def bulk_delete_conversations(
    conversation_ids: List[str],
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id)
):
    """批量删除对话"""
    service = ChatService(db)
    deleted_count = await service.bulk_delete_conversations(conversation_ids, user_id)

    return {"deleted_count": deleted_count}


@router.delete("/conversations")
async def clear_all_conversations(
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id)
):
    """清空所有对话"""
    service = ChatService(db)
    deleted_count = await service.clear_all_conversations(user_id)

    return {"deleted_count": deleted_count}


@router.get("/providers")
async def get_available_providers():
    """获取可用的 LLM 提供商"""
    from services.llm_gateway import llm_gateway
    return {
        "providers": llm_gateway.get_available_providers()
    }


@router.get("/providers/{provider}/models")
async def get_provider_models(provider: str):
    """获取指定提供商的模型列表"""
    from services.llm_gateway import llm_gateway
    return llm_gateway.get_available_providers()
