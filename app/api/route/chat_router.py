import os
from enum import Enum
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from supabase import create_client, Client
from app.core.config import settings
from app.services.chat_service import ChatService
from app.clientsdatabase_clients.db_manager import get_db_by_source
from app.api.auth_deps import get_current_user

router = APIRouter()

# إنشاء كليانت سوبابيس (بيقرأ من الـ config اللي واخد من الـ .env)
supabase_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

class LLMProvider(str, Enum):
    cohere = "cohere"
    groq = "groq"

@router.post("/ask")
async def ask_ai(
    prompt: str = Form(...), 
    db_source: str = Form("supabase"),
    provider: LLMProvider = Form(
        LLMProvider.cohere, 
        description="💡 Note: Choose 'groq' for files (PDF), 'cohere' for text."
    ), 
    file: UploadFile = File(None), 
    current_user: any = Depends(get_current_user)
):
    # فتح اتصال الداتابيز
    db_gen = get_db_by_source(db_source)
    db = next(db_gen)

    file_url = None
    try:
        # 1. لو فيه ملف، ارفعه لسوبابيس وهات اللينك
        if file:
            # قراءة الملف كـ bytes
            file_content = await file.read()
            
            # تحديد مسار فريد للملف: chats/رقم_اليوزر/اسم_الملف
            file_path_in_bucket = f"chats/{current_user.id}/{file.filename}"
            
            # الرفع لـ Storage
            supabase_client.storage.from_(settings.SUPABASE_BUCKET_NAME).upload(
                path=file_path_in_bucket,
                file=file_content,
                file_options={"content-type": file.content_type, "x-upsert": "true"}
            )
            
            # الحصول على الرابط العام (Public URL)
            # ملحوظة: تأكد إن الـ Bucket اللي اسمه 'files' معمول Public في سوبابيس
            url_res = supabase_client.storage.from_(settings.SUPABASE_BUCKET_NAME).get_public_url(file_path_in_bucket)
            file_url = url_res

        chat_service = ChatService(db)
        
        # 2. نبعت اللينك للسيرفيس بدل المسار المحلي
        answer = chat_service.ask_ai(
            user_id=current_user.id, 
            prompt=prompt, 
            provider=provider.value,
            file_path=file_url # اللينك دلوقتي هيروح هنا
        )
        
        # إضافة اللينك في الرد النهائي عشان اليوزر يفتحه
        if file_url:
            answer["uploaded_file_url"] = file_url
            
        return answer

    except Exception as e:
        print(f"🔴 Router/Storage Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File error: {str(e)}")
    finally:
        db_gen.close()