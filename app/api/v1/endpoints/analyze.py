from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from app.api.deps import get_rag_service
from app.services.rag_service import RAGService
from app.core.config import settings
from app.core.exceptions import GraphNotReadyException

router = APIRouter()

@router.post("/analyze")
async def analyze(
    request: Request,
    query: str,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    竞品分析主接口（非流式）
    """
    try:
        result = await rag_service.analyze(query, streaming=False)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/stream")
async def analyze_stream(
    request: Request,
    query: str,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    竞品分析主接口（流式）
    """
    async def event_stream():
        try:
            async for event in rag_service.analyze(query, streaming=True):
                yield f"data: {event}\n\n"
        except Exception as e:
            yield f"data: {{\"type\": \"error\", \"content\": \"{str(e)}\"}}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )