from typing import List, Dict, Any, Optional
import chromadb
import logging
from app.models.schemas import DocumentMapping

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        # 初始化 ChromaDB 客户端
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection("documents")
        
        # 确保集合存在
        if self.collection.count() == 0:
            # 添加一个空文档以确保集合结构正确
            self.collection.add(
                documents=[""],
                metadatas=[{}],
                ids=["init_doc"]
            )
            # 然后删除它
            self.collection.delete(ids=["init_doc"])
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Add documents to the vector store with custom deterministic IDs."""
        if not documents:
            return []
        
        texts = [doc["content"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]
        
        # Generate deterministic IDs based on content hash
        ids = []
        for doc in documents:
            content = doc["content"]
            # Generate deterministic ID using content hash
            content_hash = hash(content)
            doc_id = f"doc_{content_hash % 100000}"
            ids.append(doc_id)
            
            # Add custom metadata to track the source and document ID
            if "metadata" not in doc:
                doc["metadata"] = {}
            doc["metadata"].update({
                "source": "hybrid_rag",
                "doc_id": doc_id,
                "content_hash": str(content_hash)
            })
        
        # Add documents to ChromaDB with custom IDs
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        return ids
    
    def similarity_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )
        
        # Convert results to the expected format
        retrieved_docs = []
        if results and "ids" in results and results["ids"]:
            for i, doc_id in enumerate(results["ids"][0]):
                doc = {
                    "id": doc_id,
                    "content": results["documents"][0][i] if results["documents"] else "",
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {}
                }
                retrieved_docs.append(doc)
        
        return retrieved_docs
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a document by its custom ID."""
        try:
            # Query ChromaDB by ID
            results = self.collection.get(
                ids=[doc_id],
                include=["documents", "metadatas"]
            )
            
            if results and "documents" in results and results["documents"]:
                return {
                    "id": doc_id,
                    "content": results["documents"][0],
                    "metadata": results["metadatas"][0] if results["metadatas"] else {}
                }
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve document by ID {doc_id}: {str(e)}")
            return None
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Add documents to the vector store with custom deterministic IDs."""
        if not documents:
            return []
        
        texts = [doc["content"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]
        
        # Generate deterministic IDs based on content hash
        ids = []
        for doc in documents:
            content = doc["content"]
            # Generate deterministic ID using content hash
            content_hash = hash(content)
            doc_id = f"doc_{content_hash % 100000}"
            ids.append(doc_id)
            
            # Add custom metadata to track the source and document ID
            if "metadata" not in doc:
                doc["metadata"] = {}
            doc["metadata"].update({
                "source": "hybrid_rag",
                "doc_id": doc_id,
                "content_hash": str(content_hash)
            })
        
        # Add documents to ChromaDB with custom IDs
        self.chroma.add_documents(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        return ids
    
    def similarity_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        results = self.chroma.similarity_search(query, k=k)
        return results
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a document by its custom ID."""
        try:
            # ChromaDB uses the same ID we provided, so we can query directly
            results = self.chroma.get(
                ids=[doc_id],
                include=["documents", "metadatas"]
            )
            
            if results and "documents" in results and results["documents"]:
                return {
                    "id": doc_id,
                    "content": results["documents"][0],
                    "metadata": results["metadatas"][0] if results["metadatas"] else {}
                }
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve document by ID {doc_id}: {str(e)}")
            return None