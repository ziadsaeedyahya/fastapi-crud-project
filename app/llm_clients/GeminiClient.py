import google.generativeai as genai
from PIL import Image
import io
from app.core.config import settings

class GeminiClient:
    def __init__(self):
        # بنربط الـ API Key من الـ Config
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # الموديل اللي اخترته
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def get_image_response(self, prompt: str, image_bytes: bytes = None):
        """
        بتاخد البرومبت والـ bytes وبترجع النص والتوكنز في Dict
        """
        try:
            if image_bytes:
                # 1. حالة وجود صورة
                img = Image.open(io.BytesIO(image_bytes))
                response = self.model.generate_content([prompt, img])
            else:
                # 2. حالة سؤال متابعة
                response = self.model.generate_content(prompt)
            
            # استخراج بيانات الاستهلاك (Tokens)
            usage = {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count
            }
            
            # بنرجع القاموس عشان المانجر يوزعه
            return {
                "text": response.text,
                "usage": usage
            }
            
        except Exception as e:
            return {
                "text": f"Error processing with Gemini: {str(e)}",
                "usage": {"error": True}
            }

# نسخة واحدة للـ Manager
gemini_client = GeminiClient()