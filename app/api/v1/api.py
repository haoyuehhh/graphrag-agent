from fastapi import APIRouter
from app.api.v1.endpoints.analyze import router as analyze_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.competitors import router as competitors_router
from app.api.v1.endpoints.mcp import router as mcp_router 

api_router = APIRouter()
api_router.include_router(analyze_router, prefix="/analyze", tags=["analysis"])
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(competitors_router, prefix="/competitors", tags=["competitors"])
api_router.include_router(mcp_router, prefix="/mcp", tags=["mcp"])
