from typing import List, Dict, Any, Optional
import chromadb
import logging
import hashlib
import copy

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, collection_name: str = "documents"):
        # 初始化 ChromaDB 客户端（持久化到磁盘，重启后数据不丢）
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(name=collection_name)
        logger.info(f"VectorStore initialized with collection: {collection_name}")
    
    def _generate_deterministic_id(self, content: str) -> str:
        """基于内容生成确定性 ID（跨进程稳定）"""
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:12]
        return f"doc_{content_hash}"
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Add documents to the vector store with custom deterministic IDs."""
        if not documents:
            return []
        
        texts = []
        metadatas = []
        ids = []
        
        for doc in documents:
            # 深拷贝避免修改原始数据
            doc_copy = copy.deepcopy(doc)
            content = doc_copy["content"]
            
            # 生成确定性 ID
            doc_id = self._generate_deterministic_id(content)
            ids.append(doc_id)
            
            # 构建非空 metadata
            metadata = doc_copy.get("metadata", {}) or {}
            metadata.update({
                "source": "hybrid_rag",
                "doc_id": doc_id,
                "content_hash": hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
            })
            metadatas.append(metadata)
            texts.append(content)
        
        # 批量写入 ChromaDB
        try:
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Successfully added {len(ids)} documents")
            return ids
        except Exception as e:
            logger.error(f"Failed to add documents: {str(e)}")
            raise
    
    def similarity_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                include=["documents", "metadatas", "distances"]
            )
            
            retrieved_docs = []
            if results and results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    doc = {
                        "id": doc_id,
                        "content": results["documents"][0][i] if results["documents"] else "",
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results.get("distances") else None
                    }
                    retrieved_docs.append(doc)
            
            return retrieved_docs
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a document by its custom ID."""
        try:
            results = self.collection.get(
                ids=[doc_id],
                include=["documents", "metadatas"]
            )
            
            if results and results["documents"] and len(results["documents"]) > 0:
                return {
                    "id": doc_id,
                    "content": results["documents"][0],
                    "metadata": results["metadatas"][0] if results["metadatas"] else {}
                }
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve document by ID {doc_id}: {str(e)}")
            return None
    
    def delete_collection(self):
        """清空整个集合（调试用）"""
        try:
            self.client.delete_collection(self.collection.name)
            logger.info(f"Deleted collection: {self.collection.name}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")