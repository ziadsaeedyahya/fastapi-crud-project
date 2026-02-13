from fastapi import APIRouter
from app.api.v1 import item_router, user_router, user_item_router, auth_router, llm_router

api_router = APIRouter()

# ربط الـ LLM مع بريفكس خاص بيه
api_router.include_router(llm_router.router, prefix="/ai", tags=["AI Generation"])

# ربط بقية الروترات اللي في مشروعك
api_router.include_router(item_router.router, prefix="/items", tags=["Items"])
api_router.include_router(user_router.router, prefix="/users", tags=["Users"])
api_router.include_router(user_item_router.router, prefix="/user-items", tags=["User Items"])
api_router.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])