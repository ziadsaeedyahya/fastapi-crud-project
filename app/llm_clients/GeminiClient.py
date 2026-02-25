import google.generativeai as genai
from PIL import Image
import io
from app.core.config import settings

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_response(self, prompt: str):
        """
        دالة بسيطة مخصصة للـ RAG (Video Chat) تأخذ نص وترد بنص
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ فشل Gemini في الرد: {str(e)}"

    def get_image_response(self, prompt: str, image_bytes: bytes = None):
        """
        الدالة القديمة بتاعتك زي ما هي (للتعامل مع الصور والـ Usage)
        """
        try:
            if image_bytes:
                img = Image.open(io.BytesIO(image_bytes))
                response = self.model.generate_content([prompt, img])
            else:
                response = self.model.generate_content(prompt)
            
            usage = {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count
            }
            
            return {
                "text": response.text,
                "usage": usage
            }
            
        except Exception as e:
            return {
                "text": f"Error processing with Gemini: {str(e)}",
                "usage": {"error": True}
            }

# نسخة واحدة للاستخدام في الـ Router
gemini_client = GeminiClient()