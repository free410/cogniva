"""调试 RAG 检索"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from core.database import SessionLocal
from models import Chunk, Vector, Document
from services.rag_service import RAGService, embedding_service
import numpy as np

def debug_retrieve():
    db = SessionLocal()
    try:
        rag_svc = RAGService(db)

        # 测试查询
        query = "苹果腐烂病是什么"
        print(f"查询: {query}")

        # 生成查询向量
        print("\n1. 生成查询向量...")
        query_embedding = embedding_service.embed([query])[0]
        print(f"   向量维度: {len(query_embedding)}")
        print(f"   向量前5维: {query_embedding[:5]}")

        # 直接查询所有 chunks
        print("\n2. 数据库中的 chunks:")
        all_chunks = db.query(Chunk).all()
        print(f"   总数: {len(all_chunks)}")
        for chunk in all_chunks:
            vec = db.query(Vector).filter(Vector.chunk_id == chunk.id).first()
            has_vec = "有向量" if vec else "无向量"
            doc = db.query(Document).filter(Document.id == chunk.document_id).first()
            doc_name = doc.filename if doc else "未知文档"
            print(f"   - {chunk.id}: 来自《{doc_name}》, {has_vec}")

        # 手动计算相似度
        print("\n3. 计算相似度（手动）:")
        chunks_with_vectors = db.query(Chunk).join(Vector).all()
        print(f"   有向量的 chunks: {len(chunks_with_vectors)}")

        results = []
        for chunk in chunks_with_vectors:
            if chunk.vector and chunk.vector.embedding:
                similarity = rag_svc.cosine_similarity(query_embedding, chunk.vector.embedding)
                if similarity >= 0.0:  # 无阈值过滤
                    doc = db.query(Document).filter(Document.id == chunk.document_id).first()
                    results.append({
                        "chunk_id": str(chunk.id),
                        "content": chunk.content[:50],
                        "similarity": similarity,
                        "document_title": doc.filename if doc else "Unknown"
                    })
                    print(f"   - 相似度: {similarity:.4f}, 文档: {doc.filename if doc else 'Unknown'}")

        # 排序
        results.sort(key=lambda x: x["similarity"], reverse=True)
        print(f"\n4. 检索结果数: {len(results)}")
        if results:
            print("   前3条:")
            for r in results[:3]:
                print(f"   - {r['similarity']:.4f}: {r['content']}...")
        else:
            print("   未检索到任何结果！")

        # 调用实际的 retrieve 方法
        print("\n5. 调用 RAGService.retrieve():")
        retrieved = rag_svc.retrieve(query, top_k=5, similarity_threshold=0.0)
        print(f"   返回 {len(retrieved)} 条结果")
        for r in retrieved[:3]:
            print(f"   - {r['similarity']:.4f}: {r['content'][:50]}...")

    finally:
        db.close()

if __name__ == "__main__":
    debug_retrieve()
