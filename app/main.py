from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import traceback

# استيراد الـ Routers
from app.api.route.router import router
from app.api.route import embedding_router      

from app.clientsdatabase_clients import postgres_client, supabase_client, close_all_connections

# Import models
from app.models import item_model, user_item_model, user_model ,embedding_model ,video_script_model

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up application...")
    """""
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
        print("   App will continue with PostgreSQL only")
    """""
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

# 1. الـ Router الأساسي (القديم)
app.include_router(router)

# 2. روتر الـ Embeddings (هيظهر في قسم لوحده في الـ Swagger)
app.include_router(embedding_router.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)