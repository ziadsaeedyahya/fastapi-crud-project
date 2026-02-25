import uuid
import os
import time
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from moviepy import VideoFileClip
from sqlalchemy import text

from app.api.auth_deps import get_current_user 
from app.api.service_deps import get_supabase_db       
from app.llm_clients.GroqClient import groq_client 
from app.llm_clients.cohere_embedding_client import embedding_client
from app.llm_clients.GeminiClient import gemini_client
from app.models.video_script_model import VideoScriptEmbedding, VideoScriptChunk
from app.clientsdatabase_clients.db_manager import supabase_client 

router = APIRouter(prefix="/embeddings", tags=["Embeddings"])

# --- 1. دالة الـ Chunking (كما هي بدون تغيير) ---
def split_text_into_chunks(text: str, chunk_size: int = 200, overlap: int = 40):
    words = text.split()
    chunks = []
    if not words: return chunks
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        if i + chunk_size >= len(words): break
    return chunks

# --- 2. Endpoint معالجة الفيديو ---
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
        file_content = await file.read()
        file_size_mb = len(file_content) / (1024 * 1024)
        with open(temp_video_path, "wb") as f:
            f.write(file_content)

        with VideoFileClip(temp_video_path) as video_clip:
            duration_seconds = video_clip.duration
            video_width, video_height = video_clip.size
            video_clip.audio.write_audiofile(temp_audio_path, logger=None)

        # الرفع لـ Supabase - الـ current_user.id هنا أصبح UUID تلقائياً
        storage_path = f"{current_user.id}/{unique_id}.{file_ext}"
        supabase_client.storage.from_("videos").upload(
            path=storage_path,
            file=file_content,
            file_options={"content-type": file.content_type}
        )
        video_url = supabase_client.storage.from_("videos").get_public_url(storage_path)

        script_text = groq_client.transcribe_audio(temp_audio_path)
        if "❌" in script_text: raise Exception(f"خطأ في معالجة الصوت: {script_text}")

        main_vectors = embedding_client.get_embeddings([script_text], input_type="search_document")
        main_vector = main_vectors[0] if main_vectors else None

        # الحفظ في الجدول الرئيسي (الـ id سيتولد تلقائياً كـ UUID)
        new_video_record = VideoScriptEmbedding(
            user_id=current_user.id, # UUID من الـ Token
            video_url=video_url,
            script_text=script_text,
            embedding=main_vector
        )
        db.add(new_video_record)
        db.flush()

        text_chunks = split_text_into_chunks(script_text)
        if text_chunks:
            chunk_vectors = embedding_client.get_embeddings(text_chunks, input_type="search_document")
            for content, vec in zip(text_chunks, chunk_vectors):
                # الربط باستخدام الـ UUID الجديد لـ new_video_record.id
                new_chunk = VideoScriptChunk(video_id=new_video_record.id, chunk_content=content, embedding=vec)
                db.add(new_chunk)

        db.commit()
        db.refresh(new_video_record)

        return {
            "video_id": new_video_record.id, # سيرجع UUID للمستخدم
            "video_url": video_url,
            "total_chunks": len(text_chunks),
            "metadata": {
                "duration_sec": round(duration_seconds, 2),
                "resolution": f"{video_width}x{video_height}",
                "size_mb": round(file_size_mb, 2)
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_video_path): os.remove(temp_video_path)
        if os.path.exists(temp_audio_path): os.remove(temp_audio_path)

# --- 3. GET: عرض فيديوهات اليوزر ---
@router.get("/my-videos")
async def get_user_videos(current_user = Depends(get_current_user), db: Session = Depends(get_supabase_db)):
    videos = db.query(VideoScriptEmbedding).filter(
        VideoScriptEmbedding.user_id == current_user.id # مقارنة UUID بـ UUID
    ).order_by(desc(VideoScriptEmbedding.created_at)).all()
    
    return [{
        "id": v.id, 
        "url": v.video_url, 
        "date": v.created_at,
        "preview": v.script_text[:100] + "..." if v.script_text else ""
    } for v in videos]

# --- 4. GET: تفاصيل فيديو (تحديث النوع لـ UUID) ---
@router.get("/video/{video_id}")
async def get_video_details(
    video_id: uuid.UUID, # تغيير النوع هنا من int لـ uuid.UUID
    current_user = Depends(get_current_user), 
    db: Session = Depends(get_supabase_db)
):
    video = db.query(VideoScriptEmbedding).filter(
        VideoScriptEmbedding.id == video_id, 
        VideoScriptEmbedding.user_id == current_user.id
    ).first()
    
    if not video: raise HTTPException(status_code=404, detail="الفيديو غير موجود")
    
    return {
        "id": video.id,
        "url": video.video_url,
        "chunks": [c.chunk_content for c in video.chunks]
    }

# --- 5. POST: Ask AI (تحديث النوع لـ UUID) ---
@router.post("/ask-ai")
async def ask_ai_about_video(
    video_id: uuid.UUID, # تغيير النوع هنا من int لـ uuid.UUID
    user_query: str, 
    current_user = Depends(get_current_user), 
    db: Session = Depends(get_supabase_db)
):
    query_vec = embedding_client.get_embeddings([user_query], input_type="search_query")[0]
    query_vec_str = f"[{','.join(map(str, query_vec))}]"

    # جلب البيانات مع تجنب عمود الـ embedding مباشرة
    chunks_data = db.query(
        VideoScriptChunk.id, 
        VideoScriptChunk.chunk_content
    ).filter(
        VideoScriptChunk.video_id == video_id
    ).order_by(
        text(f"embedding::vector <=> '{query_vec_str}'::vector")
    ).limit(3).all()
    
    if not chunks_data: 
        raise HTTPException(status_code=404, detail="لم نجد محتوى متعلق بسؤالك")
    
    context = "\n\n".join([item.chunk_content for item in chunks_data])
    
    prompt = f"""
    أنت مساعد ذكي يساعد المستخدمين في فهم محتوى الفيديو.
    بناءً على النصوص المقتبسة التالية من الفيديو فقط:
    ---
    {context}
    ---
    سؤال المستخدم: {user_query}
    
    تعليمات:
    - أجب بدقة بناءً على النص المقدم.
    - إذا لم تتوفر الإجابة في النص، قل أن الفيديو لم يتطرق لهذا الموضوع.
    """
    
    answer = gemini_client.generate_response(prompt)
    
    return {
        "answer": answer,
        "source_chunks": [item.id for item in chunks_data] # سترجع قائمة UUIDs
    }