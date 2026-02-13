from fastapi import APIRouter, Depends
from app.services.llm_service import LLMService
from app.schemas.llm import LLMRequest, LLMResponse
from app.api.auth_deps import get_current_user 

router = APIRouter()

@router.post("/ask", response_model=LLMResponse)
def ask_question(
    request: LLMRequest,
    current_user=Depends(get_current_user)
):
    """
    إرسال سؤال للموديل والحصول على إجابة مفصلة مع التوكنز
    """
    return LLMService.ask_ai(prompt=request.prompt)