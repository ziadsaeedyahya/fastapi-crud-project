from sqlalchemy.orm import Session
from app.repositories.chat_repository import ChatRepository
from app.services.llm_service import LLMService # اتأكد من اسم الملف عندك
from app.schemas.chat_schema import ChatCreate

class ChatService:
    def __init__(self, db: Session):
        self.chat_repo = ChatRepository(db)
        self.llm_service = LLMService()

    def ask_ai(self, user_id: int, prompt: str):
        # 1. بنجيب التاريخ القديم عشان الـ AI يفتكر (آخر 5 رسايل مثلاً)
        context_data = self.chat_repo.get_history_by_user(user_id=user_id, limit=5)
        
        # 2. بنحول التاريخ لـ نص (String) عشان نبعته للـ LLM
        history_text = ""
        for chat in reversed(context_data): # reversed عشان نجيب من الأقدم للأحدث
            history_text += f"User: {chat.prompt}\nAI: {chat.response}\n"

        # 3. بنجهز الـ Prompt النهائي
        full_prompt = f"Previous conversation:\n{history_text}\nCurrent question: {prompt}"

        # 4. بنكلم Cohere (الخدمة اللي إنت عملتها قبل كدة)
        ai_response = self.llm_service.generate_response(full_prompt)

        # 5. بنسيف المحادثة الجديدة في الداتابيز
        self.chat_repo.create({
            "user_id": user_id,
            "prompt": prompt,
            "response": ai_response
        })

        return ai_response