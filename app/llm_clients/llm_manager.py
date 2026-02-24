import os
import requests
from typing import Any, Dict
from app.llm_clients.cohere_client import CohereClient
from app.llm_clients.GroqClient import groq_client 
from app.llm_clients.GeminiClient import gemini_client 

class LLMManager:
    def __init__(self):
        self._clients = {
            "cohere": CohereClient(),
            "groq": groq_client,
            "gemini": gemini_client
        }

    def get_response(self, prompt: str, provider: str = "cohere", file_path: str = None, **kwargs) -> Dict[str, Any]:
        
        # 1. تحديد الـ Provider تلقائياً بناءً على نوع الملف
        if file_path and provider == "cohere":
            # تنظيف الرابط لجلب الامتداد صح حتى لو فيه Query Parameters
            clean_path = file_path.split('?')[0]
            ext = os.path.splitext(clean_path)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.webp']:
                provider = "gemini"
            elif ext == '.pdf':
                provider = "groq"

        client = self._clients.get(provider)
        if not client:
            client = self._clients.get("groq") 

        # 2. تنفيذ الطلب بناءً على الـ Provider
        if provider == "gemini":
            try:
                file_data = None
                # تجهيز بيانات الملف لو موجود (أول مرة رفع)
                if file_path:
                    if file_path.startswith("http"):
                        resp = requests.get(file_path, timeout=10)
                        resp.raise_for_status()
                        file_data = resp.content
                    else:
                        with open(file_path, "rb") as f:
                            file_data = f.read()

                # استدعاء GeminiClient (دلوقتي بيرجع Dict فيه نص وتوكنز)
                # الـ Client هو المسؤول يقرر يبعت صورة ولا نص بس بناءً على file_data
                result = client.get_image_response(prompt, file_data)
                
                # تنظيم بيانات الرد
                response_data = {
                    "text": result.get("text", ""),
                    "usage": result.get("usage", {})
                }
                # إضافة اسم الموديل يدوياً للتوثيق
                if "model" not in response_data["usage"]:
                    response_data["usage"]["model"] = "gemini-2.5-flash"

            except Exception as e:
                response_data = f"❌ Gemini Manager Error: {str(e)}"

        elif provider == "groq":
            response_data = client.get_response(prompt, file_path=file_path)
        
        else: # Cohere
            try:
                response_data = client.generate_response(prompt, **kwargs)
            except AttributeError:
                response_data = client.get_response(prompt, **kwargs)

        # 3. توحيد شكل الرد (Response Schema)
        # لو الرد راجع نص (في حالة الخطأ أو Providers تانية)، بنحطه في قالب Dict
        if isinstance(response_data, str):
            return {
                "text": response_data,
                "usage": {"info": "Manual wrap for consistency"}
            }
            
        return response_data

llm_manager = LLMManager()