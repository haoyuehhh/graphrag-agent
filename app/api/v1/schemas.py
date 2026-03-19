from pydantic import BaseModel
from typing import Optional, List

class QueryRequest(BaseModel):
    query: str
    context: Optional[str] = None
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[str] = []
    session_id: Optional[str] = None
