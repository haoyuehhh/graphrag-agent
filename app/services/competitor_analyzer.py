from typing import List, Dict, Optional
from app.models.competitor_schemas import CompetitorProfile, CompetitorComparisonRequest, CompetitorMatrixResponse
from graph_store import GraphStore

class CompetitorAnalyzer:
    def __init__(self):
        self.store = GraphStore()
    
    async def get_profile(self, name: str) -> Optional[CompetitorProfile]:
        entity = self.store.get_entity(name)
        if not entity:
            return None
        
        # entity is dict
        entity_name = entity.get("name", name)
        attributes = entity.get("attributes", {})
        
        related = self.store.find_related_entities(name, max_depth=1)
        features = []
        if related:
            for r in related:
                rel_type = r.get("relation_type") if isinstance(r, dict) else None
                target = r.get("target") if isinstance(r, dict) else None
                if rel_type == "has_feature":
                    features.append(target)
        
        return CompetitorProfile(
            name=entity_name,
            features=features,
            pricing_tiers=attributes.get("pricing", {}) if isinstance(attributes, dict) else {},
            tech_stack=attributes.get("tech_stack", []) if isinstance(attributes, dict) else [],
            target_users=attributes.get("target_users", "General users") if isinstance(attributes, dict) else "General users"
        )
    
    async def compare_by_dimension(self, req: CompetitorComparisonRequest) -> CompetitorMatrixResponse:
        profiles = []
        for comp_name in req.competitor_names:
            profile = await self.get_profile(comp_name)
            if profile:
                profiles.append(profile)
        
        matrix = {}
        for p in profiles:
            matrix[p.name] = {
                "features": p.features,
                "pricing": p.pricing_tiers
            }
        
        return CompetitorMatrixResponse(
            status="success" if len(profiles) >= 2 else "partial",
            matrix=matrix,
            dimension=req.dimension,
            timestamp="2024-03-22T12:00:00"
        )

competitor_analyzer = CompetitorAnalyzer()