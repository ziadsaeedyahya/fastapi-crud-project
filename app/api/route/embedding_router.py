from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.api.auth_deps import get_current_user 
from app.llm_clients.cohere_embedding_client import embedding_client
from app.models.embedding_model import ItemEmbedding
from app.schemas.embedding_schema import EmbeddingRequest

# استورد الـ supabase_client اللي متعرف عندك في المشروع
from app.clientsdatabase_clients import supabase_client 

router = APIRouter(prefix="/embeddings", tags=["Embeddings"])

@router.post("/generate-and-store")
async def generate_and_store(
    request: EmbeddingRequest,
    current_user = Depends(get_current_user)
):
    # 1. هات الـ Vectors
    vectors = embedding_client.get_embeddings(request.texts, request.input_type)
    
    if not vectors:
        raise HTTPException(status_code=500, detail="Cohere failed to generate embeddings")

    # 2. نفتح جلسة (Session) مخصوصة لسوبابيز
    # بنستخدم next() لأن get_session دي Generator
    db = next(supabase_client.get_session())

    try:
        for text, vector in zip(request.texts, vectors):
            db_obj = ItemEmbedding(
                user_id=current_user.id,
                content=text,
                embedding=vector
            )
            db.add(db_obj)
        
        db.commit() # الحفظ في سوبابيز مباشرة
        
        return {
            "status": "success", 
            "message": f"Saved {len(vectors)} embeddings to SUPABASE for {current_user.email}"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
    finally:
        db.close() # مهم جداً نقفل الـ session يدوي هنا