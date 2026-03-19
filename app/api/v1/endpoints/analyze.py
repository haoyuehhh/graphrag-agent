
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.concurrency import run_in_threadpool
import asyncio
from app.api.deps import get_rag_service
from app.services.rag_service import RAGService
from app.core.config import settings
from app.core.exceptions import GraphNotReadyException
from app.api.v1.schemas import QueryRequest
from fastapi import APIRouter, Request, Response, HTTPException, Depends
from fastapi.responses import StreamingResponse  # 单独导入
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
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    流式分析接口，返回打字机效果
    """
    async def generate():
        # 模拟流式输出（如果 LLM 不支持 stream，就用分段返回）
        query = request.query
        
        # 先返回思考过程
        yield f"data: 正在分析问题: {query}...\n\n"
        await asyncio.sleep(0.3)
        
        # 模拟逐字返回（实际项目中这里调用 LLM 的流式接口）
        chunks = ["正在", "检索", "知识库...", "\n", "找到", "相关", "信息", "：", "\n\n"]
        for chunk in chunks:
            yield f"data: {chunk}"
            await asyncio.sleep(0.1)
        
        # 调用实际分析逻辑（复用现有逻辑）
        result = await run_in_threadpool(analyze, request)  # 使用线程池运行同步函数
        content = result.get("answer", "分析完成")
        
        # 分段返回结果
        for char in content[:100]:  # 限制长度避免太长
            yield f"data: {char}"
            await asyncio.sleep(0.05)
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(), 
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

# 测试命令：curl -X POST http://localhost:8000/api/v1/analyze/stream \
#   -H "Content-Type: application/json" \
#   -d '{"query":"Notion和Obsidian有什么区别"}'
