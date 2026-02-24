from pydantic import BaseModel
from typing import List, Optional

class EmbeddingRequest(BaseModel):
    texts: List[str]
    input_type: Optional[str] = "search_document"

class EmbeddingResponse(BaseModel):
    status: str
    model: str
    embeddings: List[List[float]]