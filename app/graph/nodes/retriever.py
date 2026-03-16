from typing import Dict, Any
from app.graph.state import GraphRAGState
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
import networkx as nx
import os

async def retriever(state: GraphRAGState) -> Dict[str, Any]:
    """
    Retriever 节点：从 ChromaDB 和 NetworkX 图谱中检索相关信息
    """
    query = state["query"]
    chroma_persist_dir = "./chroma_db"
    
    # 初始化 ChromaDB
    vector_store = Chroma(
        persist_directory=chroma_persist_dir,
        embedding_function=None  # 使用默认嵌入模型
    )
    
    # 从 ChromaDB 检索相关文档
    docs = vector_store.similarity_search(query, k=5)
    
    # 加载 NetworkX 图谱（简化版）
    graph_path = []
    if os.path.exists("./graph_db"):
        try:
            graph = nx.read_graphml("./graph_db/graph.graphml")
            # 这里可以添加图谱检索逻辑
            graph_path = ["graph_node1", "graph_node2"]  # 示例路径
        except Exception as e:
            print(f"Error loading graph: {e}")
    
    # 组合检索结果
    context = "\n".join([doc.page_content for doc in docs])
    if graph_path:
        context += f"\nGraph path: {' -> '.join(graph_path)}"
    
    return {
        "context": context,
        "sources": [{"type": "document", "content": doc.page_content} for doc in docs],
        "graph_path": graph_path
    }