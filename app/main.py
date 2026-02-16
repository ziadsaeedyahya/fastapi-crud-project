from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import traceback

from app.api.route.router import router
from app.clientsdatabase_clients import postgres_client, supabase_client, close_all_connections

# Import models to ensure they're registered with Base
from app.models import item_model, user_item_model, user_model

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    print("🚀 Starting up application...")
    
    # 1. PostgreSQL (Docker)
    try:
        postgres_client.create_tables()
        print("✅ PostgreSQL tables created")
    except Exception as e:
        print(f"❌ Failed to create PostgreSQL tables: {e}")
        # هنا بنعمل raise عشان لو الداتا بيز المحلية مش شغالة السيرفر ميقومش أصلاً
        raise 
    
    # 2. Supabase
    try:
        supabase_client.create_tables()
        print("✅ Supabase tables created")
    except Exception as e:
        # هنا بنطبع الأيرور بس بنكمل عشان السيرفر يشتغل عادي على المحلي
        print(f"⚠️  Supabase not available: {e}")
        print("   App will continue with PostgreSQL only")
    
    yield
    
    # Shutdown: Close connections
    close_all_connections()
    print("✅ Database connections closed")


app = FastAPI(
    title="FastAPI CRUD Clean Architecture",
    lifespan=lifespan
)

import traceback
from fastapi import Request
from fastapi.responses import JSONResponse

# ... باقي الكود (app = FastAPI) ...

# --- الـ Middleware اللي هيطبع لك الأيرور في الترمينال ---
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        # السطر ده هو اللي "بيعدي" الطلب للموقع
        response = await call_next(request)
        return response 
    except Exception as e:
        print("🔴 Middleware Error Detected:")
        # السطر ده هو اللي بيكتب لك مكان الغلط بالظبط في الترمينال
        traceback.print_exc() 
        return JSONResponse(
            status_code=500, 
            content={"detail": "Internal Server Error", "error": str(e)}
        )

# إضافة الـ Routes
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)