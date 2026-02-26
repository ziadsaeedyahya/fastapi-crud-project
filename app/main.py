from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import traceback

# 1. استيراد الـ Routers (ضفنا الـ cv_router)
from app.api.route.router import router
from app.api.route import embedding_router, cv_router 

from app.clientsdatabase_clients import postgres_client, supabase_client, close_all_connections

# 2. Import models (ضفنا الـ cv_model)
from app.models import (
    item_model, 
    user_item_model, 
    user_model, 
    embedding_model, 
    video_script_model,
    cv_model 
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up application...")
    
    # ملحوظة: لو حبيت تكريت الجداول أوتوماتيك، فك الكومنت عن الجزء اللي تحت ده
    
    # 1. PostgreSQL (Docker)
    try:
        postgres_client.create_tables()
        print("✅ PostgreSQL tables created")
    except Exception as e:
        print(f"❌ Failed to create PostgreSQL tables: {e}")
        raise 
    
    # 2. Supabase
    try:
        supabase_client.create_tables()
        print("✅ Supabase tables created")
    except Exception as e:
        print(f"⚠️  Supabase not available: {e}")
    
    yield
    
    close_all_connections()
    print("✅ Database connections closed")


app = FastAPI(
    title="FastAPI CRUD Clean Architecture",
    lifespan=lifespan
)

# --- Middleware لمعالجة الأخطاء وطباعتها ---
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response 
    except Exception as e:
        print("🔴 Middleware Error Detected:")
        traceback.print_exc() 
        return JSONResponse(
            status_code=500, 
            content={"detail": "Internal Server Error", "error": str(e)}
        )

# --- إضافة الـ Routes ---

# 1. الـ Router الأساسي
app.include_router(router)

# 2. روتر الـ Embeddings
app.include_router(embedding_router.router)

# 3. روتر الـ CV Reviewer (الجديد)
app.include_router(cv_router.router) # <-- تعديل هنا

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)