import cohere
from app.llm_clients.llm_base_client import LLMBaseClient
from app.core.config import settings

class CohereClient(LLMBaseClient):
    def __init__(self):
        self.client = cohere.Client(settings.COHERE_API_KEY)

    def generate_response(self, prompt: str, **kwargs) -> dict:
        response = self.client.chat(
            message=prompt,
            model="command-r-08-2024", 
            **kwargs
        )
        # هنا بنجمع كل الـ Output اللي يهم اليوزر
        return {
            "text": response.text,
            "meta": {
                "tokens": {
                    "input": response.meta.tokens.input_tokens,
                    "output": response.meta.tokens.output_tokens,
                    "total": response.meta.tokens.input_tokens + response.meta.tokens.output_tokens
                },
                "model": "command-r-08-2024",
                "finish_reason": response.finish_reason
            }
        }