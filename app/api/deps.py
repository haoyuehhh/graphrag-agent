from fastapi import Request, Depends
from app.services.rag_service import RAGService

async def get_rag_service(request: Request) -> RAGService:
    """
    依赖注入：获取 RAGService 实例
    """
    return request.app.state.rag_service