from typing import List, Optional, Dict, Any, AsyncIterator
from datetime import datetime, timedelta
import uuid
from sqlalchemy.orm import Session
from models import Conversation, Message, User, Citation
from services.llm_gateway import llm_gateway, LLMError
from services.rag_service import RAGService
from services.memory_service import MemoryService
from core.database import SessionLocal


class ChatService:
    """对话服务 - 增强版"""

    def __init__(self, db: Session):
        self.db = db

    # ========== 对话管理 ==========

    async def create_conversation(self, user_id: str, title: str = "新对话") -> Conversation:
        conversation = Conversation(
            user_id=user_id,
            title=title
        )
        self.db.add(conversation)
        self.db.commit()
        return conversation

    async def get_conversations(self, user_id: str) -> List[Conversation]:
        return self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc()).all()

    async def get_conversation(self, conversation_id: str, user_id: str) -> Optional[Conversation]:
        return self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()

    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        conversation = await self.get_conversation(conversation_id, user_id)
        if conversation:
            messages = self.db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).all()
            for msg in messages:
                self.db.query(Citation).filter(Citation.message_id == msg.id).delete()
                self.db.delete(msg)

            self.db.delete(conversation)
            self.db.commit()
            return True
        return False

    async def update_conversation_title(
        self,
        conversation_id: str,
        user_id: str,
        title: str
    ) -> Conversation:
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            raise ValueError("Conversation not found")

        conversation.title = title
        self.db.commit()
        return conversation

    # ========== 消息发送 ==========

    async def send_message(
        self,
        conversation_id: str,
        user_id: str,
        content: str,
        provider: str = "deepseek",
        use_rag: bool = True,
        use_memory: bool = True,
        document_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """发送消息并获取回复（非流式）
        
        Args:
            document_ids: 可选的文档ID列表，如果提供则只从这些文档检索
        """
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            raise ValueError("Conversation not found")

        # 保存用户消息
        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=content
        )
        self.db.add(user_message)
        self.db.commit()

        # 获取对话历史
        history = self._get_conversation_history(conversation_id)

        # 获取相关记忆
        memories = []
        memories_context = None
        if use_memory:
            try:
                memory_service = MemoryService(self.db)
                memories = await memory_service.get_due_memories(user_id)
                if memories:
                    memories_context = self._build_memory_context(memories)
            except Exception as e:
                print(f"Memory retrieval error: {e}")

        # RAG 检索
        retrieved_chunks = []
        if use_rag:
            try:
                rag = RAGService(self.db)
                # 如果指定了 document_ids，则只从这些文档检索
                retrieved_chunks = await rag.retrieve(
                    content, 
                    user_id=user_id,
                    document_ids=document_ids
                )
            except Exception as e:
                print(f"RAG retrieval error: {e}")

        # 【关键修复】当 use_rag=True 且没有检索结果时，才返回"未找到相关信息"
        # 如果 use_rag=False，则跳过检索，直接调用 LLM 进行普通问答
        has_valid_chunks = False
        if use_rag and retrieved_chunks:
            for c in retrieved_chunks:
                # 检查多个分数来源：similarity, bm25_score, keyword_score
                similarity = c.get('similarity', 0)
                bm25 = c.get('bm25_score', 0)
                keyword = c.get('keyword_score', 0)
                # 如果任何一个分数大于阈值，认为是有效结果
                if similarity > 0.05 or bm25 > 0 or keyword > 0.01:
                    has_valid_chunks = True
                    print(f"[CHAT] 有效chunk: similarity={similarity:.4f}, bm25={bm25:.2f}, keyword={keyword:.4f}")
                    break
        
        if use_rag and not has_valid_chunks:
            # 没有有效检索结果，直接返回
            no_result_response = "未找到相关信息"
            
            # 保存用户消息
            user_message = Message(
                conversation_id=conversation_id,
                role="user",
                content=content,
            )
            self.db.add(user_message)
            
            # 保存助手消息
            assistant_message = Message(
                conversation_id=conversation_id,
                role="assistant",
                content=no_result_response,
                extra_metadata={
                    "provider": "system",
                    "used_rag": use_rag,
                    "used_memory": use_memory,
                    "retrieved_chunks_count": 0,
                    "no_retrieval_reason": "no_valid_chunks"
                },
                evidence=None
            )
            self.db.add(assistant_message)
            self.db.commit()
            
            # 构建空的证据报告 - 关键修复：使用正确的字段名
            evidence_report = {
                "confidence": 0,
                "confidence_level": "无检索结果",
                "relevance_verified": False,
                "chunks": [],
                "top_similarity": 0,
                "avg_similarity": 0,
                "term_coverage": 0,
                "chunks_strategy": "N/A",
                "retrieval_method": "N/A"
            }
            
            return {
                "message_id": str(assistant_message.id),
                "content": no_result_response,
                "citations": [],
                "provider": "system",
                "metadata": {
                    "used_rag": use_rag,
                    "used_memory": use_memory,
                    "chunks_count": 0,
                    "has_retrieved": False,
                    "retrieval_confidence": 0
                },
                "evidence": evidence_report
            }
        
        # 构建记忆上下文
        memories_context = None
        if use_memory and memories:
            memories_context = self._build_memory_context(memories)

        # 构建可信度证据报告（先构建，获取置信度）
        rag_svc = RAGService(self.db)
        
        # 如果没有使用 RAG（use_rag=False 或没有检索结果），构建空的证据报告
        if use_rag and retrieved_chunks:
            evidence_report = rag_svc.build_evidence_report(retrieved_chunks, content)
        else:
            # use_rag=False 或没有检索结果时，返回置信度为 0 的证据报告
            evidence_report = {
                "confidence": 0,
                "confidence_level": "极低",
                "relevance_verified": False,
                "chunks_strategy": "none",
                "retrieval_method": "未启用" if not use_rag else "N/A",
                "rerank_model": "N/A",
                "top_similarity": 0,
                "avg_similarity": 0,
                "rerank_before_score": None,
                "rerank_after_score": None,
                "term_coverage": 0,
                "chunks": [],
                "note": "未启用 RAG 检索，置信度为 0" if not use_rag else "未检索到相关文档"
            }
        
        # 获取置信度和相关性验证结果
        confidence = evidence_report.get("confidence", 0)
        relevance_verified = evidence_report.get("relevance_verified", False)
        
        # 生成提示（传入置信度信息，用于调整提示词）
        messages = await rag_svc.generate_prompt(
            query=content,
            conversation_history=history,
            retrieved_chunks=retrieved_chunks,
            memories_context=memories_context,
            confidence=confidence,
            relevance_verified=relevance_verified,
            use_rag=use_rag
        )

        # 调用 LLM
        try:
            response = await llm_gateway.chat(messages, provider=provider)
        except Exception as e:
            error_msg = str(e)
            if "没有可用的 LLM 提供商" in error_msg or "not available" in error_msg:
                response = "抱歉，当前没有配置可用的 LLM 提供商。请在设置中配置 OpenAI、Claude、DeepSeek 或 Ollama API。"
            else:
                response = f"抱歉，AI 服务暂时不可用: {error_msg}"
            print(f"LLM error: {e}")

        # 保存助手回复（包含证据报告）
        assistant_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=response,
            extra_metadata={
                "provider": provider,
                "used_rag": use_rag,
                "used_memory": use_memory,
                "retrieved_chunks_count": len(retrieved_chunks),
                "memories_count": len(memories)
            },
            evidence=evidence_report if use_rag else None
        )
        self.db.add(assistant_message)
        self.db.commit()

        # 保存引用
        if retrieved_chunks and use_rag:
            try:
                await rag_svc.save_citations(
                    str(assistant_message.id),
                    retrieved_chunks,
                    threshold=0.15  # 降低阈值，保存更多引用用于后续分析
                )
            except Exception as e:
                print(f"Save citations error: {e}")

        # 计算检索状态
        has_retrieved = len(retrieved_chunks) > 0
        retrieval_confidence = evidence_report.get("confidence", 0) if use_rag else 0

        # 自动从对话中提取记忆
        if use_memory and len(history) >= 3:
            try:
                memory_service = MemoryService(self.db)
                extracted = await memory_service.extract_memories_from_conversation(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    extract_count=2
                )
                print(f"Extracted {len(extracted)} memories from conversation")
            except Exception as e:
                print(f"Memory extraction error: {e}")

        # 更新对话时间
        conversation.updated_at = datetime.utcnow()
        self.db.commit()

        return {
            "message_id": str(assistant_message.id),
            "content": response,
            "citations": retrieved_chunks[:3] if retrieved_chunks else [],
            "provider": provider,
            "metadata": {
                "used_rag": use_rag,
                "used_memory": use_memory,
                "chunks_count": len(retrieved_chunks),
                "memories_used": len(memories),
                "has_retrieved": has_retrieved,
                "retrieval_confidence": retrieval_confidence
            },
            "evidence": evidence_report  # 始终返回 evidence 报告（use_rag=False 时置信度为 0）
        }

    async def stream_message(
        self,
        conversation_id: str,
        user_id: str,
        content: str,
        provider: str = "deepseek",
        use_rag: bool = True,
        use_memory: bool = True,
        document_ids: Optional[List[str]] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """流式发送消息
        
        Args:
            document_ids: 可选的文档ID列表，如果提供则只从这些文档检索
        """
        rag_db = SessionLocal()
        assistant_message = None
        
        try:
            conversation = await self.get_conversation(conversation_id, user_id)
            if not conversation:
                raise ValueError("Conversation not found")

            # 保存用户消息
            user_message = Message(
                conversation_id=conversation_id,
                role="user",
                content=content
            )
            self.db.add(user_message)
            self.db.commit()

            # 获取对话历史
            history = self._get_conversation_history(conversation_id)

            # RAG 检索 - 使用独立的数据库会话
            retrieved_chunks = []
            if use_rag:
                try:
                    rag = RAGService(rag_db)
                    # 如果指定了 document_ids，则只从这些文档检索
                    retrieved_chunks = await rag.retrieve(
                        content, 
                        user_id=user_id,
                        document_ids=document_ids
                    )
                    # 确保返回的是可序列化的字典，保留所有元数据
                    retrieved_chunks = [
                        {
                            "chunk_id": str(c.get("chunk_id", "")),
                            "content": str(c.get("content", "")),
                            "similarity": float(c.get("similarity", c.get("_adjusted_score", 0))),
                            "document_id": str(c.get("document_id", "")),
                            "document_title": str(c.get("document_title", c.get("document_id", "Unknown"))),
                            "chunk_index": int(c.get("chunk_index", 0)),
                            "metadata": c.get("metadata", {}) if isinstance(c.get("metadata"), dict) else {},
                            # 保留意图检查的元数据
                            "reranker_score": float(c.get("reranker_score", c.get("similarity", 0))),
                            "vector_score": float(c.get("vector_score", c.get("similarity", 0))),
                            "bm25_score": float(c.get("bm25_score", 0)) if c.get("bm25_score") is not None else None,
                            "keyword_score": float(c.get("keyword_score", 0)) if c.get("keyword_score") is not None else None,
                            "matched_terms": c.get("matched_terms", []) or c.get("_matched_terms", []),
                            # 意图检查数据
                            "intent_match_ratio": float(c.get("intent_match_ratio", c.get("_intent_match_ratio", 0))),
                            "topic_match": c.get("topic_match", c.get("_topic_match", True)),
                            "entity_match_score": float(c.get("entity_match_score", c.get("_entity_match_score", 0))) if c.get("_entity_match_score") is not None else None,
                            "term_match_score": float(c.get("term_match_score", c.get("_term_match_score", 0))) if c.get("_term_match_score") is not None else None,
                            "matched_entities": c.get("matched_entities", []) or c.get("_matched_entities", []),
                            # 额外数据
                            "term_match_ratio": float(c.get("term_match_ratio", 0)),
                        }
                        for c in retrieved_chunks
                    ]
                except Exception as e:
                    print(f"RAG retrieval error: {e}")
                    import traceback
                    traceback.print_exc()

            # 【关键修复】当 use_rag=True 且没有检索结果时，才返回"未找到相关信息"
            # 如果 use_rag=False，则跳过检索，直接调用 LLM 进行普通问答
            has_valid_chunks = False
            if use_rag and retrieved_chunks:
                for c in retrieved_chunks:
                    # 检查多个分数来源
                    similarity = c.get('similarity', 0)
                    bm25 = c.get('bm25_score', 0)
                    keyword = c.get('keyword_score', 0)
                    if similarity > 0.05 or bm25 > 0 or keyword > 0.01:
                        has_valid_chunks = True
                        print(f"[STREAM] 有效chunk: similarity={similarity:.4f}, bm25={bm25:.2f}, keyword={keyword:.4f}")
                        break
            
            if use_rag and not has_valid_chunks:
                no_result_response = "未找到相关信息"
                
                # 保存助手消息
                assistant_message = Message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=no_result_response,
                    extra_metadata={
                        "provider": "system",
                        "used_rag": use_rag,
                        "retrieved_chunks_count": 0,
                        "no_retrieval_reason": "no_valid_chunks"
                    },
                    evidence=None
                )
                self.db.add(assistant_message)
                self.db.commit()
                
                # 【关键修复】不返回 evidence 字段，让前端知道这是"无检索结果"
                # 前端 EvidencePanel 会检查 evidence 是否存在来决定是否显示
                yield {
                    "type": "done",
                    "message_id": str(assistant_message.id),
                    "content": no_result_response,
                    "citations": None,  # 使用 None 而不是 []，让前端能区分"空"和"无"
                    "evidence": None,   # 使用 None 而不是空对象，让前端不显示
                    "metadata": {
                        "used_rag": use_rag,
                        "retrieved_chunks_count": 0,
                        "has_retrieved": False,
                        "retrieval_confidence": 0
                    }
                }
                return

            # 构建记忆上下文
            memories_context = None
            if use_memory:
                try:
                    memory_service = MemoryService(self.db)
                    due_memories = await memory_service.get_due_memories(user_id)
                    if due_memories:
                        memories_context = self._build_memory_context(due_memories)
                except Exception as e:
                    print(f"Memory retrieval error: {e}")

            # 生成提示 - 使用独立的数据库会话
            rag_svc = RAGService(rag_db)
            
            # 构建证据报告获取置信度
            # 如果没有使用 RAG（use_rag=False 或没有检索结果），构建空的证据报告
            try:
                if use_rag and retrieved_chunks:
                    evidence_report = rag_svc.build_evidence_report(retrieved_chunks, content)
                    print(f"[STREAM] evidence_report 构建完成: confidence={evidence_report.get('confidence', 0)}, chunks数量={len(evidence_report.get('chunks', []))}")
                else:
                    # use_rag=False 或没有检索结果时，返回置信度为 0 的证据报告
                    evidence_report = {
                        "confidence": 0,
                        "confidence_level": "极低",
                        "relevance_verified": False,
                        "chunks_strategy": "none",
                        "retrieval_method": "未启用" if not use_rag else "N/A",
                        "rerank_model": "N/A",
                        "top_similarity": 0,
                        "avg_similarity": 0,
                        "rerank_before_score": None,
                        "rerank_after_score": None,
                        "term_coverage": 0,
                        "chunks": [],
                        "note": "未启用 RAG 检索，置信度为 0" if not use_rag else "未检索到相关文档"
                    }
                    print(f"[STREAM] 未启用 RAG，置信度设为 0")
            except Exception as e:
                print(f"Build evidence report error: {e}")
                import traceback
                traceback.print_exc()
                evidence_report = {"confidence": 0, "relevance_verified": False, "chunks_strategy": "N/A", "retrieval_method": "N/A", "rerank_model": "N/A", "chunks": []}
            
            confidence = evidence_report.get("confidence", 0)
            relevance_verified = evidence_report.get("relevance_verified", False)
            
            print(f"[STREAM] 最终 evidence_report: {evidence_report}")
            
            try:
                messages = await rag_svc.generate_prompt(
                    query=content,
                    conversation_history=history,
                    retrieved_chunks=retrieved_chunks,
                    memories_context=memories_context,
                    confidence=confidence,
                    relevance_verified=relevance_verified,
                    use_rag=use_rag
                )
            except Exception as e:
                print(f"Generate prompt error: {e}")
                import traceback
                traceback.print_exc()
                messages = [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": content}]

            # 创建助手消息占位
            assistant_message = Message(
                conversation_id=conversation_id,
                role="assistant",
                content=""
            )
            self.db.add(assistant_message)
            self.db.commit()

            # 流式生成
            full_response = ""
            chunk_count = 0
            try:
                async for chunk in llm_gateway.stream_chat(messages, provider=provider):
                    full_response += chunk
                    chunk_count += 1
                    if chunk_count <= 3:
                        print(f"[STREAM] LLM 返回 chunk {chunk_count}: {chunk[:50]}...")
                    yield {
                        "type": "chunk",
                        "content": chunk,
                        "message_id": str(assistant_message.id)
                    }
                print(f"[STREAM] LLM 流式结束，共 {chunk_count} 个 chunks，full_response 长度: {len(full_response)}")
            except Exception as e:
                print(f"LLM stream error: {e}")
                import traceback
                traceback.print_exc()
                raise

            # 保存完整回复
            # 【保护】如果 LLM 返回空响应，使用默认消息
            if not full_response or not full_response.strip():
                full_response = "未找到相关信息"
                print(f"[STREAM] LLM 返回空响应，使用默认消息")
            
            assistant_message.content = full_response
            assistant_message.extra_metadata = {
                "provider": provider,
                "used_rag": use_rag,
                "retrieved_chunks_count": len(retrieved_chunks)
            }
            assistant_message.evidence = evidence_report  # 始终保存 evidence 报告
            self.db.commit()

            # 保存引用
            if retrieved_chunks and use_rag:
                try:
                    await rag_svc.save_citations(
                        str(assistant_message.id),
                        retrieved_chunks
                    )
                except Exception as e:
                    print(f"Save citations error: {e}")

            conversation.updated_at = datetime.utcnow()
            self.db.commit()

            # 【关键修复】如果置信度为 0，不返回 citations 和 evidence
            # 这发生在：1) 没有检索结果 2) 检索结果置信度过低 3) LLM 判断不相关
            evidence_confidence = evidence_report.get("confidence", 0) if evidence_report else 0
            has_valid_evidence = evidence_confidence > 0 and len(evidence_report.get("chunks", [])) > 0

            # 【额外修复】如果 AI 说"未找到相关信息"，即使有 chunks 也不返回 evidence
            # 因为 AI 明确表示没有找到有用的信息
            if has_valid_evidence and full_response:
                response_lower = full_response.lower()
                no_info_patterns = [
                    '未找到', '没有找到', '没有检索', '检索失败',
                    '无法找到', '未能找到', '未能检索',
                    'no relevant', 'not found', 'cannot find', 'could not find'
                ]
                for pattern in no_info_patterns:
                    if pattern in response_lower:
                        print(f"[STREAM] AI 说'{pattern}'，清空 evidence 数据")
                        has_valid_evidence = False
                        break

            # 如果置信度为 0，evidence_report 设为 None
            final_evidence = evidence_report if has_valid_evidence else None
            final_citations = retrieved_chunks[:3] if has_valid_evidence else None

            yield {
                "type": "done",
                "message_id": str(assistant_message.id),
                "citations": final_citations,
                "provider": provider,
                "evidence": final_evidence,
                "metadata": {
                    "used_rag": use_rag,
                    "retrieved_chunks_count": len(retrieved_chunks),
                    "has_retrieved": has_valid_evidence,
                    "retrieval_confidence": evidence_confidence
                }
            }
            print(f"[STREAM] 已发送 done 消息")
            print(f"[STREAM]   - has_valid_evidence: {has_valid_evidence}")
            print(f"[STREAM]   - citations 数量: {len(final_citations) if final_citations else 0}")
            print(f"[STREAM]   - evidence confidence: {evidence_confidence}")

        except Exception as e:
            error_msg = f"生成出错: {str(e)}"
            if assistant_message:
                try:
                    assistant_message.content = error_msg
                    assistant_message.extra_metadata = {"error": True, "provider": provider}
                    self.db.commit()
                except:
                    pass
            yield {"type": "error", "error": error_msg, "message_id": str(assistant_message.id) if assistant_message else "unknown"}

        finally:
            try:
                rag_db.close()
            except:
                pass

    # ========== 辅助方法 ==========

    def _get_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """获取对话历史（最近10条）"""
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()

        # 限制历史长度
        messages = messages[-10:] if len(messages) > 10 else messages

        return [{"role": m.role, "content": m.content} for m in messages]

    def _build_memory_context(self, memories: List[Any]) -> str:
        """构建记忆上下文"""
        if not memories:
            return ""

        memory_parts = []
        for i, memory in enumerate(memories[:5], 1):
            # 支持对象和字典两种格式
            content = memory.content if hasattr(memory, 'content') else memory.get('content', '')
            category = memory.category if hasattr(memory, 'category') else memory.get('category', 'general')
            if content:
                memory_parts.append(f"{i}. 【{category}】{content}")

        return "\n".join(memory_parts)

    # ========== 批量操作 ==========

    async def bulk_delete_conversations(
        self,
        conversation_ids: List[str],
        user_id: str
    ) -> int:
        """批量删除对话"""
        deleted_count = 0
        for conv_id in conversation_ids:
            if await self.delete_conversation(conv_id, user_id):
                deleted_count += 1
        return deleted_count

    async def clear_all_conversations(self, user_id: str) -> int:
        """清空所有对话"""
        conversations = await self.get_conversations(user_id)
        count = 0
        for conv in conversations:
            if await self.delete_conversation(str(conv.id), user_id):
                count += 1
        return count


chat_service = ChatService
