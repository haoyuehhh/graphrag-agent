"""
知识图谱存储：使用 NetworkX 存储和管理实体关系
"""
import json
import os
from typing import Dict, List, Optional, Tuple, Any
import networkx as nx
from dataclasses import dataclass, asdict
from config import SystemConfig

@dataclass
class Entity:
    """实体类"""
    id: str
    name: str
    type: str  # product, feature, price, etc.
    attributes: Dict[str, Any]
    description: Optional[str] = None

@dataclass
class Relation:
    """关系类"""
    source: str
    target: str
    relation_type: str
    attributes: Dict[str, Any]

class GraphStore:
    """知识图谱存储管理"""
    
    def __init__(self, db_path: str = "./graph_db"):
        self.db_path = db_path
        self.graph = nx.DiGraph()
        self.entities: Dict[str, Entity] = {}
        self._ensure_db_directory()
    
    def _ensure_db_directory(self):
        """确保数据库目录存在"""
        os.makedirs(self.db_path, exist_ok=True)
    
    def add_entity(self, entity: Entity) -> bool:
        """添加实体"""
        try:
            self.entities[entity.id] = entity
            self.graph.add_node(
                entity.id,
                name=entity.name,
                type=entity.type,
                attributes=entity.attributes,
                description=entity.description
            )
            return True
        except Exception as e:
            print(f"添加实体失败: {e}")
            return False
    
    def add_relation(self, relation: Relation) -> bool:
        """添加关系"""
        try:
            if relation.source not in self.entities or relation.target not in self.entities:
                print("源实体或目标实体不存在")
                return False
            
            self.graph.add_edge(
                relation.source,
                relation.target,
                relation_type=relation.relation_type,
                attributes=relation.attributes
            )
            return True
        except Exception as e:
            print(f"添加关系失败: {e}")
            return False
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """获取实体"""
        return self.entities.get(entity_id)
    
    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        """根据类型获取实体"""
        return [entity for entity in self.entities.values() if entity.type == entity_type]
    
    def get_relations(self, entity_id: str) -> List[Dict]:
        """获取实体的关系"""
        relations = []
        for source, target, data in self.graph.edges(entity_id, data=True):
            relations.append({
                "source": source,
                "target": target,
                "relation_type": data.get("relation_type"),
                "attributes": data.get("attributes", {})
            })
        return relations
    
    def find_related_entities(self, entity_id: str, depth: int = 1) -> List[Dict]:
        """查找相关实体"""
        try:
            related = []
            for neighbor in self.graph.neighbors(entity_id):
                entity = self.get_entity(neighbor)
                if entity:
                    related.append({
                        "entity": entity,
                        "relation_type": self.graph[entity_id][neighbor].get("relation_type")
                    })
            
            # 递归查找更深层次的关系
            if depth > 1:
                for item in related:
                    deeper = self.find_related_entities(item["entity"].id, depth - 1)
                    related.extend(deeper)
            
            return related
        except Exception as e:
            print(f"查找相关实体失败: {e}")
            return []
    
    def search_entities(self, query: str, limit: int = SystemConfig.MAX_ENTITIES) -> List[Entity]:
        """搜索实体"""
        results = []
        query_lower = query.lower()
        
        for entity in self.entities.values():
            if (query_lower in entity.name.lower() or 
                (entity.description and query_lower in entity.description.lower())):
                results.append(entity)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_subgraph(self, entity_ids: List[str]) -> nx.DiGraph:
        """获取子图"""
        return self.graph.subgraph(entity_ids)
    
    def save_to_file(self, filename: str = "knowledge_graph.json"):
        """保存知识图谱到文件"""
        try:
            data = {
                "entities": [asdict(entity) for entity in self.entities.values()],
                "edges": [
                    {
                        "source": edge[0],
                        "target": edge[1],
                        "relation_type": edge[2].get("relation_type"),
                        "attributes": edge[2].get("attributes", {})
                    }
                    for edge in self.graph.edges(data=True)
                ]
            }
            
            filepath = os.path.join(self.db_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"知识图谱已保存到: {filepath}")
            return True
        except Exception as e:
            print(f"保存知识图谱失败: {e}")
            return False
    
    def load_from_file(self, filename: str = "knowledge_graph.json"):
        """从文件加载知识图谱"""
        try:
            filepath = os.path.join(self.db_path, filename)
            if not os.path.exists(filepath):
                print(f"文件不存在: {filepath}")
                return False
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 清空现有数据
            self.graph.clear()
            self.entities.clear()
            
            # 加载实体
            for entity_data in data.get("entities", []):
                entity = Entity(**entity_data)
                self.add_entity(entity)
            
            # 加载边
            for edge_data in data.get("edges", []):
                relation = Relation(
                    source=edge_data["source"],
                    target=edge_data["target"],
                    relation_type=edge_data["relation_type"],
                    attributes=edge_data.get("attributes", {})
                )
                self.add_relation(relation)
            
            print(f"知识图谱已从 {filepath} 加载")
            return True
        except Exception as e:
            print(f"加载知识图谱失败: {e}")
            return False
    
    def get_graph_stats(self) -> Dict:
        """获取图谱统计信息"""
        return {
            "total_entities": len(self.entities),
            "total_relations": self.graph.number_of_edges(),
            "entity_types": list(set(entity.type for entity in self.entities.values())),
            "relation_types": list(set(
                data.get("relation_type") for _, _, data in self.graph.edges(data=True)
            ))
        }