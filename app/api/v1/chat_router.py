import shutil
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.services.chat_service import ChatService
from app.clientsdatabase_clients.db_manager import get_db_by_source
from app.api.auth_deps import get_current_user

router = APIRouter()

@router.post("/ask")
async def ask_ai(
    prompt: str = Form(...),  # استلام النص كـ Form
    db_source: str = Form("supabase"),
    file: UploadFile = File(None), # استلام ملف (اختياري)
    current_user: any = Depends(get_current_user)
):
    # 1. فتح اتصال الداتابيز
    db_gen = get_db_by_source(db_source)
    db = next(db_gen)

    file_path = None
    try:
        # 2. لو فيه ملف، بنحفظه مؤقتاً عشان نبعت مساره للجيمناي
        if file:
            temp_dir = "temp_uploads"
            os.makedirs(temp_dir, exist_ok=True)
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        chat_service = ChatService(db)
        
        # 3. نبعت الطلب للسيرفيس (وزودنا الـ file_path)
        answer = chat_service.ask_ai(
            user_id=current_user.id, 
            prompt=prompt, 
            file_path=file_path
        )
        
        return answer

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 4. تنظيف: مسح الملف المؤقت بعد ما خلصنا عشان مساحة الجهاز
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        db_gen.close()