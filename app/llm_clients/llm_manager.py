from typing import Any, Dict
from app.llm_clients.cohere_client import CohereClient
from app.llm_clients.gemini_client import gemini_client # استيراد الـ instance اللي عملناه

class LLMManager:
    def __init__(self):
        # بنسجل كل الـ Clients المتاحين هنا
        self._clients = {
            "cohere": CohereClient(),
            "gemini": gemini_client  # ضفنا جيمناي للمجموعة
        }

    def get_response(self, prompt: str, provider: str = "cohere", file_path: str = None, **kwargs) -> Dict[str, Any]:
        # لو فيه ملف، بنحول أوتوماتيك لـ gemini لأن كوهير مش بيدعم ملفات في نسختنا الحالية
        if file_path:
            provider = "gemini"
            
        client = self._clients.get(provider)
        if not client:
            raise ValueError(f"Provider {provider} not supported.")
        
        # لو الموديل هو جيمناي، بنبعت الـ file_path مع الـ prompt
        if provider == "gemini":
            return client.get_response(prompt, file_path=file_path)
        
        # لو كوهير، بننادي الدالة بتاعته العادية
        return client.generate_response(prompt, **kwargs)

# بنعمل Instance واحدة نستخدمها في كل المشروع
llm_manager = LLMManager()