import google.generativeai as genai
from PIL import Image
import io
import os # هنستخدم os لو عايز تقرأ من الـ env مباشرة
from app.core.config import settings

class GeminiClient:
    def __init__(self):
        # بنجيب الـ Key من الـ config اللي أنت لسه معدله
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # هنثبت اسم الموديل اللي اشتغل معاك هنا مباشرة
        self.model_name = "gemini-2.5-flash" 
        self.model = genai.GenerativeModel(self.model_name)

    def generate_response(self, prompt: str, image_bytes: bytes = None):
        try:
            content = [prompt]
            if image_bytes:
                img = Image.open(io.BytesIO(image_bytes))
                content.append(img)
            
            response = self.model.generate_content(content)
            return response.text
        except Exception as e:
            print(f"❌ Gemini Error: {str(e)}")
            return f"Error processing with Gemini: {str(e)}"

gemini_client = GeminiClient()