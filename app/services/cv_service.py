import fitz  # PyMuPDF
from fastapi import UploadFile
import json
import uuid
from sqlalchemy.orm import Session
from app.models.cv_model import CVAnalysis 

class CVReviewerService:
    def __init__(self, db: Session, llm_client, storage_client):
        self.db = db
        self.llm_client = llm_client
        self.storage_client = storage_client 

    def _extract_text_from_pdf(self, file_bytes: bytes) -> str:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    async def process_and_analyze_cv(self, file: UploadFile, user_id: uuid.UUID):
        # 1. قراءة محتوى الملف
        contents = await file.read()
        
        # 2. إنشاء مسار فريد للملف
        file_extension = file.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_extension}"
        storage_path = f"cvs/{user_id}/{file_name}"
        bucket_name = "cv-bucket"

        # 3. الرفع والحصول على URL
        try:
            self.storage_client.from_(bucket_name).upload(
                path=storage_path,
                file=contents,
                file_options={"content-type": file.content_type, "x-upsert": "true"}
            )
            cv_url = self.storage_client.from_(bucket_name).get_public_url(storage_path)
        except Exception as e:
            print(f"❌ Storage Upload Error: {e}")
            raise e

        # 4. استخراج النص
        raw_text = self._extract_text_from_pdf(contents)

        # 5. تجهيز الـ Prompt (تم إضافة التعليم والجامعة)
        prompt = f"""
        You are an expert Technical Recruiter. Analyze the provided CV text and extract the details strictly in JSON format.
        
        Required Fields:
        1. candidate_name: Full name.
        2. university: Name of the university or college.
        3. graduation_year: The year of graduation (or expected graduation).
        4. technical_skills: A list of core technologies mentioned.
        5. years_of_experience: Estimated number of years (e.g., "1+ years").
        6. score_out_of_10: Overall technical rating as a number.
        7. summary: A short professional summary.
        8. top_weaknesses: List exactly 2 weakest points.
        9. missing_skills: List 2-3 missing skills for a professional backend role.

        CV Text:
        {raw_text}
        
        Return ONLY valid JSON.
        """

        # 6. إرسال الطلب للـ LLM
        response = self.llm_client.generate_response(prompt)
        
        # 7. تنظيف وتحويل الـ Response
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            analysis_dict = json.loads(response[json_start:json_end])
        except Exception:
            analysis_dict = {"error": "Failed to parse AI response", "raw": response}

        # 8. حفظ البيانات في الداتابيز (تأكد من إضافة الأعمدة الجديدة في الموديل أولاً)
        new_cv_entry = CVAnalysis(
            user_id=str(user_id),
            candidate_name=analysis_dict.get("candidate_name"),
            # الحقول الجديدة 👇
            university=analysis_dict.get("university"),
            graduation_year=analysis_dict.get("graduation_year"),
            # --------
            cv_url=cv_url,
            raw_text=raw_text, # مفيد لو حبيت تعمل Search في النصوص بعدين
            analysis_result=analysis_dict,
            score=analysis_dict.get("score_out_of_10")
        )
        
        self.db.add(new_cv_entry)
        self.db.commit()
        self.db.refresh(new_cv_entry)

        return {
            "cv_id": new_cv_entry.id,
            "cv_url": cv_url,
            "analysis": analysis_dict
        }