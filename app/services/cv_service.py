import fitz  # PyMuPDF
from fastapi import UploadFile
import json
import uuid
from sqlalchemy.orm import Session
from app.models.cv_model import CVAnalysis # تأكد من إنشاء الموديل ده

class CVReviewerService:
    def __init__(self, db: Session, llm_client, storage_client):
        self.db = db
        self.llm_client = llm_client
        self.storage_client = storage_client # الكلاينت المسؤول عن Supabase Storage

    def _extract_text_from_pdf(self, file_bytes: bytes) -> str:
        """استخراج النص من ملف الـ PDF"""
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    async def process_and_analyze_cv(self, file: UploadFile, user_id: uuid.UUID):
        # 1. قراءة محتوى الملف
        contents = await file.read()
        
        # 2. رفع الملف للـ Storage (عشان نرجعلوا اللينك واليوزر ميرفعوش تاني)
        # بنعمل اسم فريد للملف باستخدام الـ UUID
        file_extension = file.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_extension}"
        storage_path = f"cvs/{user_id}/{file_name}"
        
        # نرفع الملف ونحصل على الـ Public URL
        cv_url = self.storage_client.upload_file(
            bucket_name="cv-bucket", 
            path=storage_path, 
            file_content=contents,
            content_type=file.content_type
        )

        # 3. استخراج النص للتحليل
        raw_text = self._extract_text_from_pdf(contents)

        # 4. تجهيز الـ Prompt "العبقري" (شامل نقاط الضعف)
        prompt = f"""
        You are an expert Technical Recruiter. Analyze the provided CV text and extract the following details strictly in JSON format.
        
        Required Fields:
        1. candidate_name: Full name.
        2. technical_skills: A list of core technologies mentioned.
        3. years_of_experience: Estimated number of years.
        4. score_out_of_10: Overall technical rating.
        5. summary: A 2-sentence summary of their profile.
        6. top_weaknesses: List exactly the 2 weakest points in this CV.
        7. missing_skills: Mention 2-3 critical skills for a backend role that are NOT in this CV.

        CV Text:
        {raw_text}
        
        Return ONLY valid JSON. Avoid any markdown formatting.
        """

        # 5. إرسال الطلب للـ LLM
        response = self.llm_client.generate_content(prompt)
        
        # 6. تنظيف الـ Response وتحويله لـ Dictionary
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            analysis_dict = json.loads(response[json_start:json_end])
        except Exception:
            analysis_dict = {"error": "Failed to parse AI response", "raw": response}

        # 7. حفظ البيانات في الداتابيز (الـ Metadata + لينك الملف)
        new_cv_entry = CVAnalysis(
            user_id=user_id,
            candidate_name=analysis_dict.get("candidate_name"),
            cv_url=cv_url,
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