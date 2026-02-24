import uuid
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List

from app.api.auth_deps import get_current_user 
from app.api.service_deps import get_supabase_db      
from app.llm_clients.cohere_embedding_client import embedding_client
from app.models.embedding_model import ItemEmbedding
from app.models.video_script_model import VideoScriptEmbedding
from app.schemas.embedding_schema import EmbeddingRequest

# استيراد سوبابيز كلينت للرفع
from app.clientsdatabase_clients.db_manager import supabase_client # تأكد من المسار ده عندك

router = APIRouter(prefix="/embeddings", tags=["Embeddings"])

# 1. Endpoint الـ Text Embeddings (القديمة)
@router.post("/generate-and-store")
async def generate_and_store(
    request: EmbeddingRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_supabase_db)
):
    vectors = embedding_client.get_embeddings(request.texts, request.input_type)
    if not vectors:
        raise HTTPException(status_code=500, detail="Cohere failed to generate embeddings")

    try:
        for text, vector in zip(request.texts, vectors):
            db_obj = ItemEmbedding(
                user_id=current_user.id,
                content=text,
                embedding=vector
            )
            db.add(db_obj)
        db.commit()
        return {"status": "success", "message": f"Saved {len(vectors)} embeddings"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# 2. Endpoint معالجة الفيديو (الجديدة)
@router.post("/process-video-to-script", status_code=status.HTTP_201_CREATED)
async def process_video_to_script(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_supabase_db)
):
    # التأكد من نوع الملف
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="لازم ترفع فيديو يا بطل")

    try:
        # أ- تجهيز البيانات
        file_ext = file.filename.split(".")[-1]
        unique_name = f"{uuid.uuid4()}.{file_ext}"
        storage_path = f"{current_user.id}/{unique_name}"
        
        # ب- الرفع لـ Supabase Storage
        file_content = await file.read()
        supabase_client.storage.from_("videos").upload(
            path=storage_path,
            file=file_content,
            file_options={"content-type": file.content_type}
        )

        # ج- جلب الرابط
        video_url = supabase_client.storage.from_("videos").get_public_url(storage_path)

        # د- الحفظ في الجدول الجديد
        new_video_record = VideoScriptEmbedding(
            user_id=current_user.id,
            video_url=video_url,
            script_text="Pending AI Transcription...", 
        )
        
        db.add(new_video_record)
        db.commit()
        db.refresh(new_video_record)

        return {
            "id": new_video_record.id,
            "video_url": video_url,
            "status": "Uploaded Successfully",
            "db_source": "Supabase"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")