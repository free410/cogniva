"""
高级切块器使用示例
"""

from services.advanced_chunker import AdvancedChunker, chunk_text
from services.document_service import DocumentService
from core.config import settings


# ============================================
# 示例1：基本使用
# ============================================
def example_basic():
    """基本使用示例"""
    text = "这是一段很长的文本..." * 100

    chunker = AdvancedChunker(
        chunk_size=800,      # 每块最多800字符
        chunk_overlap=150    # 块间重叠150字符
    )

    # 使用递归切块策略
    chunks = chunker.chunk(text, strategy="recursive")
    print(f"生成了 {len(chunks)} 个块")


# ============================================
# 示例2：便捷函数
# ============================================
def example_convenient():
    """使用便捷函数"""
    text = "你的文档内容..."

    chunks = chunk_text(
        text=text,
        chunk_size=1000,
        chunk_overlap=200,
        strategy="semantic"  # 语义切块
    )
    print(f"生成了 {len(chunks)} 个语义块")


# ============================================
# 示例3：在 DocumentService 中使用
# ============================================
async def example_with_document_service():
    """在文档处理服务中使用"""
    from sqlalchemy.orm import Session

    db = SessionLocal()
    service = DocumentService(db)

    # 处理文档（自动使用配置的切块策略）
    document = await service.process_document(
        user_id="user123",
        file=upload_file,
        # 可选：覆盖默认配置
        chunk_size=1000,
        overlap=200,
        chunk_strategy="hybrid"  # 混合策略
    )

    # 查看切块元数据
    print(f"策略: {document.extra_metadata.get('chunk_strategy')}")
    print(f"块数: {document.extra_metadata.get('chunk_count')}")
    print(f"平均块大小: {document.extra_metadata.get('avg_chunk_size'):.0f}")


# ============================================
# 示例4：语义切块（需要嵌入模型）
# ============================================
def example_semantic():
    """语义切块示例"""
    text = """
    机器学习是人工智能的一个重要分支。它使计算机能够在没有明确编程的情况下学习。
    神经网络是机器学习的一种方法，受人脑结构的启发。深度学习是神经网络的子集，
    使用多层网络来学习数据的多层次表示。卷积神经网络(CNN)特别适合处理图像数据。
    循环神经网络(RNN)则擅长处理序列数据，如文本和时间序列。
    """

    chunker = AdvancedChunker(chunk_size=200, chunk_overlap=30)

    # 语义切块会自动检测语义边界
    chunks = chunker.chunk(text, strategy="semantic", threshold=0.6)

    for i, chunk in enumerate(chunks):
        print(f"语义块 {i+1}: {chunk[:80]}...")


# ============================================
# 示例5：Markdown结构切块
# ============================================
def example_markdown():
    """Markdown结构感知切块"""
    md_text = """
# 项目概述

这是一个关于机器学习的项目。

## 数据集

我们使用了公开数据集。

### 数据预处理

- 清洗数据
- 归一化
- 特征提取

## 模型架构

### CNN���型

卷积神经网络包含：
1. 卷积层
2. 池化层
3. 全连接层

### RNN模型

循环神经网络用于序列建模。
"""

    chunker = AdvancedChunker(chunk_size=300, overlap=50)
    chunks = chunker.chunk(md_text, strategy="markdown")

    print(f"Markdown文档被切分为 {len(chunks)} 个结构化块:")
    for i, chunk in enumerate(chunks, 1):
        print(f"\n块 {i}:")
        print(chunk[:150] + "..." if len(chunk) > 150 else chunk)


# ============================================
# 配置不同策略的参数
# ============================================
def example_configure_strategies():
    """配置不同切块策略的参数"""
    chunker = AdvancedChunker(chunk_size=800, chunk_overlap=100)

    # 递归策略：自定义分隔符层次
    recursive_chunks = chunker.chunk(
        text,
        strategy="recursive",
        separators=["\n\n\n", "\n\n", "\n", "。", ". "]
    )

    # 语义策略：调整相似度阈值
    semantic_chunks = chunker.chunk(
        text,
        strategy="semantic",
        threshold=0.7  # 更高的阈值意味着更严格的语义一致性
    )

    # 滑动窗口：自定义窗口大小和步长
    sliding_chunks = chunker.chunk(
        text,
        strategy="sliding_window",
        window_size=1000,
        step_size=800
    )


# ============================================
# 示例6：批量语义分组
# ============================================
def example_batch_semantic():
    """批量文本语义分组"""
    from services.advanced_chunker import create_semantic_chunks

    texts = [
        "深度学习方法",
        "机器学习算法",
        "神经网络架构",
        "图像分类技术",
        "自然语言处理"
    ]

    # 生成嵌入向量
    embeddings = embedding_service.embed(texts)

    # 基于语义相似性分组
    groups = create_semantic_chunks(texts, embeddings, threshold=0.6)

    print(f"将 {len(texts)} 个文本分为 {len(groups)} 个语义组:")
    for i, group in enumerate(groups):
        print(f"组 {i+1}: {group}")


# ============================================
# 示例7：生产环境最佳实践
# ============================================
def example_production_best_practices():
    """生产环境最佳实践"""

    # 1. 根据文档类型选择策略
    def choose_strategy(filename: str, content: str) -> str:
        """根据文件类型和内容选择切块策略"""
        ext = filename.split('.')[-1].lower()

        if ext in ['md', 'markdown']:
            return "markdown"  # Markdown文档使用结构切块
        elif ext in ['txt']:
            # 短文本用递归，长文档用混合
            return "hybrid" if len(content) > 5000 else "recursive"
        elif ext in ['pdf', 'docx']:
            # 结构化文档用混合策略
            return "hybrid"
        else:
            return "recursive"  # 默认

    # 2. 动态调整块大小
    def get_optimal_chunk_size(text: str, strategy: str) -> int:
        """根据文档长度和策略计算最佳块大小"""
        text_len = len(text)

        if text_len < 2000:
            return 600   # 短文档：小一点的块
        elif text_len < 10000:
            return 1000  # 中等文档
        else:
            return 1500  # 长文档：大块减少碎片

    # 3. 使用元数据追踪
    def process_with_metadata(file, user_id):
        """处理时记录详细的元数据"""
        chunks = chunker.chunk_with_metadata(
            text=content,
            metadata={
                "source": file.filename,
                "user_id": user_id,
                "processed_at": datetime.now().isoformat(),
                "strategy": strategy
            },
            strategy=strategy
        )
        return chunks


# ============================================
# 运行示例
# ============================================
if __name__ == "__main__":
    print("选择要运行的示例:")
    print("1. 基本使用")
    print("2. 便捷函数")
    print("3. Markdown切块")
    print("4. 语义切块")
    print("5. 策略比较")

    # example_basic()
    # example_convenient()
    # example_markdown()
    # example_semantic()
    # compare_strategies()

    print("\n查看 test_advanced_chunker.py 获取完整示例")
