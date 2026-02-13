from fastapi import APIRouter
from app.api.v1 import item_router, user_router, user_item_router, auth_router, llm_router

# هنثبت الاسم على router عشان الـ main.py بيعمل import للـ router
router = APIRouter()

# ربط الـ LLM مع بريفكس خاص بيه
router.include_router(llm_router.router, prefix="/ai", tags=["AI Generation"])

# ربط بقية الروترات باستخدام نفس المتغير "router"
router.include_router(item_router.router, prefix="/items", tags=["Items"])
router.include_router(user_router.router, prefix="/users", tags=["Users"])
router.include_router(user_item_router.router, prefix="/user-items", tags=["User Items"])
router.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])