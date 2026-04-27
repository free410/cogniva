"""检查数据库状态并清理 orphaned chunks"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from core.database import SessionLocal
from models import Chunk, Vector, Document
from sqlalchemy import text

def check_and_fix():
    db = SessionLocal()
    try:
        print("=== 数据库状态检查 ===\n")

        # 统计
        doc_count = db.query(Document).count()
        chunk_count = db.query(Chunk).count()
        vector_count = db.query(Vector).count()

        print(f"文档总数: {doc_count}")
        print(f"Chunk 总数: {chunk_count}")
        print(f"Vector 总数: {vector_count}")

        # 查找 orphaned chunks
        orphaned = db.query(Chunk).filter(Chunk.document_id == None).all()
        print(f"\n孤立 chunks (document_id=NULL): {len(orphaned)}")

        if orphaned:
            print("\n正在删除孤立 chunks...")
            for chunk in orphaned:
                # 删除关联的 vector
                vec = db.query(Vector).filter(Vector.chunk_id == chunk.id).first()
                if vec:
                    db.delete(vec)
                db.delete(chunk)
            db.commit()
            print(f"✅ 已删除 {len(orphaned)} 个孤立 chunks")

        # 再次统计
        chunk_count = db.query(Chunk).count()
        vector_count = db.query(Vector).count()
        print(f"\n清理后:")
        print(f"  Chunk 总数: {chunk_count}")
        print(f"  Vector 总数: {vector_count}")

        # 显示各文档情况
        print("\n=== 各文档情况 ===")
        for doc in db.query(Document).all():
            c_count = db.query(Chunk).filter(Chunk.document_id == doc.id).count()
            v_count = db.query(Vector).join(Chunk).filter(Chunk.document_id == doc.id).count()
            print(f"  {doc.filename}: {c_count} chunks, {v_count} vectors")

        # 检查是否有文档没有 chunks
        print("\n=== 无 chunks 的文档 ===")
        for doc in db.query(Document).all():
            c_count = db.query(Chunk).filter(Chunk.document_id == doc.id).count()
            if c_count == 0:
                print(f"  ⚠️  {doc.filename} 没有 chunks!")

        print("\n✅ 检查完成")
    finally:
        db.close()

if __name__ == "__main__":
    check_and_fix()
