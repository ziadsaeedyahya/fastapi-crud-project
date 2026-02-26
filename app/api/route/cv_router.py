from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.api.auth_deps import get_current_user, get_auth_db
from app.services.cv_service import CVReviewerService
from app.llm_clients.GeminiClient import GeminiClient 
from app.clientsdatabase_clients import supabase_client 

# 1. استيراد الـ Schema الجديدة (تأكد من إنشاء الملف كما اتفقنا)
from app.schemas.cv_schema import CVAnalysisResponse

router = APIRouter(prefix="/cv", tags=["CV Reviewer"])

# 2. إضافة response_model لضمان فلترة البيانات وعرضها صح في Swagger
@router.post("/analyze", response_model=CVAnalysisResponse)
async def analyze_cv_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_auth_db),
    current_user = Depends(get_current_user)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # تهيئة الـ Clients
    llm = GeminiClient()
    
    # تمرير الـ storage_client (supabase storage)
    service = CVReviewerService(
        db=db, 
        llm_client=llm, 
        storage_client=supabase_client.storage
    ) 

    try:
        # 3. السيرفس هترجع dictionary، و FastAPI هيحوله أوتوماتيك لـ CVAnalysisResponse
        result = await service.process_and_analyze_cv(file, current_user.id)
        return result
    except Exception as e:
        # طباعة الـ Error للتصحيح
        print(f"❌ Error in analyze_cv_endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")