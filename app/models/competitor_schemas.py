from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class CompetitorProfile(BaseModel):
    """竞品画像模型"""
    name: str = Field(..., description="竞品名称")
    features: List[str] = Field(default_factory=list, description="功能列表")
    pricing_tiers: Dict[str, float] = Field(default_factory=dict, description="定价层级")
    tech_stack: List[str] = Field(default_factory=list, description="技术栈")
    target_users: str = Field(default="General users, teams, enterprises", description="目标用户")
    last_updated: datetime = Field(default_factory=datetime.now, description="最后更新时间")
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CompetitorComparisonRequest(BaseModel):
    """竞品对比请求模型"""
    competitor_names: List[str] = Field(..., description="竞品名称列表")
    dimension: str = Field(default="features", description="对比维度：pricing/features/tech_stack")
    
    class Config:
        schema_extra = {
            "example": {
                "competitor_names": ["notion", "obsidian"],
                "dimension": "features"
            }
        }

class CompetitorPositioningRequest(BaseModel):
    """竞品定位分析请求模型"""
    product_name: str = Field(..., description="要分析的产品名称")
    competitors: List[str] = Field(..., description="对比的竞品列表")
    
    class Config:
        schema_extra = {
            "example": {
                "product_name": "my_product",
                "competitors": ["notion", "obsidian"]
            }
        }

class CompetitorMatrixResponse(BaseModel):
    """竞品矩阵响应模型"""
    status: str = Field(default="success", description="操作状态")
    matrix: Dict[str, Dict[str, Any]] = Field(..., description="竞品矩阵数据")
    dimension: str = Field(..., description="对比维度")
    timestamp: str = Field(..., description="时间戳")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "matrix": {
                    "notion": {
                        "features": ["实时协作", "数据库功能", "第三方集成"],
                        "pricing": {"free": 0, "plus": 10, "business": 15}
                    },
                    "obsidian": {
                        "features": ["本地存储", "Markdown支持", "插件生态"],
                        "pricing": {"free": 0, "premium": 10}
                    }
                },
                "dimension": "features",
                "timestamp": "2024-01-01T12:00:00"
            }
        }

class CompetitorAnalysisResponse(BaseModel):
    """竞品分析响应模型"""
    status: str = Field(default="success", description="操作状态")
    analysis: str = Field(..., description="分析结果")
    timestamp: str = Field(..., description="时间戳")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "analysis": "差异化定位分析：my_product\\n\\n相对于 notion:\\n- 共同功能: 5 个\\n- 独特功能: 3 个\\n- 定价对比: {'free': 0, 'plus': 10, 'business': 15} vs {'free': 0, 'premium': 10}\\n\\n相对于 obsidian:\\n- 共同功能: 4 个\\n- 独特功能: 4 个\\n- 定价对比: {'free': 0, 'plus': 10, 'business': 15} vs {'free': 0, 'premium': 10}\\n\\n",
                "timestamp": "2024-01-01T12:00:00"
            }
        }