#!/usr/bin/env python3
"""
简单测试脚本：验证 Hybrid RAG 检索融合功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.rag_service import RAGService
import chromadb
import logging
import time

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_hybrid_simple():
    """简单测试 Hybrid RAG 检索融合功能"""
    logger.info("开始简单测试 Hybrid RAG 检索融合...")
    
    try:
        # 初始化服务
        rag_service = RAGService()
        
        # 直接使用 ChromaDB 客户端添加文档
        chroma_client = chromadb.Client()
        collection = chroma_client.get_or_create_collection("test_documents")
        
        # 添加测试文档
        test_documents = [
            {
                "content": "这是一个关于人工智能的测试文档，包含机器学习和深度学习的内容。",
                "metadata": {
                    "source": "test",
                    "title": "人工智能基础"
                }
            },
            {
                "content": "机器学习是人工智能的一个重要分支，深度学习是机器学习的子领域。",
                "metadata": {
                    "source": "test",
                    "title": "机器学习介绍"
                }
            },
            {
                "content": "图谱技术可以用于知识表示和推理，在推荐系统中广泛应用。",
                "metadata": {
                    "source": "test",
                    "title": "图谱技术"
                }
            }
        ]
        
        # 添加文档到 ChromaDB
        ids = []
        for i, doc in enumerate(test_documents):
            content = doc["content"]
            content_hash = hash(content)
            doc_id = f"doc_{content_hash % 100000}"
            ids.append(doc_id)
            
            # 添加自定义元数据
            if "metadata" not in doc:
                doc["metadata"] = {}
            doc["metadata"].update({
                "source": "hybrid_rag",
                "doc_id": doc_id,
                "content_hash": str(content_hash)
            })
        
        collection.add(
            documents=[doc["content"] for doc in test_documents],
            metadatas=[doc["metadata"] for doc in test_documents],
            ids=ids
        )
        
        # 等待索引完成
        time.sleep(1)
        
        # 测试 Hybrid 检索
        query = "人工智能和机器学习"
        retrieved_docs = rag_service.hybrid_retrieve(query, top_k=3)
        
        logger.info(f"查询: {query}")
        logger.info(f"检索到 {len(retrieved_docs)} 个文档:")
        
        for i, doc in enumerate(retrieved_docs, 1):
            logger.info(f"{i}. ID: {doc['id']}, 来源: {doc.get('source', 'unknown')}")
            logger.info(f"   内容: {doc['content'][:100]}...")
            logger.info(f"   元数据: {doc['metadata']}")
        
        # 验证结果
        if len(retrieved_docs) > 0:
            logger.info("✅ Hybrid 检索测试通过")
            return True
        else:
            logger.warning("⚠️ Hybrid 检索未找到文档")
            return False
            
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_hybrid_simple()
    sys.exit(0 if success else 1)