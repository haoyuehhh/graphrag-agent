from fastapi import APIRouter, HTTPException
from app.models.competitor_schemas import (
    CompetitorProfile,
    CompetitorComparisonRequest, 
    CompetitorMatrixResponse
)
from app.services.competitor_analyzer import competitor_analyzer

router = APIRouter(tags=["competitors"])

@router.post("/compare", response_model=CompetitorMatrixResponse)
async def compare_competitors(req: CompetitorComparisonRequest):
    """对比指定竞品"""
    try:
        result = await competitor_analyzer.compare_by_dimension(req)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@router.get("/{name}/profile", response_model=CompetitorProfile)
async def get_competitor_profile(name: str):
    """获取竞品画像"""
    profile = await competitor_analyzer.get_profile(name)
    if not profile:
        raise HTTPException(status_code=404, detail=f"未找到: {name}")
    return profile

@router.get("/matrix/features", response_model=CompetitorMatrixResponse)
async def get_feature_matrix():
    """功能矩阵"""
    req = CompetitorComparisonRequest(
        competitor_names=["notion", "obsidian", "logseq"],
        dimension="features"
    )
    return await competitor_analyzer.compare_by_dimension(req)