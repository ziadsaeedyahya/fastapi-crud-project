import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self):
        # تأكد إنك ضفت GEMINI_API_KEY في ملف .env
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ Warning: GEMINI_API_KEY not found in environment variables!")
        
        genai.configure(api_key=api_key)
        # بنستخدم موديل flash لأنه سريع جداً وبيدعم الملفات بشكل ممتاز
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def get_response(self, prompt: str, file_path: str = None):
        try:
            content = []
            
            # 1. لو فيه ملف، بنرفعه لجوجل الأول عشان الموديل "يشوفه"
            if file_path and os.path.exists(file_path):
                # رفع الملف لمساحة التخزين المؤقتة في جيمناي
                uploaded_file = genai.upload_file(path=file_path)
                content.append(uploaded_file)
            
            # 2. إضافة النص (السؤال)
            content.append(prompt)

            # 3. توليد الرد
            response = self.model.generate_content(content)
            
            # 4. بنرجع الداتا بنفس التنسيق الموحد اللي عملناه في كوهير عشان المشروع ميبوظش
            return {
                "text": response.text,
                "usage": {
                    "prompt_tokens": response.usage_metadata.prompt_token_count,
                    "candidates_tokens": response.usage_metadata.candidates_token_count,
                    "total_tokens": response.usage_metadata.total_token_count
                }
            }
        except Exception as e:
            print(f"❌ Gemini Error: {str(e)}")
            return {
                "text": f"Sorry, I encountered an error with Gemini: {str(e)}",
                "usage": {"total_tokens": 0}
            }

# عمل نسخة واحدة جاهزة للاستدعاء
gemini_client = GeminiClient()