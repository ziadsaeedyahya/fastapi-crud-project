from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Union
from uuid import UUID
from datetime import datetime

# 1. البيانات اللي الـ AI بيطلعها
class CVAnalysisData(BaseModel):
    # استخدام Union[str, int] بيخليها تقبل النوعين، بس الأحسن نستخدم Config
    candidate_name: Optional[str]
    university: Optional[str]
    graduation_year: Optional[Union[str, int]] # عشان يقبل 2026 كـ رقم أو نص
    technical_skills: List[str]
    years_of_experience: Optional[Union[str, int]] # عشان يقبل 1 كـ رقم أو نص
    score_out_of_10: float
    summary: str
    top_weaknesses: List[str]
    missing_skills: List[str]

    # السطر ده بيخلي Pydantic يحول الأرقام لنصوص لو الحقل مستني String
    model_config = ConfigDict(coerce_numbers_to_str=True)

# 2. الـ Schema للـ GET الكلّي
class CVShortResponse(BaseModel):
    id: UUID
    candidate_name: Optional[str]
    university: Optional[str]
    graduation_year: Optional[Union[str, int]]
    score: Optional[float]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, coerce_numbers_to_str=True)

# 3. الـ Schema للتفاصيل
class CVFullResponse(CVShortResponse):
    cv_url: str
    analysis_result: CVAnalysisData

# 4. الـ Schema اللي بترجع بعد الرفع
class CVAnalysisResponse(BaseModel):
    cv_id: UUID
    cv_url: str
    analysis: CVAnalysisData