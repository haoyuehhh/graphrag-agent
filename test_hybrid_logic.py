#!/usr/bin/env python3
"""
逻辑测试脚本：验证 Hybrid RAG 检索融合逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.rag_service import RAGService
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_hybrid_logic():
    """测试 Hybrid RAG 检索融合逻辑"""
    logger.info("开始测试 Hybrid RAG 检索融合逻辑...")
    
    try:
        # 初始化服务
        rag_service = RAGService()
        
        # 模拟向量检索结果
        vector_results = [
            {
                "id": "doc_12345",
                "content": "这是一个关于人工智能的测试文档，包含机器学习和深度学习的内容。",
                "metadata": {
                    "doc_id": "doc_12345",
                    "content_hash": "12345"
                }
            },
            {
                "id": "doc_67890",
                "content": "机器学习是人工智能的一个重要分支，深度学习是机器学习的子领域。",
                "metadata": {
                    "doc_id": "doc_67890",
                    "content_hash": "67890"
                }
            }
        ]
        
        # 模拟图谱检索结果
        graph_results = ["doc_12345", "doc_99999"]
        
        # 模拟 vector_store 的 similarity_search 方法
        original_similarity_search = rag_service.vector_store.similarity_search
        rag_service.vector_store.similarity_search = lambda q, k: vector_results
        
        # 模拟 graph_builder 的 search_nodes_by_keyword 方法
        original_graph_search = rag_service.graph_builder.search_nodes_by_keyword
        rag_service.graph_builder.search_nodes_by_keyword = lambda q: graph_results
        
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
        expected_doc_ids = ["doc_12345", "doc_67890", "doc_99999"]
        actual_doc_ids = [doc["id"] for doc in retrieved_docs]
        
        if set(expected_doc_ids) == set(actual_doc_ids):
            logger.info("✅ Hybrid 检索逻辑测试通过")
            return True
        else:
            logger.warning(f"⚠️ Hybrid 检索逻辑测试失败")
            logger.warning(f"期望的文档ID: {expected_doc_ids}")
            logger.warning(f"实际的文档ID: {actual_doc_ids}")
            return False
            
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        return False
    finally:
        # 恢复原始方法
        rag_service.vector_store.similarity_search = original_similarity_search
        rag_service.graph_builder.search_nodes_by_keyword = original_graph_search

if __name__ == "__main__":
    success = test_hybrid_logic()
    sys.exit(0 if success else 1)