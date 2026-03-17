#!/usr/bin/env python3
"""
测试脚本：验证 Hybrid RAG 检索融合功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.rag_service import RAGService
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_hybrid_retrieval():
    """测试 Hybrid RAG 检索融合功能"""
    logger.info("开始测试 Hybrid RAG 检索融合...")
    
    # 初始化服务
    rag_service = RAGService()
    
    try:
        # 创建测试文档
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
        
        # 处理文档
        results = rag_service.process_documents(test_documents)
        logger.info(f"文档处理结果: {results}")
        
        # 等待文档索引完成（在实际应用中可能需要）
        import time
        time.sleep(2)
        
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
    success = test_hybrid_retrieval()
    sys.exit(0 if success else 1)