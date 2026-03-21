from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import os
import logging
from app.core.skills.implementations.browser_skill import BrowserSkill
from app.services.vector_store import VectorStore
from app.models.competitor_schemas import CompetitorProfile
from app.graph.state import GraphState
import asyncio

logger = logging.getLogger(__name__)

class HybridDataCollector:
    def __init__(self, vector_store: VectorStore, browser_skill: BrowserSkill, graph_state: GraphState):
        self.vector_store = vector_store
        self.browser_skill = browser_skill
        self.graph_state = graph_state
        self.cache_dir = "data/crawled"
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def _get_cache_file(self, name: str) -> str:
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{name}_data.json")
    
    def _is_data_fresh(self, cache_file: str, max_age_hours: int = 24) -> bool:
        """检查数据是否新鲜"""
        if not os.path.exists(cache_file):
            return False
            
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        age = datetime.now() - file_time
        return age.total_seconds() < (max_age_hours * 3600)
    
    async def _fetch_and_cache_data(self, name: str) -> Dict[str, Any]:
        """通过浏览器技能获取数据并缓存"""
        try:
            # 构建搜索查询
            queries = [
                f"{name} pricing",
                f"{name} features",
                f"{name} release notes",
                f"{name} technical architecture"
            ]
            
            all_results = {}
            
            for query in queries:
                search_results = await self.browser_skill.search(query, max_results=3)
                if search_results and search_results.get('results'):
                    all_results[query] = search_results['results']
            
            if all_results:
                # 保存到缓存
                cache_file = self._get_cache_file(name)
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(all_results, f, ensure_ascii=False, indent=2)
                
                logger.info(f"成功获取并缓存 {name} 的数据")
                return all_results
            
            return {}
        except Exception as e:
            logger.error(f"获取 {name} 数据失败: {e}")
            return {}
    
    def _parse_crawled_data(self, crawled_data: Dict[str, Any]) -> CompetitorProfile:
        """解析爬取的数据为竞品画像"""
        features = []
        pricing_tiers = {}
        tech_stack = []
        
        # 从爬取结果中提取信息
        for query, results in crawled_data.items():
            for result in results:
                content = result.get('content', '')
                
                if "pricing" in query.lower():
                    # 提取定价信息
                    for line in content.split('\n'):
                        if '$' in line and '(' in line and ')' in line:
                            price_str = line.split('$')[1].split(')')[0]
                            tier_name = line.split('(')[1].split(')')[0]
                            try:
                                price = float(price_str)
                                pricing_tiers[tier_name.lower()] = price
                            except ValueError:
                                pass
                
                elif "features" in query.lower():
                    # 提取功能信息
                    if "features" in content.lower():
                        features_start = content.lower().find("features")
                        if features_start != -1:
                            features_section = content[features_start:]
                            features = [line.strip("- *").strip() for line in features_section.split('\n') if line.strip().startswith('-')]
                
                elif "tech" in query.lower() or "architecture" in query.lower():
                    # 提取技术栈信息
                    if "tech" in content.lower() or "architecture" in content.lower():
                        tech_start = min(content.lower().find("tech"), content.lower().find("architecture"))
                        if tech_start != -1:
                            tech_section = content[tech_start:]
                            tech_stack = [line.strip("- *").strip() for line in tech_section.split('\n') if line.strip().startswith('-')]
        
        return CompetitorProfile(
            name=name,
            features=features[:10],
            pricing_tiers=pricing_tiers,
            tech_stack=tech_stack[:10],
            target_users="Online users",
            last_updated=datetime.now()
        )
    
    async def get_competitor_data(self, name: str, max_age_hours: int = 24) -> Optional[CompetitorProfile]:
        """
        获取竞品数据（优先使用本地，过期时爬取补充）
        
        Args:
            name: 竞品名称
            max_age_hours: 数据最大年龄（小时）
            
        Returns:
            CompetitorProfile: 竞品画像，如果获取失败返回None
        """
        # 1. 检查本地缓存
        cache_file = self._get_cache_file(name)
        
        if self._is_data_fresh(cache_file, max_age_hours):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    crawled_data = json.load(f)
                return self._parse_crawled_data(crawled_data)
            except Exception as e:
                logger.warning(f"读取缓存文件失败 {cache_file}: {e}")
        
        # 2. 如果本地数据过期或不存在，爬取新数据
        logger.info(f"本地数据过期或不存在，开始爬取 {name} 的数据")
        crawled_data = await self._fetch_and_cache_data(name)
        
        if crawled_data:
            profile = self._parse_crawled_data(crawled_data)
            
            # 3. 更新本地知识库
            self._update_local_knowledge(name, profile)
            
            return profile
        
        return None
    
    def _update_local_knowledge(self, name: str, profile: CompetitorProfile):
        """更新本地知识库"""
        try:
            # 这里可以添加将数据保存到本地文档的逻辑
            # 简化实现：将数据保存为JSON文件
            local_file = os.path.join("data/competitors", name, f"{name}_latest.json")
            os.makedirs(os.path.dirname(local_file), exist_ok=True)
            
            with open(local_file, 'w', encoding='utf-8') as f:
                json.dump(profile.dict(), f, ensure_ascii=False, indent=2)
                
            logger.info(f"更新本地知识库: {local_file}")
        except Exception as e:
            logger.error(f"更新本地知识库失败: {e}")
    
    async def batch_get_competitors(self, names: List[str], max_age_hours: int = 24) -> Dict[str, Optional[CompetitorProfile]]:
        """
        批量获取竞品数据
        
        Args:
            names: 竞品名称列表
            max_age_hours: 数据最大年龄（小时）
            
        Returns:
            Dict: 竞品名称到竞品画像的映射
        """
        results = {}
        
        for name in names:
            profile = await self.get_competitor_data(name, max_age_hours)
            results[name] = profile
        
        return results
    
    def get_cached_data(self, name: str) -> Optional[Dict[str, Any]]:
        """获取缓存的原始数据"""
        cache_file = self._get_cache_file(name)
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"读取缓存文件失败 {cache_file}: {e}")
        
        return None
    
    def clear_cache(self, name: str = None):
        """清除缓存"""
        if name:
            cache_file = self._get_cache_file(name)
            if os.path.exists(cache_file):
                os.remove(cache_file)
                logger.info(f"清除缓存: {cache_file}")
        else:
            # 清除所有缓存
            for file in os.listdir(self.cache_dir):
                if file.endswith('_data.json'):
                    os.remove(os.path.join(self.cache_dir, file))
            logger.info("清除所有缓存")