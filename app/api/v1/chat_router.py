from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.chat_service import ChatService
from app.clientsdatabase_clients.db_manager import get_db_by_source
from app.schemas.chat_schema import ChatCreate, ChatResponse
from app.api.auth_deps import get_current_user
router = APIRouter()

@router.post("/ask", response_model=None)
def ask_ai(
    payload: ChatCreate, 
    db_source: str = "supabase", # التعديل 1: ضفنا الاختيار هنا (Default: supabase)
    current_user: any = Depends(get_current_user)
):
    # التعديل 2: بنفتح الاتصال يدوي بناءً على الـ db_source
    db_gen = get_db_by_source(db_source)
    db = next(db_gen)

    try:
        chat_service = ChatService(db)
        
        # كدة لو اليوزر بعت ID غلط في الـ Body، إحنا هنستخدم الـ ID الصح اللي في التوكن
        answer = chat_service.ask_ai(user_id=current_user.id, prompt=payload.prompt)
        
        return answer
    except Exception as e:
        print(f"Error: {str(e)}") # عشان تشوف لو فيه غلط في الـ Terminal
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # التعديل 4: قفل الجلسة لضمان استقرار الأداء
        db_gen.close()