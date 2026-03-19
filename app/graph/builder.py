import networkx as nx
from typing import List, Dict, Any
import uuid

class GraphBuilder:
    def __init__(self):
        self.graph = nx.Graph()
    
    def build_graph(self, documents: List[Dict[str, Any]]) -> nx.Graph:
        """Build a knowledge graph from documents with unified ID system."""
        G = nx.Graph()
        
        for doc in documents:
            content = doc["content"]
            # Generate deterministic ID based on content hash (same as ChromaDB)
            content_hash = hash(content)
            doc_id = f"doc_{content_hash % 100000}"
            
            # Add document node with unified ID
            G.add_node(
                doc_id,
                type="document",
                content=content,
                metadata=doc.get("metadata", {}),
                embedding_id=doc_id  # Store the same ID for embedding reference
            )
            
            # Add entities as nodes
            for entity in doc.get("entities", []):
                entity_id = str(uuid.uuid4())  # Entities can have unique IDs
                G.add_node(
                    entity_id,
                    name=entity["name"],
                    type=entity["type"],
                    description=entity.get("description", "")
                )
                
                # Add edge between document and entity
                G.add_edge(
                    doc_id,
                    entity_id,
                    relationship="contains"
                )
        
        return G
    
    def search_nodes_by_keyword(self, keyword: str) -> List[str]:
        """Search for nodes containing the keyword (simple substring match)."""
        matching_nodes = []
        
        for node_id, node_data in self.graph.nodes(data=True):
            if "content" in node_data and keyword.lower() in node_data["content"].lower():
                matching_nodes.append(node_id)
            elif "name" in node_data and keyword.lower() in node_data["name"].lower():
                matching_nodes.append(node_id)
        
        return matching_nodes

def build_graph(documents):
    """Build a knowledge graph from documents (wrapper for backward compatibility)."""
    builder = GraphBuilder()
    return builder.build_graph(documents)
