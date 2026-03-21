from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import networkx as nx
import json
import os

@dataclass
class Relationship:
    """关系数据类"""
    source: str
    target: str
    relation_type: str
    attributes: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}

class GraphStore:
    """图存储服务"""
    def __init__(self):
        self.graph = nx.DiGraph()
        self.load_data()
    
    def load_data(self):
        """加载数据到图"""
        # 这里可以从文件或数据库加载数据
        # 简化实现：添加一些示例数据
        self._add_sample_data()
    
    def _add_sample_data(self):
        """添加示例数据"""
        # Notion 数据
        self.graph.add_node("notion", 
                          name="Notion", 
                          category="note-taking", 
                          tech_stack=["React", "TypeScript", "PostgreSQL"],
                          target_users="teams and individuals")
        
        self.graph.add_node("notion_free", 
                          name="Notion Free", 
                          price=0)
        
        self.graph.add_node("notion_plus", 
                          name="Notion Plus", 
                          price=10)
        
        self.graph.add_node("notion_business", 
                          name="Notion Business", 
                          price=15)
        
        # 添加关系
        self.graph.add_edge("notion", "notion_free", relation_type="has_pricing", attributes={"price": 0})
        self.graph.add_edge("notion", "notion_plus", relation_type="has_pricing", attributes={"price": 10})
        self.graph.add_edge("notion", "notion_business", relation_type="has_pricing", attributes={"price": 15})
        
        # 功能关系
        features = [
            "实时协作", "数据库功能", "第三方集成", "移动应用", "API访问", "模板系统"
        ]
        for feature in features:
            self.graph.add_node(feature)
            self.graph.add_edge("notion", feature, relation_type="has_feature")
    
    def get_entity(self, name: str) -> Optional[Dict]:
        """获取实体信息"""
        if name in self.graph.nodes:
            return dict(self.graph.nodes[name])
        return None
    
    def find_related_entities(self, name: str, max_depth: int = 1) -> List[Relationship]:
        """查找相关实体"""
        relationships = []
        
        if name not in self.graph.nodes:
            return relationships
        
        # 获取直接关系
        for neighbor in self.graph.neighbors(name):
            edge_data = self.graph.get_edge_data(name, neighbor)
            relationships.append(Relationship(
                source=name,
                target=neighbor,
                relation_type=edge_data.get('relation_type', ''),
                attributes=edge_data.get('attributes', {})
            ))
        
        return relationships
    
    def add_entity(self, name: str, attributes: Dict[str, Any]):
        """添加实体"""
        self.graph.add_node(name, **attributes)
    
    def add_relationship(self, source: str, target: str, relation_type: str, attributes: Dict[str, Any] = None):
        """添加关系"""
        if attributes is None:
            attributes = {}
        self.graph.add_edge(source, target, relation_type=relation_type, attributes=attributes)
    
    def save_data(self):
        """保存数据"""
        # 简化实现：可以保存到文件或数据库
        pass
    
    def get_all_entities(self) -> List[Dict]:
        """获取所有实体"""
        return [dict(data) for _, data in self.graph.nodes(data=True)]
    
    def get_entities_by_category(self, category: str) -> List[Dict]:
        """按类别获取实体"""
        return [dict(data) for _, data in self.graph.nodes(data=True) if data.get('category') == category]