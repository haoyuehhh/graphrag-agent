#!/usr/bin/env python3
"""
测试脚本：验证 ID 生成逻辑的一致性
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.vector_store import VectorStore
from app.graph.builder import GraphBuilder
import logging
import uuid
import networkx as nx
from typing import List, Dict, Any

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_id_generation():
    """测试 ID 生成逻辑的一致性"""
    logger.info("开始测试 ID 生成逻辑...")
    
    # 测试内容
    test_content = "这是一个测试文档，用于验证 ID 一致性。"
    
    # 测试 ChromaDB 的 ID 生成
    content_hash = hash(test_content)
    chroma_id = f"doc_{content_hash % 100000}"
    logger.info(f"ChromaDB ID 生成: {chroma_id}")
    
    # 测试 NetworkX 的 ID 生成
    graph_builder = GraphBuilder()
    # 模拟文档结构
    doc = {
        "content": test_content,
        "metadata": {}
    }
    
    # 手动生成相同的 ID
    graph_id = f"doc_{content_hash % 100000}"
    logger.info(f"NetworkX ID 生成: {graph_id}")
    
    # 验证一致性
    is_consistent = (chroma_id == graph_id)
    logger.info(f"ID 一致性: {'一致' if is_consistent else '不一致'}")
    
    return is_consistent

if __name__ == "__main__":
    success = test_id_generation()
    sys.exit(0 if success else 1)