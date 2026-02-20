import fitz  # PyMuPDF لقراءة الـ PDF
from sqlalchemy.orm import Session
from app.repositories.chat_repository import ChatRepository
from app.llm_clients.llm_manager import llm_manager 
from app.models.chat_model import ChatHistory
import io
import requests

class ChatService:
    def __init__(self, db: Session):
        self.chat_repo = ChatRepository(db)

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """يقرأ الملف سواء كان رابط URL أو مسار محلي"""
        try:
            text = ""
            if file_path.startswith("http"):
                response = requests.get(file_path)
                response.raise_for_status()
                doc = fitz.open(stream=io.BytesIO(response.content), filetype="pdf")
            else:
                doc = fitz.open(file_path)

            with doc:
                for page in doc:
                    text += page.get_text()
            
            print(f"✅ Successfully extracted {len(text)} characters from PDF")
            return text
        except Exception as e:
            print(f"❌ Error reading PDF: {str(e)}")
            return ""

    def ask_ai(self, user_id: int, prompt: str, provider: str = "cohere", file_path: str = None):
        # 1. جلب تاريخ المحادثة (الذاكرة)
        # بنجيب آخر 5 رسائل عشان يفتكر السياق (بما في ذلك وصف الصور القديمة)
        context_data = self.chat_repo.get_history_by_user(user_id=user_id, limit=5)
        
        history_text = ""
        for chat in reversed(context_data):
            history_text += f"User: {chat.prompt}\nAI: {chat.response}\n"

        # 2. معالجة الملف وتحديد الـ Provider
        file_content = ""
        actual_provider = provider 

        if file_path:
            file_path_lower = file_path.lower()
            # حالة الـ PDF
            if file_path_lower.endswith(".pdf"):
                print(f"📄 Extracting text from PDF: {file_path}")
                file_content = self._extract_text_from_pdf(file_path)
                actual_provider = "groq"
            # حالة الصور
            elif any(file_path_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                print(f"🖼️ Image detected, switching to Gemini: {file_path}")
                actual_provider = "gemini"

        # 3. بناء الـ Prompt الذكي
        system_instruction = (
            "You are a helpful and concise assistant. "
            "Use the 'Previous conversation' to remember context, images, or documents already discussed."
        )
        
        # لو فيه PDF، بنحط النص بتاعه مباشرة
        if file_content:
            full_prompt = (
                f"{system_instruction}\n\n"
                f"DOCUMENT CONTENT (PDF):\n{file_content}\n"
                f"------------------------\n"
                f"Previous conversation:\n{history_text}\n"
                f"User Question: {prompt}"
            )
        else:
            # في حالة الصورة أو الدردشة العادية، بنعتمد على الـ History
            # لو هي صورة، الـ Manager هيبعت الـ file_path لجيميناي مع الـ prompt ده
            full_prompt = (
                f"{system_instruction}\n\n"
                f"Previous conversation:\n{history_text}\n"
                f"Current question/action: {prompt}"
            )
        
        # 4. طلب الرد من المانجر
        raw_response = llm_manager.get_response(
            prompt=full_prompt, 
            provider=actual_provider,
            file_path=file_path 
        )

        # 5. معالجة الرد واستخراج النص والتوكنز
        clean_text = ""
        usage_info = {}

        if isinstance(raw_response, dict):
            clean_text = raw_response.get('text', "")
            usage_info = raw_response.get('usage', {
                "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0
            })
        else:
            clean_text = str(raw_response)
            usage_info = {"info": "Manual wrap"}

        # 6. الحفظ في الداتابيز (دي الذاكرة اللي هيقرأ منها المرة الجاية)
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

        # 7. الرد النهائي
        return {
            "answer": clean_text,
            "usage": usage_info,
            "chat_id": saved_obj.id if saved_obj else None,
            "status": "success",
            "provider_used": actual_provider
        }