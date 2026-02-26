from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from uuid import UUID

class CVAnalysisData(BaseModel):
    candidate_name: Optional[str]
    university: Optional[str]
    graduation_year: Optional[str]
    technical_skills: List[str]
    years_of_experience: str
    score_out_of_10: float
    summary: str
    top_weaknesses: List[str]
    missing_skills: List[str]

class CVAnalysisResponse(BaseModel):
    cv_id: UUID
    cv_url: str
    analysis: CVAnalysisData