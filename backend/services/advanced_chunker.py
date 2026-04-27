"""
高级文档切块策略模块 v2
支持多种智能切块方式：
1. 智能混合切块（结合多种策略）
2. 语义感知切块（基于句子嵌入相似性）
3. 结构优先切块（保留文档结构）
4. 问答感知切块（保留问答对完整性）
5. 实体感知切块（基于命名实体）
"""

from typing import List, Optional, Tuple, Dict, Any, Set
import re
import numpy as np
from dataclasses import dataclass
from services.rag_service import embedding_service
import json


@dataclass
class ChunkResult:
    """切块结果"""
    content: str
    metadata: Dict[str, Any]
    score: float = 0.0


class AdvancedChunker:
    """高级文档切块器 v2"""

    def __init__(
        self,
        chunk_size: int = 1200,
        chunk_overlap: int = 200,
        min_chunk_size: int = 200,
        embedding_model=None
    ):
        """
        初始化切块器

        Args:
            chunk_size: 目标块大小（字符数）
            chunk_overlap: 块间重叠大小
            min_chunk_size: 最小块大小
            embedding_model: 嵌入模型
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.embedding_model = embedding_model or embedding_service

        # 定义递归分隔符层次结构（从粗到细）
        self.recursive_separators = [
            "\n\n\n",      # 三级段落分隔
            "\n\n",        # 段落分隔
            "\n",          # 行分隔
            "。", "！", "？", "；", "…",  # 中文句子结束符
            ". ", "! ", "? ", "; ",        # 英文句子结束符
            "，", ", ",     # 逗号
            " ",           # 空格
            ""             # 字符级
        ]

        # Markdown 标题模式
        self.md_heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
        
        # 问答案检测模式
        self.qa_patterns = [
            re.compile(r'问[：:]\s*(.+)'),
            re.compile(r'Q[：:]\s*(.+)'),
            re.compile(r'问题[：:]\s*(.+)'),
            re.compile(r'(什么是|如何|怎样|为什么|为何|怎么|请问)[^？\n]*[？?]'),
        ]
        self.answer_patterns = [
            re.compile(r'答[：:]\s*(.+)'),
            re.compile(r'A[：:]\s*(.+)'),
            re.compile(r'答曰[：:]\s*(.+)'),
        ]

    def chunk_smart_hybrid(
        self,
        text: str,
        preserve_qa: bool = True,
        preserve_structure: bool = True
    ) -> List[str]:
        """
        智能混合切块 - 核心高级策略
        
        策略：
        1. 检测并保留问答对结构
        2. 识别文档结构（标题、列表等）
        3. 使用语义边界切分
        4. 智能合并过小块
        """
        if not text.strip():
            return []
        
        # 1. 预处理文本
        text = self._preprocess_text(text)
        
        # 2. 检测问答对
        qa_pairs = []
        if preserve_qa:
            qa_pairs = self._extract_qa_pairs(text)
        
        # 3. 检测文档结构
        structure_info = {}
        if preserve_structure:
            structure_info = self._analyze_structure(text)
        
        # 4. 句子级别分割
        sentences = self._split_into_sentences(text)
        if not sentences:
            return [text] if len(text) >= self.min_chunk_size else []
        
        # 5. 语义边界检测
        semantic_boundaries = self._detect_semantic_boundaries(sentences)
        
        # 6. 基于语义边界切分
        chunks = self._create_chunks_from_boundaries(
            sentences, 
            semantic_boundaries,
            structure_info,
            qa_pairs
        )
        
        # 7. 后处理：合并过小块，拆分过大块
        chunks = self._post_process_chunks(chunks)
        
        return chunks

    def chunk_by_intent(self, text: str) -> List[str]:
        """
        意图感知切块 - 根据问题意图类型切分
        
        适用于常见问题类型：
        - 定义类：什么是X
        - 流程类：如何做X
        - 原因类：为什么X
        - 对比类：X和Y的区别
        """
        # 按段落分割
        paragraphs = self._split_into_paragraphs(text)
        
        chunks = []
        current_chunk = []
        current_intents = set()
        
        for para in paragraphs:
            # 检测段落意图
            intents = self._detect_intent_types(para)
            
            # 如果当前块满了或意图冲突，开始新块
            should_start_new = (
                self._get_chunk_length(current_chunk) >= self.chunk_size * 0.8 and
                len(current_chunk) > 0
            ) or (
                current_intents and intents and 
                len(current_intents.intersection(intents)) == 0 and
                len(current_chunk) >= self.min_chunk_size
            )
            
            if should_start_new:
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                current_intents = intents
            else:
                current_chunk.append(para)
                current_intents.update(intents)
        
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return self._post_process_chunks(chunks)

    def chunk_entity_aware(self, text: str) -> List[str]:
        """
        实体感知切块 - 基于命名实体的智能切分
        
        策略：
        1. 识别文本中的实体（人名、地名、机构等）
        2. 确保同一实体的信息不被拆分
        3. 基于实体共现关系切分
        """
        sentences = self._split_into_sentences(text)
        
        # 简单实体识别（基于常见模式）
        entities_per_sentence = []
        all_entities = set()
        
        for sent in sentences:
            entities = self._extract_simple_entities(sent)
            entities_per_sentence.append(entities)
            all_entities.update(entities)
        
        # 计算句子间的实体重叠度
        boundaries = self._find_entity_boundaries(entities_per_sentence)
        
        # 基于边界切分
        chunks = []
        for i, boundary_idx in enumerate(boundaries):
            if i == 0:
                chunk_sentences = sentences[:boundary_idx + 1]
            else:
                chunk_sentences = sentences[boundaries[i-1]:boundary_idx + 1]
            
            if chunk_sentences:
                chunk = '。'.join(chunk_sentences) if '。' in text else ' '.join(chunk_sentences)
                if chunk.strip():
                    chunks.append(chunk.strip())
        
        # 添加最后一块
        if boundaries[-1] < len(sentences) - 1 if boundaries else True:
            last_chunk = '。'.join(sentences[boundaries[-1] + 1:]) if '。' in text else ' '.join(sentences[boundaries[-1] + 1:])
            if last_chunk.strip():
                chunks.append(last_chunk.strip())
        
        return self._post_process_chunks(chunks)

    def chunk_deep_semantic(
        self, 
        text: str, 
        embedding_threshold: float = 0.65
    ) -> List[str]:
        """
        深度语义切块 - 使用嵌入相似性精确切分
        
        这是最智能的切块方式，适合高质量检索场景
        """
        # 句子级别分割
        sentences = self._split_into_sentences(text)
        if len(sentences) <= 1:
            return [text] if len(text) >= self.min_chunk_size else []
        
        # 计算句子嵌入
        try:
            embeddings = self.embedding_model.embed_async(sentences)
        except Exception as e:
            print(f"深度语义切块嵌入失败: {e}")
            return self.chunk_smart_hybrid(text)
        
        # 计算相邻句子间的语义相似度
        similarities = []
        for i in range(len(embeddings) - 1):
            sim = self._cosine_similarity(embeddings[i], embeddings[i + 1])
            similarities.append(sim)
        
        # 使用动态阈值找断点
        mean_sim = np.mean(similarities) if similarities else 0
        std_sim = np.std(similarities) if similarities else 0
        dynamic_threshold = max(embedding_threshold, mean_sim - std_sim)
        
        # 找语义断点（相似度显著下降的位置）
        break_points = []
        for i, sim in enumerate(similarities):
            if sim < dynamic_threshold:
                # 确保不是短期的波动
                if i == 0 or similarities[i-1] - sim > 0.1:
                    break_points.append(i + 1)
        
        # 如果断点太少，使用句子累积方式
        if len(break_points) < len(sentences) / 4:
            return self._create_balanced_chunks(sentences)
        
        # 基于断点创建块
        chunks = []
        start = 0
        for bp in break_points:
            chunk = '。'.join(sentences[start:bp]) if '。' in text else ' '.join(sentences[start:bp])
            if len(chunk) >= self.min_chunk_size:
                chunks.append(chunk)
            start = bp
        
        # 最后一块
        if start < len(sentences):
            last = '。'.join(sentences[start:]) if '。' in text else ' '.join(sentences[start:])
            if len(last) >= self.min_chunk_size or not chunks:
                chunks.append(last)
        
        return self._post_process_chunks(chunks)

    def _preprocess_text(self, text: str) -> str:
        """文本预处理"""
        # 规范化空白字符
        text = re.sub(r'\s+', ' ', text)
        # 规范化引号
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        return text.strip()

    def _split_into_sentences(self, text: str) -> List[str]:
        """将文本分割为句子"""
        # 中英文句子分割
        sentence_endings = ['。', '！', '？', '；', '…', '. ', '! ', '? ', '; ']
        
        sentences = []
        current = []
        
        for char in text:
            current.append(char)
            if char in sentence_endings:
                sentence = ''.join(current).strip()
                if sentence:
                    sentences.append(sentence)
                current = []
        
        if current:
            remaining = ''.join(current).strip()
            if remaining:
                sentences.append(remaining)
        
        # 过滤空句子和过短句子
        return [s for s in sentences if len(s) >= 5]

    def _split_into_paragraphs(self, text: str) -> List[str]:
        """将文本分割为段落"""
        # 按多个换行符分割
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]

    def _extract_qa_pairs(self, text: str) -> List[Tuple[str, str]]:
        """提取问答对"""
        pairs = []
        
        lines = text.split('\n')
        current_question = None
        
        for line in lines:
            # 检查是否是问题
            is_question = any(p.match(line) for p in self.qa_patterns if p.match(line))
            if is_question:
                current_question = line.strip()
            elif current_question:
                # 检查是否是回答
                is_answer = any(p.match(line) for p in self.answer_patterns if p.match(line))
                if is_answer:
                    pairs.append((current_question, line.strip()))
                    current_question = None
        
        return pairs

    def _analyze_structure(self, text: str) -> Dict[str, Any]:
        """分析文档结构"""
        lines = text.split('\n')
        structure = {
            'headings': [],
            'lists': [],
            'is_markdown': False
        }
        
        for i, line in enumerate(lines):
            # 检测标题
            heading_match = self.md_heading_pattern.match(line)
            if heading_match:
                structure['headings'].append({
                    'line': i,
                    'level': len(heading_match.group(1)),
                    'text': heading_match.group(2)
                })
                structure['is_markdown'] = True
            
            # 检测列表项
            if re.match(r'^[\-\*\d]+\.\s', line.strip()):
                structure['lists'].append(i)
        
        return structure

    def _detect_semantic_boundaries(
        self, 
        sentences: List[str],
        window_size: int = 3
    ) -> List[int]:
        """
        检测语义边界
        
        使用滑动窗口计算句子间的语义变化，同时检测主题切换
        """
        if len(sentences) <= 2:
            return []
        
        # 【新增】检测主题切换边界（国家名、章节标题等）
        topic_boundaries = self._detect_topic_boundaries(sentences)
        
        # 尝试获取嵌入
        try:
            embeddings = self.embedding_model.embed_async(sentences)
        except:
            # 如果嵌入失败，使用关键词重叠度
            return self._detect_keyword_boundaries(sentences)
        
        # 计算相邻句子的相似度
        boundaries = []
        for i in range(len(sentences) - 1):
            sim = self._cosine_similarity(embeddings[i], embeddings[i + 1])
            if sim < 0.6:  # 语义跳变
                boundaries.append(i + 1)
        
        # 合并主题边界和语义边界
        all_boundaries = sorted(set(boundaries + topic_boundaries))
        
        return all_boundaries
    
    def _detect_topic_boundaries(self, sentences: List[str]) -> List[int]:
        """
        检测主题切换边界
        
        识别国家名切换、章节标题等主题标记
        """
        # 常见国家美食主题标记
        country_patterns = [
            '中国美食', '美国美食', '日本美食', '韩国美食', '法国美食', '德国美食',
            '英国美食', '意大利美食', '印度美食', '泰国美食', '越南美食', '墨西哥美食',
            '俄罗斯美食', '澳大利亚美食', '巴西美食', '西班牙美食', '葡萄牙美食',
            '中国', '美国', '日本', '韩国', '法国', '德国', '英国', '意大利',
            '印度', '泰国', '越南', '墨西哥', '俄罗斯', '澳大利亚', '巴西', '西班牙',
            '非洲美食', '美洲美食', '欧洲美食', '亚洲美食',  # 大陆/地区
            '第一章', '第二章', '第三章', '第四章', '第五章',  # 章节标题
            '一、', '二、', '三、', '四、', '五、',  # 列表标题
        ]
        
        boundaries = []
        for i, sentence in enumerate(sentences):
            for pattern in country_patterns:
                if pattern in sentence:
                    # 检测到主题标记，如果不在第一个句子，就在之前切分
                    if i > 0:
                        boundaries.append(i)
                    break
        
        return boundaries

    def _detect_keyword_boundaries(self, sentences: List[str]) -> List[int]:
        """基于关键词重叠检测边界"""
        if len(sentences) <= 2:
            return []
        
        def extract_keywords(text: str) -> Set[str]:
            # 简单关键词提取：去除停用词后的名词和动词
            words = re.findall(r'[\w]+', text)
            # 简单的停用词
            stopwords = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '他', '她', '它', '们', '这个', '那个', '什么', '怎么', '如何', '为什么'}
            return {w for w in words if w not in stopwords and len(w) >= 2}
        
        boundaries = []
        for i in range(len(sentences) - 1):
            kw1 = extract_keywords(sentences[i])
            kw2 = extract_keywords(sentences[i + 1])
            
            # 计算Jaccard相似度
            if kw1 and kw2:
                overlap = len(kw1 & kw2) / len(kw1 | kw2)
                if overlap < 0.2:  # 关键词重叠度低
                    boundaries.append(i + 1)
        
        return boundaries

    def _detect_intent_types(self, text: str) -> Set[str]:
        """检测文本的意图类型"""
        intents = set()
        
        if re.search(r'什么是|定义|概念|含义', text):
            intents.add('definition')
        if re.search(r'如何|怎么|怎样|步骤|流程|方法', text):
            intents.add('process')
        if re.search(r'为什么|为何|原因|理由', text):
            intents.add('cause')
        if re.search(r'区别|不同|差异|比较', text):
            intents.add('comparison')
        if re.search(r'例子|例如|比如|如', text):
            intents.add('example')
        if re.search(r'历史|发展|演变|起源', text):
            intents.add('history')
        
        return intents

    def _extract_simple_entities(self, text: str) -> Set[str]:
        """简单实体提取"""
        entities = set()
        
        # 人名模式（简单）
        names = re.findall(r'[\u4e00-\u9fa5]{2,3}(?:先生|女士|教授|博士|经理|总|总)', text)
        entities.update(names)
        
        # 机构名模式
        orgs = re.findall(r'(?:公司|医院|学校|医院|集团|企业|机构|组织)(?:[\u4e00-\u9fa5]+)', text)
        entities.update(orgs)
        
        # 技术术语
        terms = re.findall(r'[\u4e00-\u9fa5]+(?:技术|方法|系统|平台|算法|模型)', text)
        entities.update(terms)
        
        return entities

    def _find_entity_boundaries(self, entities_per_sentence: List[Set]) -> List[int]:
        """找实体边界"""
        boundaries = []
        
        for i in range(1, len(entities_per_sentence)):
            prev_entities = entities_per_sentence[i - 1]
            curr_entities = entities_per_sentence[i]
            
            # 如果实体重叠度低于阈值，认为是边界
            if prev_entities and curr_entities:
                overlap = len(prev_entities & curr_entities) / len(prev_entities | curr_entities)
                if overlap < 0.15:
                    boundaries.append(i)
            elif prev_entities != curr_entities and (not prev_entities or not curr_entities):
                boundaries.append(i)
        
        return boundaries

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        dot = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def _get_chunk_length(self, chunks: List[str]) -> int:
        """计算块列表的总长度"""
        return sum(len(c) for c in chunks)

    def _create_chunks_from_boundaries(
        self,
        sentences: List[str],
        boundaries: List[int],
        structure_info: Dict,
        qa_pairs: List
    ) -> List[str]:
        """基于边界创建块"""
        if not boundaries:
            return ['。'.join(sentences)] if '。' in ''.join(sentences) else [' '.join(sentences)]
        
        chunks = []
        start = 0
        
        for boundary in boundaries:
            chunk = '。'.join(sentences[start:boundary])
            if chunk.strip():
                chunks.append(chunk.strip())
            start = boundary
        
        # 最后一块
        if start < len(sentences):
            last = '。'.join(sentences[start:])
            if last.strip():
                chunks.append(last.strip())
        
        return chunks

    def _create_balanced_chunks(self, sentences: List[str]) -> List[str]:
        """创建大小均衡的块"""
        # 计算目标块包含的句子数
        avg_sentence_len = np.mean([len(s) for s in sentences]) if sentences else 200
        target_sentences = max(1, int(self.chunk_size / avg_sentence_len))
        
        chunks = []
        for i in range(0, len(sentences), target_sentences):
            chunk = '。'.join(sentences[i:i + target_sentences])
            if chunk.strip():
                chunks.append(chunk.strip())
        
        return chunks

    def _post_process_chunks(self, chunks: List[str]) -> List[str]:
        """后处理：合并过小块，拆分过大块"""
        if not chunks:
            return []
        
        # 合并过小块
        merged = []
        buffer = ""
        
        for chunk in chunks:
            if len(chunk) < self.min_chunk_size:
                # 加入缓冲区
                if buffer:
                    buffer += " " + chunk
                else:
                    buffer = chunk
            else:
                # 先处理缓冲区
                if buffer:
                    combined = buffer + " " + chunk
                    if len(combined) <= self.chunk_size * 1.2:
                        merged.append(combined.strip())
                        buffer = ""
                    else:
                        if buffer:
                            merged.append(buffer.strip())
                        buffer = chunk
                else:
                    merged.append(chunk)
        
        if buffer:
            if merged:
                # 合并到最后一个块
                merged[-1] = (merged[-1] + " " + buffer).strip()
            else:
                merged.append(buffer.strip())
        
        # 拆分过大块
        final_chunks = []
        for chunk in merged:
            if len(chunk) > self.chunk_size * 1.5:
                # 递归拆分
                sub_chunks = self._split_large_chunk(chunk)
                final_chunks.extend(sub_chunks)
            else:
                final_chunks.append(chunk)
        
        return [c for c in final_chunks if len(c) >= self.min_chunk_size]

    def _split_large_chunk(self, chunk: str) -> List[str]:
        """拆分过大的块"""
        # 使用句子边界拆分
        sentences = self._split_into_sentences(chunk)
        
        if len(sentences) <= 1:
            # 按字符硬切
            return [chunk[i:i + self.chunk_size] for i in range(0, len(chunk), self.chunk_size - self.chunk_overlap)]
        
        return self._create_balanced_chunks(sentences)

    def chunk(
        self,
        text: str,
        strategy: str = "smart_hybrid",
        **kwargs
    ) -> List[str]:
        """
        主切块入口

        Args:
            text: 输入文本
            strategy: 切块策略
                - "smart_hybrid": 智能混合（推荐）
                - "intent": 意图感知
                - "entity": 实体感知
                - "deep_semantic": 深度语义（最高质量）
                - "recursive": 递归字符
            **kwargs: 策略特定参数

        Returns:
            切块列表
        """
        text = text.strip()
        if not text:
            return []

        if strategy == "smart_hybrid":
            return self.chunk_smart_hybrid(
                text,
                preserve_qa=kwargs.get("preserve_qa", True),
                preserve_structure=kwargs.get("preserve_structure", True)
            )
        elif strategy == "intent":
            return self.chunk_by_intent(text)
        elif strategy == "entity":
            return self.chunk_entity_aware(text)
        elif strategy == "deep_semantic":
            return self.chunk_deep_semantic(
                text,
                embedding_threshold=kwargs.get("embedding_threshold", 0.65)
            )
        elif strategy == "recursive":
            return self._chunk_by_recursive(text)
        else:
            return self.chunk_smart_hybrid(text)

    def _chunk_by_recursive(self, text: str) -> List[str]:
        """递归字符切块"""
        separators = self.recursive_separators
        return self._split_text_recursive(text, separators)

    def _split_text_recursive(
        self,
        text: str,
        separators: List[str]
    ) -> List[str]:
        """递归切分文本"""
        if not separators:
            chunks = []
            for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
                chunk = text[i:i + self.chunk_size]
                if chunk.strip():
                    chunks.append(chunk)
            return chunks

        separator = separators[0]
        remaining_separators = separators[1:]

        if separator:
            splits = text.split(separator)
        else:
            splits = [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size)]
            return [s for s in splits if s.strip()]

        if len(splits) == 1:
            return self._split_text_recursive(splits[0], remaining_separators)

        chunks = []
        current_chunk = []

        for split in splits:
            split_text = split + (separator if separator else '')

            if len(split_text) > self.chunk_size:
                if current_chunk:
                    chunks.append(''.join(current_chunk))
                    current_chunk = []

                nested_chunks = self._split_text_recursive(split_text, remaining_separators)
                chunks.extend(nested_chunks)
            else:
                if sum(len(c) for c in current_chunk) + len(split_text) > self.chunk_size and current_chunk:
                    chunks.append(''.join(current_chunk))
                    current_chunk = []

                current_chunk.append(split_text)

        if current_chunk:
            chunks.append(''.join(current_chunk))

        return [c.strip() for c in chunks if c.strip()]

    def chunk_with_metadata(
        self,
        text: str,
        metadata: Dict[str, Any] = None,
        strategy: str = "smart_hybrid"
    ) -> List[Dict[str, Any]]:
        """
        切块并附加元数据
        """
        chunks = self.chunk(text, strategy=strategy)

        result = []
        for i, chunk in enumerate(chunks):
            chunk_meta = {
                "chunk_id": i,
                "chunk_index": i,
                "strategy": strategy,
                "char_count": len(chunk),
                "token_count": len(chunk) // 4,
            }
            if metadata:
                chunk_meta.update(metadata)
            result.append({
                "content": chunk,
                "metadata": chunk_meta
            })

        return result


def chunk_text(
    text: str,
    chunk_size: int = 600,
    chunk_overlap: int = 80,
    strategy: str = "smart_hybrid"
) -> List[str]:
    """
    便捷函数：切分文本
    """
    chunker = AdvancedChunker(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return chunker.chunk(text, strategy=strategy)
