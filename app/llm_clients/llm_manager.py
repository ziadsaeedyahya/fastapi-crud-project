from typing import Any, Dict
from app.llm_clients.cohere_client import CohereClient

class LLMManager:
    def __init__(self):
        # حالياً بنعرف Cohere، ومستقبلاً نقدر نضيف غيره هنا
        self._clients = {
            "cohere": CohereClient()
        }

    def get_response(self, prompt: str, provider: str = "cohere", **kwargs) -> Dict[str, Any]:
        client = self._clients.get(provider)
        if not client:
            raise ValueError(f"Provider {provider} not supported.")
        
        return client.generate_response(prompt, **kwargs)

# بنعمل Instance واحدة نستخدمها في كل المشروع (Singleton Pattern)
llm_manager = LLMManager()