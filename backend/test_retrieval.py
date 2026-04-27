"""测试 RAG 检索是否正常工作"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from core.database import SessionLocal
from services.rag_service import RAGService
import asyncio

async def test_retrieval():
    db = SessionLocal()
    try:
        rag = RAGService(db)

        test_queries = [
            "苹果腐烂病",
            "果树病虫害",
            "防治方法"
        ]

        for query in test_queries:
            print(f"\n{'='*50}")
            print(f"查询: {query}")
            print('='*50)

            # 检索
            results = await rag.retrieve(query, top_k=3, similarity_threshold=0.1)

            print(f"检索到 {len(results)} 条结果\n")

            if results:
                for i, r in enumerate(results, 1):
                    print(f"{i}. 相似度: {r['similarity']:.4f}")
                    print(f"   文档: {r['document_title']}")
                    print(f"   内容: {r['content'][:80]}...")
                    print()
            else:
                print("未检索到结果!")

        # 显示数据库统计
        print("\n=== 数据库统计 ===")
        from models import Document, Chunk, Vector
        doc_count = db.query(Document).count()
        chunk_count = db.query(Chunk).count()
        vector_count = db.query(Vector).count()
        print(f"文档数: {doc_count}")
        print(f"Chunks: {chunk_count}")
        print(f"Vectors: {vector_count}")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_retrieval())
