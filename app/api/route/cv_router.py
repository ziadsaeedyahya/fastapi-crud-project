from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.api.auth_deps import get_current_user, get_auth_db
from app.services.cv_service import CVReviewerService
from app.llm_clients.GeminiClient import GeminiClient 
from app.clientsdatabase_clients import supabase_client 

# استيراد الـ Schemas الجديدة
from app.schemas.cv_schema import CVAnalysisResponse, CVShortResponse, CVFullResponse

router = APIRouter(prefix="/cv", tags=["CV Reviewer"])

# 1. تحليل CV جديد (POST)
@router.post("/analyze", response_model=CVAnalysisResponse)
async def analyze_cv_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_auth_db),
    current_user = Depends(get_current_user)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    llm = GeminiClient()
    service = CVReviewerService(db=db, llm_client=llm, storage_client=supabase_client.storage) 

    try:
        return await service.process_and_analyze_cv(file, current_user.id)
    except Exception as e:
        print(f"❌ Error in POST /analyze: {e}")
        raise HTTPException(status_code=500, detail="CV analysis failed")

# 2. جلب قائمة الـ CVs المختصرة (GET)
@router.get("/", response_model=List[CVShortResponse])
async def get_all_cvs_endpoint(
    db: Session = Depends(get_auth_db),
    current_user = Depends(get_current_user)
):
    try:
        service = CVReviewerService(db=db, llm_client=None, storage_client=None)
        return service.get_user_cvs(str(current_user.id))
    except Exception as e:
        print(f"❌ Error in GET /cv/: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve CVs")

# 3. جلب تفاصيل CV محدد (GET by ID)
@router.get("/{cv_id}", response_model=CVFullResponse)
async def get_cv_detail_endpoint(
    cv_id: UUID,
    db: Session = Depends(get_auth_db),
    current_user = Depends(get_current_user)
):
    try:
        service = CVReviewerService(db=db, llm_client=None, storage_client=None)
        cv = service.get_cv_by_id(cv_id, str(current_user.id))
        
        if not cv:
            raise HTTPException(status_code=404, detail="CV not found or access denied")
        
        return cv
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in GET /cv/{{id}}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching CV details")