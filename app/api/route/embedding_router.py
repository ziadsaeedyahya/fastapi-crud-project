import uuid
import os
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
from moviepy import VideoFileClip  # لاستخراج مميزات الفيديو والصوت

from app.api.auth_deps import get_current_user 
from app.api.service_deps import get_supabase_db      
from app.llm_clients.GroqClient import groq_client       # الكلينت بتاعك اللي فيه Whisper
from app.llm_clients.cohere_embedding_client import embedding_client
from app.models.embedding_model import ItemEmbedding
from app.models.video_script_model import VideoScriptEmbedding
from app.schemas.embedding_schema import EmbeddingRequest

# استيراد سوبابيز كلينت
from app.clientsdatabase_clients.db_manager import supabase_client 

router = APIRouter(prefix="/embeddings", tags=["Embeddings"])

# 1. Endpoint الـ Text Embeddings (كما هي)
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


# 2. Endpoint معالجة الفيديو (النسخة المتطورة)
@router.post("/process-video-to-script", status_code=status.HTTP_201_CREATED)
async def process_video_to_script(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_supabase_db)
):
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="لازم ترفع فيديو يا بطل")

    unique_id = str(uuid.uuid4())
    file_ext = file.filename.split(".")[-1]
    temp_video_path = f"temp_{unique_id}.{file_ext}"
    temp_audio_path = f"temp_{unique_id}.mp3"

    try:
        # أ- قراءة الملف وحفظه مؤقتاً
        file_content = await file.read()
        file_size_mb = len(file_content) / (1024 * 1024)
        with open(temp_video_path, "wb") as f:
            f.write(file_content)

        # ب- استخراج البيانات والصوت (تعديل: استخدام with لضمان قفل الملف)
        # تعديل 2: حذف verbose=False لأنها تسبب Error في الإصدار الجديد
        with VideoFileClip(temp_video_path) as video_clip:
            duration_seconds = video_clip.duration
            video_width, video_height = video_clip.size
            fps = video_clip.fps
            
            # ج- فصل الصوت وحفظه (logger=None بديلة لـ verbose)
            video_clip.audio.write_audiofile(temp_audio_path, logger=None)

        # د- رفع الفيديو لـ Supabase Storage
        storage_path = f"{current_user.id}/{unique_id}.{file_ext}"
        supabase_client.storage.from_("videos").upload(
            path=storage_path,
            file=file_content,
            file_options={"content-type": file.content_type}
        )
        video_url = supabase_client.storage.from_("videos").get_public_url(storage_path)

        # هـ- استخراج النص عبر Groq Whisper
        script_text = groq_client.transcribe_audio(temp_audio_path)
        
        if "❌" in script_text:
            raise Exception(f"خطأ في معالجة الصوت: {script_text}")

        # و- توليد الـ Embedding عبر Cohere
        vectors = embedding_client.get_embeddings([script_text], input_type="search_document")
        vector = vectors[0] if vectors else None

        # ز- الحفظ في قاعدة البيانات
        new_video_record = VideoScriptEmbedding(
            user_id=current_user.id,
            video_url=video_url,
            script_text=script_text,
            embedding=vector
        )
        
        db.add(new_video_record)
        db.commit()
        db.refresh(new_video_record)

        return {
            "id": new_video_record.id,
            "video_url": video_url,
            "script": script_text,
            "metadata": {
                "duration_sec": round(duration_seconds, 2),
                "format": file_ext,
                "size_mb": round(file_size_mb, 2),
                "resolution": f"{video_width}x{video_height}",
                "fps": round(fps, 0)
            },
            "status": "Success: Video Processed & Embedded"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # ح- تنظيف الملفات (إضافة محاولة للتأكد من فك قفل ويندوز)
        import time
        time.sleep(1) # تأخير بسيط لضمان أن النظام حرر الملفات
        if os.path.exists(temp_video_path):
            try: os.remove(temp_video_path)
            except: pass
        if os.path.exists(temp_audio_path):
            try: os.remove(temp_audio_path)
            except: pass