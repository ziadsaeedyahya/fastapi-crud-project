from typing import Any, Dict
from app.llm_clients.cohere_client import CohereClient
from app.llm_clients.GroqClient import groq_client 

class LLMManager:
    def __init__(self):
        self._clients = {
            "cohere": CohereClient(),
            "groq": groq_client
        }

    def get_response(self, prompt: str, provider: str = "cohere", file_path: str = None, **kwargs) -> Dict[str, Any]:
        # 1. لو فيه ملف، بنحول أوتوماتيك لـ groq
        if file_path:
            provider = "groq"
            
        client = self._clients.get(provider)
        if not client:
            client = self._clients.get("groq") 
        
        # 2. تنفيذ الطلب
        # هنا بنفترض إن الـ Clients بتوعك (Groq و Cohere) تم تعديلهم ليرجعوا Dict فيه النص والـ Usage
        if provider == "groq":
            response_data = client.get_response(prompt, file_path=file_path)
        else:
            try:
                response_data = client.generate_response(prompt, **kwargs)
            except AttributeError:
                response_data = client.get_response(prompt, **kwargs)

        # 3. التأكد من توحيد شكل الرد (Response Schema)
        # لو الـ Client لسه بيرجع نص بس، بنحوله لـ Dict عشان الـ Service متضربش
        if isinstance(response_data, str):
            return {
                "text": response_data,
                "usage": {"info": "Token counting not implemented in client"}
            }
            
        return response_data

llm_manager = LLMManager()