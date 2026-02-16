import fitz  # PyMuPDF لقراءة الـ PDF
from sqlalchemy.orm import Session
from app.repositories.chat_repository import ChatRepository
from app.llm_clients.llm_manager import llm_manager 
from app.models.chat_model import ChatHistory

class ChatService:
    def __init__(self, db: Session):
        self.chat_repo = ChatRepository(db)

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """وظيفة جانبية لاستخراج النص من ملف الـ PDF"""
        try:
            text = ""
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
            return text
        except Exception as e:
            print(f"❌ Error reading PDF: {str(e)}")
            return ""

    # التعديل هنا: أضفنا provider كـ parameter
    def ask_ai(self, user_id: int, prompt: str, provider: str = "cohere", file_path: str = None):
        # 1. جلب تاريخ المحادثة
        context_data = self.chat_repo.get_history_by_user(user_id=user_id, limit=5)
        
        history_text = ""
        for chat in reversed(context_data):
            history_text += f"User: {chat.prompt}\nAI: {chat.response}\n"

        # 2. معالجة الملف وتحديد الـ Provider النهائي
        file_content = ""
        actual_provider = provider # نستخدم اللي جاي من الـ Router مبدئياً

        if file_path and file_path.lower().endswith(".pdf"):
            print(f"📄 Extracting text from: {file_path}")
            file_content = self._extract_text_from_pdf(file_path)
            # لو فيه ملف، بنجبر السيستم يروح لـ Groq حتى لو المستخدم اختار Cohere
            actual_provider = "groq" 

        # 3. بناء الـ Prompt
        system_instruction = "You are a helpful and concise assistant."
        
        if file_content:
            full_prompt = (
                f"{system_instruction}\n\n"
                f"DOCUMENT CONTENT:\n{file_content}\n"
                f"------------------------\n"
                f"Previous conversation:\n{history_text}\n"
                f"User Question: {prompt}"
            )
        else:
            full_prompt = (
                f"{system_instruction}\n\n"
                f"Previous conversation:\n{history_text}\n"
                f"Current question: {prompt}"
            )
        
        # 4. طلب الرد من المانجر باستخدام الـ actual_provider
        raw_response = llm_manager.get_response(
            prompt=full_prompt, 
            provider=actual_provider,
            file_path=file_path 
        )

        # 5. معالجة الرد واستخراج الـ Tokens
        clean_text = ""
        usage_info = {}

        if isinstance(raw_response, dict):
            # استخراج النص
            clean_text = raw_response.get('text', "")
            # استخراج الـ Usage لو موجود (وده اللي هنعدله في الـ manager)
            usage_info = raw_response.get('usage', {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            })
        else:
            clean_text = str(raw_response)
            usage_info = {"info": "Token usage not tracked for this response"}

        # 6. حفظ في الداتابيز
        new_chat = ChatHistory(
            user_id=user_id,
            prompt=prompt,
            response=clean_text
        )
        
        saved_obj = None
        try:
            saved_obj = self.chat_repo.create(new_chat)
        except Exception as e:
            print(f"DATABASE ERROR: {str(e)}")

        # 7. الرد النهائي المنظم مع الـ Tokens
        return {
            "answer": clean_text,
            "usage": usage_info,  # 👈 دلوقتي هيرجع الأرقام الحقيقية
            "chat_id": saved_obj.id if saved_obj else None,
            "status": "success",
            "provider_used": actual_provider
        }