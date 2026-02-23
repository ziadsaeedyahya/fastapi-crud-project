from fastapi import APIRouter, HTTPException
from app.llm_clients.cohere_embedding_client import embedding_client
from app.schemas.embedding_schema import EmbeddingRequest, EmbeddingResponse

router = APIRouter(prefix="/embeddings", tags=["Embeddings"])

@router.post("/generate", response_model=EmbeddingResponse)
async def generate_embeddings(request: EmbeddingRequest):
    result = embedding_client.get_embeddings(request.texts, request.input_type)
    
    if result is None:
        raise HTTPException(status_code=500, detail="Could not generate embeddings")
    
    return {
        "status": "success",
        "model": "embed-v4.0",
        "embeddings": result
    }