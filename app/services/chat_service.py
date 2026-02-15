from sqlalchemy.orm import Session
from app.repositories.chat_repository import ChatRepository
from app.llm_clients.llm_manager import llm_manager 
from app.models.chat_model import ChatHistory

class ChatService:
    def __init__(self, db: Session):
        self.chat_repo = ChatRepository(db)

    def ask_ai(self, user_id: int, prompt: str, file_path: str = None):
        # 1. بنجيب التاريخ القديم عشان الـ AI يفتكر (آخر 5 رسايل مثلاً)
        context_data = self.chat_repo.get_history_by_user(user_id=user_id, limit=5)
        
        # 2. بنحول التاريخ لـ نص (String) عشان نبعته للـ LLM
        history_text = ""
        for chat in reversed(context_data):
            history_text += f"User: {chat.prompt}\nAI: {chat.response}\n"

        # 3. بنجهز الـ prompt الكامل اللي هيبعت للـ LLM (مع تضمين تعليمات خاصة لو فيه ملف)
        system_instruction = "You are a helpful and concise assistant."
        if file_path:
            system_instruction += " Analyze the provided file carefully to answer the user's request."
        else:
            system_instruction += " Use the previous conversation context if relevant."
        full_prompt = f"{system_instruction}\n\nPrevious conversation:\n{history_text}\nCurrent question: {prompt}"
        
        
        raw_response = llm_manager.get_response(
            prompt=full_prompt, 
            file_path=file_path # 👈 مررنا المسار للمانجر هنا
        )

        # 5. استخراج البيانات (بما إننا ضمنا إن الـ client بيرجع dict)
        clean_text = raw_response.get('text', "No response generated")
        usage = raw_response.get('usage', {"info": "Token usage not available"})

        # 6. حفظ المحادثة في الداتابيز
        new_chat = ChatHistory(
            user_id=user_id,
            prompt=prompt,
            response=clean_text
        )
        
        saved_obj = None
        try:
            saved_obj = self.chat_repo.create(new_chat)
            print(f"Successfully saved with ID: {saved_obj.id}")
        except Exception as e:
            print(f"DATABASE ERROR: {str(e)}")

        # 7. الرد النهائي المنظم اللي هيظهر في الـ Swagger
        return {
            "answer": clean_text,
            "usage": usage,
            "chat_id": saved_obj.id if saved_obj else None,
            "status": "success"
        }