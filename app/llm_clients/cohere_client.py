import cohere
from app.llm_clients.llm_base_client import LLMBaseClient
from app.core.config import settings

class CohereClient(LLMBaseClient):
    def __init__(self):
        # التأكد من سحب الـ API Key من ملف الإعدادات
        self.client = cohere.Client(settings.COHERE_API_KEY)

    def generate_response(self, prompt: str, **kwargs) -> dict:
        # هنا بننادي على Cohere
        response = self.client.chat(
            message=prompt,
            model="command-r-08-2024",
            max_tokens=200,  
            temperature=0.7, # بيخلي الرد طبيعي وأقل رغياً
            **kwargs
        )

       
        text_content = response.text 
        
        # سحب التوكنز بأمان باستخدام getattr
        input_t = getattr(response.meta.tokens, 'input_tokens', 0)
        output_t = getattr(response.meta.tokens, 'output_tokens', 0)

        return {
            "text": text_content,
            "usage": {
                "input_tokens": input_t,
                "output_tokens": output_t,
                "total_tokens": input_t + output_t
            }
        }