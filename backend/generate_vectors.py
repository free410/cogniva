"""为没有向量的 chunks 生成向量"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from core.database import SessionLocal
from models import Chunk, Vector
from services.rag_service import embedding_service

def generate_missing_vectors():
    db = SessionLocal()
    try:
        print("=== 查找缺失向量的 Chunks ===")

        # 找到没有向量的 chunks
        chunks_without_vectors = db.query(Chunk).outerjoin(Vector).filter(Vector.chunk_id == None).all()
        print(f"缺失向量的 chunks 数: {len(chunks_without_vectors)}")

        if not chunks_without_vectors:
            print("OK - 所有 chunks 都有向量")
            return

        # 批量处理
        batch_size = 50
        total = len(chunks_without_vectors)
        generated = 0

        for i in range(0, total, batch_size):
            batch = chunks_without_vectors[i:i+batch_size]
            texts = [chunk.content for chunk in batch]

            print(f"处理批次 {i//batch_size + 1}/{(total + batch_size - 1)//batch_size} ({len(batch)} 个 chunks)...")

            try:
                # 生成向量
                embeddings = embedding_service.embed(texts)

                # 保存向量
                for chunk, embedding in zip(batch, embeddings):
                    vector = Vector(
                        chunk_id=chunk.id,
                        embedding=embedding
                    )
                    db.add(vector)
                    generated += 1

                db.commit()
                print(f"  [OK] 已生成 {generated}/{total} 个向量")

            except Exception as e:
                print(f"  [FAIL] 批次处理失败: {e}")
                db.rollback()
                break

        print(f"\n[OK] 完成! 共生成 {generated} 个向量")

        # 验证结果
        print("\n=== 验证结果 ===")
        total_chunks = db.query(Chunk).count()
        total_vectors = db.query(Vector).count()
        print(f"Chunk 总数: {total_chunks}")
        print(f"Vector 总数: {total_vectors}")
        print(f"覆盖率: {total_vectors/total_chunks*100:.1f}%")

    finally:
        db.close()

if __name__ == "__main__":
    generate_missing_vectors()