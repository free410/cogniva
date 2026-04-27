"""
修复历史消息的evidence数据
遍历所有assistant消息，重新从数据库构建evidence报告
"""
import sys
import os
from pathlib import Path

# 添加backend路径
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

# 切换到backend目录
os.chdir(backend_path)

from core.database import SessionLocal, engine, Base
from models import Message, Citation, Chunk, Document, Conversation
from services.rag_service import RAGService
from sqlalchemy.orm import joinedload

def fix_historical_evidence():
    db = SessionLocal()
    try:
        # 获取所有assistant消息
        assistant_messages = db.query(Message).filter(
            Message.role == "assistant"
        ).options(
            joinedload(Message.citations)
        ).all()

        print(f"找到 {len(assistant_messages)} 条assistant消息")

        fixed_count = 0
        for msg in assistant_messages:
            msg_id = str(msg.id)
            print(f"\n处理消息: {msg_id[:8]}...")

            # 获取该消息的所有引用
            citations = db.query(Citation).filter(
                Citation.message_id == str(msg.id)
            ).all()

            print(f"  引用数: {len(citations)}")

            if not citations:
                print(f"  [SKIP] 无引用，跳过")
                continue

            # 构建chunks_data（不要过滤相似度）
            chunks_data = []
            sorted_citations = sorted(citations, key=lambda x: x.rank or 999)

            for c in sorted_citations:
                chunk = db.query(Chunk).filter(Chunk.id == c.chunk_id).first()
                doc = None
                if chunk:
                    doc = db.query(Document).filter(Document.id == chunk.document_id).first()

                content_preview = c.chunk_content if c.chunk_content else (
                    chunk.content[:200] + "..." if chunk and chunk.content else ""
                )

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

            # 使用RAGService重新计算evidence
            rag_svc = RAGService(db)
            try:
                evidence_report = rag_svc.build_evidence_report(chunks_data, msg.content)
                evidence_json = {
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

                # 更新Message的evidence字段
                msg.evidence_ = evidence_json
                print(f"  [OK] Evidence更新完成: confidence={evidence_report.get('confidence', 0):.3f}, "
                      f"chunks={len(chunks_data)}, verified={evidence_report.get('relevance_verified', False)}")
                fixed_count += 1

                # 如果需要，可以更新conversation的updated_at来标记
                conversation = msg.conversation
                if conversation:
                    conversation.updated_at = msg.created_at  # 触发更新

            except Exception as e:
                print(f"  [FAIL] 计算evidence失败: {e}")
                import traceback
                traceback.print_exc()

        db.commit()
        print(f"\n[OK] 完成！成功修复 {fixed_count}/{len(assistant_messages)} 条消息的evidence")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    fix_historical_evidence()
