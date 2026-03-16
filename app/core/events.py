from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.graph.builder import build_graph
from app.services.rag_service import RAGService
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan 管理器
    """
    # 启动时：初始化 ChromaDB 和 Graph
    print("Initializing ChromaDB and LangGraph...")
    
    # 构建 LangGraph
    graph = build_graph()
    
    # 创建 RAG 服务实例
    rag_service = RAGService()
    
    # 将服务存入 app.state 以便其他模块访问
    app.state.graph = graph
    app.state.rag_service = rag_service
    
    yield
    
    # 关闭时：清理资源
    print("Shutting down services...")
    # 这里可以添加资源清理逻辑，如关闭数据库连接等