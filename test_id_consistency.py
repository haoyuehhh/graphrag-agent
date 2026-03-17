#!/usr/bin/env python3
"""
测试脚本：验证 NetworkX 知识图谱与 ChromaDB 向量库的 ID 一致性
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.vector_store import VectorStore
from app.graph.builder import GraphBuilder
from app.services.rag_service import RAGService
from app.models.schemas import DocumentMapping
import logging
import uuid
import networkx as nx
from typing import List, Dict, Any

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_id_consistency():
    """测试 ID 一致性"""
    logger.info("开始测试 ID 一致性...")
    
    # 创建测试文档
    test_content = "这是一个测试文档，用于验证 ID 一致性。"
    test_document = {
        "content": test_content,
        "metadata": {
            "source": "test",
            "title": "测试文档"
        }
    }
    
    # 初始化服务
    vector_store = VectorStore()
    graph_builder = GraphBuilder()
    rag_service = RAGService(vector_store, graph_builder)
    
    try:
        # 处理文档
        results = rag_service.process_documents([test_document])
        logger.info(f"处理结果: {results}")
        
        # 获取生成的 ID
        doc_id = results["mappings"][0]["doc_id"]
        vector_db_id = results["vector_ids"][0]
        
        logger.info(f"生成的文档 ID: {doc_id}")
        logger.info(f"ChromaDB ID: {vector_db_id}")
        
        # 验证 ID 一致性
        is_consistent = rag_service.verify_id_consistency(doc_id)
        logger.info(f"ID 一致性验证结果: {'通过' if is_consistent else '失败'}")
        
        # 验证内容
        chroma_doc = vector_store.get_document_by_id(doc_id)
        if chroma_doc:
            logger.info(f"从 ChromaDB 获取的内容: {chroma_doc['content'][:50]}...")
            logger.info(f"ChromaDB 元数据: {chroma_doc['metadata']}")
        
        return is_consistent
        
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_id_consistency()
    sys.exit(0 if success else 1)