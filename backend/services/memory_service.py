from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Memory
import re


class MemoryService:
    """长期记忆服务 - 基于 SM-2 算法的间隔重复学习系统"""

    BASE_INTERVALS = {
        0: 1,
        1: 1,
        2: 3,
        3: 7,
        4: 14,
        5: 30,
        6: 60,
        7: 120,
    }

    QUALITY_DESCRIPTIONS = {
        0: "完全忘记",
        1: "几乎忘记",
        2: "记忆模糊",
        3: "基本记住",
        4: "记住",
        5: "完全记住",
    }

    def __init__(self, db: Session):
        self.db = db
        self._llm = None

    def _calculate_next_review(self, importance: float, review_count: int, quality: int = None) -> datetime:
        """基于 SM-2 算法的间隔重复计算"""
        now = datetime.utcnow()
        
        if quality is not None:
            # 完全忘记 (quality = 0): 立即重新学习，今天内再次出现
            if quality == 0:
                # 重置复习计数，回到"新记忆"状态
                return now + timedelta(minutes=30)  # 30分钟后
            
            # 几乎忘记 (quality = 1): 明天复习
            elif quality == 1:
                return now + timedelta(days=1)
            
            # 记忆模糊 (quality = 2): 2-3天后
            elif quality == 2:
                return now + timedelta(days=2)
            
            # 基本记住及以上 (quality >= 3): 使用间隔重复
            else:
                # SM-2 间隔序列: 1, 3, 7, 14, 30, 60, 120, 240...
                sm2_intervals = [1, 3, 7, 14, 30, 60, 120, 240]
                
                # 使用当前复习次数作为索引
                interval_idx = min(review_count, len(sm2_intervals) - 1)
                base_interval = sm2_intervals[interval_idx]
                
                # 根据质量调整间隔 (quality 3-5)
                quality_factor = 0.5 + (quality - 3) * 0.25  # 0.5, 1.0, 1.5
                interval = base_interval * quality_factor
                
                # 重要性调整
                importance_factor = 0.7 + importance * 0.6  # 0.7 - 1.3
                interval = interval * importance_factor
                
                # 确保间隔在合理范围内
                interval = max(1, min(365, int(interval)))
                return now + timedelta(days=interval)
        
        # 默认情况（新记忆首次复习）
        return now + timedelta(days=1)

    def _calculate_easiness_factor(self, quality: int, current_ef: float = 2.5) -> float:
        new_ef = current_ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        return max(1.3, min(2.5, new_ef))

    async def create_memory(
        self,
        user_id: str,
        content: str,
        category: str = "general",
        importance: float = 0.5,
        source: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Memory:
        keywords = self._extract_keywords(content)

        memory = Memory(
            user_id=user_id,
            content=content,
            category=category,
            importance=importance,
            next_review=datetime.utcnow(),
            review_count=0
        )

        if metadata:
            memory.extra_metadata = metadata
        if source:
            memory.extra_metadata = memory.extra_metadata or {}
            memory.extra_metadata['source'] = source
        if keywords:
            memory.extra_metadata = memory.extra_metadata or {}
            memory.extra_metadata['keywords'] = keywords

        self.db.add(memory)
        self.db.commit()
        return memory

    def _extract_keywords(self, text: str) -> List[str]:
        stop_words = {'的', '了', '在', '是', '和', '与', '或', '及', '等', '有', '无',
                     '为', '以', '对', '于', '中', '要', '会', '能', '让', '使'}
        phrases = re.findall(r'[\u4e00-\u9fa5]{2,6}', text)
        keywords = [p for p in phrases if p not in stop_words]
        return keywords[:5]

    async def extract_memories_from_conversation(
        self,
        conversation_id: str,
        user_id: str,
        extract_count: int = 3
    ) -> List[Memory]:
        from models import Message

        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(10).all()

        if not messages:
            return []

        memories = []
        extracted_content = set()

        for msg in messages:
            if msg.role == "user":
                content = msg.content
                if self._is_memory_worthy(content):
                    content_hash = hash(content[:100])
                    if content_hash not in extracted_content:
                        extracted_content.add(content_hash)

                        memory = await self.create_memory(
                            user_id=user_id,
                            content=content,
                            category="conversation_insight",
                            importance=0.6,
                            source="conversation",
                            metadata={"conversation_id": str(conversation_id)}
                        )
                        memories.append(memory)

                        if len(memories) >= extract_count:
                            break

        return memories

    def _is_memory_worthy(self, text: str) -> bool:
        important_keywords = ['记住', '注意', '重要', '关键', '定义', '规则', '公式', '结论']
        if '?' in text or '？' in text:
            return True
        if any(keyword in text for keyword in important_keywords):
            return True
        if 20 <= len(text) <= 200:
            return True
        return False

    async def get_memories(
        self,
        user_id: str,
        category: Optional[str] = None,
        include_due: bool = False
    ) -> List[Memory]:
        query = self.db.query(Memory).filter(Memory.user_id == user_id)

        if category:
            query = query.filter(Memory.category == category)

        if include_due:
            query = query.filter(
                (Memory.next_review <= datetime.utcnow()) |
                (Memory.next_review.isnot(None))
            )
        else:
            query = query.filter(Memory.next_review <= datetime.utcnow())

        return query.order_by(Memory.next_review.asc()).all()

    async def get_due_memories(self, user_id: str) -> List[Memory]:
        return self.db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.next_review <= datetime.utcnow()
        ).order_by(Memory.next_review.asc()).all()

    async def get_upcoming_reviews(self, user_id: str, days: int = 7) -> List[Dict]:
        end_date = datetime.utcnow() + timedelta(days=days)

        memories = self.db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.next_review >= datetime.utcnow(),
            Memory.next_review <= end_date
        ).order_by(Memory.next_review.asc()).all()

        review_plan = []
        for memory in memories:
            days_until = (memory.next_review - datetime.utcnow()).days
            review_plan.append({
                "memory_id": str(memory.id),
                "content": memory.content[:100] + "..." if len(memory.content) > 100 else memory.content,
                "category": memory.category,
                "review_date": memory.next_review.isoformat(),
                "days_until": days_until,
                "review_count": memory.review_count,
                "importance": memory.importance
            })

        return review_plan

    async def review_memory(
        self,
        memory_id: str,
        user_id: str,
        quality: int
    ) -> Memory:
        memory = self.db.query(Memory).filter(
            Memory.id == memory_id,
            Memory.user_id == user_id
        ).first()

        if not memory:
            raise ValueError("Memory not found")

        if quality < 0 or quality > 5:
            raise ValueError("Quality must be between 0 and 5")

        current_ef = memory.importance * 2.5
        new_ef = self._calculate_easiness_factor(quality, current_ef)
        memory.importance = min(1.0, max(0.1, new_ef / 2.5))

        memory.review_count += 1

        memory.next_review = self._calculate_next_review(
            memory.importance,
            memory.review_count,
            quality
        )

        self._log_review_history(memory, quality)

        self.db.commit()
        return memory

    def _log_review_history(self, memory: Memory, quality: int):
        history_entry = {
            "reviewed_at": datetime.utcnow().isoformat(),
            "quality": quality,
            "quality_desc": self.QUALITY_DESCRIPTIONS.get(quality, "未知")
        }

        history = memory.extra_metadata or {}
        if 'review_history' not in history:
            history['review_history'] = []
        history['review_history'].append(history_entry)
        history['review_history'] = history['review_history'][-20:]

        memory.extra_metadata = history

    async def update_memory(
        self,
        memory_id: str,
        user_id: str,
        content: Optional[str] = None,
        category: Optional[str] = None,
        importance: Optional[float] = None
    ) -> Memory:
        memory = self.db.query(Memory).filter(
            Memory.id == memory_id,
            Memory.user_id == user_id
        ).first()

        if not memory:
            raise ValueError("Memory not found")

        if content is not None:
            memory.content = content
            keywords = self._extract_keywords(content)
            if memory.extra_metadata:
                memory.extra_metadata['keywords'] = keywords

        if category is not None:
            memory.category = category
        if importance is not None:
            memory.importance = max(0.1, min(1.0, importance))

        self.db.commit()
        return memory

    async def delete_memory(self, memory_id: str, user_id: str) -> bool:
        memory = self.db.query(Memory).filter(
            Memory.id == memory_id,
            Memory.user_id == user_id
        ).first()

        if not memory:
            return False

        self.db.delete(memory)
        self.db.commit()
        return True

    async def get_statistics(self, user_id: str) -> Dict[str, Any]:
        total = self.db.query(Memory).filter(Memory.user_id == user_id).count()
        due = self.db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.next_review <= datetime.utcnow()
        ).count()

        category_stats = {}
        for memory in self.db.query(Memory).filter(Memory.user_id == user_id).all():
            cat = memory.category or "general"
            category_stats[cat] = category_stats.get(cat, 0) + 1

        total_reviews = sum(m.review_count for m in self.db.query(Memory).filter(Memory.user_id == user_id).all())

        return {
            "total_memories": total,
            "due_reviews": due,
            "categories": category_stats,
            "total_reviews": total_reviews,
            "average_review_count": round(total_reviews / total, 2) if total > 0 else 0
        }


memory_service = MemoryService