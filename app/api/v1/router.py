from fastapi import APIRouter
from app.api.v1 import item_router, user_router, user_item_router, auth_router, chat_router

# هنثبت الاسم على router عشان الـ main.py بيعمل import للـ router
router = APIRouter()

router.include_router(chat_router.router, prefix="/chat", tags=["AI Assistant"])

# ربط بقية الروترات باستخدام نفس المتغير "router"
router.include_router(item_router.router, prefix="/items", tags=["Items"])
router.include_router(user_router.router, prefix="/users", tags=["Users"])
router.include_router(user_item_router.router, prefix="/user-items", tags=["User Items"])
router.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])