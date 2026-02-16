import os
from groq import Groq
from app.core.config import settings

class GroqClient:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.client = Groq(api_key=self.api_key)
        self.model_name = "llama-3.3-70b-versatile"

    def get_response(self, prompt: str, file_path: str = None):
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_name,
                temperature=0.7,
            )
            
            # التعديل هنا: استخراج الـ Usage من رد Groq
            usage = chat_completion.usage
            
            return {
                "text": chat_completion.choices[0].message.content,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                }
            }
            
        except Exception as e:
            # في حالة الخطأ، بنرجع شكل موحد برضه عشان البرنامج ميقفش
            return {
                "text": f"❌ Groq Error: {str(e)}",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }

# عمل instance خاص بـ groq
groq_client = GroqClient()