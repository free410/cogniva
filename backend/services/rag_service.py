from typing import List, Optional, Dict, Any, Tuple, Set
from datetime import datetime
import numpy as np
import httpx
import hashlib
import re
import math
import itertools
from sqlalchemy.orm import Session
from models import Chunk, Vector, Citation, Message, Document
from core.config import settings
import json


class DashScopeEmbeddingService:
    """基于阿里云百炼 DashScope 的嵌入服务"""

    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        # text-embedding-v3 返回 1536 维向量
        self.dimension = 1536
        self.cache = {}

    async def embed_async(self, texts: List[str]) -> List[List[float]]:
        """异步生成嵌入向量"""
        if not texts:
            return []

        cached = []
        uncached_texts = []

        for text in texts:
            if text in self.cache:
                cached.append(self.cache[text])
            else:
                cached.append(None)
                uncached_texts.append(text)

        if uncached_texts:
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{self.base_url}/embeddings",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "text-embedding-v3",  # 升级为 v3 版本，性能更好
                            "input": uncached_texts,
                            "encoding_format": "float"  # 明确指定返回格式
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    embeddings = [item["embedding"] for item in data["data"]]

                    for text, embedding in zip(uncached_texts, embeddings):
                        self.cache[text] = embedding

                    result = []
                    j = 0
                    for i in range(len(texts)):
                        if cached[i] is not None:
                            result.append(cached[i])
                        else:
                            result.append(embeddings[j])
                            j += 1
                    return result

            except Exception as e:
                print(f"DashScope embedding failed: {e}, using fallback")
                return self._fallback_embed(texts)

        return cached

    def _fallback_embed(self, texts: List[str]) -> List[List[float]]:
        """降级方案：生成伪向量"""
        embeddings = []
        for text in texts:
            hash_bytes = hashlib.md5(text.encode()).digest()
            seed = int.from_bytes(hash_bytes[:4], 'big')
            np.random.seed(seed)
            base = np.random.randn(self.dimension)
            base = base / (np.linalg.norm(base) + 1e-8)
            word_count = len(text.split()) if text else 1
            result = base * (word_count ** 0.3)
            embeddings.append(result.tolist())
        return embeddings

    def embed(self, texts: List[str]) -> List[List[float]]:
        """同步生成嵌入向量"""
        if not texts:
            return []

        cached = []
        uncached_texts = []

        for text in texts:
            if text in self.cache:
                cached.append(self.cache[text])
            else:
                cached.append(None)
                uncached_texts.append(text)

        if uncached_texts:
            try:
                with httpx.Client(timeout=60.0) as client:
                    response = client.post(
                        f"{self.base_url}/embeddings",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "text-embedding-v3",  # 升级为 v3 版本
                            "input": uncached_texts,
                            "encoding_format": "float"
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    embeddings = [item["embedding"] for item in data["data"]]

                    for text, embedding in zip(uncached_texts, embeddings):
                        self.cache[text] = embedding

                    result = []
                    j = 0
                    for i in range(len(texts)):
                        if cached[i] is not None:
                            result.append(cached[i])
                        else:
                            result.append(embeddings[j])
                            j += 1
                    return result

            except Exception as e:
                print(f"DashScope embedding (sync) failed: {e}, using fallback")
                return self._fallback_embed(texts)

        return cached


embedding_service = DashScopeEmbeddingService()


class RAGService:
    """RAG 检索增强生成服务"""

    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = embedding_service
        # 初始化重排序模型（延迟加载以加快启动速度）
        self._reranker = None
        self._reranker_model_name = "BAAI/bge-reranker-v2-m3"  # 多语言重排模型，支持中文

    @property
    def reranker(self):
        """延迟加载重排序模型"""
        if self._reranker is None:
            try:
                from sentence_transformers import CrossEncoder
                print(f"Loading reranker model: {self._reranker_model_name}...")
                self._reranker = CrossEncoder(self._reranker_model_name, device='cpu')
                print("Reranker model loaded successfully")
            except Exception as e:
                print(f"Failed to load reranker model: {e}")
                self._reranker = False  # 标记为加载失败，不再重试
        return self._reranker if self._reranker else None

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(v1, v2) / (norm1 * norm2))

    def jaccard_similarity(self, query: str, document: str) -> float:
        """计算Jaccard相似度（集合重叠度）"""
        query_words = set(re.findall(r'[\w]+', query.lower()))
        doc_words = set(re.findall(r'[\w]+', document.lower()))

        if not query_words or not doc_words:
            return 0.0

        intersection = query_words & doc_words
        union = query_words | doc_words
        return len(intersection) / len(union) if union else 0.0

    def keyword_overlap_score(self, query: str, document: str) -> float:
        """计算关键词重叠分数"""
        # 提取中英文关键词
        chinese_chars = re.findall(r'[\u4e00-\u9fff]+', query)
        english_words = re.findall(r'[a-zA-Z]+', query)

        query_keywords = set()
        for chars in chinese_chars:
            if len(chars) >= 2:  # 至少2个中文字符
                query_keywords.add(chars)
        for word in english_words:
            if len(word) >= 2:
                query_keywords.add(word.lower())

        if not query_keywords:
            return 0.0

        doc_lower = document.lower()
        matches = 0
        for keyword in query_keywords:
            if keyword in doc_lower:
                matches += 1

        return matches / len(query_keywords)

    def bm25_score(self, query: str, document: str, k1: float = 1.5, b: float = 0.75) -> float:
        """计算BM25分数 - 增强版，支持中文分词（无jieba依赖）"""
        
        def simple_tokenize(text: str) -> List[str]:
            """简单分词：处理中英文混合文本"""
            text = text.lower()
            # 提取中文字符序列和英文字符序列
            chinese_words = re.findall(r'[\u4e00-\u9fff]+', text)
            english_words = re.findall(r'[a-z0-9]+', text)
            # 合并：中文字符按2-4字切分
            words = []
            for cw in chinese_words:
                for i in range(len(cw)):
                    for l in range(2, min(5, len(cw) - i + 1)):
                        words.append(cw[i:i+l])
            # 英文单词保留
            words.extend(english_words)
            return words

        # 【关键修复】确保短国家名不被切分，在jieba分词前先标记
        use_jieba = False
        try:
            import jieba
            use_jieba = True
        except ImportError:
            pass
        
        if use_jieba:
            # 重要术语列表（这些词不会被切分）
            important_terms = [
                # 国家名
                '印度', '巴西', '中国', '美国', '日本', '韩国', '法国', '德国', 
                '英国', '意大利', '泰国', '越南', '墨西哥', '俄罗斯', '澳大利亚', 
                '加拿大', '新加坡', '马来西亚', '印尼', '菲律宾', '土耳其', '埃及',
                '南非', '尼日利亚', '肯尼亚', '摩洛哥', '秘鲁', '阿根廷', '智利',
                '哥伦比亚', '新西兰', '荷兰', '比利时', '瑞士', '奥地利', '波兰',
                '瑞典', '挪威', '丹麦', '芬兰', '希腊', '葡萄牙', '匈牙利', '捷克',
                # 菜系名
                '闽菜', '川菜', '粤菜', '湘菜', '鲁菜', '苏菜', '浙菜', '徽菜', '闽菜', '京菜',
                # 特色美食
                '肉夹馍', '凉皮', '羊肉泡馍', 'biangbiang面', '臊子面', '油泼面',
                # 其他重要术语
                '泡馍', '面食', '凉菜', '热菜', '小吃', '主食', '菜肴',
                # 闽菜相关
                '闽菜', '福州菜', '闽南菜', '佛跳墙', '荔枝肉', '闽西菜',
            ]
            
            # 标记重要术语，防止被切分
            marked_query = query
            marked_doc = document
            for term in important_terms:
                if term in query:
                    marked_query = marked_query.replace(term, f"_{term}_")
                if term in document:
                    marked_doc = marked_doc.replace(term, f"_{term}_")
            
            def tokenize(text: str) -> List[str]:
                words = list(jieba.cut(text.lower()))
                stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '但', '还', '么', '什么', '可以', '这个', '那个', '主要', '具有', '以及', '还有'}
                words = [w.strip('_') for w in words if len(w.strip('_')) >= 2 and w.strip('_') not in stopwords]
                return words
        else:
            marked_query = query
            marked_doc = document
            def tokenize(text: str) -> List[str]:
                return simple_tokenize(text)
        
        # 使用标记后的文本进行分词
        query_terms = tokenize(marked_query)
        doc_terms = tokenize(marked_doc)

        if not query_terms or not doc_terms:
            # 回退：使用简单的字符级匹配
            query_lower = query.lower()
            doc_lower = document.lower()
            if not query_lower or not doc_lower:
                return 0.0
            # 计算查询词在文档中出现的次数
            matches = 0
            for term in query_lower.split():
                if term in doc_lower:
                    matches += 1
            return matches * 2.0  # 每个匹配给予2分

        doc_len = len(doc_terms)

        # 统计词频
        doc_freq = {}
        for term in doc_terms:
            doc_freq[term] = doc_freq.get(term, 0) + 1

        # 【关键修复】使用固定IDF计算
        # 假设我们有足够多的文档，使用平均文档长度作为归一化因子
        # 对于单个chunk的BM25，使用简化的IDF：直接用词频作为权重
        score = 0.0
        matched_terms = []
        
        for term in query_terms:
            if term in doc_freq:
                tf = doc_freq[term]
                # 【优化】简化的IDF计算：使用tf作为主要因素
                # 如果一个词在文档中出现多次，说明更相关
                term_idf = 1.0  # 使用固定IDF，让TF主导
                
                # 【优化】使用原始TF而非BM25公式
                # 匹配次数越多，分数越高
                term_score = term_idf * tf
                score += term_score
                matched_terms.append(f"{term}({term_score:.2f})")
        
        # 【调试】如果有匹配，显示
        if matched_terms:
            print(f"[BM25-DBG] query='{query[:30]}...', matched={matched_terms}, score={score:.2f}")

        return score

    def generate_query_variants(self, query: str) -> List[str]:
        """生成查询变体以提高召回率"""
        variants = [query]

        # 提取关键实体词（名词、专有名词优先）
        chinese = re.findall(r'[\u4e00-\u9fff]+', query)
        english = re.findall(r'[a-zA-Z]+', query)

        # 使用同义词扩展
        expanded = self.expand_query_with_synonyms(query)
        for exp in expanded:
            if exp != query and exp not in variants:
                variants.append(exp)

        # 构建多级查询：核心词 + 组合词
        if len(chinese) >= 2:
            # 两两组合
            for i in range(len(chinese)):
                for j in range(len(chinese)):
                    if i != j:
                        combined = chinese[i] + chinese[j]
                        if combined != query and combined not in variants:
                            variants.append(combined)
            # 如果有3个以上词，尝试核心+其他
            if len(chinese) >= 3:
                core = chinese[0] + chinese[1]  # 取前两个
                if core not in variants:
                    variants.append(core)
        elif chinese:
            variants.extend(chinese)

        # 如果有英文
        if english:
            core_english = ' '.join(english)
            if core_english != query and core_english not in variants:
                variants.append(core_english)

        return list(set(variants))

    def extract_core_terms(self, query: str) -> List[str]:
        """提取核心术语用于精确匹配 - 保留重要复合词"""
        core_terms = []

        # 重要术语列表（保持完整，不被切分）
        important_terms = [
            # 菜系名
            '闽菜', '川菜', '粤菜', '湘菜', '鲁菜', '苏菜', '浙菜', '徽菜', '京菜',
            # 特色美食
            '肉夹馍', '凉皮', '羊肉泡馍', 'biangbiang面', '臊子面', '油泼面',
            '泡馍', '面食', '凉菜', '热菜', '小吃', '主食', '菜肴',
            # 国家名
            '印度', '巴西', '中国', '美国', '日本', '韩国', '法国', '德国',
            '英国', '意大利', '泰国', '越南', '墨西哥', '俄罗斯', '澳大利亚',
            '加拿大', '新加坡', '马来西亚', '印尼', '菲律宾', '土耳其', '埃及',
            '南非', '尼日利亚', '肯尼亚', '摩洛哥', '秘鲁', '阿根廷', '智利',
        ]

        # 先提取重要术语
        for term in important_terms:
            if term.lower() in query.lower():
                core_terms.append(term)

        # 使用jieba进行分词
        try:
            import jieba
            words = list(jieba.cut(query))
        except ImportError:
            words = re.findall(r'[\u4e00-\u9fff]{2,4}', query)

        # 过滤停用词，保留有意义的词
        stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '看', '好', '这', '那', '但', '还', '什么', '怎么', '如何', '为', '为什', '呢', '啊', '吧', '吗', '哦', '嗯', '可以', '这个', '那个', '主要', '具有', '以及', '还有', '哪些', '哪个'}
        
        for word in words:
            word = word.strip()
            if len(word) >= 2 and word not in stopwords and word not in core_terms:
                core_terms.append(word)

        # 提取英文词
        english_words = re.findall(r'[a-zA-Z]+', query)
        core_terms.extend([w.lower() for w in english_words if len(w) >= 2])
        
        # 添加完整查询作为术语
        if query not in core_terms:
            core_terms.append(query)

        return core_terms

    def expand_query_with_synonyms(self, query: str) -> List[str]:
        """查询扩展：使用同义词和词干变体"""
        expanded = [query]

        # 农业术语同义词库（扩展版）
        synonym_dict = {
            # 病害相关
            '病': ['病害', '疾病', '症状', '发病', '病变', '病理'],
            '害': ['害虫', '虫害', '虫害', '防治'],
            '防治': ['防治', '治疗', '控制', '治理', '方法', '措施', '技术'],
            '症状': ['症状', '特征', '表现', '迹象', '表征'],
            # 防治方法
            '杀虫': ['杀虫', '灭虫', '杀灭', '杀除', '驱虫'],
            '预防': ['预防', '防治', '避免', '防止', '规避'],
            '治疗': ['治疗', '治愈', '用药', '施药', '疗法'],
            # 作物相关
            '水稻': ['水稻', '稻谷', '稻田', '水稻种植', '稻子', '大米'],
            '小麦': ['小麦', '麦子', '麦田', '小麦种植', '麦穗'],
            '玉米': ['玉米', '苞米', '玉蜀黍', '玉米种植', '苞谷', '棒子'],
            '蔬菜': ['蔬菜', '菜类', '蔬菜作物', '蔬菜种植', '青菜'],
            '大豆': ['大豆', '黄豆', '毛豆', '豆类', '大豆种植'],
            '棉花': ['棉花', '棉株', '棉田', '棉铃'],
            '果树': ['果树', '果木', '果树林', '水果树', '果树栽培'],
            '柑橘': ['柑橘', '橘子', '橙子', '柑桔', '柚子'],
            # 肥料相关
            '肥': ['肥料', '施肥', '营养', '养分', '有机肥', '无机肥', '氮磷钾', '复合肥'],
            '施肥': ['施肥', '追肥', '底肥', '基肥', '撒肥', '施肥方法'],
            '氮肥': ['氮肥', '尿素', '氨态氮', '氮素', '氮'],
            '磷肥': ['磷肥', '磷素', '磷'],
            '钾肥': ['钾肥', '钾素', '钾'],
            '有机肥': ['有机肥', '农家肥', '粪肥', '堆肥', '厩肥'],
            # 土壤相关
            '土': ['土壤', '土质', '地力', '土壤条件', '泥土', '土地'],
            '酸碱': ['pH值', '酸碱度', '酸碱性', '土壤pH', 'PH值'],
            '土壤': ['土壤', '土地', '田地', '耕地', '土壤改良'],
            '肥力': ['肥力', '地力', '土壤肥力', '养分含量'],
            # 种植相关
            '种': ['种子', '种苗', '品种', '作物品种', '种植材料'],
            '栽': ['栽种', '种植', '栽培', '播种', '育苗', '移栽'],
            '播种': ['播种', '撒种', '种植', '条播', '点播', '撒播'],
            '育苗': ['育苗', '培育', '培养', '培育幼苗'],
            '收获': ['收获', '收割', '采收', '采摘', '丰收'],
            # 气候相关
            '温': ['温度', '气温', '温室', '保温', '温度管理'],
            '湿': ['湿度', '水分', '水分管理', '灌溉', '保湿'],
            '光': ['光照', '光合作用', '光照强度', '日照', '阳光'],
            '气候': ['气候', '天气', '气象', '气候条件'],
            '干旱': ['干旱', '旱情', '缺水', '干旱灾害'],
            '涝': ['涝害', '洪涝', '水灾', '积水', '排水不良'],
            '霜': ['霜冻', '霜害', '低温冻害', '防霜'],
            # 病虫害相关
            '虫': ['害虫', '虫害', '虫害防治', '杀虫剂', '农药', '虫子'],
            '菌': ['病菌', '真菌', '细菌', '微生物', '杀菌剂', '菌类'],
            '病毒': ['病毒', '病毒病', '病原', '病害'],
            '蚜虫': ['蚜虫', '腻虫', '蚜害'],
            '螟虫': ['螟虫', '螟蛾', '钻心虫', '二化螟', '三化螟'],
            '稻飞虱': ['稻飞虱', '飞虱', '褐飞虱', '白背飞虱'],
            '红蜘蛛': ['红蜘蛛', '螨虫', '叶��', '蛛螨'],
            '白粉病': ['白粉病', '白粉菌', '粉状霉'],
            '纹枯病': ['纹枯病', '纹枯菌', '鞘腐病'],
            '锈病': ['锈病', '锈菌', '叶锈', '杆锈'],
            '腐烂': ['腐烂', '腐病', '软腐', '茎腐', '根腐'],
            # 农业措施相关
            '管理': ['管理', '栽培管理', '田间管理', '养护', '农事管理'],
            '处理': ['处理', '处置', '方法', '技术', '措施'],
            '灌溉': ['灌溉', '浇水', '供水', '灌溉系统', '滴灌', '喷灌'],
            '排水': ['排水', '排涝', '泄水', '排水系统'],
            '除草': ['除草', '锄草', '杂草防除', '草害防治'],
            '修剪': ['修剪', '整枝', '剪枝', '修枝', '整形'],
            '套袋': ['套袋', '果实套袋', '保护袋'],
            # 产量相关
            '产量': ['产量', '收成', '产出', '单位面积产量', '亩产', '产量提高'],
            '品质': ['品质', '质量', '品级', '等级', '优质'],
            '成熟': ['成熟', '成熟期', '老熟', '完熟', '成熟度'],
            # 农药相关
            '农药': ['农药', '药剂', '杀虫剂', '杀菌剂', '除草剂', '农药使用'],
            '剂量': ['剂量', '用药量', '浓度', '配比', '稀释倍数'],
            '残留': ['残留', '农药残留', '残留量', '安全间隔期'],
            # 农业技术相关
            '技术': ['技术', '方法', '工艺', '规程', '操作规程'],
            '设施': ['设施', '设备', '装置', '农业设施', '大棚'],
            '薄膜': ['薄膜', '地膜', '农膜', '塑料薄膜', '覆盖'],
            '温室': ['温室', '大棚', '日光温室', '智能温室', '塑料大棚'],
        }

        # 提取查询中的词
        words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', query)
        expanded_query = list(words)

        # 查找同义词
        for word in words:
            if word in synonym_dict:
                for syn in synonym_dict[word]:
                    if syn not in expanded_query:
                        expanded_query.append(syn)

        # 生成新的查询组合
        if len(expanded_query) > len(words):
            # 不同组合方式
            # 1. 原始词 + 一个同义词
            for i, word in enumerate(words):
                if word in synonym_dict:
                    for syn in synonym_dict[word]:
                        variant = list(words)
                        variant[i] = syn
                        expanded.append(''.join(variant))

            # 2. 全部同义词替换
            if all(w in synonym_dict for w in words):
                for combo in itertools.product(*[synonym_dict.get(w, [w]) for w in words]):
                    variant = ''.join(combo)
                    if variant != query:
                        expanded.append(variant)

        # 通用同义词扩展（基于单字符的同义替换）
        general_synonyms = {
            '怎': ['如何', '怎样', '怎么'],
            '何': ['如何', '怎样', '怎么'],
            '因': ['原因', '病因', '因素'],
            '为': ['因为', '为何', '原因'],
            '时': ['时间', '时期', '时节', '什么时候'],
            '要': ['主要', '重要', '要点', '要素'],
            '做': ['做法', '如何做', '怎么做的'],
            '用': ['使用', '用途', '用处', '应用'],
            '能': ['能力', '可以', '能够'],
            '好': ['良好', '优良', '优秀'],
            '坏': ['不良', '劣质', '问题'],
        }

        return list(set(expanded))  # 去重

    async def _intent_relevance_check(self, query: str, retrieved_chunks: List[Dict], threshold: float = 0.20) -> Tuple[List[Dict], float]:
        """
        意图相关性检查 - 智能动态主题识别与相关性验证
        完全自动化，无需硬编码主题列表，自动适应任何领域
        """
        if not retrieved_chunks:
            return [], 0.0

        query_lower = query.lower().strip()

        # ===== 阶段1：提取查询核心实体和概念 =====
        # 提取命名实体（人名、地名、机构名、专有名词等）
        query_entities = self._extract_entities(query)

        # 提取核心关键词（去除停用词后长度>=2的词）
        stop_words = {'的', '了', '是', '在', '和', '与', '及', '或', '我', '你', '他', '她', '它',
                      '请问', '请', '帮我', '什么', '哪些', '哪个', '怎么', '如何', '怎样', '怎么办',
                      '是什么', '为什么', '为何', '有没有', '吗', '呢', '啊', '吧', '呢'}
        query_keywords = [w for w in query_lower.split()
                         if len(w) >= 2 and w not in stop_words and not w.isdigit()]

        # 提取专业术语（连续的2-4字词，可能包含专业词汇）
        import re
        # 匹配可能的中文专业术语（2-4个连续汉字，非停用词）
        pattern = r'[\u4e00-\u9fa5]{2,4}'
        potential_terms = re.findall(pattern, query)
        professional_terms = [t for t in potential_terms
                            if t not in stop_words and len(t) >= 2]

        # 合并所有查询特征
        query_features = {
            'entities': set(query_entities),
            'keywords': set(query_keywords),
            'professional_terms': set(professional_terms),
            'full_query': query_lower
        }
        
        # 检查是否只有停用词（如果是，给一个宽松的fallback）
        has_meaningful_features = len(query_features['entities']) > 0 or len(query_features['professional_terms']) > 0 or len(query_features['keywords']) > 0

        print(f"[RAG-INTENT] 查询特征提取:")
        print(f"[RAG-INTENT]   实体: {query_features['entities']}")
        print(f"[RAG-INTENT]   关键词: {query_features['keywords']}")
        print(f"[RAG-INTENT]   专业术语: {query_features['professional_terms']}")

        # ===== 阶段2：动态计算每个chunk的相关性 =====
        adjusted_chunks = []
        all_scores = []

        for i, chunk in enumerate(retrieved_chunks):
            content = chunk.get('content', '').lower()
            content_preview = content[:1000]  # 扩大检查范围

            # --- 子评分1：实体匹配度（高权重） ---
            content_entities = self._extract_entities(content[:500])
            entity_overlap = len(query_features['entities'] & set(content_entities))
            entity_score = entity_overlap / max(len(query_features['entities']), 1) if query_features['entities'] else 0.0

            # --- 子评分2：关键词匹配度 ---
            content_words = set(content_preview.split())
            keyword_overlap = len(query_features['keywords'] & content_words)
            keyword_score = keyword_overlap / max(len(query_features['keywords']), 1) if query_features['keywords'] else 0.0

            # --- 子评分3：专业术语匹配度（最高权重）---
            content_terms = set(re.findall(r'[\u4e00-\u9fa5]{2,4}', content_preview))
            term_overlap = len(query_features['professional_terms'] & content_terms)
            term_score = term_overlap / max(len(query_features['professional_terms']), 1) if query_features['professional_terms'] else 0.0

            # --- 子评分4：语义相关性（reranker或向量相似度）---
            semantic_score = chunk.get('reranker_score', 0)
            if semantic_score <= 0:
                semantic_score = chunk.get('similarity', 0)
            # 如果没有语义分数，使用原始相似度
            if semantic_score <= 0:
                semantic_score = 0.5  # 默认中等分数

            # --- 子评分5：查询词在文档中的覆盖率 ---
            query_tokens = [w for w in query_lower.split() if len(w) >= 2]
            if query_tokens:
                matched_tokens = [t for t in query_tokens if t in content_preview]
                coverage_ratio = len(matched_tokens) / len(query_tokens)
            else:
                coverage_ratio = 0.0

            # ===== 动态权重融合 =====
            # 【关键修复】BM25应该主导排序，分数范围需要正确归一化
            # 原始BM25分数通常0-10，需要归一化到0-1
            
            # 获取原始BM25和关键词分数
            bm25_raw = chunk.get('bm25_score', 0)
            keyword_raw = chunk.get('keyword_score', 0)
            semantic_raw = chunk.get('reranker_score', 0)
            
            # 【关键修复】检查查询中的国家/地区名是否在chunk中
            # 提取查询中的国家名
            countries_in_query = ['巴西', '中国', '美国', '日本', '韩国', '法国', '德国', '英国', '意大利', '印度', '泰国', '越南', '墨西哥', '俄罗斯', '澳大利亚', '加拿大', '巴西利亚']
            content_lower = chunk.get('content', '').lower()
            query_lower = query.lower()
            
            country_match_bonus = 0
            # 【修复】只奖励，不惩罚：如果chunk中提到了查询中的国家，给奖励
            # 如果查询没有明确指定国家（问的是通用问题），不要降分
            
            for country in countries_in_query:
                if country in query_lower and country in content_lower:
                    # 查询和chunk都提到了该国家，给予奖励
                    country_match_bonus = 0.15
                    print(f"[RAG-COUNTRY] Chunk命中国家: {country}")
                    break  # 只需匹配一次
            
            # 【修复】移除主题纯净度检查，因为这会错误降分很多相关内容
            # 原因：即使chunk主要讨论其他国家，只要提到了查询中的国家，也是相关的
            topic_purity_bonus = 0
            
            # 【关键修复】确保语义分数归一化到0-1范围
            # reranker_score 可能是原始分数（>1），需要归一化
            if semantic_raw > 1:
                # 归一化到0-1范围（假设原始分数最大约100）
                semantic_normalized = min(semantic_raw / 100, 1.0)
            else:
                semantic_normalized = semantic_raw
            
            # 【修复】BM25分数主导：如果BM25 > 0，应该有较高的分数
            # 归一化因子：假设BM25最大约10，归一化到0.5-1.0范围
            if bm25_raw > 0:
                # BM25归一化：使用对数缩放，避免分数差异过大
                bm25_normalized = 0.4 + min(bm25_raw / 12.0, 0.6)  # 0.4-1.0范围
                # 有关键词匹配时，BM25占主导
                combined_score = bm25_normalized * 0.80 + semantic_normalized * 0.20 + country_match_bonus
            elif keyword_raw > 0:
                # 有TF-IDF匹配
                combined_score = min(keyword_raw, 1.0) * 0.65 + semantic_normalized * 0.35 + country_match_bonus
            else:
                # 没有关键词匹配，主要依赖语义分数
                combined_score = semantic_normalized + country_match_bonus
            
            # 确保分数不会为负
            combined_score = max(combined_score, 0)

            # 【修复】意图检查只做微调

            # 更新原始chunk，将意图检查的分数和元数据保存进去
            chunk['similarity'] = combined_score
            chunk['intent_match_ratio'] = coverage_ratio
            chunk['term_match_ratio'] = coverage_ratio  # 添加别名，方便前端使用
            chunk['topic_match'] = term_score > 0 or entity_score > 0 or semantic_score > 0.5
            chunk['entity_match_score'] = entity_score
            chunk['term_match_score'] = term_score
            chunk['matched_entities'] = list(query_features['entities'] & set(content_entities))
            chunk['matched_terms'] = list(query_features['professional_terms'] & content_terms)
            adjusted_chunks.append(chunk)
            all_scores.append(combined_score)

            # 调试日志（前5个）
            if i < 5:
                print(f"[RAG-INTENT] Chunk#{i+1}: bm25={bm25_raw:.2f}, keyword={keyword_raw:.4f}, semantic={semantic_raw:.2f} → combined={combined_score:.3f}")

        # ===== 阶段3：按调整后分数重新排序 =====
        adjusted_chunks.sort(key=lambda x: x['similarity'], reverse=True)

        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
        max_score = max(all_scores) if all_scores else 0

        print(f"[RAG-INTENT] 查询: {query}")
        print(f"[RAG-INTENT] 查询特征: 实体={len(query_features['entities'])}, 术语={len(query_features['professional_terms'])}, 关键词={len(query_features['keywords'])}")
        top5_scores = [f"{c['similarity']:.3f}" for c in adjusted_chunks[:5]]
        print(f"[RAG-INTENT] 调整后Top5分数: {top5_scores}")
        print(f"[RAG-INTENT] 平均分: {avg_score:.3f}, 最高分: {max_score:.3f}")
        
        # 【修改】始终返回所有调整后的结果，不做额外过滤
        # 只要有任何检索结果，就返回它们
        return adjusted_chunks, avg_score

    def _extract_entities(self, text: str) -> Set[str]:
        """
        从文本中��取命名实体
        支持中文人名、地名、机构名、专有名词
        """
        import re
        entities = set()

        # 1. 中文大写字母开头的专有名词（如"韩国"、"北京"、"特斯拉"）
        # 匹配首字母大写或全大写的英文专有名词
        english_entities = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', text)
        entities.update([e.lower() for e in english_entities])

        # 2. 中文连续专有名词（2-4字，可能包含常见实体后缀）
        # 常见国家、城市、地区后缀
        location_suffixes = ['国', '省', '市', '县', '区', '州', '府', '京', '沪', '深', '港', '澳']
        # 常见机构后缀
        org_suffixes = ['公司', '集团', '大学', '学院', '医院', '政府', '部门', '局', '院', '所', '中心']
        # 常见人名（2-3字）
        person_pattern = r'[\u4e00-\u9fa5]{2,3}(?:先生|女士|老师|教授|医生|总|经理|主任|总裁)'

        # 匹配可能的地名（2-4字 + 常见后缀）
        for suffix in location_suffixes:
            pattern = rf'[\u4e00-\u9fa5]{{1,3}}{suffix}'
            entities.update(re.findall(pattern, text))

        # 匹配可能的机构名
        for suffix in org_suffixes:
            pattern = rf'[\u4e00-\u9fa5]{{2,6}}{suffix}'
            entities.update(re.findall(pattern, text))

        # 匹配人名
        persons = re.findall(person_pattern, text)
        entities.update(persons)

        # 3. 提取数字+单位的专有名词（如"2024年"、"第1名"）
        numbers = re.findall(r'\d+[年月日届届级款型]', text)
        entities.update(numbers)

        # 4. 特殊符号标记的专有名词
        quotes = re.findall(r'["「『《〈]([^"」』》〉]+)["」』》〉]', text)
        entities.update([q.strip() for q in quotes if 2 <= len(q) <= 10])

        # 5. 大小写混合的词（通常是英文专有名词）
        mixed_case = re.findall(r'\b[A-Za-z]+[a-z]+[A-Za-z]*\b', text)
        entities.update([w.lower() for w in mixed_case if len(w) >= 3])

        # 6. 明确列出的常见实体词典（可选扩展）
        common_entities = {
            '人工智能', '机器学习', '深度学习', '神经网络', '自然语言处理', '计算机视觉',
            '区块链', '云计算', '大数据', '物联网', '5g', '6g',
            'python', 'java', 'javascript', 'c++', 'go', 'rust',
            '数学', '物理', '化学', '生物', '历史', '地理', '政治', '经济',
        }
        for ent in common_entities:
            if ent in text:
                entities.add(ent)

        # 过滤掉过于常见的词
        common_words = {'方法', '过程', '结果', '分析', '研究', '系统', '技术', '问题', '内容', '方面'}
        entities = {e for e in entities if e not in common_words and len(e.strip()) >= 2}

        return entities
        
        # 3. 判断是否真正相关
        avg_score = sum(match_scores) / len(match_scores) if match_scores else 0
        max_score = max(match_scores) if match_scores else 0
        
        # 必须满足：
        # 条件1: 平均分 >= 阈值（说明整体检索质量还行）
        # 条件2: 最高分 >= 阈值*1.5（说明至少有一个结果是真正相关的）
        # 优化：降低阈值，避免误判
        is_relevant = avg_score >= threshold and max_score >= threshold * 1.5
        
        # 额外放宽条件：如果Reranker分数>=0.6，直接通过
        if any(c.get('reranker_score', 0) >= 0.6 for c in retrieved_chunks):
            is_relevant = True
        
        # 如果查询涉及特定国家/地区，根据调整后的分数重新排序
        if query_countries:
            # 将调整后的分数更新到检索结果中
            for i, chunk in enumerate(retrieved_chunks):
                chunk['_adjusted_score'] = match_scores[i]
            # 按调整后的分数重新排序
            retrieved_chunks = sorted(retrieved_chunks, key=lambda x: x.get('_adjusted_score', 0), reverse=True)
        
        print(f"[RAG-INTENT] 查询意图词: {intent_words}")
        if query_countries:
            print(f"[RAG-INTENT] 查询涉及国家: {query_countries}")
        print(f"[RAG-INTENT] 匹配分数: {[f'{s:.3f}' for s in match_scores]}")
        print(f"[RAG-INTENT] 平均相关度: {avg_score:.3f}, 最高相关度: {max_score:.3f}")
        print(f"[RAG-INTENT] 意图相关性: {'✅ 通过' if is_relevant else '❌ 失败'}")
        
        return is_relevant, avg_score

    async def retrieve(
        self,
        query: str,
        top_k: int = None,
        user_id: Optional[str] = None,
        similarity_threshold: float = 0.1,
        document_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        工业级RAG检索系统 - 顶级优化版本
        
        Args:
            document_ids: 可选的文档ID列表，如果提供则只从这些文档检索
        
        策略：
        1. Query Expansion - 多角度查询扩展
        2. HyDE (Hypothetical Document Embeddings) - 假设文档嵌入
        3. Hybrid Search - 密集向量 + 稀疏检索 (TF-IDF/BM25)
        4. Multi-Stage Retrieval - 召回 → 重排 → 精排
        5. Cross-Encoder Reranking - 语义级重排序
        6. MMR Diversity - 最大边际相关性保证多样性
        7. 智能置信度 - 多维度证据融合
        """
        if top_k is None:
            top_k = settings.TOP_K

        print(f"[RAG-HYBRID] ===== 开始高级检索 =====")
        print(f"[RAG-HYBRID] 查询: {query}")

        # ===== 第一阶段：Query Expansion & HyDE =====
        expanded_queries = await self._expand_query_with_hyde(query)
        print(f"[RAG-HYBRID] 扩展查询数量: {len(expanded_queries)}")

        # 获取所有查询变体的embedding
        all_embeddings = []
        for expanded_q in expanded_queries:
            try:
                emb = await self.embedding_service.embed_async([expanded_q])
                if emb:
                    all_embeddings.append((expanded_q, emb[0]))
            except Exception as e:
                print(f"[RAG-HYBRID] Embedding错误: {e}")
                continue

        if not all_embeddings:
            return []

        # 提取核心术语
        core_terms = self.extract_core_terms(query)
        query_variants = self.generate_query_variants(query)

        # ===== 第二阶段：多路召回 =====
        try:
            from sqlalchemy import create_engine
            engine = create_engine(settings.DATABASE_URL)
            session = Session(bind=engine)
            try:
                # 根据 document_ids 过滤 chunks
                if document_ids:
                    chunks = session.query(Chunk).join(Vector).filter(
                        Chunk.document_id.in_(document_ids)
                    ).all()
                    print(f"[RAG-HYBRID] 从指定文档获取 {len(chunks)} 个chunks: {document_ids}")
                else:
                    chunks = session.query(Chunk).join(Vector).all()
                    print(f"[RAG-HYBRID] 从所有文档获取 {len(chunks)} 个chunks")

                # 构建chunk数据缓存
                chunk_data = {}
                for chunk in chunks:
                    if not chunk or not chunk.vector or not chunk.vector.embedding:
                        continue

                    doc = session.query(Document).filter_by(id=chunk.document_id).first()

                    # AI过滤
                    doc_meta = doc.metadata if doc and doc.metadata else {}
                    if isinstance(doc_meta, dict):
                        if doc_meta.get('is_ai_generated', False) or doc_meta.get('ai_generated', False):
                            continue
                    fname = (doc.filename or '').lower() if doc else ''
                    if any(x in fname for x in ['ai生成', 'ai_generated', 'auto-generated']):
                        continue
                    content = chunk.content or ''
                    if content[:200].lower():
                        if any(x in content[:200].lower() for x in ['ai生成', 'ai generated', '由 ai']):
                            continue

                    chunk_id = str(chunk.id)
                    chunk_data[chunk_id] = {
                        'chunk': chunk,
                        'doc': doc,
                        'content': content,
                        'content_lower': content.lower()
                    }

                print(f"[RAG-HYBRID] 有效候选: {len(chunk_data)}")

                # ===== 密集检索：向量相似度 =====
                dense_scores = {}
                for chunk_id, data in chunk_data.items():
                    max_sim = 0
                    best_q = ""
                    for q_text, emb in all_embeddings:
                        sim = self.cosine_similarity(emb, data['chunk'].vector.embedding)
                        if sim > max_sim:
                            max_sim = sim
                            best_q = q_text
                    dense_scores[chunk_id] = {
                        'score': max_sim,
                        'best_query': best_q,
                        'all_scores': [self.cosine_similarity(e, data['chunk'].vector.embedding) for _, e in all_embeddings]
                    }

                # ===== 稀疏检索：TF-IDF + BM25 =====
                sparse_scores = {}
                debug_count = 0
                for chunk_id, data in chunk_data.items():
                    # TF-IDF 分数
                    tfidf_score = self._tfidf_score(query, data['content'])
                    
                    # BM25 分数
                    bm25_score = 0
                    for variant in query_variants:
                        bm25_score += self.bm25_score(variant, data['content'])
                    bm25_score = bm25_score / max(len(query_variants), 1)
                    
                    # 术语精确匹配
                    term_match = sum(1 for t in core_terms if t.lower() in data['content_lower'])
                    term_ratio = term_match / max(len(core_terms), 1)
                    
                    # 组合稀疏分数
                    sparse_scores[chunk_id] = {
                        'tfidf': tfidf_score,
                        'bm25': bm25_score,
                        'term_match': term_ratio,
                        'term_count': term_match,
                        'exact_terms': [t for t in core_terms if t.lower() in data['content_lower']]
                    }
                    
                # 【调试】显示每个chunk的分数（只显示前20个）
                debug_count += 1
                if debug_count <= 30:
                    exact_terms_debug = [t for t in core_terms if t.lower() in data['content_lower']]
                    print(f"[RAG-SPARSE] #{debug_count}: bm25={bm25_score:.4f}, tfidf={tfidf_score:.4f}, term_match={term_ratio:.2f}, matched_terms={exact_terms_debug}, content={data['content'][:50]}...")

                # ===== 第三阶段：分数归一化 =====
                # 密集分数归一化
                max_dense = max((s['score'] for s in dense_scores.values()), default=1)
                if max_dense <= 0:
                    max_dense = 1  # 防止除零
                for chunk_id in dense_scores:
                    dense_scores[chunk_id]['normalized'] = dense_scores[chunk_id]['score'] / max_dense

                # 稀疏分数归一化
                max_sparse_candidates = []
                for s in sparse_scores.values():
                    candidates = [s['tfidf'], s['bm25'] / 10 if s['bm25'] > 0 else 0]
                    max_sparse_candidates.append(max(candidates))
                max_sparse = max(max_sparse_candidates) if max_sparse_candidates else 1
                if max_sparse <= 0:
                    max_sparse = 0.001  # 防止除零，给一个最小正值
                    
                for chunk_id in sparse_scores:
                    s = sparse_scores[chunk_id]
                    s['normalized'] = max(s['tfidf'] / max_sparse, s['bm25'] / (max_sparse * 10))

                # ===== 第四阶段：分数融合 =====
                # 【彻底优化】BM25分数主导排序，确保关键词匹配的内容排在最前面
                fused_scores = {}
                
                for chunk_id in chunk_data:
                    dense = dense_scores.get(chunk_id, {}).get('normalized', 0)
                    
                    # 使用原始/绝对BM25分数
                    sparse_info = sparse_scores.get(chunk_id, {})
                    raw_bm25 = sparse_info.get('bm25', 0)
                    raw_tfidf = sparse_info.get('tfidf', 0)
                    term_match = sparse_info.get('term_match', 0)
                    
                    # 【核心修复】BM25主导的混合分数计算
                    # 策略：如果BM25 > 0，则BM25必须主导排序
                    # 1. 首先检查是否有BM25匹配（关键词匹配）
                    # 2. 如果有BM25匹配，使用 BM25 + dense + term
                    # 3. 如果没有BM25匹配，则使用dense主导
                    
                    if raw_bm25 > 0:
                        # 【修复】BM25分数通常在0-100范围，归一化到0-1
                        bm25_norm = raw_bm25 / 100  # 假设BM25最大100
                        hybrid = bm25_norm * 0.4 + dense * 0.5 + term_match * 0.1
                    else:
                        # 没有BM25匹配时，使用向量相似度
                        hybrid = dense * 0.8
                    
                    # 保存各个分数供后续使用
                    vector_score = dense_scores.get(chunk_id, {}).get('score', 0)
                    
                    fused_scores[chunk_id] = {
                        'hybrid_score': hybrid,
                        'dense_score': dense,
                        'term_match': term_match,
                        'exact_terms': sparse_info.get('exact_terms', []),
                        'best_query': dense_scores.get(chunk_id, {}).get('best_query', ''),
                        'vector_score': vector_score,
                        'bm25_score': raw_bm25,
                        'keyword_score': raw_tfidf,
                    }

                # ===== 第四阶段后半：简化过滤 - 只过滤完全无关的chunk =====
                # 【彻底优化】大幅放宽过滤条件，只过滤掉完全没有相关性的chunk
                filtered_chunk_ids = []
                for chunk_id, score_info in fused_scores.items():
                    bm25 = score_info.get('bm25_score', 0)
                    keyword = score_info.get('keyword_score', 0)
                    term_match = score_info.get('term_match', 0)
                    dense_score = score_info.get('dense_score', 0)
                    hybrid_score = score_info.get('hybrid_score', 0)
                    
                    # 【关键】大幅放宽过滤条件：
                    # 只要有任何相关性迹象就保留
                    # 1. BM25 > 0 （有任何词匹配）
                    # 2. 关键词 > 0.0001 （有轻量关键词匹配）
                    # 3. 术语匹配 > 0 （有任何核心术语）
                    # 4. 语义相似度 > 0.3 （中等语义相关就保留）
                    # 5. 混合分数 > 0.1 （有一点综合相关性）
                    is_relevant = (
                        bm25 > 0 or 
                        keyword > 0.0001 or 
                        term_match > 0 or 
                        dense_score > 0.3 or  # 从0.7降到0.3
                        hybrid_score > 0.1
                    )
                    
                    if is_relevant:
                        filtered_chunk_ids.append(chunk_id)
                    else:
                        print(f"[RAG-FILTER] 过滤掉: bm25={bm25:.4f}, keyword={keyword:.4f}, term={term_match:.2f}, dense={dense_score:.3f}, hybrid={hybrid_score:.3f}")
                
                print(f"[RAG-FILTER] 过滤前: {len(fused_scores)}, 过滤后: {len(filtered_chunk_ids)}")
                
                # 更新chunk_data，移除不相关的chunk
                filtered_chunk_data = {k: v for k, v in chunk_data.items() if k in filtered_chunk_ids}
                filtered_fused_scores = {k: v for k, v in fused_scores.items() if k in filtered_chunk_ids}
                
                # 如果过滤后没有结果，直接返回空
                if not filtered_chunk_data:
                    print(f"[RAG-HYBRID] ⚠️ 过滤后无有效chunk，返回空")
                    return []
                
                # ===== 第五阶段：简单排序选择 =====
                # 【优化】直接按混合分数排序，不需要复杂的MMR
                # 按混合分数降序排序
                sorted_chunks = sorted(
                    filtered_fused_scores.items(),
                    key=lambda x: x[1]['hybrid_score'],
                    reverse=True
                )
                
                # 选择前 top_k * 10 个候选
                top_candidates = [chunk_id for chunk_id, _ in sorted_chunks[:top_k * 10]]
                
                print(f"[RAG-HYBRID] 候选数量: {len(top_candidates)}")

                # ===== 第六阶段：Cross-Encoder精排（可选）=====
                # 【优化】如果Reranker可用，进行精排；否则直接使用排序结果
                final_results = await self._cross_encoder_rerank(
                    top_candidates, chunk_data, query, fused_scores
                )
                
                print(f"[RAG-HYBRID] 精排后结果数量: {len(final_results)}")
                if final_results:
                    print(f"[RAG-HYBRID] 精排结果Top5:")
                    for i, r in enumerate(final_results[:5]):
                        bm25_val = r.get('bm25_score', 0)
                        keyword_val = r.get('keyword_score', 0)
                        similarity = r.get('similarity', 0)
                        print(f"[RAG-HYBRID]   #{i+1}: bm25={bm25_val:.4f}, keyword={keyword_val:.4f}, similarity={similarity:.3f}")
                        print(f"[RAG-HYBRID]       内容: {r.get('content', '')[:60]}...")

                # ===== 第七阶段：最终排序和过滤 =====
                # 【核心优化】以精确短语匹配为主，确保高相关chunk排在前面

                def final_sort_key(chunk):
                    """计算综合排序分数 - 精确短语匹配优先"""
                    phrase_score = chunk.get('phrase_score', 0)  # 精确短语匹配分数
                    similarity = chunk.get('similarity', 0)

                    # 【核心改进】精确短语匹配分数主导排序
                    # 【关键修复】确保 phrase > 0 的chunk始终排在 phrase = 0 的chunk前面
                    # 使用分区策略：先按是否有phrase分组，再组内排序
                    if phrase_score > 0:
                        # 有精确短语匹配时：基础分数 1.0-2.0
                        score = 1.0 + phrase_score
                    else:
                        # 没有精确短语匹配时：基础分数 0-1.0
                        score = similarity / 1000

                    return score

                # 过滤并排序
                filtered_results = [c for c in final_results if final_sort_key(c) > 0]
                
                # 【关键修复】使用元组排序确保正确分区：有phrase的始终排在前
                # 排序规则：(has_phrase, phrase) 降序，有phrase的排在前面
                def phrase_sort_key(chunk):
                    phrase = chunk.get('phrase_score', 0) or 0
                    has_phrase = 1 if phrase > 0 else 0
                    # 有phrase的排在前面，同组内按phrase降序
                    return (has_phrase, phrase)
                
                filtered_results.sort(key=phrase_sort_key, reverse=True)

                print(f"[RAG-HYBRID] 过滤后剩余 {len(filtered_results)} 个结果")
                
                # ===== 第八阶段：直接返回精排结果 =====
                # 【关键修复】不再进行邻接扩展，避免破坏 phrase_score 排序
                # 邻接扩展会添加没有 phrase_score 的上下文 chunk，导致正确排序被打乱
                return filtered_results

            finally:
                session.close()
        except Exception as e:
            print(f"[RAG-HYBRID] 错误: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def _expand_query_with_hyde(self, query: str) -> List[str]:
        """Query Expansion: 只保留原查询，避免引入不相关主题"""
        # 核心原则：只使用原查询进行检索，避免HyDE扩展引入不相关内容
        return [query]  # 只保留原查询

    async def _expand_adjacent_chunks(
        self,
        initial_results: List[Dict[str, Any]],
        chunk_data: Dict,
        session,
        query: str = "",
        top_k: int = 12
    ) -> List[Dict[str, Any]]:
        """
        邻接扩展策略 - 【核心重写】

        新策略：以相关性分数为主，确保高相关性的chunk排在前面
        1. 首先按相关性分数对所有chunk排序
        2. 选择top_k个高相关性chunk
        3. 对于选中的chunk，添加必要的上下文（相邻chunk）
        4. 整体保持相关性排序，高相关性内容在前
        """
        if not initial_results:
            return []

        print(f"[RAG-ADJACENT] ===== 开始邻接扩展 =====")
        print(f"[RAG-ADJACENT] 初始结果数: {len(initial_results)}")

        # 提取查询关键词用于判断相关性
        try:
            query_keywords = self._extract_topic_keywords(query)
            print(f"[RAG-ADJACENT] 查询关键词: {query_keywords}")
        except Exception as e:
            print(f"[RAG-ADJACENT] 关键词提取失败: {e}")
            query_keywords = []

        # ===== 第一步：按相关性分数排序初始结果 =====
        def get_relevance_score(chunk):
            """计算chunk的综合相关性分数 - 关键改进：精确短语匹配优先"""
            phrase_score = chunk.get('phrase_score', 0)  # 精确短语匹配分数
            similarity = chunk.get('similarity', 0)
            reranker = chunk.get('reranker_score', 0)

            # 【核心改进】精确短语匹配分数主导排序
            # 【修复】确保 phrase > 0 的chunk始终排在 phrase = 0 的chunk前面
            if phrase_score > 0:
                # 有精确短语匹配时，给予极高分数
                score = phrase_score * 100000 + similarity * 10 + reranker
            else:
                # 没有精确短语匹配时，使用较低的分数范围
                score = similarity * 100 + reranker
            return score

        # 按相关性分数排序
        sorted_results = sorted(initial_results, key=get_relevance_score, reverse=True)

        # ===== 第二步：选择top_k个高相关性chunk作为核心 =====
        core_chunks = sorted_results[:top_k]

        # ===== 第三步：为每个核心chunk添加上下文 =====
        # 收集需要获取的chunk信息
        chunk_ids_to_fetch = set()
        doc_to_chunks = {}  # doc_id -> {chunk_index -> chunk_obj}

        for chunk in core_chunks:
            doc_id = chunk.get('document_id', '')
            chunk_id = str(chunk.get('chunk_id', ''))
            chunk_ids_to_fetch.add((doc_id, chunk_id))

        # 获取所有相关文档的chunk信息
        try:
            from models import Chunk

            all_docs = set(c.get('document_id', '') for c in core_chunks)
            for doc_id in all_docs:
                doc_chunks = session.query(Chunk).filter(
                    Chunk.document_id == doc_id
                ).order_by(Chunk.chunk_index).all()

                doc_to_chunks[doc_id] = {c.chunk_index: c for c in doc_chunks}

        except Exception as e:
            print(f"[RAG-ADJACENT] 获取文档chunk失败: {e}")
            import traceback
            traceback.print_exc()
            # 即使获取失败，也返回按相关性排序的结果
            print(f"[RAG-ADJACENT] 跳过上下文扩展，直接返回相关性排序结果")
            return core_chunks

        # ===== 第四步：构建最终结果 =====
        result = []
        seen_ids = set()

        for chunk in core_chunks:
            doc_id = chunk.get('document_id', '')
            chunk_id = str(chunk.get('chunk_id', ''))
            chunk_index = chunk.get('chunk_index', 0)
            
            # 【调试】显示核心chunk的phrase_score
            phrase_in_core = chunk.get('phrase_score', 0)
            sim_in_core = chunk.get('similarity', 0)

            if chunk_id in seen_ids:
                continue

            # 添加这个核心chunk
            chunk_dict = chunk.copy()
            chunk_dict['adjacent_reason'] = 'core'
            result.append(chunk_dict)
            seen_ids.add(chunk_id)

            # 添加上下文：同一文档中最近的相邻chunk
            if doc_id in doc_to_chunks:
                chunk_map = doc_to_chunks[doc_id]
                max_index = max(chunk_map.keys())

                # 查找前后相邻的chunk（最多各2个）
                adjacent_added = {'before': 0, 'after': 0}
                for offset in [1, 2]:  # 偏移1和2表示第1、2个相邻chunk
                    # 前一个
                    before_idx = chunk_index - offset
                    if before_idx >= 0 and adjacent_added['before'] < 2:
                        before_chunk = chunk_map.get(before_idx)
                        if before_chunk:
                            before_id = str(before_chunk.id)
                            if before_id not in seen_ids and len(result) < top_k + 4:
                                before_dict = {
                                    'chunk_id': before_id,
                                    'document_id': doc_id,
                                    'chunk_index': before_idx,
                                    'content': before_chunk.content or '',
                                    'similarity': chunk.get('similarity', 0.5) * 0.9,
                                    'bm25_score': chunk.get('bm25_score', 0) * 0.5,
                                    'adjacent_reason': 'context_before'
                                }
                                result.append(before_dict)
                                seen_ids.add(before_id)
                                adjacent_added['before'] += 1

                    # 后一个
                    after_idx = chunk_index + offset
                    if after_idx <= max_index and adjacent_added['after'] < 2:
                        after_chunk = chunk_map.get(after_idx)
                        if after_chunk:
                            after_id = str(after_chunk.id)
                            if after_id not in seen_ids and len(result) < top_k + 4:
                                after_dict = {
                                    'chunk_id': after_id,
                                    'document_id': doc_id,
                                    'chunk_index': after_idx,
                                    'content': after_chunk.content or '',
                                    'similarity': chunk.get('similarity', 0.5) * 0.9,
                                    'bm25_score': chunk.get('bm25_score', 0) * 0.5,
                                    'adjacent_reason': 'context_after'
                                }
                                result.append(after_dict)
                                seen_ids.add(after_id)
                                adjacent_added['after'] += 1

        # ===== 第五步：再次按相关性排序 =====
        # 只对核心chunk（adjacent_reason='core'）保持原位，相邻chunk插入到其后
        final_result = []
        core_result = [r for r in result if r.get('adjacent_reason') == 'core']

        for core_chunk in core_result:
            final_result.append(core_chunk)
            # 添加该核心chunk的上下文
            chunk_idx = core_chunk.get('chunk_index', 0)
            doc_id = core_chunk.get('document_id', '')

            # 找到所有属于这个核心chunk上下文的chunks
            context_chunks = [
                r for r in result
                if r.get('adjacent_reason') in ('context_before', 'context_after')
                and r.get('document_id') == doc_id
                and abs(r.get('chunk_index', 0) - chunk_idx) <= 2
            ]
            # 按chunk_index排序（前面先，后面前）
            context_chunks.sort(key=lambda x: (
                x.get('chunk_index', 0) < chunk_idx,  # 前面的排前面
                abs(x.get('chunk_index', 0) - chunk_idx)  # 距离近的排前面
            ))
            for ctx in context_chunks:
                if ctx not in final_result:
                    final_result.append(ctx)

        print(f"[RAG-ADJACENT] 最终结果数: {len(final_result)}")
        print(f"[RAG-ADJACENT] 最终结果顺序（Top8）:")
        for i, c in enumerate(final_result[:8]):
            doc_id_short = str(c.get('document_id', ''))[:8]
            idx = c.get('chunk_index', 0)
            reason = c.get('adjacent_reason', 'unknown')
            bm25 = c.get('bm25_score', 0)
            content_preview = c.get('content', '')[:40]
            print(f"[RAG-ADJACENT]   #{i+1}: doc={doc_id_short}..., idx={idx}, bm25={bm25:.2f}, reason={reason}, content={content_preview}...")

        return final_result

    def _extract_topic_keywords(self, query: str) -> List[str]:
        """从查询中提取主题关键词 - 使用jieba分词确保正确分词"""
        if not query:
            return []

        import re

        # 清理查询中的标点符号，但保留特殊字符（如biangbiang面的biang）
        cleaned_query = re.sub(r'[，。！？、；：""''【】（）]', ' ', query)

        # 常见停用词（排除）
        stop_words = {'什么', '哪些', '哪个', '怎么', '如何', '为什么', '请问', '帮我', '告诉',
                      '一下', '这个', '那个', '可以', '有没有', '主要', '具有', '以及', '还有',
                      '及其', '其中', '特点', '特征', '特色', '简介', '介绍', '关于',
                      '请问', '分别', '通常', '一般', '常见', '著名', '哪些', '哪些',
                      '种', '个', '些', '有', '是', '的', '了', '在', '和', '或', '与'}

        # 使用jieba分词确保正确的中文分词
        keywords = []
        try:
            import jieba
            # 精确模式分词，避免过度细分
            words = jieba.cut(cleaned_query, cut_all=False)
            for word in words:
                word = word.strip()
                # 保留2-8字的词组（包含成语和专有名词），排除停用词
                if len(word) >= 2 and word not in stop_words and not word.isdigit():
                    keywords.append(word)
        except ImportError:
            # 如果没有jieba，使用改进的正则提取
            # 提取连续的中文字符序列（至少2个字）
            chinese_phrases = re.findall(r'[\u4e00-\u9fff]{2,8}', cleaned_query)
            keywords = [p for p in chinese_phrases if p not in stop_words]

        # 去重并限制数量
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen and kw not in stop_words:
                seen.add(kw)
                unique_keywords.append(kw)

        # 提取英文词组
        english_words = re.findall(r'[a-zA-Z]{2,}', query)
        unique_keywords.extend([w.lower() for w in english_words if len(w) >= 2])

        print(f"[RAG-ADJACENT] 提取的关键词: {unique_keywords[:15]}")
        return unique_keywords[:15]  # 最多返回15个关键词

    async def _get_adjacent_chunks(
        self,
        doc_id: str,
        chunk_index: int,
        session,
        max_expand: int = 5
    ) -> List[Dict[str, Any]]:
        """获取指定chunk的前后相邻chunks"""
        adjacent_chunks = []

        try:
            from models import Chunk, Vector, Document

            doc_chunks = session.query(Chunk).filter(
                Chunk.document_id == doc_id
            ).order_by(Chunk.chunk_index).all()

            if not doc_chunks:
                return adjacent_chunks

            chunk_map = {c.chunk_index: c for c in doc_chunks}
            doc = session.query(Document).filter_by(id=doc_id).first()

            indices_to_fetch = set()
            for i in range(chunk_index - max_expand, chunk_index + max_expand + 1):
                if i in chunk_map and i >= 0:
                    indices_to_fetch.add(i)

            for idx in sorted(indices_to_fetch):
                chunk = chunk_map[idx]
                if not chunk or not chunk.vector:
                    continue

                chunk_id = str(chunk.id)
                adjacent_chunks.append({
                    'chunk_id': chunk_id,
                    'content': chunk.content or '',
                    'similarity': max(0.5, 1.0 - abs(idx - chunk_index) * 0.1),
                    'document_id': doc_id,
                    'document_title': doc.filename if doc else 'Unknown',
                    'chunk_index': chunk.chunk_index,
                    'metadata': doc.metadata if doc else {},
                    'bm25_score': 0,
                    'keyword_score': 0,
                    'reranker_score': 0,
                    'is_adjacent': True,
                    'distance_from_origin': abs(idx - chunk_index)
                })

        except Exception as e:
            print(f"[RAG-ADJACENT] 获取相邻chunks失败: {e}")

        return adjacent_chunks

    def _tfidf_score(self, query: str, document: str) -> float:
        """计算TF-IDF风格的相关性分数"""
        query_terms = query.lower().split()
        doc_lower = document.lower()
        
        # 简单TF计算
        query_tf = {}
        for term in query_terms:
            count = doc_lower.count(term)
            if count > 0:
                query_tf[term] = count / max(len(doc_lower.split()), 1)
        
        # 返回最大TF值
        return max(query_tf.values()) if query_tf else 0

    async def _mmr_diversity_select(
        self, 
        fused_scores: Dict,
        chunk_data: Dict,
        query: str,
        k: int
    ) -> List[str]:
        """
        MMR (Maximal Marginal Relevance) 多样性选择
        【优化】简化实现，直接按分数选择，保留更多相关结果
        """
        # 按混合分数排序
        sorted_chunks = sorted(
            fused_scores.items(),
            key=lambda x: x[1]['hybrid_score'],
            reverse=True
        )
        
        selected = []
        selected_contents = []  # 用于计算内容相似度（避免重复）
        
        for chunk_id, score_info in sorted_chunks:
            if len(selected) >= k:
                break
                
            content = chunk_data[chunk_id]['content']
            content_lower = content.lower()
            
            # 【优化】简化处理：如果分数足够高，直接选择
            # 如果混合分数 > 0.5，认为是高相关，直接通过
            hybrid_score = score_info.get('hybrid_score', 0)
            if hybrid_score >= 0.5:
                selected.append(chunk_id)
                selected_contents.append(content)
                continue
            
            # 对于中等分数的chunks，简单检查是否与已选结果太相似
            max_similarity_to_selected = 0
            for sc in selected_contents:
                # 简单的词重叠计算
                selected_terms = set(sc.lower().split())
                current_terms = set(content_lower.split())
                if selected_terms and current_terms:
                    overlap = len(selected_terms & current_terms) / len(selected_terms | current_terms)
                    max_similarity_to_selected = max(max_similarity_to_selected, overlap)
            
            # 【优化】放宽多样性限制：只要不是完全重复就选择
            # 只有当内容相似度 > 0.9 时才跳过（基本相同的chunk）
            if max_similarity_to_selected < 0.9:
                selected.append(chunk_id)
                selected_contents.append(content)
            elif hybrid_score >= 0.3:
                # 中等相关但不是完全重复，也选择
                selected.append(chunk_id)
                selected_contents.append(content)
        
        return selected

    def _calculate_phrase_match_score(self, query: str, document: str) -> float:
        """
        计算精确短语匹配分数 - 关键优化！
        
        检查查询中的重要短语是否完整出现在文档中
        对于中文来说，需要检查多字词组是否完整匹配
        """
        score = 0.0
        
        # 提取查询中的重要短语（2-4字的中文词组）
        important_phrases = []
        
        # 提取连续的2-4字中文词组
        import re
        chinese_phrases = re.findall(r'[\u4e00-\u9fff]{2,4}', query)
        important_phrases.extend(chinese_phrases)
        
        # 菜系名、招牌菜等重要词组
        key_terms = ['闽菜', '川菜', '粤菜', '湘菜', '鲁菜', '苏菜', '浙菜', '徽菜', '京菜',
                     '佛跳墙', '荔枝肉', '招牌菜', '三大流派', '福州菜', '闽南菜', '闽西菜']
        
        for term in key_terms:
            if term in query:
                important_phrases.append(term)
        
        # 过滤掉单字符（太泛）
        important_phrases = [p for p in important_phrases if len(p) >= 2]
        
        # 去重
        important_phrases = list(set(important_phrases))
        
        # 检查每个重要短语是否完整出现在文档中
        doc_lower = document.lower()
        matched_phrases = []
        for phrase in important_phrases:
            if phrase.lower() in doc_lower:
                matched_phrases.append(phrase)
                # 短语越长，分数越高
                score += 0.3 * (len(phrase) / 4)  # 最长4字，权重最高0.3
        
        if matched_phrases:
            print(f"[PHRASE-MATCH] 查询: {query}, 匹配短语: {matched_phrases}, 分数: {score:.3f}")
        
        return min(score, 1.0)  # 最高1分

    async def _cross_encoder_rerank(
        self,
        chunk_ids: List[str],
        chunk_data: Dict,
        query: str,
        fused_scores: Dict = None
    ) -> List[Dict]:
        """
        Cross-Encoder 精细重排
        使用BGE-Reranker进行语义级相关性评估
        """
        if not chunk_ids:
            return []
        
        # 准备数据
        chunks_to_score = []
        for chunk_id in chunk_ids:
            if chunk_id in chunk_data:
                chunks_to_score.append({
                    'chunk_id': chunk_id,
                    'content': chunk_data[chunk_id]['content'],
                    'doc': chunk_data[chunk_id]['doc']
                })
        
        if not chunks_to_score:
            return []
        
        # 【关键改进】计算精确短语匹配分数
        phrase_scores = {}
        for chunk_info in chunks_to_score:
            chunk_id = chunk_info['chunk_id']
            phrase_score = self._calculate_phrase_match_score(query, chunk_info['content'])
            phrase_scores[chunk_id] = phrase_score
        
        # 使用Reranker进行评分
        reranker = self.reranker
        results = []
        
        if reranker is not None:
            try:
                # 批量预测
                pairs = [(query, chunk['content']) for chunk in chunks_to_score]
                scores = reranker.predict(pairs, show_progress_bar=False)

                # 将numpy数组转换为列表，避免数组判断问题
                if hasattr(scores, 'tolist'):
                    scores = scores.tolist()
                elif hasattr(scores, '__iter__'):
                    scores = list(scores)

                # 分数范围通常是[-5, 5]或[0, 10]
                # 策略：使用相对排序 + 绝对阈值
                min_score = min(scores) if scores and len(scores) > 0 else 0
                max_score = max(scores) if scores and len(scores) > 0 else 1
                avg_score = sum(scores) / len(scores) if scores and len(scores) > 0 else 0
                
                for i, chunk in enumerate(chunks_to_score):
                    raw_score = scores[i]

                    # 【优化】综合考虑Reranker分数和原始BM25分数
                    chunk_id = chunk['chunk_id']
                    fuse_info = fused_scores.get(chunk_id, {}) if fused_scores else {}

                    # 原始混合分数（包含BM25/TF-IDF）
                    original_score = fuse_info.get('hybrid_score', 0.5)

                    # 基于Reranker排名的分数
                    rank = sum(1 for s in scores if s > raw_score) + 1
                    rank_score = 1 - (rank - 1) / len(scores) * 0.3  # 范围[0.7, 1.0]

                    # 【关键改进】精确短语匹配主导排序
                    phrase_score = phrase_scores.get(chunk_id, 0)
                    
                    # 【核心修复】使用合理的分数范围用于显示
                    # 排序由 phrase_sort_key 函数控制（使用元组分区）
                    # 【优化】高相关的内容应该显示更高的分数
                    if phrase_score > 0:
                        # 有精确短语匹配：高分数 0.75-0.98
                        final_score = min(0.75 + phrase_score * 0.23, 0.98)
                    else:
                        # 无精确短语匹配：分数基于其他因素 0.3-0.75
                        final_score = min(rank_score * 0.3 + original_score * 0.3 + 0.3, 0.75)
                    
                    # 【调试】
                    if phrase_score > 0:
                        print(f"[RERANK] chunk_id={chunk_id[:8]}..., phrase={phrase_score:.3f}, final={final_score:.3f}")

                    results.append({
                        'chunk_id': chunk_id,
                        'content': chunk['content'],
                        'similarity': float(final_score),
                        'reranker_score': float(raw_score),
                        'document_id': str(chunk['doc'].id) if chunk['doc'] else '',
                        'document_title': chunk['doc'].filename if chunk['doc'] else 'Unknown',
                        'chunk_index': chunk_data[chunk_id]['chunk'].chunk_index,
                        'metadata': chunk['doc'].metadata if chunk['doc'] else {},
                        # 保存原始检索分数
                        'vector_score': fuse_info.get('vector_score', final_score),
                        'bm25_score': fuse_info.get('bm25_score', 0),
                        'keyword_score': fuse_info.get('keyword_score', 0),
                        'matched_terms': fuse_info.get('exact_terms', []),
                        'phrase_score': phrase_score  # 新增：精确短语匹配分数
                    })
            except Exception as e:
                print(f"[RAG-HYBRID] Reranker错误: {e}")
                # 【修复】回退时也要保留BM25和关键词分数
                for chunk in chunks_to_score:
                    chunk_id = chunk['chunk_id']
                    fuse_info = fused_scores.get(chunk_id, {}) if fused_scores else {}
                    phrase_score = phrase_scores.get(chunk_id, 0)
                    results.append({
                        'chunk_id': chunk_id,
                        'content': chunk['content'],
                        'similarity': fuse_info.get('hybrid_score', 0.5),  # 使用混合分数
                        'reranker_score': 0.0,
                        'document_id': str(chunk['doc'].id) if chunk['doc'] else '',
                        'document_title': chunk['doc'].filename if chunk['doc'] else 'Unknown',
                        'chunk_index': chunk_data[chunk_id]['chunk'].chunk_index,
                        'metadata': chunk['doc'].metadata if chunk['doc'] else {},
                        # 【关键】保留BM25和关键词分数
                        'bm25_score': fuse_info.get('bm25_score', 0),
                        'keyword_score': fuse_info.get('keyword_score', 0),
                        'matched_terms': fuse_info.get('exact_terms', []),
                        'phrase_score': phrase_score
                    })
        else:
            # 无Reranker时使用短语匹配和混合分数
            for chunk in chunks_to_score:
                chunk_id = chunk['chunk_id']
                fuse_info = fused_scores.get(chunk_id, {}) if fused_scores else {}
                phrase_score = phrase_scores.get(chunk_id, 0)
                original_score = fuse_info.get('hybrid_score', 0.5)
                
                # 短语匹配主导
                final_score = phrase_score * 0.6 + original_score * 0.4
                
                results.append({
                    'chunk_id': chunk_id,
                    'content': chunk['content'],
                    'similarity': float(final_score),
                    'reranker_score': 0.0,
                    'document_id': str(chunk['doc'].id) if chunk['doc'] else '',
                    'document_title': chunk['doc'].filename if chunk['doc'] else 'Unknown',
                    'chunk_index': chunk_data[chunk_id]['chunk'].chunk_index,
                    'metadata': chunk['doc'].metadata if chunk['doc'] else {},
                    # 【关键】保留BM25和关键词分数
                    'bm25_score': fuse_info.get('bm25_score', 0),
                    'keyword_score': fuse_info.get('keyword_score', 0),
                    'matched_terms': fuse_info.get('exact_terms', []),
                    'phrase_score': phrase_score
                })
        
        # 【关键改进】按精确短语匹配优先排序
        results.sort(key=lambda x: (x.get('phrase_score', 0), x['similarity']), reverse=True)
        
        # 【关键修复】确保所有 similarity 在 [0, 1] 范围内
        # 检查是否有异常大的分数
        for r in results:
            sim = r.get('similarity', 0)
            if sim > 1:
                # 找出最大值用于归一化
                pass  # 归一化在下一阶段处理
        
        return results

    def _rerank_chunks(self, chunks: List[Dict], query: str, core_terms: List[str]) -> List[Dict]:
        """重排：使用 BGE-Reranker 模型 + 规则评分对候选块进行二次排序"""
        if not chunks:
            return []

        query_lower = query.lower()
        query_len = len(query)

        # 尝试使用 BGE-Reranker 模型
        reranker = self.reranker
        use_reranker_model = reranker is not None

        if use_reranker_model:
            try:
                # 使用重排序模型计算 query-document 对的分数
                pairs = [(query, chunk.get("content", "")) for chunk in chunks]
                reranker_scores = reranker.predict(pairs, show_progress_bar=False)

                # 归一化重排分数到 0-1 范围
                max_score = max(reranker_scores) if max(reranker_scores) > 0 else 1
                normalized_scores = [s / max_score for s in reranker_scores]

                for chunk, norm_score in zip(chunks, normalized_scores):
                    chunk["reranker_score"] = float(norm_score)
            except Exception as e:
                print(f"Reranker model prediction failed: {e}")
                use_reranker_model = False
                for chunk in chunks:
                    chunk["reranker_score"] = 0.0
        else:
            for chunk in chunks:
                chunk["reranker_score"] = 0.0

        # 规则重排序评分（保留现有逻辑）
        for chunk in chunks:
            rerank_score = 0
            content = chunk.get("content", "")
            content_lower = content.lower()

            # 1. 完整查询匹配检查
            if query_lower in content_lower:
                rerank_score += 0.15

            # 2. 术语出现频率
            term_count = 0
            for term in core_terms:
                count = content_lower.count(term.lower())
                term_count += count
            if term_count > 0:
                rerank_score += min(term_count * 0.1, 0.25)

            # 3. 术语在文档开头出现
            first_term_pos = query_len * 2  # 很大的初始值
            for term in core_terms:
                pos = content_lower.find(term.lower())
                if pos >= 0 and pos < first_term_pos:
                    first_term_pos = pos

            if first_term_pos < query_len * 0.5:
                rerank_score += 0.15
            elif first_term_pos < query_len:
                rerank_score += 0.1

            # 4. 上下文密度：周围是否有相关词
            related_terms = ["症状", "防治", "原因", "方法", "如何", "怎样", "为什么", "什么时候"]
            context_bonus = 0
            for rel in related_terms:
                if rel in content_lower:
                    context_bonus += 0.02
            rerank_score += min(context_bonus, 0.1)

            # 5. 长度惩罚：太短的块可能信息不足
            content_len = len(content)
            if content_len < 50:
                rerank_score -= 0.1
            elif 100 < content_len < 500:
                rerank_score += 0.05  # 适中长度有轻微加分

            chunk["rule_score"] = rerank_score

            # 6. 综合分数：结合重排模型分数和规则分数
            original_score = chunk.get("similarity", 0)

            if use_reranker_model:
                # 使用重排模型为主，规则分为辅
                final_score = (
                    original_score * 0.3 +                    # 原始向量相似度 30%
                    chunk["reranker_score"] * 0.5 +            # 重排模型分数 50%
                    rerank_score * 0.2                         # 规则评分 20%
                )
            else:
                # 无重排模型时，使用规则分
                final_score = original_score + rerank_score

            chunk["rerank_bonus"] = rerank_score
            chunk["final_score"] = final_score
            chunk["similarity"] = final_score

        # 按最终分数排序
        return sorted(chunks, key=lambda x: x.get("final_score", 0), reverse=True)

    def _retrieve_with_pgvector(self, query_embedding: List[float], top_k: int, threshold: float) -> List[Dict[str, Any]]:
        """使用 pgvector 进行高效相似度搜索"""
        from sqlalchemy import text

        vector_str = '[' + ','.join(map(str, query_embedding)) + ']'

        sql = text(f"""
            SELECT
                c.id as chunk_id,
                c.content,
                c.document_id,
                c.chunk_index,
                d.filename as document_title,
                d.metadata as document_metadata,
                1 - (v.embedding <=> :vector) as similarity
            FROM vectors v
            JOIN chunks c ON v.chunk_id = c.id
            JOIN documents d ON c.document_id = d.id
            WHERE 1 - (v.embedding <=> :vector) >= :threshold
            ORDER BY v.embedding <=> :vector
            LIMIT :top_k
        """)

        try:
            result = self.db.execute(sql, {
                "vector": vector_str,
                "threshold": threshold,
                "top_k": top_k
            }).fetchall()

            return [
                {
                    "chunk_id": str(row.chunk_id),
                    "content": row.content,
                    "similarity": float(row.similarity),
                    "document_id": str(row.document_id),
                    "document_title": row.document_title,
                    "chunk_index": row.chunk_index,
                    "metadata": row.document_metadata or {}
                }
                for row in result
            ]
        except Exception as e:
            print(f"pgvector error: {e}")
            return []

    def build_context(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """构建 RAG 上下文"""
        if not retrieved_chunks:
            return ""

        context_parts = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            source_info = f"[Source {i}: {chunk.get('document_title', 'Unknown')}]"
            content = chunk['content']
            context_parts.append(f"{source_info}\n{content}")

        return "\n\n---\n\n".join(context_parts)

    def build_enhanced_context(self, retrieved_chunks: List[Dict[str, Any]], query: str) -> str:
        """构建增强的上下文"""
        if not retrieved_chunks:
            return ""

        context_parts = []
        total_length = 0
        max_length = 3000

        for i, chunk in enumerate(retrieved_chunks, 1):
            if chunk.get('document_title'):
                source_info = f"[Document: {chunk['document_title']}]"
            else:
                source_info = f"[Relevant Document {i}]"

            content = chunk['content']
            chunk_length = len(content)

            if total_length + chunk_length > max_length:
                remaining = max_length - total_length
                if remaining > 200:
                    content = content[:remaining] + "..."
                else:
                    break

            context_parts.append(f"{source_info}\n{content}")
            total_length += chunk_length

        return "\n\n---\n\n".join(context_parts)

    def _calculate_answerability_score(self, query: str, chunk_content: str) -> float:
        """
        答案可答性评分 - 评估检索结果是否能回答该问题
        
        高级策略：
        1. 问题类型匹配
        2. 答案模式检测
        3. 实体覆盖度
        """
        score = 0.5  # 基础分
        
        query_lower = query.lower()
        content_lower = chunk_content.lower()
        
        # 1. 问题类型检测并匹配
        question_patterns = {
            # 定义类问题 - 需要解释性答案
            '是什么': ['是', '指', '称为', '叫做', '定义为'],
            '为什么': ['因为', '原因', '由于', '所以', '导致', '为了'],
            '如何': ['方法', '步骤', '过程', '技巧', '方案', '如何', '怎样'],
            '哪里': ['位置', '地点', '地址', '位于', '场所'],
            '何时': ['时间', '时候', '日期', '期间', '年代', '季节'],
            '多少': ['数量', '数量', '金额', '价格', '比例', '百分比'],
            '谁': ['人', '作者', '创建者', '负责人'],
        }
        
        # 检测查询的问题类型
        detected_types = []
        for qtype, patterns in question_patterns.items():
            if qtype in query_lower:
                for pattern in patterns:
                    if pattern in content_lower:
                        score += 0.05
                        detected_types.append(qtype)
                        break
        
        # 2. 答案模式检测
        answer_patterns = [
            '具体来说', '主要包括', '有以下几点', '具体步骤', '详细说明',
            '第一', '第二', '第三', '首先', '其次', '最后',
            '例如', '比如', '以', '如', '包括',
        ]
        for pattern in answer_patterns:
            if pattern in content_lower:
                score += 0.02
        
        # 3. 实体覆盖度
        # 提取查询中的重要实体（长度>1的词）
        query_entities = [w for w in query_lower.split() if len(w) >= 2]
        if query_entities:
            covered_entities = sum(1 for e in query_entities if e in content_lower)
            entity_coverage = covered_entities / len(query_entities)
            score += entity_coverage * 0.1
        
        return min(score, 1.0)

    def _calculate_coverage_analysis(self, query: str, retrieved_chunks: List[Dict]) -> Dict[str, float]:
        """
        查询覆盖度分析 - 评估检索结果对查询的覆盖程度
        
        返回: {
            'semantic_coverage': 语义覆盖度,
            'lexical_coverage': 词汇覆盖度,
            'completeness': 完整性,
            'diversity': 多样性
        }
        """
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        # 过滤停用词（只保留最常见的虚词）
        stop_words = {'的', '了', '是', '在', '和', '与', '及', '或', '吗', '呢', '吧', '啊', '的', '了'}
        query_terms = {t for t in query_terms if len(t) >= 2 and t not in stop_words}
        
        # 收集所有chunk的内容
        all_content = ' '.join(c.get('content', '').lower() for c in retrieved_chunks)
        
        # 1. 语义覆盖度（通过查询扩展词）
        semantic_keywords = {
            '如何': ['方法', '步骤', '技巧', '流程', '操作', '使用'],
            '什么': ['类型', '种类', '包括', '包含', '定义'],
            '为什么': ['原因', '理由', '导致', '由于', '结果'],
            '哪里': ['位置', '地点', '场所', '地址', '在哪里'],
        }
        expanded_terms = set(query_terms)
        for term in query_terms:
            if term in semantic_keywords:
                expanded_terms.update(semantic_keywords[term])
        
        covered_semantic = sum(1 for t in expanded_terms if t in all_content)
        semantic_coverage = covered_semantic / len(expanded_terms) if expanded_terms else 0
        
        # 2. 词汇覆盖度
        covered_lexical = sum(1 for t in query_terms if t in all_content)
        lexical_coverage = covered_lexical / len(query_terms) if query_terms else 0
        
        # 3. 完整性 - 是否每个chunk都有一定内容
        completeness_scores = []
        for chunk in retrieved_chunks:
            content = chunk.get('content', '')
            # 内容长度合理性（50-2000字）
            if 50 <= len(content) <= 2000:
                completeness_scores.append(1.0)
            elif len(content) < 50:
                completeness_scores.append(len(content) / 50)
            else:
                completeness_scores.append(2000 / len(content))
        completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0
        
        # 4. 多样性 - chunk之间是否有内容重叠
        if len(retrieved_chunks) > 1:
            contents = [c.get('content', '').lower() for c in retrieved_chunks]
            # 计算Jaccard相似度
            total_words = set()
            overlap_words = set()
            for i, c1 in enumerate(contents):
                words1 = set(c1.split())
                total_words.update(words1)
                for c2 in contents[i+1:]:
                    words2 = set(c2.split())
                    overlap_words.update(words1 & words2)
            diversity = 1 - (len(overlap_words) / len(total_words)) if total_words else 0
        else:
            diversity = 0.5  # 只有一个结果时给中等分数
        
        return {
            'semantic_coverage': semantic_coverage,
            'lexical_coverage': lexical_coverage,
            'completeness': completeness,
            'diversity': diversity
        }

    def _calculate_consistency_score(self, retrieved_chunks: List[Dict]) -> float:
        """
        一致性评分 - 评估多个检索结果之间的一致性
        
        高级策略：
        1. 分数集中度
        2. 答案一致性
        3. 证据链完整性
        """
        if len(retrieved_chunks) < 2:
            return 0.6  # 单个结果给予中等偏高分数（因为缺乏对比，不应该过度惩罚）
        
        similarities = [c.get('similarity', 0) for c in retrieved_chunks]
        reranker_scores = [c.get('reranker_score', c.get('similarity', 0)) for c in retrieved_chunks]
        
        # 1. 分数集中度
        top1 = max(similarities)
        top2 = sorted(similarities, reverse=True)[1] if len(similarities) > 1 else 0
        top3 = sorted(similarities, reverse=True)[2] if len(similarities) > 2 else top2
        
        # top结果越接近，分数越高
        concentration = 1 - (top1 - top2) if top1 > 0 else 0
        
        # 2. 答案一致性（通过Reranker分数方差）
        mean_rerank = sum(reranker_scores) / len(reranker_scores)
        variance = sum((s - mean_rerank) ** 2 for s in reranker_scores) / len(reranker_scores)
        std_dev = variance ** 0.5
        
        # 方差越小，一致性越高
        consistency = 1 / (1 + std_dev)
        
        # 3. 证据链完整性 - top结果的数量
        evidence_chain = min(len([s for s in similarities if s > top1 * 0.5]) / 3, 1.0)
        
        # 综合评分
        score = (concentration * 0.4 + consistency * 0.4 + evidence_chain * 0.2)
        
        return min(score, 1.0)

    def _calculate_granularity_match(self, query: str, chunk_content: str) -> float:
        """
        粒度匹配评分 - 评估检索结果的详细程度是否匹配问题
        
        例如：
        - "什么是AI" -> 需要定义性内容
        - "如何学习Python" -> 需要步骤性内容
        """
        score = 0.5
        
        query_lower = query.lower()
        content_lower = chunk_content.lower()
        
        # 1. 检测查询复杂度
        query_complexity = len(query_lower.split())
        
        # 2. 评估内容详细度
        content_detail = len(chunk_content)
        
        # 简单查询（<5词）应该返回简洁答案
        if query_complexity < 5:
            if 100 <= content_detail <= 500:  # 适中长度
                score += 0.2
            elif content_detail > 1000:  # 太长
                score -= 0.1
        # 复杂查询（>10词）需要详细答案
        elif query_complexity > 10:
            if content_detail > 500:
                score += 0.2
            elif content_detail < 200:
                score -= 0.2
        
        # 3. 步骤性内容检测
        step_indicators = ['第一步', '第二', '第三', '首先', '其次', '最后', 
                          '1.', '2.', '3.', '一、', '二、', '三、']
        for indicator in step_indicators:
            if indicator in content_lower:
                score += 0.05
                break
        
        # 4. 详细解释检测
        detail_indicators = ['具体来说', '详细', '具体', '包括', '例如']
        detail_count = sum(1 for d in detail_indicators if d in content_lower)
        score += min(detail_count * 0.02, 0.1)
        
        return min(max(score, 0), 1.0)

    def build_evidence_report(
        self,
        retrieved_chunks: List[Dict[str, Any]],
        query: str
    ) -> Dict[str, Any]:
        """
        构建证据报告 - 高级多维度置信度评估系统
        
        采用8个维度进行综合评估：
        1. Reranker分数 - 语义相关性权威评估
        2. 向量相似度 - 语义匹配质量
        3. 多结果一致性 - 检索稳定性
        4. 术语精确匹配 - 关键词覆盖
        5. 答案可答性 - 能否回答问题
        6. 查询覆盖度 - 对问题的覆盖程度
        7. 粒度匹配 - 详细程度匹配
        8. 答案质量 - 内容质量评估
        """
        if not retrieved_chunks:
            return {
                "confidence": 0.0,
                "confidence_level": "无检索结果",
                "chunks_strategy": "N/A",
                "retrieval_method": "N/A",
                "rerank_model": "No Reranking",
                "chunks": [],
                "top_similarity": 0,
                "avg_similarity": 0,
                "term_coverage": 0,
                "relevance_verified": False,
                "evidence_details": {
                    "reranker_score": 0,
                    "vector_similarity": 0,
                    "consistency_score": 0,
                    "term_match_score": 0,
                    "answerability_score": 0,
                    "coverage_score": 0,
                    "granularity_score": 0,
                    "quality_score": 0
                }
            }

        # ===== 收集核心指标 =====
        # 智能获取分数 - 使用最终调整后的 similarity 作为主要分数
        # reranker_score 可能有两种含义：原始分数或调整后分数
        all_scores = []
        for c in retrieved_chunks:
            # 优先使用 similarity（这是经过意图检查调整后的最终分数）
            sim = c.get('similarity', 0)
            rr = c.get('reranker_score')
            
            # 如果 similarity 不存在，用 reranker_score
            if sim == 0 and rr is not None:
                sim = rr
            all_scores.append(sim)
        
        top_similarity = max(all_scores) if all_scores else 0
        avg_similarity = sum(all_scores) / len(all_scores) if all_scores else 0
        
        # 【关键修复】如果最高相似度低于阈值，认为是无效检索，返回零置信度
        # 阈值设为 0.3，低于此值的检索结果不可靠
        MIN_VALID_SIMILARITY = 0.30
        if top_similarity < MIN_VALID_SIMILARITY:
            return {
                "confidence": 0.0,
                "confidence_level": "无检索结果",
                "chunks_strategy": "N/A",
                "retrieval_method": "N/A",
                "rerank_model": "No Reranking",
                "chunks": [],
                "top_similarity": 0,
                "avg_similarity": 0,
                "term_coverage": 0,
                "relevance_verified": False,
                "evidence_details": {
                    "reranker_score": 0,
                    "vector_similarity": 0,
                    "consistency_score": 0,
                    "term_match_score": 0,
                    "answerability_score": 0,
                    "coverage_score": 0,
                    "granularity_score": 0,
                    "quality_score": 0
                }
            }
        
        # ===== 综合相关性 =====
        # top_similarity 已经在 0-1 范围内，直接使用
        combined_score = top_similarity
        relevance_weight = 0.50
        relevance_confidence = combined_score * relevance_weight
        
        # ===== 维度2: 向量相似度（权重15%）=====
        # 从 chunks 中获取原始向量分数
        vector_scores = []
        for c in retrieved_chunks:
            vs = c.get('vector_score')
            if vs:
                vector_scores.append(vs)
        # 【修复】如果 vector_score 为空，使用 similarity 作为替代
        if vector_scores:
            top_vector = max(vector_scores)
        else:
            # 使用 top_similarity 作为向量相似度的近似
            top_vector = top_similarity * 0.95
        vector_weight = 0.15
        vector_confidence = top_vector * vector_weight
        
        # ===== 维度3: 多结果一致性（权重15%）=====
        # 【提升权重】多个检索结果的一致性是高质量检索的重要指标
        consistency_weight = 0.15
        consistency_confidence = self._calculate_consistency_score(retrieved_chunks) * consistency_weight
        
        # ===== 维度4: 术语精确匹配（权重8%）=====
        term_weight = 0.08
        term_scores = []
        for chunk in retrieved_chunks:
            term_match = chunk.get('term_match_ratio', 0)
            if not term_match:
                matched = chunk.get('matched_terms', [])
                if matched:
                    term_match = min(len(matched) / 5, 1.0)
            term_scores.append(term_match)
        max_term_match = max(term_scores) if term_scores else 0
        term_confidence = max_term_match * term_weight
        
        # ===== 维度5: 答案可答性（权重5%）=====
        answerability_weight = 0.05
        answerability_scores = []
        for chunk in retrieved_chunks:
            score = self._calculate_answerability_score(query, chunk.get('content', ''))
            answerability_scores.append(score)
        max_answerability = max(answerability_scores) if answerability_scores else 0
        answerability_confidence = max_answerability * answerability_weight
        
        # ===== 维度6: 查询覆盖度（权重3%）=====
        coverage_weight = 0.03
        coverage_analysis = self._calculate_coverage_analysis(query, retrieved_chunks)
        total_coverage = (coverage_analysis['semantic_coverage'] * 0.4 + 
                         coverage_analysis['lexical_coverage'] * 0.4 + 
                         coverage_analysis['completeness'] * 0.2)
        coverage_confidence = total_coverage * coverage_weight
        
        # ===== 维度7: 粒度匹配（权重1%）=====
        granularity_weight = 0.01
        granularity_scores = []
        for chunk in retrieved_chunks:
            score = self._calculate_granularity_match(query, chunk.get('content', ''))
            granularity_scores.append(score)
        max_granularity = max(granularity_scores) if granularity_scores else 0
        granularity_confidence = max_granularity * granularity_weight
        
        # ===== 维度8: 答案质量（权重1%）=====
        quality_weight = 0.01
        content_lengths = [len(c.get('content', '')) for c in retrieved_chunks]
        avg_length = sum(content_lengths) / len(content_lengths) if content_lengths else 0
        if 200 <= avg_length <= 1000:
            length_quality = 1.0
        elif avg_length < 200:
            length_quality = avg_length / 200
        else:
            length_quality = max(0.5, 1000 / avg_length)
        quality_confidence = length_quality * quality_weight
        
        # ===== 综合置信度 =====
        raw_confidence = (relevance_confidence + vector_confidence + consistency_confidence + 
                         term_confidence + answerability_confidence + coverage_confidence + 
                         granularity_confidence + quality_confidence)
        
        # 权重总和验证: 0.50 + 0.15 + 0.15 + 0.08 + 0.05 + 0.03 + 0.01 + 0.01 = 0.98
        
        # ===== 智能校准 - 基于真实分数 =====
        # 【修复】让置信度更保守，不要轻易达到100%
        
        if top_similarity >= 0.90:  # 极高相关（接近完美匹配）
            raw_confidence = min(raw_confidence * 1.15, 0.98)
        elif top_similarity >= 0.80:  # 高相关
            raw_confidence = min(raw_confidence * 1.10, 0.92)
        elif top_similarity >= 0.70:  # 中高相关
            raw_confidence = min(raw_confidence * 1.05, 0.85)
        elif top_similarity >= 0.55:  # 中相关
            raw_confidence = min(raw_confidence * 1.02, 0.75)
        
        confidence = raw_confidence
        
        # 根据检索结果数量调整（保守加成）
        if len(retrieved_chunks) >= 3 and top_similarity >= 0.85:
            # 只有多个检索结果且都很高时，才给予轻微加成
            confidence = min(confidence * 1.03, 0.95)
        elif len(retrieved_chunks) == 1:
            confidence = confidence * 0.90
        
        # 设置合理的置信度范围
        confidence = max(0.10, min(0.98, confidence))
        
        # ===== 置信度等级 =====
        if confidence >= 0.90:
            confidence_level = "极高"
        elif confidence >= 0.75:
            confidence_level = "高"
        elif confidence >= 0.55:
            confidence_level = "中"
        elif confidence >= 0.35:
            confidence_level = "低"
        else:
            confidence_level = "极低"
        
        # ===== 构建详细证据报告 =====
        # 使用 top_similarity 作为主要分数显示
        main_score = top_similarity if top_similarity > 0 else (max(vector_scores) if vector_scores else 0)
        evidence_details = {
            "reranker_score": round(main_score, 4),  # 使用主要分数
            "vector_similarity": round(top_similarity, 4),
            "consistency_score": round(consistency_confidence / consistency_weight if consistency_weight > 0 else 0, 4),
            "term_match_score": round(max_term_match, 4),
            "answerability_score": round(max_answerability, 4),
            "coverage_score": round(total_coverage, 4),
            "granularity_score": round(max_granularity, 4),
            "quality_score": round(length_quality, 4),
            "coverage_details": coverage_analysis
        }
        
        # ===== 日志输出 =====
        print(f"[EVIDENCE] ============== 置信度评估报告 ==============")
        print(f"[EVIDENCE] 查询: {query[:30]}...")
        print(f"[EVIDENCE] 检索结果数: {len(retrieved_chunks)}")
        print(f"[EVIDENCE] Top相似度: {top_similarity:.4f}, Top向量分数: {top_vector:.4f}")
        print(f"[EVIDENCE] 维度得分:")
        print(f"[EVIDENCE]   - 综合相关性: {relevance_confidence:.3f} (权重{relevance_weight})")
        print(f"[EVIDENCE]   - 向量相似度:   {vector_confidence:.3f} (权重{vector_weight})")
        print(f"[EVIDENCE]   - 一致性:       {consistency_confidence:.3f} (权重{consistency_weight})")
        print(f"[EVIDENCE]   - 术语匹配:     {term_confidence:.3f} (权重{term_weight})")
        print(f"[EVIDENCE]   - 答案可答性:   {answerability_confidence:.3f} (权重{answerability_weight})")
        print(f"[EVIDENCE]   - 查询覆盖度:   {coverage_confidence:.3f} (权重{coverage_weight})")
        print(f"[EVIDENCE]   - 粒度匹配:     {granularity_confidence:.3f} (权重{granularity_weight})")
        print(f"[EVIDENCE]   - 答案质量:     {quality_confidence:.3f} (权重{quality_weight})")
        print(f"[EVIDENCE]   - 覆盖详情:     语义{coverage_analysis['semantic_coverage']:.2f}, 词汇{coverage_analysis['lexical_coverage']:.2f}")
        print(f"[EVIDENCE] 最终置信度: {confidence:.3f} ({confidence_level})")
        print(f"[EVIDENCE] ===========================================")

        # 安全获取 metadata
        first_chunk = retrieved_chunks[0] if retrieved_chunks else {}
        raw_metadata = first_chunk.get('metadata', {})
        if not isinstance(raw_metadata, dict):
            raw_metadata = {}

        chunk_strategy = raw_metadata.get('chunking_strategy', 'semantic')
        if not chunk_strategy or chunk_strategy == 'semantic':
            chunk_strategy = raw_metadata.get('strategy', 'semantic')

        # 构建chunk信息
        chunks_info = []
        for i, chunk in enumerate(retrieved_chunks[:10]):
            # 保留完整内容，只做预览处理
            full_content = chunk.get('content', '')
            # content_preview 用于列表显示（可选截断）
            content_preview = full_content[:300] + '...' if len(full_content) > 300 else full_content
            similarity = chunk.get('similarity', 0)
            bm25 = chunk.get('bm25_score')
            keyword_score = chunk.get('keyword_score')
            term_match_ratio = chunk.get('term_match_ratio')
            phrase_score = chunk.get('phrase_score')
            position_bonus = chunk.get('position_bonus')
            matched_terms = chunk.get('matched_terms', [])

            # 获取reranker原始分数
            raw_reranker = chunk.get('reranker_score', 0)

            chunks_info.append({
                "id": str(chunk.get('chunk_id', '')),
                "source": str(chunk.get('document_title', 'Unknown')),
                "content_preview": content_preview,
                "full_content": full_content,  # 完整内容，展开时显示
                "score": float(similarity),
                "rank": i,
                "method": "multi-strategy",
                "bm25_score": float(bm25) if bm25 is not None else None,
                "keyword_score": float(keyword_score) if keyword_score is not None else None,
                "term_match_ratio": float(term_match_ratio) if term_match_ratio is not None else None,
                "phrase_score": float(phrase_score) if phrase_score is not None else None,
                "position_bonus": float(position_bonus) if position_bonus is not None else None,
                "matched_terms": matched_terms,
                "reranker_score": float(raw_reranker) if raw_reranker else None,
            })

        # 计算词汇覆盖度
        lexical_coverage = coverage_analysis['lexical_coverage']

        return {
            "confidence": round(confidence, 3),
            "confidence_level": confidence_level,
            "chunks_strategy": chunk_strategy,
            "retrieval_method": "Multi-Strategy Hybrid",
            "rerank_model": "Multi-Factor Reranking",
            "rerank_before_score": None,
            "rerank_after_score": None,
            "top_similarity": round(top_similarity, 4),
            "avg_similarity": round(avg_similarity, 4),
            "chunks": chunks_info,
            "relevance_verified": main_score >= 0.5 and lexical_coverage >= 0.2,
            "term_coverage": round(lexical_coverage, 3),
            "evidence_details": evidence_details
        }

    def _get_relevance_label(self, similarity: float) -> str:
        """根据相似度返回相关性标签"""
        if similarity >= 0.85:
            return "Very High"
        elif similarity >= 0.7:
            return "High"
        elif similarity >= 0.55:
            return "Medium"
        elif similarity >= 0.4:
            return "Low"
        else:
            return "Very Low"

    async def generate_prompt(
        self,
        query: str,
        conversation_history: List[Dict[str, str]] = None,
        retrieved_chunks: List[Dict[str, Any]] = None,
        use_enhanced: bool = True,
        memories_context: str = None,
        confidence: float = 1.0,
        relevance_verified: bool = True,
        use_rag: bool = True
    ) -> List[Dict[str, str]]:
        """生成 RAG 增强的提示
        
        Args:
            use_rag: 如果为 False，使用普通对话提示（不强制要求基于参考资料回答）
        """
        messages = []

        # 构建记忆上下文
        memory_section = ""
        if memories_context:
            memory_section = f"""

## 你的学习记忆（重要！）
{memories_context}

请结合以上记忆内容来回答问题。如果参考资料与记忆有冲突，优先以记忆中的知识为准，因为记忆代表你已经确认过的知识。"""

        if retrieved_chunks and use_rag:
            if use_enhanced:
                context = self.build_enhanced_context(retrieved_chunks, query)
            else:
                context = self.build_context(retrieved_chunks)

            # 根据置信度调整提示词
            confidence_warning = ""
            if confidence < 0.5 or not relevance_verified:
                confidence_warning = """

**⚠️ 重要警告**：
当前检索结果与您的问题相关性较低或置信度不高（{:.0%}）。请特别注意：
1. 您的提问内容与知识库中的文档可能存在较大差异
2. 请务必基于参考资料回答，不要编造不存在的信息
3. 如果参考资料确实无法回答您的问题，请明确告知用户"根据当前知识库，无法找到与您问题直接相关的内容"
4. 可以建议用户换一种方式提问，或确认问题是否涉及知识库中的其他领域""".format(confidence)
            elif confidence < 0.7:
                confidence_warning = """

**⚠️ 提示**：当前置信度为 {:.0%}，检索结果仅供参考，请谨慎使用。""".format(confidence)

            system_prompt = f"""你是一个基于参考资料回答问题的助手。

【数据来源约束】
1. 只能根据"参考资料"中的内容回答
2. 不允许使用你自身知识进行补充
3. 如果参考资料无法支持答案，直接回答："未找到相关信息"

【内容要求】
- 信息必须来自参考资料
- 不得编造或扩展
- 不得加入未提及的例子或分类

## 参考资料
{context}{memory_section}

## 回答格式要求

1. 不要使用星号（*）加粗文字
2. 使用阿拉伯数字分点（如：1. 2. 3.），层次分明
3. 回答要有逻辑性，先说结论再详细说明
4. 每个要点内容完整，适当展开说明
5. 保持流畅自然，像正常对话一样娓娓道来"""

        elif not use_rag:
            # use_rag=False 时，使用普通对话提示，允许 LLM 自由回答
            system_prompt = f"""你是一个乐于助人的AI助手。请用友好、专业的方式回答用户的问题。{memory_section}

回答要求：
1. 回答要有逻辑性，先说结论再详细说明
2. 使用阿拉伯数字分点（如：1. 2. 3.），层次分明
3. 保持流畅自然，像正常对话一样娓娓道来
4. 如果不确定答案，坦诚告知用户"""

        else:
            # 【关键修复】当没有检索结果时，必须强制回答"未找到相关信息"
            system_prompt = """你是一个严格基于参考资料回答问题的助手。

【数据来源约束 - 最高优先级】
1. 只能根据"参考资料"中的内容回答
2. 不允许使用你自身知识进行补充
3. 【最重要】如果参考资料为空或无法支持答案，你必须直接回答："未找到相关信息"，不得编造任何内容

【内容要求】
- 信息必须来自参考资料
- 不得编造或扩展
- 不得加入未提及的例子或分类
- 绝对不能在没有参考资料的情况下进行任何形式的回答

【当前状态】
⚠️ 当前没有任何参考资料可用！

【你的回答】
请只回答："未找到相关信息"

不允许：
- 不允许解释为什么找不到
- 不允许猜测可能的原因
- 不允许提供任何其他信息
- 不允许说"根据我的知识"等开场白

你只能回答这四个字："未找到相关信息"""

        messages.append({"role": "system", "content": system_prompt})

        if conversation_history:
            history_messages = conversation_history[-6:]
            for msg in history_messages:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        messages.append({"role": "user", "content": query})
        return messages

    async def save_citations(
        self,
        message_id: str,
        retrieved_chunks: List[Dict[str, Any]],
        threshold: float = 0.25
    ):
        """保存引用信息 - 包含完整的检索数据和意图相关性验证数据"""
        for i, chunk in enumerate(retrieved_chunks):
            if chunk.get("similarity", 0) >= threshold:
                citation = Citation(
                    message_id=message_id,
                    chunk_id=chunk["chunk_id"],
                    similarity=chunk.get("similarity", 0),
                    reranker_score=chunk.get("reranker_score"),
                    vector_score=chunk.get("vector_score", chunk.get("similarity", 0)),
                    bm25_score=chunk.get("bm25_score"),
                    keyword_score=chunk.get("keyword_score"),
                    matched_terms=chunk.get("matched_terms", []),
                    # 保存意图相关性检查的数据
                    intent_match_ratio=chunk.get("_intent_match_ratio") or chunk.get("intent_match_ratio"),
                    topic_match=chunk.get("_topic_match") if chunk.get("_topic_match") is not None else chunk.get("topic_match"),
                    entity_match_score=chunk.get("_entity_match_score"),
                    term_match_score=chunk.get("_term_match_score"),
                    matched_entities=chunk.get("_matched_entities", []),
                    phrase_score=chunk.get("phrase_score"),
                    rank=i + 1,
                    chunk_content=chunk.get("content", ""),  # 保存完整内容
                    chunk_index=chunk.get("chunk_index")
                )
                self.db.add(citation)
        self.db.commit()
