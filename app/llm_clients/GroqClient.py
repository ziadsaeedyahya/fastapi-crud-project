import os
from groq import Groq
from app.core.config import settings

class GroqClient:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.client = Groq(api_key=self.api_key)
        self.model_name = "llama-3.3-70b-versatile"

    # --- دالة الـ Chat القديمة (سيبها زي ما هي بالظبط) ---
    def get_response(self, prompt: str, file_path: str = None):
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_name,
                temperature=0.7,
            )
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
            return {
                "text": f"❌ Groq Error: {str(e)}",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }

    # --- 🆕 الدالة الجديدة (دي اللي هنستخدمها للفيديو والـ Script) ---
    def transcribe_audio(self, audio_file_path: str):
        """
        بتاخد مسار ملف الصوت وتطلعه نص باستخدام Whisper.
        مبتأثرش على دالة الـ get_response نهائي.
        """
        try:
            with open(audio_file_path, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                    file=(audio_file_path, file.read()),
                    model="whisper-large-v3",
                    response_format="text"
                )
                return transcription
        except Exception as e:
            return f"❌ Transcription Error: {str(e)}"

# عمل instance خاص بـ groq
groq_client = GroqClient()