from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from app.services.rag_service import RAGService
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.events import lifespan
from app.core.limiter import setup_limiter
from app.api.v1.api import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan 管理器
    """
    # 启动时：初始化 Graph 和服务
    app.state.rag_service = RAGService()
    yield
    # 关闭时：清理资源（如果有需要）

app = FastAPI(
    title="GraphRAG Multi-Agent API",
    description="基于 LangGraph 的多智能体 GraphRAG 系统",
    version="1.0.0",
    lifespan=lifespan
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设置限流器
setup_limiter(app)

# 挂载路由
app.include_router(api_router, prefix="/api/v1")

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy"}